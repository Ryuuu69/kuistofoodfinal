from decimal import Decimal
from typing import Dict, Optional, Iterable, Set, Tuple
import re

# ================== Helpers génériques ==================
def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _is_tacos_product(p) -> bool:
    s = _norm(getattr(p, "slug", None)) or _norm(getattr(p, "name", None))
    return ("taco" in s) and ("menu" not in s)

def _is_menu_tacos_product(p) -> bool:
    s = _norm(getattr(p, "slug", None)) or _norm(getattr(p, "name", None))
    return ("taco" in s) and ("menu" in s)

def _is_meat_option(opt) -> bool:
    key = _norm(getattr(opt, "slug", None)) or _norm(getattr(opt, "name", None))
    return ("viande" in key) or ("meat" in key)

def _is_combo_menu_product(p) -> bool:
    s = _norm(getattr(p, "slug", None)) or _norm(getattr(p, "name", None))
    # "menu combo", "combo menu", etc.
    return ("combo" in s)

def _is_burger_selector_option(opt) -> bool:
    key = _norm(getattr(opt, "slug", None)) or _norm(getattr(opt, "name", None))
    return ("burger" in key)

# ================== TACOS ==================
def _parse_meat_count_from_choice_name(choice_name: str) -> Optional[int]:
    s = _norm(choice_name)
    m = re.search(r"\b([1-3])\b", s)
    if m:
        n = int(m.group(1))
        if n in (1, 2, 3):
            return n
    if re.search(r"\b(s|small|petit|simple)\b", s):
        return 1
    if re.search(r"\b(m|medium|moyen|double)\b", s):
        return 2
    if re.search(r"\b(l|large|grand|triple)\b", s):
        return 3
    return None

def _extract_meat_info(choice_reqs: Optional[Iterable], co_map: Dict[int, object]) -> int:
    if not choice_reqs:
        return 0
    found = 0
    for ch in choice_reqs:
        co = co_map.get(ch.choice_option_id)
        if not co:
            continue
        cnt = _parse_meat_count_from_choice_name(getattr(co, "name", ""))
        if cnt:
            found = max(found, cnt)
    return found

_MEAT_PRICES = {1: Decimal("7.00"), 2: Decimal("8.00"), 3: Decimal("10.00")}
_MENU_TACOS_EXTRA = Decimal("3.00")

def _sum_meat_mods_and_ids(choice_reqs: Optional[Iterable], opt_map: Dict[int, object], co_map: Dict[int, object]) -> Tuple[Decimal, Set[int]]:
    total = Decimal("0.00")
    ids: Set[int] = set()
    if choice_reqs:
        for ch in choice_reqs:
            opt = opt_map.get(ch.option_id)
            co  = co_map.get(ch.choice_option_id)
            if not opt or not co:
                continue
            if _is_meat_option(opt):
                if ch.choice_option_id not in ids:
                    ids.add(ch.choice_option_id)
                    total += Decimal(str(getattr(co, "price_modifier", 0) or 0))
    return total, ids

# ================== UTIL communs ==================
def _sum_modifiers(choice_reqs: Optional[Iterable], co_map: Dict[int, object]) -> Decimal:
    total = Decimal("0.00")
    if choice_reqs:
        for ch in choice_reqs:
            co = co_map.get(ch.choice_option_id)
            if co:
                total += Decimal(str(getattr(co, "price_modifier", 0) or 0))
    return total

def _find_selected_burger_name(choice_reqs: Optional[Iterable], opt_map: Dict[int, object], co_map: Dict[int, object]) -> Optional[str]:
    if not choice_reqs:
        return None
    for ch in choice_reqs:
        opt = opt_map.get(ch.option_id)
        co  = co_map.get(ch.choice_option_id)
        if not opt or not co:
            continue
        if _is_burger_selector_option(opt):
            name = getattr(co, "name", None)
            if name:
                return str(name).strip()
    return None

def _detect_burger_category_base(burger_choice_name: Optional[str], products_by_name: Optional[Dict[str, object]]) -> Optional[Decimal]:
    """
    Retourne 6.00 si burger ∈ catégorie 'Smash', 10.50 si ∈ 'Signature'.
    1) on mappe le nom du choix -> Product (avec .category chargé)
    2) fallback heuristique si pas trouvé: chercher 'smash' / 'signature' dans le nom
    """
    if not burger_choice_name:
        return None
    key = _norm(burger_choice_name)
    if products_by_name:
        p = products_by_name.get(key)
        if p is not None:
            cat = getattr(p, "category", None)
            cat_name = _norm(getattr(cat, "name", None)) if cat else ""
            cat_slug = _norm(getattr(cat, "slug", None)) if cat else ""
            cat_str = cat_slug or cat_name
            if "smash" in cat_str:
                return Decimal("6.00")
            if "signature" in cat_str:
                return Decimal("10.50")
    # fallback sur le libellé du choix
    if "smash" in key:
        return Decimal("6.00")
    if "signature" in key:
        return Decimal("10.50")
    return None

_COMBO_EXTRA = Decimal("5.00")

# ================== PRICING PRINCIPAL ==================
def compute_unit_price_for_item(
    product,
    choice_reqs: Optional[Iterable],
    options_map: Dict[int, object],
    choice_options_map: Dict[int, object],
    products_by_name: Optional[Dict[str, object]] = None,  # map: nom normalisé -> Product (avec .category)
) -> Decimal:
    """
    - TACOS: override 7/8/10 selon nb viandes; +3€ pour Menu Tacos; retire les mods 'viandes'.
    - MENU COMBO: prix = base_catégorie_burger (6 smash | 10.50 signatures) + 5€ + Σ price_modifier (inclut delta du burger).
    - AUTRES: base_price + Σ price_modifier (inchangé).
    """
    base = Decimal(str(getattr(product, "base_price")))
    extras_all = _sum_modifiers(choice_reqs, choice_options_map)

    # ---------- TACOS ----------
    if _is_tacos_product(product) or _is_menu_tacos_product(product):
        meat_count = _extract_meat_info(choice_reqs, choice_options_map)
        meat_mod_sum, _ids = _sum_meat_mods_and_ids(choice_reqs, options_map, choice_options_map)
        price = base
        if meat_count in (1, 2, 3):
            price = _MEAT_PRICES[meat_count]
            extras_all -= meat_mod_sum
        if _is_menu_tacos_product(product):
            price += _MENU_TACOS_EXTRA
        return (price + extras_all).quantize(Decimal("0.01"))

    # ---------- MENU COMBO ----------
    if _is_combo_menu_product(product):
        burger_choice_name = _find_selected_burger_name(choice_reqs, options_map, choice_options_map)
        cat_base = _detect_burger_category_base(burger_choice_name, products_by_name)
        if cat_base is not None:
            # On utilise TON sélecteur tel quel: Σ price_modifier contient déjà le delta du burger choisi.
            price = cat_base + _COMBO_EXTRA
            return (price + extras_all).quantize(Decimal("0.01"))
        # fallback si on ne peut pas classer le burger: ancien comportement
        return (base + extras_all).quantize(Decimal("0.01"))

    # ---------- AUTRES PRODUITS ----------
    return (base + extras_all).quantize(Decimal("0.01"))

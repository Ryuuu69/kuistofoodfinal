import os 
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "ton_token_admin_super_secret")
HEADERS = {
    "Content-Type": "application/json",
    "X-Admin-Token": ADMIN_TOKEN
}

def get_json(path, params=None):
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params or {})
    if not resp.ok:
        print(f"[GET ERROR] {path} -> {resp.status_code} {resp.text}")
        return []
    return resp.json()

def post_json(path, payload):
    resp = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"[POST ERROR] {path} {payload} -> {resp.status_code} {resp.text}")
        return None
    return resp.json()

def link_option_to_product(option_id, product_id):
    resp = requests.post(
        f"{BASE_URL}/api/options/{option_id}/products/{product_id}",
        headers=HEADERS,
        json={}
    )
    if not (resp.status_code == 204 or resp.status_code == 200):
        print(f"[LINK ERROR] Option {option_id} ⇄ Produit {product_id} -> {resp.status_code} {resp.text}")
    else:
        print(f"[LINK] Option {option_id} liée à Produit {product_id}")

def find_or_create_category(name, slug=None):
    cats = get_json("/api/categories/")
    for c in cats:
        if c.get("name", "").lower() == name.lower():
            return c["id"]
    payload = {"name": name, "slug": slug or name.lower().replace(" ", "-")}
    created = post_json("/api/categories/", payload)
    return created["id"] if created else None

def find_product_by_slug(slug):
    prods = get_json("/api/products/")
    for p in prods:
        if p.get("slug", "").lower() == slug.lower():
            return p
    return None

def create_product(prod_def, category_id):
    existing = find_product_by_slug(prod_def["slug"])
    if existing:
        print(f"[SKIP] Produit déjà existant : {prod_def['name']}")
        return existing
    payload = {
        "name": prod_def["name"],
        "slug": prod_def["slug"],
        "description": prod_def.get("description", ""),
        "base_price": prod_def.get("price", 0.0) or 0.0,
        "image_url": prod_def.get("image"),
        "category_id": category_id
    }
    created = post_json("/api/products/", payload)
    if created:
        print(f"[CREATE] Produit: {created['name']} (id={created.get('id')})")
    return created

def find_or_create_option(name, slug, opt_type="checkbox", image_url=None):
    opts = get_json("/api/options/")
    for o in opts:
        if o.get("name", "").lower() == name.lower():
            return o
    payload = {
        "name": name,
        "slug": slug,
        "type": opt_type,
        "image_url": image_url
    }
    created = post_json("/api/options/", payload)
    if created:
        print(f"[OPTION] {name} (id={created.get('id')})")
    return created

def find_or_create_choiceoption(name, price_modifier, option_id, image_url=None):
    opt = get_json(f"/api/options/{option_id}")
    for c in opt.get("choice_options", []):
        if c.get("name", "").lower() == name.lower():
            return c
    payload = {
        "name": name,
        "price_modifier": price_modifier or 0,
        "option_id": option_id,
        "image_url": image_url
    }
    created = post_json("/api/choice-options/", payload)
    if created:
        print(f"    [CHOICE] {name} (option_id={option_id}, id={created.get('id')})")
    return created

def extract_name_and_price(val):
    if "name" in val:
        return val["name"], val.get("price", 0)
    elif "label" in val:  # ex: meatCounts
        return val["label"], val.get("price", val.get("price_modifier", 0))
    else:
        return str(val), 0

def seed():
    print("=== Démarrage du SEED MENU ===")
    category_ids = {}
    # 1. Catégories
    for prod in products:
        cat = prod.get("category", "Autre")
        if cat not in category_ids:
            category_ids[cat] = find_or_create_category(cat)
    # 2. Produits
    for prod in products:
        cat_id = category_ids[prod.get("category", "Autre")]
        prod_obj = create_product(prod, cat_id)
        if not prod_obj:
            print(f"Erreur création produit {prod['name']}")
            continue
        product_id = prod_obj["id"]
        # 3. Options dynamiques (création globale, puis association)
        options = prod.get("options", {})
        for key, value in options.items():
            option_name = key.capitalize()
            opt_type = "checkbox"
            if key in ["remove"]:
                opt_type = "checkbox"
            elif key in ["burgerSelect", "petitCreuxSelect", "meatCounts", "meats", "drinks", "sizes"]:
                opt_type = "radio"
            elif key in ["sauces", "supplements"]:
                opt_type = "checkbox"
            else:
                opt_type = "checkbox"
            # Crée ou récupère l'option
            option = find_or_create_option(option_name, slug=option_name.lower(), opt_type=opt_type)
            if not option:
                continue
            option_id = option["id"]
            # Associe option <-> produit (table pivot)
            link_option_to_product(option_id, product_id)
            # Ajoute chaque choix pour l’option
            for val in value:
                choice_name, price = extract_name_and_price(val)
                image = val.get("image") if isinstance(val, dict) else None
                find_or_create_choiceoption(
                    name=choice_name,
                    price_modifier=price,
                    option_id=option_id,
                    image_url=image
                )
    print("=== SEED TERMINÉ ===")
# ------------ ⬇️ Mets ton menu ici (Python array) ⬇️ -------------
products = [
    {
        "id": 200,
        "name": "Tacos personnalisé",
        "slug": "tacos",
        "category": "tacos",
        "description": "Compose ton Menu tacos : 1, 2 ou 3 viandes au choix, sauces ,suppléments , frites maison et boisson.",
        "price": 7.00,
        "image": "img/tacos.jpg",
        "options": {
            "meatCounts": [
                {"name": 1, "label": "1 viande", "price": 7.00},
                {"name": 2, "label": "2 viandes", "price": 8.00},
                {"name": 3, "label": "3 viandes", "price": 10.00}
            ],
            "meats": [
                {"name": "Poulet mariné", "image": "img/poulet.jpg"},
                {"name": "Kefta", "image": "img/kefta.jpg"},
                {"name": "Tenders", "image": "img/tenders.jpg"},
                {"name": "Cordon Bleu", "image": "img/cordonbleu.jpg"},
                {"name": "Steak haché", "image": "img/steak.jpg"},
                {"name": "Nuggets", "image": "img/nuggets.jpg"},
                {"name": "Kebab", "image": "img/kebab.jpg"}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Chili Thaï", "price": 0, "image": "img/sauce-chili.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
                

            ],
            "supplements": [
                {"name": "Oeuf", "price": 1.20, "image": "img/oeuf.jpg"},
                {"name": "Chèvre", "price": 1.20, "image": "img/chevre.jpg"},
                {"name": "Champignons", "price": 1.20, "image": "img/champignons.jpg"},
                {"name": "Vache qui rit", "price": 1.20, "image": "img/vachequirit.jpg"},
                {"name": "Boursin", "price": 1.20, "image": "img/boursin.jpg"},
                {"name": "Oignons frits", "price": 1.20, "image": "img/oignonsfrits.jpg"},
                {"name": "Jambon", "price": 1.20, "image": "img/jambon.jpg"},
                {"name": "Cheddar", "price": 1.20, "image": "img/cheddar.jpg"},
                {"name": "Bacon", "price": 1.20, "image": "img/bacon.jpg"}
            ],
            "remove": [
                {"name": "Sans oignons", "price": 0},
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0}
            ]
            
        }
    },
    {
        "id": 198,
        "name": "Menu Tacos personnalisé",
        "slug": "menu-tacos",
        "category": "tacos",
        "description": "Compose ton tacos : 1, 2 ou 3 viandes au choix, sauces, suppléments, Frites Maison et une boisson.",
        "price": 10.00,
        "image": "img/tacos.jpg",
        "options": {
            "meatCounts": [
                {"name": 1, "label": "1 viande", "price": 10.00},
                {"name": 2, "label": "2 viandes", "price": 8.00},
                {"name": 3, "label": "3 viandes", "price": 10.00}
            ],
            "meats": [
                {"name": "Poulet mariné", "image": "img/poulet.jpg"},
                {"name": "Kefta", "image": "img/kefta.jpg"},
                {"name": "Tenders", "image": "img/tenders.jpg"},
                {"name": "Cordon Bleu", "image": "img/cordonbleu.jpg"},
                {"name": "Steak haché", "image": "img/steak.jpg"},
                {"name": "Nuggets", "image": "img/nuggets.jpg"},
                {"name": "Kebab", "image": "img/kebab.jpg"}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ],
            "supplements": [
                {"name": "Oeuf", "price": 1.20, "image": "img/oeuf.jpg"},
                {"name": "Chèvre", "price": 1.20, "image": "img/chevre.jpg"},
                {"name": "Champignons", "price": 1.20, "image": "img/champignons.jpg"},
                {"name": "Vache qui rit", "price": 1.20, "image": "img/vachequirit.jpg"},
                {"name": "Boursin", "price": 1.20, "image": "img/boursin.jpg"},
                {"name": "Oignons frits", "price": 1.20, "image": "img/oignonsfrits.jpg"},
                {"name": "Jambon", "price": 1.20, "image": "img/jambon.jpg"},
                {"name": "Cheddar", "price": 1.20, "image": "img/cheddar.jpg"},
                {"name": "Bacon", "price": 1.20, "image": "img/bacon.jpg"}
            ],
            "remove": [
                {"name": "Sans oignons", "price": 0},
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0}
            ],
            "drinks": [
                {"name": "Coca-Cola", "price": 0, "image": "img/coca.jpg"},
                {"name": "Ice Tea", "price": 0, "image": "img/icetea.jpg"},
                {"name": "Eau", "price": 0, "image": "img/eau.jpg"}
            ]
        }
    },
    {
        "id": 101,
        "name": "Classique",
        "slug": "smash-classique",
        "category": "smash-burgers",
        "description": "Viande hachée, cheddar, salade, tomate, oignon",
        "price": 6.00,
        "image": "img/smash-classique.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 102,
        "name": "Double",
        "slug": "smash-double",
        "category": "smash-burgers",
        "description": "2 steaks, double cheddar, salade, tomate, oignon",
        "price": 7.50,
        "image": "img/smash-double.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 103,
        "name": "Bacon",
        "slug": "smash-bacon",
        "category": "smash-burgers",
        "description": "Steak haché, bacon, cheddar, salade, tomate, oignon",
        "price": 7.50,
        "image": "img/smash-bacon.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                { "name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 104,
        "name": "Double Bacon",
        "slug": "smash-double-bacon",
        "category": "smash-burgers",
        "description": "2 steaks, bacon, double cheddar, salade, tomate, oignon",
        "price": 8.00,
        "image": "img/smash-double-bacon.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 105,
        "name": "Chicken",
        "slug": "smash-chicken",
        "category": "smash-burgers",
        "description": "Tenders, cheddar, salade, tomate, oignon",
        "price": 8.00,
        "image": "img/smash-chicken.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 15,
        "name": "BABY SMASH CHEESE",
        "slug": "cheese-burger",
        "category": "smash-burgers",
        "description": "Portion de fromage.",
        "price": 2.90,
        "image": "img/cheese.jpg",
        "options": {}
    },
    {
        "id": 16,
        "name": "BABAY SMASH DOUBLE CHEESE",
        "slug": "double-cheese-burger",
        "category": "smash-burgers",
        "description": "Double portion de fromage.",
        "price": 3.90,
        "image": "img/cheese.jpg",
        "options": {}
    },
    {
        "id": 106,
        "name": "Chèvre Miel",
        "slug": "smash-chevre-miel",
        "category": "smash-burgers",
        "description": "Viande hachée, salade, fromage de chèvre, miel",
        "price": 8.00,
        "image": "img/smash-chevre-miel.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 107,
        "name": "Fish",
        "slug": "smash-fish",
        "category": "smash-burgers",
        "description": "Poisson pané, salade, tomate, oignon, sauce blanche",
        "price": 8.00,
        "image": "img/smash-fish.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
        {
        "id": 201,
        "name": "Kuisto",
        "slug": "signature-kuisto",
        "category": "burgers-signature",
        "description": "Viande hachée, 2 tenders, oignons frits, cheddar, salade, ketchup",
        "price": 10.50,
        "image": "img/signature-kuisto.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 202,
        "name": "Pistachio",
        "slug": "signature-pistachio",
        "category": "burgers-signature",
        "description": "Viande hachée, roquette, tomates poêlées, stracciatella, pistache, parmesan",
        "price": 12.50,
        "image": "img/signature-pistachio.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 203,
        "name": "Grogon",
        "slug": "signature-grogon",
        "category": "burgers-signature",
        "description": "Double cheese, viande hachée, onion rings, oignons frits, sauce burger, frites, cornichons",
        "price": 10.50,
        "image": "img/signature-grogon.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 204,
        "name": "Le Veggie",
        "slug": "signature-le-veggie",
        "category": "burgers-signature",
        "description": "Steak de falafel, stracciatella, roquette, tomates poêlées, oignons, sauce blanche ciboulette",
        "price": 11.50,
        "image": "img/signature-le-veggie.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 205,
        "name": "Chicken Truff",
        "slug": "signature-chicken-truff",
        "category": "burgers-signature",
        "description": "Tenders, oignons, champignons persillés, sauce truffe",
        "price": 12.50,
        "image": "img/signature-chicken-truff.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ]
        }
    },
    {
        "id": 301,
        "name": "Menu Smash Burger",
        "slug": "menu-smash-burger",
        "category": "menus-burgers",
        "description": "Smash burger au choix, frites, boisson, sauces",
        "price": 8.50,
        "image": "img/menu-smash.jpg",
        "options": {
            "burgerSelect": [
                {"name": "Classique", "price": 6.00, "image": "img/burger-classique.jpg"},
                {"name": "Double", "price": 7.50, "image": "img/burger-double.jpg"},
                {"name": "Bacon", "price": 7.50, "image": "img/burger-bacon.jpg"},
                {"name": "Double Bacon", "price": 8.00, "image": "img/burger-double-bacon.jpg"},
                {"name": "Chicken", "price": 8.00, "image": "img/burger-chicken.jpg"},
                {"name": "Chèvre Miel", "price": 8.00, "image": "img/burger-chevre.jpg"},
                {"name": "Fish", "price": 8.00, "image": "img/burger-fish.jpg"}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ],
            "drinks": [
                {"name": "Coca-Cola", "price": 0, "image": "img/coca.jpg"},
                {"name": "Ice Tea", "price": 0, "image": "img/icetea.jpg"},
                {"name": "Eau", "price": 0, "image": "img/eau.jpg"}
            ],
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    },
    {
        "id": 302,
        "name": "Menu Signature Burger",
        "slug": "menu-signature-burger",
        "category": "menus-burgers",
        "description": "Burger signature au choix, frites, boisson, sauces",
        "price": 13.00,
        "image": "img/menu-signature.jpg",
        "options": {
            "burgerSelect": [
                {"name": "Kuisto", "price": 10.50, "image": "img/burger-kuisto.jpg"},
                {"name": "Pistachio", "price": 12.50, "image": "img/burger-pistachio.jpg"},
                {"name": "Grogon", "price": 10.50, "image": "img/burger-grogon.jpg"},
                {"name": "Le Veggie", "price": 11.50, "image": "img/burger-veggie.jpg"},
                {"name": "Chicken Truff", "price": 12.50, "image": "img/burger-truff.jpg"}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ],
            "drinks": [
                {"name": "Coca-Cola", "price": 0, "image": "img/coca.jpg"},
                {"name": "Ice Tea", "price": 0, "image": "img/icetea.jpg"},
                {"name": "Eau", "price": 0, "image": "img/eau.jpg"}
            ],
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    },
    {
        "id": 303,
        "name": "Menu Combo",
        "slug": "menu-combo",
        "category": "menus-burgers",
        "description": "Burger au choix, frites, boisson, sauces, petit creux",
        "price": 11.00,
        "image": "img/menu-combo.jpg",
        "options": {
            "burgerSelect": [
                {"name": "Kuisto", "price": 10.50, "image": "img/burger-kuisto.jpg"},
                {"name": "Pistachio", "price": 12.50, "image": "img/burger-pistachio.jpg"},
                {"name": "Grogon", "price": 10.50, "image": "img/burger-grogon.jpg"},
                {"name": "Le Veggie", "price": 11.50, "image": "img/burger-veggie.jpg"},
                {"name": "Chicken Truff", "price": 12.50, "image": "img/burger-truff.jpg"},
                {"name": "Classique", "price": 6.00, "image": "img/burger-classique.jpg"},
                {"name": "Double", "price": 7.50, "image": "img/burger-double.jpg"},
                {"name": "Bacon", "price": 7.50, "image": "img/burger-bacon.jpg"},
                {"name": "Double Bacon", "price": 8.00, "image": "img/burger-double-bacon.jpg"},
                {"name": "Chicken", "price": 8.00, "image": "img/burger-chicken.jpg"},
                {"name": "Chèvre Miel", "price": 8.00, "image": "img/burger-chevre.jpg"},
                {"name": "Fish", "price": 8.00, "image": "img/burger-fish.jpg"}
            ],
            "petitCreuxSelect": [
                {"name": "Nuggets", "price": 0, "image": "img/frites.jpg"},
                {"name": "Potatoes", "price": 0, "image": "img/potatoes.jpg"},
                {"name": "Onion Rings", "price": 0, "image": "img/onionrings.jpg"},
                {"name": "Tiramisu", "price": 0, "image": "img/salade.jpg"}
            ],
            "sauces": [
                {"name": "Mayonnaise", "price": 0, "image": "img/sauce-mayo.jpg" },
                {"name": "Ketchup", "price": 0, "image": "img/sauce-ketchup.jpg" },
                {"name": "Algérienne", "price": 0, "image": "img/sauce-algerienne.jpg" },
                {"name": "Biggy", "price": 0, "image": "img/sauce-biggy.jpg" },
                {"name": "Barbecue", "price": 0, "image": "img/sauce-bbq.jpg" },
                {"name": "Samouraï", "price": 0, "image": "img/sauce-samourai.jpg" },
                {"name": "Curry", "price": 0, "image": "img/sauce-curry.jpg" },
                {"name": "Andalouse", "price": 0, "image": "img/sauce-andalouse.jpg" },
                {"name": "Poivre", "price": 0, "image": "img/sauce-poivre.jpg" },
                {"name": "Marocaine", "price": 0, "image": "img/sauce-marocaine.jpg" },
                {"name": "Harissa", "price": 0, "image": "img/sauce-harissa.jpg" },
                {"name": "Moutarde", "price": 0, "image": "img/sauce-moutarde.jpg" },
                {"name": "Blanche", "price": 0.50, "image": "img/sauce-blanche.jpg"},
                {"name": "Smoky", "price": 0.50, "image": "img/sauce-smoky.jpg"},
                {"name": "Chili Thaï", "price": 0.50, "image": "img/sauce-chili.jpg"},
                {"name": "Mayo Truffe", "price": 0.50, "image": "img/sauce-truffe.jpg"},
                {"name": "Fromagère", "price": 0.50, "image": "img/sauce-fromagere.jpg"}
            ],
            "drinks": [
                {"name": "Coca-Cola", "price": 0, "image": "img/coca.jpg"},
                {"name": "Ice Tea", "price": 0, "image": "img/icetea.jpg"},
                {"name": "Eau", "price": 0, "image": "img/eau.jpg"}
            ],
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    },
        {
        "id": 12,
        "name": "CHICKEN POP",
        "slug": "chicken-pop",
        "category": "sides",
        "description": "Petites bouchées de poulet croustillant.",
        "price": None,
        "image": "img/chicken-pop.jpg",
        "options": {
            "sizes": [
                {"name": "S (200g)", "price": 3.90},
                {"name": "M (350g)", "price": 5.90},
                {"name": "L (500g)", "price": 7.90}
            ]
        }
    },
    {
        "id": 13,
        "name": "STICK MOZZA",
        "slug": "stick-mozza",
        "category": "sides",
        "description": "Bâtonnets de mozzarella panés.",
        "price": None,
        "image": "img/stick-mozza.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 14,
        "name": "NUGGETS",
        "slug": "nuggets",
        "category": "sides",
        "description": "Nuggets de poulet.",
        "price": None,
        "image": "img/nuggets.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 15,
        "name": "B.CAMEMBERT",
        "slug": "b-camembert",
        "category": "sides",
        "description": "Bouchées de camembert pané.",
        "price": None,
        "image": "img/b-camembert.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 16,
        "name": "OIGNONS RINGS",
        "slug": "oignons-rings",
        "category": "sides",
        "description": "Rondelles d’oignons frits.",
        "price": None,
        "image": "img/oignons-rings.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 17,
        "name": "JALAPENOS",
        "slug": "jalapenos",
        "category": "sides",
        "description": "Jalapeños panés et fondants.",
        "price": None,
        "image": "img/jalapenos.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 18,
        "name": "WINGS",
        "slug": "wings",
        "category": "sides",
        "description": "Ailes de poulet croustillantes.",
        "price": None,
        "image": "img/wings.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 19,
        "name": "TENDERS",
        "slug": "tenders",
        "category": "sides",
        "description": "Tenders de poulet.",
        "price": None,
        "image": "img/tenders.jpg",
        "options": {
            "sizes": [
                {"name": "4 pièces", "price": 3.50},
                {"name": "6 pièces", "price": 4.50},
                {"name": "8 pièces", "price": 6.50}
            ]
        }
    },
    {
        "id": 20,
        "name": "FRITES",
        "slug": "frites",
        "category": "sides",
        "description": "Frites maison classiques.",
        "price": None,
        "image": "img/frites.jpg",
        "options": {
            "sizes": [
                {"name": "Petite", "price": 1.50},
                {"name": "Grande", "price": 3.00}
            ]
        }
    },
    {
        "id": 21,
        "name": "FRITES CHEDDAR",
        "slug": "frites-cheddar",
        "category": "sides",
        "description": "Frites maison nappées de cheddar.",
        "price": None,
        "image": "img/frites-cheddar.jpg",
        "options": {
            "sizes": [
                {"name": "Petite", "price": 2.50},
                {"name": "Grande", "price": 3.50}
            ]
        }
    },
    {
        "id": 22,
        "name": "FRITES CHEDDAR BACON",
        "slug": "frites-cheddar-bacon",
        "category": "sides",
        "description": "Frites maison nappées de cheddar et bacon.",
        "price": None,
        "image": "img/frites-cheddar-bacon.jpg",
        "options": {
            "sizes": [
                {"name": "Petite", "price": 3.00},
                {"name": "Grande", "price": 4.50}
            ]
        }
    },
    {
        "id": 21,
        "name": "BUCKET DUO",
        "slug": "bucket-duo",
        "category": "buckets",
        "description": "Bucket Duo : 16 wings ou 8 wings + 6 tenders, avec 2 frites maison, 4 sauces et 2 boissons de 33 cl. Le combo parfait à partager.",
        "price": None,
        "image": "img/nuggets.jpg",
        "options": {
            "sizes": [
                {"name": "16 wings", "price": 18.00},
                {"name": "8 wings et 6 Tenders", "price": 19.00}
            ]
        }
    },
    {
        "id": 22,
        "name": "BUCKET FAMILY",
        "slug": "bucket-family",
        "category": "buckets",
        "description": "Bucket Family : 28 wings ou 16 wings + 10 tenders, avec 4 frites maison, 8 sauces et boisson 1,5L. Le combo familial à partager.",
        "price": None,
        "image": "img/nuggets.jpg",
        "options": {
            "sizes": [
                {"name": "28 wings", "price": 32.00},
                {"name": "16 wings et 10 Tenders", "price": 34.00}
            ]
        }
    },
    {
        "id": 32,
        "name": "Trompe-l’œil",
        "slug": "trompe-loeil",
        "category": "boissons-desserts",
        "description": "Trompe-l’œil : dessert signature du chef.",
        "price": 7.50,
        "image": "img/trompe-loeil.jpg",
        "options": {}
    },
    {
        "id": 24,
        "name": "Tiramisu",
        "slug": "tiramisu",
        "category": "boissons-desserts",
        "description": "Mascarpone crémeux, Nutella, spéculoos croquant et éclats d’Orio — le tiramisu qui fait fondre.",
        "price": 3.50,
        "image": "img/cheese.jpg",
        "options": {}
    },
    {
        "id": 25,
        "name": "Boisson 33 CL",
        "slug": "boisson-33cl",
        "category": "boissons-desserts",
        "description": "Canette de 33 cl au choix (Coca-Cola, Sprite, Fanta, etc.).",
        "price": 2.00,
        "image": "img/boisson-33cl.jpg",
        "options": {}
    },
    {
        "id": 26,
        "name": "Boisson 1,5 L",
        "slug": "boisson-1-5l",
        "category": "boissons-desserts",
        "description": "Bouteille de 1,5 litre au choix.",
        "price": 3.50,
        "image": "img/boisson-1-5l.jpg",
        "options": {}
    },
    {
        "id": 29,
        "name": "Menu Nuggets Bambino",
        "slug": "menu-nuggets-bambino",
        "category": "menus-bambino",
        "description": "5 nuggets, une portion de frites, une boisson et une compote.",
        "price": 4.90,
        "image": "img/menu-nuggets-bambino.jpg",
        "options": {}
    },
    {
        "id": 30,
        "name": "Menu Cheeseburger Bambino",
        "slug": "menu-cheeseburger-bambino",
        "category": "menus-bambino",
        "description": "Cheeseburger, une portion de frites, une boisson et une compote.",
        "price": 4.90,
        "image": "img/menu-cheeseburger-bambino.jpg",
        "options": {}
    },
    {
        "id": 31,
        "name": "Menu Tenders Bambino",
        "slug": "menu-tenders-bambino",
        "category": "menus-bambino",
        "description": "2 tenders, une portion de frites, une boisson et une compote.",
        "price": 4.90,
        "image": "img/menu-tenders-bambino.jpg",
        "options": {}
    },
    {
        "id": 401,
        "name": "CÉSARE",
        "slug": "salade-cesare",
        "category": "salades",
        "description": "Tenders, salade, oignon, parmesan, croûtons, oeuf mollet, sauce césar",
        "price": 9.00,
        "image": "img/salade-cesare.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    },
    {
        "id": 402,
        "name": "ITALIENNE",
        "slug": "salade-italienne",
        "category": "salades",
        "description": "Poulet grillé, stracciatella, tomates poêlées, salade, oignon, sauce blanche",
        "price": 8.90,
        "image": "img/salade-italienne.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    },
    {
        "id": 403,
        "name": "VEGGIE",
        "slug": "salade-veggie",
        "category": "salades",
        "description": "Falafel, stracciatella, tomates poêlées, salade, oignon",
        "price": 8.90,
        "image": "img/salade-veggie.jpg",
        "options": {
            "remove": [
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0},
                {"name": "Sans oignon", "price": 0}
            ]
        }
    }
]


if __name__ == "__main__":
    seed()



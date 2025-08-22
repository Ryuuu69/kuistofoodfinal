from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
import base64
from crud.crud_operations import geocode_address, calculate_distance

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.deps import get_db, get_admin_token
from schemas.schemas import OrderCreate, OrderUpdate, OrderResponse, OrderItemResponse
from crud.crud_operations import order_crud
from models.models import (
    OrderStatus, Order, OrderItem, DeliveryMode, PaymentMode, Product, ChoiceOption, Option
)
import stripe
from core.config import settings

# Pricing centralisé (tacos/menus tacos + menu combo)
from core.pricing import compute_unit_price_for_item

router = APIRouter(prefix="/orders", tags=["Orders"])
stripe.api_key = settings.STRIPE_SECRET_KEY


def map_order_to_response(order: Order) -> OrderResponse:
    items: List[OrderItemResponse] = []
    for it in order.order_items:
        snaps = getattr(it, "_choice_snapshots", None) or []
        items.append(
            OrderItemResponse(
                id=it.id,
                order_id=it.order_id,
                product_id=it.product_id,
                product_name_snapshot=it.product_name_snapshot,
                base_price_snapshot=it.base_price_snapshot,
                quantity=it.quantity,
                item_total=it.item_total,
                created_at=it.created_at,
                updated_at=it.updated_at,
                choice_options=snaps,
                product=None,
            )
        )
    return OrderResponse(
        id=order.id,
        name=order.name,
        address=order.address,
        phone=order.phone,
        delivery_mode=order.delivery_mode,
        payment_mode=order.payment_mode,
        fee=order.fee,
        latitude=None,
        longitude=None,
        total=order.total,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        order_items=items,
    )


# ---------------- CASH ----------------
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    payload = order_in.model_copy(update={"delivery_mode": DeliveryMode.delivery})
    db_order_full = await order_crud.create(db, obj_in=payload)
    return map_order_to_response(db_order_full)


@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token),
):
    orders = await order_crud.get_multi_with_relations(db, skip=skip, limit=limit, status=status)
    return [map_order_to_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token),
):
    order = await order_crud.get_with_relations(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return map_order_to_response(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    order_in: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token),
):
    order = await order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order_in.status:
        order.status = order_in.status
    await db.commit()
    await db.refresh(order)
    full_order = await order_crud.get_with_relations(db, id=order_id)
    return map_order_to_response(full_order)


# ---------------- CARD: create intent ONLY (no DB order) ----------------
def _encode_order_to_metadata_chunks(payload: Dict[str, Any], chunk_size: int = 495) -> Dict[str, str]:
    """
    Stripe metadata value limit ≈ 500 chars. On encode en base64 et on segmente.
    """
    raw = json.dumps(payload, separators=(",", ":"))
    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    parts = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]
    md = {"order_created": "0", "order_parts": str(len(parts))}
    for idx, part in enumerate(parts):
        md[f"order_data_b64_{idx}"] = part
    return md


def _decode_order_from_metadata(md: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstitue l'OrderCreate à partir des segments.
    Supporte aussi l'ancien 'order_data' si présent et valide.
    """
    single = md.get("order_data")
    if single:
        try:
            return json.loads(single)
        except Exception:
            pass

    n_parts = int(md.get("order_parts") or 0)
    if n_parts <= 0:
        raise ValueError("Aucune donnée de commande dans la metadata.")
    buf = []
    for i in range(n_parts):
        key = f"order_data_b64_{i}"
        part = md.get(key)
        if not part:
            raise ValueError(f"Métadonnée manquante: {key}")
        buf.append(part)
    b64 = "".join(buf)
    raw = base64.b64decode(b64.encode("ascii")).decode("utf-8")
    return json.loads(raw)


@router.post("/stripe-intent")
async def create_stripe_intent(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    """
    - Calcule total au serveur (pricing centralisé)
    - Vérifie la zone de livraison et calcule les frais (géofencing)
    - Crée PaymentIntent avec metadata CHUNKÉE (aucune création de commande ici)
    """
    safe_payload = order_in.model_copy(update={
        "delivery_mode": DeliveryMode.delivery,
        "payment_mode": PaymentMode.cb,
    })

    # ---------- GÉO-FENCING & FRAIS (identique au CRUD) ----------
    radius_km = float(getattr(settings, "DELIVERY_MAX_KM", 8.0))

    try:
        if safe_payload.latitude and safe_payload.longitude:
            distance_km = calculate_distance(
                settings.RESTAURANT_LAT, settings.RESTAURANT_LNG,
                float(safe_payload.latitude), float(safe_payload.longitude),
            )
        else:
            lat, lon = await geocode_address(safe_payload.address)
            distance_km = calculate_distance(settings.RESTAURANT_LAT, settings.RESTAURANT_LNG, lat, lon)
    except Exception:
        raise HTTPException(status_code=400, detail="Adresse invalide ou introuvable.")

    if distance_km > radius_km:
        raise HTTPException(
            status_code=400,
            detail=f"Adresse hors zone de livraison ({distance_km:.1f} km > {radius_km:.1f} km)."
        )

    fee = (
        settings.DELIVERY_BASE_FEE
        + settings.DELIVERY_PER_KM_FEE * Decimal(str(distance_km))
    ).quantize(Decimal("0.01"))

    # On met aussi le fee dans la payload encodée (cohérence avec /capture)
    safe_payload = safe_payload.model_copy(update={"fee": fee})
    # --------------------------------------------------------------

    # Chargement produits / options / choice options
    product_ids = [i.product_id for i in safe_payload.items]
    co_ids = [ch.choice_option_id for i in safe_payload.items if i.choices for ch in i.choices]
    opt_ids = [ch.option_id for i in safe_payload.items if i.choices for ch in i.choices]

    products = {}
    if product_ids:
        res = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        products = {p.id: p for p in res.scalars().all()}

    co_map = {}
    if co_ids:
        res = await db.execute(select(ChoiceOption).where(ChoiceOption.id.in_(co_ids)))
        co_map = {c.id: c for c in res.scalars().all()}

    opt_map = {}
    if opt_ids:
        res = await db.execute(select(Option).where(Option.id.in_(opt_ids)))
        opt_map = {o.id: o for o in res.scalars().all()}

    # Map "nom de choix burger" -> Product (avec catégorie) pour Menu Combo
    choice_names = set()
    for it in safe_payload.items:
        if it.choices:
            for ch in it.choices:
                co = co_map.get(ch.choice_option_id)
                if co and getattr(co, "name", None):
                    choice_names.add(co.name.strip())

    products_by_name: Dict[str, Product] = {}
    if choice_names:
        res = await db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.name.in_(list(choice_names)))
        )
        products_by_name = {(p.name or "").strip().lower(): p for p in res.scalars().all()}

    total = Decimal("0.00")
    for i in safe_payload.items:
        p = products.get(i.product_id)
        if not p:
            raise HTTPException(status_code=400, detail=f"Produit {i.product_id} introuvable.")
        # Pricing centralisé (tacos/menu tacos + menu combo)
        unit = compute_unit_price_for_item(p, i.choices, opt_map, co_map, products_by_name)
        qty = int(i.quantity or 1)
        line_total = unit * qty
        total += line_total

    # Utilise le fee calculé ci-dessus
    grand_total = (total + fee).quantize(Decimal("0.01"))
    amount_cents = max(50, int(grand_total * 100))

    # CHUNKED metadata
    md = _encode_order_to_metadata_chunks(jsonable_encoder(safe_payload))

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="eur",
            automatic_payment_methods={"enabled": True},
            metadata=md,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "amount_cents": amount_cents,
    }


# ---------------- CARD: capture after redirect (creates order ONCE) ----------------
@router.post("/capture", response_model=OrderResponse)
async def capture_payment(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Body: { "payment_intent_id": "pi_..." }
    Si PI payé et commande pas encore créée → crée la commande, marque metadata (order_created=1, order_id=...).
    Met aussi la commande en 'preparing' si le paiement est 'succeeded' (fallback si le webhook n'a pas encore tourné).
    """
    pi_id = str(payload.get("payment_intent_id") or "").strip()
    if not pi_id:
        raise HTTPException(status_code=400, detail="payment_intent_id requis.")

    try:
        pi = stripe.PaymentIntent.retrieve(pi_id)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e}")

    md = dict(pi.metadata or {})
    if pi.status not in ("succeeded", "processing", "requires_capture"):
        raise HTTPException(status_code=400, detail=f"Paiement non finalisé: {pi.status}")

    # Déjà créée ?
    if md.get("order_created") == "1" and md.get("order_id"):
        try:
            existing_id = int(md["order_id"])
        except (TypeError, ValueError):
            existing_id = None

        if existing_id:
            existing = await order_crud.get_with_relations(db, id=existing_id)
            if existing:
                # Fallback: si déjà payé, passer en 'preparing'
                if (
                    pi.status == "succeeded"
                    and existing.payment_mode == PaymentMode.cb
                    and existing.status == OrderStatus.pending
                ):
                    existing.status = OrderStatus.preparing
                    await db.commit()
                    await db.refresh(existing)
                return map_order_to_response(existing)

    # Reconstruire payload depuis metadata segmentée
    try:
        data = _decode_order_from_metadata(md)
        order_in = OrderCreate(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"order_data invalide dans metadata: {e}")

    # Créer la commande maintenant
    db_order_full = await order_crud.create(db, obj_in=order_in)

    # Fallback : si déjà payé, passer en 'preparing'
    try:
        if (
            pi.status == "succeeded"
            and db_order_full.payment_mode == PaymentMode.cb
            and db_order_full.status == OrderStatus.pending
        ):
            db_order_full.status = OrderStatus.preparing
            await db.commit()
            await db.refresh(db_order_full)
    except Exception:
        pass

    # Mettre à jour la metadata pour idempotence
    try:
        stripe.PaymentIntent.modify(
            pi_id,
            metadata={**md, "order_created": "1", "order_id": str(db_order_full.id)},
        )
    except stripe.error.StripeError:
        pass

    return map_order_to_response(db_order_full)

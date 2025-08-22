from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from decimal import Decimal
import httpx
from geopy.distance import geodesic
import stripe

from core.config import settings
from crud.base import CRUDBase
from models.models import (
    Category, Product, Option, ChoiceOption, Order, OrderItem,
    DeliveryMode, PaymentMode, OrderStatus,
    order_item_choices_association,
)
from schemas.schemas import (
    CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate,
    OptionCreate, OptionUpdate,
    ChoiceOptionCreate, ChoiceOptionUpdate, OrderCreate, OrderUpdate,
)

# Pricing centralisé (tacos/menus tacos + menu combo)
from core.pricing import compute_unit_price_for_item

stripe.api_key = settings.STRIPE_SECRET_KEY


# --- Geocoding and Distance Calculation ---
async def geocode_address(address: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not geocode address: {address}",
            )
        return float(data[0]["lat"]), float(data[0]["lon"])


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return geodesic((lat1, lon1), (lat2, lon2)).km


# --- UTIL snapshots choices (avec nom d'option pour l'admin) ---
async def get_order_item_choice_snapshots(db: AsyncSession, order_item_id: int):
    """
    Récupère les snapshots des choix d'un OrderItem + le nom/ID de l'option
    (ex: option_name = 'Sauces', 'Suppléments', ...).
    Aucune migration: on déduit via des JOINs.
    """
    q = (
        select(
            order_item_choices_association.c.choice_option_id,
            order_item_choices_association.c.choice_name_snapshot,
            order_item_choices_association.c.choice_price_modifier_snapshot,
            ChoiceOption.option_id,
            Option.name.label("option_name"),
        )
        .join(ChoiceOption, ChoiceOption.id == order_item_choices_association.c.choice_option_id)
        .join(Option, Option.id == ChoiceOption.option_id)
        .where(order_item_choices_association.c.order_item_id == order_item_id)
    )
    res = await db.execute(q)
    rows = res.fetchall()

    return [
        {
            "choice_option_id": row.choice_option_id,
            "choice_name_snapshot": row.choice_name_snapshot,
            "choice_price_modifier_snapshot": row.choice_price_modifier_snapshot,
            "option_id": row.option_id,
            "option_name": row.option_name,
        }
        for row in rows
    ]


# --- CRUD ---
class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def get_with_relations(self, db: AsyncSession, id: int):
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(Product.category),
                selectinload(Product.options).selectinload(Option.choice_options),
                selectinload(Product.order_items),
            )
            .filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_relations(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(Product.category),
                selectinload(Product.options).selectinload(Option.choice_options),
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()


class CRUDOption(CRUDBase[Option, OptionCreate, OptionUpdate]):
    async def get_with_relations(self, db: AsyncSession, id: int):
        result = await db.execute(
            select(self.model)
            .options(selectinload(Option.choice_options))
            .filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_relations(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(self.model)
            .options(selectinload(Option.choice_options))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()


class CRUDChoiceOption(CRUDBase[ChoiceOption, ChoiceOptionCreate, ChoiceOptionUpdate]):
    pass


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    async def create(self, db: AsyncSession, obj_in: OrderCreate):
        # Maps
        products_map: Dict[int, Product] = {}
        options_map: Dict[int, Option] = {}
        choice_options_map: Dict[int, ChoiceOption] = {}

        product_ids = [item.product_id for item in obj_in.items]
        choice_option_ids = [
            ch.choice_option_id
            for item in obj_in.items if item.choices
            for ch in item.choices
        ]
        option_ids_from_choices = [
            ch.option_id
            for item in obj_in.items if item.choices
            for ch in item.choices
        ]

        if product_ids:
            products_result = await db.execute(
                select(Product).filter(Product.id.in_(product_ids))
            )
            products_map = {p.id: p for p in products_result.scalars().all()}

        if option_ids_from_choices:
            options_result = await db.execute(
                select(Option).filter(Option.id.in_(option_ids_from_choices))
            )
            options_map = {o.id: o for o in options_result.scalars().all()}

        if choice_option_ids:
            choice_options_result = await db.execute(
                select(ChoiceOption).filter(ChoiceOption.id.in_(choice_option_ids))
            )
            choice_options_map = {co.id: co for co in choice_options_result.scalars().all()}

        # ---- map "nom (choice) -> Product (avec .category)" pour Menu Combo
        choice_names = set()
        for item_req in obj_in.items:
            if item_req.choices:
                for ch in item_req.choices:
                    co = choice_options_map.get(ch.choice_option_id)
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

        # Items & total
        db_order_items: List[OrderItem] = []
        order_total_items_sum = Decimal("0.00")

        for item_req in obj_in.items:
            product = products_map.get(item_req.product_id)
            if not product:
                raise HTTPException(status_code=400, detail=f"Product with ID {item_req.product_id} not found.")

            # Pricing centralisé (tacos/menu tacos + menu combo + autres produits)
            unit_price = compute_unit_price_for_item(
                product,
                item_req.choices,
                options_map,
                choice_options_map,
                products_by_name,  # important pour Menu Combo (catégorie du burger choisi)
            )
            qty = int(item_req.quantity or 1)
            item_total_for_quantity = unit_price * qty
            order_total_items_sum += item_total_for_quantity

            db_order_item = OrderItem(
                product_id=product.id,
                product_name_snapshot=product.name,
                base_price_snapshot=Decimal(str(product.base_price)),
                quantity=qty,
                item_total=item_total_for_quantity,
            )
            db_order_items.append(db_order_item)

        # ----------------------- GÉO-FENCING / FRAIS -----------------------
        # Rayon de livraison autorisé (km). Si non défini dans Settings, fallback 8.0 km.
        radius_km = float(getattr(settings, "DELIVERY_MAX_KM", 8.0))

        # On calcule la distance quoiqu'il arrive (même si le client a proposé un fee)
        distance_km = 0.0
        try:
            if obj_in.latitude and obj_in.longitude:
                distance_km = calculate_distance(
                    settings.RESTAURANT_LAT, settings.RESTAURANT_LNG,
                    float(obj_in.latitude), float(obj_in.longitude),
                )
            else:
                lat, lon = await geocode_address(obj_in.address)
                distance_km = calculate_distance(
                    settings.RESTAURANT_LAT, settings.RESTAURANT_LNG, lat, lon,
                )
        except Exception:
            # En cas d'échec de géocodage, on laisse 0.0 (mais tu peux choisir de lever 400 si tu préfères)
            distance_km = 0.0

        # Blocage hors zone
        if distance_km > radius_km:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hors zone de livraison : {distance_km:.1f} km > {radius_km:.1f} km.",
            )

        # Fee
        final_fee = Decimal(str(obj_in.fee or 0))
        if final_fee <= 0:
            calc_fee = (
                settings.DELIVERY_BASE_FEE
                + settings.DELIVERY_PER_KM_FEE * Decimal(str(distance_km))
            )
            final_fee = calc_fee.quantize(Decimal("0.01"))
        # -------------------------------------------------------------------

        # Order
        db_order = Order(
            name=obj_in.name,
            address=obj_in.address,
            phone=obj_in.phone,
            delivery_mode=DeliveryMode.delivery,
            payment_mode=obj_in.payment_mode,
            fee=final_fee,
            total=(order_total_items_sum + final_fee),
            status=OrderStatus.pending if obj_in.payment_mode == PaymentMode.cb else OrderStatus.preparing,
        )
        db_order.order_items.extend(db_order_items)
        db.add(db_order)
        await db.flush()  # IDs d'items

        # Snapshots des choix (NULL-safe)
        for db_item, item_req in zip(db_order_items, obj_in.items):
            if item_req.choices:
                for choice_req in item_req.choices:
                    co = choice_options_map.get(choice_req.choice_option_id)
                    if not co:
                        continue
                    await db.execute(
                        order_item_choices_association.insert().values(
                            order_item_id=db_item.id,
                            choice_option_id=co.id,
                            choice_name_snapshot=co.name,
                            choice_price_modifier_snapshot=Decimal(str(getattr(co, "price_modifier", 0) or 0)),
                        )
                    )
        await db.commit()

        # Recharger avec relations nécessaires
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product),
            )
            .where(Order.id == db_order.id)
        )
        db_order_full = result.scalar_one()

        # Attacher les snapshots (avec option_name) pour Pydantic
        for item in db_order_full.order_items:
            item._choice_snapshots = await get_order_item_choice_snapshots(db, item.id)

        return db_order_full

    async def get_multi_with_relations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
    ):
        query = (
            select(Order)
            .options(selectinload(Order.order_items))
            .offset(skip)
            .limit(limit)
        )
        if status:
            query = query.where(Order.status == status)
        result = await db.execute(query)
        orders = result.scalars().unique().all()

        for order in orders:
            for item in order.order_items:
                item._choice_snapshots = await get_order_item_choice_snapshots(db, item.id)

        return orders


# --- Instantiate CRUD objects ---
category_crud = CRUDCategory(Category)
product_crud = CRUDProduct(Product)
option_crud = CRUDOption(Option)
choice_option_crud = CRUDChoiceOption(ChoiceOption)
order_crud = CRUDOrder(Order)

from __future__ import annotations

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

# ==== imports projet (version actuelle) ====
# On suppose que ces modules existent à côté de ce server.py
from database import get_db, engine as async_engine, Base
from models import (
    Category, Product, Menu, Option, ChoiceOption,
    Order, OrderItem, order_item_choices_association,
    DeliveryMode, PaymentMode, OrderStatus,
)
import schemas


# ==== FastAPI ====
app = FastAPI(
    title="Restaurant API",
    description="API pour la gestion d'un restaurant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==== CORS ====
# Gitpod change d'hôte à chaque session -> on accepte tous les sous-domaines *.gitpod.io
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:8000",
        "https://localhost:5173", "https://localhost:8000",
    ],
    allow_origin_regex=r"https://.*\.gitpod\.io$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# ==== DB: create-all en DEV ====
@app.on_event("startup")
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ==== Routers ====
api = APIRouter(prefix="/api")


# ---------------------------
#        CATEGORIES
# ---------------------------
@api.post("/categories/", response_model=schemas.CategoryResponse)
async def create_category(category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    db_obj = Category(**category.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@api.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.id == category_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Category not found")
    return obj

@api.get("/categories/", response_model=List[schemas.CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category))
    return res.scalars().all()

@api.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(category_id: int, payload: schemas.CategoryUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.id == category_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Category not found")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@api.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.id == category_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Category not found")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}


# ---------------------------
#         PRODUCTS
# ---------------------------
@api.post("/products/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    db_obj = Product(**product.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@api.get("/products/{product_id}", response_model=schemas.ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Product not found")
    return obj

@api.get("/products/", response_model=List[schemas.ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product))
    return res.scalars().all()

@api.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Product not found")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}


# ---------------------------
#          MENUS
# ---------------------------
@api.get("/menus/", response_model=List[schemas.MenuResponse])
async def list_menus(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Menu))
    return res.scalars().all()


# ---------------------------
#          OPTIONS
# ---------------------------
@api.get("/options/", response_model=List[schemas.OptionResponse])
async def list_options(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Option))
    return res.scalars().all()

@api.get("/choice-options/", response_model=List[schemas.ChoiceOptionResponse])
async def list_choice_options(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ChoiceOption))
    return res.scalars().all()


# ---------------------------
#           ORDERS
# ---------------------------
@api.post("/orders/", response_model=schemas.OrderResponse)
async def create_order(order: schemas.OrderCreate, db: AsyncSession = Depends(get_db)):
    """
    Crée la commande + items + snapshots de choix.
    Calcul du total: (base_price + supplément menu + somme des options) * quantité  (+ fee).
    """
    # 1) créer l'ordre
    fee = Decimal(order.fee or 0)
    db_order = Order(
        name=order.name.strip(),
        address=order.address.strip(),
        phone=order.phone.strip(),
        delivery_mode=DeliveryMode.delivery,  # unique
        payment_mode=order.payment_mode,
        fee=fee,
        total=Decimal("0.00"),
        status=OrderStatus.pending,
    )
    db.add(db_order)
    await db.flush()  # obtient db_order.id sans commit

    # 2) créer les items + snapshots
    running_total = Decimal("0.00")

    for item in order.items:
        # produit
        res_prod = await db.execute(select(Product).where(Product.id == item.product_id))
        product = res_prod.scalar_one_or_none()
        if not product:
            raise HTTPException(400, f"Produit {item.product_id} introuvable")

        base_price = Decimal(product.base_price)
        qty = int(item.quantity or 1)

        # supplément de menu (si présent)
        menu_supp = Decimal("0.00")
        if item.menu_id:
            res_menu = await db.execute(select(Menu).where(Menu.id == item.menu_id))
            menu = res_menu.scalar_one_or_none()
            if menu and menu.supplement:
                menu_supp = Decimal(menu.supplement)

        # options choisies
        options_total = Decimal("0.00")
        if item.choices:
            choice_ids = [c.choice_option_id for c in item.choices]
            if choice_ids:
                res_choices = await db.execute(
                    select(ChoiceOption).where(ChoiceOption.id.in_(choice_ids))
                )
                for co in res_choices.scalars().all():
                    options_total += Decimal(co.price_modifier or 0)

        unit_price = base_price + menu_supp + options_total
        item_total = (unit_price * qty).quantize(Decimal("0.01"))
        running_total += item_total

        db_item = OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            menu_id=item.menu_id,
            product_name_snapshot=product.name,
            base_price_snapshot=base_price,
            quantity=qty,
            item_total=item_total,
        )
        db.add(db_item)
        await db.flush()  # pour avoir db_item.id

        # snapshots des choix
        if item.choices:
            for choice in item.choices:
                # on relit la choice option pour snapshot (si pas déjà chargée)
                res_co = await db.execute(select(ChoiceOption).where(ChoiceOption.id == choice.choice_option_id))
                co = res_co.scalar_one_or_none()
                if not co:
                    continue
                await db.execute(
                    insert(order_item_choices_association).values(
                        order_item_id=db_item.id,
                        choice_option_id=co.id,
                        choice_name_snapshot=co.name,
                        choice_price_modifier_snapshot=Decimal(co.price_modifier or 0),
                    )
                )

    # 3) total = somme items + fee
    db_order.total = (running_total + fee).quantize(Decimal("0.01"))
    await db.commit()

    # 4) renvoyer l'ordre complet
    return await get_order(db_order.id, db)


@api.get("/orders/{order_id}", response_model=schemas.OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).where(Order.id == order_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Order not found")
    # lazy relationships -> rechargées via Pydantic from_attributes si config OK
    return obj


@api.get("/orders/", response_model=List[schemas.OrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).order_by(Order.id.desc()))
    return res.scalars().all()


# ==== register router ====
app.include_router(api)


# ==== Health / Root ====
@app.get("/")
async def root():
    return {"message": "Restaurant API is running", "docs": "/docs", "redoc": "/redoc"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

import enum
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, Enum,
    DECIMAL, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

# --- ENUMS ---
class DeliveryMode(enum.Enum):
    # Livraison uniquement
    delivery = "delivery"

class PaymentMode(enum.Enum):
    cb = "cb"
    especes = "especes"

class OrderStatus(enum.Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"

# --- ASSOCIATION TABLES ---

# Options réutilisables (sauces, etc.) associées à plusieurs produits
product_options_association = Table(
    "product_options",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("option_id", Integer, ForeignKey("options.id"), primary_key=True)
)

# Commande : snapshot des choix
order_item_choices_association = Table(
    "order_item_choices",
    Base.metadata,
    Column("order_item_id", Integer, ForeignKey("order_items.id"), primary_key=True),
    Column("choice_option_id", Integer, ForeignKey("choice_options.id"), primary_key=True),
    Column("choice_name_snapshot", String(100), nullable=False),
    Column("choice_price_modifier_snapshot", DECIMAL(10, 2), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

# --- CATEGORY ---
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    products = relationship("Product", back_populates="category")

# --- PRODUCT ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=True)
    description = Column(Text)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    category = relationship("Category", back_populates="products")

    # Plusieurs options réutilisables (sauces, etc.)
    options = relationship("Option", secondary=product_options_association, back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

# --- OPTION ---
class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(500))
    slug = Column(String(100), unique=True, nullable=True)
    type = Column(String(20), nullable=False)  # radio, checkbox, etc.
    products = relationship("Product", secondary=product_options_association, back_populates="options")
    choice_options = relationship("ChoiceOption", back_populates="option")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# --- CHOIX POSSIBLE D'UNE OPTION ---
class ChoiceOption(Base):
    __tablename__ = "choice_options"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(500))
    price_modifier = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    option = relationship("Option", back_populates="choice_options")
    order_items = relationship("OrderItem", secondary=order_item_choices_association, back_populates="choice_options")

# --- ORDER + ITEMS ---
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    delivery_mode = Column(
        Enum(DeliveryMode, name="deliverymode"),
        nullable=False,
        server_default="delivery"
    )
    payment_mode = Column(Enum(PaymentMode), nullable=False)
    fee = Column(DECIMAL(10, 2), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # >>> SUPPRIMÉ: menu_id
    product_name_snapshot = Column(String(200), nullable=False)
    base_price_snapshot = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    item_total = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    choice_options = relationship("ChoiceOption", secondary=order_item_choices_association, back_populates="order_items")
    # >>> SUPPRIMÉ: menu = relationship("Menu")

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from models.models import DeliveryMode, PaymentMode, OrderStatus

# ----- Common Timestamps -----
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None


# ----- CATEGORY -----
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ----- CHOICE OPTION -----
class ChoiceOptionBase(BaseModel):
    name: str
    price_modifier: Decimal = Decimal("0.00")
    option_id: int
    image_url: Optional[str] = None

class ChoiceOptionCreate(ChoiceOptionBase):
    pass

class ChoiceOptionUpdate(ChoiceOptionBase):
    pass

class ChoiceOptionResponse(ChoiceOptionBase, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ----- OPTION -----
class OptionBase(BaseModel):
    name: str
    slug: Optional[str] = None
    type: str  # 'radio', 'checkbox', etc.
    image_url: Optional[str] = None

class OptionCreate(OptionBase):
    pass

class OptionUpdate(OptionBase):
    pass

class OptionResponse(OptionBase, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # OK de garder une liste par défaut ici (Pydantic v2 gère)
    choice_options: List["ChoiceOptionResponse"] = []


# ----- PRODUCT -----
class ProductBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    base_price: Decimal
    image_url: Optional[str] = None
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: Optional["CategoryResponse"] = None
    options: List["OptionResponse"] = []


# ----- ORDER ITEM CHOICE (snapshots) -----
class OrderItemChoiceRequest(BaseModel):
    option_id: int
    choice_option_id: int

class OrderItemChoiceSnapshotResponse(BaseModel):
    """
    Snapshot renvoyé avec chaque ligne d'article.
    Ajout de option_id / option_name pour permettre le regroupement
    par type d'option côté admin (ex: 'Sauces', 'Suppléments').
    """
    model_config = ConfigDict(from_attributes=True)

    choice_option_id: int
    choice_name_snapshot: str
    choice_price_modifier_snapshot: Decimal

    # NOUVEAU : présents grâce au JOIN dans get_order_item_choice_snapshots()
    option_id: Optional[int] = None
    option_name: Optional[str] = None


# ----- ORDER ITEM -----
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int
    choices: Optional[List[OrderItemChoiceRequest]] = None

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    product_id: int
    product_name_snapshot: str
    base_price_snapshot: Decimal
    quantity: int
    item_total: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    choice_options: List[OrderItemChoiceSnapshotResponse] = []
    product: Optional["ProductResponse"] = None


# ----- ORDER -----
class OrderBase(BaseModel):
    name: str
    address: str
    phone: str
    delivery_mode: DeliveryMode = DeliveryMode.delivery
    payment_mode: PaymentMode
    fee: Optional[Decimal] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class OrderCreate(OrderBase):
    items: List[OrderItemRequest]

class OrderUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    payment_mode: Optional[PaymentMode] = None
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total: Decimal
    status: OrderStatus
    order_items: List[OrderItemResponse] = []

from pydantic import BaseModel, computed_field
from typing import Optional, List
from datetime import datetime


# ── Shared lightweight product info embedded inside an order item ──────────────

class OrderItemProduct(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None

    class Config:
        from_attributes = True


# ── Single order-item row ──────────────────────────────────────────────────────

class OrderItemDetail(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float          # unit price at time of order
    product: OrderItemProduct

    @computed_field
    @property
    def item_total(self) -> float:
        return round(self.price * self.quantity, 2)

    @computed_field
    @property
    def product_name(self) -> str:
        return self.product.name if self.product else "N/A"

    @computed_field
    @property
    def product_image(self) -> Optional[str]:
        return self.product.image if self.product else None

    @computed_field
    @property
    def product_description(self) -> Optional[str]:
        return self.product.description if self.product else None

    @computed_field
    @property
    def product_price(self) -> float:
        return self.product.price if self.product else self.price

    class Config:
        from_attributes = True


# ── Payload used for placing an order (checkout) ───────────────────────────────

class OrderCreate(BaseModel):
    payment_method: Optional[str] = "Cash on Delivery"
    address_id: Optional[int] = None


# ── Minimal response used by list endpoints (unchanged shape) ──────────────────

class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: Optional[datetime] = None
    payment_method: Optional[str] = "N/A"

    class Config:
        from_attributes = True


# ── Full detail response used by GET /orders/{order_id} ───────────────────────

class OrderDetailResponse(BaseModel):
    id: int
    status: str
    total_price: float
    payment_method: str = "N/A"
    created_at: datetime
    shipping_address: Optional[str] = "N/A"
    items: List[OrderItemDetail] = []

    @computed_field
    @property
    def order_date(self) -> str:
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"

    @computed_field
    @property
    def products(self) -> List[OrderItemDetail]:
        return self.items

    class Config:
        from_attributes = True


# ── Status update payload ──────────────────────────────────────────────────────

class OrderStatusUpdate(BaseModel):
    status: str
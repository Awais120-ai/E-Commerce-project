from pydantic import BaseModel
from typing import Optional
from datetime import datetime


from typing import Optional

class CheckoutRequest(BaseModel):
    address_id: int
    payment_method: str

    # Buy Now Support
    buy_now: bool = False
    product_id: Optional[int] = None
    quantity: Optional[int] = 1

# Product inside Order
class OrderProduct(BaseModel):
    id: int
    name: str
    description: str | None = None
    image: str | None = None

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    price: float

    product: OrderProduct

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: Optional[datetime] = None

    address_id: Optional[int] = None

    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
from pydantic import BaseModel
from app.schemas.product import ProductResponse


class CartBase(BaseModel):
    product_id: int
    quantity: int


class CartCreate(CartBase):
    pass


class CartResponse(CartBase):
    id: int
    user_id: int
    product: ProductResponse

    class Config:
        from_attributes = True
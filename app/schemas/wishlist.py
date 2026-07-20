from pydantic import BaseModel


class WishlistCreate(BaseModel):
    product_id: int


class ProductWishlist(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    image: str | None = None

    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product: ProductWishlist

    class Config:
        from_attributes = True
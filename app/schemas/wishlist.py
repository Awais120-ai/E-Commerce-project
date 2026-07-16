from pydantic import BaseModel


class WishlistProduct(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    image: str | None = None

    class Config:
        from_attributes = True


class WishlistCreate(BaseModel):
    product_id: int


class WishlistResponse(BaseModel):
    id: int
    product_id: int

    product: WishlistProduct

    class Config:
        from_attributes = True
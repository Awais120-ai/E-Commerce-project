from pydantic import BaseModel


class WishlistCreate(BaseModel):
    product_id: int


class WishlistResponse(BaseModel):
    id: int
    product_id: int

    class Config:
        from_attributes = True
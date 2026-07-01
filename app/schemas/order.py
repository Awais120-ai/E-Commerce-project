from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
from pydantic import BaseModel


class AddressBase(BaseModel):
    full_name: str
    phone: str
    country: str
    city: str
    postal_code: str
    address: str


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    postal_code: str | None = None
    address: str | None = None


class AddressResponse(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
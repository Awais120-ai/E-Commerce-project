from pydantic import BaseModel, field_validator
from typing import Optional


class AddressBase(BaseModel):
    address_type: Optional[str] = "Home"
    street_address: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: Optional[str] = "Pakistan"
    phone_number: Optional[str] = None


class AddressCreate(AddressBase):

    @field_validator("street_address", "city", "postal_code")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("This field is required and cannot be blank.")
        return v.strip()


class AddressUpdate(BaseModel):
    address_type: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator("street_address", "city", "postal_code", mode="before")
    @classmethod
    def must_not_be_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not str(v).strip():
                raise ValueError("This field cannot be blank.")
            return str(v).strip()
        return v


class AddressResponse(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse


router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post("/", response_model=AddressResponse, status_code=201)
def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_address(db, address, current_user.id)


@router.get("/", response_model=List[AddressResponse])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_addresses(db, current_user.id)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = crud.get_address(db, address_id, current_user.id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_address = crud.update_address(db, address_id, address, current_user.id)
    if not updated_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated_address


@router.delete("/{address_id}", status_code=200)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = crud.delete_address(db, address_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted successfully"}

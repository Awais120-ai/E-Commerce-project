from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud
from app.dependencies import get_db, get_current_user
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse
)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]

)

@router.post("/", response_model=AddressResponse)
def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.create_address(
        db,
        address,
        current_user.id
    )


@router.get("/", response_model=list[AddressResponse])
def get_addresses(db: Session = Depends(get_db)):
    return crud.get_addresses(db)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):

    address = crud.get_address(db, address_id)

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address: AddressUpdate,
    db: Session = Depends(get_db)
):

    updated = crud.update_address(
        db,
        address_id,
        address
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    return updated


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db)
):

    deleted = crud.delete_address(
        db,
        address_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    return {
        "message": "Address deleted successfully"
    }
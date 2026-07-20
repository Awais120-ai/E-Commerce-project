from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

import app.crud as crud

from app.schemas.cart import (
    CartCreate,
    CartResponse
)

from app.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


class CartQuantityUpdate(BaseModel):
    quantity: int


@router.post("/", response_model=CartResponse)
def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return crud.add_to_cart(
        db,
        current_user.id,
        cart
    )


@router.get("/", response_model=list[CartResponse])
def view_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return crud.get_cart(
        db,
        current_user.id
    )


@router.put("/{cart_id}", response_model=CartResponse)
def update_cart_quantity(
    cart_id: int,
    body: CartQuantityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated = crud.update_cart_quantity(db, cart_id, body.quantity)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    return updated


@router.delete("/{cart_id}")
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    deleted = crud.remove_from_cart(
        db,
        cart_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    return {
        "message": "Item removed from cart"
    }
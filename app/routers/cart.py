from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
import app.crud as crud
from pydantic import BaseModel

from app.schemas.cart import (
    CartCreate,
    CartResponse
)

from app.dependencies import get_current_user

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

class CartUpdate(BaseModel): 
     quantity: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
def update_cart(
    cart_id: int,
    cart: CartUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    updated = crud.update_cart(
        db,
        cart_id,
        cart.quantity,
        current_user.id
    )

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
        cart_id,
        current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    return {
        "message": "Item removed from cart"
    }

   

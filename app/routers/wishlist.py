from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.wishlist import WishlistCreate, WishlistResponse


router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


@router.post("/", response_model=WishlistResponse, status_code=201)
def add_to_wishlist(
    wishlist: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.add_to_wishlist(db, current_user.id, wishlist)


@router.get("/", response_model=List[WishlistResponse])
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_wishlist(db, current_user.id)


@router.delete("/{wishlist_id}", status_code=200)
def remove_from_wishlist(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = crud.remove_from_wishlist(db, wishlist_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return {"message": "Item removed from wishlist"}

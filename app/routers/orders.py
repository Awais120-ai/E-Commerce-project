from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
import app.crud as crud

from app.schemas.order import (
    OrderResponse,
    OrderStatusUpdate
)

from app.dependencies import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Checkout
@router.post("/", response_model=OrderResponse)
def checkout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    order = crud.create_order(
        db,
        current_user.id
    )

    if not order:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    return order


# My Orders
@router.get("/", response_model=list[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return crud.get_orders(
        db,
        current_user.id
    )


# Single Order
@router.get("/{order_id}", response_model=OrderResponse)
def order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    order = crud.get_order(
        db,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# Update Status
@router.put("/{order_id}/status")
def update_status(
    order_id: int,
    status: OrderStatusUpdate,
    db: Session = Depends(get_db)
):

    order = crud.update_order_status(
        db,
        order_id,
        status.status
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud

from app.schemas.order import (
    OrderResponse,
    OrderDetailResponse,
    OrderStatusUpdate,
    OrderCreate
)
from typing import Optional
from pydantic import BaseModel

from app.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# Checkout
@router.post("/", response_model=OrderResponse)
def checkout(
    order_data: Optional[OrderCreate] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    payment_method = "Cash on Delivery"
    address_id = None
    if order_data:
        payment_method = order_data.payment_method or "Cash on Delivery"
        address_id = order_data.address_id

    order = crud.create_order(
        db,
        current_user.id,
        payment_method=payment_method,
        address_id=address_id
    )


    if not order:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    return order


# Buy Now — place an order for a single product immediately (no cart required)
class BuyNowRequest(BaseModel):
    product_id: int
    quantity: int = 1
    payment_method: Optional[str] = "Cash on Delivery"
    address_id: Optional[int] = None


@router.post("/buy-now", response_model=OrderResponse)
def buy_now(
    body: BuyNowRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = crud.buy_now(
        db,
        user_id=current_user.id,
        product_id=body.product_id,
        quantity=body.quantity,
        payment_method=body.payment_method or "Cash on Delivery",
        address_id=body.address_id
    )

    if not order:
        raise HTTPException(
            status_code=400,
            detail="Order could not be placed."
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


# Order Details
@router.get("/{order_id}", response_model=OrderDetailResponse)
def order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = crud.get_order_detail(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# Update Status (admin / internal use)
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
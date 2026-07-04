from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

import app.crud as crud
# User import removed to avoid circular import
from app.dependencies import get_current_user

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PaymentResponse)
def make_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verify the order belongs to the user
    order = crud.get_order(db, payment.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    return crud.create_payment(
        db,
        order.id,
        order.total_price,
        payment.payment_method
    )


@router.get("/", response_model=list[PaymentResponse])
def read_payments(
    db: Session = Depends(get_db)
):

    return crud.get_payments(db)
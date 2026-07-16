from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.constants import PENDING
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # NEW
    address_id = Column(
        Integer,
        ForeignKey("addresses.id")
    )

    status = Column(
        String(20),
        default=PENDING
    )

    total_price = Column(
        Integer,
        default=0
    )
    created_at = Column(
    DateTime,
    default=datetime.utcnow
)
    user = relationship("User")



    # NEW
    address = relationship("Address")

    items = relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete"
    )
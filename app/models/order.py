from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base
from app.utils.constants import PENDING


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    status = Column(String(20), default=PENDING)

    total_price = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    payment_method = Column(
        String(50),
        nullable=True,
        default="N/A"
    )

    shipping_address = Column(
        String(500),
        nullable=True,
        default="N/A"
    )

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

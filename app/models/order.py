from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.constants import PENDING


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    status = Column(
    String(20),
    default=PENDING
)

    total_price = Column(
        Integer,
        default=0
    )

    user = relationship("User")
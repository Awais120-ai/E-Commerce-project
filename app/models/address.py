from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    address_type = Column(String(50), nullable=True, default="Home")
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="Pakistan")
    phone_number = Column(String(20), nullable=True)

    user = relationship("User")

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    role = Column(
        String(20),
        default="user"
    )
    # Relationships for multi‑tenant ownership
    products = relationship("Product", back_populates="owner")
    categories = relationship("Category", back_populates="owner")
    addresses = relationship("Address", back_populates="user")

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.core.database import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)  # Ensures a user can’t have the same product in cart multiple times
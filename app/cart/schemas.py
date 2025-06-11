from pydantic import BaseModel, Field
from typing import Optional

class CartItemCreate(BaseModel):
    product_id: int
    quantity: Optional[int] = 1  # Quantity of item be 1 by default when not mentioned while adding into cart

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

from fastapi import Path
from pydantic import BaseModel, Field, model_validator
from typing import Optional

class CartItemCreate(BaseModel):
    product_id: int
    quantity: Optional[int] = Field(default = 1)  # Quantity of item be 1 by default when not mentioned while adding into cart, greater than 0 if mentioned

    @model_validator(mode="after")
    def check_quantity(cls, values):
        if values.quantity < 1:
            raise ValueError("Quantity must be at least 1")
        return values

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0)

class CartItemOut(BaseModel):
    id: int = Path(..., ge = 1)
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

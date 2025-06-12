from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        form_attributes = True

class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        form_attributes = True

class OrderSummary(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime

    class Config:
        form_attributes = True

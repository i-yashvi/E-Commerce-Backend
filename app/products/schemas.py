from fastapi import Path
from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = Field(default = None)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    category: Optional[str] = Field(default = None)
    image_url: Optional[str] = Field(default = None)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default = None)
    description: Optional[str] = Field(default = None)
    price: Optional[float] = Field(default = None)
    stock: Optional[int] = Field(default = None)
    category: Optional[str] = Field(default = None)
    image_url: Optional[str] = Field(default = None)

class ProductOut(ProductCreate):
    id: int = Path(..., ge = 1)

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from .item import ItemInDB

class CartItem(BaseModel):
    # CartItem properties
    quantity: int = Field(ge=1)

    # Item properties
    id: int
    name: str
    price: float
    available: bool

class CartWithItems(BaseModel):
    """Schema for Cart with full Item details"""
    id: int
    price: float = 0.
    items: List[CartItem]

class CartList(BaseModel):
    """Schema for list of Carts"""
    carts: List[CartWithItems]
    total: int

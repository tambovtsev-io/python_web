from typing import Optional
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    """Base schema for Item"""
    name: str
    price: float = Field(gt=0)
    deleted: bool = False

class ItemCreate(ItemBase):
    """Schema for creating a new Item"""
    pass

class ItemUpdate(BaseModel, extra="forbid"):
    """Schema for updating an Item"""
    name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)


class ItemInDB(ItemBase):
    """Schema for Item as stored in the database"""
    id: int

    class ConfigDict:
        from_attributes = True

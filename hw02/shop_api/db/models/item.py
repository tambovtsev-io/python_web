from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship, Session
from db.database import Base
from api.schemas.item import ItemCreate

class ItemModel(Base):
    """
    SQLAlchemy ORM model for Item.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    deleted = Column(Boolean, default=False)

    # Relationships
    cart_items = relationship("CartItemModel", back_populates="item")


def find_item(item_id: int, db: Session) -> ItemModel:
    """Get an item by ID."""
    return (
        db.query(ItemModel)
        .filter(ItemModel.id == item_id)
        .first()
    )

def create_item(item: ItemCreate, db: Session) -> ItemModel:
    """Create a new item in the database."""
    db_item = ItemModel(
        name=item.name,
        price=item.price,
        deleted=item.deleted
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

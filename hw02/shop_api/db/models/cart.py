from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import (
    ForeignKey,
    Column,
    Integer, String, Float, Boolean
)
from db.database import Base
from api.schemas.cart import CartItem, CartWithItems


class CartModel(Base):
    """ORM model for shopping carts."""
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    @hybrid_property
    def total_price(self):
        return sum(item.item.price * item.quantity
                   for item in self.cart_items
                   if not item.item.deleted)

    # Relationship
    cart_items = relationship("CartItemModel", back_populates="cart")

    def to_pydantic(self):
        cart_items = [
            CartItem(
                quantity=cart_item.quantity,
                id=cart_item.item.id,
                name=cart_item.item.name,
                price=cart_item.item.price,
                available=not cart_item.item.deleted
            )
            for cart_item in self.cart_items
        ]
        return CartWithItems(
            id=self.id,
            price=self.total_price,
            items=cart_items
        )

class CartItemModel(Base):
    """Association table for Cart and Item relationship."""
    __tablename__ = "cart_items"

    cart_id = Column(Integer, ForeignKey("carts.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, default=1)
    available = Column(Boolean, default=True)

    # Relationships
    cart = relationship("CartModel", back_populates="cart_items")
    item = relationship("ItemModel", back_populates="cart_items")


def find_cart(item_id: int, db: Session) -> CartModel:
    """Get an item by ID."""
    return (
        db.query(CartModel)
        .filter(CartModel.id == item_id)
        .first()
    )


def create_cart(db: Session) -> CartModel:
    """Create a new cart."""
    db_cart = CartModel()
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def add_item_to_cart(
        db: Session,
        cart_id: int,
        item_id: int,
        quantity: int = 1
    ) -> CartItemModel:
    """Add an item to a cart."""
    cart_item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.item_id == item_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItemModel(
            cart_id=cart_id,
            item_id=item_id,
            quantity=quantity
        )
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from db.database import Base
from api.schemas.item import ItemCreate
from config import settings

from db.models.item import create_item
from db.models.cart import (
    CartModel, CartItemModel,
    create_cart, add_item_to_cart
)

def seed_database():
    """Seed the database with sample data."""
    base = Base
    engine = create_engine(settings.DATABASE_URL)
    base.metadata.drop_all(engine)
    base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create sample items
        items = [
            {"name": "Laptop", "price": 1000, "deleted": False},
            {"name": "Smartphone", "price": 500, "deleted": False},
            {"name": "Headphones", "price": 100, "deleted": False},
            {"name": "Mouse", "price": 30, "deleted": False},
            {"name": "Keyboard", "price": 60, "deleted": True},
        ]

        # Convert dict to schemas.ItemCreate
        items_obj = [ItemCreate(**item) for item in items]

        created_items = []
        for item_data in items_obj:
            item = create_item(item_data, session)
            created_items.append(item)

        # Create sample carts
        cart1 = create_cart(session)
        cart2 = create_cart(session)

        # Add items to carts
        add_item_to_cart(session, cart1.id, created_items[0].id)
        add_item_to_cart(session, cart1.id, created_items[1].id)
        add_item_to_cart(session, cart2.id, created_items[2].id)
        add_item_to_cart(session, cart2.id, created_items[3].id)

        session.commit()

    print("Database seeded successfully!")


def reset_database():
    base = Base
    engine = create_engine(settings.DATABASE_URL)
    base.metadata.drop_all(engine)
    base.metadata.create_all(engine)


if __name__ == "__main__":
    seed_database()

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from http import HTTPStatus

from db.database import get_db
from db.models.item import ItemModel, find_item
from db.models.cart import (
    CartModel,
    CartItemModel,
    create_cart,
    add_item_to_cart,
    find_cart
)
from api.schemas.cart import (
    CartItem,
    CartWithItems,
    CartList
)

from api.item import get_item

router = APIRouter()

@router.post("/cart", response_model=CartWithItems, status_code=HTTPStatus.CREATED)
async def create_new_cart(response: Response, db: Session = Depends(get_db)):
    """Create a new cart"""
    new_cart = create_cart(db)
    cart_data = new_cart.to_pydantic()

    # Set the Location header
    response.headers["Location"] = f"/cart/{new_cart.id}"

    return cart_data

@router.get("/cart/{cart_id}", response_model=CartWithItems, status_code=HTTPStatus.OK)
async def get_cart(cart_id: int, db: Session = Depends(get_db)):
    """Get a cart by id"""
    cart = find_cart(cart_id, db)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return cart.to_pydantic()

@router.get("/cart", response_model=List[CartWithItems], status_code=HTTPStatus.OK)
async def list_carts(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        min_quantity: Optional[int] = Query(None, ge=0),
        max_quantity: Optional[int] = Query(None, ge=0),
        db: Session = Depends(get_db)
    ):
    """Get a list of carts with optional filtering."""
    # Base query
    query = db.query(CartModel)

    # Subquery for total price and quantity
    subquery = db.query(
        CartItemModel.cart_id,
        func.sum(CartItemModel.quantity * ItemModel.price).label("total_price"),
        func.sum(CartItemModel.quantity).label("total_quantity")
    ).join(ItemModel, CartItemModel.item_id == ItemModel.id
    ).filter(ItemModel.deleted == False
    ).group_by(CartItemModel.cart_id
    ).subquery()

    # Join with the main query
    query = query.outerjoin(subquery, CartModel.id == subquery.c.cart_id)

    # Apply filters
    filters = []
    if min_price is not None:
        filters.append(subquery.c.total_price >= min_price)
    if max_price is not None:
        filters.append(subquery.c.total_price <= max_price)
    if min_quantity is not None:
        filters.append(subquery.c.total_quantity >= min_quantity)
    if max_quantity is not None:
        filters.append(subquery.c.total_quantity <= max_quantity)

    if filters:
        query = query.filter(and_(*filters))

    # Execute query
    total = query.count()
    carts = query.offset(offset).limit(limit).all()

    # Convert to Pydantic models
    cart_list = [cart.to_pydantic() for cart in carts]

    return cart_list

@router.post("/cart/{cart_id}/add/{item_id}", response_model=CartWithItems)
async def add_item_to_cart_endpoint(
        cart_id: int,
        item_id: int,
        db: Session = Depends(get_db)
    ):
    """Add an item to a cart or increase its quantity if already present."""
    # Handle errors for undefined ids
    await get_cart(cart_id, db)
    await get_item(item_id, db)


    cart_item = add_item_to_cart(db, cart_id, item_id)

    return cart_item.cart.to_pydantic()

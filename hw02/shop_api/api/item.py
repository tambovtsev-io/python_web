from fastapi import APIRouter, Depends, HTTPException, Query, Body
from http import HTTPStatus
from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import and_

from db.database import get_db
from db.models.item import ItemModel, find_item
from api.schemas.item import ItemCreate, ItemUpdate, ItemInDB

router = APIRouter()

@router.post("/item", response_model=ItemInDB, status_code=HTTPStatus.CREATED)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> ItemModel:
    """Create a new item"""
    db_item = ItemModel(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/item/{item_id}", response_model=ItemInDB)
async def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemModel:
    """Get an item by id"""
    item = find_item(item_id, db)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/item", response_model=List[ItemInDB])
async def list_items(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        min_price: Optional[float] = Query(None, gt=0),
        max_price: Optional[float] = Query(None, gt=0),
        show_deleted: bool = False,
        db: Session = Depends(get_db)
    ):
    """Get a list of items with optional filtering"""
    query = db.query(ItemModel)

    if not show_deleted:
        query = query.filter(ItemModel.deleted == False)

    if min_price is not None:
        query = query.filter(ItemModel.price >= min_price)

    if max_price is not None:
        query = query.filter(ItemModel.price <= max_price)

    return query.offset(offset).limit(limit).all()

@router.put("/item/{item_id}", response_model=ItemInDB)
async def update_item(
        item_id: int,
        item: ItemCreate,
        db: Session = Depends(get_db)
    ) -> ItemModel:
    """Replace an existing item"""
    db_item = find_item(item_id, db)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.model_dump().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/item/{item_id}", response_model=ItemInDB)
async def partial_update_item(
        item_id: int,
        item: ItemUpdate,
        db: Session = Depends(get_db)
    ) -> ItemModel:
    """Partially updae an item"""
    db_item = find_item(item_id, db)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item is deleted.")

    # This will raise a ValidationError if there are extra fields
    try:
        item_data = item.model_dump(exclude_unset=True)
    except ValidationError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    for key, value in item_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/item/{item_id}", response_model=ItemInDB)
async def delete_item(item_id: int, db: Session = Depends(get_db)) -> ItemModel:
    """Mark an item as deleted"""
    db_item = find_item(item_id, db)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.deleted = True
    db.commit()
    db.refresh(db_item)
    return db_item

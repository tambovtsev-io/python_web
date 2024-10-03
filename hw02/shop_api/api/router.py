from fastapi import APIRouter
from api.item import router as item_router
from api.cart import router as cart_router


router = APIRouter()

router.include_router(item_router, tags=["items"])
router.include_router(cart_router, tags=["carts"])

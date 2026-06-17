"""
CartPay — Items / Inventory Router
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.inventory import get_item_by_barcode, search_items, ALL_ITEMS
from app.models.schemas import Item

router = APIRouter()


@router.get("/{barcode}", response_model=Item)
def get_item(barcode: str):
    item = get_item_by_barcode(barcode)
    if not item:
        raise HTTPException(status_code=404, detail=f"Barcode {barcode} not found")
    return item


@router.get("/", response_model=list[Item])
def list_items(
    category: str | None = Query(None),
    near_expiry: bool    = Query(False, description="Only items expiring within 3 days"),
):
    items = ALL_ITEMS
    if category:
        items = [i for i in items if i.category.lower() == category.lower()]
    if near_expiry:
        items = [i for i in items if i.days_until_expiry is not None and i.days_until_expiry <= 3]
    return items


@router.get("/search/", response_model=list[Item])
def search(q: str = Query(..., min_length=2)):
    return search_items(q)

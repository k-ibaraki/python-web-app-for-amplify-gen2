from fastapi import APIRouter, HTTPException

from shared import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])

# インメモリストレージ（実験用）
_items: list[ItemResponse] = []
_next_id = 1


@router.get("", response_model=list[ItemResponse])
async def get_items():
    return _items


@router.post("", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    global _next_id
    new_item = ItemResponse(id=_next_id, **item.model_dump())
    _items.append(new_item)
    _next_id += 1
    return new_item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    for item in _items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

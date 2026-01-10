from pydantic import BaseModel


class ItemCreate(BaseModel):
    """アイテム作成リクエスト"""

    name: str
    price: float


class ItemResponse(BaseModel):
    """アイテムレスポンス"""

    id: int
    name: str
    price: float

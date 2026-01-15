from pydantic import BaseModel


class TodoCreate(BaseModel):
    """Todo作成リクエスト"""

    title: str


class TodoResponse(BaseModel):
    """Todoレスポンス"""

    id: int
    title: str
    completed: bool

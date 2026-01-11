import httpx

from schemas import TodoCreate, TodoResponse

# ビルド時に生成されるconfig.pyから設定を読み取る
try:
    from config import API_URL as DEFAULT_API_URL
except ImportError:
    # 開発時はconfig.pyが存在しないのでデフォルト値を使用
    DEFAULT_API_URL = "http://localhost:8000"


class ApiClient:
    """バックエンドAPIクライアント"""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or DEFAULT_API_URL

    async def get_todos(self) -> list[TodoResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/todos")
            response.raise_for_status()
            return [TodoResponse(**todo) for todo in response.json()]

    async def create_todo(self, title: str) -> TodoResponse:
        async with httpx.AsyncClient() as client:
            payload = TodoCreate(title=title)
            response = await client.post(
                f"{self.base_url}/todos",
                json=payload.model_dump(),
            )
            response.raise_for_status()
            return TodoResponse(**response.json())

    async def toggle_todo(self, todo_id: int) -> TodoResponse:
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{self.base_url}/todos/{todo_id}/toggle")
            response.raise_for_status()
            return TodoResponse(**response.json())

    async def delete_todo(self, todo_id: int) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/todos/{todo_id}")
            response.raise_for_status()

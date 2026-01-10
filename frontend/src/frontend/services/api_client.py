import httpx

from shared import ItemCreate, ItemResponse


class ApiClient:
    """バックエンドAPIクライアント"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def get_items(self) -> list[ItemResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/items")
            response.raise_for_status()
            return [ItemResponse(**item) for item in response.json()]

    async def create_item(self, name: str, price: float) -> ItemResponse:
        async with httpx.AsyncClient() as client:
            payload = ItemCreate(name=name, price=price)
            response = await client.post(
                f"{self.base_url}/items",
                json=payload.model_dump(),
            )
            response.raise_for_status()
            return ItemResponse(**response.json())

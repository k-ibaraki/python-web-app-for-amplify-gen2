from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import todos

app = FastAPI(title="Backend API")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

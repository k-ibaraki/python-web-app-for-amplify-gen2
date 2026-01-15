import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import TodoCreate, TodoResponse

# API Gateway stage prefix (empty for local development)
ROOT_PATH = os.getenv("API_ROOT_PATH", "")

app = FastAPI(title="Todo API", root_path=ROOT_PATH)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# インメモリストレージ
_todos: list[TodoResponse] = []
_next_id = 1


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoResponse])
async def get_todos():
    return _todos


@app.post("/todos", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    global _next_id
    new_todo = TodoResponse(id=_next_id, title=todo.title, completed=False)
    _todos.append(new_todo)
    _next_id += 1
    return new_todo


@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo(todo_id: int):
    for i, todo in enumerate(_todos):
        if todo.id == todo_id:
            _todos[i] = TodoResponse(
                id=todo.id, title=todo.title, completed=not todo.completed
            )
            return _todos[i]
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    global _todos
    for i, todo in enumerate(_todos):
        if todo.id == todo_id:
            _todos.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Todo not found")

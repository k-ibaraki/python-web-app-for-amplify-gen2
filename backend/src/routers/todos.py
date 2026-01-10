from fastapi import APIRouter, HTTPException

from shared import TodoCreate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

# インメモリストレージ（実験用）
_todos: list[TodoResponse] = []
_next_id = 1


@router.get("", response_model=list[TodoResponse])
async def get_todos():
    return _todos


@router.post("", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    global _next_id
    new_todo = TodoResponse(id=_next_id, title=todo.title, completed=False)
    _todos.append(new_todo)
    _next_id += 1
    return new_todo


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo(todo_id: int):
    for i, todo in enumerate(_todos):
        if todo.id == todo_id:
            _todos[i] = TodoResponse(
                id=todo.id, title=todo.title, completed=not todo.completed
            )
            return _todos[i]
    raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int):
    global _todos
    for i, todo in enumerate(_todos):
        if todo.id == todo_id:
            _todos.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Todo not found")

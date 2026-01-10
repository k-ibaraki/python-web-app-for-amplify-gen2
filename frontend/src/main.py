import flet as ft

from api_client import ApiClient


async def main(page: ft.Page):
    page.title = "Todo App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 40
    page.bgcolor = "#1a1a2e"

    api = ApiClient()
    todos_container = ft.Column(spacing=8)

    async def refresh_todos():
        todos_container.controls.clear()
        todos = await api.get_todos()
        for todo in todos:
            todos_container.controls.append(create_todo_item(todo))
        page.update()

    def create_todo_item(todo):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Checkbox(
                        value=todo.completed,
                        on_change=lambda e, tid=todo.id: page.run_task(
                            toggle_todo, tid
                        ),
                        active_color="#6c63ff",
                    ),
                    ft.Text(
                        todo.title if not todo.completed else f"✓ {todo.title}",
                        size=16,
                        weight=ft.FontWeight.W_400,
                        color="#ffffff" if not todo.completed else "#666666",
                        italic=todo.completed,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#ff6b6b",
                        icon_size=20,
                        on_click=lambda e, tid=todo.id: page.run_task(delete_todo, tid),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor="#16213e",
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    async def toggle_todo(todo_id: int):
        await api.toggle_todo(todo_id)
        await refresh_todos()

    async def delete_todo(todo_id: int):
        await api.delete_todo(todo_id)
        await refresh_todos()

    async def add_todo(e):
        if input_field.value:
            await api.create_todo(input_field.value)
            input_field.value = ""
            await refresh_todos()

    input_field = ft.TextField(
        hint_text="Add a new task...",
        border_radius=12,
        bgcolor="#16213e",
        border_color="#6c63ff",
        focused_border_color="#6c63ff",
        cursor_color="#6c63ff",
        text_style=ft.TextStyle(color="#ffffff"),
        hint_style=ft.TextStyle(color="#666666"),
        expand=True,
        on_submit=add_todo,
    )

    add_button = ft.IconButton(
        icon=ft.Icons.ADD_CIRCLE,
        icon_color="#6c63ff",
        icon_size=40,
        on_click=add_todo,
    )

    page.add(
        ft.Column(
            [
                ft.Text(
                    "Todo",
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff",
                ),
                ft.Text(
                    "Keep track of your tasks",
                    size=14,
                    color="#666666",
                ),
                ft.Container(height=24),
                ft.Row(
                    [input_field, add_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=24),
                todos_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    )

    await refresh_todos()


ft.run(main)

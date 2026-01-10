import flet as ft

from frontend.services.api_client import ApiClient


async def main(page: ft.Page):
    page.title = "Flet + FastAPI Demo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    api = ApiClient()

    # 入力フィールド
    name_field = ft.TextField(label="アイテム名", width=300)
    price_field = ft.TextField(
        label="価格", width=300, keyboard_type=ft.KeyboardType.NUMBER
    )

    # アイテムリスト表示
    items_column = ft.Column()

    async def refresh_items():
        items_column.controls.clear()
        items = await api.get_items()
        for item in items:
            items_column.controls.append(ft.Text(f"{item.name}: ¥{item.price:.0f}"))
        page.update()

    async def add_item(e):
        if name_field.value and price_field.value:
            await api.create_item(name_field.value, float(price_field.value))
            name_field.value = ""
            price_field.value = ""
            await refresh_items()

    add_button = ft.Button("追加", on_click=add_item)

    page.add(
        ft.Column(
            [
                ft.Text("アイテム管理", size=24, weight=ft.FontWeight.BOLD),
                name_field,
                price_field,
                add_button,
                ft.Divider(),
                ft.Text("登録済みアイテム", size=18),
                items_column,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    await refresh_items()


ft.run(main)

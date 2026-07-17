import flet as ft

def PaginationControls(page: ft.Page, current_page: int, total_items_on_page: int, limit: int, on_prev, on_next):
    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.ElevatedButton(
                "Previous", 
                disabled=(current_page == 0),
                on_click=lambda _: on_prev(),
                bgcolor="#1a2535",
                color="white"
            ),
            ft.Text(f"Page {current_page + 1}", color="#59657a", size=14, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Next",
                disabled=(total_items_on_page < limit),
                on_click=lambda _: on_next(),
                bgcolor="#1a2535",
                color="white"
            )
        ]
    )

import flet as ft
import time
import random
from app.api_client import api_client
from app.component.pagination_controls import PaginationControls

BG = "#020710"
SIDEBAR_BG = "#070816"
BORDER = "#172231"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"


def InventoryView(page: ft.Page, business_id: str):
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    view_route = page.route

    search_ref = ft.Ref[ft.TextField]()
    all_rows = []

    # ── Table header ──────────────────────────────────────────────
    def col_header(label, flex):
        return ft.Container(
            expand=flex,
            content=ft.Text(label, color="#59657a", size=9,
                            weight=ft.FontWeight.BOLD),
        )

    table_header = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, "#131b2a")),
        content=ft.Row(
            controls=[
                col_header("PRODUCT NAME", 4),
                col_header("QUANTITY", 2),
                col_header("UNIT PRICE", 2),
                col_header("STATUS", 2),
                col_header("ACTIONS", 3),
            ],
        ),
    )

    # ── Table body ────────────────────────────────────────────────
    table_body = ft.ListView(expand=True, spacing=0)

    empty_state = ft.Container(
        visible=False,
        padding=ft.padding.symmetric(vertical=60),
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Container(
                    width=72, height=72, border_radius=36,
                    bgcolor="#0d1a27",
                    border=ft.border.all(1, "#1a2e40"),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.WAREHOUSE_OUTLINED,
                                    color="#2a4257", size=32),
                ),
                ft.Text("NO INVENTORY FOUND", color="white", size=16,
                        weight=ft.FontWeight.BOLD),
                ft.Text("Add products first to manage inventory.",
                        color="#59657a", size=12),
            ],
        ),
    )

    def make_row(item, index):
        product = item.get("product") or {}
        name = product.get("product_name") or item.get(
            "product_name") or "Unknown"
        brand = product.get("brand") or item.get("brand") or ""
        stock = item.get("stock_quantity", 0) or 0
        unit = (item.get("unit") or "PCS").upper()
        price = item.get("selling_price", 0) or 0
        inv_id = item.get("id", "")
        product_id = item.get("product_id", "")
        in_stock = stock > 0

        row_bg = "#070d17" if index % 2 == 0 else "#050b14"

        def on_adjust(e):
            page.go(
                f"/businesses/{business_id}/inventory/{inv_id}/restock"
            )

        def on_delete(e):
            pass  # TODO: confirm dialog

        return ft.Container(
            bgcolor=row_bg,
            padding=ft.padding.symmetric(horizontal=24, vertical=18),
            border=ft.border.only(bottom=ft.BorderSide(1, "#0e1622")),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Product Name + Brand
                    ft.Container(
                        expand=4,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(
                                    width=36, height=36,
                                    border_radius=10,
                                    bgcolor="#0d1a27",
                                    border=ft.border.all(1, "#1a2e40"),
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(
                                        ft.Icons.INVENTORY_2_OUTLINED,
                                        color=CYAN, size=16,
                                    ),
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Text(name, color="white",
                                                size=13,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Text(
                                            f"({brand})" if brand else "",
                                            color="#59657a", size=11,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),

                    # Quantity
                    ft.Container(
                        expand=2,
                        content=ft.Row(
                            spacing=5,
                            controls=[
                                ft.Text(f"{int(stock)}", color="white",
                                        size=13, weight=ft.FontWeight.BOLD),
                                ft.Text(unit, color="#59657a", size=11),
                            ],
                        ),
                    ),

                    # Unit Price
                    ft.Container(
                        expand=2,
                        content=ft.Row(
                            spacing=2,
                            controls=[
                                ft.Text(f"₹{int(price):,}", color="white",
                                        size=13, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f".{int((price % 1) * 100):02d}",
                                    color="#3d4a5c", size=10,
                                ),
                            ],
                        ),
                    ),

                    # Status badge
                    ft.Container(
                        expand=2,
                        content=ft.Container(
                            padding=ft.padding.symmetric(
                                horizontal=12, vertical=6),
                            border_radius=20,
                            bgcolor="#071a14" if in_stock else "#1a0710",
                            border=ft.border.all(
                                1, "#0e3326" if in_stock else "#3a0e20"),
                            content=ft.Text(
                                "IN STOCK" if in_stock else "OUT OF STOCK",
                                color=GREEN if in_stock else "#fb7185",
                                size=9, weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ),

                    # Actions
                    ft.Container(
                        expand=3,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                # Stock Adj button
                                ft.Container(
                                    height=36,
                                    padding=ft.padding.symmetric(
                                        horizontal=14),
                                    border_radius=8,
                                    bgcolor="#071a14",
                                    border=ft.border.all(1, "#0e3326"),
                                    alignment=ft.Alignment(0, 0),
                                    ink=True,
                                    on_click=on_adjust,
                                    content=ft.Row(
                                        tight=True, spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.ADD_ROUNDED,
                                                    color=GREEN, size=13),
                                            ft.Text("STOCK ADJ.",
                                                    color=GREEN, size=9,
                                                    weight=ft.FontWeight.BOLD),
                                        ],
                                    ),
                                ),
                                # Delete button
                                # ft.Container(
                                #     width=36, height=36,
                                #     border_radius=8,
                                #     bgcolor="#0d1a27",
                                #     border=ft.border.all(1, "#1a2e40"),
                                #     alignment=ft.Alignment(0, 0),
                                #     ink=True,
                                #     on_click=on_delete,
                                #     content=ft.Icon(
                                #         ft.Icons.DELETE_OUTLINE_ROUNDED,
                                #         color="#657188", size=16,
                                #     ),
                                # ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def render_rows(data):
        if page.route != view_route:
            return

        table_body.controls.clear()
        if not data:
            empty_state.visible = True
        else:
            empty_state.visible = False
            for i, item in enumerate(data):
                table_body.controls.append(make_row(item, i))
        page.update()

    def filter_items(e=None):
        search_field = search_ref.current
        query = ((search_field.value if search_field else "") or "").strip().lower()
        if not query:
            render_rows(all_rows)
            pagination_container.content = PaginationControls(page, state["current_page"], len(all_rows), state["limit"], on_prev, on_next)
            page.update()
            return
        filtered = [
            r for r in all_rows
            if query in (
                (r.get("product") or {}).get("product_name") or
                r.get("product_name") or ""
            ).lower()
        ]
        render_rows(filtered)

    # ── Main content ──────────────────────────────────────────────
    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=36, right=36, top=32, bottom=24),
        content=ft.Column(
            spacing=24,
            controls=[
                # Header row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("Inventory", color="white",
                                        size=34, weight=ft.FontWeight.BOLD),
                                ft.Text("MANAGE ITEMS & STOCK",
                                        color="#59657a", size=9,
                                        weight=ft.FontWeight.BOLD),
                            ],
                        ),
                        ft.Row(
                            spacing=14,
                            controls=[
                                # Search
                                ft.Container(
                                    width=240, height=44,
                                    border_radius=12,
                                    bgcolor="#070d17",
                                    border=ft.border.all(1, "#1a2535"),
                                    padding=ft.padding.symmetric(
                                        horizontal=14),
                                    content=ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Icon(ft.Icons.SEARCH_ROUNDED,
                                                    color="#3d4a5c",
                                                    size=16),
                                            ft.TextField(
                                                ref=search_ref,
                                                hint_text="Search items...",
                                                hint_style=ft.TextStyle(
                                                    color="#3d4a5c",
                                                    size=12),
                                                border=ft.InputBorder.NONE,
                                                color="white",
                                                text_size=12,
                                                expand=True,
                                                on_change=filter_items,
                                            ),
                                        ],
                                    ),
                                ),
                                # Quick Add button
                                ft.Container(
                                    height=44,
                                    padding=ft.padding.symmetric(
                                        horizontal=20),
                                    border_radius=12,
                                    bgcolor=CYAN,
                                    alignment=ft.Alignment(0, 0),
                                    ink=True,
                                    on_click=lambda e: page.go(
                                        f"/businesses/{business_id}/products/add"
                                    ),
                                    content=ft.Row(
                                        tight=True, spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.BOLT_ROUNDED,
                                                    color="#02101a",
                                                    size=16),
                                            ft.Text("QUICK ADD",
                                                    color="#02101a",
                                                    size=9,
                                                    weight=ft.FontWeight.BOLD),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),

                # Table card
                ft.Container(
                    expand=True,
                    border_radius=16,
                    bgcolor="#070d17",
                    border=ft.border.all(1, "#131b2a"),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            table_header,
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    spacing=0,
                                    controls=[
                                        table_body,
                                        empty_state,
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ── Load data ─────────────────────────────────────────────────
    def on_prev():
        if state["current_page"] > 0:
            state["current_page"] -= 1
            load_data()

    def on_next():
        state["current_page"] += 1
        load_data()

    def load_data():
        if page.route != view_route:
            return

        try:
            data, status = api_client.get_inventory(business_id, skip=state["current_page"] * state["limit"], limit=state["limit"])
            if status == 401:
                api_client.set_token(None)
                if page.route == view_route:
                    page.go("/login")
                return
            if status == 200:
                if page.route != view_route:
                    return
                all_rows.clear()
                all_rows.extend(data if isinstance(data, list) else [])
                render_rows(all_rows)
                pagination_container.content = PaginationControls(page, state["current_page"], len(all_rows), state["limit"], on_prev, on_next)
                page.update()
                return
        except Exception:
            pass

        render_rows([])

    load_data()

    main_content.content.controls.append(pagination_container)
    return main_content

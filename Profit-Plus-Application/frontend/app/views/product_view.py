import flet as ft

from app.api_client import api_client
from app.component.pagination_controls import PaginationControls

BORDER = "#172231"
CYAN = "#16cdf2"
GREEN = "#14d59b"


def ProductsView(page: ft.Page, business_id: str):
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    view_route = page.route
    search_value = ft.Ref[ft.TextField]()
    all_products = []
    inv_map = {}
    inventory_by_product = {}

    products_grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=340,
        spacing=20,
        run_spacing=20,
        padding=ft.padding.only(left=4, right=12, top=4, bottom=18),
    )

    empty_state = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=14,
        controls=[
            ft.Container(
                width=80,
                height=80,
                border_radius=40,
                bgcolor="#0d1a27",
                border=ft.border.all(1, "#1a2e40"),
                alignment=ft.Alignment(0, 0),
                content=ft.Icon(
                    ft.Icons.INVENTORY_2_OUTLINED, color="#2a4257", size=36
                ),
            ),
            ft.Text(
                "NO PRODUCTS FOUND", color="white", size=18, weight=ft.FontWeight.BOLD
            ),
            ft.Text("Add your first product to get started.", color="#59657a", size=12),
        ],
    )

    warning_banner = ft.Container(
        padding=14,
        border_radius=8,
        bgcolor="#3c101a",
        border=ft.border.all(1, "#f21650"),
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.WARNING_ROUNDED, color="#f21650", size=20),
                ft.Text(
                    "SUBSCRIPTION EXPIRED: Locked products will be deleted in 7 days if the subscription is not renewed.",
                    color="white",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
            ],
        ),
    )

    def product_card(product):
        pid = product.get("id", "")
        name = product.get("product_name") or "Unnamed Product"
        inventory = inventory_by_product.get(str(pid), {})
        stock = inventory.get("stock_quantity", 0) or 0
        unit = (inventory.get("unit") or "PCS").upper()
        price = inventory.get("selling_price", 0) or 0
        brand = product.get("brand") or "N/A"
        ptype = product.get("business_type") or "N/A"
        category = (product.get("category") or "")[:5].upper() or "GEN"
        is_accessible = product.get("is_accessible", True)
        card_opacity = 1.0 if is_accessible else 0.4

        stock_color = GREEN if stock > 0 else "#fb7185"
        if stock <= (inventory.get("minimum_stock_alert", 5) or 5):
            stock_color = "#f59e0b"

        def on_manage_stock(e):
            if not is_accessible:
                return

            inv_id = inv_map.get(str(pid))
            if inv_id:
                page.go(f"/businesses/{business_id}/inventory/{inv_id}/restock")
                return

            try:
                data, status = api_client.create_inventory(business_id, pid)
            except Exception:
                page.go(f"/businesses/{business_id}/inventory")
                return

            if status in (200, 201) and data.get("id"):
                page.go(f"/businesses/{business_id}/inventory/{data['id']}/restock")
            elif status == 401:
                api_client.set_token(None)
                page.go("/login")
            else:
                page.go(f"/businesses/{business_id}/inventory")

        def on_edit(e):
            if is_accessible:
                page.go(f"/businesses/{business_id}/products/{pid}/edit")

        def on_delete(e):
            if not is_accessible:
                return

            try:
                data, status = api_client.delete_product(pid)
            except Exception:
                return

            if status == 401:
                api_client.set_token(None)
                page.go("/login")
                return

            if status in (200, 204):
                load_data()

        return ft.Container(
            width=320,
            height=280,
            border_radius=20,
            bgcolor="#070d17",
            border=ft.border.all(1, "#1a2535"),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            opacity=card_opacity,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(left=20, right=16, top=18, bottom=12),
                        content=ft.Column(
                            spacing=14,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Container(
                                            width=52,
                                            height=52,
                                            border_radius=14,
                                            bgcolor="#0d1a27",
                                            border=ft.border.all(1, "#1a2e40"),
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Icon(
                                                ft.Icons.INVENTORY_2_OUTLINED,
                                                color=CYAN,
                                                size=24,
                                            ),
                                        ),
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Container(
                                                    padding=ft.padding.symmetric(
                                                        horizontal=10, vertical=5
                                                    ),
                                                    border_radius=20,
                                                    bgcolor="#0d1a27",
                                                    border=ft.border.all(1, "#1a2e40"),
                                                    content=ft.Text(
                                                        category,
                                                        color="white",
                                                        size=9,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ),
                                                ft.Container(
                                                    width=32,
                                                    height=32,
                                                    border_radius=8,
                                                    bgcolor="#0d1a27",
                                                    border=ft.border.all(1, "#1a2e40"),
                                                    alignment=ft.Alignment(0, 0),
                                                    ink=is_accessible,
                                                    on_click=on_edit,
                                                    content=ft.Icon(
                                                        ft.Icons.EDIT_OUTLINED,
                                                        color="#657188",
                                                        size=14,
                                                    ),
                                                ),
                                                ft.Container(
                                                    width=32,
                                                    height=32,
                                                    border_radius=8,
                                                    bgcolor="#0d1a27",
                                                    border=ft.border.all(1, "#1a2e40"),
                                                    alignment=ft.Alignment(0, 0),
                                                    ink=is_accessible,
                                                    on_click=on_delete,
                                                    content=ft.Icon(
                                                        ft.Icons.DELETE_OUTLINE_ROUNDED,
                                                        color="#657188",
                                                        size=14,
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    name,
                                    color="white",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                metric_column("STOCK", f"{stock} {unit}", stock_color),
                                metric_column(
                                    "PRICE", f"Rs.{int(price):,}.00", "white", end=True
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20, vertical=6),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                metric_column("BRAND", brand, "white"),
                                metric_column("TYPE", ptype, CYAN, end=True),
                            ],
                        ),
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(left=20, right=20, top=10, bottom=20),
                        alignment=ft.Alignment(0, 1),
                        content=ft.Container(
                            height=38,
                            border_radius=8,
                            bgcolor=CYAN if is_accessible else "#3d4a5c",
                            alignment=ft.Alignment(0, 0),
                            ink=is_accessible,
                            on_click=on_manage_stock if is_accessible else None,
                            content=ft.Text(
                                "MANAGE STOCK"
                                if is_accessible
                                else "LOCKED (PRO REQUIRED)",
                                color="#02101a" if is_accessible else "#141b27",
                                size=9,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ),
                ],
            ),
        )

    def metric_column(label, value, color, end=False):
        return ft.Column(
            spacing=4,
            horizontal_alignment=(
                ft.CrossAxisAlignment.END if end else ft.CrossAxisAlignment.START
            ),
            controls=[
                ft.Text(label, color="#4a5568", size=8, weight=ft.FontWeight.BOLD),
                ft.Text(
                    value,
                    color=color,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def filter_products(e=None):
        search_field = search_value.current
        query = ((search_field.value if search_field else "") or "").strip().lower()
        products_grid.controls.clear()
        filtered = [
            p
            for p in all_products
            if not query
            or query in (p.get("product_name") or "").lower()
            or query in (p.get("brand") or "").lower()
        ]

        empty_state_container.visible = not filtered
        for product in filtered:
            products_grid.controls.append(product_card(product))

        if page.route == view_route:
            page.update()

    content_area = ft.Container(
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=products_grid,
    )
    empty_state_container = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=empty_state,
        visible=False,
    )

    header_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=5,
                controls=[
                    ft.Text(
                        "Products",
                        color="white",
                        size=34,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "BUSINESS PRODUCT CATALOG",
                        color="#59657a",
                        size=9,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
            ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=260,
                        height=46,
                        border_radius=12,
                        bgcolor="#070d17",
                        border=ft.border.all(1, "#1a2535"),
                        padding=ft.padding.symmetric(horizontal=14),
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.SEARCH_ROUNDED,
                                    color="#3d4a5c",
                                    size=18,
                                ),
                                ft.TextField(
                                    ref=search_value,
                                    hint_text="Search products...",
                                    hint_style=ft.TextStyle(
                                        color="#3d4a5c", size=12
                                    ),
                                    border=ft.InputBorder.NONE,
                                    color="white",
                                    text_size=12,
                                    expand=True,
                                    on_change=filter_products,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        width=140,
                        height=46,
                        border_radius=12,
                        bgcolor=CYAN,
                        alignment=ft.Alignment(0, 0),
                        ink=True,
                        on_click=lambda e: page.go(
                            f"/businesses/{business_id}/products/add"
                        ),
                        content=ft.Row(
                            tight=True,
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.ADD_ROUNDED,
                                    color="#02101a",
                                    size=18,
                                ),
                                ft.Text(
                                    "ADD PRODUCT",
                                    color="#02101a",
                                    size=9,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )
    header_section = ft.Column(spacing=14, controls=[header_row])

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=36, right=36, top=0, bottom=24),
        content=ft.Column(
            spacing=18,
            controls=[
                header_section,
                ft.Stack(
                    expand=True,
                    controls=[
                        content_area,
                        empty_state_container,
                    ],
                ),
            ],
        ),
    )

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

        products_grid.controls.clear()
        inv_map.clear()
        inventory_by_product.clear()

        try:
            data, status = api_client.get_inventory(business_id, limit=1000)
            if status == 200 and isinstance(data, list):
                for inv in data:
                    product_id = str(inv.get("product_id"))
                    inv_map[product_id] = inv.get("id")
                    inventory_by_product[product_id] = inv
        except Exception:
            pass

        try:
            data, status = api_client.get_products(business_id, skip=state["current_page"] * state["limit"], limit=state["limit"])
            if status == 401:
                api_client.set_token(None)
                if page.route == view_route:
                    page.go("/login")
                return

            if status == 200:
                if page.route != view_route:
                    return
                all_products.clear()
                all_products.extend(data if isinstance(data, list) else [])

                has_inaccessible = any(
                    not product.get("is_accessible", True)
                    for product in all_products
                )
                header_section.controls = (
                    [header_row, warning_banner] if has_inaccessible else [header_row]
                )
                filter_products()
                pagination_container.content = PaginationControls(page, state["current_page"], len(all_products), state["limit"], on_prev, on_next)
                page.update()
                return
        except Exception as ex:
            print("PRODUCTS ERROR:", ex)
            empty_state_container.visible = True

        if page.route == view_route:
            page.update()

    load_data()
    main_content.content.controls.append(pagination_container)
    return main_content

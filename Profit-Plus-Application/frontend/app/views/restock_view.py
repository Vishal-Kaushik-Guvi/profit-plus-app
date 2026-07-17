import flet as ft
from datetime import datetime
from app.api_client import api_client

BG = "#020710"
SIDEBAR_BG = "#070816"
BORDER = "#172231"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"
INPUT_BG = "#080d17"


def RestockView(page: ft.Page, business_id: str, inventory_id: str):


    error_text = ft.Text("", color="#fb7185", size=12)

    # ── Section header ────────────────────────────────────────────
    def section_header(title):
        return ft.Row(
            spacing=14,
            controls=[
                ft.Container(
                    width=8, height=8,
                    border_radius=4, bgcolor=CYAN,
                ),
                ft.Text(title, color=CYAN, size=10,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True, height=1, bgcolor=BORDER),
            ],
        )

    # ── Input field builder ───────────────────────────────────────
    def input_field(label, hint="", required=False,
                    keyboard_type=None, value="", is_date=False):
        label_text = f"{label} *" if required else label
        
        input_filter = None
        if keyboard_type == ft.KeyboardType.NUMBER:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$")
        elif is_date:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9-]*$")

        tf = ft.TextField(
            value=value,
            hint_text=hint,
            color="white",
            hint_style=ft.TextStyle(color="#3d4a5c", size=12),
            text_size=13,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            focused_border_color=CYAN,
            border_radius=8,
            keyboard_type=keyboard_type,
            input_filter=input_filter,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
        )
        return ft.Column(
            expand=True,
            spacing=6,
            controls=[
                ft.Text(label_text, color="#8792a7", size=9,
                        weight=ft.FontWeight.BOLD),
                tf,
            ],
        ), tf

    def dropdown_field(label, options, required=False):
        label_text = f"{label} *" if required else label
        dd = ft.Dropdown(
            options=[ft.dropdown.Option(o) for o in options],
            color="white",
            bgcolor=INPUT_BG,
            border_color=BORDER,
            focused_border_color=CYAN,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            text_size=13,
        )
        return ft.Column(
            expand=True,
            spacing=6,
            controls=[
                ft.Text(label_text, color="#8792a7", size=9,
                        weight=ft.FontWeight.BOLD),
                dd,
            ],
        ), dd

    # ── Product dropdown ──────────────────────────────────────────
    product_dropdown_col, product_dd = dropdown_field(
        "SELECT PRODUCT", [], required=True)
    all_inventory = []  # store fetched inventory list

    # ── Stock Configuration ───────────────────────────────────────
    stock_col, stock_tf = input_field(
        "ADD STOCK", "e.g. 8", required=True,
        keyboard_type=ft.KeyboardType.NUMBER)

    unit_options = ["Pieces (pcs)", "Kilograms (kg)",
                    "Litres (ltr)", "Metres (mtr)",
                    "Grams (g)", "Boxes", "Dozens", "Units"]
    unit_col, unit_dd = dropdown_field("UNIT TYPE", unit_options)

    min_stock_col, min_stock_tf = input_field(
        "MIN STOCK ALERT", "e.g. 5",
        keyboard_type=ft.KeyboardType.NUMBER)

    # ── Pricing & Tax ─────────────────────────────────────────────
    purchase_col, purchase_tf = input_field(
        "PURCHASE PRICE", "500",
        keyboard_type=ft.KeyboardType.NUMBER)

    selling_col, selling_tf = input_field(
        "SELLING PRICE", "300",
        keyboard_type=ft.KeyboardType.NUMBER)

    discount_col, discount_tf = input_field(
        "DISCOUNT PRICE", "0.00",
        keyboard_type=ft.KeyboardType.NUMBER)

    tax_col, tax_tf = input_field(
        "TAX (%)", "18",
        keyboard_type=ft.KeyboardType.NUMBER)

    # ── Lifecycle & Tracking ──────────────────────────────────────
    today_str = datetime.today().strftime("%d-%m-%Y")
    restock_date_col, restock_date_tf = input_field(
        "RESTOCK DATE", "dd-mm-yyyy", value=today_str, is_date=True)

    batch_col, batch_tf = input_field(
        "BATCH NUMBER", "BATCH-001")

    warranty_col, warranty_tf = input_field(
        "WARRANTY (MONTHS)", "12",
        keyboard_type=ft.KeyboardType.NUMBER)

    # ── Submit button ─────────────────────────────────────────────
    confirm_btn = ft.Container(
        height=50,
        padding=ft.padding.symmetric(horizontal=28),
        border_radius=12,
        bgcolor=CYAN,
        alignment=ft.Alignment(0, 0),
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=24, color="#2816cdf2", offset=ft.Offset(0, 6)
        ),
        content=ft.Row(
            tight=True, spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_ROUNDED, color="#02101a", size=18),
                ft.Text("CONFIRM RESTOCK", color="#02101a", size=11,
                        weight=ft.FontWeight.BOLD),
            ],
        ),
    )

    def reset_confirm_btn():
        confirm_btn.content = ft.Row(
            tight=True, spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_ROUNDED, color="#02101a", size=18),
                ft.Text("CONFIRM RESTOCK", color="#02101a", size=11,
                        weight=ft.FontWeight.BOLD),
            ],
        )

    def submit(e):
        error_text.value = ""

        # Validate
        selected_product_label = product_dd.value or ""
        stock_val = (stock_tf.value or "").strip()

        if not selected_product_label:
            error_text.value = "Please select a product"
            page.update()
            return
        if not stock_val:
            error_text.value = "Stock quantity is required"
            page.update()
            return

        # Find inventory_id from selected product name
        target_inv_id = inventory_id  # use route param if available
        for inv in all_inventory:
            prod = inv.get("product") or {}
            label = f"{prod.get('product_name', '')} ({prod.get('brand', '') or 'N/A'})"
            if label == selected_product_label:
                target_inv_id = inv.get("id", inventory_id)
                break

        confirm_btn.content = ft.ProgressRing(
            width=20, height=20, stroke_width=2, color="#02101a"
        )
        page.update()

        try:
            payload = {
                "stock_quantity": float(stock_val or 0),
                "minimum_stock_alert": float(
                    (min_stock_tf.value or "0").strip() or 0),
                "purchase_price": float(
                    (purchase_tf.value or "0").strip() or 0),
                "selling_price": float(
                    (selling_tf.value or "0").strip() or 0),
                "discount_price": float(
                    (discount_tf.value or "0").strip() or 0),
                "tax_percentage": float(
                    (tax_tf.value or "0").strip() or 0),
                "unit": (unit_dd.value or "").split(
                    " ")[0].lower() if unit_dd.value else None,
                "last_restock_date": (
                    restock_date_tf.value or "").strip() or None,
                "batch_number": (
                    batch_tf.value or "").strip() or None,
                "warranty_months": int(
                    (warranty_tf.value or "0").strip() or 0) or None,
            }
            data, status_code = api_client.update_inventory(
                target_inv_id, payload)
        except Exception:
            error_text.value = "Unable to connect to server"
            reset_confirm_btn()
            page.update()
            return

        if status_code in (200, 201):
            page.go(f"/businesses/{business_id}/inventory")
            return

        if status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        error_text.value = data.get("detail", "Failed to update inventory")
        reset_confirm_btn()
        page.update()

    confirm_btn.on_click = submit

    # ── Form card ─────────────────────────────────────────────────
    form_card = ft.Container(
        border_radius=16,
        bgcolor="#060c18",
        border=ft.border.all(1, "#131b2a"),
        padding=ft.padding.only(left=40, right=40, top=32, bottom=36),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=28,
            controls=[
                # Title row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text("RESTOCK INVENTORY",
                                        color="white", size=26,
                                        weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=7, height=7,
                                            border_radius=4,
                                            bgcolor=CYAN),
                                        ft.Text(
                                            "R E P L E N I S H   S T O C K   A N D   U P D A T E   P R I C I N G",
                                            color="#59657a", size=7,
                                            weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            width=7, height=7,
                                            border_radius=4,
                                            bgcolor=CYAN),
                                    ],
                                ),
                            ],
                        ),
                        # Back button
                        ft.Container(
                            height=34,
                            padding=ft.padding.symmetric(horizontal=16),
                            border_radius=8,
                            border=ft.border.all(1, BORDER),
                            alignment=ft.Alignment(0, 0),
                            ink=True,
                            on_click=lambda e: page.go(
                                f"/businesses/{business_id}/inventory"),
                            content=ft.Text("BACK", color="#8a95aa",
                                            size=9, weight=ft.FontWeight.BOLD),
                        ),
                    ],
                ),

                ft.Divider(color="#131b29", height=1),

                # Section 1 — Catalog Linking
                section_header("CATALOG LINKING"),
                product_dropdown_col,

                # Section 2 — Stock Configuration
                section_header("STOCK CONFIGURATION"),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[stock_col, unit_col, min_stock_col],
                ),

                # Section 3 — Pricing & Tax
                section_header("PRICING & TAX"),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        purchase_col, selling_col,
                        discount_col, tax_col,
                    ],
                ),

                # Section 4 — Lifecycle & Tracking
                section_header("LIFECYCLE & TRACKING (OPTIONAL)"),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        restock_date_col, batch_col,
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        warranty_col,
                        ft.Container(expand=True),
                        ft.Container(expand=True),
                    ],
                ),

                ft.Container(height=4),

                # Bottom action row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        error_text,
                        confirm_btn,
                    ],
                ),
            ],
        ),
    )

    # ── Main content ──────────────────────────────────────────────
    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=36, right=36, top=32, bottom=24),
        content=ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[form_card],
                    ),
                ),
            ],
        ),
    )

    # ── Load data ─────────────────────────────────────────────────
    def load_data():
        # Load business name

        # Load inventory list to populate product dropdown
        try:
            data, status = api_client.get_inventory(business_id)
            if status == 200 and isinstance(data, list):
                all_inventory.clear()
                all_inventory.extend(data)

                options = []
                preselect = None
                for inv in data:
                    prod = inv.get("product") or {}
                    name = prod.get("product_name") or "Unknown"
                    brand = prod.get("brand") or "N/A"
                    label = f"{name} ({brand})"
                    options.append(ft.dropdown.Option(label))
                    # If we came from a specific inventory_id, preselect it
                    if inv.get("id") == inventory_id:
                        preselect = label

                product_dd.options = options
                if preselect:
                    product_dd.value = preselect

        except Exception:
            pass

        page.update()

    load_data()

    return main_content

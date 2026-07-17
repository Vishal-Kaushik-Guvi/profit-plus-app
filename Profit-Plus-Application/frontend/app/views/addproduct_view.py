import flet as ft
from app.api_client import api_client

BG = "#020710"
SIDEBAR_BG = "#070816"
BORDER = "#172231"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"
INPUT_BG = "#080d17"


def AddProductView(page: ft.Page, business_id: str, product_id: str = None):

    error_text = ft.Text("", color="#fb7185", size=12)
    is_edit_mode = bool(product_id)



    # ── Form field builder ────────────────────────────────────────
    def field(label, hint="", required=False, keyboard_type=None,
              multiline=False, min_lines=1, max_lines=1):
        label_text = f"{label} *" if required else label
        
        input_filter = None
        if keyboard_type == ft.KeyboardType.NUMBER:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$")

        return ft.Column(
            expand=True,
            spacing=7,
            controls=[
                ft.Text(label_text, color="#8792a7", size=10,
                        weight=ft.FontWeight.BOLD),
                ft.TextField(
                    hint_text=hint,
                    color="white",
                    hint_style=ft.TextStyle(color="#3d4a5c", size=13),
                    text_size=13,
                    bgcolor=INPUT_BG,
                    border_color=BORDER,
                    focused_border_color=CYAN,
                    border_radius=10,
                    multiline=multiline,
                    min_lines=min_lines,
                    max_lines=max_lines,
                    keyboard_type=keyboard_type,
                    input_filter=input_filter,
                    content_padding=ft.padding.symmetric(
                        horizontal=16, vertical=14),
                ),
            ],
        )

    def dropdown_field(label, options, required=False):
        label_text = f"{label} *" if required else label
        return ft.Column(
            expand=True,
            spacing=7,
            controls=[
                ft.Text(label_text, color="#8792a7", size=10,
                        weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    options=[ft.dropdown.Option(o) for o in options],
                    color="white",
                    bgcolor=INPUT_BG,
                    border_color=BORDER,
                    focused_border_color=CYAN,
                    border_radius=10,
                    content_padding=ft.padding.symmetric(
                        horizontal=16, vertical=14),
                    text_size=13,
                ),
            ],
        )

    def section_header(number, title):
        return ft.Row(
            spacing=14,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=22, height=22,
                            border_radius=6,
                            bgcolor="#0d1a27",
                            border=ft.border.all(1, "#1a2e40"),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(number, color=CYAN, size=9,
                                            weight=ft.FontWeight.BOLD),
                        ),
                        ft.Text(title, color=CYAN, size=10,
                                weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Container(expand=True, height=1, bgcolor=BORDER),
            ],
        )

    # ── Form fields ───────────────────────────────────────────────
    product_name = field(
        "PRODUCT NAME", "e.g. Samsung Galaxy S24", required=True)
    category = field("CATEGORY", "e.g. Electronics, Clothing, Medical")
    brand = field("BRAND", "e.g. Samsung, Nike, Cipla")
    description = field("DESCRIPTION", "Short product description...",
                        multiline=True, min_lines=3, max_lines=3)
    hsn_code = field("HSN CODE", "e.g. 8517")
    tax_pct = field("TAX %", "e.g. 18",
                    keyboard_type=ft.KeyboardType.NUMBER)
    color_variant = field("DEFAULT COLOR", "e.g. Black, Blue")
    size_variant = field("DEFAULT SIZE", "e.g. M, 42, 1L")
    business_type = dropdown_field(
        "BUSINESS TYPE",
        ["General", "Electronics", "Clothing & Fashion",
         "Medical & Pharmacy", "Food & Grocery", "Mobile & Accessories",
         "Footwear", "Furniture", "Books & Stationery", "Other"],
    )

    # ── Helper to get field value ─────────────────────────────────
    def val(f):
        return (f.controls[1].value or "").strip()

    def ddval(f):
        return (f.controls[1].value or "").strip()

    # ── Submit button ─────────────────────────────────────────────
    submit_btn = ft.Container(
        width=220, height=52,
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
                ft.Text(
                    "UPDATE PRODUCT" if is_edit_mode else "SAVE PRODUCT",
                    color="#02101a", size=11,
                        weight=ft.FontWeight.BOLD),
            ],
        ),
    )

    def reset_btn():
        submit_btn.content = ft.Row(
            tight=True, spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_ROUNDED, color="#02101a", size=18),
                ft.Text(
                    "UPDATE PRODUCT" if is_edit_mode else "SAVE PRODUCT",
                    color="#02101a", size=11,
                        weight=ft.FontWeight.BOLD),
            ],
        )

    def submit(e):
        error_text.value = ""

        if not val(product_name):
            error_text.value = "Product name is required"
            page.update()
            return

        submit_btn.content = ft.ProgressRing(
            width=20, height=20, stroke_width=2, color="#02101a"
        )
        page.update()

        try:
            payload = {
                "product_name": val(product_name),
                "category": val(category),
                "brand": val(brand),
                "description": val(description),
                "hsn_code": val(hsn_code),
                "tax_percentage": float(val(tax_pct) or 0),
                "color": val(color_variant),
                "size": val(size_variant),
                "business_type": ddval(business_type),
            }
            if is_edit_mode:
                data, status_code = api_client.update_product(product_id, payload)
            else:
                data, status_code = api_client.create_product(
                    business_id=business_id,
                    **payload,
                )
        except Exception:
            error_text.value = "Unable to connect to the server"
            reset_btn()
            page.update()
            return

        if status_code == 200:
            page.go(f"/businesses/{business_id}/products")
            return

        if status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        error_text.value = data.get("detail", "Failed to save product")
        reset_btn()
        page.update()

    submit_btn.on_click = submit

    # ── Form layout ───────────────────────────────────────────────
    form = ft.Column(
        spacing=30,
        controls=[
            # Section 1 — Identity
            section_header("01", "I D E N T I T Y"),
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[product_name, category],
            ),
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[brand, business_type],
            ),
            description,

            # Section 2 — Tax & Compliance
            section_header("02", "T A X   &   C O M P L I A N C E"),
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[hsn_code, tax_pct],
            ),

            # Section 3 — Variants (optional)
            section_header("03", "V A R I A N T S   ( O P T I O N A L )"),
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[color_variant, size_variant],
            ),

            # Action row
            ft.Container(height=8),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    error_text,
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.Container(
                                width=110, height=52,
                                border_radius=12,
                                border=ft.border.all(1, BORDER),
                                alignment=ft.Alignment(0, 0),
                                ink=True,
                                on_click=lambda e: page.go(
                                    f"/businesses/{business_id}/products"),
                                content=ft.Text("CANCEL", color="#8a95aa",
                                                size=10,
                                                weight=ft.FontWeight.BOLD),
                            ),
                            submit_btn,
                        ],
                    ),
                ],
            ),
            ft.Container(height=20),
        ],
    )

    # ── Main content ──────────────────────────────────────────────
    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=60, right=60, top=40, bottom=30),
        content=ft.Column(
            spacing=28,
            controls=[
                # Page header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(
                                        "EDIT PRODUCT" if is_edit_mode else "ADD PRODUCT",
                                        color="white",
                                        size=30, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=7, height=7,
                                            border_radius=4, bgcolor=CYAN),
                                        ft.Text(
                                            "U P D A T E   P R O D U C T   D E T A I L S"
                                            if is_edit_mode
                                            else "R E G I S T E R   A   N E W   P R O D U C T   T O   Y O U R   C A T A L O G",
                                            color="#69758b", size=7,
                                            weight=ft.FontWeight.BOLD),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Divider(color="#131b29", height=1),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[form],
                    ),
                ),
            ],
        ),
    )

    # ── Load business info ────────────────────────────────────────
    def load_product():
        if not is_edit_mode:
            return

        try:
            data, status = api_client.get_product(product_id)
        except Exception:
            error_text.value = "Unable to load product"
            page.update()
            return

        if status == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        if status != 200:
            error_text.value = data.get("detail", "Unable to load product")
            page.update()
            return

        product_name.controls[1].value = data.get("product_name") or ""
        category.controls[1].value = data.get("category") or ""
        brand.controls[1].value = data.get("brand") or ""
        description.controls[1].value = data.get("description") or ""
        hsn_code.controls[1].value = data.get("hsn_code") or ""
        tax_pct.controls[1].value = str(data.get("tax_percentage") or "")
        color_variant.controls[1].value = data.get("color") or ""
        size_variant.controls[1].value = data.get("size") or ""
        business_type.controls[1].value = data.get("business_type") or None
        page.update()

    load_product()

    return main_content

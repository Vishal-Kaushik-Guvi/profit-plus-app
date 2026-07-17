from datetime import datetime

import flet as ft
import time
import random

from app.api_client import api_client
from app.theme import Colors



BG = "#030711"
SIDEBAR_BG = "#070816"
PANEL_BG = "#cc07101c"
PANEL_BORDER = "#182232"
CYAN = "#16cdf2"
PURPLE = "#6d22d9"


def MyBusinessView(page: ft.Page):
    businesses_column = ft.Column(spacing=14)
    directory_panel = ft.Container(expand=True)
    error_text = ft.Text("", color="#fb7185", size=12)
    status_text = ft.Text("", color="#34d399", size=12)
    def field_style():
        return ft.TextStyle(
            color="#8c98ad",
            size=10,
            weight=ft.FontWeight.BOLD,
        )

    def input_field(label, hint="", width=250, keyboard_type=None):
        input_filter = None
        if keyboard_type == ft.KeyboardType.NUMBER:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$")

        return ft.TextField(
            label=label,
            hint_text=hint,
            width=width,
            height=54,
            color="white",
            text_size=13,
            label_style=field_style(),
            border_color=PANEL_BORDER,
            focused_border_color=CYAN,
            bgcolor="#070b14",
            border_radius=8,
            keyboard_type=keyboard_type,
            input_filter=input_filter,
        )

    business_name_field = input_field("BUSINESS NAME", "Your shop name", 330)
    phone_field = input_field(
        "PHONE", "1234567890", keyboard_type=ft.KeyboardType.NUMBER
    )
    email_field = input_field("EMAIL", "shop@example.com")
    gst_field = input_field("GST", "Optional")
    address_field = input_field("ADDRESS", "Street / area", 330)
    city_field = input_field("CITY")
    pincode_field = input_field(
        "PINCODE", keyboard_type=ft.KeyboardType.NUMBER
    )
    state_field = input_field("STATE")
    country_field = input_field("COUNTRY", "India")

    def action_button(text, on_click=None, width=218):
        return ft.Container(
            width=width,
            height=54,
            border_radius=12,
            bgcolor=CYAN,
            alignment=ft.Alignment(0, 0),
            ink=True,
            on_click=on_click,
            shadow=ft.BoxShadow(
                blur_radius=30,
                color="#2516cdf2",
                offset=ft.Offset(0, 9),
            ),
            content=ft.Row(
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Icon(ft.Icons.ADD_ROUNDED, color="#02101a", size=22),
                    ft.Text(
                        text,
                        color="#02101a",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
        )

    create_button = action_button("CREATE BUSINESS", width=210)

    def set_create_button(text):
        create_button.content = ft.Row(
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.ADD_ROUNDED, color="#02101a", size=20),
                ft.Text(
                    text,
                    color="#02101a",
                    weight=ft.FontWeight.BOLD,
                    size=11,
                ),
            ],
        )

    def set_create_loading():
        create_button.content = ft.ProgressRing(
            width=18,
            height=18,
            stroke_width=2,
            color="#02101a",
        )

    def business_card(business):
        business_name = business.get("business_name") or "Untitled business"
        initials = "".join(
            part[0] for part in business_name.split()[:2]
        ).upper() or "B"
        location = ", ".join(
            part for part in [
                business.get("city"),
                business.get("state"),
            ] if part
        ) or business.get("country") or "Not provided"
        contact = business.get("email") or business.get("phone") or "Not provided"
        gst_number = business.get("gst") or "NOT PROVIDED"
        plan = business.get("subscription_type") or "FREE"

        def format_date(raw_date, include_time=False):
            if not raw_date:
                return "NOT AVAILABLE"
            try:
                parsed = datetime.fromisoformat(
                    str(raw_date).replace("Z", "+00:00")
                )
                date_text = parsed.strftime("%d/%m/%Y")
                if include_time:
                    date_text += f"  {parsed.strftime('%I:%M %p')}"
                return date_text
            except (TypeError, ValueError):
                return str(raw_date)

        def detail_item(label, value, width=165):
            return ft.Container(
                width=width,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(
                            label,
                            color="#536078",
                            size=8,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            value,
                            color="#dbe2ed",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
            )

        logo_url = api_client.absolute_url(business.get("logo_url"))
        business_id = business.get("id")

        def enter_business(e):
            if business_id:
                page.go(f"/businesses/{business_id}/dashboard")

        logo_content = (
            ft.Image(
                src=logo_url,
                width=66,
                height=66,
                fit=ft.BoxFit.COVER,
                border_radius=33,
            )
            if logo_url
            else ft.Text(
                initials,
                color="white",
                size=18,
                weight=ft.FontWeight.BOLD,
            )
        )

        return ft.Container(
            height=278,
            border_radius=42,
            bgcolor="#070d17",
            border=ft.border.all(1, "#202a39"),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(
                            left=38, right=28, top=38, bottom=30
                        ),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=22,
                                    controls=[
                                        ft.Container(
                                            width=72,
                                            height=72,
                                            border_radius=36,
                                            bgcolor="#172334",
                                            border=ft.border.all(1, "#27364a"),
                                            alignment=ft.Alignment(0, 0),
                                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                            content=logo_content,
                                        ),
                                        ft.Column(
                                            spacing=7,
                                            controls=[
                                                ft.Text(
                                                    business_name,
                                                    color="white",
                                                    size=28,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    f"GSTID:  {gst_number}",
                                                    color="#68758a",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        detail_item(
                                            "OPERATIONAL SINCE",
                                            format_date(
                                                business.get("created_at"),
                                                include_time=True,
                                            ),
                                            180,
                                        ),
                                        detail_item(
                                            "CONTACT NODE", contact, 170
                                        ),
                                        detail_item(
                                            "LOCATION", location, 150
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        width=285,
                        padding=ft.padding.all(38),
                        border=ft.border.only(
                            left=ft.BorderSide(1, "#182231")
                        ),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                            colors=["#09111d", "#0b1822"],
                        ),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Container(
                                    height=58,
                                    padding=ft.padding.symmetric(horizontal=18),
                                    border_radius=14,
                                    bgcolor="#151e2b",
                                    border=ft.border.all(1, "#202b3a"),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(
                                                "PLAN LEVEL",
                                                color="#66738a",
                                                size=9,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Container(
                                                padding=ft.padding.symmetric(
                                                    horizontal=16, vertical=7
                                                ),
                                                border_radius=18,
                                                bgcolor="#103624" if plan == "PRO" else "#2a3542",
                                                border=ft.border.all(
                                                    1, "#16a34a" if plan == "PRO" else "#3b4857"
                                                ),
                                                content=ft.Text(
                                                    plan,
                                                    color="#4ade80" if plan == "PRO" else "#d7dee8",
                                                    size=9,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "EXPIRES",
                                            color="#56637a",
                                            size=8,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            format_date(
                                                business.get(
                                                    "subscription_expiry"
                                                )
                                            )
                                            if business.get(
                                                "subscription_expiry"
                                            )
                                            else "NO EXPIRY",
                                            color="#d9e0ea",
                                            size=10,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    height=64,
                                    border_radius=16,
                                    bgcolor="#151e29",
                                    border=ft.border.all(1, "#2b3746"),
                                    alignment=ft.Alignment(0, 0),
                                    ink=True,
                                    on_click=enter_business,
                                    content=ft.Text(
                                        "E N T E R",
                                        color="white",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def show_form(e=None):
        page.go("/businesses/create")

    def hide_form(e=None):
        form_panel.visible = False
        directory_panel.visible = True
        error_text.value = ""
        status_text.value = ""
        page.update()

    empty_state = ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        controls=[
            ft.Container(
                width=88,
                height=88,
                border_radius=44,
                bgcolor="#10212c",
                border=ft.border.all(1, "#1a3543"),
                alignment=ft.Alignment(0, 0),
                content=ft.Icon(
                    ft.Icons.BUSINESS_OUTLINED,
                    color="#395064",
                    size=38,
                ),
            ),
            ft.Container(height=8),
            ft.Text(
                "NO BUSINESSES FOUND",
                color="white",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(
                width=390,
                content=ft.Text(
                    "Your business portfolio is currently empty. Initialize your\n"
                    "first business unit to begin management.",
                    color="#59657a",
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            ft.Container(height=12),
            action_button("CREATE BUSINESS", show_form),
        ],
    )

    def render_businesses(businesses):
        businesses_column.controls.clear()
        if not businesses:
            directory_panel.content = empty_state
            return

        for business in businesses:
            businesses_column.controls.append(business_card(business))

        directory_panel.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=[
                ft.Text(
                    f"{len(businesses)} ACTIVE "
                    f"{'UNIT' if len(businesses) == 1 else 'UNITS'}",
                    color="#69758b",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                ),
                businesses_column,
            ],
        )

    def load_businesses():
        error_text.value = ""
        try:
            data, status_code = api_client.get_my_businesses()
        except Exception:
            error_text.value = "Unable to connect to the server"
            render_businesses([])
            page.update()
            return

        if status_code == 200:
            render_businesses(data)
        elif status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return
        else:
            error_text.value = data.get(
                "detail", "Failed to load businesses"
            )
            render_businesses([])

        page.update()

    def load_current_user():
        try:
            data, status_code = api_client.get_me()
        except Exception:
            page.update()
            return

        if status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        if status_code == 200:
            name = (data.get("name") or "").strip()
            email = (data.get("email") or "").strip()
            display_name = name or email.split("@")[0] or "Profit Plus User"
            name_parts = display_name.split()
            initials = "".join(part[0] for part in name_parts[:2]).upper()

        else:
            pass
        page.update()

    def create_business_clicked(e):
        error_text.value = ""
        status_text.value = ""
        business_name = (business_name_field.value or "").strip()

        if not business_name:
            error_text.value = "Enter your business name"
            page.update()
            return

        set_create_loading()
        page.update()

        try:
            data, status_code = api_client.create_business(
                business_name=business_name,
                phone=(phone_field.value or "").strip(),
                email=(email_field.value or "").strip(),
                address=(address_field.value or "").strip(),
                city=(city_field.value or "").strip(),
                pincode=(pincode_field.value or "").strip(),
                state=(state_field.value or "").strip(),
                country=(country_field.value or "").strip(),
                gst=(gst_field.value or "").strip(),
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            set_create_button("CREATE BUSINESS")
            page.update()
            return

        set_create_button("CREATE BUSINESS")

        if status_code == 200:
            for field in [
                business_name_field,
                phone_field,
                email_field,
                gst_field,
                address_field,
                city_field,
                pincode_field,
                state_field,
                country_field,
            ]:
                field.value = ""
            status_text.value = "Business created successfully"
            form_panel.visible = False
            directory_panel.visible = True
            load_businesses()
            return

        if status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        error_text.value = data.get("detail", "Failed to add business")
        page.update()

    create_button.on_click = create_business_clicked



    form_panel = ft.Container(
        expand=True,
        visible=False,
        padding=30,
        border_radius=28,
        bgcolor=PANEL_BG,
        border=ft.border.all(1, PANEL_BORDER),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text(
                                    "CREATE BUSINESS",
                                    color="white",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Register a new business unit.",
                                    color="#69758b",
                                    size=12,
                                ),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color="#69758b",
                            on_click=hide_form,
                        ),
                    ],
                ),
                ft.Divider(color=PANEL_BORDER, height=1),
                ft.Row(
                    wrap=True,
                    spacing=14,
                    run_spacing=14,
                    controls=[
                        business_name_field,
                        phone_field,
                        email_field,
                        gst_field,
                        address_field,
                        city_field,
                        pincode_field,
                        state_field,
                        country_field,
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[status_text, error_text],
                        ),
                        create_button,
                    ],
                ),
            ],
        ),
    )

    directory_panel.padding = 34
    directory_panel.border_radius = 48
    directory_panel.bgcolor = PANEL_BG
    directory_panel.border = ft.border.all(1, PANEL_BORDER)

    main_header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=5,
                controls=[
                    ft.Text(
                        "My Businesses",
                        color="white",
                        size=39,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "B U S I N E S S   D I R E C T O R Y  ·  A C T I V E   U N I T S",
                        color="#657087",
                        size=9,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
            action_button("CREATE BUSINESS", show_form),
        ],
    )

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=108, right=110, top=62, bottom=22),
        content=ft.Column(
            spacing=43,
            controls=[
                main_header,
                ft.Container(
                    expand=True,
                    content=ft.Stack(
                        expand=True,
                        controls=[directory_panel, form_panel],
                    ),
                ),
            ],
        ),
    )

    stars = [
        (38, 54, 2),
        (94, 120, 2),
        (158, 29, 1),
        (206, 86, 2),
        (274, 45, 1),
        (348, 142, 2),
        (441, 59, 1),
        (518, 112, 2),
        (611, 35, 2),
        (704, 91, 1),
        (790, 49, 2),
        (876, 129, 1),
        (952, 72, 2),
        (1031, 22, 1),
        (1098, 114, 2),
        (82, 326, 1),
        (235, 274, 2),
        (491, 353, 1),
        (744, 305, 2),
        (1002, 381, 1),
        (1120, 292, 2),
    ]
    star_controls = [
        ft.Container(
            left=x,
            top=y,
            width=size,
            height=size,
            border_radius=size,
            bgcolor="#9aa7bd",
        )
        for x, y, size in stars
    ]

    background = ft.Stack(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=ft.RadialGradient(
                    center=ft.Alignment(0.75, 0.35),
                    radius=1.2,
                    colors=["#071621", BG],
                ),
            ),
            *star_controls,
        ],
    )

    load_businesses()
    load_current_user()

    return main_content

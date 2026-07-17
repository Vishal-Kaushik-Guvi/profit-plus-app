import flet as ft
import time
import random
import os

from app.api_client import api_client


BG = "#030711"
SIDEBAR_BG = "#070816"
BORDER = "#1a2231"
INPUT_BG = "#080d17"
CYAN = "#16cdf2"
PURPLE = "#6d22d9"


def CreateBusinessView(page: ft.Page):
    error_text = ft.Text("", color="#fb7185", size=12)
    selected_logo_text = ft.Text(
        "No file chosen", color="#6d788d", size=11
    )
    selected_logo_path = {"path": ""}

    logo_file_picker = ft.FilePicker()

    async def choose_logo(e):
        files = await logo_file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["jpg", "jpeg", "png", "webp"],
        )
        if files:
            selected_logo_path["path"] = files[0].path
            selected_logo_text.value = os.path.basename(files[0].path)
        else:
            selected_logo_path["path"] = ""
            selected_logo_text.value = "No file chosen"
        page.update()

    def cancel(e=None):
        page.go("/businesses")

    def input_field(
        label,
        hint="",
        multiline=False,
        min_lines=1,
        max_lines=1,
        keyboard_type=None,
    ):
        input_filter = None
        if keyboard_type == ft.KeyboardType.NUMBER:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$")

        return ft.Column(
            expand=True,
            spacing=8,
            controls=[
                ft.Text(
                    label,
                    color="#8792a7",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.TextField(
                    hint_text=hint,
                    color="white",
                    hint_style=ft.TextStyle(
                        color="#687286",
                        size=14,
                        weight=ft.FontWeight.W_600,
                    ),
                    text_size=14,
                    multiline=multiline,
                    min_lines=min_lines,
                    max_lines=max_lines,
                    keyboard_type=keyboard_type,
                    input_filter=input_filter,
                    bgcolor=INPUT_BG,
                    border_color=BORDER,
                    focused_border_color=CYAN,
                    border_radius=12,
                    content_padding=ft.padding.symmetric(
                        horizontal=18, vertical=17
                    ),
                ),
            ],
        )

    business_name = input_field("BUSINESS NAME", "e.g. Acme Corp")
    gst = input_field("GST NUMBER", "22AAAAA0000A1Z5")
    referral = input_field(
        "REFERRAL CODE (OPTIONAL)", "E.G. X4Y9Z2"
    )
    phone = input_field(
        "PHONE NUMBER",
        "+91 00000 00000",
        keyboard_type=ft.KeyboardType.PHONE,
    )
    email = input_field(
        "EMAIL ADDRESS",
        "contact@company.com",
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    address = input_field(
        "FULL ADDRESS",
        "Street, City, State, Country...",
        multiline=True,
        min_lines=3,
        max_lines=3,
    )
    city = input_field("CITY")
    pincode = input_field(
        "PINCODE", keyboard_type=ft.KeyboardType.NUMBER
    )
    state = input_field("STATE")
    country = input_field("COUNTRY", "India")

    def value(field):
        return (field.controls[1].value or "").strip()

    submit_button = ft.Container(
        width=300,
        height=56,
        border_radius=11,
        bgcolor=CYAN,
        alignment=ft.Alignment(0, 0),
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=28, color="#3d16cdf2", offset=ft.Offset(0, 8)
        ),
        content=ft.Row(
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_ROUNDED, color="#02101a", size=19),
                ft.Text(
                    "CREATE BUSINESS",
                    color="#02101a",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
    )

    def reset_submit_button():
        submit_button.content = ft.Row(
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(
                    ft.Icons.CHECK_ROUNDED, color="#02101a", size=19
                ),
                ft.Text(
                    "CREATE BUSINESS",
                    color="#02101a",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        )

    def submit(e):
        error_text.value = ""
        if not value(business_name):
            error_text.value = "Enter your business name"
            page.update()
            return

        submit_button.content = ft.ProgressRing(
            width=19, height=19, stroke_width=2, color="#02101a"
        )
        page.update()

        try:
            data, status_code = api_client.create_business(
                business_name=value(business_name),
                gst=value(gst),
                referred_by_code=value(referral),
                phone=value(phone),
                email=value(email),
                address=value(address),
                city=value(city),
                pincode=value(pincode),
                state=value(state),
                country=value(country),
                logo_path=selected_logo_path["path"],
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            reset_submit_button()
            page.update()
            return

        if status_code == 200:
            page.go("/businesses")
            return

        if status_code == 401:
            api_client.set_token(None)
            page.go("/login")
            return

        error_text.value = data.get(
            "detail", "Failed to create business"
        )
        reset_submit_button()
        page.update()

    submit_button.on_click = submit

    def section_header(number, title):
        return ft.Row(
            spacing=14,
            controls=[
                ft.Text(
                    f"{number} {title}",
                    color=CYAN,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(expand=True, height=1, bgcolor=BORDER),
            ],
        )



    logo_picker = ft.Row(
        spacing=12,
        controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=7,
                bgcolor="#073042",
                ink=True,
                on_click=choose_logo,
                content=ft.Text(
                    "CHOOSE FILE",
                    color=CYAN,
                    size=9,
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            selected_logo_text,
        ],
    )

    form = ft.Column(
        spacing=34,
        controls=[
            section_header("01", "I D E N T I T Y"),
            ft.Row(
                spacing=32,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[business_name, gst],
            ),
            ft.Row(
                spacing=32,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "BUSINESS LOGO",
                                color="#8792a7",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                            ),
                            logo_picker,
                        ],
                    ),
                    referral,
                ],
            ),
            section_header("02", "C O M M U N I C A T I O N"),
            ft.Row(
                spacing=32,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[phone, email],
            ),
            section_header("03", "O P E R A T I O N S"),
            address,
            ft.Row(
                spacing=32,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[city, pincode],
            ),
            ft.Row(
                spacing=32,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[state, country],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[error_text, submit_button],
            ),
            ft.Container(height=22),
        ],
    )

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=88, right=88, top=50),
        content=ft.Column(
            spacing=30,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=7,
                            controls=[
                                ft.Text(
                                    "CREATE BUSINESS",
                                    color="white",
                                    size=34,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=7,
                                            height=7,
                                            border_radius=4,
                                            bgcolor=CYAN,
                                        ),
                                        ft.Text(
                                            "R E G I S T E R   A   N E W   C O M M E R C I A L   E N T I T Y",
                                            color="#69758b",
                                            size=8,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            width=96,
                            height=42,
                            border_radius=10,
                            border=ft.border.all(1, BORDER),
                            alignment=ft.Alignment(0, 0),
                            on_click=cancel,
                            ink=True,
                            content=ft.Text(
                                "CANCEL",
                                color="#8a95aa",
                                size=9,
                                weight=ft.FontWeight.BOLD,
                            ),
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

    stars = [
        (32, 48, 2), (114, 111, 1), (191, 35, 2), (275, 83, 1),
        (361, 21, 2), (446, 126, 1), (534, 57, 2), (627, 101, 1),
        (714, 31, 2), (809, 74, 1), (901, 139, 2), (1003, 46, 1),
        (1095, 96, 2), (72, 307, 1), (223, 255, 2), (401, 342, 1),
        (578, 286, 2), (769, 366, 1), (957, 277, 2), (1118, 332, 1),
        (128, 505, 2), (318, 451, 1), (515, 548, 2), (716, 479, 1),
        (895, 561, 2), (1077, 491, 1),
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
            *[
                ft.Container(
                    left=x,
                    top=y,
                    width=size,
                    height=size,
                    border_radius=size,
                    bgcolor="#a7b1c2",
                )
                for x, y, size in stars
            ],
        ],
    )

    return main_content

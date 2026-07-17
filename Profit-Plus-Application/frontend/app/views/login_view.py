import flet as ft

from app.api_client import api_client
from app.theme import Colors


def LoginView(page: ft.Page):
    
    def go_to_home(e):
        page.go("/")

    def go_to_signup(e):
        page.go("/signup")

    def forgot_password_clicked(e):
        page.go("/forgot-password")



    email_field = ft.TextField(
        label="EMAIL ADDRESS",
        hint_text="you@example.com",
        color="white",
        label_style=ft.TextStyle(
            color=Colors.TEXT_SECONDARY,
            size=11,
            weight=ft.FontWeight.BOLD,
        ),
        border_color=Colors.BORDER,
        focused_border_color=Colors.PRIMARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
    )

    password_field = ft.TextField(
        label="PASSWORD",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        color="white",
        label_style=ft.TextStyle(
            color=Colors.TEXT_SECONDARY,
            size=11,
            weight=ft.FontWeight.BOLD,
        ),
        border_color=Colors.BORDER,
        focused_border_color=Colors.PRIMARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
    )

    error_text = ft.Text("", color=Colors.DANGER, size=12)

    forgot_password_button = ft.TextButton(
        "FORGOT PASSWORD?",
        on_click=forgot_password_clicked,
        style=ft.ButtonStyle(
            color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
        ),
    )

    login_button = ft.Container(
        content=ft.Text("LOG IN", color="white", weight=ft.FontWeight.BOLD, size=14),
        bgcolor=Colors.PRIMARY,
        padding=ft.padding.symmetric(vertical=16),
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        width=350,
        ink=True,
    )

    def reset_login_button():
        login_button.content = ft.Text(
            "LOG IN",
            color="white",
            weight=ft.FontWeight.BOLD,
            size=14,
        )

    def login_clicked(e):
        error_text.value = ""

        email = (email_field.value or "").strip()
        password = password_field.value or ""

        if not email or "@" not in email:
            error_text.value = "Enter a valid email address"
            page.update()
            return

        if not password:
            error_text.value = "Enter your password"
            page.update()
            return

        login_button.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(
                    width=18,
                    height=18,
                    stroke_width=2,
                    color="white",
                )
            ],
        )
        page.update()

        try:
            data, status_code = api_client.login(email=email, password=password)
        except Exception:
            error_text.value = "Unable to connect to the server"
            reset_login_button()
            page.update()
            return

        if status_code == 200:
            api_client.set_token(data["access_token"])
            if data.get("user", {}).get("id") == "admin":
                page.go("/admin/dashboard")
            else:
                page.go("/businesses")
            return

        error_text.value = data.get("detail", "Invalid email or password")
        reset_login_button()
        page.update()

    login_button.on_click = login_clicked
    email_field.on_submit = login_clicked
    password_field.on_submit = login_clicked

    login_card = ft.Container(
        width=420,
        padding=40,
        bgcolor="#b30a0a14",
        border_radius=20,
        border=ft.border.all(1, Colors.BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Welcome Back", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Log in to manage your shop.", size=13, color=Colors.TEXT_SECONDARY),
                ft.Container(height=10),
                email_field,
                password_field,
                ft.Container(
                    width=350,
                    alignment=ft.Alignment(1, 0),
                    content=forgot_password_button,
                ),
                login_button,
                error_text,
                ft.Container(height=8),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Don't have an account? ",
                            size=13,
                            color=Colors.TEXT_SECONDARY,
                        ),
                        ft.TextButton(
                            "Sign up",
                            on_click=go_to_signup,
                            style=ft.ButtonStyle(color=Colors.SECONDARY),
                        ),
                    ],
                ),
            ],
        ),
    )

    def handle_keyboard(e: ft.KeyboardEvent):
        if page.route == "/login":
            if e.key == "Enter":
                login_clicked(None)
            elif e.key == "Escape":
                go_to_home(None)
                
    page.on_keyboard_event = handle_keyboard

    return ft.Stack(
                expand=True,
                controls=[
                    # Background (Transparent to let stars show through)
                    ft.Container(
                        expand=True,
                        bgcolor="transparent",
                    ),
                    # Centered login card
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        padding=40,
                        content=login_card,
                    ),
                    # Back button — top left
                    ft.Container(
                        left=24,
                        top=24,
                        content=ft.Container(
                            height=38,
                            padding=ft.padding.symmetric(horizontal=14),
                            border_radius=8,
                            border=ft.border.all(1, "#172231"),
                            ink=True,
                            on_click=go_to_home,
                            content=ft.Row(
                                tight=True,
                                spacing=8,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.ARROW_BACK_ROUNDED,
                                        color="#657188",
                                        size=16,
                                    ),
                                    ft.Text(
                                        "BACK",
                                        color="#657188",
                                        size=9,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ),
                    ),
                ],
            )

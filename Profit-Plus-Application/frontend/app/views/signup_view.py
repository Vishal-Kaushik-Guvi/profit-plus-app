import flet as ft

from app.api_client import api_client
from app.theme import Colors


def SignupView(page: ft.Page):
    state = {"otp_sent": False}

    def go_to_login(e):
        page.go("/login")

    def go_to_home(e):
        page.go("/")

    def field_style():
        return ft.TextStyle(
            color=Colors.TEXT_SECONDARY,
            size=11,
            weight=ft.FontWeight.BOLD,
        )

    name_field = ft.TextField(
        label="FULL NAME",
        hint_text="Enter your name",
        color="white",
        label_style=field_style(),
        border_color=Colors.BORDER,
        focused_border_color=Colors.SECONDARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
    )

    phone_field = ft.TextField(
        label="PHONE NUMBER",
        hint_text="1234567890",
        color="white",
        label_style=field_style(),
        border_color=Colors.BORDER,
        focused_border_color=Colors.SECONDARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"),
        max_length=10,
    )

    email_field = ft.TextField(
        label="EMAIL ADDRESS",
        hint_text="you@example.com",
        color="white",
        label_style=field_style(),
        border_color=Colors.BORDER,
        focused_border_color=Colors.SECONDARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
    )

    password_field = ft.TextField(
        label="PASSWORD",
        hint_text="Create a password",
        password=True,
        can_reveal_password=True,
        color="white",
        label_style=field_style(),
        border_color=Colors.BORDER,
        focused_border_color=Colors.SECONDARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
    )

    otp_field = ft.TextField(
        label="ENTER EMAIL OTP",
        hint_text="6-digit code",
        color="white",
        label_style=field_style(),
        border_color=Colors.BORDER,
        focused_border_color=Colors.SECONDARY,
        bgcolor="#0d0d18",
        border_radius=10,
        width=350,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=6,
        visible=False,
    )

    error_text = ft.Text("", color=Colors.DANGER, size=12)
    status_text = ft.Text("", color=Colors.SUCCESS, size=12)

    main_button = ft.Container(
        content=ft.Text("GET OTP", color="white", weight=ft.FontWeight.BOLD, size=14),
        bgcolor=Colors.PRIMARY,
        padding=ft.padding.symmetric(vertical=16),
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        width=350,
        ink=True,
    )

    def set_button_text(text):
        main_button.content = ft.Text(
            text,
            color="white",
            weight=ft.FontWeight.BOLD,
            size=14,
        )

    def set_button_loading():
        main_button.content = ft.Row(
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

    def form_values():
        return {
            "name": (name_field.value or "").strip(),
            "phone": (phone_field.value or "").strip(),
            "email": (email_field.value or "").strip(),
            "password": password_field.value or "",
            "otp": (otp_field.value or "").strip(),
        }

    def validate_account_fields(values):
        if not values["name"]:
            return "Please enter your name"
        if not values["phone"] or len(values["phone"]) != 10 or not values["phone"].isdigit():
            return "Enter a valid 10-digit phone number"
        if not values["email"] or "@" not in values["email"]:
            return "Enter a valid email address"
        if len(values["password"]) < 6:
            return "Password must be at least 6 characters"
        return None

    def get_otp_clicked(e):
        error_text.value = ""
        status_text.value = ""
        values = form_values()

        validation_error = validate_account_fields(values)
        if validation_error:
            error_text.value = validation_error
            page.update()
            return

        set_button_loading()
        page.update()

        try:
            data, status_code = api_client.send_otp(
                email=values["email"],
                purpose="signup",
                phone=values["phone"],
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            set_button_text("GET OTP")
            page.update()
            return

        if status_code == 200:
            state["otp_sent"] = True
            otp_field.visible = True
            status_text.value = data.get("message", "OTP sent to your email")
            set_button_text("CREATE ACCOUNT")
        else:
            error_text.value = data.get("detail", "Failed to send OTP")
            set_button_text("GET OTP")

        page.update()

    def create_account_clicked(e):
        error_text.value = ""
        status_text.value = ""
        values = form_values()

        validation_error = validate_account_fields(values)
        if validation_error:
            error_text.value = validation_error
            page.update()
            return

        if len(values["otp"]) != 6 or not values["otp"].isdigit():
            error_text.value = "Enter a valid 6-digit OTP"
            page.update()
            return

        set_button_loading()
        page.update()

        try:
            data, status_code = api_client.signup(
                name=values["name"],
                phone=values["phone"],
                email=values["email"],
                password=values["password"],
                otp=values["otp"],
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            set_button_text("CREATE ACCOUNT")
            page.update()
            return

        if status_code == 200:
            page.go("/login")
            return

        error_text.value = data.get("detail", "Signup failed")
        set_button_text("CREATE ACCOUNT")
        page.update()

    def main_button_clicked(e):
        if state["otp_sent"]:
            create_account_clicked(e)
        else:
            get_otp_clicked(e)

    main_button.on_click = main_button_clicked
    name_field.on_submit = main_button_clicked
    phone_field.on_submit = main_button_clicked
    email_field.on_submit = main_button_clicked
    password_field.on_submit = main_button_clicked
    otp_field.on_submit = main_button_clicked

    signup_card = ft.Container(
        width=420,
        padding=40,
        bgcolor="#b30a0a14",
        border_radius=20,
        border=ft.border.all(1, Colors.BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Create Account", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Start managing your shop.", size=13, color=Colors.TEXT_SECONDARY),
                ft.Container(height=10),
                name_field,
                phone_field,
                email_field,
                password_field,
                otp_field,
                ft.Container(height=4),
                main_button,
                status_text,
                error_text,
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Already have an account? ", size=13, color=Colors.TEXT_SECONDARY),
                        ft.TextButton(
                            "Log in",
                            on_click=go_to_login,
                            style=ft.ButtonStyle(color=Colors.SECONDARY),
                        ),
                    ],
                ),
            ],
        ),
    )

    def handle_keyboard(e: ft.KeyboardEvent):
        if page.route == "/signup":
            if e.key == "Enter":
                main_button_clicked(None)
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
                    # Centered signup card
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        padding=40,
                        content=signup_card,
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

import flet as ft

from app.api_client import api_client
from app.theme import Colors


def ForgotPasswordView(page: ft.Page):
    state = {"otp_sent": False}

    def go_to_login(e=None):
        page.go("/login")

    field_style = ft.TextStyle(
        color=Colors.TEXT_SECONDARY,
        size=11,
        weight=ft.FontWeight.BOLD,
    )

    def text_field(
        label,
        hint,
        password=False,
        keyboard_type=None,
        max_length=None,
        visible=True,
    ):
        input_filter = None
        if keyboard_type == ft.KeyboardType.NUMBER:
            input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9]*$")

        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            keyboard_type=keyboard_type,
            input_filter=input_filter,
            max_length=max_length,
            visible=visible,
            width=350,
            color="white",
            label_style=field_style,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            bgcolor="#0d0d18",
            border_radius=10,
        )

    email_field = text_field(
        "EMAIL ADDRESS",
        "you@example.com",
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    otp_field = text_field(
        "RESET OTP",
        "6-digit code",
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=6,
        visible=False,
    )
    password_field = text_field(
        "NEW PASSWORD",
        "At least 6 characters",
        password=True,
        visible=False,
    )
    confirm_password_field = text_field(
        "CONFIRM NEW PASSWORD",
        "Enter the password again",
        password=True,
        visible=False,
    )

    error_text = ft.Text("", color=Colors.DANGER, size=12)
    status_text = ft.Text("", color=Colors.SUCCESS, size=12)

    action_button = ft.Container(
        width=350,
        padding=ft.padding.symmetric(vertical=16),
        border_radius=10,
        bgcolor=Colors.PRIMARY,
        alignment=ft.Alignment(0, 0),
        ink=True,
        content=ft.Text(
            "SEND RESET OTP",
            color="white",
            size=14,
            weight=ft.FontWeight.BOLD,
        ),
    )

    def set_button_text(text):
        action_button.content = ft.Text(
            text,
            color="white",
            size=14,
            weight=ft.FontWeight.BOLD,
        )

    def set_loading():
        action_button.content = ft.ProgressRing(
            width=18,
            height=18,
            stroke_width=2,
            color="white",
        )

    def email_value():
        return (email_field.value or "").strip()

    def send_reset_otp():
        email = email_value()
        if not email or "@" not in email:
            error_text.value = "Enter a valid email address"
            page.update()
            return

        set_loading()
        page.update()

        try:
            data, status_code = api_client.send_otp(
                email=email,
                purpose="reset_password",
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            set_button_text("SEND RESET OTP")
            page.update()
            return

        if status_code == 200:
            state["otp_sent"] = True
            email_field.disabled = True
            otp_field.visible = True
            password_field.visible = True
            confirm_password_field.visible = True
            status_text.value = data.get(
                "message", "Reset OTP sent to your email"
            )
            set_button_text("RESET PASSWORD")
        else:
            error_text.value = data.get(
                "detail", "Failed to send reset OTP"
            )
            set_button_text("SEND RESET OTP")

        page.update()

    def reset_password():
        otp = (otp_field.value or "").strip()
        password = password_field.value or ""
        confirmation = confirm_password_field.value or ""

        if len(otp) != 6 or not otp.isdigit():
            error_text.value = "Enter a valid 6-digit OTP"
            page.update()
            return
        if len(password) < 6:
            error_text.value = "Password must be at least 6 characters"
            page.update()
            return
        if password != confirmation:
            error_text.value = "Passwords do not match"
            page.update()
            return

        set_loading()
        page.update()

        try:
            data, status_code = api_client.reset_password(
                email=email_value(),
                otp=otp,
                new_password=password,
            )
        except Exception:
            error_text.value = "Unable to connect to the server"
            set_button_text("RESET PASSWORD")
            page.update()
            return

        if status_code == 200:
            sb = ft.SnackBar(ft.Text("Password reset successfully! Please log in."), bgcolor=Colors.SUCCESS)
            page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
            page.overlay.append(sb)
            sb.open = True
            page.go("/login")
            return

        error_text.value = data.get("detail", "Password reset failed")
        set_button_text("RESET PASSWORD")
        page.update()

    def action_clicked(e=None):
        error_text.value = ""
        status_text.value = ""
        if state["otp_sent"]:
            reset_password()
        else:
            send_reset_otp()

    action_button.on_click = action_clicked
    email_field.on_submit = action_clicked
    otp_field.on_submit = action_clicked
    password_field.on_submit = action_clicked
    confirm_password_field.on_submit = action_clicked

    card = ft.Container(
        width=430,
        padding=40,
        bgcolor="#b30a0a14",
        border_radius=20,
        border=ft.border.all(1, Colors.BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=17,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=26,
                    bgcolor="#1c1530",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.LOCK_RESET_ROUNDED,
                        color=Colors.PRIMARY_LIGHT,
                        size=26,
                    ),
                ),
                ft.Text(
                    "Reset Password",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                ),
                ft.Text(
                    "We'll email you a code to secure your account.",
                    size=13,
                    color=Colors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=7),
                email_field,
                otp_field,
                password_field,
                confirm_password_field,
                action_button,
                status_text,
                error_text,
                ft.TextButton(
                    "BACK TO LOGIN",
                    on_click=go_to_login,
                    style=ft.ButtonStyle(
                        color=Colors.SECONDARY,
                        text_style=ft.TextStyle(
                            size=11,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ),
            ],
        ),
    )

    return ft.Container(
                expand=True,
                bgcolor="transparent",
                alignment=ft.Alignment(0, 0),
                padding=40,
                content=card,
            )

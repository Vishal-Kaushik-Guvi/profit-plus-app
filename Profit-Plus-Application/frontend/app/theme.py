import flet as ft

# ── Colors ────────────────────────────────────────────────────────────

class Colors:
    BG_DARK = "#05050a"
    BG_CARD = "#11111f"
    BG_INPUT = "#0d0d18"
    BORDER = "#1f1f33"

    PRIMARY = "#7c3aed"
    PRIMARY_LIGHT = "#a78bfa"
    SECONDARY = "#00e5ff"
    SUCCESS = "#22c55e"
    DANGER = "#ef4444"
    WARNING = "#f59e0b"

    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"


# ── Gradients ─────────────────────────────────────────────────────────

def background_gradient():
    return ft.RadialGradient(
        center=ft.Alignment(0, -0.3),
        radius=1.5,
        colors=[Colors.BG_CARD, Colors.BG_DARK]
    )


def primary_button_gradient():
    return ft.LinearGradient(
        begin=ft.Alignment(-1, 0),
        end=ft.Alignment(1, 0),
        colors=[Colors.PRIMARY, Colors.PRIMARY_LIGHT]
    )


# ── Text Styles ──────────────────────────────────────────────────────

def heading_style():
    return {
        "size": 32,
        "weight": ft.FontWeight.BOLD,
        "color": Colors.TEXT_PRIMARY
    }

def subheading_style():
    return {
        "size": 14,
        "color": Colors.TEXT_SECONDARY
    }

def label_style():
    return {
        "size": 11,
        "weight": ft.FontWeight.W_600,
        "color": Colors.TEXT_SECONDARY
    }


# ── Reusable Components ─────────────────────────────────────────────

def styled_text_field(label: str, hint: str = "", password: bool = False, **kwargs):
    return ft.TextField(
        label=label,
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        color=Colors.TEXT_PRIMARY,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=11),
        border_color=Colors.BORDER,
        focused_border_color=Colors.PRIMARY,
        bgcolor=Colors.BG_INPUT,
        border_radius=10,
        **kwargs
    )


def primary_button(text: str, on_click=None, width: int = 300):
    return ft.Container(
        width=width,
        height=50,
        border_radius=10,
        gradient=primary_button_gradient(),
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        ink=True,
        content=ft.Text(
            text,
            color=Colors.TEXT_PRIMARY,
            weight=ft.FontWeight.BOLD,
            size=15
        )
    )


def secondary_button(text: str, on_click=None, width: int = 300):
    return ft.OutlinedButton(
        text,
        width=width,
        height=50,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1.5, Colors.BORDER),
            color=Colors.TEXT_SECONDARY,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=on_click
    )


def card_container(content, padding: int = 30, width: int = None):
    return ft.Container(
        content=content,
        padding=padding,
        width=width,
        bgcolor=Colors.BG_CARD,
        border_radius=16,
        border=ft.border.all(1, Colors.BORDER)
    )
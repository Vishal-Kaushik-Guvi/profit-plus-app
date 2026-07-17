import os
import subprocess
import time
import webbrowser

import flet as ft

from app.api_client import api_client

BG_COLOR = "transparent"
CARD_BG = "#cc131a26"
BORDER = "#1a2536"
PURPLE = "#6d22d9"
CYAN = "#16cdf2"
GREEN = "#22c55e"
RED = "#ef4444"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"


def SubscriptionView(page: ft.Page, business_id: str):
    state = {
        "tier": "FREE",
        "polling": False,
        "loading": False,
        "payment_url": "",
        "order_id": "",
    }

    pro_button_ref = ft.Ref[ft.ElevatedButton]()
    free_button_ref = ft.Ref[ft.ElevatedButton]()

    def show_snack(message: str, color: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"), bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    def reset_pro_button():
        state["loading"] = False
        if pro_button_ref.current and state["tier"] != "PRO":
            pro_button_ref.current.text = "UPGRADE TO PRO"
            pro_button_ref.current.disabled = False
            pro_button_ref.current.bgcolor = PURPLE
            pro_button_ref.current.update()

    def set_plan_button_state():
        is_pro = state["tier"] == "PRO"

        if pro_button_ref.current:
            pro_button_ref.current.text = "CURRENT PLAN" if is_pro else "UPGRADE TO PRO"
            pro_button_ref.current.disabled = is_pro
            pro_button_ref.current.bgcolor = "#2d3748" if is_pro else PURPLE

        if free_button_ref.current:
            free_button_ref.current.text = (
                "CURRENT PLAN" if not is_pro else "CONTACT SUPPORT TO DOWNGRADE"
            )
            free_button_ref.current.disabled = True
            free_button_ref.current.bgcolor = "#2d3748" if not is_pro else "#1a2536"

        page.update()

    def poll_subscription_status(timeout_seconds=300, interval_seconds=5):
        """Poll the subscription status endpoint to detect when payment completes."""
        elapsed = 0
        while state["polling"] and elapsed < timeout_seconds:
            time.sleep(interval_seconds)
            elapsed += interval_seconds

            try:
                # First check subscription status (fast — just a DB lookup)
                data, status = api_client.get_subscription_status(business_id)
                if status == 200 and data.get("is_pro"):
                    state["polling"] = False
                    state["tier"] = "PRO"
                    api_client.invalidate_business_cache(business_id)
                    set_plan_button_state()
                    show_snack("Payment confirmed - you're now on PRO!", GREEN)
                    return

                # If we have an order_id, also try verifying the order directly
                # with Razorpay (backup path if checkout JS verification failed)
                if state.get("order_id") and elapsed % 15 == 0:
                    verify_data, verify_status = api_client.verify_order_status(
                        business_id, state["order_id"]
                    )
                    if verify_status == 200 and verify_data.get("is_pro"):
                        state["polling"] = False
                        state["tier"] = "PRO"
                        api_client.invalidate_business_cache(business_id)
                        set_plan_button_state()
                        show_snack("Payment confirmed - you're now on PRO!", GREEN)
                        return

            except Exception:
                continue

        if state["polling"]:
            state["polling"] = False
            show_snack(
                "Still waiting on payment confirmation - check back shortly.", PURPLE
            )
            reset_pro_button()

    def _launch_url(url: str):
        """Reliably open a URL in the default browser on Windows."""
        try:
            webbrowser.open(url)
            return True
        except Exception:
            pass
        try:
            os.startfile(url)
            return True
        except Exception:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", url], shell=True)
            return True
        except Exception:
            pass
        try:
            page.launch_url(url)
            return True
        except Exception:
            pass
        return False

    def open_payment_page():
        if not state["payment_url"]:
            return
        opened = _launch_url(state["payment_url"])
        if opened:
            show_snack("Payment page opened. Complete payment in your browser.", PURPLE)
        else:
            show_snack("Could not open browser. Copy this URL manually: " + state["payment_url"], RED)

    def start_upgrade(e):
        if state["polling"] and state["payment_url"]:
            open_payment_page()
            return

        if state["tier"] == "PRO" or state["loading"]:
            return

        state["loading"] = True
        button = e.control
        button.text = "CREATING ORDER..."
        button.disabled = True
        button.bgcolor = "#2d3748"
        page.update()

        try:
            data, status = api_client.create_subscription_payment_link(business_id)
        except Exception as exc:
            reset_pro_button()
            show_snack(f"Could not start upgrade: {exc}", RED)
            return

        if status in (200, 201) and data.get("payment_url"):
            state["payment_url"] = data["payment_url"]
            state["order_id"] = data.get("order_id", "")
            open_payment_page()
            should_start_polling = not state["polling"]
            state["polling"] = True
            state["loading"] = False
            button.text = "OPEN PAYMENT PAGE"
            button.disabled = False
            button.bgcolor = GREEN
            page.update()
            if should_start_polling:
                poll_subscription_status()
            return

        detail = data.get("detail", "Could not create payment order.")
        if status == 400 and "already on PRO" in detail:
            state["tier"] = "PRO"
            api_client.invalidate_business_cache(business_id)
            set_plan_button_state()
            show_snack("This business is already on PRO.", GREEN)
            return

        reset_pro_button()
        show_snack(detail, RED)

    def create_feature_row(feature: str, is_included: bool):
        icon = (
            ft.Icons.CHECK_CIRCLE_OUTLINE if is_included else ft.Icons.CANCEL_OUTLINED
        )
        color = GREEN if is_included else RED
        text_style = ft.TextStyle(
            decoration=(
                ft.TextDecoration.LINE_THROUGH
                if not is_included
                else ft.TextDecoration.NONE
            )
        )
        return ft.Row(
            spacing=10,
            controls=[
                ft.Icon(icon, color=color, size=18),
                ft.Text(
                    feature,
                    color=TEXT_SECONDARY if not is_included else TEXT_PRIMARY,
                    size=14,
                    style=text_style,
                ),
            ],
        )

    def create_subscription_card(
        title: str,
        price: str,
        period: str,
        features: list,
        is_pro: bool,
        current_plan: bool,
        button_ref: ft.Ref,
    ):
        if current_plan:
            button_text = "CURRENT PLAN"
            button_color = "#2d3748"
            button_disabled = True
        elif is_pro:
            button_text = "UPGRADE TO PRO"
            button_color = PURPLE
            button_disabled = False
        else:
            button_text = "CONTACT SUPPORT TO DOWNGRADE"
            button_color = "#2d3748"
            button_disabled = True

        card_border_color = PURPLE if is_pro else BORDER

        def on_hover(e):
            e.control.scale = 1.03 if e.data == "true" else 1.0
            e.control.border = (
                ft.border.all(1, CYAN)
                if e.data == "true" and is_pro
                else ft.border.all(1, card_border_color)
            )
            e.control.update()

        return ft.Container(
            width=360,
            padding=35,
            border_radius=16,
            bgcolor=CARD_BG,
            border=ft.border.all(1, card_border_color),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            scale=1.0,
            on_hover=on_hover,
            content=ft.Column(
                spacing=25,
                controls=[
                    ft.Text(
                        title,
                        color=PURPLE if is_pro else TEXT_PRIMARY,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                price,
                                color=TEXT_PRIMARY,
                                size=42,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(f"/{period}", color=TEXT_SECONDARY, size=16),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Text(
                        (
                            "Unlock advanced tools for your business"
                            if is_pro
                            else "Perfect for getting started"
                        ),
                        color=TEXT_SECONDARY,
                        size=12,
                    ),
                    ft.Divider(color=BORDER, height=20),
                    ft.Column(
                        spacing=15,
                        controls=[create_feature_row(f[0], f[1]) for f in features],
                    ),
                    ft.Container(height=15),
                    ft.ElevatedButton(
                        button_text,
                        ref=button_ref,
                        expand=True,
                        height=55,
                        color="white",
                        bgcolor=button_color,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            animation_duration=300,
                        ),
                        disabled=button_disabled,
                        on_click=start_upgrade if is_pro and not current_plan else None,
                    ),
                ],
            ),
        )

    free_features = [
        ("Save up to 25 products", True),
        ("Dashboard access", True),
        ("Sales history access", True),
        ("Customer access", True),
        ("Inventory access", True),
        ("Unlimited products", False),
        ("Access to analytics", False),
        ("Send PDF bill to email", False),
    ]

    pro_features = [
        ("Save unlimited products", True),
        ("Dashboard access", True),
        ("Sales history access", True),
        ("Customer access", True),
        ("Inventory access", True),
        ("Unlimited products", True),
        ("Access to analytics", True),
        ("Send PDF bill to email", True),
    ]

    dynamic_pricing = api_client.get_pricing()
    pro_price_str = f"Rs.{dynamic_pricing.get('PRO', 499)}"

    try:
        data, status = api_client.get_business(business_id)
        if status == 200:
            state["tier"] = data.get("subscription_type", "FREE")
    except Exception as e:
        print(f"Error fetching business subscription: {e}")

    return ft.Container(
        expand=True,
        padding=40,
        bgcolor=BG_COLOR,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(height=20),
                ft.Text(
                    "Choose Your Plan",
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                ),
                ft.Container(height=5),
                ft.Text(
                    "Unlock the full potential of your business with our Pro plan.",
                    size=16,
                    color=TEXT_SECONDARY,
                ),
                ft.Container(height=50),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=50,
                    wrap=True,
                    controls=[
                        create_subscription_card(
                            title="Free",
                            price="Rs.0",
                            period="month",
                            features=free_features,
                            is_pro=False,
                            current_plan=(state["tier"] == "FREE"),
                            button_ref=free_button_ref,
                        ),
                        create_subscription_card(
                            title="Pro",
                            price=pro_price_str,
                            period="month",
                            features=pro_features,
                            is_pro=True,
                            current_plan=(state["tier"] == "PRO"),
                            button_ref=pro_button_ref,
                        ),
                    ],
                ),
                ft.Container(height=40),
            ],
        ),
    )

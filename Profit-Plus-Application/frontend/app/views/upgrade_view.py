import flet as ft
import os
import subprocess
import time
import webbrowser
from app.theme import Colors, background_gradient, card_container, primary_button
from app.api_client import api_client


class UpgradeView(ft.Container):
    def __init__(self, page: ft.Page, business_id: str, on_upgraded=None):
        super().__init__(expand=True, gradient=background_gradient())
        self.page = page
        self.business_id = business_id
        self.on_upgraded = on_upgraded
        self._polling = False
        self._order_id = ""

        self.status_text = ft.Text(
            "Upgrade to PRO to unlock full billing and EMI features.",
            color=Colors.TEXT_SECONDARY,
            size=14,
        )
        self.progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
        self.upgrade_button = primary_button(
            "Upgrade to PRO", on_click=self.start_upgrade
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                card_container(
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Profit Plus PRO",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.PRIMARY,
                            ),
                            self.status_text,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[self.progress_ring, self.upgrade_button],
                            ),
                        ],
                    )
                )
            ],
        )

    def start_upgrade(self, e):
        self.upgrade_button.disabled = True
        self.progress_ring.visible = True
        self.status_text.value = "Creating payment order..."
        self.page.update()

        try:
            data, status = api_client.create_subscription_payment_link(self.business_id)
        except Exception as exc:
            self.status_text.value = f"Error: {exc}"
            self.upgrade_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()
            return

        if status not in (200, 201):
            error_message = data.get("detail", "Could not start payment.")
            self.status_text.value = f"Error: {error_message}"
            self.upgrade_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()
            return

        self._order_id = data.get("order_id", "")
        self._launch_url(data["payment_url"])
        self.status_text.value = (
            "Complete the payment in your browser. Waiting for confirmation..."
        )
        self.page.update()

        self._polling = True
        self._poll_status()

    def _launch_url(self, url: str):
        """Reliably open a URL in the default browser on Windows."""
        try:
            webbrowser.open(url)
            return
        except Exception:
            pass
        try:
            os.startfile(url)
            return
        except Exception:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", url], shell=True)
            return
        except Exception:
            pass
        try:
            self.page.launch_url(url)
        except Exception:
            self.status_text.value = f"Could not open browser. Open this URL manually: {url}"
            self.page.update()

    def _poll_status(self, timeout_seconds: int = 300, interval_seconds: int = 5):
        elapsed = 0
        while self._polling and elapsed < timeout_seconds:
            time.sleep(interval_seconds)
            elapsed += interval_seconds

            try:
                # Check subscription status (quick DB check)
                data, status = api_client.get_subscription_status(self.business_id)
                if status == 200 and data.get("is_pro"):
                    self._on_confirmed()
                    return

                # Backup: verify order directly with Razorpay every 15s
                if self._order_id and elapsed % 15 == 0:
                    verify_data, verify_status = api_client.verify_order_status(
                        self.business_id, self._order_id
                    )
                    if verify_status == 200 and verify_data.get("is_pro"):
                        self._on_confirmed()
                        return

            except Exception:
                continue

        if self._polling:
            self._polling = False
            self.status_text.value = "Still waiting? Payments can take a minute — reopen this screen to check again."
            self.progress_ring.visible = False
            self.upgrade_button.disabled = False
            self.page.update()

    def _on_confirmed(self):
        self._polling = False
        api_client.invalidate_business_cache(self.business_id)
        self.status_text.value = "Payment confirmed! You're now on PRO."
        self.progress_ring.visible = False
        self.upgrade_button.visible = False
        self.page.update()
        if self.on_upgraded:
            self.on_upgraded()

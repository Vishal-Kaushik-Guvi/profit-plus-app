import flet as ft
from app.theme import Colors
from app.api_client import api_client

def AdminSubscriptionsView(page: ft.Page):
    subs_list = []
    
    def on_cancel(e, bid):
        if api_client.cancel_admin_subscription(bid):
            page.snack_bar = ft.SnackBar(ft.Text("Subscription Cancelled!"), bgcolor=Colors.SUCCESS)
            page.snack_bar.open = True
            api_client._get_cache.clear()
            load_subs()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Failed to cancel subscription"), bgcolor=Colors.DANGER)
            page.snack_bar.open = True
            page.update()

    def on_update_pricing(e, plan, text_field):
        try:
            val = int(text_field.value)
            if api_client.update_admin_pricing(plan, val):
                page.snack_bar = ft.SnackBar(ft.Text(f"{plan} Plan Pricing Updated to ₹{val}!"), bgcolor=Colors.SUCCESS)
                page.snack_bar.open = True
            else:
                raise Exception()
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Invalid pricing or request failed"), bgcolor=Colors.DANGER)
            page.snack_bar.open = True
        page.update()

    def load_subs():
        try:
            data, status = api_client.get_admin_subscriptions()
            if status == 200:
                subs_list.clear()
                subs_list.extend(data)
                render_all()
        except Exception as e:
            print("Error loading subscriptions:", e)

    content_col = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=32)

    def hover_card(e):
        e.control.border = ft.border.all(1, Colors.PRIMARY if e.data == "true" else "#1a2130")
        e.control.update()

    def render_all():
        controls = []
        
        # 1. Pricing Config Section
        pricing_cards = []
        
        dynamic_pricing = api_client.get_pricing()
        current_pro = str(dynamic_pricing.get("PRO", 499))
        
        # PRO Plan Card
        pro_price = ft.TextField(value=current_pro, label="Monthly Price (₹)", border_color="#1a2130", focused_border_color=Colors.PRIMARY, height=45, expand=True)
        pricing_cards.append(
            ft.Container(
                expand=1,
                bgcolor="#0d1421",
                border_radius=12,
                border=ft.border.all(1, "#1a2130"),
                padding=24,
                content=ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("PRO PLAN", color="#f59e0b", weight=ft.FontWeight.BOLD, size=16),
                                ft.Icon(ft.Icons.STAR_ROUNDED, color="#f59e0b", size=20)
                            ]
                        ),
                        ft.Text("Full featured business suite.", size=12, color=Colors.TEXT_SECONDARY),
                        ft.Row(
                            controls=[
                                pro_price,
                                ft.ElevatedButton("Update", bgcolor=Colors.PRIMARY, color="white", on_click=lambda e: on_update_pricing(e, "PRO", pro_price))
                            ]
                        )
                    ]
                )
            )
        )
        

        
        controls.append(ft.Text("Pricing Setup", size=20, weight=ft.FontWeight.BOLD, color="white"))
        controls.append(ft.Row(controls=pricing_cards, spacing=24))
        
        # 2. Active Subscriptions List
        controls.append(ft.Container(height=16))
        controls.append(ft.Text("Active Subscriptions", size=20, weight=ft.FontWeight.BOLD, color="white"))
        
        subs_container = ft.Column(spacing=8)
        
        for sub in subs_list:
            is_pro = sub["plan"] == "PRO"
            plan_color = "#f59e0b" if is_pro else "#3b82f6"
            date_str = sub["expiry"].split("T")[0] if "T" in sub["expiry"] else sub["expiry"]
            
            sub_card = ft.Container(
                bgcolor="#0d1421",
                border_radius=8,
                border=ft.border.all(1, "#1a2130"),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                on_hover=hover_card,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                content=ft.Row(
                    controls=[
                        # Details
                        ft.Container(
                            expand=2,
                            content=ft.Row(
                                spacing=16,
                                controls=[
                                    ft.Container(
                                        width=40, height=40, border_radius=20,
                                        bgcolor=plan_color + "22",
                                        alignment=ft.Alignment(0,0),
                                        content=ft.Icon(ft.Icons.WORKSPACE_PREMIUM, color=plan_color, size=20)
                                    ),
                                    ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(sub["business_name"], weight=ft.FontWeight.BOLD, color="white", size=15),
                                            ft.Text(f"Owner: {sub['owner_name']}", color=Colors.TEXT_SECONDARY, size=12)
                                        ]
                                    )
                                ]
                            )
                        ),
                        # Plan type
                        ft.Container(
                            expand=1,
                            content=ft.Container(
                                bgcolor=plan_color + "22",
                                padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                border_radius=12,
                                border=ft.border.all(1, plan_color + "55"),
                                content=ft.Text(sub["plan"] + " PLAN", color=plan_color, weight=ft.FontWeight.BOLD, size=11)
                            )
                        ),
                        # Expiry
                        ft.Container(
                            expand=1,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Expires On", color=Colors.TEXT_SECONDARY, size=11),
                                    ft.Text(date_str, color="white", size=13, weight=ft.FontWeight.W_500)
                                ]
                            )
                        ),
                        # Action
                        ft.Container(
                            expand=1,
                            content=ft.ElevatedButton(
                                "Cancel",
                                on_click=lambda e, bid=sub["business_id"]: on_cancel(e, bid),
                                bgcolor=Colors.DANGER,
                                color="white",
                                height=32,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=0)
                                )
                            )
                        )
                    ]
                )
            )
            subs_container.controls.append(sub_card)
            
        if not subs_list:
            subs_container.controls.append(ft.Text("No active subscriptions found.", color=Colors.TEXT_SECONDARY))
            
        controls.append(subs_container)
        
        content_col.controls = controls
        page.update()

    # Initial load
    load_subs()

    content = ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Subscription Management", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Manage active business subscriptions and configure platform pricing plans.", size=14, color=Colors.TEXT_SECONDARY),
                ft.Container(height=24),
                content_col
            ]
        )
    )

    return ft.Stack(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                bgcolor="transparent",
            ),
            content,
        ],
    )

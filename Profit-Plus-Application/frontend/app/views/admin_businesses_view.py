import flet as ft
from app.theme import Colors
from app.api_client import api_client

def AdminBusinessesView(page: ft.Page):
    
    business_list = []

    def load_businesses():
        try:
            data, status = api_client.get_admin_businesses()
            if status == 200:
                business_list.clear()
                business_list.extend(data)
                render_cards()
        except Exception as e:
            print("Error loading businesses:", e)
            
    list_container = ft.Container(expand=True)

    def hover_card(e):
        e.control.bgcolor = "#162032" if e.data == "true" else "#0d1421"
        e.control.border = ft.border.all(1, Colors.PRIMARY if e.data == "true" else "#1a2130")
        e.control.update()

    def render_cards():
        controls = []
        
        # Header Row
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor="#171b29",
            border_radius=8,
            border=ft.border.all(1, "#1a2130"),
            content=ft.Row(
                controls=[
                    ft.Container(content=ft.Text("Business Details", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Owner Info", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Phone", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Subscription", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Created Date", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=1),
                ]
            )
        )
        controls.append(header)
        controls.append(ft.Container(height=8))

        # Data Rows
        for b in business_list:
            raw_date = b.get("created_date", "")
            created_str = raw_date.split("T")[0] if "T" in raw_date else raw_date
            
            sub_type = b.get("subscription_type", "FREE")
            sub_color = Colors.PRIMARY
            if sub_type == "PRO":
                sub_color = "#f59e0b"
            elif sub_type == "PLUS":
                sub_color = "#3b82f6"
            elif sub_type == "FREE":
                sub_color = Colors.SUCCESS
                
            b_name = b.get("business_name", "N/A")
            initials = "".join([w[0].upper() for w in b_name.split() if w])[:2] if b_name != "N/A" else "--"

            card = ft.Container(
                bgcolor="#0d1421",
                border_radius=8,
                border=ft.border.all(1, "#1a2130"),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                on_hover=hover_card,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                content=ft.Row(
                    controls=[
                        # Business Details
                        ft.Container(
                            expand=2,
                            content=ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(
                                        width=40, height=40, border_radius=20,
                                        bgcolor="#1e293b",
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(initials, color=Colors.PRIMARY, weight=ft.FontWeight.BOLD)
                                    ),
                                    ft.Text(b_name, color="white", weight=ft.FontWeight.BOLD, size=14)
                                ]
                            )
                        ),
                        # Owner Info
                        ft.Container(
                            expand=2,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(b.get("owner_name", "N/A"), color="white", size=13, weight=ft.FontWeight.BOLD),
                                    ft.Text(b.get("email", "N/A"), color=Colors.TEXT_SECONDARY, size=11)
                                ]
                            )
                        ),
                        # Phone
                        ft.Container(
                            expand=2,
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.PHONE_OUTLINED, size=14, color=Colors.TEXT_SECONDARY),
                                    ft.Text(b.get("phone", "N/A"), color="white", size=13)
                                ]
                            )
                        ),
                        # Subscription
                        ft.Container(
                            expand=2,
                            content=ft.Container(
                                bgcolor=sub_color + "22",
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=12,
                                border=ft.border.all(1, sub_color + "55"),
                                content=ft.Text(sub_type, color=sub_color, weight=ft.FontWeight.BOLD, size=11)
                            )
                        ),
                        # Created Date
                        ft.Container(
                            expand=1,
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=14, color=Colors.TEXT_SECONDARY),
                                    ft.Text(created_str, color="white", size=13)
                                ]
                            )
                        ),
                    ]
                )
            )
            controls.append(card)

        list_container.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=controls
        )
        page.update()

    # Initial load
    load_businesses()

    content = ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Registered Businesses", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("View and monitor all businesses created on the platform with a premium interface.", size=14, color=Colors.TEXT_SECONDARY),
                ft.Container(height=24),
                list_container
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

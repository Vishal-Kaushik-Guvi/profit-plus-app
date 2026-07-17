import flet as ft
from app.theme import Colors
from app.api_client import api_client

def AdminDashboardView(page: ft.Page):
    
    # State variables
    overview_data = {
        "total_users": 0,
        "total_businesses": 0,
        "total_subscriptions": 0
    }
    
    # UI Refs
    users_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="white")
    businesses_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="white")
    subscriptions_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="white")

    def load_data():
        try:
            data, status = api_client.get_admin_overview()
            if status == 200:
                users_text.value = str(data.get("total_users", 0))
                businesses_text.value = str(data.get("total_businesses", 0))
                subscriptions_text.value = str(data.get("total_subscriptions", 0))
                page.update()
        except Exception as e:
            pass
            
    # Load data immediately
    load_data()

    def create_stat_card(title, icon, text_ref, color):
        return ft.Container(
            width=300,
            bgcolor="#0d1117",
            border_radius=12,
            border=ft.border.all(1, Colors.BORDER),
            padding=24,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(title, size=14, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                            ft.Icon(icon, size=24, color=color)
                        ]
                    ),
                    text_ref
                ]
            )
        )

    content = ft.Container(
        padding=20,
        expand=True,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Overview Stats", size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ]
                ),
                ft.Container(height=30),
                ft.Row(
                    spacing=20,
                    wrap=True,
                    controls=[
                        create_stat_card("Total Users", ft.Icons.PEOPLE_OUTLINED, users_text, "#16cdf2"),
                        create_stat_card("Registered Businesses", ft.Icons.BUSINESS_OUTLINED, businesses_text, "#6d22d9"),
                        create_stat_card("Active Subscriptions", ft.Icons.CARD_MEMBERSHIP_OUTLINED, subscriptions_text, "#10b981")
                    ]
                )
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

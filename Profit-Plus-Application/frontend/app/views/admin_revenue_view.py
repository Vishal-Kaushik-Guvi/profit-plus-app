import flet as ft
from app.theme import Colors
from app.api_client import api_client

def AdminRevenueView(page: ft.Page):
    
    revenue_data = {
        "total_revenue": 0,
        "chart_data": [],
        "transactions": []
    }

    def load_revenue():
        try:
            data, status = api_client.get_admin_revenue()
            if status == 200:
                revenue_data["total_revenue"] = data.get("total_revenue", 0)
                revenue_data["chart_data"] = data.get("chart_data", [])
                revenue_data["transactions"] = data.get("transactions", [])
                render_all()
        except Exception as e:
            print("Error loading revenue:", e)

    content_col = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=24)

    def render_all():
        controls = []
        
        # 1. Total Revenue Card
        total_rev_card = ft.Container(
            bgcolor="#0d1117",
            border_radius=12,
            border=ft.border.all(1, Colors.BORDER),
            padding=24,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Total Subscription Revenue", size=14, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                            ft.Icon(ft.Icons.ATTACH_MONEY_ROUNDED, size=24, color="#10b981")
                        ]
                    ),
                    ft.Text(f"₹ {revenue_data['total_revenue']:,}", size=36, weight=ft.FontWeight.BOLD, color="white")
                ]
            )
        )
        controls.append(total_rev_card)
        
        # 2. Revenue Graph
        if revenue_data["chart_data"]:
            bars = []
            max_rev = max([item["revenue"] for item in revenue_data["chart_data"]] + [1])
            
            for item in revenue_data["chart_data"]:
                height_pct = item["revenue"] / max_rev
                bar_height = max(10, int(200 * height_pct))
                
                bar = ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=30,
                            height=bar_height,
                            bgcolor="#10b981",
                            border_radius=ft.border_radius.only(top_left=4, top_right=4),
                            tooltip=f"₹ {item['revenue']}"
                        ),
                        ft.Text(item["month"], size=12, color=Colors.TEXT_SECONDARY)
                    ]
                )
                bars.append(
                    ft.Container(
                        alignment=ft.Alignment(0, 1),
                        height=230,
                        content=bar
                    )
                )
                
            chart = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=bars
            )
            
            chart_container = ft.Container(
                bgcolor="#0d1421",
                border_radius=12,
                border=ft.border.all(1, "#1a2130"),
                padding=24,
                height=300,
                content=ft.Column(
                    controls=[
                        ft.Text("Revenue Trend (Last 6 Months)", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=10),
                        ft.Container(expand=True, content=chart)
                    ]
                )
            )
            controls.append(chart_container)

        # 3. Transaction History
        txn_controls = [
            ft.Text("Recent Transactions", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=8)
        ]
        
        for txn in revenue_data["transactions"]:
            date_str = txn["date"].split("T")[0] if "T" in txn["date"] else txn["date"]
            is_pro = txn["plan"] == "PRO"
            plan_color = "#f59e0b" if is_pro else "#3b82f6"
            
            txn_card = ft.Container(
                bgcolor="#0d1421",
                border_radius=8,
                border=ft.border.all(1, "#1a2130"),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Left side: Icon + ID + Business
                        ft.Row(
                            spacing=16,
                            controls=[
                                ft.Container(
                                    width=40, height=40, border_radius=20,
                                    bgcolor="#1e293b",
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, color="#10b981", size=18)
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(txn["business_name"], color="white", weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(txn["id"], color=Colors.TEXT_SECONDARY, size=12)
                                    ]
                                )
                            ]
                        ),
                        # Middle: Plan Badge + Date
                        ft.Row(
                            spacing=24,
                            controls=[
                                ft.Container(
                                    bgcolor=plan_color + "22",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=12,
                                    border=ft.border.all(1, plan_color + "55"),
                                    content=ft.Text(txn["plan"] + " PLAN", color=plan_color, weight=ft.FontWeight.BOLD, size=10)
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=Colors.TEXT_SECONDARY),
                                        ft.Text(date_str, color="white", size=12)
                                    ]
                                )
                            ]
                        ),
                        # Right side: Amount + Status
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            spacing=2,
                            controls=[
                                ft.Text(f"₹ {txn['amount']}", color="#10b981", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(txn["status"], color=Colors.SUCCESS, size=10, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ]
                )
            )
            txn_controls.append(txn_card)

        if not revenue_data["transactions"]:
            txn_controls.append(ft.Text("No transactions found.", color=Colors.TEXT_SECONDARY))

        controls.append(ft.Column(spacing=8, controls=txn_controls))
        
        content_col.controls = controls
        page.update()

    # Initial load
    load_revenue()

    content = ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Revenue Analysis", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Track subscription revenue, transaction history, and financial trends.", size=14, color=Colors.TEXT_SECONDARY),
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

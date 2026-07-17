import flet as ft
import time
import random
from datetime import datetime
from app.api_client import api_client

BG = "#030711"
SIDEBAR_BG = "#070816"
BORDER = "#1a2231"
CYAN = "#16cdf2"
PURPLE = "#6d22d9"


def DashboardView(page: ft.Page, business_id: str):

    # ── Stat card builder ─────────────────────────────────────────
    def stat_card(title, value_text, icon, icon_color, glow_color, ref=None):
        value_ctrl = ft.Text(
            value_text, color="white", size=26,
            weight=ft.FontWeight.BOLD
        )
        if ref is not None:
            ref.append(value_ctrl)

        return ft.Container(
            expand=True,
            height=110,
            padding=ft.padding.symmetric(horizontal=22, vertical=18),
            border_radius=14,
            bgcolor="#070e1c",
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=glow_color,
                offset=ft.Offset(0, 4)
            ),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(title, color="#69758b", size=10,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(
                                width=32, height=32,
                                border_radius=8,
                                bgcolor=glow_color,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icon, color=icon_color, size=16)
                            )
                        ]
                    ),
                    value_ctrl,
                ]
            )
        )

    # ── Refs to update stat values after load ─────────────────────
    today_sales_ref = []
    monthly_profit_ref = []
    low_stock_ref = []
    pending_emi_ref = []

    stat_row = ft.Row(
        spacing=16,
        controls=[
            stat_card("TODAY'S SALES", "₹0",
                      ft.Icons.TRENDING_UP_ROUNDED, CYAN, "#0d2a30",
                      today_sales_ref),
            stat_card("MONTHLY PROFIT", "₹0",
                      ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "#a78bfa", "#1c1030",
                      monthly_profit_ref),
            stat_card("LOW STOCK ALERTS", "0",
                      ft.Icons.WARNING_AMBER_ROUNDED, "#fb923c", "#2a1800",
                      low_stock_ref),
            stat_card("PENDING EMIs", "0",
                      ft.Icons.CREDIT_CARD_ROUNDED, "#f472b6", "#2a0f1e",
                      pending_emi_ref),
        ]
    )

    # ── Recent transactions table ─────────────────────────────────
    transactions_column = ft.Column(spacing=0)

    no_transactions = ft.Container(
        padding=40,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED,
                        color="#2a3444", size=48),
                ft.Text("No transactions yet", color="#3d4a5c", size=13),
            ]
        )
    )

    def transaction_row(invoice, customer, amount, date_str, is_emi):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            border=ft.border.only(
                bottom=ft.BorderSide(1, "#0e1522")
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        width=130,
                        content=ft.Text(invoice, color=CYAN, size=11,
                                        weight=ft.FontWeight.BOLD)
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(customer, color="white", size=12,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS)
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(f"₹{amount:,.2f}", color="#a3b0c2",
                                        size=12)
                    ),
                    ft.Container(
                        width=90,
                        content=ft.Text(date_str, color="#596475", size=11)
                    ),
                    ft.Container(
                        width=60,
                        content=ft.Container(
                            padding=ft.padding.symmetric(
                                horizontal=8, vertical=4),
                            border_radius=6,
                            bgcolor="#0d2a1a" if not is_emi else "#1c1030",
                            content=ft.Text(
                                "EMI" if is_emi else "PAID",
                                color="#4ade80" if not is_emi else "#a78bfa",
                                size=9, weight=ft.FontWeight.BOLD
                            )
                        )
                    ),
                ]
            )
        )

    transactions_card = ft.Container(
        border_radius=14,
        bgcolor="#070e1c",
        border=ft.border.all(1, BORDER),
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20, vertical=16),
                    border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("RECENT TRANSACTIONS", color="white",
                                    size=11, weight=ft.FontWeight.BOLD),
                            ft.Text("Last 5 sales", color="#59657a", size=10),
                        ]
                    )
                ),
                transactions_column,
                no_transactions,
            ]
        )
    )



    # ── Main content ──────────────────────────────────────────────
    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=48, right=48, top=40, bottom=40),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=28,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text("DASHBOARD", color="white",
                                        size=30, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=7, height=7,
                                            border_radius=4, bgcolor=CYAN
                                        ),
                                        ft.Text(
                                            "G L O B A L   S T O R E   O V E R V I E W",
                                            color="#69758b", size=8,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        ft.Text(
                            datetime.now().strftime("%B %d, %Y"),
                            color="#59657a", size=12
                        ) if True else ft.Text(""),
                    ]
                ),
                stat_row,
                transactions_card,
            ]
        )
    )

    # ── Star background ───────────────────────────────────────────
    stars = [
        (32, 48, 2), (114, 111, 1), (191, 35, 2), (275, 83, 1),
        (361, 21, 2), (446, 126, 1), (534, 57, 2), (627, 101, 1),
        (714, 31, 2), (809, 74, 1), (901, 139, 2), (1003, 46, 1),
        (1095, 96, 2), (72, 307, 1), (223, 255, 2), (401, 342, 1),
        (578, 286, 2), (769, 366, 1), (957, 277, 2), (1118, 332, 1),
        (128, 505, 2), (318, 451, 1), (515, 548, 2), (716, 479, 1),
        (895, 561, 2), (1077, 491, 1),
    ]
    background = ft.Stack(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=ft.RadialGradient(
                    center=ft.Alignment(0.75, 0.35),
                    radius=1.2,
                    colors=["#071621", BG],
                ),
            ),
            *[
                ft.Container(
                    left=x, top=y,
                    width=size, height=size,
                    border_radius=size,
                    bgcolor="#a7b1c2",
                )
                for x, y, size in stars
            ],
        ]
    )

    # ── Data loading ──────────────────────────────────────────────
    def load_data():
        # Load user
        try:
            data, status = api_client.get_me()
            if status == 200:
                name = (data.get("name") or "").strip()
                email_addr = (data.get("email") or "").strip()
                display = name or email_addr.split("@")[0] or "User"
        except Exception:
            pass

        # Load dashboard stats
        try:
            stats, status = api_client.get_dashboard_stats(business_id)
            if status == 200:
                today_sales_ref[0].value = f"₹{stats['today_sales']:,.0f}"
                monthly_profit_ref[0].value = f"₹{stats['monthly_profit']:,.0f}"
                low_stock_ref[0].value = str(stats['low_stock_count'])
                pending_emi_ref[0].value = str(stats['pending_emi_count'])

                txns = stats.get("recent_transactions", [])
                if txns:
                    no_transactions.visible = False
                    for t in txns:
                        transactions_column.controls.append(
                            transaction_row(
                                t["invoice_no"],
                                t["buyer_name"],
                                t["total_amount"],
                                t["transaction_date"],
                                t["is_emi"],
                            )
                        )
                else:
                    no_transactions.visible = True
        except Exception:
            pass

        page.update()

    import threading
    load_data()

    return main_content

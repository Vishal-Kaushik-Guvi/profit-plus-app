import flet as ft
import time
import random
from app.api_client import api_client

BG = "#020710"
SIDEBAR_BG = "#070816"
BORDER = "#172231"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"


def BusinessDashboardView(page: ft.Page, business_id: str):
    error_text = ft.Text("", color="#fb7185", size=12)

    # ── Metric value refs ─────────────────────────────────────────
    gross_sales_val = ft.Text("₹0.00", color="white", size=24,
                              weight=ft.FontWeight.BOLD)
    cash_val = ft.Text("₹0.00", color="white", size=24,
                       weight=ft.FontWeight.BOLD)
    profit_val = ft.Text("₹0.00", color="white", size=24,
                         weight=ft.FontWeight.BOLD)
    margin_badge_val = ft.Text("0% ACCRUED MARGIN", color=CYAN,
                               size=8, weight=ft.FontWeight.BOLD)
    emi_received_val = ft.Text("₹0.00", color="white", size=24,
                               weight=ft.FontWeight.BOLD)
    emi_due_val = ft.Text("₹0.00", color="white", size=24,
                          weight=ft.FontWeight.BOLD)
    emi_due_badge_val = ft.Text("ALL CLEAR", color="#7d899e",
                                size=8, weight=ft.FontWeight.BOLD)

    # GST values
    output_gst_val = ft.Text("₹0.00", color="white", size=12,
                             weight=ft.FontWeight.BOLD)
    input_gst_val = ft.Text("₹0.00", color="white", size=12,
                            weight=ft.FontWeight.BOLD)
    net_gst_val = ft.Text("₹0.00", color="white", size=12,
                          weight=ft.FontWeight.BOLD)

    # Subscription Banner
    sub_banner_text = ft.Text("Loading subscription...", color="white", size=11, weight=ft.FontWeight.BOLD)
    sub_banner_icon = ft.Icon(ft.Icons.VERIFIED_USER_OUTLINED, color=GREEN, size=16)
    sub_banner_container = ft.Container(
        padding=12, border_radius=8, bgcolor="#060b14", border=ft.border.all(1, BORDER),
        content=ft.Row(spacing=8, controls=[sub_banner_icon, sub_banner_text]),
        visible=False
    )
    def badge(text_ctrl, color, bgcolor):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=14,
            bgcolor=bgcolor,
            border=ft.border.all(1, color),
            content=text_ctrl,
        )

    # ── GST value cell ────────────────────────────────────────────
    def gst_cell(label, value_ctrl, highlighted=False):
        return ft.Container(
            expand=True, height=64, padding=14,
            border_radius=10,
            bgcolor="#073342" if highlighted else "#141b27",
            border=ft.border.all(1, "#1e2a39"),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(label, color="#68758a", size=7),
                    value_ctrl,
                ],
            ),
        )

    # ── Dashboard layout ──────────────────────────────────────────
    dashboard = ft.Container(
        expand=True,
        padding=ft.padding.only(left=32, right=32, top=25, bottom=20),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=25,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("SHOP MANAGER", color="white",
                                        size=26, weight=ft.FontWeight.BOLD),
                                ft.Text("Store activity for today",
                                        color="#68758a", size=10),
                            ],
                        ),
                        ft.Container(
                            width=145, height=49, border_radius=11,
                            bgcolor=GREEN, alignment=ft.Alignment(0, 0),
                            ink=True,
                            on_click=lambda e: page.go(
                                f"/businesses/{business_id}/billing"),
                            content=ft.Row(
                                tight=True, spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.ADD_ROUNDED,
                                            color="#03110d", size=19),
                                    ft.Text("NEW BILL", color="#03110d",
                                            size=9,
                                            weight=ft.FontWeight.BOLD),
                                ],
                            ),
                        ),
                    ],
                ),

                # Subscription banner (hidden by default)
                sub_banner_container,

                # Row 1 — Sales metrics
                ft.Row(
                    spacing=18,
                    controls=[
                        ft.Container(
                            expand=True, height=145, padding=26,
                            border_radius=32, bgcolor="#060b14",
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("Gross Sales Today",
                                                    color="#657188", size=9),
                                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                                                    color="#3f4b5e", size=14),
                                        ]
                                    ),
                                    gross_sales_val,
                                    ft.Row(controls=[
                                        badge(ft.Text("TOTAL BUSINESS DONE",
                                                      color="#5a9cf0", size=8,
                                                      weight=ft.FontWeight.BOLD),
                                              "#5a9cf0", "#101e32")
                                    ]),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=True, height=145, padding=26,
                            border_radius=32, bgcolor="#060b14",
                            border=ft.border.all(1, BORDER),
                            gradient=ft.RadialGradient(
                                center=ft.Alignment(0.85, 0),
                                radius=1.1,
                                colors=["#08251f", "#060b14"],
                            ),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("Cash Collected Today",
                                                    color="#657188", size=9),
                                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                                                    color="#3f4b5e", size=14),
                                        ]
                                    ),
                                    cash_val,
                                    ft.Row(controls=[
                                        badge(ft.Text("LIQUID CASH IN HAND",
                                                      color=GREEN, size=8,
                                                      weight=ft.FontWeight.BOLD),
                                              GREEN, "#07372d")
                                    ]),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=True, height=145, padding=26,
                            border_radius=32, bgcolor="#060b14",
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("Today's Profit Margin",
                                                    color="#657188", size=9),
                                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                                                    color="#3f4b5e", size=14),
                                        ]
                                    ),
                                    profit_val,
                                    ft.Row(controls=[
                                        badge(margin_badge_val,
                                              CYAN, "#082936")
                                    ]),
                                ],
                            ),
                        ),
                    ],
                ),

                # Row 2 — EMI metrics
                ft.Row(
                    spacing=18,
                    controls=[
                        ft.Container(
                            expand=True, height=145, padding=26,
                            border_radius=32, bgcolor="#060b14",
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("EMI Received Today",
                                                    color="#657188", size=9),
                                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                                                    color="#3f4b5e", size=14),
                                        ]
                                    ),
                                    emi_received_val,
                                    ft.Row(controls=[
                                        badge(ft.Text("HOVER FOR MONTH",
                                                      color="#f59e0b", size=8,
                                                      weight=ft.FontWeight.BOLD),
                                              "#f59e0b", "#32200d")
                                    ]),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=True, height=145, padding=26,
                            border_radius=32, bgcolor="#060b14",
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("EMI Due Today",
                                                    color="#657188", size=9),
                                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                                                    color="#3f4b5e", size=14),
                                        ]
                                    ),
                                    emi_due_val,
                                    ft.Row(controls=[
                                        badge(emi_due_badge_val,
                                              "#7d899e", "#181f2b")
                                    ]),
                                ],
                            ),
                        ),
                    ],
                ),

                # GST Summary
                ft.Container(
                    height=118, padding=26, border_radius=30,
                    bgcolor="#080d16",
                    border=ft.border.all(1, BORDER),
                    content=ft.Row(
                        spacing=24,
                        controls=[
                            ft.Container(
                                width=145,
                                content=ft.Row(
                                    spacing=12,
                                    controls=[
                                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED,
                                                color=CYAN, size=18),
                                        ft.Text("GST SUMMARY", color="white",
                                                size=15,
                                                weight=ft.FontWeight.BOLD),
                                    ],
                                ),
                            ),
                            gst_cell("Output GST (Collected)", output_gst_val),
                            gst_cell("Input GST (ITC Paid)", input_gst_val),
                            gst_cell("Net GST Payable", net_gst_val, True),
                        ],
                    ),
                ),

                error_text,
            ],
        ),
    )

    # ── Load data ─────────────────────────────────────────────────
    def load_stats():
        try:
            # Load dashboard stats
            data, status_code = api_client.get_dashboard_stats(business_id)
            # Load business subscription info
            b_data, b_status = api_client.get_business(business_id)
            
            if b_status == 200:
                sub_type = b_data.get("subscription_type", "FREE")
                if sub_type != "FREE":
                    days = b_data.get("subscription_days_remaining", 0)
                    sub_banner_text.value = f"PRO Subscription active • {days} days remaining"
                    sub_banner_icon.color = GREEN
                    sub_banner_icon.name = ft.Icons.VERIFIED_OUTLINED
                    sub_banner_container.bgcolor = "#061a14"
                    sub_banner_container.border = ft.border.all(1, "#14d59b33")
                else:
                    sub_banner_text.value = "FREE Tier • Max 25 products. Upgrade to PRO to unlock everything."
                    sub_banner_icon.color = "#94a3b8"
                    sub_banner_icon.name = ft.Icons.INFO_OUTLINE
                    sub_banner_container.bgcolor = "#131a26"
                    sub_banner_container.border = ft.border.all(1, "#1a2536")
                
                sub_banner_container.visible = True
        except Exception:
            return

        if status_code != 200:
            return

        gross = data.get("gross_sales_today", 0)
        cash = data.get("cash_collected_today", 0)
        profit = data.get("profit_today", 0)
        margin = data.get("margin_pct", 0)
        emi_recv = data.get("emi_received_today", 0)
        emi_due = data.get("emi_due_today", 0)
        out_gst = data.get("output_gst", 0)
        in_gst = data.get("input_gst", 0)
        net_gst = data.get("net_gst", 0)

        gross_sales_val.value = f"₹{gross:,.2f}"
        cash_val.value = f"₹{cash:,.2f}"
        profit_val.value = f"₹{profit:,.2f}"
        margin_badge_val.value = f"{margin}% ACCRUED MARGIN"
        emi_received_val.value = f"₹{emi_recv:,.2f}"
        emi_due_val.value = f"₹{emi_due:,.2f}"
        emi_due_badge_val.value = (
            f"₹{emi_due:,.2f} DUE" if emi_due > 0 else "ALL CLEAR"
        )
        output_gst_val.value = f"₹{out_gst:,.2f}"
        input_gst_val.value = f"₹{in_gst:,.2f}"
        net_gst_val.value = f"₹{net_gst:,.2f}"
        page.update()

    load_stats()

    return dashboard

import flet as ft
from app.api_client import api_client

BG = "#030711"
SIDEBAR_BG = "#070816"
BORDER = "#1a2231"
CYAN = "#16cdf2"
PURPLE = "#6d22d9"
GREEN = "#10b981"
YELLOW = "#f59e0b"
RED = "#ef4444"
BLUE = "#3b82f6"

def AnalyticsView(page: ft.Page, business_id: str):
    
    current_period = "day"

    # --- Header & Filters ---
    title = ft.Column(
        spacing=4,
        controls=[
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(width=4, height=20, bgcolor=CYAN, border_radius=2),
                    ft.Text("BI TERMINAL", color="white", size=24, weight=ft.FontWeight.BOLD),
                ]
            ),
            ft.Text("PERFORMANCE & MARGIN DIAGNOSTICS", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
        ]
    )

    def on_period_click(e):
        nonlocal current_period
        current_period = e.control.data
        for c in period_row.controls:
            if c.data == current_period:
                c.bgcolor = CYAN
                c.content.color = "black"
            else:
                c.bgcolor = "transparent"
                c.content.color = "#59657a"
        load_data()

    def filter_chip(label, value):
        return ft.Container(
            content=ft.Text(label, color="black" if current_period == value else "#59657a", size=9, weight=ft.FontWeight.BOLD),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=12,
            bgcolor=CYAN if current_period == value else "transparent",
            on_click=on_period_click,
            data=value,
            ink=True
        )

    period_row = ft.Row(
        spacing=0,
        controls=[
            filter_chip("DAY", "day"),
            filter_chip("WEEK", "week"),
            filter_chip("MONTH", "month"),
            filter_chip("YEAR", "year"),
        ]
    )

    period_container = ft.Container(
        content=period_row,
        border=ft.border.all(1, BORDER),
        border_radius=16,
        padding=2
    )

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[title, period_container]
    )

    # --- Top Cards ---
    net_revenue_ref = ft.Text("₹0.00", color="white", size=24, weight=ft.FontWeight.BOLD)
    pure_profit_ref = ft.Text("₹0.00", color="white", size=24, weight=ft.FontWeight.BOLD)
    profit_margin_ref = ft.Text("MARGIN: 0%", color=GREEN, size=9, weight=ft.FontWeight.BOLD)
    sales_volume_ref = ft.Text("0", color="white", size=24, weight=ft.FontWeight.BOLD)
    efficiency_ref = ft.Text("0%", color="white", size=24, weight=ft.FontWeight.BOLD)

    def metric_card(title_text, value_ctrl, tag_text, tag_color, tag_bg, ref_tag=None):
        tag_content = ref_tag if ref_tag else ft.Text(tag_text, color=tag_color, size=9, weight=ft.FontWeight.BOLD)
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor="#070e1c",
            border=ft.border.all(1, BORDER),
            border_radius=12,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(title_text, color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                    value_ctrl,
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=tag_bg,
                        border_radius=6,
                        border=ft.border.all(1, tag_color) if tag_color != "transparent" else None,
                        content=tag_content
                    )
                ]
            )
        )

    top_cards = ft.Row(
        spacing=16,
        controls=[
            metric_card("NET REVENUE", net_revenue_ref, "EXCL. GST (BASE)", CYAN, "#0a1f2e"),
            metric_card("PURE PROFIT", pure_profit_ref, "", GREEN, "#082b1c", profit_margin_ref),
            metric_card("SALES VOLUME", sales_volume_ref, "TRANSACTIONS", BLUE, "#0b1b36"),
            metric_card("EFFICIENCY", efficiency_ref, "MARGIN SCORE", PURPLE, "#1a0b36"),
        ]
    )

    # --- Performance Stream Chart ---
    chart_data = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.END,
        expand=True,
        spacing=4
    )

    chart_container = ft.Container(
        height=300,
        padding=20,
        bgcolor="#070e1c",
        border=ft.border.all(1, BORDER),
        border_radius=12,
        content=ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("PERFORMANCE STREAM", color="white", size=12, weight=ft.FontWeight.BOLD),
                                ft.Text("REAL-TIME REVENUE & PROFIT FLOW (TAX EXCLUSIVE)", color="#59657a", size=9, weight=ft.FontWeight.BOLD),
                            ]
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border=ft.border.all(1, YELLOW), border_radius=6,
                                    content=ft.Row(spacing=4, controls=[ft.Container(width=6, height=6, border_radius=3, bgcolor=YELLOW), ft.Text("REVENUE", color="white", size=9, weight=ft.FontWeight.BOLD)])
                                ),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border=ft.border.all(1, GREEN), border_radius=6,
                                    content=ft.Row(spacing=4, controls=[ft.Container(width=6, height=6, border_radius=3, bgcolor=GREEN), ft.Text("PROFIT", color="white", size=9, weight=ft.FontWeight.BOLD)])
                                )
                            ]
                        )
                    ]
                ),
                ft.Container(height=10),
                chart_data
            ]
        )
    )

    # --- Bottom Lists ---
    def list_card(title_text, list_ref):
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor="#070e1c",
            border=ft.border.all(1, BORDER),
            border_radius=12,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(width=3, height=14, bgcolor=CYAN),
                                    ft.Text(title_text, color="white", size=11, weight=ft.FontWeight.BOLD),
                                ]
                            ),
                            ft.Text("TOP 5", color="#59657a", size=9, weight=ft.FontWeight.BOLD)
                        ]
                    ),
                    ft.Divider(color=BORDER, height=1),
                    ft.Column(spacing=8, controls=[], ref=list_ref)
                ]
            )
        )
        
    most_sold_ref = ft.Ref[ft.Column]()
    most_profitable_ref = ft.Ref[ft.Column]()
    least_sold_ref = ft.Ref[ft.Column]()
    loss_making_ref = ft.Ref[ft.Column]()

    bottom_lists = ft.Column(
        spacing=16,
        controls=[
            ft.Row(
                spacing=16,
                controls=[
                    list_card("MOST SOLD ITEMS", most_sold_ref),
                    list_card("MOST PROFITABLE PRODUCTS", most_profitable_ref),
                ]
            ),
            ft.Row(
                spacing=16,
                controls=[
                    list_card("LEAST SOLD ITEMS", least_sold_ref),
                    list_card("LOSS MAKING ITEMS", loss_making_ref),
                ]
            )
        ]
    )

    def populate_list(ref, items, value_key, value_format, color, suffix=""):
        ref.current.controls.clear()
        if not items:
            ref.current.controls.append(ft.Text("No data available", color="#59657a", size=11))
            return
            
        for i, item in enumerate(items):
            val = item.get("value", 0)
            formatted_val = value_format.format(val)
            
            ref.current.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(vertical=6),
                    border=ft.border.only(bottom=ft.BorderSide(1, "#111827")),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(
                                        width=24, height=24, border_radius=12,
                                        bgcolor="#111827", border=ft.border.all(1, "#1f2937"),
                                        alignment=ft.Alignment(0,0),
                                        content=ft.Text(str(i+1), color="#9ca3af", size=10, weight=ft.FontWeight.BOLD)
                                    ),
                                    ft.Text(item.get("name", "Unknown"), color="white", size=11),
                                ]
                            ),
                            ft.Column(
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(formatted_val, color=color, size=11, weight=ft.FontWeight.BOLD),
                                    ft.Text(suffix, color="#59657a", size=8, weight=ft.FontWeight.BOLD) if suffix else ft.Container()
                                ]
                            )
                        ]
                    )
                )
            )

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=48, right=48, top=40, bottom=40),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=24,
            controls=[
                header,
                top_cards,
                chart_container,
                bottom_lists
            ]
        )
    )

    def load_data():
        try:
            stats, status = api_client.get_bi_terminal_stats(business_id, period=current_period)
            if status == 200:
                net_revenue_ref.value = f"₹{stats.get('net_revenue', 0):,.2f}"
                pure_profit_ref.value = f"₹{stats.get('pure_profit', 0):,.2f}"
                sales_volume_ref.value = str(stats.get('sales_volume', 0))
                efficiency_ref.value = f"{stats.get('margin_pct', 0)}%"
                profit_margin_ref.value = f"MARGIN: {stats.get('margin_pct', 0)}%"
                
                # Setup chart
                stream = stats.get('performance_stream', [])
                
                # Extremely simple agg for chart
                # Group by time slots (hours or days)
                agg = {}
                for s in stream:
                    key = s["time"].split(":")[0] if current_period == "day" else s["date"]
                    if key not in agg:
                        agg[key] = {"rev": 0, "prof": 0}
                    agg[key]["rev"] += s["revenue"]
                    agg[key]["prof"] += s["profit"]
                    
                sorted_keys = sorted(list(agg.keys()))
                
                max_y = 100
                for k in sorted_keys:
                    r = agg[k]["rev"]
                    if r > max_y: max_y = r

                chart_data.controls.clear()
                
                if not sorted_keys:
                    chart_data.controls.append(ft.Text("No performance data available", color="#59657a", size=11))
                else:
                    for k in sorted_keys:
                        r = agg[k]["rev"]
                        p = agg[k]["prof"]
                        
                        # Calculate heights relative to max_y (max height ~200px)
                        r_h = max(2, (r / max_y) * 200)
                        p_h = max(2, (p / max_y) * 200)
                        
                        label = k + ":00" if current_period == "day" else k
                        
                        bar = ft.Column(
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Row(
                                    vertical_alignment=ft.CrossAxisAlignment.END,
                                    spacing=2,
                                    controls=[
                                        ft.Container(width=6, height=r_h, bgcolor=YELLOW, border_radius=2, tooltip=f"Rev: ₹{r:,.0f}"),
                                        ft.Container(width=6, height=p_h, bgcolor=GREEN, border_radius=2, tooltip=f"Prof: ₹{p:,.0f}"),
                                    ]
                                ),
                                ft.Text(label[-5:], size=7, color="#59657a")
                            ]
                        )
                        chart_data.controls.append(bar)

                # Populate lists
                populate_list(most_sold_ref, stats.get('most_sold_items', []), "value", "{} units", YELLOW, "SOLD QUANTITY")
                populate_list(most_profitable_ref, stats.get('most_profitable_products', []), "value", "+₹{:,.2f}", GREEN, "TOTAL PROFIT")
                populate_list(least_sold_ref, stats.get('least_sold_items', []), "value", "{} units", BLUE, "SOLD QUANTITY")
                populate_list(loss_making_ref, stats.get('loss_making_items', []), "value", "₹{:,.2f}", RED, "TOTAL DEFICIT")
                
                page.update()
            elif status == 403:
                main_content.content = ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=80),
                        ft.Icon(ft.Icons.LOCK_OUTLINE, color=PURPLE, size=80),
                        ft.Container(height=20),
                        ft.Text("PRO FEATURE", color=PURPLE, size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Analytics and BI Terminal are only available on the Pro plan.", color="#59657a", size=14),
                        ft.Container(height=30),
                        ft.ElevatedButton(
                            "UPGRADE TO PRO",
                            color="white",
                            bgcolor=PURPLE,
                            on_click=lambda e: page.go(f"/businesses/{business_id}/subscription"),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=20)
                        )
                    ]
                )
                page.update()
        except Exception as e:
            print("Error loading BI terminal data:", e)

    # Initial Load
    load_data()

    return main_content

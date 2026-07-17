import flet as ft

SIDEBAR_BG = "#cc070816"
BORDER = "#172231"
CYAN = "#16cdf2"
PURPLE = "#6d22d9"


def BusinessSidebar(page, business_id: str, active_route: str,
                    business_name: str = "Loading...",
                    business_initials: str = "--"):

    # ── Refs so caller can update name/initials later ─────────────
    name_text = ft.Text(
        business_name, color="white", size=11,
        weight=ft.FontWeight.BOLD, max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    initials_text = ft.Text(
        business_initials, color="white", size=10,
        weight=ft.FontWeight.BOLD
    )

    def menu_item(icon, label, route):
        active = active_route == route
        return ft.Container(
            height=38,
            padding=ft.padding.symmetric(horizontal=16),
            border_radius=8,
            bgcolor="#1c073c" if active else None,
            border=ft.border.all(1, "#32105f") if active else None,
            on_click=lambda e: page.go(route),
            ink=True,
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Icon(icon,
                            color=PURPLE if active else "#657188",
                            size=16),
                    ft.Text(label,
                            color=PURPLE if active else "#7a869b",
                            size=10, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    sidebar = ft.Container(
        width=220,
        bgcolor=SIDEBAR_BG,
        border=ft.border.only(right=ft.BorderSide(1, "#171b29")),
        padding=ft.padding.only(left=16, right=16, top=24, bottom=14),
        content=ft.Column(
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=6),
                    content=ft.Column(
                        spacing=9,
                        controls=[
                            ft.Text("PROFIT", color="white", size=17,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("B U S I N E S S   D A S H B O A R D",
                                    color="#5d687d", size=7,
                                    weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                ft.Container(height=26),
                ft.Text("  MENU", color="#5d687d", size=7,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,
                        controls=[
                            menu_item(ft.Icons.HOME_OUTLINED,
                                      "Dashboard",
                                      f"/businesses/{business_id}/dashboard"),
                            menu_item(ft.Icons.RECEIPT_LONG_OUTLINED,
                                      "Billing",
                                      f"/businesses/{business_id}/billing"),
                            menu_item(ft.Icons.HISTORY_OUTLINED,
                                      "Sales History",
                                      f"/businesses/{business_id}/sales"),
                            menu_item(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                                      "EMI Management",
                                      f"/businesses/{business_id}/emi"),
                            menu_item(ft.Icons.INVENTORY_2_OUTLINED,
                                      "Products",
                                      f"/businesses/{business_id}/products"),
                            menu_item(ft.Icons.WAREHOUSE_OUTLINED,
                                      "Inventory",
                                      f"/businesses/{business_id}/inventory"),

                            menu_item(ft.Icons.BAR_CHART_ROUNDED,
                                      "Analytics",
                                      f"/businesses/{business_id}/analytics"),
                            menu_item(ft.Icons.GROUP_OUTLINED,
                                      "Customers",
                                      f"/businesses/{business_id}/customers"),
                            menu_item(ft.Icons.CREDIT_CARD_OUTLINED,
                                      "Subscription",
                                      f"/businesses/{business_id}/subscription"),
                        ]
                    )
                ),
                ft.Divider(color="#171b29", height=1),
                ft.Container(height=12),
                ft.Container(
                    height=68, padding=12, border_radius=11,
                    border=ft.border.all(1, "#1a2130"),
                    ink=True,
                    on_click=lambda e: page.go(f"/businesses/{business_id}/profile"),
                    content=ft.Row(
                        spacing=11,
                        controls=[
                            ft.Container(
                                width=37, height=37, border_radius=19,
                                border=ft.border.all(1, "#496078"),
                                bgcolor="#111b29",
                                alignment=ft.Alignment(0, 0),
                                content=initials_text,
                            ),
                            ft.Container(
                                width=125,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=3,
                                    controls=[
                                        name_text,
                                        ft.Text("BUSINESS PROFILE",
                                                color="#59657a", size=7),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Container(height=10),
                ft.Container(
                    height=38, border_radius=8,
                    bgcolor="#0d1421",
                    border=ft.border.all(1, "#1a2536"),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e: page.go("/businesses"),
                    ink=True,
                    content=ft.Row(
                        tight=True,
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.ARROW_BACK_ROUNDED,
                                    color="#8796af", size=14),
                            ft.Text("BACK TO HUB", color="#8796af",
                                    size=9, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
            ],
        ),
    )

    # Return both the sidebar container AND the text refs
    # so the caller can update name/initials after API loads
    return sidebar, name_text, initials_text


def HubSidebar(page, active_route: str):
    from app.api_client import api_client
    
    user_initials = ft.Text("--", color="white", size=10, weight=ft.FontWeight.BOLD)
    user_name = ft.Text("Loading user...", color="white", size=11, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
    user_email = ft.Text("", color="#566176", size=8, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)

    def logout(e):
        api_client.set_token(None)
        page.go("/login")

    def menu_item(icon, label, route):
        active = active_route == route
        return ft.Container(
            height=42,
            padding=ft.padding.symmetric(horizontal=17),
            border_radius=9,
            bgcolor="#1c073c" if active else None,
            border=ft.border.all(1, "#32105f") if active else None,
            on_click=lambda e: page.go(route) if route else None,
            ink=True if route else False,
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Icon(icon, color=PURPLE if active else "#637087", size=17),
                    ft.Text(label, color=PURPLE if active else "#778399", size=11, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    me_data, me_status = api_client.get_me()
    is_admin = me_status == 200 and me_data.get("id") == "admin"

    sidebar = ft.Container(
        width=242,
        bgcolor=SIDEBAR_BG,
        border=ft.border.only(right=ft.BorderSide(1, "#171b29")),
        padding=ft.padding.only(left=14, right=14, top=23, bottom=14),
        content=ft.Column(
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=6),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("PROFIT", color="white", size=17, weight=ft.FontWeight.BOLD),
                            ft.Text("BUSINESS HUB", color="#586278", size=9, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                ft.Container(height=25),
                ft.Text("  MENU", color="#5d687d", size=8, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,
                        controls=[
                            menu_item(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, "Admin Panel", "/admin/dashboard") if is_admin else ft.Container(),
                            ft.Container(height=4) if is_admin else ft.Container(),
                            menu_item(ft.Icons.BUSINESS_CENTER_OUTLINED, "Manage Business", "/businesses"),
                            ft.Container(height=4),
                            menu_item(ft.Icons.WORK_OUTLINE_ROUNDED, "Workplace (Coming soon)", ""),
                            ft.Container(height=4),
                            menu_item(ft.Icons.REDEEM_OUTLINED, "Referral Program (Coming Soon)", ""),
                        ]
                    )
                ),
                ft.Divider(color="#171b29", height=1),
                ft.Container(height=13),
                ft.Container(
                    height=68,
                    padding=14,
                    border_radius=11,
                    border=ft.border.all(1, "#1a2130"),
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=37, height=37, border_radius=19,
                                border=ft.border.all(1, "#6e42e8"),
                                alignment=ft.Alignment(0, 0),
                                content=user_initials,
                            ),
                            ft.Container(
                                width=130,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=3,
                                    controls=[user_name, user_email],
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Container(height=12),
                ft.Container(
                    height=38, border_radius=8,
                    border=ft.border.all(1, "#251220"),
                    alignment=ft.Alignment(0, 0),
                    on_click=logout, ink=True,
                    content=ft.Text("SIGN OUT SESSION", color="#8f294d", size=9, weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )

    return sidebar, user_name, user_initials, user_email

def AdminSidebar(page, active_route: str):
    from app.api_client import api_client
    
    def logout(e):
        api_client.set_token(None)
        page.go("/login")

    def menu_item(icon, label, route):
        active = active_route == route
        return ft.Container(
            height=42,
            padding=ft.padding.symmetric(horizontal=17),
            border_radius=9,
            bgcolor="#1c073c" if active else None,
            border=ft.border.all(1, "#32105f") if active else None,
            on_click=lambda e: page.go(route) if route else None,
            ink=True if route else False,
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Icon(icon, color=PURPLE if active else "#637087", size=17),
                    ft.Text(label, color=PURPLE if active else "#778399", size=11, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    sidebar = ft.Container(
        width=242,
        bgcolor=SIDEBAR_BG,
        border=ft.border.only(right=ft.BorderSide(1, "#171b29")),
        padding=ft.padding.only(left=14, right=14, top=23, bottom=14),
        content=ft.Column(
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=6),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("PROFIT", color="white", size=17, weight=ft.FontWeight.BOLD),
                            ft.Text("ADMINISTRATOR", color="#586278", size=9, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                ft.Container(height=25),
                ft.Text("  MENU", color="#5d687d", size=8, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,
                        controls=[
                            menu_item(ft.Icons.DASHBOARD_OUTLINED, "Overview Stats", "/admin/dashboard"),
                            menu_item(ft.Icons.GROUP_OUTLINED, "User Management", "/admin/users"),
                            menu_item(ft.Icons.BUSINESS_OUTLINED, "Registered Businesses", "/admin/businesses"),
                            menu_item(ft.Icons.ATTACH_MONEY_OUTLINED, "Revenue Analysis", "/admin/revenue"),
                            menu_item(ft.Icons.CARD_MEMBERSHIP_OUTLINED, "Subscriptions", "/admin/subscriptions"),
                        ]
                    )
                ),
                ft.Divider(color="#171b29", height=1),
                ft.Container(height=12),
                ft.Container(
                    height=38, border_radius=8,
                    bgcolor="#0d1421",
                    border=ft.border.all(1, "#1a2536"),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e: page.go("/businesses"),
                    ink=True,
                    content=ft.Row(
                        tight=True,
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.EXIT_TO_APP_ROUNDED,
                                    color="#8796af", size=14),
                            ft.Text("ENTER USER APP", color="#8796af",
                                    size=9, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                ft.Container(height=10),
                ft.Container(
                    height=38, border_radius=8,
                    border=ft.border.all(1, "#251220"),
                    alignment=ft.Alignment(0, 0),
                    on_click=logout, ink=True,
                    content=ft.Text("SIGN OUT ADMIN", color="#8f294d", size=9, weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )

    return sidebar

import flet as ft
from app.theme import Colors


def HomeView(page: ft.Page):

    def go_to_login(e):
        page.go("/login")

    def go_to_signup(e):
        page.go("/signup")

    def hover_lift(e):
        e.control.scale = 1.03 if e.data == "true" else 1.0
        e.control.update()

    # ── Background layers — layered radial glows for depth ─────────────
    background = ft.Stack(
        expand=True,
        controls=[
            # Base dark layer (Transparent to let stars show through)
            ft.Container(
                expand=True,
                bgcolor="transparent",
            ),
            # Purple glow — top left (fades to background color, not transparent)
            ft.Container(
                width=500,
                height=500,
                left=-150,
                top=-150,
                border_radius=500,
                gradient=ft.RadialGradient(colors=["#3c1e6e", "#06060c"]),
            ),
            # Cyan glow — right side (fades to background color, not transparent)
            ft.Container(
                width=600,
                height=600,
                right=-200,
                top=100,
                border_radius=600,
                gradient=ft.RadialGradient(colors=["#0a3a42", "#06060c"]),
            ),
        ],
    )

    # ── Navbar ───────────────────────────────────────────────────────
    navbar = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=34, height=34,
                            border_radius=10,
                            bgcolor=Colors.PRIMARY,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.BOLT_ROUNDED, color="white", size=18)
                        ),
                        ft.Text("Profit Plus", size=18, weight=ft.FontWeight.BOLD, color="white"),
                    ]
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.TextButton(
                            content=ft.Text("Log in", color=Colors.TEXT_SECONDARY, size=14),
                            on_click=go_to_login,
                        ),
                        ft.Container(
                            content=ft.Text("Sign up free", color="white", size=14, weight=ft.FontWeight.W_600),
                            bgcolor=Colors.PRIMARY,
                            padding=ft.padding.symmetric(horizontal=22, vertical=13),
                            border_radius=8,
                            on_click=go_to_signup,
                            ink=True,
                            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                            on_hover=hover_lift,
                        )
                    ]
                )
            ]
        )
    )

    # ── Hero ─────────────────────────────────────────────────────────
    hero = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=60),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Container(
                    content=ft.Text("BUILT FOR SMALL RETAIL SHOPS", size=11,
                                     color=Colors.SECONDARY, weight=ft.FontWeight.W_600),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border_radius=30,
                    bgcolor="#0d1f26",
                    border=ft.border.all(1, "#16323d"),
                ),

                ft.Container(height=6),

                ft.Text(
                    "Everything your shop needs,",
                    size=44, weight=ft.FontWeight.BOLD, color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "in one place.",
                    size=44, weight=ft.FontWeight.BOLD, color=Colors.PRIMARY_LIGHT,
                    text_align=ft.TextAlign.CENTER
                ),

                ft.Container(
                    
                    content=ft.Text(
                        "Track inventory, manage EMIs, record sales and keep your "
                        "customers organized — all from a single dashboard built "
                        "for local businesses.",
                        size=15, color=Colors.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER
                    )
                ),

                ft.Container(height=16),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                spacing=8, tight=True,
                                controls=[
                                    ft.Text("Start free trial", color="white", size=14, weight=ft.FontWeight.W_600),
                                    ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="white", size=16),
                                ]
                            ),
                            bgcolor=Colors.PRIMARY,
                            padding=ft.padding.symmetric(horizontal=28, vertical=18),
                            border_radius=10,
                            on_click=go_to_signup,
                            ink=True,
                            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                            on_hover=hover_lift,
                        ),
                        ft.Container(
                            content=ft.Text("See how it works", color="white", size=14, weight=ft.FontWeight.W_600),
                            bgcolor="#13131f",
                            border=ft.border.all(1, Colors.BORDER),
                            padding=ft.padding.symmetric(horizontal=28, vertical=18),
                            border_radius=10,
                            ink=True,
                            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                            on_hover=hover_lift,
                        ),
                    ]
                ),

                ft.Container(height=10),
                ft.Text("No credit card required  ·  7-day free trial  ·  Cancel anytime",
                        size=12, color=Colors.TEXT_MUTED)
            ]
        )
    )

    # ── Stats strip ──────────────────────────────────────────────────
    def stat_block(value, label):
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(label, size=12, color=Colors.TEXT_MUTED),
            ]
        )

    stats_strip = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=36),
        margin=ft.margin.symmetric(horizontal=20),
        border_radius=16,
        bgcolor="#cc0d0d18",
        border=ft.border.all(1, Colors.BORDER),
        content=ft.Row(
            wrap=True,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                stat_block("500+", "Shops onboarded"),
                ft.Container(width=1, height=40, bgcolor=Colors.BORDER),
                stat_block("₹2.4Cr", "Sales tracked monthly"),
                ft.Container(width=1, height=40, bgcolor=Colors.BORDER),
                stat_block("12k", "EMIs managed"),
                ft.Container(width=1, height=40, bgcolor=Colors.BORDER),
                stat_block("99.9%", "Uptime"),
            ]
        )
    )

    # ── Feature cards ────────────────────────────────────────────────
    def feature_card(icon, badge_bg, badge_color, title, description):
        return ft.Container(
            width=300,
            padding=26,
            border_radius=16,
            bgcolor="#cc0d0d18",
            border=ft.border.all(1, Colors.BORDER),
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            on_hover=hover_lift,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        width=46, height=46,
                        border_radius=12,
                        bgcolor=badge_bg,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, color=badge_color, size=22)
                    ),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(description, size=13, color=Colors.TEXT_SECONDARY),
                ]
            )
        )

    features_header = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.Text("Everything, in sync.", size=30, weight=ft.FontWeight.BOLD,
                    color="white", text_align=ft.TextAlign.CENTER),
            ft.Container(
                width=480,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "From the counter to the back office — one system "
                    "keeps your stock, sales and customer accounts aligned.",
                    size=14, color=Colors.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER
                )
            )
        ]
    )

    features_grid = ft.Row(
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20, run_spacing=20,
        controls=[
            feature_card(
                ft.Icons.RECEIPT_LONG_ROUNDED, "#1c1530", Colors.PRIMARY_LIGHT,
                "Fast billing",
                "Create GST-ready invoices in seconds with automatic "
                "tax calculation and stock deduction."
            ),
            feature_card(
                ft.Icons.INVENTORY_2_ROUNDED, "#0d2330", Colors.SECONDARY,
                "Live inventory",
                "Get low-stock alerts, track batches and expiry dates, "
                "and manage variants by size and color."
            ),
            feature_card(
                ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "#1f2316", Colors.SUCCESS,
                "EMI tracking",
                "Convert sales into structured EMI plans with automatic "
                "interest calculation and due-date reminders."
            ),
            feature_card(
                ft.Icons.PEOPLE_ALT_ROUNDED, "#241319", "#f87171",
                "Customer ledger",
                "Keep a running history of every customer's purchases, "
                "dues and payments in one place."
            ),
            feature_card(
                ft.Icons.BAR_CHART_ROUNDED, "#1a2030", "#60a5fa",
                "Profit analytics",
                "See daily and monthly profit, best-selling products "
                "and slow-moving stock at a glance."
            ),
            feature_card(
                ft.Icons.SHIELD_ROUNDED, "#241c10", Colors.WARNING,
                "Secure by design",
                "OTP-based login and encrypted data keep your "
                "business information safe."
            ),
        ]
    )

    # ── CTA banner ───────────────────────────────────────────────────
    cta_banner = ft.Container(
        margin=ft.margin.symmetric(horizontal=50, vertical=60),
        padding=ft.padding.symmetric(horizontal=20, vertical=50),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
            colors=["#2a1a5e", "#0d2330"]
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Ready to take control of your shop?",
                        size=26, weight=ft.FontWeight.BOLD, color="white",
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Join hundreds of shop owners already using Profit Plus.",
                        size=14, color=Colors.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=6),
                ft.Container(
                    content=ft.Text("Create your account", color=Colors.PRIMARY,
                                     size=14, weight=ft.FontWeight.W_600),
                    bgcolor="white",
                    padding=ft.padding.symmetric(horizontal=28, vertical=18),
                    border_radius=10,
                    on_click=go_to_signup,
                    ink=True,
                    animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                    on_hover=hover_lift,
                )
            ]
        )
    )

    # ── Footer ───────────────────────────────────────────────────────
    footer = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=30),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Divider(color=Colors.BORDER, height=1),
                ft.Container(height=6),
                ft.Text("© 2026 Profit Plus  ·  Built for local businesses",
                        size=12, color=Colors.TEXT_MUTED)
            ]
        )
    )

    # ── Page assembly ────────────────────────────────────────────────
    content_column = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            navbar,
            hero,
            stats_strip,
            ft.Container(height=70),
            features_header,
            ft.Container(height=30),
            features_grid,
            cta_banner,
            footer,
        ]
    )

    return ft.Stack(
                expand=True,
                controls=[
                    ft.Column(  # ✅ wrap in scrollable column
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                        controls=[content_column],
                    ),
                ],
            )

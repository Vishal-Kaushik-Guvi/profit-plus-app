import flet as ft
from app.theme import Colors
from app.api_client import api_client

def AdminUsersView(page: ft.Page):
    
    users_list = []
    
    def on_toggle_lock(e, user_id):
        # API call
        try:
            data, status = api_client.toggle_user_lock(user_id)
            if status == 200:
                load_users()  # Refresh table
        except Exception:
            pass

    def load_users():
        try:
            data, status = api_client.get_admin_users()
            if status == 200:
                users_list.clear()
                users_list.extend(data)
                render_cards()
        except Exception as e:
            print("Error loading users:", e)
            
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
                    ft.Container(content=ft.Text("User Name", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Contact Info", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Joined Date", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=2),
                    ft.Container(content=ft.Text("Status", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=1),
                    ft.Container(content=ft.Text("Action", color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.BOLD, size=12), expand=1),
                ]
            )
        )
        controls.append(header)
        controls.append(ft.Container(height=8))

        # Data Rows
        for u in users_list:
            is_locked = u.get("is_locked", False)
            
            # Format joined date
            raw_date = u.get("joined_date", "")
            joined_str = raw_date.split("T")[0] if "T" in raw_date else raw_date
            
            u_name = u.get("name", "N/A")
            initials = "".join([w[0].upper() for w in u_name.split() if w])[:2] if u_name != "N/A" else "--"
            
            lock_btn = ft.ElevatedButton(
                "Unlock" if is_locked else "Lock",
                on_click=lambda e, uid=u["id"]: on_toggle_lock(e, uid),
                bgcolor=Colors.SUCCESS if is_locked else Colors.DANGER,
                color="white",
                height=32,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.padding.symmetric(horizontal=12, vertical=0)
                )
            )

            status_color = Colors.DANGER if is_locked else Colors.SUCCESS
            status_text = "LOCKED" if is_locked else "ACTIVE"

            card = ft.Container(
                bgcolor="#0d1421",
                border_radius=8,
                border=ft.border.all(1, "#1a2130"),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                on_hover=hover_card,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                content=ft.Row(
                    controls=[
                        # User Name
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
                                    ft.Text(u_name, color="white", weight=ft.FontWeight.BOLD, size=14)
                                ]
                            )
                        ),
                        # Contact Info
                        ft.Container(
                            expand=2,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.EMAIL_OUTLINED, size=12, color=Colors.TEXT_SECONDARY), ft.Text(u.get("email", "N/A"), color="white", size=12)]),
                                    ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.PHONE_OUTLINED, size=12, color=Colors.TEXT_SECONDARY), ft.Text(u.get("phone", "N/A"), color="white", size=12)]),
                                ]
                            )
                        ),
                        # Joined Date
                        ft.Container(
                            expand=2,
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=14, color=Colors.TEXT_SECONDARY),
                                    ft.Text(joined_str, color="white", size=13)
                                ]
                            )
                        ),
                        # Status
                        ft.Container(
                            expand=1,
                            content=ft.Container(
                                bgcolor=status_color + "22",
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=12,
                                border=ft.border.all(1, status_color + "55"),
                                content=ft.Text(status_text, color=status_color, weight=ft.FontWeight.BOLD, size=11)
                            )
                        ),
                        # Action
                        ft.Container(
                            expand=1,
                            content=lock_btn
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
    load_users()

    content = ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("User Management", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Manage all registered users and toggle account locks with a dynamic interface.", size=14, color=Colors.TEXT_SECONDARY),
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

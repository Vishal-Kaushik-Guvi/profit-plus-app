import flet as ft
from app.api_client import api_client
import uuid
import urllib.parse
import os

BG = "#020710"
PANEL_BG = "#070d17"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"
BORDER = "#131b2a"

def BillingSuccessView(page: ft.Page, business_id: str):
    
    # Parse query params manually since flet route is full string
    display_txn_id = f"#{str(uuid.uuid4()).replace('-', '')[:14].upper()}"
    amt = "0.00"
    name = "Customer"
    actual_sale_id = ""
    
    if "?" in page.route:
        q = page.route.split("?")[1]
        params = urllib.parse.parse_qs(q)
        if 'txn' in params:
            actual_sale_id = params['txn'][0]
            display_txn_id = f"#{actual_sale_id.replace('-', '')[:14].upper()}"
        if 'amt' in params:
            amt = params['amt'][0]
        if 'name' in params:
            name = params['name'][0]

    email_input = ft.Ref[ft.TextField]()
    
    def close_email_dialog(e):
        email_dialog.open = False
        page.update()

    def send_email(e):
        if not actual_sale_id:
            return
        if not email_input.current.value:
            sb = ft.SnackBar(ft.Text("Please enter an email address."), bgcolor="red")
            page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
        
        email = email_input.current.value
        res, status = api_client.send_pdf_email(actual_sale_id, email)
        if status == 200:
            sb = ft.SnackBar(ft.Text(f"Email sent successfully to {email}!"), bgcolor="green")
            email_dialog.open = False
        else:
            err_msg = res.get('detail', 'Unknown error') if isinstance(res, dict) else str(res)
            sb = ft.SnackBar(ft.Text(f"Failed to send email: {err_msg}"), bgcolor="red")
        
        page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
        
        page.overlay.append(sb)
        sb.open = True
        page.update()

    email_dialog = ft.AlertDialog(
        title=ft.Text("Send Bill via Email"),
        content=ft.TextField(ref=email_input, label="Email Address", width=300),
        actions=[
            ft.TextButton("Cancel", on_click=close_email_dialog),
            ft.TextButton("Send", on_click=send_email)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_email_dialog(e):
        page.overlay.append(email_dialog)
        email_dialog.open = True
        page.update()
            
    main_content = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=600,
                    margin=ft.margin.only(top=20),
                    padding=40,
                    border_radius=24,
                    bgcolor=PANEL_BG,
                    border=ft.border.all(1, BORDER),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=30,
                        controls=[
                            ft.Container(
                                width=80, height=80, border_radius=40,
                                bgcolor="#041a1e", border=ft.border.all(2, "#0a3a42"),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=CYAN, size=40)
                            ),
                            
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                                controls=[
                                     ft.Text("SALE CONFIRMED!", color="white", size=32, weight=ft.FontWeight.BOLD),
                                    ft.Text("The transaction has been successfully processed.", color="#59657a", size=14)
                                ]
                            ),
                            
                            ft.Container(
                                padding=24, border_radius=16,
                                bgcolor="#050a14", border=ft.border.all(1, "#1a2535"),
                                content=ft.Column(
                                    spacing=15,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("TRANSACTION ID", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                                ft.Text(display_txn_id, color="white", size=12, weight=ft.FontWeight.BOLD)
                                            ]
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("CUSTOMER", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                                ft.Text(name, color="white", size=12, weight=ft.FontWeight.BOLD)
                                            ]
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("AMOUNT PAID", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                                ft.Text(f"₹{float(amt):,.2f}", color=CYAN, size=12, weight=ft.FontWeight.BOLD)
                                            ]
                                        ),
                                    ]
                                )
                            ),
                            
                            ft.Row(
                                spacing=20,
                                controls=[
                                    ft.Container(
                                        expand=True, padding=20, border_radius=16,
                                        bgcolor="#0a121e", border=ft.border.all(1, "#1a2535"),
                                        ink=True, on_click=open_email_dialog,
                                        content=ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                            controls=[
                                                ft.Icon(ft.Icons.MAIL_OUTLINE, color=CYAN, size=24),
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    spacing=6,
                                                    controls=[
                                                        ft.Text("Send Bill", color="white", size=12, weight=ft.FontWeight.BOLD),
                                                        ft.Container(
                                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                            border_radius=4, bgcolor=PURPLE,
                                                            content=ft.Text("PRO", color="white", size=8, weight=ft.FontWeight.BOLD)
                                                        )
                                                    ]
                                                ),
                                                ft.Text("Email receipt to client", color="#59657a", size=9)
                                            ]
                                        )
                                    )
                                ]
                             ),
                            
                            ft.Container(
                                margin=ft.margin.only(top=10),
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                border_radius=30,
                                bgcolor="#050a14",
                                border=ft.border.all(1, "#1a2535"),
                                ink=True,
                                on_click=lambda e: page.go(f"/businesses/{business_id}/billing"),
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    tight=True,
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.ARROW_BACK, color="white", size=16),
                                        ft.Text("Back to Billing", color="white", size=14, weight=ft.FontWeight.BOLD)
                                    ]
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    return main_content

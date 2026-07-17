import flet as ft
from app.api_client import api_client
from app.component.pagination_controls import PaginationControls

BG = "#020710"
PANEL_BG = "#070d17"
BORDER = "#131b2a"
CYAN = "#16cdf2"
GREEN = "#14d59b"

def EmiManagementView(page: ft.Page, business_id: str):
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    
    emi_list = ft.ListView(expand=True, spacing=15)
    
    def open_ledger(emi):
        amount_field = ft.TextField(
            value=str(round(emi.get('next_billing_amount', 0), 2)),
            color="white", bgcolor="#0a121e", border=ft.InputBorder.NONE, text_size=12, expand=True,
            read_only=True
        )
        method_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(x) for x in ["CASH", "UPI", "BANK_TRANSFER", "OTHER"]],
            value="CASH", color="white", bgcolor="#0a121e", text_size=12, border=ft.InputBorder.NONE, expand=True
        )
        
        dialog = ft.AlertDialog(bgcolor="transparent", content_padding=0)
        
        def handle_pay(e):
            try:
                amt = float(amount_field.value)
            except:
                return
            
            payload = {
                "emi_id": emi.get('id'),
                "business_id": business_id,
                "amount": amt,
                "payment_method": method_dropdown.value,
                "installment_number": emi.get("months_completed", 0) + 1
            }
            res, status = api_client.create_emi_payment(payload)
            if status in [200, 201]:
                dialog.open = False
                page.update()
                load_emis()
        
        # Payment History List
        history_list = ft.ListView(expand=True, spacing=10)
        for p in emi.get("payments", []):
            history_list.controls.append(
                ft.Container(
                    padding=10, border_radius=8, bgcolor="#041a1e", border=ft.border.all(1, "#0a3a42"),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[ft.Text(p.get("date", ""), color="white", size=10, weight=ft.FontWeight.BOLD), ft.Text("INSTALLMENT", color=GREEN, size=8)]),
                            ft.Text(p.get("payment_method", ""), color="white", size=10, weight=ft.FontWeight.BOLD),
                            ft.Text(f"+₹{p.get('amount', 0):,.2f}", color=GREEN, size=12, weight=ft.FontWeight.BOLD)
                        ]
                    )
                )
            )
            
        rem = emi.get("remaining_balance", 0)
        tot = emi.get("total_payable", 0)
        pct = (1 - (rem / tot)) * 100 if tot > 0 else 0
        
        dialog_content = ft.Container(
            width=800, height=600, padding=20, bgcolor="#060b14", border_radius=16,
            content=ft.Row(
                spacing=20,
                controls=[
                    # Left
                    ft.Column(
                        expand=1,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row([ft.Text("EMI Ledger", color="white", size=20, weight=ft.FontWeight.BOLD), ft.Container(padding=ft.padding.symmetric(horizontal=8, vertical=4), bgcolor="#0a3a42", border_radius=4, content=ft.Text(emi.get('status', 'ACTIVE'), color=CYAN, size=8, weight=ft.FontWeight.BOLD))]),
                                ]
                            ),
                            ft.Text(f"Customer: {emi.get('customer_name')} ({emi.get('customer_phone')})", color="#59657a", size=10),
                            ft.Divider(color=BORDER),
                            ft.Container(
                                padding=15, border_radius=12, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                                content=ft.Column([
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("TOTAL PAYABLE", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Text("REMAINING BALANCE", color="#59657a", size=8, weight=ft.FontWeight.BOLD)]),
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(f"₹{tot:,.2f}", color="white", size=16, weight=ft.FontWeight.BOLD), ft.Text(f"₹{rem:,.2f}", color=GREEN, size=16, weight=ft.FontWeight.BOLD)]),
                                    ft.ProgressBar(value=pct/100, color=GREEN, bgcolor="#131b2a"),
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(f"{emi.get('months_completed', 0)} OF {emi.get('total_months', 0)} MONTHS PAID", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Text(f"{pct:.1f}% COMPLETED", color="#59657a", size=8, weight=ft.FontWeight.BOLD)]),
                                ])
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                padding=15, border_radius=12, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                                content=ft.Column([
                                    ft.Text("PURCHASE DETAILS", color="white", size=10, weight=ft.FontWeight.BOLD),
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("ORIGINATION DATE", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Text(emi.get("start_date", ""), color="white", size=10, weight=ft.FontWeight.BOLD)]),
                                ])
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                padding=15, border_radius=12, bgcolor="#041a1e", border=ft.border.all(1, "#0a3a42"),
                                content=ft.Column([
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("UPCOMING TOTAL", color=CYAN, size=8, weight=ft.FontWeight.BOLD), ft.Text("NEXT DEADLINE", color="#59657a", size=8, weight=ft.FontWeight.BOLD)]),
                                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(f"₹{emi.get('next_billing_amount', 0):,.2f}", color="white", size=18, weight=ft.FontWeight.BOLD), ft.Text(emi.get("next_due_date", "") or "", color="white", size=12, weight=ft.FontWeight.BOLD)]),
                                ])
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                padding=15, border_radius=12, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                                content=ft.Column([
                                    ft.Text("LOG NEW PAYMENT", color="white", size=10, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Column(expand=True, controls=[ft.Text("AMOUNT RECEIVED", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Container(padding=10, border_radius=8, border=ft.border.all(1, "#1a2535"), content=amount_field)]),
                                            ft.Column(expand=True, controls=[ft.Text("PAYMENT METHOD", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Container(padding=10, border_radius=8, border=ft.border.all(1, "#1a2535"), content=method_dropdown)]),
                                        ]
                                    ),
                                    ft.ElevatedButton(f"PAY ₹{emi.get('next_billing_amount', 0):.2f}", bgcolor=GREEN, color="#042218", on_click=handle_pay)
                                ])
                            )
                        ]
                    ),
                    # Right
                    ft.Container(
                        expand=1, padding=20, border_radius=12, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                        content=ft.Column([
                            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                ft.Text("PAYMENT LEDGER HISTORY", color="white", size=12, weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.Icons.CLOSE, icon_size=16, icon_color="white", on_click=lambda e: setattr(dialog, 'open', False) or page.update())
                            ]),
                            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("DATE", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Text("METHOD", color="#59657a", size=8, weight=ft.FontWeight.BOLD), ft.Text("AMOUNT PAID", color="#59657a", size=8, weight=ft.FontWeight.BOLD)]),
                            ft.Divider(color=BORDER),
                            history_list
                        ])
                    )
                ]
            )
        )
        
        dialog.content = dialog_content
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        
    def on_prev():
        if state["current_page"] > 0:
            state["current_page"] -= 1
            load_emis()

    def on_next():
        state["current_page"] += 1
        load_emis()

    def load_emis():
        emi_list.controls.clear()
        data, status = api_client.get_business_emis(business_id, skip=state["current_page"] * state["limit"], limit=state["limit"])
        if status == 200:
            for emi in data:
                status_color = GREEN if emi.get('status') == 'ACTIVE' else "#f59e0b"
                if emi.get('status') == 'COMPLETED': status_color = "#3d4a5c"
                
                emi_list.controls.append(
                    ft.Container(
                        padding=20,
                        border_radius=12,
                        bgcolor=PANEL_BG,
                        border=ft.border.only(left=ft.BorderSide(3, status_color), top=ft.BorderSide(1, BORDER), right=ft.BorderSide(1, BORDER), bottom=ft.BorderSide(1, BORDER)),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=4,
                                            controls=[
                                                ft.Text(emi.get('customer_name') or 'N/A', color="white", size=16, weight=ft.FontWeight.BOLD),
                                                ft.Text(f"Phone: {emi.get('customer_phone') or 'N/A'} | Aadhaar: {emi.get('aadhaar_number') or 'N/A'}", color="#59657a", size=12),
                                                ft.Text(f"Address: {emi.get('customer_address') or 'N/A'}", color="#59657a", size=11)
                                            ]
                                        ),
                                        ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.END,
                                            spacing=4,
                                            controls=[
                                                ft.Text(f"Balance: ₹{emi.get('remaining_balance', 0):,.2f}", color=status_color, size=20, weight=ft.FontWeight.BOLD),
                                                ft.Text(f"Total Amount: ₹{emi.get('total_amount', 0):,.2f}", color="#59657a", size=10)
                                            ]
                                        )
                                    ]
                                ),
                                ft.Divider(color=BORDER, height=1),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=15,
                                            controls=[
                                                ft.Text(f"Down Payment: ₹{emi.get('down_payment', 0):,.2f}", color="white", size=11),
                                                ft.Text(f"Interest: {emi.get('monthly_interest', 0)}%/mo", color="white", size=11),
                                                ft.Text(f"Tenure: {emi.get('total_months', 0)} months", color="white", size=11),
                                            ]
                                        ),
                                        ft.ElevatedButton(
                                            "RECORD PAYMENT",
                                            bgcolor=CYAN, color="#001824",
                                            height=30,
                                            on_click=lambda e, curr=emi: open_ledger(curr)
                                        ) if emi.get('remaining_balance', 0) > 0 else ft.Container()
                                    ]
                                )
                            ]
                        )
                    )
                )
        page.update()
        
    main_content = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column(
            spacing=30,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("EMI Management", color="white", size=36, weight=ft.FontWeight.BOLD),
                                ft.Text("TRACK AND RECORD EMI PAYMENTS", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ]
                ),
                ft.Container(
                    expand=True,
                    content=emi_list
                )
            ]
        )
    )
    
    load_emis()
    main_content.content.controls.append(pagination_container)
    return main_content

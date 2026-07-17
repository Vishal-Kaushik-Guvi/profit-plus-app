import flet as ft
from app.api_client import api_client
from app.component.pagination_controls import PaginationControls

BG = "#020710"
PANEL_BG = "#070d17"
BORDER = "#131b2a"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"

def CustomerView(page: ft.Page, business_id: str):
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    
    # State
    all_customers = []
    filtered_customers = []
    all_sales = []
    all_emis = []
    
    search_input = ft.Ref[ft.TextField]()
    customer_list = ft.ListView(expand=True, spacing=15)
    
    # EMI Ledger logic from emi_management_view
    def open_emi_ledger(emi):
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
                load_data()
        
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
                    ft.Column(
                        expand=1, scroll=ft.ScrollMode.AUTO,
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

    def open_customer_modal(customer):
        c_id = customer.get("id")
        # Find customer sales
        cust_sales = [s for s in all_sales if s.get("customer_id") == c_id]
        # Find customer EMIs
        cust_emis = [e for e in all_emis if e.get("customer_id") == c_id]
        
        sales_list = ft.ListView(expand=True, spacing=10)
        for s in cust_sales:
            for item in s.get("items", []):
                payment_method = "EMI" if s.get("is_emi") else "CASH/CREDIT"
                sales_list.controls.append(
                    ft.Container(
                        padding=15, border_radius=8, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=2, controls=[
                                    ft.Text(item.get("name", "Product"), color="white", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{s.get('transaction_date', '')} | Invoice: {s.get('invoice_no', '')}", color="#59657a", size=10),
                                ]),
                                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                                    ft.Text(f"₹{item.get('total_price', 0):,.2f}", color="white", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{item.get('quantity', 0)} qty • {payment_method}", color=CYAN, size=10, weight=ft.FontWeight.BOLD),
                                ])
                            ]
                        )
                    )
                )
        if not sales_list.controls:
            sales_list.controls.append(ft.Text("No purchases found.", color="#59657a", size=12))

        emi_list = ft.ListView(expand=True, spacing=10)
        for emi in cust_emis:
            status_color = GREEN if emi.get('status') == 'ACTIVE' else "#f59e0b"
            if emi.get('status') == 'COMPLETED': status_color = "#3d4a5c"
            
            emi_list.controls.append(
                ft.Container(
                    padding=15, border_radius=8, bgcolor="#0a121e", border=ft.border.only(left=ft.BorderSide(3, status_color), top=ft.BorderSide(1, BORDER), right=ft.BorderSide(1, BORDER), bottom=ft.BorderSide(1, BORDER)),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text(f"Balance: ₹{emi.get('remaining_balance', 0):,.2f}", color=status_color, size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Started: {emi.get('start_date', '')} | Next Due: {emi.get('next_due_date', '')}", color="#59657a", size=10),
                            ]),
                            ft.ElevatedButton(
                                "MANAGE EMI",
                                bgcolor=CYAN, color="#001824",
                                height=30,
                                on_click=lambda e, curr=emi: open_emi_ledger(curr)
                            )
                        ]
                    )
                )
            )
        if not emi_list.controls:
            emi_list.controls.append(ft.Text("No active EMIs.", color="#59657a", size=12))

        dialog = ft.AlertDialog(bgcolor="transparent", content_padding=0)
        dialog_content = ft.Container(
            width=800, height=600, padding=20, bgcolor="#060b14", border_radius=16,
            content=ft.Row(
                spacing=20,
                controls=[
                    # Profile
                    ft.Column(
                        expand=2,
                        controls=[
                            ft.Text("Customer Profile", color="white", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.Container(
                                width=60, height=60, border_radius=30, bgcolor="#1c073c", border=ft.border.all(1, "#32105f"), alignment=ft.Alignment(0, 0),
                                content=ft.Text(customer.get('name', 'C')[0].upper(), color=PURPLE, size=24, weight=ft.FontWeight.BOLD)
                            ),
                            ft.Container(height=10),
                            ft.Text(customer.get("name", "Unknown"), color="white", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(customer.get("phone", "N/A"), color="#59657a", size=12),
                            ft.Text(customer.get("email", ""), color="#59657a", size=12),
                            ft.Text(f"Address: {customer.get('address', 'N/A')}", color="#59657a", size=12),
                            ft.Text(f"Aadhaar: {customer.get('aadhaar_number', 'N/A')}", color="#59657a", size=12),
                            ft.Container(height=20),
                            ft.Container(
                                padding=15, border_radius=12, bgcolor="#0a121e", border=ft.border.all(1, BORDER),
                                content=ft.Column([
                                    ft.Text("LIFETIME VALUE", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"₹{customer.get('total_spent', 0):,.2f}", color=GREEN, size=24, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{customer.get('total_orders', 0)} Total Orders", color="white", size=12)
                                ])
                            )
                        ]
                    ),
                    # History
                    ft.Column(
                        expand=5,
                        controls=[
                            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                ft.Text("Purchase History & EMIs", color="white", size=16, weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.Icons.CLOSE, icon_size=16, icon_color="white", on_click=lambda e: setattr(dialog, 'open', False) or page.update())
                            ]),
                            ft.Divider(color=BORDER),
                            ft.Text("EMI CONTRACTS", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                            ft.Container(height=140, content=emi_list),
                            ft.Divider(color=BORDER),
                            ft.Text("ALL PURCHASES", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True, content=sales_list)
                        ]
                    )
                ]
            )
        )
        dialog.content = dialog_content
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def render_customers():
        customer_list.controls.clear()
        for cust in filtered_customers:
            name = cust.get("name", "Unknown")
            phone = cust.get("phone", "N/A")
            email = cust.get("email", "") or "No Email"
            address = cust.get("address", "") or "No Address"
            spent = cust.get("total_spent", 0)
            orders = cust.get("total_orders", 0)
            
            customer_list.controls.append(
                ft.Container(
                    padding=20, border_radius=12, bgcolor=PANEL_BG, border=ft.border.all(1, BORDER),
                    ink=True, on_click=lambda e, c=cust: open_customer_modal(c),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=15, controls=[
                                ft.Container(
                                    width=48, height=48, border_radius=24, bgcolor="#0d1a27", border=ft.border.all(1, "#1a2e40"), alignment=ft.Alignment(0, 0),
                                    content=ft.Text(name[0].upper(), color=CYAN, size=20, weight=ft.FontWeight.BOLD)
                                ),
                                ft.Column(spacing=4, controls=[
                                    ft.Text(name, color="white", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{phone} | {email} | {address}", color="#59657a", size=12)
                                ])
                            ]),
                            ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4, controls=[
                                ft.Text(f"₹{spent:,.2f}", color=GREEN, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{orders} Orders", color="#59657a", size=12)
                            ])
                        ]
                    )
                )
            )
        page.update()

    def search_customers(e):
        q = (search_input.current.value or "").strip().lower()
        nonlocal filtered_customers
        if not q:
            filtered_customers = all_customers[:]
        else:
            filtered_customers = [
                c for c in all_customers 
                if q in c.get("name", "").lower() or 
                   q in c.get("phone", "").lower() or 
                   q in (c.get("email") or "").lower() or
                   q in (c.get("aadhaar_number") or "").lower()
            ]
        render_customers()

    def on_prev():
        if state["current_page"] > 0:
            state["current_page"] -= 1
            load_data()

    def on_next():
        state["current_page"] += 1
        load_data()

    def load_data():
        try:
            nonlocal all_customers, filtered_customers, all_sales, all_emis
            cust_data, cust_status = api_client.get_business_customers(business_id)
            if cust_status == 200:
                all_customers = cust_data if isinstance(cust_data, list) else []
                filtered_customers = all_customers[:]
            
            sales_data, sales_status = api_client.get_business_sales(business_id)
            if sales_status == 200:
                all_sales = sales_data if isinstance(sales_data, list) else []
                
            emi_data, emi_status = api_client.get_business_emis(business_id)
            if emi_status == 200:
                all_emis = emi_data if isinstance(emi_data, list) else []
                
            render_customers()
        except Exception:
            pass

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=36, right=36, top=0, bottom=24),
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(
                                    spacing=5,
                                    controls=[
                                        ft.Text("Customer Directory", color="white", size=36, weight=ft.FontWeight.BOLD),
                                        ft.Text("VIEW AND MANAGE CUSTOMER PROFILES AND HISTORIES", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
                                    ]
                                ),
                                ft.Container(
                                    height=44, border_radius=12, bgcolor=CYAN,
                                    padding=ft.padding.symmetric(horizontal=16),
                                    alignment=ft.Alignment(0, 0), ink=True,
                                    on_click=lambda e: page.go(f"/businesses/{business_id}/customers/add"),
                                    content=ft.Row(
                                        tight=True, spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.ADD_ROUNDED, color="#042218", size=18),
                                            ft.Text("ADD CUSTOMER", color="#042218", size=10, weight=ft.FontWeight.BOLD)
                                        ]
                                    )
                                )
                            ]
                        ),
                        ft.Container(
                            height=50, border_radius=25, bgcolor=PANEL_BG, border=ft.border.all(1, BORDER),
                            padding=ft.padding.symmetric(horizontal=20),
                            content=ft.Row(
                                spacing=15,
                                controls=[
                                    ft.Icon(ft.Icons.SEARCH, color="#3d4a5c", size=20),
                                    ft.TextField(
                                        ref=search_input,
                                        hint_text="Search by Name, Phone, Email, or Aadhaar...",
                                        hint_style=ft.TextStyle(color="#3d4a5c", size=14),
                                        border=ft.InputBorder.NONE,
                                        color="white",
                                        text_size=14,
                                        expand=True,
                                        on_change=search_customers
                                    )
                                ]
                            )
                        )
                    ]
                ),
                ft.Container(
                    expand=True,
                    content=customer_list
                )
            ]
        )
    )

    load_data()
    main_content.content.controls.append(pagination_container)
    return main_content

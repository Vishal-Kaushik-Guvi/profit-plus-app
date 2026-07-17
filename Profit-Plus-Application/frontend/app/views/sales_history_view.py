import flet as ft
from app.api_client import api_client
from app.component.pagination_controls import PaginationControls

BG = "#020710"
PANEL_BG = "#070d17"
BORDER = "#131b2a"
CYAN = "#16cdf2"
GREEN = "#14d59b"

def SalesHistoryView(page: ft.Page, business_id: str):
    
    sales_list = ft.ListView(expand=True, spacing=15)
    
    # Pagination state
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    
    def on_prev():
        if state["current_page"] > 0:
            state["current_page"] -= 1
            load_sales()
            
    def on_next():
        state["current_page"] += 1
        load_sales()
    
    def load_sales():
        sales_list.controls.clear()
        skip = state["current_page"] * state["limit"]
        data, status = api_client.get_business_sales(business_id, skip=skip, limit=state["limit"])
        if status == 200:
            for sale in data:
                items_str = ", ".join(f"{i['name']} (x{i['quantity']})" for i in sale.get('items', []))
                
                sales_list.controls.append(
                    ft.Container(
                        padding=20,
                        border_radius=12,
                        bgcolor=PANEL_BG,
                        border=ft.border.all(1, BORDER),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Row(
                                            spacing=10,
                                            controls=[
                                                ft.Text(sale.get('invoice_no', 'TRX-UNKNOWN'), color="white", size=16, weight=ft.FontWeight.BOLD),
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                    border_radius=6,
                                                    bgcolor="#0d2b1f" if not sale.get('is_emi') else "#2b1b0d",
                                                    content=ft.Text("CASH" if not sale.get('is_emi') else "EMI", color=GREEN if not sale.get('is_emi') else "#f59e0b", size=10, weight=ft.FontWeight.BOLD)
                                                )
                                            ]
                                        ),
                                        ft.Text(f"Customer: {sale.get('buyer_name') or 'N/A'}", color="#59657a", size=12),
                                        ft.Text(f"Items: {items_str}", color="#59657a", size=11, max_lines=1)
                                    ]
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=4,
                                    controls=[
                                        ft.Text(f"?{sale.get('total_amount', 0):,.2f}", color=CYAN, size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"{sale.get('transaction_date', '')} {sale.get('transaction_time', '')}", color="#59657a", size=10)
                                    ]
                                )
                            ]
                        )
                    )
                )
            pagination_container.content = PaginationControls(
                page, state["current_page"], len(data), state["limit"], on_prev, on_next
            )
        page.update()
        
    # Main Layout
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
                                ft.Text("Sales History", color="white", size=36, weight=ft.FontWeight.BOLD),
                                ft.Text("ALL PAST TRANSACTIONS", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.ElevatedButton(
                            "NEW BILL",
                            bgcolor=CYAN, color="#001824",
                            on_click=lambda e: page.go(f"/businesses/{business_id}/billing")
                        )
                    ]
                ),
                ft.Container(
                    expand=True,
                    content=sales_list
                ),
                pagination_container
            ]
        )
    )
    
    load_sales()
    return main_content

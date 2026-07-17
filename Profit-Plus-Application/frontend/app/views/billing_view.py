import flet as ft
from app.api_client import api_client
from app.component.pagination_controls import PaginationControls
import uuid

BG = "#020710"
PANEL_BG = "#070d17"
BORDER = "#131b2a"
CYAN = "#16cdf2"
GREEN = "#14d59b"
PURPLE = "#6d22d9"

def BillingView(page: ft.Page, business_id: str):
    state = {"current_page": 0, "limit": 10}
    pagination_container = ft.Container()
    
    # State
    all_inventory = []
    filtered_inventory = []
    cart = [] # list of dicts: {'item': inv_item, 'qty': 1}
    
    # Customer Details
    cust_name = ft.Ref[ft.TextField]()
    cust_phone = ft.Ref[ft.TextField]()
    cust_email = ft.Ref[ft.TextField]()
    cust_address = ft.Ref[ft.TextField]()
    cust_gstin = ft.Ref[ft.TextField]()
    cust_pos = ft.Ref[ft.TextField]()
    
    # Billing Settings
    is_credit = False
    is_emi = False
    discount_pct = ft.Ref[ft.TextField]()
    
    # EMI Settings
    emi_downpayment = ft.Ref[ft.TextField]()
    emi_id = ft.Ref[ft.TextField]()
    emi_interest = ft.Ref[ft.TextField]()
    emi_tenure = ft.Ref[ft.TextField]()
    
    search_input = ft.Ref[ft.TextField]()
    
    # UI Containers
    inventory_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=15, expand=True)
    cart_list = ft.Column(spacing=10)
    
    subtotal_text = ft.Text("₹0.00", color="white", size=10, weight=ft.FontWeight.BOLD)
    total_text = ft.Text("₹0.00", color=GREEN, size=18, weight=ft.FontWeight.BOLD)
    
    # Calculate Totals
    def update_totals():
        sub = sum(item['qty'] * (item['item'].get('selling_price') or 0) for item in cart)
        try:
            disc = float(discount_pct.current.value or 0)
        except ValueError:
            disc = 0
            
        tot = sub * (1 - disc / 100)
        
        subtotal_text.value = f"₹{sub:,.2f}"
        total_text.value = f"₹{tot:,.2f}"
        
        cart_list_container.content.controls[0].controls[1].content.value = f"{len(cart)} items"
        calculate_expected_emi()
        
        
    def render_cart():
        new_cart = []
        for idx, cart_item in enumerate(cart):
            inv = cart_item['item']
            prod = inv.get("product") or {}
            name = prod.get("product_name") or inv.get("product_name") or "Item"
            price = inv.get("selling_price") or 0
            unit = (inv.get("unit") or "PCS").upper()
            color = prod.get("color") or ""
            size = prod.get("size") or ""
            
            def make_qty_changer(index):
                def change_qty(delta):
                    inv_item = cart[index]['item']
                    stock = inv_item.get("stock_quantity", 0) or 0
                    if delta > 0 and cart[index]['qty'] + delta > stock:
                        sb = ft.SnackBar(ft.Text("Not enough stock!"), bgcolor="red")
                        page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                        page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                        page.overlay.append(sb)
                        sb.open = True
                        page.update()
                        return
                        
                    cart[index]['qty'] += delta
                    if cart[index]['qty'] <= 0:
                        cart.pop(index)
                    render_cart()
                    update_totals()
                    page.update()
                return change_qty
                
            def remove_item(index):
                cart.pop(index)
                render_cart()
                update_totals()
                page.update()
            
            new_cart.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor="#050a14",
                    border=ft.border.all(1, "#1a2535"),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(name, color="white", size=14, weight=ft.FontWeight.BOLD),
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    ft.Text(f"#{str(prod.get('id', ''))[:8]}", color="#59657a", size=10),
                                                    ft.Text(f"HSN: {prod.get('hsn_code', 'N/A')}", color=GREEN, size=10, weight=ft.FontWeight.BOLD),
                                                    ft.Text(f"{color.upper()} • {size.upper()}", color=CYAN, size=10, weight=ft.FontWeight.BOLD)
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CLOSE,
                                        icon_color="#59657a",
                                        icon_size=16,
                                        on_click=lambda e, i=idx: remove_item(i)
                                    )
                                ]
                            ),
                            ft.Container(
                                padding=ft.padding.only(top=10),
                                border=ft.border.only(top=ft.BorderSide(1, "#1a2535")),
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("QUANTITY & UNIT", color="#59657a", size=9, weight=ft.FontWeight.BOLD),
                                        ft.Row(
                                            spacing=15,
                                            controls=[
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                    border_radius=8,
                                                    bgcolor="#0a121e",
                                                    border=ft.border.all(1, "#1a2535"),
                                                    content=ft.Row(
                                                        spacing=12,
                                                        controls=[
                                                            ft.IconButton(icon=ft.Icons.REMOVE, icon_color="white", icon_size=14, on_click=lambda e, i=idx: make_qty_changer(i)(-1)),
                                                            ft.Text(str(cart_item['qty']), color=CYAN, size=12, weight=ft.FontWeight.BOLD),
                                                            ft.IconButton(icon=ft.Icons.ADD, icon_color="white", icon_size=14, on_click=lambda e, i=idx: make_qty_changer(i)(1))
                                                        ]
                                                    )
                                                ),
                                                ft.Text(f"TOTAL: ₹{(price * cart_item['qty']):,.2f}", color="white", size=10, weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                )
            )
        cart_list.controls = new_cart
            
        

    def add_to_cart(inv_item):
        stock = inv_item.get("stock_quantity", 0) or 0
        if stock <= 0:
            sb = ft.SnackBar(ft.Text("Out of stock! Cannot add to bill."), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
            
        for item in cart:
            if item['item']['id'] == inv_item['id']:
                if item['qty'] + 1 > stock:
                    sb = ft.SnackBar(ft.Text("Not enough stock!"), bgcolor="red")
                    for c in list(page.overlay):
                        if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                            try: page.overlay.remove(c)
                            except: pass
                    page.overlay.append(sb)
                    sb.open = True
                    page.update()
                    return
                item['qty'] += 1
                render_cart()
                update_totals()
                page.update()
                return
        cart.append({'item': inv_item, 'qty': 1})
        render_cart()
        update_totals()
        page.update()
        
    def render_inventory():
        new_controls = []
        for inv in filtered_inventory:
            prod = inv.get("product") or {}
            name = prod.get("product_name") or inv.get("product_name") or "Unknown"
            brand = prod.get("brand") or inv.get("brand") or ""
            stock = inv.get("stock_quantity", 0) or 0
            unit = (inv.get("unit") or "PCS").upper()
            price = inv.get("selling_price", 0) or 0
            color = prod.get("color") or ""
            size = prod.get("size") or ""
            
            badges = []
            if color:
                badges.append(ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4, border=ft.border.all(1, "#1a2535"),
                    content=ft.Text(f"COLOR: {color.upper()}", color="white", size=8, weight=ft.FontWeight.BOLD)
                ))
            if size:
                badges.append(ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4, border=ft.border.all(1, "#0a3a42"), bgcolor="#041a1e",
                    content=ft.Text(f"SIZE: {size.upper()}", color=CYAN, size=8, weight=ft.FontWeight.BOLD)
                ))
                
            new_controls.append(
                ft.Container(
                    padding=20,
                    border_radius=16,
                    bgcolor=PANEL_BG,
                    border=ft.border.only(left=ft.BorderSide(3, CYAN), top=ft.BorderSide(1, BORDER), right=ft.BorderSide(1, BORDER), bottom=ft.BorderSide(1, BORDER)),
                    ink=True,
                    on_click=lambda e, item=inv: add_to_cart(item),
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=15,
                                        controls=[
                                            ft.Container(
                                                width=48, height=48, border_radius=12,
                                                bgcolor="#0d1a27", border=ft.border.all(1, "#1a2e40"),
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=CYAN, size=24)
                                            ),
                                            ft.Column(
                                                spacing=4,
                                                controls=[
                                                    ft.Text(name, color="white", size=18, weight=ft.FontWeight.BOLD),
                                                    ft.Row(spacing=8, controls=badges) if badges else ft.Container()
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                        border_radius=20,
                                        border=ft.border.all(1, "#332200"),
                                        bgcolor="#1a1100",
                                        content=ft.Text(f"{int(stock)} {unit}", color="#f59e0b", size=10, weight=ft.FontWeight.BOLD)
                                    )
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"₹{price:,.2f}", color="white", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"({brand})" if brand else "", color="#59657a", size=11)
                                ]
                            )
                        ]
                    )
                )
            )
        inventory_list.controls = new_controls
        pagination_container.content = PaginationControls(page, state["current_page"], len(filtered_inventory), state["limit"], on_prev, on_next)
        page.update()

    def filter_inventory(e):
        q = (search_input.current.value or "").strip().lower()
        nonlocal filtered_inventory
        if not q:
            filtered_inventory = all_inventory[:]
        else:
            filtered_inventory = [
                inv for inv in all_inventory 
                if q in ((inv.get("product") or {}).get("product_name") or inv.get("product_name") or "").lower()
            ]
        render_inventory()
        
    def toggle_emi(e):
        nonlocal is_emi
        is_emi = e.control.value
        emi_container.visible = is_emi
        page.update()
        
    def toggle_credit(e):
        nonlocal is_credit
        is_credit = e.control.value
        
    def format_aadhaar(e):
        val = e.control.value.replace(" ", "")
        val = ''.join(c for c in val if c.isdigit())
        if len(val) > 12:
            val = val[:12]
        formatted = " ".join([val[i:i+4] for i in range(0, len(val), 4)]).strip()
        if e.control.value != formatted:
            e.control.value = formatted
            e.control.update()
            
    def input_field(ref, label, icon=None, expand=False, **kwargs):
        return ft.Container(
            expand=expand,
            height=44,
            border_radius=8,
            bgcolor="#0a121e",
            border=ft.border.all(1, "#1a2535"),
            padding=ft.padding.symmetric(horizontal=12),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(icon, color="#3d4a5c", size=16) if icon else ft.Container(),
                    ft.TextField(
                        ref=ref,
                        hint_text=label,
                        hint_style=ft.TextStyle(color="#3d4a5c", size=12),
                        border=ft.InputBorder.NONE,
                        color="white",
                        text_size=12,
                        expand=True,
                        content_padding=0,
                        **kwargs
                    )
                ]
            )
        )

    emi_calc_card = ft.Container(
        visible=False,
        padding=12,
        border_radius=8,
        bgcolor="#0a121e",
        border=ft.border.all(1, "#1a2535"),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("EXPECTED MONTHLY EMI", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                ft.Text("₹0.00", color=GREEN, size=14, weight=ft.FontWeight.BOLD)
            ]
        )
    )

    def calculate_expected_emi(e=None):
        try:
            sub = sum(item['qty'] * (item['item'].get('selling_price') or 0) for item in cart)
            disc = float(discount_pct.current.value or 0) if discount_pct.current.value else 0
            tot = sub * (1 - disc / 100)
            
            dp = float(emi_downpayment.current.value or 0) if emi_downpayment.current.value else 0
            rate = float(emi_interest.current.value or 0) if emi_interest.current.value else 0
            months = int(emi_tenure.current.value or 0) if emi_tenure.current.value else 0
            
            if months > 0:
                principal = tot - dp
                if principal > 0:
                    total_interest = principal * (rate / 100.0) * months
                    total_payable = principal + total_interest
                    monthly = total_payable / months
                    emi_calc_card.content.controls[1].value = f"₹{monthly:,.2f}"
                    emi_calc_card.visible = True
                else:
                    emi_calc_card.visible = False
            else:
                emi_calc_card.visible = False
        except Exception:
            emi_calc_card.visible = False
        if e:
            page.update()

    emi_container = ft.Container(
        visible=False,
        padding=16,
        border_radius=12,
        bgcolor="#050a14",
        border=ft.border.all(1, "#1a2535"),
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Column(expand=True, spacing=6, controls=[ft.Text("DOWN PAYMENT", color="#59657a", size=9, weight=ft.FontWeight.BOLD), input_field(emi_downpayment, "0", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$"), on_change=calculate_expected_emi)]),
                        ft.Column(expand=True, spacing=6, controls=[ft.Text("AADHAAR", color="#59657a", size=9, weight=ft.FontWeight.BOLD), input_field(emi_id, "12 Digit Aadhaar", on_change=format_aadhaar)])
                    ]
                ),
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Column(expand=True, spacing=6, controls=[ft.Text("INTEREST/MONTH (%)", color="#59657a", size=9, weight=ft.FontWeight.BOLD), input_field(emi_interest, "e.g. 2", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$"), on_change=calculate_expected_emi)]),
                        ft.Column(expand=True, spacing=6, controls=[ft.Text("MONTHS (TENURE)", color="#59657a", size=9, weight=ft.FontWeight.BOLD), input_field(emi_tenure, "e.g. 6", input_filter=ft.NumbersOnlyInputFilter(), on_change=calculate_expected_emi)])
                    ]
                ),
                emi_calc_card
            ]
        )
    )

    cart_list_container = ft.Container(
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("PRODUCTS", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12, border=ft.border.all(1, "#1a2535"),
                            content=ft.Text("0 items", color="#59657a", size=9)
                        )
                    ]
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[cart_list])
                )
            ]
        )
    )

    def finalize_bill():
        if not cart:
            sb = ft.SnackBar(ft.Text("Cart is empty! Add items first."), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
            
        if not cust_name.current.value or not cust_name.current.value.strip():
            sb = ft.SnackBar(ft.Text("Customer Name is required!"), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
            
        if not cust_phone.current.value or not cust_phone.current.value.strip():
            sb = ft.SnackBar(ft.Text("Customer Phone is required!"), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
            
        sub = sum(item['qty'] * (item['item'].get('selling_price') or 0) for item in cart)
        try:
            disc = float(discount_pct.current.value or 0)
        except ValueError:
            sb = ft.SnackBar(ft.Text("Discount must be a number!"), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()
            return
            
        tot = sub * (1 - disc / 100)
        
        payload = {
            "business_id": business_id,
            "buyer_name": cust_name.current.value,
            "buyer_phone": cust_phone.current.value,
            "buyer_email": cust_email.current.value,
            "buyer_address": cust_address.current.value,
            "buyer_gstin": cust_gstin.current.value,
            "place_of_supply": cust_pos.current.value,
            "subtotal": sub,
            "discount_percentage": disc,
            "total_amount": tot,
            "is_emi": is_emi,
            "items": []
        }
        
        if is_emi:
            if not emi_id.current.value or len(emi_id.current.value.replace(" ", "")) > 12:
                sb = ft.SnackBar(ft.Text("Valid Aadhaar (upto 12 digits) is required for EMI!"), bgcolor="red")
                page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                page.overlay.append(sb)
                sb.open = True
                page.update()
                return
            try:
                dp = float(emi_downpayment.current.value or 0)
                if dp > sub * 0.5:
                    sb = ft.SnackBar(ft.Text("Downpayment cannot be more than 50% of subtotal!"), bgcolor="red")
                    for c in list(page.overlay):
                        if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                            try: page.overlay.remove(c)
                            except: pass
                    page.overlay.append(sb)
                    sb.open = True
                    page.update()
                    return
                payload["emi_down_payment"] = dp
                payload["aadhaar_number"] = emi_id.current.value.replace(" ", "")
                payload["emi_interest_rate"] = float(emi_interest.current.value or 0)
                payload["emi_months"] = int(emi_tenure.current.value or 0)
                if payload["emi_months"] <= 0:
                    raise ValueError()
            except ValueError:
                sb = ft.SnackBar(ft.Text("EMI fields must be valid numbers!"), bgcolor="red")
                page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                page.overlay.append(sb)
                sb.open = True
                page.update()
                return
                
        for c in cart:
            inv = c['item']
            prod = inv.get("product") or {}
            qty = c['qty']
            price = inv.get("selling_price") or 0
            payload["items"].append({
                "product_id": prod.get("id"),
                "name": prod.get("product_name") or inv.get("product_name") or "Item",
                "quantity": qty,
                "unit_price": price,
                "total_price": price * qty
            })
            
        res, status = api_client.create_sale(payload)
        if status in [200, 201]:
            txn_id = res.get('id', '')
            amt = res.get('total_amount', 0)
            name = res.get('buyer_name', '')
            page.go(f"/businesses/{business_id}/billing/success?txn={txn_id}&amt={amt}&name={name}")
        else:
            sb = ft.SnackBar(ft.Text(f"Error creating bill: {res}"), bgcolor="red")
            for c in list(page.overlay):
                if getattr(c, "open", None) is False or type(c).__name__ == "SnackBar":
                    try: page.overlay.remove(c)
                    except: pass
            page.overlay.append(sb)
            sb.open = True
            page.update()

    right_panel = ft.Container(
        expand=4,
        padding=24,
        border_radius=20,
        bgcolor="#060b14",
        border=ft.border.all(1, "#131b2a"),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # Header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=40, height=40, border_radius=12,
                                    bgcolor="#041a1e", border=ft.border.all(1, "#0a3a42"),
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.CHECK, color=CYAN, size=20)
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Active Bill", color="white", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("TERMINAL SESSION", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
                                    ]
                                )
                            ]
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=8, border=ft.border.all(1, "#0a3a42"), bgcolor="#041a1e",
                            content=ft.Text(f"TRX-{str(uuid.uuid4())[:4].upper()}", color=CYAN, size=10, weight=ft.FontWeight.BOLD)
                        )
                    ]
                ),
                ft.Divider(color="#131b2a", height=1),
                
                # Customer Details
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(spacing=12, controls=[input_field(cust_name, "Search or Enter Name", ft.Icons.PERSON, True), input_field(cust_phone, "Phone", ft.Icons.PHONE, True, input_filter=ft.NumbersOnlyInputFilter())]),
                        input_field(cust_email, "Customer Email (Optional)", ft.Icons.EMAIL),
                        input_field(cust_address, "Customer Address", ft.Icons.LOCATION_ON),
                        ft.Row(spacing=12, controls=[input_field(cust_gstin, "Buyer GSTIN (Optional)", expand=True), input_field(cust_pos, "Place of Supply", expand=True)]),
                    ]
                ),
                
                ft.Divider(color="#131b2a", height=1),
                
                # Cart
                cart_list_container,
                
                # EMI Checkbox
                ft.Checkbox(label="PURCHASE ON EMI", value=False, on_change=toggle_emi, label_style=ft.TextStyle(color="white", size=11, weight=ft.FontWeight.BOLD), fill_color=GREEN),
                emi_container,
                
                ft.Divider(color="#131b2a", height=1),
                
                # Totals & Finalize
                ft.Column(
                    spacing=15,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Switch(value=False, on_change=toggle_credit, active_color=PURPLE),
                                        ft.Text("UDHAR / CREDIT", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
                                    ]
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Text("SUBTOTAL", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                        subtotal_text
                                    ]
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Text("DISCOUNT", color="#59657a", size=10, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            width=60, height=32, border_radius=8, bgcolor="#0a121e", border=ft.border.all(1, "#1a2535"),
                                            content=ft.TextField(ref=discount_pct, value="0", text_align=ft.TextAlign.CENTER, border=ft.InputBorder.NONE, color="white", text_size=12, on_change=lambda e: update_totals())
                                        ),
                                        ft.Text("%", color="#3d4a5c", size=12)
                                    ]
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=2,
                                    controls=[
                                        ft.Text("TOTAL AMOUNT", color="white", size=10, weight=ft.FontWeight.BOLD),
                                        total_text
                                    ]
                                )
                            ]
                        ),
                        ft.Container(
                            height=54, border_radius=12, bgcolor=GREEN, alignment=ft.Alignment(0, 0), ink=True,
                            on_click=lambda e: finalize_bill(),
                            content=ft.Row(
                                tight=True, spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#042218", size=20),
                                    ft.Text("FINALIZE BILL", color="#042218", size=14, weight=ft.FontWeight.BOLD)
                                ]
                            )
                        )
                    ]
                )
            ]
        )
    )

    left_panel = ft.Container(
        expand=6,
        padding=ft.padding.only(right=30),
        content=ft.Column(
            spacing=28,
            controls=[
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("Make Bill", color="white", size=36, weight=ft.FontWeight.BOLD),
                                ft.Text("SELECT ITEMS FOR THE NEW BILL", color="#59657a", size=10, weight=ft.FontWeight.BOLD)
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
                                        hint_text="Search all items...",
                                        hint_style=ft.TextStyle(color="#3d4a5c", size=14),
                                        border=ft.InputBorder.NONE,
                                        color="white",
                                        text_size=14,
                                        expand=True,
                                        on_change=filter_inventory
                                    )
                                ]
                            )
                        )
                    ]
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(controls=[inventory_list, pagination_container])
                )
            ]
        )
    )

    main_content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=36, right=36, top=32, bottom=24),
        content=ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[left_panel, right_panel]
        )
    )

    def on_prev():
        if state["current_page"] > 0:
            state["current_page"] -= 1
            load_inventory()

    def on_next():
        state["current_page"] += 1
        load_inventory()

    def load_inventory():
        try:
            data, status = api_client.get_inventory(business_id, skip=state["current_page"] * state["limit"], limit=state["limit"])
            if status == 200:
                nonlocal all_inventory, filtered_inventory
                all_inventory = data if isinstance(data, list) else []
                filtered_inventory = all_inventory[:]
                render_inventory()
        except Exception:
            pass

    load_inventory()
    return main_content

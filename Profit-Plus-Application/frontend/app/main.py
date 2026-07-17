import os
import flet as ft

from app.api_client import api_client
from app.views.home_view import HomeView
from app.views.login_view import LoginView
from app.views.forgot_password_view import ForgotPasswordView
from app.views.admin_dashboard_view import AdminDashboardView
from app.views.admin_users_view import AdminUsersView
from app.views.admin_businesses_view import AdminBusinessesView
from app.views.admin_revenue_view import AdminRevenueView
from app.views.createbusiness_view import CreateBusinessView

from app.views.business_dashboard_view import BusinessDashboardView
from app.views.mybusiness_view import MyBusinessView
from app.views.signup_view import SignupView
from app.views.product_view import ProductsView
from app.views.addproduct_view import AddProductView
from app.views.inventory_view import InventoryView
from app.views.restock_view import RestockView
from app.views.billing_view import BillingView
from app.views.billing_success_view import BillingSuccessView
from app.views.sales_history_view import SalesHistoryView
from app.views.emi_management_view import EmiManagementView
from app.views.analytics_view import AnalyticsView
from app.views.customer_view import CustomerView
from app.views.subscription_view import SubscriptionView
from app.component.sidebar_view import HubSidebar, BusinessSidebar, AdminSidebar


from app.component.background_view import create_animated_background

def main(page: ft.Page):
    page.title = "Profit Plus"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800

    sidebar_container = ft.Container(visible=False, expand=False)
    main_content_container = ft.Container(expand=True)
    
    animated_bg = create_animated_background(page)

    master_view = ft.View(
        route="/",
        padding=0,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    animated_bg,
                    ft.Row(
                        expand=True,
                        spacing=0,
                        controls=[sidebar_container, main_content_container],
                    ),
                ],
            )
        ],
    )

    def route_change(e):
        if master_view not in page.views:
            page.views.clear()
            page.views.append(master_view)
        
        master_view.route = page.route

        public_routes = ["/", "/login", "/signup", "/forgot-password"]
        if page.route not in public_routes and not api_client.token:
            page.go("/login")
            return


        current_content = None
        
        def _fetch_and_update_bus_info(b_id, n_text, i_text):
            try:
                data, status = api_client.get_business(b_id)
                if status == 200:
                    name = (data.get("business_name") or "Business").strip()
                    n_text.value = name
                    i_text.value = "".join(p[0] for p in name.split()[:2]).upper() or "B"
                    page.update()
            except Exception:
                pass

        if page.route == "/":
            sidebar_container.visible = False
            current_content = HomeView(page)

        elif page.route == "/login":
            sidebar_container.visible = False
            current_content = LoginView(page)

        elif page.route == "/signup":
            sidebar_container.visible = False
            current_content = SignupView(page)

        elif page.route == "/forgot-password":
            sidebar_container.visible = False
            current_content = ForgotPasswordView(page)
        elif page.route.startswith("/admin"):
            sidebar = AdminSidebar(page, page.route)
            sidebar_container.content = sidebar
            sidebar_container.visible = True
            
            if page.route == "/admin/dashboard":
                current_content = AdminDashboardView(page)
            elif page.route == "/admin/users":
                current_content = AdminUsersView(page)
            elif page.route == "/admin/businesses":
                current_content = AdminBusinessesView(page)
            elif page.route == "/admin/revenue":
                current_content = AdminRevenueView(page)
            elif page.route == "/admin/subscriptions":
                from app.views.admin_subscriptions_view import AdminSubscriptionsView
                current_content = AdminSubscriptionsView(page)
            else:
                current_content = ft.Container(
                    expand=True,
                    padding=40,
                    content=ft.Column(
                        controls=[
                            ft.Text("Coming Soon", size=32, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text(f"This is the placeholder for {page.route}", color="white54")
                        ]
                    )
                )


        elif page.route in ["/businesses", "/businesses/create"]:
            sidebar, user_name_text, user_initials_text, user_email_text = HubSidebar(page, page.route)
            def load_user_info():
                try:
                    data, status = api_client.get_me()
                    if status == 200:
                        name = (data.get("full_name") or "User").strip()
                        user_name_text.value = name
                        user_initials_text.value = "".join(p[0] for p in name.split()[:2]).upper() or "U"
                        user_email_text.value = data.get("email") or ""
                        page.update()
                except Exception:
                    pass
            load_user_info()
                
            sidebar_container.content = sidebar
            sidebar_container.visible = True
            
            if page.route == "/businesses":
                current_content = MyBusinessView(page)
            else:
                current_content = CreateBusinessView(page)


        elif page.route.startswith("/businesses/") and "/billing" in page.route:
            parts = page.route.split("/")
            business_id = parts[2]
            
            base_route = page.route.split("?")[0]
            if base_route.endswith("/billing"):
                current_content = BillingView(page, business_id)
            elif base_route.endswith("/billing/success"):
                current_content = BillingSuccessView(page, business_id)
            else:
                page.go(f"/businesses/{business_id}/billing")
                return
            sidebar, name_text, init_text = BusinessSidebar(page, business_id, page.route)
            
            _fetch_and_update_bus_info(business_id, name_text, init_text)
                
            sidebar_container.content = sidebar
            sidebar_container.visible = True

        elif page.route.startswith("/businesses/") and "/sales" in page.route:
            parts = page.route.split("/")
            business_id = parts[2]
            current_content = SalesHistoryView(page, business_id)
            sidebar, name_text, init_text = BusinessSidebar(page, business_id, page.route)
            _fetch_and_update_bus_info(business_id, name_text, init_text)
            sidebar_container.content = sidebar
            sidebar_container.visible = True

        elif page.route.startswith("/businesses/") and "/emi" in page.route:
            parts = page.route.split("/")
            business_id = parts[2]
            current_content = EmiManagementView(page, business_id)
            sidebar, name_text, init_text = BusinessSidebar(page, business_id, page.route)
            _fetch_and_update_bus_info(business_id, name_text, init_text)
            sidebar_container.content = sidebar
            sidebar_container.visible = True

        elif page.route.startswith("/businesses/"):
            parts = page.route.split("/")
            business_id = parts[2] if len(parts) > 2 else ""
            
            sidebar, name_text, init_text = BusinessSidebar(page, business_id, page.route)
            
            _fetch_and_update_bus_info(business_id, name_text, init_text)
                
            sidebar_container.content = sidebar
            sidebar_container.visible = True

            if page.route.endswith("/dashboard"):
                current_content = BusinessDashboardView(page, business_id)

            elif page.route.endswith("/analytics"):
                current_content = AnalyticsView(page, business_id)

            elif page.route.endswith("/customers"):
                current_content = CustomerView(page, business_id)

            elif page.route.endswith("/profile"):
                from app.views.business_profile_edit_view import BusinessProfileEditView
                current_content = BusinessProfileEditView(page, business_id)

            elif page.route.endswith("/subscription"):
                current_content = SubscriptionView(page, business_id)

            elif "/products" in page.route:
                if page.route.endswith("/products"):
                    current_content = ProductsView(page, business_id)
                elif page.route.endswith("/products/add"):
                    current_content = AddProductView(page, business_id)
                elif len(parts) >= 6 and parts[5] == "edit":
                    current_content = AddProductView(page, business_id, parts[4])
                else:
                    page.go(f"/businesses/{business_id}/products")
                    return

            elif "/inventory" in page.route:
                if page.route.endswith("/inventory"):
                    current_content = InventoryView(page, business_id)
                elif len(parts) >= 6 and parts[5] == "restock":
                    current_content = RestockView(page, business_id, parts[4])
                else:
                    page.go(f"/businesses/{business_id}/inventory")
                    return

            else:
                current_content = ft.Text("Coming Soon", color="white", size=24)
        else:
            page.go("/")
            return

        main_content_container.content = current_content
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change(None)

    if api_client.token:
        data, status = api_client.get_me()
        if status == 200:
            if data.get("id") == "admin":
                page.go("/admin/dashboard")
            else:
                page.go("/businesses")
        else:
            api_client.set_token(None)
            page.go("/")
    else:
        page.go("/")

    page.update()


if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(port))
    else:
        ft.app(target=main)

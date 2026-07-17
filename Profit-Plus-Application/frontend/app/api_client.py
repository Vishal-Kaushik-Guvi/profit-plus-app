import base64
import os
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")
TOKEN_FILE = Path(__file__).resolve().parents[1] / ".auth_token"
REQUEST_TIMEOUT = 15
CACHE_TTL_SECONDS = 3600


class ApiClient:

    def __init__(self):
        self.token = self._load_token()
        self.session = requests.Session()
        self.session.trust_env = False  # Completely disables Windows proxy checks which cause 2s lag
        self._get_cache = {}

    def _load_token(self):
        try:
            token = TOKEN_FILE.read_text(encoding="utf-8").strip()
            return token or None
        except OSError:
            return None

    def set_token(self, token: str):
        self.token = token
        self._get_cache.clear()
        if token:
            TOKEN_FILE.write_text(token, encoding="utf-8")
            return
        try:
            TOKEN_FILE.unlink()
        except FileNotFoundError:
            pass

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs):
        # Automatically invalidate ALL cached data whenever we mutate something!
        # This guarantees the user instantly sees fresh data after adding a product, sale, etc.
        if method in ("POST", "PUT", "DELETE"):
            self._get_cache.clear()
            
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        return self.session.request(method, f"{BASE_URL}{path}", **kwargs)
        
    def _get_cached(self, path: str):
        cache_entry = self._get_cache.get(path)
        if cache_entry and time.monotonic() - cache_entry[0] < CACHE_TTL_SECONDS:
            return cache_entry[1], cache_entry[2]
            
        response = self._request("GET", path)
        data, status = self._result(response)
        
        if status == 200:
            self._get_cache[path] = (time.monotonic(), data, status)
            
        return data, status

    @staticmethod
    def absolute_url(path: str):
        if not path:
            return path
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/"):
            return f"{BASE_URL}{path}"
        return path

    @staticmethod
    def _result(response):
        try:
            return response.json(), response.status_code
        except requests.exceptions.JSONDecodeError:
            message = response.text.strip() or "Server returned an invalid response"
            return {"detail": message}, response.status_code

    # ── Auth ──────────────────────────────────────────────────────

    def send_otp(self, email: str, purpose: str = "signup", phone: str = ""):
        payload = {"purpose": purpose, "email": email}
        if phone:
            payload["phone"] = phone
        response = self._request("POST", "/auth/send-otp", json=payload)
        return self._result(response)

    def signup(self, name: str, phone: str, email: str, password: str, otp: str):
        response = self._request(
            "POST",
            "/auth/signup",
            json={
                "name": name,
                "phone": phone,
                "email": email,
                "password": password,
                "otp": otp,
            },
        )
        return self._result(response)

    def login(self, email: str, password: str):
        response = self._request(
            "POST",
            "/auth/login",
            json={"email": email, "password": password},
        )
        return self._result(response)



    def get_me(self):
        return self._get_cached("/auth/me")

    def reset_password(self, email: str, otp: str, new_password: str):
        response = self._request(
            "POST",
            "/auth/reset-password",
            json={"email": email, "otp": otp, "new_password": new_password},
        )
        return self._result(response)

    # ── Business ──────────────────────────────────────────────────

    def get_my_businesses(self):
        return self._get_cached("/business/my-businesses")

    def get_business(self, business_id: str):
        return self._get_cached(f"/business/{business_id}")

    def create_business(
        self,
        business_name: str,
        phone: str = "",
        email: str = "",
        address: str = "",
        city: str = "",
        pincode: str = "",
        state: str = "",
        country: str = "",
        gst: str = "",
        referred_by_code: str = "",
        logo_path: str = "",
    ):
        payload = {
            "business_name": business_name,
            "phone": phone or None,
            "email": email or None,
            "address": address or None,
            "city": city or None,
            "pincode": pincode or None,
            "state": state or None,
            "country": country or None,
            "gst": gst or None,
            "referred_by_code": referred_by_code or None,
        }
        if logo_path:
            with open(logo_path, "rb") as logo_file:
                payload["logo_filename"] = os.path.basename(logo_path)
                payload["logo_data"] = base64.b64encode(logo_file.read()).decode(
                    "ascii"
                )
        response = self._request("POST", "/business/register", json=payload)
        return self._result(response)

    def get_dashboard_stats(self, business_id: str):
        return self._get_cached(f"/analytics/dashboard/{business_id}")

    def get_bi_terminal_stats(self, business_id: str, period: str = "day"):
        return self._get_cached(f"/analytics/bi-terminal/{business_id}?period={period}")

    def update_business(
        self,
        business_id: str,
        payload: dict,
        logo_path: str = ""
    ):
        if logo_path:
            with open(logo_path, "rb") as logo_file:
                payload["logo_filename"] = os.path.basename(logo_path)
                payload["logo_data"] = base64.b64encode(logo_file.read()).decode("ascii")
        response = self._request("PUT", f"/business/{business_id}", json=payload)
        return self._result(response)

    def delete_business(self, business_id: str):
        response = self._request("DELETE", f"/business/{business_id}")
        return self._result(response)

    # ── Products ──────────────────────────────────────────────────

    def create_product(
        self,
        business_id,
        product_name,
        category="",
        brand="",
        description="",
        hsn_code="",
        tax_percentage=0.0,
        color="",
        size="",
        business_type="",
    ):
        response = self._request(
            "POST",
            "/products/",
            json={
                "business_id": business_id,
                "product_name": product_name,
                "category": category,
                "brand": brand,
                "description": description,
                "hsn_code": hsn_code,
                "tax_percentage": tax_percentage,
                "color": color,
                "size": size,
                "business_type": business_type,
            },
        )
        return self._result(response)

    def get_products(self, business_id: str, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/products/business/{business_id}?skip={skip}&limit={limit}")

    def get_product(self, product_id: str):
        return self._get_cached(f"/products/{product_id}")

    def update_product(self, product_id: str, payload: dict):
        response = self._request("PUT", f"/products/{product_id}", json=payload)
        return self._result(response)

    def delete_product(self, product_id: str):
        response = self._request("DELETE", f"/products/{product_id}")
        return self._result(response)

    # ── Inventory ─────────────────────────────────────────────────

    def get_inventory(self, business_id: str, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/inventory/business/{business_id}?skip={skip}&limit={limit}")

    def update_inventory(self, inventory_id: str, payload: dict):
        response = self._request(
            "PUT",
            f"/inventory/{inventory_id}",
            json=payload,
        )
        return self._result(response)

    def create_inventory(self, business_id: str, product_id: str):
        payload = {"business_id": business_id, "product_id": product_id}
        response = self._request("POST", "/inventory/", json=payload)
        return self._result(response)

    def create_sale(self, payload: dict):
        response = self._request("POST", "/sales/", json=payload)
        return self._result(response)

    def get_business_sales(self, business_id: str, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/sales/business/{business_id}?skip={skip}&limit={limit}")

    def get_business_emis(self, business_id: str, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/emi/business/{business_id}?skip={skip}&limit={limit}")

    def create_emi_payment(self, payload: dict):
        response = self._request("POST", "/emi/payment", json=payload)
        return self._result(response)

    def download_pdf(self, sale_id: str, dest_path: str):
        response = self._request("GET", f"/sales/{sale_id}/pdf")
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(response.content)
            return True
        return False

    def send_pdf_email(self, sale_id: str, email: str):
        response = self._request("POST", f"/sales/{sale_id}/email", json={"email": email})
        return self._result(response)

    def get_business_customers(self, business_id: str, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/customers/business/{business_id}?skip={skip}&limit={limit}")

    def create_subscription_payment_link(self, business_id: str):
        response = self._request("POST", f"/subscription/create-payment-link/{business_id}")
        return self._result(response)

    def get_subscription_status(self, business_id: str):
        response = self._request("GET", f"/subscription/status/{business_id}")
        return self._result(response)

    def verify_order_status(self, business_id: str, order_id: str):
        """Verify a Razorpay order's payment status as a backup verification path."""
        response = self._request(
            "GET",
            f"/subscription/verify-order/{business_id}?order_id={order_id}",
        )
        return self._result(response)

    def get_admin_overview(self):
        return self._get_cached("/auth/admin/overview")

    def get_admin_users(self, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/auth/admin/users?skip={skip}&limit={limit}")

    def toggle_user_lock(self, user_id: str):
        response = self._request("POST", f"/auth/admin/users/{user_id}/toggle-lock")
        return self._result(response)

    def get_admin_businesses(self, skip: int = 0, limit: int = 10):
        return self._get_cached(f"/auth/admin/businesses?skip={skip}&limit={limit}")

    def get_admin_revenue(self, skip: int = 0, limit: int = 10):
        """Admin ONLY: Get revenue stats"""
        return self._get_cached(f"/auth/admin/revenue?skip={skip}&limit={limit}")
        
    def get_admin_subscriptions(self, skip: int = 0, limit: int = 10):
        """Admin ONLY: Get active subscriptions"""
        return self._get_cached(f"/auth/admin/subscriptions?skip={skip}&limit={limit}")
        
    def cancel_admin_subscription(self, business_id: str):
        """Admin ONLY: Cancel a subscription"""
        try:
            response = self._request("POST", f"/auth/admin/subscriptions/{business_id}/cancel")
            if response and response.status_code == 200:
                return True
        except:
            pass
        return False
        
    def get_pricing(self):
        try:
            response = self._request("GET", "/auth/pricing")
            if response and response.status_code == 200:
                return response.json()
        except:
            pass
        return {"PRO": 499}
        
    def update_admin_pricing(self, plan: str, price: int):
        """Admin ONLY: Update plan pricing"""
        try:
            response = self._request("POST", "/auth/admin/pricing", json={"plan": plan, "price": price})
            if response and response.status_code == 200:
                return True
        except:
            pass
        return False

    def invalidate_business_cache(self, business_id: str):
        self._get_cache.clear()


api_client = ApiClient()

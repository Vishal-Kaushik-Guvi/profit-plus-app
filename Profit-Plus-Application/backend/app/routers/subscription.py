from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.config import settings
from app.models.user import User
from app.models.business import Business, SubType
import razorpay
from datetime import datetime, timedelta, timezone
import json
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscription", tags=["Subscription"])

# ── Razorpay client ────────────────────────────────────────────────
try:
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
except Exception as exc:
    logger.error("Failed to initialize Razorpay client: %s", exc)
    razorpay_client = None


# ── HTML Templates ─────────────────────────────────────────────────
SUCCESS_HTML = """
<html>
    <head>
        <title>Payment Successful</title>
        <style>
            body { font-family: sans-serif; background-color: #0b101a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .container { text-align: center; background: #131a26; padding: 40px; border-radius: 12px; border: 1px solid #6d22d9; }
            h1 { color: #22c55e; }
            p { color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Payment Successful!</h1>
            <p>Your business has been upgraded to the <b>PRO</b> plan.</p>
            <p>You can now close this window and return to the application.</p>
        </div>
    </body>
</html>
"""

FAILED_HTML = """
<html>
    <head>
        <title>Payment Failed</title>
        <style>
            body { font-family: sans-serif; background-color: #0b101a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .container { text-align: center; background: #131a26; padding: 40px; border-radius: 12px; border: 1px solid #ef4444; }
            h1 { color: #ef4444; }
            p { color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Payment Failed</h1>
            <p>There was an issue processing your payment.</p>
            <p>You can close this window and try again from the application.</p>
        </div>
    </body>
</html>
"""

# Checkout HTML page that opens Razorpay inline checkout.
# All substitutions use .format() — JS braces are doubled ({{ }}).
CHECKOUT_HTML = """
<html>
    <head>
        <title>Profit Plus PRO Checkout</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <style>
            body {{ font-family: sans-serif; background-color: #0b101a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .container {{ text-align: center; background: #131a26; padding: 40px; border-radius: 12px; border: 1px solid #6d22d9; max-width: 460px; }}
            h1 {{ color: #f8fafc; }}
            p {{ color: #94a3b8; }}
            button {{ background: #6d22d9; color: white; border: 0; padding: 12px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; }}
            button:hover {{ background: #7c3aed; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Profit Plus PRO</h1>
            <p id="status">Opening secure Razorpay checkout...</p>
            <button id="retry" style="display:none;">Open checkout</button>
        </div>
        <script>
            const options = {options_json};
            const statusText = document.getElementById("status");
            const retryButton = document.getElementById("retry");

            options.handler = async function(response) {{
                statusText.textContent = "Verifying payment...";
                retryButton.style.display = "none";

                try {{
                    const verifyResponse = await fetch("{verify_url}", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify(response)
                    }});

                    if (verifyResponse.ok) {{
                        document.open();
                        document.write({success_html_json});
                        document.close();
                        return;
                    }}

                    const errorData = await verifyResponse.json().catch(() => null);
                    console.error("Verification failed:", errorData);
                }} catch (err) {{
                    console.error("Verification request failed:", err);
                }}

                document.open();
                document.write({failed_html_json});
                document.close();
            }};

            options.modal = {{
                ondismiss: function() {{
                    statusText.textContent = "Checkout was closed before payment was completed.";
                    retryButton.style.display = "inline-block";
                }}
            }};

            function openCheckout() {{
                try {{
                    const checkout = new Razorpay(options);
                    checkout.on("payment.failed", function(response) {{
                        statusText.textContent = "Payment failed: " + (response.error.description || "Unknown error");
                        retryButton.style.display = "inline-block";
                    }});
                    checkout.open();
                }} catch (err) {{
                    statusText.textContent = "Could not open checkout: " + err.message;
                    retryButton.style.display = "inline-block";
                }}
            }}

            retryButton.onclick = openCheckout;
            window.onload = openCheckout;
        </script>
    </body>
</html>
"""


# ── Helpers ────────────────────────────────────────────────────────

def _ensure_razorpay():
    """Raise a clear error if the Razorpay client is not configured."""
    if razorpay_client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Razorpay is not configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file."
            ),
        )


def _get_pro_price():
    """Read dynamic PRO price from pricing.json, default 499."""
    pricing_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "pricing.json",
    )
    pro_price = 499
    if os.path.exists(pricing_file):
        try:
            with open(pricing_file, "r") as f:
                pro_price = json.load(f).get("PRO", 499)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read pricing.json: %s", exc)
    return pro_price


def _customer_details(business: Business, current_user: User = None):
    """Build a customer prefill dict for Razorpay checkout."""
    raw_email = business.email or (current_user.email if current_user else "") or ""
    valid_email = (
        raw_email if "@" in raw_email and "." in raw_email else "customer@example.com"
    )

    raw_phone = business.phone or (current_user.phone if current_user else "") or "9876543210"
    valid_phone = raw_phone if len(set(raw_phone)) > 1 else "9876543210"

    return {
        "name": business.business_name or "Profit Plus Customer",
        "email": valid_email,
        "contact": valid_phone,
    }


def _mark_business_pro(business: Business, db: Session):
    """Upgrade a business to PRO subscription."""
    business.subscription_type = SubType.PRO
    business.subscription_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30)
    db.commit()


# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/create-payment-link/{business_id}")
def create_payment_link(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a Razorpay Order and returns a checkout page URL.

    This always uses the Checkout Order flow (not Payment Links) because:
    - Payment Links have a 30-link limit in test mode.
    - Checkout Orders work entirely client-side (no server callback needed).
    - UPI, cards, netbanking all work through the Razorpay checkout widget.
    """
    _ensure_razorpay()

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.subscription_type == SubType.PRO:
        raise HTTPException(status_code=400, detail="Business is already on PRO plan")

    try:
        pro_price = _get_pro_price()
        amount = int(pro_price * 100)  # Razorpay expects paise

        # Create an Order — this has no test-mode limit
        order = razorpay_client.order.create(
            {
                "amount": amount,
                "currency": "INR",
                "receipt": f"pro_{business.id}",
                "notes": {"business_id": str(business.id)},
            }
        )

        checkout_url = (
            f"{settings.RAZORPAY_CALLBACK_BASE_URL}"
            f"/subscription/checkout/{business.id}?order_id={order['id']}"
        )

        return {
            "payment_url": checkout_url,
            "order_id": order["id"],
            "payment_method": "checkout_order",
        }

    except razorpay.errors.BadRequestError as e:
        logger.error("Razorpay BadRequest: %s", e)
        raise HTTPException(
            status_code=400,
            detail=f"Razorpay rejected the request: {e}",
        )
    except Exception as e:
        logger.error("Razorpay Error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Could not create payment order. Reason: {e}",
        )


@router.get("/checkout/{business_id}")
def checkout_order_page(
    business_id: str,
    order_id: str,
    db: Session = Depends(get_db),
):
    """
    Serves the Razorpay checkout page.
    The browser opens this URL; the Razorpay widget pops up inline.
    On successful payment the JS handler posts to /checkout/verify.
    """
    _ensure_razorpay()

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        return HTMLResponse(content=FAILED_HTML, status_code=404)

    if business.subscription_type == SubType.PRO:
        return HTMLResponse(content=SUCCESS_HTML, status_code=200)

    pro_price = _get_pro_price()
    amount = int(pro_price * 100)
    customer = _customer_details(business)

    options = {
        "key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "currency": "INR",
        "name": "Profit Plus",
        "description": "Profit Plus Pro Subscription (1 Month)",
        "order_id": order_id,
        "prefill": customer,
        "theme": {"color": "#6d22d9"},
    }

    verify_url = (
        f"{settings.RAZORPAY_CALLBACK_BASE_URL}"
        f"/subscription/checkout/verify?business_id={business.id}"
    )

    return HTMLResponse(
        content=CHECKOUT_HTML.format(
            options_json=json.dumps(options),
            verify_url=verify_url,
            success_html_json=json.dumps(SUCCESS_HTML),
            failed_html_json=json.dumps(FAILED_HTML),
        ),
        status_code=200,
    )


@router.post("/checkout/verify")
async def verify_checkout_payment(
    request: Request,
    business_id: str,
    db: Session = Depends(get_db),
):
    """
    Verifies the payment signature after Razorpay checkout completes.
    Called from the checkout page's JS handler (same machine, so localhost works).
    """
    _ensure_razorpay()

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    required_fields = [
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
    ]
    if not all(payload.get(field) for field in required_fields):
        raise HTTPException(status_code=400, detail="Missing payment verification data")

    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": payload["razorpay_order_id"],
                "razorpay_payment_id": payload["razorpay_payment_id"],
                "razorpay_signature": payload["razorpay_signature"],
            }
        )
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    _mark_business_pro(business, db)
    return {"message": "Subscription upgraded successfully"}


@router.get("/callback")
def payment_callback(
    request: Request,
    business_id: str,
    razorpay_payment_id: str = None,
    razorpay_payment_link_id: str = None,
    razorpay_payment_link_reference_id: str = None,
    razorpay_payment_link_status: str = None,
    razorpay_signature: str = None,
    db: Session = Depends(get_db),
):
    """
    Legacy callback for Payment Links (kept for backward compatibility).
    New flow uses Checkout Orders which verify via /checkout/verify.
    """
    _ensure_razorpay()

    if not all(
        [
            razorpay_payment_id,
            razorpay_payment_link_id,
            razorpay_payment_link_status,
            razorpay_signature,
        ]
    ):
        return HTMLResponse(content=FAILED_HTML, status_code=400)

    try:
        verify_payload = {
            "payment_link_id": razorpay_payment_link_id,
            "payment_link_reference_id": razorpay_payment_link_reference_id or "",
            "payment_link_status": razorpay_payment_link_status,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }
        razorpay_client.utility.verify_payment_link_signature(verify_payload)
    except razorpay.errors.SignatureVerificationError:
        return HTMLResponse(content=FAILED_HTML, status_code=400)

    if razorpay_payment_link_status == "paid":
        business = db.query(Business).filter(Business.id == business_id).first()
        if business:
            _mark_business_pro(business, db)
            return HTMLResponse(content=SUCCESS_HTML, status_code=200)

    return HTMLResponse(content=FAILED_HTML, status_code=400)


@router.get("/verify-order/{business_id}")
def verify_order_status(
    business_id: str,
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Allows the frontend to verify an order's payment status directly with Razorpay.
    This is a backup verification path — if the checkout page's JS verification
    fails (e.g. browser closed), the app can poll this endpoint.
    """
    _ensure_razorpay()

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Already PRO — no need to check
    if business.subscription_type == SubType.PRO:
        return {"status": "already_pro", "is_pro": True}

    try:
        # Fetch order from Razorpay to check if it's been paid
        order = razorpay_client.order.fetch(order_id)
        if order.get("status") == "paid":
            # Fetch payments for this order to verify
            payments = razorpay_client.order.payments(order_id)
            paid_payments = [
                p for p in (payments.get("items") or [])
                if p.get("status") == "captured"
            ]
            if paid_payments:
                _mark_business_pro(business, db)
                return {"status": "paid", "is_pro": True}

        return {"status": order.get("status", "unknown"), "is_pro": False}

    except Exception as e:
        logger.error("Order verification error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Could not verify order status: {e}",
        )


@router.get("/status/{business_id}")
def get_subscription_status(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Polled by the Flet app while the system browser handles payment."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    return {
        "subscription_type": business.subscription_type.value,
        "is_pro": business.subscription_type == SubType.PRO,
    }

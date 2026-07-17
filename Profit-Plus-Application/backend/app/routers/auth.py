import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    SendOtpRequest,
    SignupRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse
)
from app.utils.email_service import send_otp_email
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def is_incomplete_signup_user(user: User) -> bool:
    return (
        user
        and not user.is_verified
        and not user.password
        and not user.name
        and not user.phone
    )


# ── Send OTP ────────────────────────────────────────────────────────

@router.post("/send-otp")
def send_otp(request: SendOtpRequest, db: Session = Depends(get_db)):
    """
    Sends OTP to email. Used for both signup and login verification.
    """
    otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)

    existing = db.query(User).filter(User.email == request.email).first()

    if request.purpose == "reset_password" and (
        not existing or not existing.is_verified
    ):
        return {
            "message": "If that email is registered, a reset code has been sent."
        }

    if existing and existing.is_verified and request.purpose == "signup":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please log in instead."
        )

    if request.purpose == "signup" and request.phone:
        phone_owner = db.query(User).filter(User.phone == request.phone).first()
        if phone_owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    created_placeholder = False
    if existing:
        existing.email_otp = otp
        existing.email_otp_expiry = otp_expiry
        user_name = existing.name or "there"
    else:
        existing = User(
            id=uuid.uuid4(),
            email=request.email,
            email_otp=otp,
            email_otp_expiry=otp_expiry,
            is_verified=False
        )
        db.add(existing)
        created_placeholder = True
        user_name = "there"

    db.commit()

    # Send actual email
    email_sent = send_otp_email(request.email, otp, user_name)

    if not email_sent:
        print(f"\n\n==========================================\nOTP FOR {request.email}: {otp}\n==========================================\n\n", flush=True)
        return {"message": f"Render blocked email. Your OTP is: {otp}"}

    return {"message": "OTP sent to your email successfully"}


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset request"
        )

    if not user.email_otp or user.email_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    if (
        not user.email_otp_expiry
        or datetime.now(timezone.utc).replace(tzinfo=None) > user.email_otp_expiry
    ):
        user.email_otp = None
        user.email_otp_expiry = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new one"
        )

    user.password = hash_password(request.new_password)
    user.email_otp = None
    user.email_otp_expiry = None
    db.commit()

    return {"message": "Password reset successfully"}


# ── Signup ──────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Complete signup with name, email, password + OTP verification.
    """
    existing = db.query(User).filter(User.email == request.email).first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please request an OTP first"
        )

    # Verify OTP
    if existing.email_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if datetime.now(timezone.utc).replace(tzinfo=None) > existing.email_otp_expiry:
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one")

    if request.phone:
        phone_owner = db.query(User).filter(User.phone == request.phone, User.id != existing.id).first()
        if phone_owner:
            if is_incomplete_signup_user(existing):
                db.delete(existing)
                db.commit()
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Update user
    existing.name = request.name
    existing.phone = request.phone
    existing.password = hash_password(request.password)
    existing.is_verified = True
    existing.is_email_verified = True
    existing.email_otp = None
    existing.email_otp_expiry = None

    if not existing.referral_code:
        existing.referral_code = str(uuid.uuid4())[:8].upper()

    db.commit()
    db.refresh(existing)

    access_token = create_access_token(data={"sub": str(existing.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(existing.id),
            name=existing.name,
            email=existing.email,
            is_verified=existing.is_verified,
            referral_code=existing.referral_code
        )
    )


# ── Login ───────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email + password. (Handles both standard users and admin)
    """
    if request.email == "vishal2wishall@gmail.com" and request.password == "ProfitPlus@123098":
        admin_user = db.query(User).filter(User.email == request.email).first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email=request.email,
                name="Administrator",
                is_verified=True,
                is_email_verified=True,
                password=hash_password(request.password),
                referral_code="ADMIN"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        access_token = create_access_token(data={"sub": str(admin_user.id), "role": "admin"})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id="admin",
                name=admin_user.name,
                email=admin_user.email,
                is_verified=True,
                referral_code="ADMIN"
            )
        )

    user = db.query(User).filter(User.email == request.email).first()

    if not user or not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if getattr(user, "is_locked", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been locked by the platform."
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_verified=user.is_verified,
            referral_code=user.referral_code
        )
    )


# ── Get Current User ──────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    user_id_str = "admin" if current_user.email == "vishal2wishall@gmail.com" else str(current_user.id)
    return UserResponse(
        id=user_id_str,
        name=current_user.name,
        email=current_user.email,
        is_verified=current_user.is_verified,
        referral_code=current_user.referral_code
    )

# ── Admin Overview ──────────────────────────────────────────────────

from app.models.business import Business, SubType

@router.get("/admin/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
        
    total_users = db.query(User).count()
    total_businesses = db.query(Business).count()
    
    total_subscriptions = db.query(Business).filter(
        Business.subscription_type.in_([SubType.PRO, SubType.PLUS])
    ).count()
    
    return {
        "total_users": total_users,
        "total_businesses": total_businesses,
        "total_subscriptions": total_subscriptions
    }


# ── Admin User Management ───────────────────────────────────────────

@router.get("/admin/users")
def admin_get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    result = []
    for u in users:
        result.append({
            "id": str(u.id),
            "name": u.name or "N/A",
            "email": u.email or "N/A",
            "phone": u.phone or "N/A",
            "joined_date": u.created_at.isoformat() if u.created_at else None,
            "is_locked": getattr(u, "is_locked", False)
        })
    return result

@router.post("/admin/users/{user_id}/toggle-lock")
def admin_toggle_user_lock(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    current_lock = getattr(user, "is_locked", False)
    user.is_locked = not current_lock
    db.commit()
    
    return {"message": "User lock toggled successfully", "is_locked": user.is_locked}

# ── Admin Business Management ───────────────────────────────────────

@router.get("/admin/businesses")
def admin_get_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    from sqlalchemy.orm import joinedload
    businesses = db.query(Business).options(joinedload(Business.owner)).order_by(Business.created_at.desc()).all()
    
    result = []
    for b in businesses:
        owner_name = b.owner.name if b.owner else "Unknown"
        result.append({
            "id": str(b.id),
            "business_name": b.business_name or "N/A",
            "owner_name": owner_name,
            "email": b.email or "N/A",
            "phone": b.phone or "N/A",
            "subscription_type": b.subscription_type.value if b.subscription_type else "FREE",
            "created_date": b.created_at.isoformat() if b.created_at else None
        })
    return result

# ── Admin Revenue Analysis ──────────────────────────────────────────

from sqlalchemy import extract
@router.get("/admin/revenue")
def admin_get_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    pro_count = db.query(Business).filter(Business.subscription_type == SubType.PRO).count()
    
    import json
    import os
    pricing_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "pricing.json")
    PRO_PRICE = 499
    if os.path.exists(pricing_file):
        with open(pricing_file, "r") as f:
            PRO_PRICE = json.load(f).get("PRO", 499)
    
    total_revenue = pro_count * PRO_PRICE
    
    today = datetime.now(timezone.utc).date()
    chart_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_name = month_date.strftime("%b")
        val = max(100, int((total_revenue / 6) * (1 + (i % 3) * 0.2))) if total_revenue > 0 else 0
        chart_data.append({"month": month_name, "revenue": val})
        
    transactions = []
    recent_txns = db.query(Business).filter(Business.subscription_type == SubType.PRO).order_by(Business.updated_at.desc().nullslast()).limit(20).all()
    
    for b in recent_txns:
        date_str = (b.updated_at or b.created_at).isoformat()
        transactions.append({
            "id": f"TXN-{str(b.id)[:8].upper()}",
            "business_name": b.business_name or "Unknown",
            "plan": "PRO",
            "amount": PRO_PRICE,
            "date": date_str,
            "status": "SUCCESS"
        })
        
    return {
        "total_revenue": total_revenue,
        "chart_data": chart_data,
        "transactions": transactions
    }

# ── Admin Subscription Management ───────────────────────────────────

@router.get("/admin/subscriptions")
def admin_get_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    from sqlalchemy.orm import joinedload
    subs = db.query(Business).filter(Business.subscription_type == SubType.PRO).options(joinedload(Business.owner)).all()
    
    result = []
    for b in subs:
        result.append({
            "business_id": str(b.id),
            "business_name": b.business_name or "Unknown",
            "owner_name": b.owner.name if b.owner else "Unknown",
            "plan": b.subscription_type.value,
            "expiry": b.subscription_expiry.isoformat() if getattr(b, "subscription_expiry", None) else "N/A"
        })
    return result

@router.post("/admin/subscriptions/{business_id}/cancel")
def admin_cancel_subscription(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    business.subscription_type = SubType.FREE
    business.subscription_expiry = None
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}

from pydantic import BaseModel
class PricingRequest(BaseModel):
    plan: str
    price: int

@router.post("/admin/pricing")
def admin_update_pricing(
    request: PricingRequest,
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "vishal2wishall@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    import json
    import os
    pricing_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "pricing.json")
    
    pricing = {"PRO": 499}
    if os.path.exists(pricing_file):
        with open(pricing_file, "r") as f:
            pricing = json.load(f)
            
    pricing[request.plan.upper()] = request.price
    
    with open(pricing_file, "w") as f:
        json.dump(pricing, f)
        
    return {"message": "Pricing updated successfully", "plan": request.plan, "price": request.price}

@router.get("/pricing")
def get_pricing():
    import json
    import os
    pricing_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "pricing.json")
    if os.path.exists(pricing_file):
        with open(pricing_file, "r") as f:
            return json.load(f)
    return {"PRO": 499}


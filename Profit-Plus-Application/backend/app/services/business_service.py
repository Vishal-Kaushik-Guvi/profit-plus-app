from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.business import Business, SubType
from app.models.user import User
from app.schemas.business import BusinessCreateRequest, BusinessUpdateRequest
from pathlib import Path
import base64
import binascii
import uuid
from datetime import datetime, timezone

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "business_logos"
ALLOWED_LOGO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_LOGO_SIZE = 2 * 1024 * 1024


def save_business_logo(request, business_id: uuid.UUID) -> str | None:
    if not getattr(request, "logo_data", None):
        return None

    if not getattr(request, "logo_filename", None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logo filename is required"
        )

    extension = Path(request.logo_filename).suffix.lower()
    if extension not in ALLOWED_LOGO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logo must be a JPG, PNG, or WEBP image"
        )

    try:
        logo_bytes = base64.b64decode(request.logo_data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid logo file"
        )

    if len(logo_bytes) > MAX_LOGO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logo file must be 2MB or smaller"
        )

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{business_id}{extension}"
    logo_path = UPLOAD_ROOT / filename
    logo_path.write_bytes(logo_bytes)

    return f"/uploads/business_logos/{filename}"

def create_business(
    request: BusinessCreateRequest,
    current_user: User,
    db: Session
) -> Business:
    """
    Creates a new business for the logged in user.
    Like @Service method in Spring Boot.
    """

    # Check if user already has a business with same name
    existing = db.query(Business).filter(
        Business.owner_id == current_user.id,
        Business.business_name == request.business_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a business with this name"
        )

    # Check referral code if provided
    referred_by_user_id = None
    if request.referred_by_code:
        referrer = db.query(User).filter(
            User.referral_code == request.referred_by_code
        ).first()
        if referrer:
            referred_by_user_id = referrer.id

    business_id = uuid.uuid4()
    logo_url = save_business_logo(request, business_id)

    # Create new business
    business = Business(
        id=business_id,
        owner_id=current_user.id,
        business_name=request.business_name,
        logo_url=logo_url,
        phone=request.phone,
        email=request.email,
        address=request.address,
        city=request.city,
        pincode=request.pincode,
        state=request.state,
        country=request.country,
        gst=request.gst,
        bank_name=request.bank_name,
        account_number=request.account_number,
        ifsc_code=request.ifsc_code,
        branch_name=request.branch_name,
        referred_by_code=request.referred_by_code,
        referred_by_user_id=referred_by_user_id,
        subscription_type=SubType.FREE  # always starts FREE
    )

    db.add(business)
    db.commit()
    db.refresh(business)

    return business


def _check_subscription_expiry(business: Business, db: Session):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    # 1. Check if an active subscription has expired
    if business.subscription_type != SubType.FREE and business.subscription_expiry:
        if now > business.subscription_expiry:
            # Downgrade to FREE, but KEEP the expiry date to track the grace period
            business.subscription_type = SubType.FREE
            db.commit()
            
    # 2. Check if grace period has expired for a FREE business (that was previously PRO)
    if business.subscription_type == SubType.FREE and business.subscription_expiry:
        from datetime import timedelta
        if now > business.subscription_expiry + timedelta(days=7):
            # Grace period is over! Delete products beyond the 25 limit.
            from app.models.product import Product
            from app.models.inventory import Inventory
            
            # Find all products ordered by creation date
            products = db.query(Product).filter(
                Product.business_id == business.id
            ).order_by(Product.created_at).all()
            
            # If they have more than 25 products, delete the newer ones
            if len(products) > 25:
                products_to_delete = products[25:]
                for p in products_to_delete:
                    # Delete inventory first (if cascade isn't working as expected)
                    db.query(Inventory).filter(Inventory.product_id == p.id).delete()
                    db.delete(p)
                
            # Clear the expiry date so we don't run this expensive check again
            business.subscription_expiry = None
            db.commit()

def get_my_businesses(current_user: User, db: Session, skip: int = 0, limit: int = 10):
    """Get all businesses owned by current user"""
    businesses = db.query(Business).filter(
        Business.owner_id == current_user.id
    ).order_by(Business.created_at).offset(skip).limit(limit).all()
    for b in businesses:
        _check_subscription_expiry(b, db)
    return businesses


def get_business_by_id(business_id: str, current_user: User, db: Session):
    """Get a single business — must belong to current user"""
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user.id
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    _check_subscription_expiry(business, db)
    return business


def update_business(
    business_id: str,
    request: BusinessUpdateRequest,
    current_user: User,
    db: Session
) -> Business:
    """Update business details"""
    business = get_business_by_id(business_id, current_user, db)

    update_data = request.model_dump(exclude_unset=True)

    if getattr(request, "logo_data", None) and getattr(request, "logo_filename", None):
        logo_url = save_business_logo(request, business.id)
        if logo_url:
            update_data["logo_url"] = logo_url

    update_data.pop("logo_data", None)
    update_data.pop("logo_filename", None)

    for field, value in update_data.items():
        setattr(business, field, value)

    db.commit()
    db.refresh(business)

    return business


def delete_business(business_id: str, current_user: User, db: Session):
    """Delete a business"""
    from sqlalchemy import text
    business = get_business_by_id(business_id, current_user, db)

    b_id = {"b_id": str(business.id)}
    
    # 1. Delete EMI Payments and EMIs (References Sales & Customers)
    db.execute(text("DELETE FROM emi_payments WHERE business_id = :b_id"), b_id)
    db.execute(text("DELETE FROM emis WHERE business_id = :b_id"), b_id)
    
    # 2. Delete Sale Items and Sales (References Customers & Products)
    db.execute(text("DELETE FROM sale_items WHERE sale_id IN (SELECT id FROM sales WHERE business_id = :b_id)"), b_id)
    db.execute(text("DELETE FROM sales WHERE business_id = :b_id"), b_id)
    
    # 3. Delete Purchase Items and Purchases (References Suppliers & Products)
    db.execute(text("DELETE FROM purchase_items WHERE purchase_id IN (SELECT id FROM purchases WHERE business_id = :b_id)"), b_id)
    db.execute(text("DELETE FROM purchases WHERE business_id = :b_id"), b_id)
    
    # 4. Delete Inventory (References Products)
    db.execute(text("DELETE FROM inventory WHERE business_id = :b_id"), b_id)
    
    # 5. Delete Products
    db.execute(text("DELETE FROM products WHERE business_id = :b_id"), b_id)
    
    # 6. Delete Customers and Suppliers
    db.execute(text("DELETE FROM customers WHERE business_id = :b_id"), b_id)
    db.execute(text("DELETE FROM suppliers WHERE business_id = :b_id"), b_id)
    
    # 7. Delete Referral Earnings
    db.execute(text("DELETE FROM referral_earnings WHERE referred_business_id = :b_id"), b_id)

    db.delete(business)
    db.commit()

    return {"message": "Business deleted successfully"}

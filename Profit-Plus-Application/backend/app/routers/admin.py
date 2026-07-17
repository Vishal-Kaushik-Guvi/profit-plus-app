from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.business import Business, SubType

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    # Only allow admin
    if getattr(current_user, "id", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
        
    total_users = db.query(User).count()
    total_businesses = db.query(Business).count()
    
    # Subscriptions are businesses with PRO or PLUS
    total_subscriptions = db.query(Business).filter(
        Business.subscription_type.in_([SubType.PRO, SubType.PLUS])
    ).count()
    
    return {
        "total_users": total_users,
        "total_businesses": total_businesses,
        "total_subscriptions": total_subscriptions
    }

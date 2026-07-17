from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.referral import ReferralEarning
from app.schemas.referral import ReferralCreateRequest
from app.models.user import User

def create_referral(request: ReferralCreateRequest, current_user: User, db: Session) -> ReferralEarning:
    new_referral = ReferralEarning(
        **request.model_dump(),
        referrer_user_id=current_user.id
    )
    db.add(new_referral)
    db.commit()
    db.refresh(new_referral)
    return new_referral

def get_referrals_by_user(current_user: User, db: Session):
    return db.query(ReferralEarning).filter(ReferralEarning.referrer_user_id == current_user.id).all()

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.referral import ReferralCreateRequest, ReferralResponse
from app.services import referral_service

router = APIRouter(prefix="/referrals", tags=["Referrals"])

@router.post("/", response_model=ReferralResponse)
def create_referral(
    request: ReferralCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return referral_service.create_referral(request, current_user, db)

@router.get("/my-referrals", response_model=List[ReferralResponse])
def get_my_referrals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return referral_service.get_referrals_by_user(current_user, db)

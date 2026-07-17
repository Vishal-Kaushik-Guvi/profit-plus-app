from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.emi import EmiCreateRequest, EmiResponse, EmiPaymentCreateRequest, EmiPaymentResponse
from app.services import emi_service

router = APIRouter(prefix="/emi", tags=["EMI"])

@router.post("/", response_model=EmiResponse)
def create_emi(
    request: EmiCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return emi_service.create_emi(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[EmiResponse])
def get_business_emis(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    return emi_service.get_emis_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{emi_id}", response_model=EmiResponse)
def get_emi(
    emi_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return emi_service.get_emi_by_id(emi_id, current_user, db)

@router.post("/payment", response_model=EmiPaymentResponse)
def create_emi_payment(
    request: EmiPaymentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return emi_service.create_emi_payment(request, current_user, db)

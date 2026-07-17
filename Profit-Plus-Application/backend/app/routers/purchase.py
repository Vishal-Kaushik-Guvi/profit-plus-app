from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.purchase import PurchaseCreateRequest, PurchaseResponse
from app.services import purchase_service

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("/", response_model=PurchaseResponse)
def create_purchase(
    request: PurchaseCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return purchase_service.create_purchase(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[PurchaseResponse])
def get_business_purchases(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    return purchase_service.get_purchases_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(
    purchase_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return purchase_service.get_purchase_by_id(purchase_id, current_user, db)

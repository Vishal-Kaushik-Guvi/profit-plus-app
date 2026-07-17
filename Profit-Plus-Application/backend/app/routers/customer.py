from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.customer import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse)
def create_customer(
    request: CustomerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return customer_service.create_customer(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[CustomerResponse])
def get_business_customers(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    return customer_service.get_customers_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return customer_service.get_customer_by_id(customer_id, current_user, db)

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return customer_service.update_customer(customer_id, request, current_user, db)

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return customer_service.delete_customer(customer_id, current_user, db)

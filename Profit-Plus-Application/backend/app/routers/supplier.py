from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.supplier import SupplierCreateRequest, SupplierUpdateRequest, SupplierResponse
from app.services import supplier_service

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("/", response_model=SupplierResponse)
def create_supplier(
    request: SupplierCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return supplier_service.create_supplier(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[SupplierResponse])
def get_business_suppliers(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    return supplier_service.get_suppliers_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return supplier_service.get_supplier_by_id(supplier_id, current_user, db)

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    request: SupplierUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return supplier_service.update_supplier(supplier_id, request, current_user, db)

@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return supplier_service.delete_supplier(supplier_id, current_user, db)

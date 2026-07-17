from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.inventory import (
    InventoryCreateRequest,
    InventoryUpdateRequest,
    InventoryResponse,
    InventoryWithProductResponse
)
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/", response_model=InventoryResponse)
def create_inventory(
    request: InventoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create inventory record for a product"""
    return inventory_service.create_inventory(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[InventoryWithProductResponse])
def get_business_inventory(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    """Get all inventory records for a business"""
    return inventory_service.get_inventory_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_product_inventory(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory details for a specific product"""
    return inventory_service.get_inventory_by_product(product_id, current_user, db)

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: str,
    request: InventoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inventory details"""
    return inventory_service.update_inventory(inventory_id, request, current_user, db)

@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an inventory record"""
    return inventory_service.delete_inventory(inventory_id, current_user, db)

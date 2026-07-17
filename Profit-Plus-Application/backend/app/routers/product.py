from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse
)
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=200)
def create_product(
    request: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product for a business"""
    return product_service.create_product(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[ProductResponse])
def get_business_products(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    """Get all products for a specific business"""
    return product_service.get_products_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single product by its ID"""
    return product_service.get_product_by_id(product_id, current_user, db)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    return product_service.update_product(product_id, request, current_user, db)

@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    return product_service.delete_product(product_id, current_user, db)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.business import (
    BusinessCreateRequest,
    BusinessUpdateRequest,
    BusinessResponse
)
from app.services import business_service
from typing import List

# In Java → @RestController @RequestMapping("/business")
router = APIRouter(prefix="/business", tags=["Business"])


@router.post("/register", response_model=BusinessResponse)
def register_business(
    request: BusinessCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔐 requires login
):
    """
    Register a new business.
    Requires JWT token in header.
    In Java → @PostMapping("/register") @PreAuthorize("isAuthenticated()")
    """
    return business_service.create_business(request, current_user, db)


@router.get("/my-businesses", response_model=List[BusinessResponse])
def get_my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    """Get all businesses of logged in user"""
    return business_service.get_my_businesses(current_user, db, skip=skip, limit=limit)


@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single business by ID"""
    return business_service.get_business_by_id(business_id, current_user, db)


@router.put("/{business_id}", response_model=BusinessResponse)
def update_business(
    business_id: str,
    request: BusinessUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update business details"""
    return business_service.update_business(business_id, request, current_user, db)


@router.delete("/{business_id}")
def delete_business(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a business"""
    return business_service.delete_business(business_id, current_user, db)
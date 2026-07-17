from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreateRequest, SupplierUpdateRequest
from app.models.user import User

def create_supplier(request: SupplierCreateRequest, current_user: User, db: Session) -> Supplier:
    new_supplier = Supplier(**request.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier

def get_supplier_by_id(supplier_id: str, current_user: User, db: Session) -> Supplier:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier

def get_suppliers_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    return db.query(Supplier).filter(Supplier.business_id == business_id).offset(skip).limit(limit).all()

def update_supplier(supplier_id: str, request: SupplierUpdateRequest, current_user: User, db: Session) -> Supplier:
    supplier = get_supplier_by_id(supplier_id, current_user, db)
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)
        
    db.commit()
    db.refresh(supplier)
    return supplier

def delete_supplier(supplier_id: str, current_user: User, db: Session):
    supplier = get_supplier_by_id(supplier_id, current_user, db)
    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}

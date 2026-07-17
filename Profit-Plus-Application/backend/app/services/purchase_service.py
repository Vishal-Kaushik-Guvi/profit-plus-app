from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.purchase import Purchase, PurchaseItem
from app.schemas.purchase import PurchaseCreateRequest
from app.models.user import User

def create_purchase(request: PurchaseCreateRequest, current_user: User, db: Session) -> Purchase:
    purchase_data = request.model_dump(exclude={"items"})
    new_purchase = Purchase(**purchase_data)
    db.add(new_purchase)
    db.flush()
    
    for item_in in request.items:
        purchase_item = PurchaseItem(**item_in.model_dump(), purchase_id=new_purchase.id)
        db.add(purchase_item)
        
    db.commit()
    db.refresh(new_purchase)
    return new_purchase

def get_purchase_by_id(purchase_id: str, current_user: User, db: Session) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    return purchase

def get_purchases_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    from sqlalchemy.orm import joinedload
    return db.query(Purchase).options(joinedload(Purchase.items)).filter(Purchase.business_id == business_id).offset(skip).limit(limit).all()

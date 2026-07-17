from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.customer import Customer
from app.schemas.customer import CustomerCreateRequest, CustomerUpdateRequest
from app.models.user import User

def create_customer(request: CustomerCreateRequest, current_user: User, db: Session) -> Customer:
    new_customer = Customer(**request.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

def get_customer_by_id(customer_id: str, current_user: User, db: Session) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

def get_customers_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    return db.query(Customer).filter(Customer.business_id == business_id).offset(skip).limit(limit).all()

def update_customer(customer_id: str, request: CustomerUpdateRequest, current_user: User, db: Session) -> Customer:
    customer = get_customer_by_id(customer_id, current_user, db)
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
        
    db.commit()
    db.refresh(customer)
    return customer

def delete_customer(customer_id: str, current_user: User, db: Session):
    customer = get_customer_by_id(customer_id, current_user, db)
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

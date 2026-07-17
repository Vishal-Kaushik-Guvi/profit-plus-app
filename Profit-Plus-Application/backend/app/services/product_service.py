from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest
from app.models.user import User
from app.models.business import Business, SubType
import uuid

def create_product(request: ProductCreateRequest, current_user: User, db: Session) -> Product:
    business = db.query(Business).filter(Business.id == request.business_id).first()
    if business and business.subscription_type != SubType.PRO:
        product_count = db.query(Product).filter(Product.business_id == request.business_id).count()
        if product_count >= 25:
            raise HTTPException(status_code=403, detail="Free plan allows up to 25 products. Please upgrade to Pro.")

    new_product = Product(
        **request.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_product)
    db.flush()
    db.add(Inventory(
        business_id=new_product.business_id,
        product_id=new_product.id,
    ))
    db.commit()
    db.refresh(new_product)
    return new_product

def get_product_by_id(product_id: str, current_user: User, db: Session) -> Product:
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.owner_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

def get_products_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    products = db.query(Product).filter(
        Product.business_id == business_id,
        Product.owner_id == current_user.id
    ).order_by(Product.created_at).offset(skip).limit(limit).all()
    
    business = db.query(Business).filter(Business.id == business_id).first()
    
    # Mark products as inaccessible if they are on FREE tier and exceed 25 limit
    for i, product in enumerate(products):
        if business and business.subscription_type == SubType.FREE:
            # Pydantic will serialize this temporary attribute
            product.is_accessible = i < 25
        else:
            product.is_accessible = True
            
    return products

def update_product(product_id: str, request: ProductUpdateRequest, current_user: User, db: Session) -> Product:
    product = get_product_by_id(product_id, current_user, db)
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

def delete_product(product_id: str, current_user: User, db: Session):
    product = get_product_by_id(product_id, current_user, db)
    db.query(Inventory).filter(Inventory.product_id == product.id).delete()
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

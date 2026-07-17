from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreateRequest, InventoryUpdateRequest
from app.models.user import User
from app.schemas.product import ProductCreateRequest

def create_inventory(request: InventoryCreateRequest, current_user: User, db: Session) -> Inventory:
    # A validation could be added to ensure the product belongs to the user
    new_inv = Inventory(**request.model_dump())
    db.add(new_inv)
    db.commit()
    db.refresh(new_inv)
    return new_inv


def create_product(request: ProductCreateRequest, current_user: User, db: Session) -> Product:
    new_product = Product(
        **request.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_product)
    db.flush()  # get new_product.id before commit

    # Auto-create empty inventory record
    new_inventory = Inventory(
        business_id=new_product.business_id,
        product_id=new_product.id,
    )
    db.add(new_inventory)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_inventory_by_id(inventory_id: str, current_user: User, db: Session) -> Inventory:
    # Check by joining with Business to ensure ownership, but here we assume user has access 
    # to this business's inventory. For simplicity, direct query.
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inv

def get_inventory_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    return db.query(Inventory).options(joinedload(Inventory.product)).filter(Inventory.business_id == business_id).offset(skip).limit(limit).all()

def get_inventory_by_product(product_id: str, current_user: User, db: Session):
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def update_inventory(inventory_id: str, request: InventoryUpdateRequest, current_user: User, db: Session) -> Inventory:
    inv = get_inventory_by_id(inventory_id, current_user, db)

    update_data = request.model_dump(exclude_unset=True)

    # ✅ ADD to stock instead of replacing
    if "stock_quantity" in update_data:
        inv.stock_quantity = (inv.stock_quantity or 0) + \
            update_data.pop("stock_quantity")

    for key, value in update_data.items():
        setattr(inv, key, value)

    db.commit()
    db.refresh(inv)
    return inv

def delete_inventory(inventory_id: str, current_user: User, db: Session):
    inv = get_inventory_by_id(inventory_id, current_user, db)
    db.delete(inv)
    db.commit()
    return {"message": "Inventory deleted successfully"}
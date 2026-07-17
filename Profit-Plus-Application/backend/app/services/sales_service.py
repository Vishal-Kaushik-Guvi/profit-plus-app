from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.sales import Sales, SaleItem
from app.models.customer import Customer
from app.models.emipayment import Emi, EmiStatus
from app.models.inventory import Inventory
from app.schemas.sales import SalesCreateRequest
from app.models.user import User
from datetime import datetime, timezone

def create_sale(request: SalesCreateRequest, current_user: User, db: Session) -> Sales:
    sale_data = request.model_dump(exclude={"items"})
    
    # 1. Handle Customer
    customer = None
    if request.buyer_phone and request.buyer_name:
        customer = db.query(Customer).filter(
            Customer.phone == request.buyer_phone,
            Customer.business_id == request.business_id
        ).first()
        if not customer:
            customer = Customer(
                business_id=request.business_id,
                name=request.buyer_name,
                phone=request.buyer_phone,
                address=request.buyer_address,
                gstin=request.buyer_gstin,
                aadhaar_number=request.aadhaar_number
            )
            db.add(customer)
            db.flush()
        else:
            customer.name = request.buyer_name
            if request.buyer_address: customer.address = request.buyer_address
            if request.buyer_gstin: customer.gstin = request.buyer_gstin
            if request.aadhaar_number: customer.aadhaar_number = request.aadhaar_number
            db.flush()
            
        sale_data["customer_id"] = customer.id
        
        # update stats
        customer.total_orders += 1
        customer.total_spent += request.total_amount
    
    # 2. Create Sale
    new_sale = Sales(**sale_data)
    # Generate Transaction ID / Invoice No
    import uuid
    new_sale.invoice_no = f"TRX-{str(uuid.uuid4())[:8].upper()}"
    new_sale.transaction_date = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
    new_sale.transaction_time = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%H:%M:%S")
    
    db.add(new_sale)
    db.flush()
    
    total_profit = 0.0
    # 3. Create Items and Deduct Stock
    product_ids = [item.product_id for item in request.items if item.product_id]
    inventories = db.query(Inventory).filter(
        Inventory.business_id == request.business_id,
        Inventory.product_id.in_(product_ids)
    ).all() if product_ids else []
    inventory_map = {inv.product_id: inv for inv in inventories}

    for item_in in request.items:
        sale_item = SaleItem(**item_in.model_dump(), sale_id=new_sale.id)
        
        # Deduct from inventory and calculate profit
        if item_in.product_id:
            inventory = inventory_map.get(item_in.product_id)
            if inventory:
                current_stock = inventory.stock_quantity or 0
                inventory.stock_quantity = current_stock - item_in.quantity
                
                # Calculate Profit
                sale_item.purchase_price = inventory.purchase_price or 0.0
                sale_item.profit = (sale_item.unit_price - sale_item.purchase_price) * sale_item.quantity
        
        total_profit += (sale_item.profit or 0.0)
        db.add(sale_item)
        
    new_sale.total_profit = total_profit
        
    # 4. Create EMI
    if request.is_emi:
        if not customer:
            raise HTTPException(status_code=400, detail="Customer Name and Phone are required for EMI.")
            
        principal = request.total_amount - (request.emi_down_payment or 0)
        interest_rate = request.emi_interest_rate or 0
        months = request.emi_months or 1
        
        # Simple interest for EMI
        total_interest = principal * (interest_rate / 100.0) * months
        total_payable = principal + total_interest
        emi_amount = total_payable / months if months > 0 else 0
        # Calculate next due date (approx 1 month)
        from datetime import datetime as dt, timedelta
        next_due_date = (dt.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

        emi = Emi(
            sale_id=new_sale.id,
            customer_id=customer.id,
            business_id=request.business_id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            customer_address=customer.address,
            aadhaar_number=request.aadhaar_number,
            total_amount=request.total_amount,
            down_payment=request.emi_down_payment or 0,
            principal=principal,
            monthly_interest=interest_rate,
            total_interest=total_interest,
            total_payable=total_payable,
            emi_amount=emi_amount,
            total_months=months,
            remaining_balance=total_payable,
            next_billing_amount=emi_amount,
            start_date=new_sale.transaction_date,
            next_due_date=next_due_date,
            status=EmiStatus.ACTIVE
        )
        db.add(emi)
        
    db.commit()
    db.refresh(new_sale)
    return new_sale

def get_sale_by_id(sale_id: str, current_user: User, db: Session) -> Sales:
    sale = db.query(Sales).options(joinedload(Sales.items)).filter(Sales.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale

def get_sales_by_business(business_id: str, current_user: User, db: Session, skip: int = 0, limit: int = 10):
    return db.query(Sales).options(joinedload(Sales.items), joinedload(Sales.customer)).filter(Sales.business_id == business_id).order_by(Sales.created_at.desc()).offset(skip).limit(limit).all()

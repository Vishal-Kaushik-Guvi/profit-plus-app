from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime, date

class InventoryBase(BaseModel):
    stock_quantity: Optional[float] = 0.0
    minimum_stock_alert: Optional[float] = 0.0
    sold_quantity: Optional[float] = 0.0
    returned_quantity: Optional[float] = 0.0
    damaged_quantity: Optional[float] = 0.0

    purchase_price: Optional[float] = 0.0
    purchase_taxable_amount: Optional[float] = 0.0
    purchase_tax_amount: Optional[float] = 0.0

    selling_price: Optional[float] = 0.0
    selling_taxable_amount: Optional[float] = 0.0
    selling_tax_amount: Optional[float] = 0.0

    discount_price: Optional[float] = 0.0
    tax_percentage: Optional[float] = 0.0

    unit: Optional[str] = None
    last_restock_date: Optional[str] = None
    last_restock_time: Optional[str] = None
    
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    warranty_months: Optional[int] = None
    serial_number: Optional[str] = None
    product_size: Optional[str] = None
    product_color: Optional[str] = None

class InventoryCreateRequest(InventoryBase):
    business_id: UUID4
    product_id: UUID4

class InventoryUpdateRequest(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    id: UUID4
    business_id: UUID4
    product_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        

class ProductInfo(BaseModel):
    id: UUID4
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryWithProductResponse(InventoryResponse):
    product: Optional[ProductInfo] = None

    class Config:
        from_attributes = True

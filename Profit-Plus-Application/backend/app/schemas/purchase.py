from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class PurchaseItemBase(BaseModel):
    product_id: Optional[UUID4] = None
    name: str
    hsn_code: Optional[str] = None
    tax_percentage: Optional[float] = 0.0
    taxable_amount: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    total_amount: float
    quantity: float
    unit: Optional[str] = None

class PurchaseBase(BaseModel):
    supplier_id: Optional[UUID4] = None
    supplier_name: Optional[str] = None
    supplier_gstin: Optional[str] = None
    invoice_no: Optional[str] = None
    place_of_supply: Optional[str] = None

    total_taxable_amount: Optional[float] = 0.0
    total_tax_amount: Optional[float] = 0.0
    total_amount: float
    
    status: Optional[str] = "Pending"
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None

class PurchaseCreateRequest(PurchaseBase):
    business_id: UUID4
    items: List[PurchaseItemBase]

class PurchaseItemResponse(PurchaseItemBase):
    id: UUID4
    purchase_id: UUID4

    class Config:
        from_attributes = True

class PurchaseResponse(PurchaseBase):
    id: UUID4
    business_id: UUID4
    created_at: datetime
    items: List[PurchaseItemResponse]

    class Config:
        from_attributes = True

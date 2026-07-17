from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class SaleItemBase(BaseModel):
    product_id: Optional[UUID4] = None
    name: str
    brand: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_percentage: Optional[float] = 0.0
    taxable_amount: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    purchase_price: Optional[float] = 0.0
    total_price: float
    profit: Optional[float] = 0.0
    color: Optional[str] = None
    size: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None

class SalesBase(BaseModel):
    customer_id: Optional[UUID4] = None
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    buyer_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None

    subtotal: float
    discount_percentage: Optional[float] = 0.0
    total_amount: float
    total_profit: Optional[float] = 0.0
    amount_in_words: Optional[str] = None

    invoice_no: Optional[str] = None
    is_emi: Optional[bool] = False
    
    emi_down_payment: Optional[float] = None
    emi_interest_rate: Optional[float] = None
    emi_months: Optional[int] = None
    emi_total_interest: Optional[float] = None
    emi_day: Optional[int] = None

    send_sms: Optional[bool] = False
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None

class SalesCreateRequest(SalesBase):
    business_id: UUID4
    items: List[SaleItemBase]

class SaleItemResponse(SaleItemBase):
    id: UUID4
    sale_id: UUID4

    class Config:
        from_attributes = True

class SalesResponse(SalesBase):
    id: UUID4
    business_id: UUID4
    created_at: datetime
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True

from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    gstin: Optional[str] = None

class CustomerCreateRequest(CustomerBase):
    business_id: UUID4

class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    gstin: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: UUID4
    business_id: UUID4
    total_orders: int
    total_spent: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

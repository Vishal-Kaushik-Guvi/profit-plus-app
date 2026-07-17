from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class SupplierBase(BaseModel):
    supplier_name: str
    contact: Optional[str] = None
    address: Optional[str] = None

class SupplierCreateRequest(SupplierBase):
    business_id: UUID4

class SupplierUpdateRequest(BaseModel):
    supplier_name: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None

class SupplierResponse(SupplierBase):
    id: UUID4
    business_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

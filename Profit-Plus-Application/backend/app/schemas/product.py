from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    product_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_percentage: Optional[float] = 0.0
    color: Optional[str] = None
    size: Optional[str] = None
    business_type: Optional[str] = None

class ProductCreateRequest(ProductBase):
    business_id: UUID4

class ProductUpdateRequest(BaseModel):
    product_name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_percentage: Optional[float] = None
    color: Optional[str] = None
    size: Optional[str] = None
    business_type: Optional[str] = None

class ProductResponse(ProductBase):
    id: UUID4
    business_id: UUID4
    owner_id: UUID4
    is_accessible: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

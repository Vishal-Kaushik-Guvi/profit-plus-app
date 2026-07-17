from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID

class SubType(str, Enum):
    PRO = "PRO"
    PLUS = "PLUS"
    FREE = "FREE"
    NONE = "NONE"

# ── Request Schemas ─────────────────────────────────────────────────

class BusinessCreateRequest(BaseModel):
    """What client sends to register a new business"""
    business_name: str
    logo_filename: Optional[str] = None
    logo_data: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    # GST
    gst: Optional[str] = None

    # Bank Details                        
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None

    # Referral
    referred_by_code: Optional[str] = None


class BusinessUpdateRequest(BaseModel):
    """What client sends to update business info"""
    business_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    gst: Optional[str] = None
    logo_url: Optional[str] = None
    logo_filename: Optional[str] = None
    logo_data: Optional[str] = None

    # Bank Details
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None

# ── Response Schemas ────────────────────────────────────────────────

class BusinessResponse(BaseModel):
    """What server sends back"""
    id: UUID
    business_name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    pincode: Optional[str]
    state: Optional[str]
    country: Optional[str]
    gst: Optional[str]
    gst_verified: bool
    subscription_type: str
    subscription_expiry: Optional[datetime]
    subscription_days_remaining: int = 0
    grace_period_days_remaining: int = 0
    logo_url: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    ifsc_code: Optional[str]
    branch_name: Optional[str]
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

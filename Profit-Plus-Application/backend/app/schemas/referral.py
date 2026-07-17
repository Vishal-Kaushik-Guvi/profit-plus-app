from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class ReferralBase(BaseModel):
    referred_business_id: UUID4
    referred_business_name: Optional[str] = None
    subscription_type: Optional[str] = None
    subscription_amount: Optional[float] = 0.0
    commission_percentage: Optional[float] = 0.0
    commission_earned: Optional[float] = 0.0
    purchase_date: Optional[str] = None
    purchase_time: Optional[str] = None

class ReferralCreateRequest(ReferralBase):
    pass # referrer is current user

class ReferralResponse(ReferralBase):
    id: UUID4
    referrer_user_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

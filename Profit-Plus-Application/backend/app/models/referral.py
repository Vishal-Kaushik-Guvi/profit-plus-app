import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.core.database import Base

class ReferralEarning(Base):
    __tablename__ = "referral_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    referrer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    referred_business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Info
    referred_business_name = Column(String(100), nullable=True)
    subscription_type = Column(String(20), nullable=True)
    subscription_amount = Column(Float, default=0.0)
    commission_percentage = Column(Float, default=0.0)
    commission_earned = Column(Float, default=0.0)

    # Audit
    purchase_date = Column(String(20), nullable=True)
    purchase_time = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
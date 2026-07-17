import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

# Enum — same as your Java SubType enum
class SubType(str, enum.Enum):
    PRO = "PRO"
    PLUS = "PLUS"
    FREE = "FREE"
    NONE = "NONE"

class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Basic Info
    business_name = Column(String(100), nullable=False)
    logo_url = Column(String(255), nullable=True)
    phone = Column(String(15), nullable=True, index=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(50), nullable=True)
    pincode = Column(String(10), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)

    # GST
    gst = Column(String(20), nullable=True, unique=True)
    gst_verified = Column(Boolean, default=False)

    # Subscription
    subscription_type = Column(Enum(SubType), default=SubType.FREE)
    subscription_expiry = Column(DateTime, nullable=True)

    # Referral
    referred_by_code = Column(String(20), nullable=True)
    referred_by_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Bank Details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(30), nullable=True)
    ifsc_code = Column(String(15), nullable=True)
    branch_name = Column(String(100), nullable=True)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    owner = relationship("User", back_populates="businesses")
    customers = relationship("Customer", back_populates="business", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="business", cascade="all, delete-orphan")
    sales = relationship("Sales", back_populates="business", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="business", cascade="all, delete-orphan")

    @property
    def subscription_days_remaining(self) -> int:
        if self.subscription_type == SubType.FREE or not self.subscription_expiry:
            return 0
        delta = self.subscription_expiry - datetime.now(timezone.utc).replace(tzinfo=None)
        return max(0, delta.days)

    @property
    def grace_period_days_remaining(self) -> int:
        if self.subscription_type != SubType.FREE or not self.subscription_expiry:
            return 0
        delta = (self.subscription_expiry + __import__("datetime").timedelta(days=7)) - datetime.now(timezone.utc).replace(tzinfo=None)
        return max(0, delta.days)
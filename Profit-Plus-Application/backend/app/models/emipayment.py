import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

class EmiStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"

class Emi(Base):
    __tablename__ = "emis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True, unique=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Denormalized Customer Info (snapshot)
    customer_name = Column(String(100), nullable=True)
    customer_phone = Column(String(15), nullable=True, index=True)
    customer_address = Column(String(255), nullable=True)
    aadhaar_number = Column(String(20), nullable=True)

    # Financial Fields
    total_amount = Column(Float, default=0.0)       # Original sale total
    down_payment = Column(Float, default=0.0)       # Upfront payment
    principal = Column(Float, default=0.0)          # total - down_payment
    monthly_interest = Column(Float, default=0.0)   # % per month
    total_interest = Column(Float, default=0.0)     # principal × rate × months
    total_payable = Column(Float, default=0.0)      # principal + total_interest
    emi_amount = Column(Float, default=0.0)         # per installment
    amount_in_words = Column(String(255), nullable=True)

    # Repayment Tracking
    total_months = Column(Integer, default=0)
    months_completed = Column(Integer, default=0)
    amount_paid = Column(Float, default=0.0)
    remaining_balance = Column(Float, default=0.0)
    next_billing_amount = Column(Float, default=0.0)
    overdue_amount = Column(Float, default=0.0)

    # Dates
    start_date = Column(String(20), nullable=True)
    next_due_date = Column(String(20), nullable=True)
    emi_day = Column(Integer, nullable=True)  # 1-31

    # Status
    status = Column(Enum(EmiStatus), default=EmiStatus.ACTIVE)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    sale = relationship("Sales", back_populates="emi")
    payments = relationship("EmiPayment", back_populates="emi",
                            cascade="all, delete-orphan")


class EmiPayment(Base):
    __tablename__ = "emi_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    emi_id = Column(UUID(as_uuid=True), ForeignKey("emis.id"), nullable=False, index=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Payment Breakdown
    amount = Column(Float, default=0.0)
    principal_amount = Column(Float, default=0.0)
    interest_amount = Column(Float, default=0.0)
    balance_after = Column(Float, default=0.0)

    # Payment Info
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    installment_number = Column(Integer, nullable=False)
    date = Column(String(20), nullable=True)
    time = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)
    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    emi = relationship("Emi", back_populates="payments")
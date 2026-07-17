import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Basic Info
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False, index=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

    # KYC
    aadhaar_number = Column(String(20), nullable=True)
    pan_number = Column(String(15), nullable=True)
    gstin = Column(String(20), nullable=True)

    # Aggregated Stats
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    business = relationship("Business", back_populates="customers")
    sales = relationship("Sales", back_populates="customer")
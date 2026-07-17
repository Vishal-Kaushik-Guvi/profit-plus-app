import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    name = Column(String(100), nullable=True)
    phone = Column(String(15), nullable=True, index=True, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(255), nullable=True)  # optional since OTP based
    
    # OTP Auth
    otp = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    # Email verification
    email_otp = Column(String(6), nullable=True)
    email_otp_expiry = Column(DateTime, nullable=True)
    is_email_verified = Column(Boolean, default=False)

    # Referral
    referral_code = Column(String(20), nullable=True, unique=True)
    joined_referral_program = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    businesses = relationship("Business", back_populates="owner")
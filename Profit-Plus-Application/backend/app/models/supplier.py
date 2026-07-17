import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Info
    supplier_name = Column(String(100), nullable=False)
    contact = Column(String(15), nullable=True)
    address = Column(String(255), nullable=True)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    business = relationship("Business", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")
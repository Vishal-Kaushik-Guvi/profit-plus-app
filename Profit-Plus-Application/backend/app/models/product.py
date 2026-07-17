import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Basic Info
    product_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    image_url = Column(String(255), nullable=True)

    # GST / Tax
    hsn_code = Column(String(20), nullable=True)
    tax_percentage = Column(Float, default=0.0)

    # Default Variant
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)

    # Business Type
    business_type = Column(String(50), nullable=True)  # e.g. electronics, clothing, medical

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    business = relationship("Business", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
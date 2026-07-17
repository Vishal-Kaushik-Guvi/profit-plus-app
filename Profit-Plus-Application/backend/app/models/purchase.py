import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True, index=True)

    # Supplier Info (stored at time of purchase)
    supplier_name = Column(String(100), nullable=True)
    supplier_gstin = Column(String(20), nullable=True)
    invoice_no = Column(String(50), nullable=True)
    place_of_supply = Column(String(100), nullable=True)

    # Totals
    total_taxable_amount = Column(Float, default=0.0)
    total_tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)

    # Status
    status = Column(String(20), default="Pending")  # Matched, Pending

    # Audit
    transaction_date = Column(String(20), nullable=True)
    transaction_time = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    business = relationship("Business", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase",
                         cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)

    # Item details (snapshot at time of purchase)
    name = Column(String(150), nullable=False)
    hsn_code = Column(String(20), nullable=True)
    tax_percentage = Column(Float, default=0.0)
    taxable_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20), nullable=True)

    # Relationships
    purchase = relationship("Purchase", back_populates="items")
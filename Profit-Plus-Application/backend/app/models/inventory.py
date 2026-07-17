import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)

    # Stock
    stock_quantity = Column(Float, default=0.0)
    minimum_stock_alert = Column(Float, default=0.0)
    sold_quantity = Column(Float, default=0.0)
    returned_quantity = Column(Float, default=0.0)
    damaged_quantity = Column(Float, default=0.0)

    # Purchase Pricing (what you paid supplier)
    purchase_price = Column(Float, default=0.0)           # Total paid
    purchase_taxable_amount = Column(Float, default=0.0)  # Base cost (net)
    purchase_tax_amount = Column(Float, default=0.0)      # GST paid (ITC)

    # Selling Pricing (what you charge customer)
    selling_price = Column(Float, default=0.0)            # MRP
    selling_taxable_amount = Column(Float, default=0.0)   # Base price
    selling_tax_amount = Column(Float, default=0.0)       # GST to collect

    discount_price = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)

    # Unit
    unit = Column(String(20), nullable=True)  # pcs, kg, liter etc

    # Restock Tracking
    last_restock_date = Column(String(20), nullable=True)
    last_restock_time = Column(String(20), nullable=True)

    # Chemist specific
    expiry_date = Column(Date, nullable=True)
    batch_number = Column(String(50), nullable=True)

    # Electronics specific
    warranty_months = Column(Integer, nullable=True)

    # Mobile specific
    serial_number = Column(String(100), nullable=True)

    # Variant Support (Shoe, Cloth)
    product_size = Column(String(20), nullable=True)
    product_color = Column(String(30), nullable=True)

    # Audit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    product = relationship("Product", back_populates="inventory")
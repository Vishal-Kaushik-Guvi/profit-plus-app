import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Sales(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)

    # Buyer Info (snapshot at time of sale)
    buyer_name = Column(String(100), nullable=True)
    buyer_phone = Column(String(15), nullable=True, index=True)
    buyer_address = Column(String(255), nullable=True)
    aadhaar_number = Column(String(20), nullable=True)
    buyer_gstin = Column(String(20), nullable=True)
    place_of_supply = Column(String(100), nullable=True)

    # Totals
    subtotal = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    amount_in_words = Column(String(255), nullable=True)

    # Invoice
    invoice_no = Column(String(50), nullable=True, unique=True)

    # EMI flag
    is_emi = Column(Boolean, default=False)

    # EMI Details (only if is_emi = True)
    emi_down_payment = Column(Float, nullable=True)
    emi_interest_rate = Column(Float, nullable=True)
    emi_months = Column(Integer, nullable=True)
    emi_total_interest = Column(Float, nullable=True)
    emi_day = Column(Integer, nullable=True)  # day of month 1-31

    # SMS
    send_sms = Column(Boolean, default=False)

    # Audit
    transaction_date = Column(String(20), nullable=True)
    transaction_time = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    business = relationship("Business", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale",
                         cascade="all, delete-orphan")
    emi = relationship("Emi", back_populates="sale", uselist=False)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FKs
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)

    # Item snapshot at time of sale
    name = Column(String(150), nullable=False)
    brand = Column(String(100), nullable=True)
    hsn_code = Column(String(20), nullable=True)
    tax_percentage = Column(Float, default=0.0)
    taxable_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20), nullable=True)
    unit_price = Column(Float, default=0.0)
    purchase_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

    # Variant
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    model_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)

    # Relationships
    sale = relationship("Sales", back_populates="items")
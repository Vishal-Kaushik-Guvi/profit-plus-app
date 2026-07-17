from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EmiStatus(str, Enum):
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"

class EmiPaymentBase(BaseModel):
    amount: float
    principal_amount: Optional[float] = 0.0
    interest_amount: Optional[float] = 0.0
    balance_after: Optional[float] = 0.0
    payment_method: Optional[PaymentMethod] = PaymentMethod.CASH
    installment_number: int
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None

class EmiBase(BaseModel):
    total_amount: float
    down_payment: Optional[float] = 0.0
    principal: Optional[float] = 0.0
    monthly_interest: Optional[float] = 0.0
    total_interest: Optional[float] = 0.0
    total_payable: Optional[float] = 0.0
    emi_amount: float
    amount_in_words: Optional[str] = None
    total_months: int
    months_completed: Optional[int] = 0
    amount_paid: Optional[float] = 0.0
    remaining_balance: float
    next_billing_amount: float
    overdue_amount: Optional[float] = 0.0
    start_date: Optional[str] = None
    next_due_date: Optional[str] = None
    emi_day: Optional[int] = None
    status: Optional[EmiStatus] = EmiStatus.ACTIVE

class EmiCreateRequest(EmiBase):
    sale_id: UUID4
    customer_id: UUID4
    business_id: UUID4
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    aadhaar_number: Optional[str] = None

class EmiPaymentCreateRequest(EmiPaymentBase):
    emi_id: UUID4
    business_id: UUID4

class EmiPaymentResponse(EmiPaymentBase):
    id: UUID4
    emi_id: UUID4
    business_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class EmiResponse(EmiBase):
    id: UUID4
    sale_id: UUID4
    customer_id: UUID4
    business_id: UUID4
    created_at: datetime
    updated_at: datetime
    payments: List[EmiPaymentResponse] = []

    class Config:
        from_attributes = True

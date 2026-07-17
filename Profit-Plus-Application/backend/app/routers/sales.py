from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.sales import SalesCreateRequest, SalesResponse
from app.services import sales_service

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=SalesResponse)
def create_sale(
    request: SalesCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sales_service.create_sale(request, current_user, db)

@router.get("/business/{business_id}", response_model=List[SalesResponse])
def get_business_sales(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
,
    skip: int = 0, limit: int = 10):
    return sales_service.get_sales_by_business(business_id, current_user, db, skip=skip, limit=limit)

@router.get("/{sale_id}", response_model=SalesResponse)
def get_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sales_service.get_sale_by_id(sale_id, current_user, db)

@router.get("/{sale_id}/pdf")
def download_sale_pdf(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import FileResponse
    from app.utils.pdf_generator import generate_invoice_pdf
    from app.models.business import Business
    
    sale = sales_service.get_sale_by_id(sale_id, current_user, db)
    business = db.query(Business).filter(Business.id == sale.business_id).first()
    
    pdf_path = generate_invoice_pdf(sale, business)
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"Invoice_{sale.invoice_no}.pdf")

from pydantic import BaseModel
class EmailRequest(BaseModel):
    email: str

from fastapi import BackgroundTasks

@router.post("/{sale_id}/email")
def email_sale_pdf(
    sale_id: str,
    payload: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.utils.pdf_generator import generate_invoice_pdf
    from app.utils.email_service import send_bill_email
    from app.models.business import Business, SubType
    from fastapi import HTTPException
    
    sale = sales_service.get_sale_by_id(sale_id, current_user, db)
    business = db.query(Business).filter(Business.id == sale.business_id).first()
    
    if business and business.subscription_type != SubType.PRO:
        raise HTTPException(status_code=403, detail="Email feature requires Pro plan.")
        
    def generate_and_send():
        pdf_path = generate_invoice_pdf(sale, business)
        send_bill_email(payload.email, pdf_path, sale.invoice_no, sale.buyer_name or "Customer")

    background_tasks.add_task(generate_and_send)
        
    return {"message": "Email is being prepared and sent in the background"}

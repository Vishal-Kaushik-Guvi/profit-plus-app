from fpdf import FPDF
from app.models.sales import Sales
from app.models.business import Business
import os

def generate_invoice_pdf(sale: Sales, business: Business) -> str:
    pdf = FPDF()
    pdf.add_page()
    
    # Fonts
    pdf.set_font('helvetica', 'B', 16)
    
    # Business Header
    pdf.cell(0, 10, business.business_name.upper(), ln=True, align='C')
    pdf.set_font('helvetica', '', 10)
    if business.address:
        pdf.cell(0, 5, business.address, ln=True, align='C')
    if business.email or business.phone:
        pdf.cell(0, 5, f"Email: {business.email or ''} | Phone: {business.phone or ''}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Invoice Details
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "TAX INVOICE", ln=True, align='C')
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(100, 6, f"Invoice No: {sale.invoice_no or 'N/A'}")
    pdf.cell(90, 6, f"Date: {sale.transaction_date or ''} {sale.transaction_time or ''}", ln=True, align='R')
    
    # Customer Details
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 6, "Billed To:", ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 5, f"Name: {sale.buyer_name or 'Walk-in Customer'}", ln=True)
    if sale.buyer_phone: pdf.cell(0, 5, f"Phone: {sale.buyer_phone}", ln=True)
    if sale.buyer_address: pdf.cell(0, 5, f"Address: {sale.buyer_address}", ln=True)
    if sale.buyer_gstin: pdf.cell(0, 5, f"GSTIN: {sale.buyer_gstin}", ln=True)
    
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(10, 8, "#", 1, 0, 'C', True)
    pdf.cell(70, 8, "Item", 1, 0, 'L', True)
    pdf.cell(30, 8, "Qty", 1, 0, 'C', True)
    pdf.cell(40, 8, "Price", 1, 0, 'R', True)
    pdf.cell(40, 8, "Total", 1, 1, 'R', True)
    
    # Items
    pdf.set_font('helvetica', '', 10)
    for idx, item in enumerate(sale.items):
        pdf.cell(10, 8, str(idx+1), 1, 0, 'C')
        pdf.cell(70, 8, item.name, 1, 0, 'L')
        pdf.cell(30, 8, f"{item.quantity} {item.unit or ''}", 1, 0, 'C')
        pdf.cell(40, 8, f"{item.unit_price:,.2f}", 1, 0, 'R')
        pdf.cell(40, 8, f"{item.total_price:,.2f}", 1, 1, 'R')
        
    # Totals
    pdf.ln(5)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(150, 6, "Subtotal:", align='R')
    pdf.cell(40, 6, f"{sale.subtotal:,.2f}", ln=True, align='R')
    
    if sale.discount_percentage > 0:
        pdf.cell(150, 6, f"Discount ({sale.discount_percentage}%):", align='R')
        pdf.cell(40, 6, f"{(sale.subtotal * sale.discount_percentage / 100):,.2f}", ln=True, align='R')
        
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(150, 8, "Grand Total:", align='R')
    pdf.cell(40, 8, f"Rs. {sale.total_amount:,.2f}", ln=True, align='R')
    
    if sale.is_emi:
        pdf.ln(5)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 6, "EMI Details:", ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 5, f"Down Payment: Rs. {sale.emi_down_payment or 0:,.2f}", ln=True)
        pdf.cell(0, 5, f"Tenure: {sale.emi_months or 0} months @ {sale.emi_interest_rate or 0}%/mo", ln=True)
    
    pdf.ln(20)
    pdf.set_font('helvetica', 'I', 9)
    pdf.cell(0, 5, "Thank you for your business!", align='C')
    
    os.makedirs("generated_pdfs", exist_ok=True)
    filename = f"generated_pdfs/{sale.id}.pdf"
    pdf.output(filename)
    return filename

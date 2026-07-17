from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.emipayment import Emi, EmiPayment, EmiStatus
from app.models.inventory import Inventory
from app.models.sales import SaleItem, Sales
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard/{business_id}")
def get_dashboard_stats(
    business_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    current_month = today.month
    current_year = today.year
    month_prefix = f"{current_year}-{current_month:02d}-%"
    legacy_month_suffix = f"/{current_month:02d}/{current_year}"

    today_sales_total, cash_today, profit_today = db.query(
        func.coalesce(func.sum(Sales.total_amount), 0.0),
        func.coalesce(
            func.sum(case((Sales.is_emi == False, Sales.total_amount), else_=0.0)),
            0.0,
        ),
        func.coalesce(func.sum(Sales.total_profit), 0.0),
    ).filter(
        Sales.business_id == business_id,
        Sales.transaction_date == today_str,
    ).one()

    emi_received_today = db.query(
        func.coalesce(func.sum(EmiPayment.amount), 0.0)
    ).filter(
        EmiPayment.business_id == business_id,
        EmiPayment.date == today_str,
    ).scalar()

    emi_due_today = db.query(
        func.coalesce(func.sum(Emi.next_billing_amount), 0.0)
    ).filter(
        Emi.business_id == business_id,
        Emi.next_due_date == today_str,
        Emi.status == EmiStatus.ACTIVE,
    ).scalar()

    monthly_date_filter = (
        Sales.transaction_date.like(month_prefix),
        Sales.transaction_date.like(f"%{legacy_month_suffix}"),
    )
    output_gst = db.query(
        func.coalesce(func.sum(SaleItem.tax_amount), 0.0)
    ).join(Sales, SaleItem.sale_id == Sales.id).filter(
        Sales.business_id == business_id,
        or_(*monthly_date_filter),
    ).scalar()

    inventory_monthly_date_filter = (
        Inventory.last_restock_date.like(month_prefix),
        Inventory.last_restock_date.like(f"%{legacy_month_suffix}"),
    )
    input_gst = db.query(
        func.coalesce(func.sum(Inventory.purchase_tax_amount), 0.0)
    ).filter(
        Inventory.business_id == business_id,
        or_(*inventory_monthly_date_filter),
    ).scalar()

    net_gst = output_gst - input_gst

    margin_pct = 0.0
    if today_sales_total and today_sales_total > 0:
        margin_pct = (profit_today / today_sales_total) * 100

    return {
        "gross_sales_today": float(today_sales_total or 0),
        "cash_collected_today": float(cash_today or 0),
        "profit_today": float(profit_today or 0),
        "margin_pct": round(float(margin_pct or 0), 1),
        "emi_received_today": float(emi_received_today or 0),
        "emi_due_today": float(emi_due_today or 0),
        "output_gst": round(float(output_gst or 0), 2),
        "input_gst": round(float(input_gst or 0), 2),
        "net_gst": round(float(net_gst or 0), 2),
    }

@router.get("/bi-terminal/{business_id}")
def get_bi_terminal_stats(
    business_id: str,
    period: str = "day",  # day, week, month, year
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.business import Business, SubType
    from fastapi import HTTPException
    
    business = db.query(Business).filter(Business.id == business_id).first()
    if business and business.subscription_type != SubType.PRO:
        raise HTTPException(status_code=403, detail="Analytics access requires Pro plan.")

    from datetime import date, timedelta
    today = date.today()
    
    if period == "day":
        date_filter = Sales.transaction_date == today.strftime("%Y-%m-%d")
    elif period == "week":
        start_date = today - timedelta(days=7)
        date_filter = Sales.transaction_date >= start_date.strftime("%Y-%m-%d")
    elif period == "month":
        month_prefix = f"{today.year}-{today.month:02d}-%"
        legacy_suffix = f"/{today.month:02d}/{today.year}"
        date_filter = or_(Sales.transaction_date.like(month_prefix), Sales.transaction_date.like(f"%{legacy_suffix}"))
    elif period == "year":
        date_filter = or_(Sales.transaction_date.like(f"{today.year}-%"), Sales.transaction_date.like(f"%/{today.year}"))
    else:
        date_filter = Sales.transaction_date == today.strftime("%Y-%m-%d")

    # Overall metrics
    # The query above might duplicate if a sale has multiple items, so let's separate them.
    overall = db.query(
        func.coalesce(func.sum(Sales.total_amount), 0.0),
        func.coalesce(func.sum(Sales.total_profit), 0.0),
        func.count(Sales.id)
    ).filter(
        Sales.business_id == business_id,
        date_filter
    ).one()
    
    gross_sales = overall[0] or 0.0
    pure_profit = overall[1] or 0.0
    sales_volume = overall[2] or 0
    
    tax_data = db.query(func.coalesce(func.sum(SaleItem.tax_amount), 0.0)).join(Sales, Sales.id == SaleItem.sale_id).filter(
        Sales.business_id == business_id,
        date_filter
    ).scalar() or 0.0

    net_revenue = gross_sales - tax_data
    
    margin_pct = (pure_profit / net_revenue * 100) if net_revenue > 0 else 0.0

    # Stream
    # Let's get all sales in this period for the chart
    stream_data = db.query(
        Sales.transaction_date,
        Sales.transaction_time,
        Sales.total_amount,
        Sales.total_profit
    ).filter(
        Sales.business_id == business_id,
        date_filter
    ).all()
    
    performance_stream = []
    for s in stream_data:
        # Just return raw events, front-end will aggregate them
        performance_stream.append({
            "date": s[0],
            "time": s[1] or "00:00",
            "revenue": s[2],
            "profit": s[3]
        })

    # Item aggregates
    item_stats = db.query(
        SaleItem.name,
        func.sum(SaleItem.quantity).label("total_qty"),
        func.sum(SaleItem.profit).label("total_profit")
    ).join(Sales, Sales.id == SaleItem.sale_id).filter(
        Sales.business_id == business_id,
        date_filter
    ).group_by(SaleItem.name).all()

    # Sort in memory
    most_sold = sorted(item_stats, key=lambda x: x.total_qty or 0, reverse=True)[:5]
    least_sold = sorted(item_stats, key=lambda x: x.total_qty or 0)[:5]
    most_profitable = sorted(item_stats, key=lambda x: x.total_profit or 0, reverse=True)[:5]
    loss_making = [x for x in sorted(item_stats, key=lambda x: x.total_profit or 0) if (x.total_profit or 0) < 0][:5]

    return {
        "net_revenue": float(net_revenue),
        "pure_profit": float(pure_profit),
        "sales_volume": int(sales_volume),
        "margin_pct": round(float(margin_pct), 1),
        "performance_stream": performance_stream,
        "most_sold_items": [{"name": i.name, "value": float(i.total_qty or 0)} for i in most_sold],
        "least_sold_items": [{"name": i.name, "value": float(i.total_qty or 0)} for i in least_sold],
        "most_profitable_products": [{"name": i.name, "value": float(i.total_profit or 0)} for i in most_profitable],
        "loss_making_items": [{"name": i.name, "value": float(i.total_profit or 0)} for i in loss_making],
    }

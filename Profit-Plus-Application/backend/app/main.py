from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path
from app.core.database import engine, Base

# Models
from app.models import user
from app.models import business
from app.models import customer
from app.models import supplier
from app.models import product
from app.models import inventory
from app.models import purchase
from app.models import sales
from app.models import emipayment
from app.models import referral

# Routers
from app.routers import analytics as analytics_router
from app.routers import auth
from app.routers import business as business_router
from app.routers import product as product_router
from app.routers import inventory as inventory_router
from app.routers import customer as customer_router
from app.routers import supplier as supplier_router
from app.routers import sales as sales_router
from app.routers import purchase as purchase_router
from app.routers import emi as emi_router
from app.routers import referral as referral_router
from app.routers import subscription as subscription_router
from app.routers import admin as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Profit Plus API",
    description="SaaS backend for local business management",
    version="1.0.0"
)

# Enable Gzip compression to significantly reduce payload size
app.add_middleware(GZipMiddleware, minimum_size=1000)

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(business_router.router)
app.include_router(product_router.router)
app.include_router(inventory_router.router)
app.include_router(customer_router.router)
app.include_router(supplier_router.router)
app.include_router(sales_router.router)
app.include_router(purchase_router.router)
app.include_router(emi_router.router)
app.include_router(referral_router.router)
app.include_router(analytics_router.router)
app.include_router(subscription_router.router)
app.include_router(admin_router.router)

@app.get("/")
def root():
    return {"message": "Profit Plus API is running 🚀"}

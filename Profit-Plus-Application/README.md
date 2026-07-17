# Profit Plus Application

Profit Plus is a comprehensive Business Management and Point-of-Sale (POS) application designed to help business owners manage their day-to-day operations seamlessly. It features a modern desktop-grade user interface built purely in Python, backed by a robust and highly concurrent FastAPI backend.

## 🚀 Key Features

*   **Multi-tenant Business Management:** A single user account can create and manage multiple businesses, each with isolated data (products, sales, customers, etc.).
*   **Advanced Billing & POS System:**
    *   Search and add products to a cart dynamically.
    *   Automatic stock validation and calculation of subtotals and taxes.
    *   Integrated **EMI (Equated Monthly Installment)** tracking for sales on credit.
*   **Product & Inventory Control:**
    *   Track item categories, brands, colors, sizes, and HSN codes.
    *   Detailed stock tracking, automated deduction upon sale, and restock management.
*   **Customer & Supplier Management:** Maintain a rich database of buyers and vendors.
*   **Analytics Dashboard:** Visual representation of sales trends, revenue over time, and other business KPIs.
*   **Admin Control Panel:** Super-admin capabilities to oversee platform revenue, monitor business activity, and manage active subscriptions and users.
*   **Referral & Subscription System:** Multi-tiered access with subscription upgrades and a referral program.

## 🛠️ Technology Stack

The application is fully written in Python and is divided into two primary services:

### 1. Frontend (Flet)
*   **Framework:** [Flet](https://flet.dev/) - Allows building interactive, real-time web, desktop, and mobile applications entirely in Python based on Flutter.
*   **Architecture:** Component-based architecture with separate view files for routing (e.g., `billing_view.py`, `inventory_view.py`).
*   **State Management & Performance:** Heavily optimized UI rendering using background threading to prevent UI blocking, and atomic DOM updates to handle deep component trees. Implements generic pagination components for high-volume data tables.

### 2. Backend (FastAPI)
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast (high-performance) web framework.
*   **Database ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 with asynchronous relationships and eager loading optimizations (addressing N+1 query problems).
*   **Migrations:** Alembic.
*   **Authentication:** JWT (JSON Web Tokens) with Passlib and bcrypt for secure password hashing.
*   **Payments & Integrations:** Razorpay.
*   **Performance optimizations:** Background tasks used for generating invoice PDFs and sending out billing emails asynchronously.

## 📂 Project Structure

```text
Profit-Plus-Application/
├── backend/
│   ├── app/
│   │   ├── core/           # Database setup, config, security (JWT)
│   │   ├── models/         # SQLAlchemy DB models (User, Business, Sales, etc.)
│   │   ├── routers/        # FastAPI Endpoints
│   │   ├── schemas/        # Pydantic models for request/response validation
│   │   └── services/       # Core business logic isolating DB operations from routers
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── app/
│   │   ├── api_client.py   # REST API wrapper orchestrating cache and auth state
│   │   ├── component/      # Reusable Flet components (sidebar, pagination, themes)
│   │   ├── views/          # Flet page views (login, billing, inventory, analytics)
│   │   └── main.py         # App entry point & Routing controller
└── README.md
```


## 🏃 Getting Started

*(Assuming a virtual environment is active)*

### Backend
1. Navigate to the `backend/` directory.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (DB credentials, Razorpay tokens, JWT secrets).
4. Run the API server: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to the `frontend/` directory.
2. Ensure you have Flet installed.
3. Start the application: `flet run app/main.py`
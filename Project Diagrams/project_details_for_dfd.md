# Profit Plus - Comprehensive Project Details (For DFD Creation)

This document provides a detailed breakdown of the **Profit Plus** application to assist in creating Data Flow Diagrams (Context Diagram, Level 0, Level 1, and Level 2 DFDs). 

*Note: The referral functionality has been excluded from these details as per requirements.*

---

## 1. External Entities (Sources and Sinks)
These are the actors that interact with the system from the outside.

1.  **System Administrator (Super Admin):** Manages all users, oversees platform revenue, manages dynamic pricing, and has the authority to lock/unlock user accounts.
2.  **Business Owner (Tenant):** The primary user who registers on the platform (via OTP), creates businesses, manages inventory, handles billing, and pays for subscriptions.
3.  **Customer:** The end-consumer who purchases goods from the Business Owner. They receive invoices and SMS/email notifications for bills or pending EMI payments.
4.  **Supplier / Vendor:** The entity that supplies stock to the Business Owner. The system records purchase orders and restocks from them.
5.  **Payment Gateway (Razorpay):** External API used for processing PRO subscription upgrades via Razorpay Orders and secure signature verifications.
6.  **Email Service Provider (SMTP/API):** External service used for sending OTPs during the signup and password reset processes.

---

## 2. Core Data Stores (Databases/Tables)
These represent where the data is stored within the system (the open-ended rectangles in DFDs).

*   **D1: Users DB:** Stores user credentials, email OTPs, lock status (`is_locked`), roles (admin, owner), and profile details.
*   **D2: Businesses DB:** Stores business profiles, GST details, logos, and subscription status (FREE vs PRO) with expiry dates.
*   **D3: Products DB:** Stores product catalog data (categories, brands, sizes, colors, HSN codes).
*   **D4: Inventory DB:** Stores stock quantities, barcodes, purchase price, selling price, and low-stock alerts.
*   **D5: Customers DB:** Stores customer contact details, purchase history, and outstanding dues.
*   **D6: Suppliers DB:** Stores vendor details and contact information.
*   **D7: Sales DB:** Stores completed bills, invoice PDFs, sub-totals, taxes, and transaction modes.
*   **D8: Purchases DB:** Stores restock history and vendor purchase orders.
*   **D9: EMI DB:** Stores credit sale agreements, installment schedules, and payment logs.
*   **D10: Pricing Config (JSON/File):** Stores dynamic subscription pricing data managed by the Admin.

---

## 3. Major Processes (Level 0 DFD Modules)

### Process 1.0: User Authentication & OTP Verification
*   **Inputs:** Registration email/password, OTP code from the Business Owner.
*   **Processing:** Generates a 6-digit OTP, sends it via Email Service, verifies the OTP for signup/password reset, and issues JWT access tokens upon login.
*   **Outputs:** OTP Email, Authentication status, Secure JWT Token.
*   **Data Stores Accessed:** Users DB.

### Process 2.0: Multi-tenant Business Management
*   **Inputs:** Business details (name, address, tax info) from Business Owner.
*   **Processing:** Creates a new business profile linked to the owner's account. Validates subscription limits based on FREE/PRO plan.
*   **Outputs:** Confirmation of business creation, Business ID.
*   **Data Stores Accessed:** Businesses DB, Users DB.

### Process 3.0: Product & Inventory Management
*   **Inputs:** Product details, barcode scans, stock quantities, Supplier info.
*   **Processing:** Registers new items, adds restock data, and generates low-stock alerts.
*   **Outputs:** Updated stock levels, Inventory reports.
*   **Data Stores Accessed:** Products DB, Inventory DB, Suppliers DB, Purchases DB.

### Process 4.0: Billing & Point-of-Sale (POS)
*   **Inputs:** Barcode scans, manual item selections, Customer details.
*   **Processing:** Calculates subtotals, taxes, and grand total. Deducts sold quantity from Inventory. Generates Invoice PDF.
*   **Outputs:** Customer Invoice (PDF/Email), Updated Stock, Sales Record.
*   **Data Stores Accessed:** Products DB, Inventory DB, Customers DB, Sales DB.

### Process 5.0: EMI & Credit Sales Management
*   **Inputs:** Down payment, total installments, Customer ID.
*   **Processing:** Registers credit sale, calculates monthly installment due dates, logs partial payments.
*   **Outputs:** EMI schedule, Payment Receipts.
*   **Data Stores Accessed:** Sales DB, EMI DB, Customers DB.

### Process 6.0: Subscription & Payments (Razorpay Integration)
*   **Inputs:** Upgrade request from Business Owner.
*   **Processing:** Communicates with Razorpay API to generate an Order ID. Serves inline checkout page. Verifies the Razorpay Signature payload on callback to confirm payment. Updates business to PRO.
*   **Outputs:** Checkout Link, Payment Success/Failure Notification.
*   **Data Stores Accessed:** Businesses DB, Pricing Config.

### Process 7.0: Super Admin Controls & Reporting
*   **Inputs:** System management commands from the Admin.
*   **Processing:** Fetches global metrics, calculates total revenue from PRO subscriptions (using Pricing Config), toggles user account locks (`is_locked`), updates dynamic pricing, and can forcefully cancel subscriptions.
*   **Outputs:** Revenue Charts, Global KPI Dashboards, User Management Status.
*   **Data Stores Accessed:** Users DB, Businesses DB, Pricing Config.

---

## 4. Detailed Data Flow Examples (For Level 1 / Level 2 DFDs)

### A. Signup & OTP Flow
1.  **User** requests OTP via email.
2.  **Auth Process** generates OTP, saves hash to **Users DB**, and sends to **Email Service**.
3.  **User** receives OTP and submits full registration data with OTP.
4.  **Auth Process** validates OTP against **Users DB**.
5.  If valid, **Auth Process** completes registration and issues a JWT token.

### B. Razorpay Subscription Upgrade Flow
1.  **Business Owner** clicks "Upgrade to PRO".
2.  **Subscription Process** checks **Pricing Config**, calculates amount, and requests Order from **Razorpay API**.
3.  **Razorpay** returns an `order_id`.
4.  **Subscription Process** renders a secure checkout page.
5.  **Business Owner** completes payment through the Razorpay inline widget.
6.  Widget sends payment payload to **Subscription Process** for Signature Verification.
7.  Process validates signature, updates the status to PRO in **Businesses DB**, and shows Success page.

### C. Admin User-Lock Flow
1.  **System Administrator** queries user list from **Admin Process**.
2.  Process fetches data from **Users DB**.
3.  Admin clicks "Lock User" for a specific account.
4.  Process toggles the `is_locked` flag in **Users DB**.
5.  If that locked User tries to login, **Auth Process** will read the flag and return a `403 Forbidden` error.

---

## 5. End-to-End Entity Lifecycle Flows (Signup to End Session)

### Flow 1: The User (Business Owner) Lifecycle
1.  **Signup & OTP Verification:** User submits email -> System sends OTP via email -> User submits OTP along with profile details -> Account created in **Users DB**.
2.  **Login & Authentication:** User inputs credentials -> System validates against **Users DB** and ensures account is *not* locked -> Secure JWT Token is issued.
3.  **Business Setup & Upgrades:** User creates a business in **Businesses DB**. If they hit FREE plan limits, they initiate the Razorpay checkout flow to upgrade to PRO.
4.  **Day-to-Day Operations:** User performs inventory, POS billing, and EMI management. Every action sends the JWT token to enforce strict data isolation between businesses.
5.  **End Session (Logout):** User logs out, JWT is wiped from the client, and the session ends.

### Flow 2: The Administrator Lifecycle
1.  **Admin Login:** Admin logs in using highly-privileged, pre-configured credentials (e.g., specific admin email). A scoped Admin JWT token is issued.
2.  **Global Dashboard Access:** Admin accesses `/admin/dashboard` to view aggregated data of total users, businesses, and active subscriptions.
3.  **Platform Management:**
    *   **Revenue:** Admin views dynamically generated revenue charts based on active PRO subscriptions.
    *   **Pricing:** Admin adjusts the global subscription price which saves to the **Pricing Config** JSON.
    *   **Moderation:** Admin reviews users and can instantly toggle a user's lock status, preventing them from logging in.
    *   **Subscriptions:** Admin can forcefully cancel a business's PRO subscription back to FREE.
4.  **End Session (Logout):** Admin logs out, JWT is destroyed, and session ends securely.

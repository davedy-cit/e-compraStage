# E-Compra Developer Guide

## Architecture Overview
- **Frontend**: Vue 3 + Vite + Tailwind CSS v4 + Pinia + Vue Router
- **Backend**: Django 6.1 + DRF 3.18 + SimpleJWT + MySQL 8.4
- **Database**: Managed via SQL scripts (`sql/`) — Django `managed=False` models
- **Auth**: JWT (access 60m, refresh 7d, rotation + blacklist)

## Project Structure
```
e-compraSystem/
├── backend/
│   ├── accounts/     # User profiles, auth
│   ├── catalog/      # Products, vendors, categories, inventory
│   ├── cart/         # Cart, cart items
│   ├── orders/       # Orders, items, transactions, payments, delivery
│   ├── vendors/      # POS vendor, vendor transactions
│   ├── favorites/    # Favorite products/vendors
│   └── config/       # Django settings, URLs
├── frontend/
│   ├── src/
│   │   ├── views/       # Page components
│   │   ├── components/  # Reusable UI
│   │   ├── stores/      # Pinia stores
│   │   ├── services/    # API client
│   │   └── router/      # Vue Router
│   └── ...
├── sql/              # Schema, indexes, seed, views, procedures, roles, backup
├── docs/             # This folder
└── steps/            # Phase instructions + PROGRESS_LOG.md
```

## Database Schema Key Points
- **28 tables** across 6 apps
- **FK fields use `db_column` names**: `unit_code`, `availability_code`, `status_code`, `fulfillment_code`, `transaction_type`
- **Lookup tables**: TransactionStatus, PaymentStatus, DeliveryStatus, FulfillmentMethod, TransactionType, AvailabilityStatus
- **Seed data codes** are the contract — never use raw strings in code
- **Primary key caution**: `Customerprofile.user` is `primary_key=True` (no separate `id` field). Serializers must reference `obj.customerprofile.user.id`, not `obj.customerprofile.id`.

## API Endpoints
| Module | Base Path | Key Endpoints |
|---|---|---|
| Catalog | `/api/catalog/` | `products/`, `categories/`, `vendors/`, `units/`, `availability/` |
| Orders | `/api/orders/` | `transaction-statuses/`, `payment-statuses/`, `delivery-statuses/`, `fulfillment-methods/`, `transaction-types/` |
| Cart | `/api/cart/` | `GET /`, `POST add/`, `POST update_item/`, `POST remove_item/` |
| Checkout | `/api/checkout/` | `POST /` (cart-splitting by vendor) |
| Payment | `/api/payment/` | `POST /` (record payment) |
| Vendors | `/api/vendors/` | `GET pos/`, `POST pos/` (status update) |
| Favorites | `/api/favorites/` | `GET products/`, `GET vendors/` |
| Auth | `/api/auth/` | `POST token/`, `POST token/refresh/`, `POST token/verify/`, `GET user/` |

## Service Layer Pattern
- **Views are thin** — only HTTP handling, serialization, permission checks
- **Services contain business logic** — `orders/services.py` has `transition_order_status()`, `checkout_cart()`
- **Always use services** from views — never put logic in views

## Common Commands
```bash
# Backend
cd backend
python manage.py runserver          # Start API on :8000
python manage.py check              # Validate models
python -m pytest -v                 # Run tests
ruff check && ruff format           # Lint + format

# Frontend
cd frontend
npm run dev                         # Start Vite on :5173 (may auto-increment to :5174)
npm run build                       # Production build
npm test                            # Unit tests
npx playwright test                 # E2E tests

# Database
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_indexes.sql
mysql -u root -p < sql/03_seed.sql
```

> **CORS port note**: `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py` must include every Vite dev-server port. If Vite starts on `:5174` (port `:5173` in use), add `http://localhost:5174` and `http://127.0.0.1:5174` to the list, then restart the backend.

## Adding a New Status Code
1. Add to `sql/03_seed.sql` (INSERT INTO orders_transactionstatus)
2. Update `orders/services.py` `ALLOWED_TRANSITIONS` dict
3. Run seed script: `mysql -u root -p ecompra < sql/03_seed.sql`
4. Test transition in Vendor POS

## Deployment Checklist
- [ ] `DEBUG=False` in settings
- [ ] `ALLOWED_HOSTS` set
- [ ] `SECRET_KEY` from env
- [ ] `CORS_ALLOWED_ORIGINS` production domain
- [ ] HTTPS + HSTS headers
- [ ] Database user: `ecompra_app` (least privilege)
- [ ] Backup schedule configured
- [ ] Static files: `collectstatic` + CDN
- [ ] Frontend build: `npm run build` → serve via nginx
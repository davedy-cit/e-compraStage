# E-Compra Backend (M2 Complete)

## Stack
- Python 3.12+
- Django 6.1.3
- Django REST Framework 3.18.3
- MySQL 8.4 (local) — schema `ecompra`, charset `utf8mb4`
- PyMySQL 1.2.4
- drf-spectacular (OpenAPI 3)
- SimpleJWT (auth)
- CORS Headers (frontend integration)
- pytest / pytest-django (tests)
- ruff (lint/format)

## Setup

```powershell
# 1. Clone and enter
git clone https://github.com/davedy-cit/e-compraStage.git
cd e-compraStage/backend

# 2. Virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Dependencies
pip install -r ../requirements.txt

# 4. Environment config
Copy-Item ..\.env.example .env
# Edit .env with your MySQL root password

# 5. Database schema & seed (run once)
cmd /c "mysql -u root -p < ..\sql\01_schema.sql"
cmd /c "mysql -u root -p < ..\sql\02_indexes.sql"
cmd /c "mysql -u root -p < ..\sql\03_seed.sql"

# 6. Django migrations (creates auth_user, django_* tables)
python manage.py migrate

# 7. Auth_user handover (points FKs at real auth_user)
cmd /c "mysql -u root -p ecompra < ..\sql\04b_auth_user_fks.sql"

# 8. Superuser
python manage.py createsuperuser

# 9. Run
python manage.py runserver
```

## API Surface (M2)

| Endpoint | Description |
|---|---|
| `GET /api/catalog/products/` | List products (filter: `?q=`, `?category=`) |
| `GET /api/catalog/products/{id}/` | Product detail |
| `GET /api/catalog/categories/` | List categories |
| `GET /api/catalog/vendors/` | List vendors |
| `GET /api/catalog/units/` | List units of measure |
| `GET /api/catalog/availability/` | List availability statuses |
| `GET /api/orders/transaction-statuses/` | Transaction status lookup |
| `GET /api/orders/transaction-types/` | Transaction type lookup |
| `GET /api/orders/payment-statuses/` | Payment status lookup |
| `GET /api/orders/delivery-statuses/` | Delivery status lookup |
| `GET /api/orders/fulfillment-methods/` | Fulfillment method lookup |
| `GET /api/vendors/pos-vendors/` | POS vendor extensions |
| `GET /api/favorites/products/` | User's favorite products (auth required) |
| `GET /api/favorites/vendors/` | User's favorite vendors (auth required) |
| `POST /api/token/` | Obtain JWT pair |
| `POST /api/token/refresh/` | Refresh JWT access token |
| `GET /api/schema/swagger-ui/` | Swagger UI |
| `GET /api/schema/redoc/` | ReDoc |

## Testing

```powershell
# Clone seed to test database (run once)
cmd /c 'mysql -u root -p -e "DROP DATABASE IF EXISTS test_ecompra; CREATE DATABASE test_ecompra CHARACTER SET utf8mb4;"'
cmd /c "mysqldump -u root -p ecompra > ..\backups\test_seed.sql"
cmd /c 'mysql -u root -p test_ecompra < ..\backups\test_seed.sql'

# Run tests
pytest
```

## Linting

```powershell
ruff check backend
ruff format backend
```
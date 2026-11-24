# E-Compra System - Fresh Desktop Setup Guide

**Complete step-by-step guide to set up and run the E-Compra capstone project on a fresh desktop environment**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Repository Setup](#repository-setup)
4. [Backend Setup (Django)](#backend-setup-django)
5. [Frontend Setup (Vue 3 + Vite)](#frontend-setup-vue-3--vite)
6. [Database Setup (MySQL)](#database-setup-mysql)
7. [Environment Configuration](#environment-configuration)
8. [Running the Application](#running-the-application)
9. [Running Tests](#running-tests)
10. [Troubleshooting](#troubleshooting)
11. [Production Deployment Notes](#production-deployment-notes)

---

## 🔧 Prerequisites

### Required Software (Install in Order)

| Software | Version | Purpose | Download Link |
|----------|---------|---------|---------------|
| **Git** | 2.40+ | Version control | [git-scm.com](https://git-scm.com/downloads) |
| **Python** | 3.11+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ (LTS) | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| **MySQL** | 8.0+ | Database server | [mysql.com](https://dev.mysql.com/downloads/mysql/) |
| **MySQL Workbench** | 8.0+ | Database GUI (optional) | [mysql.com](https://dev.mysql.com/downloads/workbench/) |

### Verify Installations

```bash
# Open new terminal/PowerShell after installations
git --version          # Should show 2.40+
python --version       # Should show 3.11+
node --version         # Should show 18+
npm --version          # Should show 9+
mysql --version        # Should show 8.0+
```

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11, macOS 14+, Ubuntu 22.04+ |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB free | 20 GB free |
| **CPU** | 2 cores | 4+ cores |

---

## 📁 Repository Setup

### 1. Clone the Repository

```bash
# Navigate to your desired directory
cd C:\Users\YourName\Documents\Projects  # Windows
# cd ~/Documents/Projects                 # macOS/Linux

# Clone the repository
git clone https://github.com/your-org/e-compraSystem.git
# OR if using SSH
git clone git@github.com:your-org/e-compraSystem.git

# Enter project directory
cd e-compraSystem

# Verify branch (should be on 'develop' or 'main')
git branch
```

### 2. Verify Project Structure

```bash
# Should see this structure (only required files/folders to run the project)
e-compraSystem/
├── backend/                          # Django REST API
│   ├── accounts/                     # User auth, registration, profiles
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── authentication.py        # Custom JWT authentication
│   │   ├── migrations/              # Django auth migrations only
│   │   ├── models.py                # AuthUser, Userprofile, Customerprofile
│   │   ├── permissions.py           # IsMarketAdmin permission
│   │   ├── serializers.py           # RegisterSerializer, CurrentUserSerializer
│   │   ├── tests.py                 # RegisterAPITest
│   │   ├── urls.py
│   │   └── views.py                 # RegisterView, CurrentUserView
│   ├── cart/                         # Shopping cart
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py                # Cart, CartItem
│   │   ├── serializers.py
│   │   ├── services.py              # Cart business logic
│   │   ├── test_cart.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── catalog/                      # Products, vendors, categories
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py                # Product, Vendor, Category, UnitOfMeasure, AvailabilityStatus
│   │   ├── serializers.py           # ProductSerializer, VendorSerializer
│   │   ├── test_catalog.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── config/                       # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py              # Main settings (DB, JWT, CORS, DRF)
│   │   ├── urls.py                  # Root URL router
│   │   └── wsgi.py
│   ├── favorites/                    # Favorites feature
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py                # FavoriteProduct, FavoriteVendor
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py                 # OrderList, OrderDetail
│   ├── orders/                       # Orders, checkout, payments, POS
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py                # Order, OrderItem, Transaction, Payment, DeliveryBooking, lookup tables
│   │   ├── serializers.py           # OrderSerializer with nested Vendor
│   │   ├── services.py              # checkout_cart, status transitions
│   │   ├── test_checkout.py
│   │   ├── test_orders.py
│   │   ├── test_services.py
│   │   ├── urls.py                  # /orders/, /checkout/, /payment/
│   │   └── views.py                 # CheckoutView, PaymentView, OrderList, OrderDetail
│   ├── vendors/                      # Vendor management (admin)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py                # Vendor (uses catalog.Vendor), PosVendor
│   │   ├── serializers.py           # VendorCreateSerializer, VendorListSerializer
│   │   ├── tests.py                 # AdminVendorAPITest
│   │   ├── urls.py                  # /admin/ vendor endpoints
│   │   └── views.py                 # AdminVendorListView, CreateView, DetailView, DeactivateView
│   ├── sql/                          # Database schema & seed scripts
│   │   ├── 01_schema.sql            # Full schema (tables, indexes, FKs)
│   │   ├── 02_indexes.sql
│   │   ├── 03_seed.sql              # Lookup data, sample vendors/products
│   │   ├── 04_auth_user_handover.sql
│   │   └── 04b_auth_user_fks.sql
│   ├── .env                          # Local config (create from .env.example)
│   ├── .env.example                  # Template for environment variables
│   ├── manage.py                     # Django CLI
│   ├── requirements.txt              # Python dependencies
│   ├── pytest.ini                    # Pytest config (--reuse-db)
│   └── conftest.py                   # Pytest fixtures (test data factories)
├── frontend/                         # Vue 3 + Vite SPA
│   ├── public/                       # Static assets (favicon, etc.)
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   │   ├── Navbar.vue           # Top navigation (auth-aware)
│   │   │   ├── OrderCard.vue        # Order list card (OrderTracking)
│   │   │   └── HelloWorld.vue       # Default (can remove)
│   │   ├── views/                    # Page components (route targets)
│   │   │   ├── CatalogView.vue      # Marketplace with favorites
│   │   │   ├── ProductDetailView.vue
│   │   │   ├── CartView.vue
│   │   │   ├── CheckoutView.vue
│   │   │   ├── PaymentView.vue
│   │   │   ├── OrderTrackingView.vue
│   │   │   ├── FavoritesHistoryView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── AdminDashboardView.vue
│   │   │   ├── AdminVendorsView.vue
│   │   │   ├── VendorDashboardView.vue
│   │   │   ├── VendorProductsView.vue
│   │   │   ├── VendorOrdersView.vue
│   │   │   ├── VendorPOSView.vue
│   │   │   ├── MarketMapView.vue
│   │   │   ├── PriceComparisonView.vue
│   │   │   ├── DeliveryBookingView.vue
│   │   │   └── PickupReservationView.vue
│   │   ├── router/
│   │   │   └── index.js             # Vue Router (auth guards, roles)
│   │   ├── services/
│   │   │   └── api.js               # Axios instance (interceptors, JWT)
│   │   ├── stores/
│   │   │   ├── auth.js              # Pinia auth store (login, register, user)
│   │   │   ├── cart.js              # Pinia cart store
│   │   │   └── __tests__/auth.test.js
│   │   ├── assets/main.css          # Design system (CSS variables, utilities)
│   │   ├── style.css                # Global styles
│   │   ├── App.vue                  # Root component (global Navbar)
│   │   ├── main.js                  # App entry (Pinia, Router, Vue)
│   │   └── test/setup.js            # Vitest axios mock (vi.doMock)
│   ├── e2e/                          # Playwright E2E tests
│   │   ├── registration-admin.spec.js
│   │   └── customer-journey.spec.js
│   ├── index.html                    # Vite entry HTML
│   ├── package.json                  # NPM dependencies + scripts
│   ├── package-lock.json
│   ├── vite.config.js                # Vite config (proxy, aliases)
│   ├── vitest.config.js              # Vitest config (setupFiles)
│   ├── playwright.config.js          # Playwright config
│   ├── tailwind.config.js            # Tailwind (minimal, design system)
│   ├── postcss.config.js
│   └── .env.local                    # Local config (create: VITE_API_BASE_URL)
├── docs/                             # Project documentation (not required to run)
│   ├── IMPLEMENTATION_GUIDE_REGISTRATION_ADMIN.md
│   ├── IMPLEMENTATION_LOG_REGISTRATION_ADMIN.md
│   ├── FRONTEND_DESIGN_SYSTEM.md
│   └── (other design docs)
├── sql/                              # Root SQL (copies of backend/sql/)
│   ├── 01_schema.sql
│   ├── 02_indexes.sql
│   ├── 03_seed.sql
│   └── 04_*.sql
├── steps/                            # Development phase guides (not required)
│   ├── PROGRESS_LOG.md
│   ├── phase-0-system-design.md
│   ├── phase-1-github-setup.md
│   ├── phase-2-data-backend-core.md
│   ├── phase-3-feature-build.md
│   └── phase-4-hardening-delivery.md
├── PROMPT.md                         # Original project prompt
├── SETUP_GUIDE.md                    # This file
└── requirements.txt                  # Root requirements (pip install -r requirements.txt)
```

**Key Required Files Checklist:**
| File | Purpose | Required |
|------|---------|----------|
| `backend/.env` | DB credentials, JWT secret, CORS | ✅ Yes |
| `backend/requirements.txt` | Python deps | ✅ Yes |
| `backend/sql/01_schema.sql` | MySQL schema | ✅ Yes |
| `backend/sql/03_seed.sql` | Lookup/seed data | ✅ Yes |
| `frontend/.env.local` | API base URL | ✅ Yes |
| `frontend/package.json` | NPM deps + scripts | ✅ Yes |
| `backend/manage.py` | Django CLI | ✅ Yes |
| `frontend/vite.config.js` | Dev server proxy | ✅ Yes |

---

## 🐍 Backend Setup (Django)

### 1. Create Python Virtual Environment

```bash
cd backend

# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Verify activation (should show (.venv) in prompt)
python -c "import sys; print(sys.prefix)"
```

### 2. Upgrade pip and Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "django|djangorestframework|mysql|simplejwt|drf-spectacular"
```

Expected packages:
- Django 4.2+
- djangorestframework 3.14+
- mysqlclient / pymysql
- djangorestframework-simplejwt
- drf-spectacular
- pytest-django

### 3. Install MySQL Client (if not in requirements.txt)

```bash
# Windows (if mysqlclient fails)
pip install pymysql

# macOS
brew install mysql-client
pip install mysqlclient

# Ubuntu
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

---

## 🗄️ Database Setup (MySQL)

### 1. Start MySQL Service

```bash
# Windows (PowerShell as Administrator)
net start mysql80
# OR: net start MySQL

# macOS
brew services start mysql

# Ubuntu/Linux
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2. Secure MySQL Installation (First Time Only)

```bash
mysql_secure_installation
# Follow prompts:
# - Set root password
# - Remove anonymous users
# - Disallow root login remotely
# - Remove test database
# - Reload privilege tables
```

### 3. Create Database and User

```bash
# Login to MySQL
mysql -u root -p
# Enter root password when prompted
```

**Run these SQL commands in MySQL:**

```sql
-- Create database
CREATE DATABASE ecompra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create test database
CREATE DATABASE test_ecompra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER 'ecompra_app'@'localhost' IDENTIFIED BY 'your_secure_password';
CREATE USER 'ecompra_app'@'127.0.0.1' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_app'@'localhost';
GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_app'@'127.0.0.1';
GRANT ALL PRIVILEGES ON test_ecompra.* TO 'ecompra_app'@'localhost';
GRANT ALL PRIVILEGES ON test_ecompra.* TO 'ecompra_app'@'127.0.0.1';

FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'ecompra_app';

EXIT;
```

### 4. Import Schema (if SQL dump exists)

```bash
# If you have a schema dump file
mysql -u ecompra_app -p ecompra < backend/sql/schema.sql

# OR if using the test database for development
mysql -u ecompra_app -p test_ecompra < backend/sql/schema.sql
```

---

## ⚙️ Environment Configuration

### 1. Backend Environment File

```bash
cd backend

# Copy example
cp .env.example .env
```

**Edit `.env` with your values:**

```ini
# Django
SECRET_KEY=your-super-secret-key-generate-with-python -c "import secrets; print(secrets.token_urlsafe(50))"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ecompra
DB_USER=ecompra_app
DB_PASSWORD=your_secure_password
DB_HOST=127.0.0.1
DB_PORT=3306

# CORS (for frontend dev server)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# Email (console backend for dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 2. Frontend Environment File

```bash
cd ../frontend

# Copy example (if exists)
cp .env.example .env.local 2>/dev/null || echo 'VITE_API_BASE_URL=http://localhost:8000/api/' > .env.local
```

**Edit `.env.local`:**

```ini
# API Base URL (must match backend)
VITE_API_BASE_URL=http://localhost:8000/api/

# Optional: Sentry, Analytics, etc.
# VITE_SENTRY_DSN=
```

---

## 🗃️ Database Migration & Seeding

### 1. Run Django Migrations

```bash
cd backend
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # macOS/Linux

# Create tables for managed apps (auth, admin, sessions, etc.)
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

### 2. Handle Unmanaged Models (Important!)

This project uses `managed=False` for most models (they map to existing MySQL tables). You need to:

**Option A: Use existing schema dump (recommended)**
```bash
# Import the full schema with data
mysql -u ecompra_app -p ecompra < backend/sql/full_dump.sql
```

**Option B: Create tables manually via Django inspectdb**
```bash
# This won't work for managed=False models - you need the actual MySQL tables
# The models are already defined in backend/*/models.py
# You must have the tables created in MySQL beforehand
```

**Option C: Use the provided SQL scripts**
```bash
# Check for SQL files in backend/sql/
ls -la backend/sql/

# Run any schema creation scripts
mysql -u ecompra_app -p ecompra < backend/sql/create_tables.sql
mysql -u ecompra_app -p ecompra < backend/sql/seed_data.sql
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your choice)
```

### 4. Verify Database Connection

```bash
python manage.py check
python manage.py dbshell
# Should connect to MySQL without errors
# Type \q to exit
```

---

## 🎨 Frontend Setup (Vue 3 + Vite)

### 1. Install Dependencies

```bash
cd frontend

# Install packages (use npm ci for clean install)
npm ci
# OR
npm install

# Verify key packages
npm list | grep -E "vue|vite|pinia|axios|vitest|playwright"
```

Expected packages:
- Vue 3.3+
- Vite 4+
- Pinia 2+
- Axios 1+
- Vue Router 4+
- Vitest 0.34+
- Playwright 1.35+

### 2. Verify Build Works

```bash
# Development build check
npm run build

# Should complete without errors
# Output in dist/ folder
```

---

## 🚀 Running the Application

### Terminal 1: Backend Server

```bash
cd e-compraSystem/backend
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # macOS/Linux

# Run Django development server
python manage.py runserver 8000

# Should show:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK (Windows) / CONTROL-C (macOS/Linux)
```

### Terminal 2: Frontend Server

```bash
cd e-compraSystem/frontend

# Run Vite development server
npm run dev

# Should show:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: http://192.168.x.x:5173/
```

### 3. Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend (Vue 3) |
| http://localhost:8000/api/ | Backend API |
| http://localhost:8000/api/schema/swagger-ui/ | API Documentation |
| http://localhost:8000/admin/ | Django Admin |

---

## ✅ Running Tests

### Backend Tests (pytest)

```bash
cd backend
source .venv/Scripts/activate

# Run all tests (uses --reuse-db flag from pytest.ini)
python -m pytest -v

# Run specific app tests
python -m pytest accounts/tests.py -v
python -m pytest vendors/tests.py -v
python -m pytest orders/ -v

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Frontend Unit Tests (Vitest)

```bash
cd frontend

# Run once (CI mode)
npm test -- --run

# Run in watch mode
npm test
```

### E2E Tests (Playwright)

```bash
cd frontend

# Install browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run headed (visible browser)
npx playwright test --headed
```

### All Tests Summary

| Test Suite | Command | Expected |
|------------|---------|----------|
| Backend | `python -m pytest -v` | 27 passed |
| Frontend Unit | `npm test -- --run` | 8 passed |
| E2E | `npx playwright test` | 12 passed |
| **Total** | | **47 passed** |

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. MySQL Connection Errors

```bash
# Error: Can't connect to MySQL server
# Solution: Check MySQL service is running
net start mysql80        # Windows
brew services start mysql # macOS
sudo systemctl start mysql # Linux

# Error: Access denied for user
# Solution: Verify user privileges
mysql -u root -p -e "SHOW GRANTS FOR 'ecompra_app'@'localhost';"
```

#### 2. Python Module Not Found

```bash
# Error: ModuleNotFoundError: No module named 'mysqlclient'
# Solution:
pip install pymysql  # Alternative pure-Python driver

# Or install mysqlclient properly:
# Windows: pip install mysqlclient (may need Visual C++ Build Tools)
# macOS: brew install mysql-client && pip install mysqlclient
# Ubuntu: sudo apt-get install python3-dev default-libmysqlclient-dev && pip install mysqlclient
```

#### 3. Virtual Environment Not Activating

```bash
# Windows PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1

# Or use Command Prompt instead of PowerShell
.venv\Scripts\activate.bat
```

#### 4. Frontend API Connection Errors

```bash
# Error: Network Error / CORS
# Solution: Check .env.local has correct API URL
# Check backend CORS_ALLOWED_ORIGINS in .env includes frontend URL
# Restart both servers after changes
```

#### 5. Port Already in Use

```bash
# Error: Port 8000/5173 already in use
# Solution: Kill existing processes
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

#### 6. Vue Runtime Compilation Warning

```bash
# Warning: "Component provided template option but runtime compilation is not supported"
# Solution: Already fixed in project - ensure components use <script setup> 
# and not inline template strings with defineComponent
```

#### 7. Test Database Issues

```bash
# Error: Table doesn't exist in test database
# Solution: The project uses managed=False models with --reuse-db
# Run tests with pytest (not python manage.py test) to reuse test database
python -m pytest -v  # Works with --reuse-db
```

---

## 📦 Production Deployment Notes

### Backend Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use PostgreSQL or MySQL with connection pooling
- [ ] Configure `SECURE_SSL_REDIRECT=True`
- [ ] Set up static file serving (nginx/Apache)
- [ ] Configure Gunicorn/uWSGI
- [ ] Set up process manager (systemd/Supervisor)
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)

### Frontend Production Checklist

- [ ] Run `npm run build` 
- [ ] Serve `dist/` folder with nginx/Apache
- [ ] Configure reverse proxy to backend API
- [ ] Enable gzip/brotli compression
- [ ] Set up CSP headers
- [ ] Configure cache headers for static assets

### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🔄 Daily Development Workflow

```bash
# 1. Pull latest changes
git pull origin develop

# 2. Activate virtual environment
cd backend
source .venv/Scripts/activate

# 3. Run migrations (if any new ones)
python manage.py migrate

# 4. Start backend
python manage.py runserver 8000

# 5. In new terminal, start frontend
cd frontend
npm run dev

# 6. Run tests before committing
cd backend && python -m pytest -v
cd frontend && npm test -- --run && npx playwright test
```

---

## 📚 Useful Commands Reference

### Django Management Commands

```bash
# Create new app
python manage.py startapp newapp

# Create migration (for managed models)
python manage.py makemigrations appname

# Inspect database
python manage.py inspectdb > models.py

# Shell access
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check --deploy
```

### Frontend Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

### Git Commands

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/new-feature

# Commit with message
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Create PR on GitHub/GitLab
```

---

## 📞 Support & Resources

### Project Documentation
- `docs/IMPLEMENTATION_LOG_REGISTRATION_ADMIN.md` - Implementation history
- `docs/PROGRESS_LOG.md` - Development progress
- `IMPLEMENTATION_GUIDE_REGISTRATION_ADMIN.md` - Original implementation guide

### Key Files to Understand
- `backend/config/settings.py` - Django settings
- `backend/config/urls.py` - API routes
- `frontend/vite.config.js` - Vite configuration
- `frontend/src/router/index.js` - Vue routes
- `frontend/src/stores/auth.js` - Pinia auth store
- `frontend/src/services/api.js` - Axios instance

### Test Credentials (Development)

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Market Admin | `marketadmin` | `adminpass123` | Admin Dashboard, Vendor Management |
| Superuser | `admin` | `Admin2627` | Full Admin |
| Customer | (register) | (user-defined) | Marketplace, Cart, Orders |
| Vendor | (created by admin) | (admin-defined) | Vendor Dashboard, POS |

---

## 🎯 Quick Start Checklist

- [ ] Git installed and configured
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MySQL 8.0+ installed and running
- [ ] Repository cloned
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Database created and user granted privileges
- [ ] Schema imported (or tables created)
- [ ] `.env` files configured
- [ ] Migrations run
- [ ] Frontend dependencies installed
- [ ] Backend server running on :8000
- [ ] Frontend server running on :5173
- [ ] All 47 tests passing
- [ ] Application accessible at http://localhost:5173

---

**Guide Version:** 1.0  
**Last Updated:** 2026-11-24  
**Project:** E-Compra System (CCS630 Capstone)  
**Branches:** `develop` (development), `master` (production)
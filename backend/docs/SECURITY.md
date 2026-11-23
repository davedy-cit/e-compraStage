# E-Compra Security Audit

This document describes the security measures implemented in the E-Compra system, covering OWASP Top 10 relevant items, and documents known limitations for the student project scope.

## Authentication & Authorization

| Measure | Description |
|---------|-------------|
| **JWT Tokens** | Short-lived access tokens (60 min), rotating refresh tokens (7 days) with blacklist after rotation |
| **Password Hashing** | Django's PBKDF2 with SHA-256 (default) via `django.contrib.auth` |
| **Role-Based Access** | Customer / Vendor / Admin roles enforced at view level via `meta.role` router guards and view permission checks |
| **Object-Level Permissions** | Vendors can only access their own orders/Products; customer orders filtered by `request.user` |
| **Authentication Class** | Custom `CustomJWTAuthentication` fetches actual `AuthUser` model (not `TokenUser`) |
| **Token Rotation** | `ROTATE_REFRESH_TOKENS: True` + `BLACKLIST_AFTER_ROTATION: True` mitigates token theft |

## Input Validation & Injection Prevention

| Measure | Description |
|---------|-------------|
| **ORM Parameterization** | All database queries via Django ORM — no raw SQL in views; user input never interpolated into SQL strings |
| **Serializer Validation** | DRF serializers validate all input fields (types, ranges, required fields) before business logic executes |
| **FK Lookups** | Status transitions use `Model.objects.get(code=...)` object lookups — no raw string assignment to FK fields |
| **Choice Constraints** | Availability status, fulfillment method, payment status, transaction type all constrained via seed-data lookup tables |
| **Request Size** | DRF throttling not yet configured (see Known Limitations) |

## Data Protection

| Measure | Description |
|---------|-------------|
| **No Card Data Stored** | Payment records only store provider reference (not PAN/CVV/expiry) — PCI scope excluded |
| **UTF-8mb4** | Full UTF-8mb4 charset end-to-end (MySQL schema, seed data, ORM) — safe for ₱ currency symbol and multilingual content |
| **HTTPS Enforced** | Production uses TLS 1.2+ (configured at reverse proxy / load balancer); `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` recommended |
| **Secrets Management** | `.env` for secrets (`SECRET_KEY`, `DB_PASSWORD`); `.gitignore` prevents commits of `.env` |
| **Session Tokens** | JWT access tokens stored in `localStorage` (not HttpOnly cookies) — acceptable for SPA architecture; refresh token rotation limits exposure |

## CORS & CSRF

| Measure | Description |
|---------|-------------|
| **CORS** | Restricted to `http://localhost:5173` (dev) / production domain via `CORS_ALLOWED_ORIGINS`; `CORS_ALLOW_CREDENTIALS=True` |
| **CSRF** | Not needed for JWT stateless API; `SessionAuthentication` only used for Django admin |

## Database Security

| Measure | Description |
|---------|-------------|
| **Least-Privilege Roles** | See `sql/06_roles_grants.sql` (M4.15) — `ecompra_app`, `ecompra_readonly`, `ecompra_admin` roles |
| **Managed=False Models** | Django `managed=False` models — Django cannot `DROP`/`ALTER` tables; schema changes via SQL scripts only (`sql/01_schema.sql`, `sql/02_indexes.sql`, etc.) |
| **FK Constraints** | 37 foreign key constraints enforce referential integrity at the database level |
| **Check Constraints** | `CHECK (total_amount >= 0)` on orders; uniqueness constraints on favorites, payments |
| **Password Storage** | Django's built-in password hashing (PBKDF2) — never plaintext |

## Audit Logging

| Measure | Description |
|---------|-------------|
| **Inventory Ledger** | Every stock change writes to `catalog_inventorymovement` (product, quantity change, reason, timestamp) — immutable audit trail |
| **Payment Records** | Immutable payment rows with provider reference, status, and timestamps — financial audit trail |
| **Delivery Bookings** | Order fulfillment tracked via `orders_deliverybooking` — fulfillment audit trail |

## OWASP Top 10 (2021) Coverage

| OWASP Category | Coverage | Implementation |
|----------------|----------|----------------|
| A01: Broken Access Control | ✅ Covered | Role-based guards, object-level permissions, vendor-scoped order access |
| A02: Cryptographic Failures | ✅ Covered | PBKDF2 password hashing, JWT signing with HS256, no card data storage |
| A03: Injection | ✅ Covered | Django ORM parameterization, DRF serializer validation, no raw SQL |
| A04: Insecure Design | ✅ Covered | Service layer pattern separates business logic from views; ALLOWED_TRANSITIONS state machine |
| A05: Security Misconfiguration | ⚠️ Partial | `.gitignore` protects `.env`; CORS restricted; DEBUG=True only in dev |
| A06: Vulnerable Components | ⚠️ Partial | Pinned dependencies in `requirements.txt`; no automated scanning yet |
| A07: Authentication Failures | ✅ Covered | Short-lived JWT access (60m), rotating refresh tokens (7d), blacklist after rotation |
| A08: Software/Data Integrity Failures | ⚠️ Partial | Immutable payment records, inventory ledger; no signed updates |
| A09: Logging Failures | ✅ Covered | Inventory ledger, payment records, delivery bookings provide audit trails |
| A10: Server-Side Request Forgery | ⚠️ Partial | No external HTTP calls from server-side code; CORS restricts browser origins |

## Known Limitations (Student Project Scope)

1. **No rate limiting** on auth endpoints — add `django-ratelimit` in production to prevent brute-force attacks
2. **No 2FA** — recommend TOTP for vendor/admin accounts
3. **No automated security scanning** — add `bandit` and `safety` to CI pipeline
4. **JWT in localStorage** — vulnerable to XSS; consider HttpOnly cookies for production
5. **DEBUG=True** — only safe in development; must be `False` in production
6. **No SSL/TLS enforcement** at application level — rely on reverse proxy for HTTPS
7. **No password complexity validation** — Django's default validators apply but are not customized
8. **No session timeout UI warning** — tokens expire silently after 60 minutes

## Security Checklist for Production Deployment

- [ ] `DEBUG=False` in settings
- [ ] `ALLOWED_HOSTS` set to production domain(s)
- [ ] `SECRET_KEY` from environment variable (not hardcoded)
- [ ] `CORS_ALLOWED_ORIGINS` set to production domain(s)
- [ ] HTTPS + HSTS headers configured at reverse proxy
- [ ] Database user: `ecompra_app` (least privilege, no DDL)
- [ ] Backup schedule configured (`scripts/backup.ps1`)
- [ ] Frontend build served via nginx with security headers
- [ ] Rate limiting enabled on auth endpoints
- [ ] Automated security scanning in CI

## CCS630 Lessons Applied

- **Defense in depth**: Multiple layers (ORM parameterization + serializer validation + DB constraints) prevent injection
- **Principle of least privilege**: Database roles and Django permission classes limit what each component can do
- **Audit trails**: Inventory ledger and payment records provide immutable logs for compliance
- **State machine security**: `ALLOWED_TRANSITIONS` in service layer prevents unauthorized status jumps
- **Secret management**: `.env` + `.gitignore` prevents credential exposure in version control
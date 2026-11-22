# Phase 2 — Data & Backend Core

**Milestone M2 · Nov 19 – Dec 2, 2026 · 18 steps · Steps M2.1 – M2.18**

This milestone builds the Django backend on top of the M0 schema: project skeleton, MySQL connection via
PyMySQL, the 27 domain models mapped to the existing tables, the admin site, a read-only DRF browse API,
OpenAPI docs, CORS + JWT, and the first tests. **Work happens on `develop`** — `master` is protected.

**Core ruling for this phase — the SQL scripts remain the source of truth.** All domain models are
`managed = False`: Django reads and writes the tables M0 created, it does not re-create them. Only Django's
own tables (auth, sessions, admin log, content types) are migration-managed. This keeps the M0.13
reproducibility story intact: `01_schema.sql` + `02_indexes.sql` + `03_seed.sql` + `manage.py migrate` = the
whole database, from nothing.

> **You build; the coach instructs and verifies.** Type every command and every file yourself.

---

## Step M2.1 — Virtual environment & project skeleton

**Goal.** Django installed in a virtualenv and the `config` project living in `backend/`.

**Where.** `backend/` — PowerShell.

**Actions.**

1. Create and activate the virtualenv:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2. Install the pinned stack from M0.2:

```powershell
pip install -r ..\requirements.txt
```

3. Create the project **inside** `backend/` (note the trailing dot):

```powershell
django-admin startproject config .
```

4. Smoke-test it:

```powershell
python manage.py check
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — you should see the Django rocket page. Stop the server with Ctrl+C.

**Expected result.** `backend/config/`, `backend/manage.py`, `backend/config/settings.py` exist; check passes; rocket page loads.

**Verify.** Run and paste:

```powershell
Get-ChildItem backend
python manage.py check
```

Expected: `config/`, `manage.py`, `.venv/` listed; `System check identified no issues (0 silenced).`

**If it fails.**
- `.\.venv\Scripts\Activate.ps1 cannot be loaded… running scripts is disabled` →
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.
- `django-admin: command not found` → the venv is not active; run step 1 again.
- `python` resolves to the wrong install → use `py -3.13` everywhere `python` appears.

> 📌 **CCS630 lesson — environments are reproducibility too.** The venv isolates this project's exact package
> versions from every other project on the machine, the same way `01_schema.sql` isolates the schema.

---

## Step M2.2 — Secrets & settings via python-dotenv

**Goal.** No secret in source control: `SECRET_KEY` and DB credentials come from `backend/.env`.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. Generate a secret key and create `backend/.env`:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Create `backend/.env` with (substitute your values):

```env
SECRET_KEY=<paste the generated key>
DEBUG=True
DB_NAME=ecompra
DB_USER=root
DB_PASSWORD=<your MySQL root password>
DB_HOST=127.0.0.1
DB_PORT=3306
```

2. Create `backend/.env.example` — same keys, **no real values**:

```env
SECRET_KEY=
DEBUG=True
DB_NAME=ecompra
DB_USER=
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

3. Edit `backend/config/settings.py` — top of the file:

```python
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
```

**Expected result.** `manage.py check` still passes with the env-driven settings.

**Verify.** Run and paste:

```powershell
git check-ignore backend/.env
python manage.py check
```

Expected: `backend/.env` printed (it is ignored — the M0.1 `.gitignore` rule `​.env` matches in any folder),
and the check passes.

**If it fails.**
- `git check-ignore` prints nothing and exits 1 → `.env` would be committed! Stop, fix `.gitignore` before anything else.
- `ModuleNotFoundError: dotenv` → the venv is not active.

> 📌 **CCS630 lesson — the same security rule as M0.1, now with a real secret.** `.env` never travels; `.env.example`
> documents the shape without the value.

---

## Step M2.3 — MySQL connection via PyMySQL

**Goal.** Django talks to the local MySQL 8 `ecompra` database through PyMySQL.

**Where.** `backend/` — editor, PowerShell.

**Actions.**

1. Add the PyMySQL shim to `backend/config/__init__.py`:

```python
import pymysql

pymysql.install_as_MySQLdb()
```

2. Replace `DATABASES` in `backend/config/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "ecompra"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

3. Prove the connection reaches the existing tables:

```powershell
python manage.py dbshell
```

then inside the client:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM catalog_product;
exit
```

**Expected result.** `dbshell` opens a MySQL client connected to `ecompra`; `SHOW TABLES` lists the 28 M0 tables.

**Verify.** Run and paste:

```powershell
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME']); print('db ok')"
```

Expected: `ecompra` and `db ok`.

**If it fails.**
- `Error loading MySQLdb module` → the shim in step 1 is missing or `config/__init__.py` was not saved.
- `Access denied for user 'root'` → `DB_PASSWORD` in `.env` is wrong; fix it.
- `Unknown database 'ecompra'` → re-run the M0 scripts (`sql/01_schema.sql` → `02` → `03`).

> 📌 **CCS630 lesson — the DB predates the app.** Django is joining a database that already exists and is already
> populated — the normal situation in industry, and the reason `inspectdb` (next steps) exists.

---

## Step M2.4 — Apps + generate models with inspectdb

**Goal.** Six Django apps matching the schema's table prefixes, and a first-pass `inspectdb` model dump.

**Where.** `backend/` — PowerShell.

**Actions.**

1. Create the six apps:

```powershell
python manage.py startapp accounts
python manage.py startapp catalog
python manage.py startapp cart
python manage.py startapp orders
python manage.py startapp vendors
python manage.py startapp favorites
```

2. Register them in `INSTALLED_APPS` (settings.py) — **before** the default `django.contrib.*` entries' comment
   block ends, add:

```python
    "accounts",
    "catalog",
    "cart",
    "orders",
    "vendors",
    "favorites",
```

3. Dump every table's generated model class:

```powershell
python manage.py inspectdb > _inspectdb_all.py
```

4. Note the table → app mapping you will use in M2.5:

| App | Tables (prefix) | Count |
|---|---|---|
| accounts | `accounts_userprofile`, `accounts_customerprofile` | 2 |
| catalog | `catalog_*` (vendor, category, unitofmeasure, comparisongroup, comparisongroupunit, availabilitystatus, product, inventoryreason, inventorymovement) | 9 |
| cart | `cart_cart`, `cart_cartitem` | 2 |
| orders | `orders_*` (5 lookups + order, orderitem, transaction, payment, deliverybooking) | 10 |
| vendors | `vendors_vendor`, `vendors_vendortransaction` | 2 |
| favorites | `favorites_favoriteproduct`, `favorites_favoritevendor` | 2 |

That is 27 domain tables. Any `django_*` or `auth_*` classes in the dump are **discarded** — Django's own apps own those.

**Expected result.** Six app folders; `_inspectdb_all.py` holds generated classes for all 28 tables.

**Verify.** Run and paste:

```powershell
(Get-ChildItem backend -Directory | Where-Object Name -in accounts,catalog,cart,orders,vendors,favorites).Count
Select-String -Path _inspectdb_all.py -Pattern "^class " | Measure-Object -Line
```

Expected: `6` apps, and ≥ 27 generated classes.

**If it fails.**
- `inspectdb` prints an error about a table → note which table; you can re-run for single tables later:
  `python manage.py inspectdb catalog_product`.
- `startapp` says the app already exists → skip that one; it was created in an earlier attempt.

> 📌 **CCS630 lesson — from ER to relational to ORM.** You designed the ER model (M0), wrote the relational DDL
> (M0.7), and now generate the ORM from the database — the same model, three representations.

---

## Step M2.5 — Clean up the models, per app

**Goal.** Hand-verified model classes in the right apps: proper names, `db_table`, `managed = False`,
`__str__`, and FKs pointing at the project's `AuthUser` (in `accounts` app, mapped to the existing `auth_user` table).

**Where.** `backend/<app>/models.py` — editor.

**Actions.**

For **each** app, move its classes from `_inspectdb_all.py` into `<app>/models.py` and fix them up:

1. **Rename classes** to CamelCase domain names. The inspectdb output uses `AppTable` prefixes; the actual
   renames used in this project:

   | inspectdb name | → | Domain name | App |
   |---|---|---|---|
   | `UsersUserprofile` | → | `Userprofile` | accounts |
   | `UsersCustomerprofile` | → | `Customerprofile` | accounts |
   | `UsersAuthUser` | → | `AuthUser` | accounts |
   | `CatalogProduct` | → | `Product` | catalog |
   | `CatalogVendor` | → | `Vendor` | catalog |
   | `CatalogCategory` | → | `Category` | catalog |
   | `CatalogUnitofmeasure` | → | `UnitOfMeasure` | catalog |
   | `CatalogComparisongroup` | → | `ComparisonGroup` | catalog |
   | `CatalogComparisongroupunit` | → | `ComparisonGroupUnit` | catalog |
   | `CatalogAvailabilitystatus` | → | `AvailabilityStatus` | catalog |
   | `CatalogInventoryreason` | → | `InventoryReason` | catalog |
   | `CatalogInventorymovement` | → | `InventoryMovement` | catalog |
   | `CartCart` | → | `Cart` | cart |
   | `CartCartitem` | → | `CartItem` | cart |
   | `OrdersOrder` | → | `Order` | orders |
   | `OrdersOrderitem` | → | `OrderItem` | orders |
   | `OrdersTransaction` | → | `Transaction` | orders |
   | `OrdersPayment` | → | `Payment` | orders |
   | `OrdersDeliverybooking` | → | `DeliveryBooking` | orders |
   | `OrdersTransactionstatus` | → | `TransactionStatus` | orders |
   | `OrdersTransactiontype` | → | `TransactionType` | orders |
   | `OrdersPaymentstatus` | → | `PaymentStatus` | orders |
   | `OrdersDeliverystatus` | → | `DeliveryStatus` | orders |
   | `OrdersFulfillmentmethod` | → | `FulfillmentMethod` | orders |
   | `VendorsVendor` | → | `PosVendor` | vendors (POS 1:1 extension) |
   | `VendorsVendortransaction` | → | `VendorTransaction` | vendors |
   | `FavoritesFavoriteproduct` | → | `FavoriteProduct` | favorites |
   | `FavoritesFavoritevendor` | → | `FavoriteVendor` | favorites |

2. **Every model gets exactly**:

```python
    class Meta:
        managed = False          # M0 SQL scripts are the source of truth
        db_table = "<exact_table_name>"
```

3. **Add `__str__`** to each model — the human-meaningful field(s), e.g.:

```python
    def __str__(self):
        return self.name                     # Vendor, Category, Product, PosVendor
        # return self.code                   # lookups (TransactionStatus, UnitOfMeasure, …)
        # return f"Order {self.pk} ({self.status_code})"   # Order
```

4. **Re-point user FKs.** The `AuthUser` model lives in `accounts` app (`db_table='auth_user'`, `managed=False`).
   **Do not use Django's built-in `User`.** Instead, reference `AuthUser` via string ref with the correct
   `on_delete` per the schema (not just `PROTECT`):

   ```python
   # accounts app — user is PK, CASCADE
   user = models.OneToOneField('accounts.AuthUser', models.CASCADE, primary_key=True)

   # catalog.Vendor — user is 1:1, DO_NOTHING (M6 ruling: vendor identity = catalog_vendor.user NOT NULL)
   user = models.OneToOneField('accounts.AuthUser', models.DO_NOTHING)

   # cart.Cart — user is PK, CASCADE
   user = models.OneToOneField('accounts.AuthUser', models.CASCADE, primary_key=True)

   # orders.Order — user nullable for walk-ins (C5), SET_NULL
   user = models.ForeignKey('accounts.AuthUser', models.SET_NULL, blank=True, null=True)

   # favorites — user FK, CASCADE
   user = models.ForeignKey('accounts.AuthUser', models.CASCADE)
   ```

   (`null=True` **only** on `Order.user` per C5; every other user FK is `NOT NULL`.)

5. **Cross-app FKs** use string references with the correct `on_delete` per schema:

   ```python
   # catalog.Product → catalog.Vendor (CASCADE per schema)
   vendor = models.ForeignKey('catalog.Vendor', models.CASCADE, db_column='vendor_id')

   # catalog.Product → catalog.Category (DO_NOTHING)
   category = models.ForeignKey('catalog.Category', models.DO_NOTHING)

   # catalog.Product → catalog.UnitOfMeasure (DO_NOTHING)
   unit = models.ForeignKey('catalog.UnitOfMeasure', models.DO_NOTHING, db_column='unit_code')

   # orders.Order → catalog.Vendor (DO_NOTHING)
   vendor = models.ForeignKey('catalog.Vendor', models.DO_NOTHING)

   # orders.Order → orders.TransactionStatus (DO_NOTHING)
   status = models.ForeignKey('orders.TransactionStatus', models.DO_NOTHING, db_column='status_code')

   # vendors.PosVendor → catalog.Vendor (1:1 PK, CASCADE)
   catalog_vendor = models.OneToOneField('catalog.Vendor', models.CASCADE, primary_key=True)

   # favorites → catalog.Product / catalog.Vendor (CASCADE)
   product = models.ForeignKey('catalog.Product', models.CASCADE)
   vendor = models.ForeignKey('catalog.Vendor', models.CASCADE)
   ```

   ⚠️ **Match the exact `on_delete` from the M0 schema** — it varies (CASCADE, SET_NULL, DO_NOTHING, RESTRICT).

6. **Delete `_inspectdb_all.py`** when every class has been moved — do not commit it.

Work one app at a time; after each app:

```powershell
python manage.py check
```

**Expected result.** 27 model classes across six apps, all `managed = False`, all with `db_table`, `__str__`.

**Verify.** Run and paste:

```powershell
python manage.py check
Select-String -Path accounts\models.py,catalog\models.py,cart\models.py,orders\models.py,vendors\models.py,favorites\models.py -Pattern "managed = False" | Measure-Object -Line
Select-String -Path accounts\models.py,catalog\models.py,cart\models.py,orders\models.py,vendors\models.py,favorites\models.py -Pattern "db_table" | Measure-Object -Line
```

Expected: check passes; `managed = False` ≥ 27; `db_table` ≥ 27.

**If it fails.**
- `unused import` / lint noise → ignore for now; M2.16 cleans style.
- `ImproperlyConfigured: app_label` → a model class name does not match any installed app convention; add
  `app_label` in `Meta` or confirm the file lives in the right app.
- `NameError: name 'X' is not defined` → cross-app FK used bare class name; use string ref `'app.Model'`.
- `TypeError: 'X' is not a class` → wrong class name; check rename table above.
- `ERROR 3780 Referencing column ... incompatible` → FK column type doesn't match target PK; check `db_column`.
- A `related_name` clash (two FKs to the same model) → inspectdb names them `<model>_set` twice; add explicit
  `related_name=` to each.

> 📌 **CCS630 lesson — read generated code critically.** `inspectdb` is a starting point, not an authority: it
> cannot know your design intent (which ruling made `user` nullable, which extension is 1:1). You are reconciling
> three documents — schema, ER mapping, ORM — and mismatches are findings, not accidents.

---

## Step M2.6 — Hand over `auth_user` to Django, then migrate

**Goal.** Django's own tables created by migrations, with the M0 placeholder `auth_user` replaced by the real
one — and every FK that pointed at it re-created.

**Why.** `01_schema.sql` created a placeholder `auth_user`, but Django's admin/sessions/auth need the *full*
auth schema (`auth_group`, `auth_permission`, …) that only `migrate` can build. `migrate` cannot run while the
placeholder blocks `CREATE TABLE auth_user`. The database is empty of users, so replacing it loses nothing.

**Where.** `backend/` — PowerShell, `sql/`.

**Actions.**

1. List the FKs that reference `auth_user` (there are 7 — profiles, vendor, order, cart, favorites):

```sql
SELECT table_name, constraint_name, column_name
FROM information_schema.key_column_usage
WHERE table_schema = 'ecompra' AND referenced_table_name = 'auth_user';
```

2. Create `sql/04_auth_user_handover.sql` with **two sections**, using exactly the names from step 1.
   ⚠️ MySQL uses `DROP FOREIGN KEY <name>` (not `DROP CONSTRAINT`):

```sql
-- Section 1 — run BEFORE `migrate` (one-off)
ALTER TABLE accounts_userprofile        DROP FOREIGN KEY fk_userprofile_user;
ALTER TABLE accounts_customerprofile    DROP FOREIGN KEY fk_customerprofile_user;
ALTER TABLE catalog_vendor              DROP FOREIGN KEY fk_vendor_user;
ALTER TABLE cart_cart                   DROP FOREIGN KEY fk_cart_user;
ALTER TABLE orders_order                DROP FOREIGN KEY fk_order_user;
ALTER TABLE favorites_favoriteproduct   DROP FOREIGN KEY fk_favproduct_user;
ALTER TABLE favorites_favoritevendor    DROP FOREIGN KEY fk_favvendor_user;
DROP TABLE auth_user;

-- Section 2 — run AFTER `migrate` (re-points the FKs at the new auth_user)
-- ⚠️ The M0 schema used BIGINT UNSIGNED for user_id; Django's auth_user.id is INT.
--     All child tables must be altered first, and FOREIGN_KEY_CHECKS=0 is required
--     because the new auth_user is empty (existing user_id values have no match yet).
ALTER TABLE accounts_userprofile        MODIFY user_id int NOT NULL;
ALTER TABLE accounts_customerprofile    MODIFY user_id int NOT NULL;
ALTER TABLE cart_cart                   MODIFY user_id int NOT NULL;
ALTER TABLE catalog_vendor              MODIFY user_id int NOT NULL;
ALTER TABLE orders_order                MODIFY user_id int NOT NULL;
ALTER TABLE favorites_favoriteproduct   MODIFY user_id int NOT NULL;
ALTER TABLE favorites_favoritevendor    MODIFY user_id int NOT NULL;

SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE accounts_userprofile         ADD CONSTRAINT fk_userprofile_user        FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE accounts_customerprofile     ADD CONSTRAINT fk_customerprofile_user    FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE catalog_vendor               ADD CONSTRAINT fk_vendor_user             FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE cart_cart                    ADD CONSTRAINT fk_cart_user               FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE orders_order                 ADD CONSTRAINT fk_order_user              FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoriteproduct    ADD CONSTRAINT fk_favproduct_user         FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoritevendor     ADD CONSTRAINT fk_favvendor_user          FOREIGN KEY (user_id) REFERENCES auth_user (id);
SET FOREIGN_KEY_CHECKS=1;
```

3. Apply Section 1:

```powershell
cmd /c "mysql -u root -p ecompra < sql\04_auth_user_handover.sql"
```

   (It will error on Section 2 — that is expected; Section 2 is applied after `migrate`.)

4. Migrate — creates `auth_user` (real), `auth_group`, `auth_permission`, `django_session`,
   `django_content_type`, `django_admin_log`, `django_migrations` (18 migrations):

```powershell
python manage.py migrate
```

5. Apply Section 2 — simplest: save Section 2 alone as `sql/04b_auth_user_fks.sql` and run it:

```powershell
cmd /c "mysql -u root -p ecompra < sql\04b_auth_user_fks.sql"
```

6. Amend `sql/01_schema.sql`: **remove** the `auth_user` block (lines 14–34) and add the comment
   `-- auth_user is created by Django migrations (M2.6); see 04b_auth_user_fks.sql.`

**Expected result.** `migrate` reports applying 18 migrations; all FKs resolve again.

**Verify.** Run and paste:

```sql
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'ecompra';
SELECT COUNT(*) AS broken_fk FROM information_schema.key_column_usage
WHERE table_schema = 'ecompra' AND referenced_table_name IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM information_schema.tables t2
                WHERE t2.table_schema = 'ecompra' AND t2.table_name = information_schema.key_column_usage.referenced_table_name);
SELECT COUNT(*) FROM django_migrations;
```

Expected: `table_count` = 35 (28 domain + 7 Django), `broken_fk` = `0`, `django_migrations` = 18.

**If it fails.**
- `ERROR 3730 Cannot drop table referenced by a foreign key` → a child FK was missed in Section 1; the query in
  step 1 shows which.
- `ERROR 1824 Failed to open the referenced table 'auth_user'` in Section 2 → `migrate` did not run or did not
  create `auth_user`; check `python manage.py showmigrations`.
- `ERROR 3780 Referencing column 'user_id' and referenced column 'id' ... are incompatible` → child `user_id` is
  `BIGINT UNSIGNED` but `auth_user.id` is `INT`; run the `MODIFY user_id int NOT NULL` statements in Section 2.
- `ERROR 1452 Cannot add or update a child row` → `auth_user` is empty but child tables have `user_id` values;
  wrap Section 2 with `SET FOREIGN_KEY_CHECKS=0` / `SET FOREIGN_KEY_CHECKS=1`.
- `migrate` errors on an existing table → a `django_*` table already existed; tell the coach which.

> 📌 **CCS630 lesson — schema ownership must be explicit.** One table, one owner: the SQL scripts own the 27
> domain tables; Django's migrations own auth and sessions. Mixing owners on one table is how "works here,
> breaks there" bugs are born.

---

## Step M2.7 — ORM round-trip verification

**Goal.** Proof the models read the real seeded data: every count matches M0.9, and the tomato query reproduces correctly.

**Where.** `backend/` — `manage.py shell`.

**Actions.**

1. **Activate venv and start shell:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python manage.py shell
   ```

2. **Run the verification script in the shell:**
   ```python
   from catalog.models import Product, Vendor, Category
   from orders.models import TransactionStatus, PaymentStatus, DeliveryStatus, FulfillmentMethod, TransactionType
   from catalog.models import AvailabilityStatus, UnitOfMeasure

   print(TransactionStatus.objects.count(), PaymentStatus.objects.count(), DeliveryStatus.objects.count(),
         FulfillmentMethod.objects.count(), TransactionType.objects.count(), AvailabilityStatus.objects.count(),
         Category.objects.count(), Vendor.objects.count(), Product.objects.count())

   for p in (Product.objects.filter(name__istartswith="Tomato")
             .select_related("vendor", "unit_code", "availability_code").order_by("price")):
       print(p, "|", p.vendor.name, "|", p.price, "|", p.unit_code.code)
   ```

3. **Cross-check one relation end-to-end:**
   ```python
   v = Vendor.objects.get(name__contains="Villamor")
   print(v.product_set.count())
   from accounts.models import AuthUser
   print(AuthUser.objects.exists())   # Should be False (no users yet — just migrated)
   ```

**Expected result.** Counts exactly `7 4 5 3 3 4 9 6 34`; three tomato rows ₱75, ₱78, ₱80 in order; auth_user table empty (`False`).

**Verify.** Paste the shell output here.

**If it fails.**
- `ProgrammingError (1146): table doesn't exist` → a `db_table` is misspelled in M2.5.
- Wrong counts → pointed at wrong database; check `.env`.
- Tomato order differs → `.order_by("price")` must be present.
- `NameError: name 'User' is not defined` → project uses custom `AuthUser` in `accounts` app, not Django's built-in User.
- `FieldError: Invalid field name(s) given in select_related: 'unit'` → the FK field is named `unit_code` (matching `db_column`), not `unit`; use `select_related("unit_code", "availability_code")` and access via `p.unit_code.code`, `p.availability_code.code`.

> 📌 **CCS630 lesson — the ORM is a lens on the schema, not a replacement for it.** If the ORM and the seed data
> disagree, the bug is in the mapping — and this exact test is how you find it.

---

## Step M2.8 — Register the models in the admin

**Goal.** Every domain model visible and manageable in Django admin with useful columns matching actual model field names.

**Where.** `backend/<app>/admin.py` — editor.

**Actions.**

1. **Create `backend/accounts/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import AuthUser, Userprofile, Customerprofile

   @admin.register(AuthUser)
   class AuthUserAdmin(admin.ModelAdmin):
       list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
       list_filter = ("is_staff", "is_active", "is_superuser")
       search_fields = ("username", "email", "first_name", "last_name")
       readonly_fields = ("date_joined", "last_login", "password")

   @admin.register(Userprofile)
   class UserprofileAdmin(admin.ModelAdmin):
       list_display = ("user", "is_vendor", "created_at", "updated_at")
       list_filter = ("is_vendor",)

   @admin.register(Customerprofile)
   class CustomerprofileAdmin(admin.ModelAdmin):
       list_display = ("user", "phone", "created_at", "updated_at")
   ```

2. **Create `backend/catalog/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import (
       Product, Vendor, Category, UnitOfMeasure, ComparisonGroup,
       ComparisonGroupUnit, AvailabilityStatus, InventoryReason, InventoryMovement
   )

   @admin.register(Product)
   class ProductAdmin(admin.ModelAdmin):
       list_display = ("name", "vendor", "category", "price", "unit", "stock_quantity", "availability", "low_stock_threshold")
       list_filter = ("category", "availability", "vendor")
       search_fields = ("name",)
       readonly_fields = ("created_at", "updated_at")

   @admin.register(Vendor)
   class VendorAdmin(admin.ModelAdmin):
       list_display = ("name", "stall_location", "market_section", "contact_phone", "contact_email", "is_active", "user")
       list_filter = ("is_active",)
       search_fields = ("name", "stall_location", "contact_email")
       readonly_fields = ("created_at", "updated_at")

   @admin.register(Category)
   class CategoryAdmin(admin.ModelAdmin):
       list_display = ("name", "slug", "is_active", "created_at", "updated_at")
       prepopulated_fields = {}
       search_fields = ("name",)

   @admin.register(UnitOfMeasure)
   class UnitOfMeasureAdmin(admin.ModelAdmin):
       list_display = ("code", "name", "is_active")
       search_fields = ("code", "name")

   @admin.register(ComparisonGroup)
   class ComparisonGroupAdmin(admin.ModelAdmin):
       list_display = ("code", "name", "base_unit", "is_active")
       search_fields = ("code", "name")

   admin.site.register(ComparisonGroupUnit)
   admin.site.register(AvailabilityStatus)
   admin.site.register(InventoryReason)
   admin.site.register(InventoryMovement)
   ```

3. **Create `backend/cart/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import Cart, CartItem

   @admin.register(Cart)
   class CartAdmin(admin.ModelAdmin):
       list_display = ("user", "created_at")
       search_fields = ("user__username",)

   @admin.register(CartItem)
   class CartItemAdmin(admin.ModelAdmin):
       list_display = ("cart", "product", "quantity", "created_at")
       list_filter = ("cart__user",)
       search_fields = ("product__name",)
   ```

4. **Create `backend/orders/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import (
       Order, OrderItem, Transaction, Payment, DeliveryBooking,
       TransactionStatus, TransactionType, PaymentStatus, DeliveryStatus, FulfillmentMethod
   )

   @admin.register(Order)
   class OrderAdmin(admin.ModelAdmin):
       list_display = ("id", "user", "customer_label", "vendor", "status", "fulfillment", "total_amount", "created_at")
       list_filter = ("status", "fulfillment", "vendor")
       search_fields = ("id", "user__username", "customer_label", "vendor__name")
       readonly_fields = ("created_at", "updated_at")

   @admin.register(OrderItem)
   class OrderItemAdmin(admin.ModelAdmin):
       list_display = ("order", "product", "quantity", "unit_price")
       search_fields = ("order__id", "product__name")

   @admin.register(Transaction)
   class TransactionAdmin(admin.ModelAdmin):
       list_display = ("id", "order", "transaction_type", "reference_no", "created_at")
       search_fields = ("reference_no", "order__id")

   @admin.register(Payment)
   class PaymentAdmin(admin.ModelAdmin):
       list_display = ("id", "transaction", "provider", "amount", "status", "paid_at")
       list_filter = ("status", "provider")
       search_fields = ("provider_reference",)

   @admin.register(DeliveryBooking)
   class DeliveryBookingAdmin(admin.ModelAdmin):
       list_display = ("id", "transaction", "provider", "booking_reference", "status", "fee", "delivered_at")
       list_filter = ("status", "provider")
       search_fields = ("booking_reference",)

   admin.site.register(TransactionStatus)
   admin.site.register(TransactionType)
   admin.site.register(PaymentStatus)
   admin.site.register(DeliveryStatus)
   admin.site.register(FulfillmentMethod)
   ```

5. **Create `backend/vendors/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import PosVendor, VendorTransaction

   @admin.register(PosVendor)
   class PosVendorAdmin(admin.ModelAdmin):
       list_display = ("catalog_vendor", "stall_name", "stall_location")
       search_fields = ("stall_name", "catalog_vendor__name")

   @admin.register(VendorTransaction)
   class VendorTransactionAdmin(admin.ModelAdmin):
       list_display = ("id", "vendor", "order", "status", "receipt_serial", "receipt_attempt", "created_at")
       list_filter = ("status",)
       search_fields = ("receipt_serial", "order__id")
   ```

6. **Create `backend/favorites/admin.py`:**
   ```python
   from django.contrib import admin
   from .models import FavoriteProduct, FavoriteVendor

   @admin.register(FavoriteProduct)
   class FavoriteProductAdmin(admin.ModelAdmin):
       list_display = ("user", "product", "created_at")
       search_fields = ("user__username", "product__name")

   @admin.register(FavoriteVendor)
   class FavoriteVendorAdmin(admin.ModelAdmin):
       list_display = ("user", "vendor", "created_at")
       search_fields = ("user__username", "vendor__name")
   ```

**Expected result.** `/admin/` lists all 27 domain models grouped by app with useful columns.

**Verify.** Run and paste:

```powershell
Select-String -Path accounts\admin.py,catalog\admin.py,cart\admin.py,orders\admin.py,vendors\admin.py,favorites\admin.py -Pattern "register" | Measure-Object -Line
```

Expected: ≥ 27 register lines (3 accounts + 9 catalog + 2 cart + 10 orders + 2 vendors + 2 favorites = 28, but some use `admin.site.register`).

**If it fails.**
- `AdminSite already registered` → a model registered twice; remove the duplicate.
- `list_display` field error → the field name does not exist on the model; check M2.5's actual field names (e.g., `availability` not `availability_code`, `unit` not `unit_code`).
- `ImproperlyConfigured: ModelAdmin` → missing `list_display` tuple comma on single item.

> 📌 **CCS630 lesson — admin is the cheapest CRUD proof.** Before a single API exists, the admin demonstrates the
> full read/write path to every table — and later it is your data-fixing tool during the defense demo.

---

## Step M2.9 — Superuser + admin walkthrough

**Goal.** A superuser account in Django's `auth_user`, and a click-through of the seeded data in the admin proving read/write on `managed = False` tables.

**Where.** `backend/` — PowerShell, browser.

**Actions.**

1. **Activate venv and create the superuser:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python manage.py createsuperuser
   ```
   - Username: `admin`
   - Email: your email
   - Password: a password you will remember for the defense (e.g., `Admin2627`)
   - If prompted "Superuser creation skipped" → answer `no` and provide valid username.

2. **Start server and open admin:**
   ```powershell
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/admin/`, log in with `admin` / your password.

3. **Walk and confirm each section:**
   - **Catalog → Products** → shows **34** seeded products; prices display **₱** correctly (no `?` or mojibake)
   - **Catalog → Vendors** → shows **6** seeded vendors with stall locations
   - **Catalog → Categories** → shows **9** categories
   - **Catalog → Units of measure** → shows **4** units (KG, PC, G, ML)
   - **Orders → Orders** → empty (no orders yet — correct)
   - **Auth → Users** → shows only `admin` (the superuser you just created)
   - **Auth → Groups / Permissions** → Django's built-in auth tables populated by migrations

4. **Prove write access on a managed=False table:**
   - Go to **Catalog → Units of measure → Add**
   - Enter: Code=`doz`, Name=`Dozen`, Description=`Twelve pieces`, Is_active=✓
   - Save → row appears in list
   - Select the `doz` row → Delete → confirm → row removed
   - This proves the ORM can write to SQL-managed tables.

**Expected result.** Admin login works; all seeded data renders with ₱ intact; add/delete works on managed=False table.

**Verify.** Paste:
- Admin Products list count (should show **34**)
- Confirm ₱ sign renders correctly (not `?` or `â€¡`)
- Confirm Units of measure add/delete worked

**If it fails.**
- `Superuser creation skipped` → answer `no` to the "bypass" prompt and provide a valid username.
- ₱ renders as `?` or garbled → the connection charset is wrong; check `DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'` in `config/settings.py` (M2.3).
- `ProgrammingError (1146)` on a table → `db_table` misspelled in M2.5.
- "Table 'ecompra.django_admin_log' doesn't exist" → migrations didn't run; run `python manage.py migrate`.

> 📌 **CCS630 lesson — utf8mb4 end to end.** The ₱ sign survived schema → seed → ORM → admin. One non-utf8mb4 hop
> anywhere would have mangled it; this walkthrough is the check.

---

## Step M2.10 — DRF + core serializers

**Goal.** REST framework installed and serializers for all customer-facing read models using correct FK field names from M2.5 models.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. **Activate venv and install (unpinned; versions get frozen in M2.17):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install djangorestframework
   ```

2. **Edit `backend/config/settings.py`:** add `"rest_framework"` to `INSTALLED_APPS`.

3. **Create `backend/catalog/serializers.py`:**
   ```python
   from rest_framework import serializers
   from .models import Product, Category, Vendor, UnitOfMeasure, AvailabilityStatus

   class CategorySerializer(serializers.ModelSerializer):
       class Meta:
           model = Category
           fields = ("id", "name", "slug")

   class VendorSerializer(serializers.ModelSerializer):
       class Meta:
           model = Vendor
           fields = ("id", "name", "stall_location", "market_section", "contact_phone", "contact_email")

   class ProductSerializer(serializers.ModelSerializer):
       vendor = VendorSerializer(read_only=True)
       category = CategorySerializer(read_only=True)
       unit = serializers.CharField(source="unit_code.code", read_only=True)
       availability = serializers.CharField(source="availability_code.code", read_only=True)

       class Meta:
           model = Product
           fields = ("id", "name", "description", "image_url", "vendor", "category", "unit", "price",
                     "stock_quantity", "low_stock_threshold", "availability", "stall_location", "comparison_group")

   class UnitOfMeasureSerializer(serializers.ModelSerializer):
       class Meta:
           model = UnitOfMeasure
           fields = ("code", "name", "description")

   class AvailabilityStatusSerializer(serializers.ModelSerializer):
       class Meta:
           model = AvailabilityStatus
           fields = ("code", "description", "is_orderable")
   ```

4. **Create `backend/orders/serializers.py`:**
   ```python
   from rest_framework import serializers
   from .models import (
       Order, OrderItem, Transaction, Payment, DeliveryBooking,
       TransactionStatus, TransactionType, PaymentStatus, DeliveryStatus, FulfillmentMethod
   )

   class TransactionStatusSerializer(serializers.ModelSerializer):
       class Meta:
           model = TransactionStatus
           fields = ("code", "description")

   class TransactionTypeSerializer(serializers.ModelSerializer):
       class Meta:
           model = TransactionType
           fields = ("code", "description")

   class PaymentStatusSerializer(serializers.ModelSerializer):
       class Meta:
           model = PaymentStatus
           fields = ("code", "description", "is_terminal")

   class DeliveryStatusSerializer(serializers.ModelSerializer):
       class Meta:
           model = DeliveryStatus
           fields = ("code", "description", "is_terminal")

   class FulfillmentMethodSerializer(serializers.ModelSerializer):
       class Meta:
           model = FulfillmentMethod
           fields = ("code", "description")

   class OrderItemSerializer(serializers.ModelSerializer):
       product_name = serializers.CharField(source="product.name", read_only=True)
       class Meta:
           model = OrderItem
           fields = ("id", "product", "product_name", "quantity", "unit_price")

   class TransactionSerializer(serializers.ModelSerializer):
       class Meta:
           model = Transaction
           fields = ("id", "order", "transaction_type", "reference_no", "created_at")

   class PaymentSerializer(serializers.ModelSerializer):
       class Meta:
           model = Payment
           fields = ("id", "transaction", "provider", "provider_reference", "amount", "status", "paid_at")

   class DeliveryBookingSerializer(serializers.ModelSerializer):
       class Meta:
           model = DeliveryBooking
           fields = ("id", "transaction", "provider", "booking_reference", "tracking_url", "fee", "status", "booked_at", "delivered_at")

   class OrderSerializer(serializers.ModelSerializer):
       items = OrderItemSerializer(many=True, read_only=True)
       transaction = TransactionSerializer(read_only=True)
       status_display = serializers.CharField(source="status.description", read_only=True)
       fulfillment_display = serializers.CharField(source="fulfillment.description", read_only=True)

       class Meta:
           model = Order
           fields = ("id", "user", "customer_label", "vendor", "status", "status_display",
                     "fulfillment", "fulfillment_display", "total_amount", "notes",
                     "created_at", "updated_at", "items", "transaction")
   ```

5. **Create `backend/vendors/serializers.py`:**
   ```python
   from rest_framework import serializers
   from .models import PosVendor, VendorTransaction

   class PosVendorSerializer(serializers.ModelSerializer):
       catalog_vendor_name = serializers.CharField(source="catalog_vendor.name", read_only=True)
       class Meta:
           model = PosVendor
           fields = ("catalog_vendor", "catalog_vendor_name", "stall_name", "stall_location")

   class VendorTransactionSerializer(serializers.ModelSerializer):
       class Meta:
           model = VendorTransaction
           fields = ("id", "vendor", "order", "status", "receipt_serial", "receipt_attempt", "created_at")
   ```

6. **Create `backend/favorites/serializers.py`:**
   ```python
   from rest_framework import serializers
   from .models import FavoriteProduct, FavoriteVendor
   from catalog.serializers import ProductSerializer, VendorSerializer

   class FavoriteProductSerializer(serializers.ModelSerializer):
       product = ProductSerializer(read_only=True)
       class Meta:
           model = FavoriteProduct
           fields = ("id", "product", "created_at")

   class FavoriteVendorSerializer(serializers.ModelSerializer):
       vendor = VendorSerializer(read_only=True)
       class Meta:
           model = FavoriteVendor
           fields = ("id", "vendor", "created_at")
   ```

**Expected result.** DRF installed; all serializer files import cleanly.

**Verify.**
```powershell
python manage.py shell -c "
from catalog.serializers import ProductSerializer, CategorySerializer, VendorSerializer
from orders.serializers import OrderSerializer, TransactionStatusSerializer
from vendors.serializers import PosVendorSerializer
from favorites.serializers import FavoriteProductSerializer
print('catalog serializers ok')
print('orders serializers ok')
print('vendors serializers ok')
print('favorites serializers ok')
"
```
Expected: all four lines print.

**If it fails.**
- `source="unit.code"` errors → the FK field name on the model differs; check M2.5 (should be `unit` not `unit_code`, `availability` not `availability_code`).
- `ImproperlyConfigured: Could not resolve URL` → `rest_framework` not in `INSTALLED_APPS`.
- Circular import → use string references in serializer relations or import inside method.

> 📌 **CCS630 lesson — the serializer is the API contract.** It decides exactly which columns leave the database —
> the API version of choosing a projection in SQL.

---

## Step M2.11 — Read-only API views

**Goal.** List/detail endpoints for products, categories, vendors — the customer browse path. Plus lookup endpoints for orders.

**Where.** `backend/catalog/views.py`, `backend/orders/views.py`, `backend/vendors/views.py` — editor.

**Actions.**

1. **Create `backend/catalog/views.py`:**
   ```python
   from django.db.models import Q
   from rest_framework import generics
   from .models import Product, Category, Vendor, UnitOfMeasure, AvailabilityStatus
   from .serializers import ProductSerializer, CategorySerializer, VendorSerializer, UnitOfMeasureSerializer, AvailabilityStatusSerializer

   class ProductList(generics.ListAPIView):
       serializer_class = ProductSerializer

       def get_queryset(self):
           qs = (Product.objects.filter(availability_code__is_orderable=True)
                 .select_related("vendor", "category", "unit_code", "availability_code"))
           q = self.request.query_params.get("q")
           cat = self.request.query_params.get("category")
           if q:
               qs = qs.filter(Q(name__icontains=q) | Q(vendor__name__icontains=q))
           if cat:
               qs = qs.filter(category__slug=cat)
           return qs.order_by("name")

   class ProductDetail(generics.RetrieveAPIView):
       queryset = Product.objects.select_related("vendor", "category", "unit_code", "availability_code")
       serializer_class = ProductSerializer

   class CategoryList(generics.ListAPIView):
       queryset = Category.objects.filter(is_active=True)
       serializer_class = CategorySerializer

   class VendorList(generics.ListAPIView):
       queryset = Vendor.objects.all()
       serializer_class = VendorSerializer

   class UnitOfMeasureList(generics.ListAPIView):
       queryset = UnitOfMeasure.objects.filter(is_active=True)
       serializer_class = UnitOfMeasureSerializer

   class AvailabilityStatusList(generics.ListAPIView):
       queryset = AvailabilityStatus.objects.filter(is_orderable=True)
       serializer_class = AvailabilityStatusSerializer
   ```

2. **Create `backend/orders/views.py`:**
   ```python
   from rest_framework import generics
   from .models import (
       TransactionStatus, TransactionType, PaymentStatus,
       DeliveryStatus, FulfillmentMethod
   )
   from .serializers import (
       TransactionStatusSerializer, TransactionTypeSerializer,
       PaymentStatusSerializer, DeliveryStatusSerializer, FulfillmentMethodSerializer
   )

   class TransactionStatusList(generics.ListAPIView):
       queryset = TransactionStatus.objects.all()
       serializer_class = TransactionStatusSerializer

   class TransactionTypeList(generics.ListAPIView):
       queryset = TransactionType.objects.all()
       serializer_class = TransactionTypeSerializer

   class PaymentStatusList(generics.ListAPIView):
       queryset = PaymentStatus.objects.all()
       serializer_class = PaymentStatusSerializer

   class DeliveryStatusList(generics.ListAPIView):
       queryset = DeliveryStatus.objects.all()
       serializer_class = DeliveryStatusSerializer

   class FulfillmentMethodList(generics.ListAPIView):
       queryset = FulfillmentMethod.objects.all()
       serializer_class = FulfillmentMethodSerializer
   ```

3. **Create `backend/vendors/views.py`:**
   ```python
   from rest_framework import generics
   from .models import PosVendor
   from .serializers import PosVendorSerializer

   class PosVendorList(generics.ListAPIView):
       queryset = PosVendor.objects.select_related("catalog_vendor")
       serializer_class = PosVendorSerializer
   ```

4. **Create `backend/favorites/views.py`:**
   ```python
   from rest_framework import generics
   from .models import FavoriteProduct, FavoriteVendor
   from .serializers import FavoriteProductSerializer, FavoriteVendorSerializer

   class FavoriteProductList(generics.ListAPIView):
       serializer_class = FavoriteProductSerializer

       def get_queryset(self):
           return FavoriteProduct.objects.filter(user=self.request.user).select_related("product")

   class FavoriteVendorList(generics.ListAPIView):
       serializer_class = FavoriteVendorSerializer

       def get_queryset(self):
           return FavoriteVendor.objects.filter(user=self.request.user).select_related("vendor")
   ```

**Expected result.** 13 working read-only views across 4 apps (6 catalog + 5 orders + 1 vendors + 2 favorites).

**Verify.**
```powershell
Select-String -Path catalog\views.py,orders\views.py,vendors\views.py,favorites\views.py -Pattern "^class " | Measure-Object -Line
```
Expected: 13 classes.

**If it fails.**
- `is_orderable` unknown → field lives on `AvailabilityStatus` model; the related name traverses `availability__is_orderable`.
- `select_related` field error → check FK field names in M2.5 (e.g., `unit` not `unit_code`, `availability` not `availability_code`).
- `request.user` in favorites → requires authentication (JWT from M2.14); for now use `AllowAny` or skip favorites views until M2.14.

> 📌 **CCS630 lesson — search is a query plan.** `?q=` becomes a `LIKE %…%` over `catalog_product.name` — the
> exact query `ix_product_name` (M0.8) was built to serve. You will `EXPLAIN` this in M4.

---

## Step M2.12 — URLs + browsable API root

**Goal.** A tidy URL tree under `/api/` with all app endpoints included, and a working browsable API.

**Where.** `backend/config/urls.py`, `backend/catalog/urls.py`, `backend/orders/urls.py`, `backend/vendors/urls.py`, `backend/favorites/urls.py`.

**Actions.**

1. **Create `backend/catalog/urls.py`:**
   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path("products/", views.ProductList.as_view(), name="product-list"),
       path("products/<int:pk>/", views.ProductDetail.as_view(), name="product-detail"),
       path("categories/", views.CategoryList.as_view(), name="category-list"),
       path("vendors/", views.VendorList.as_view(), name="vendor-list"),
       path("units/", views.UnitOfMeasureList.as_view(), name="unit-list"),
       path("availability/", views.AvailabilityStatusList.as_view(), name="availability-list"),
   ]
   ```

2. **Create `backend/orders/urls.py`:**
   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path("transaction-statuses/", views.TransactionStatusList.as_view(), name="transaction-status-list"),
       path("transaction-types/", views.TransactionTypeList.as_view(), name="transaction-type-list"),
       path("payment-statuses/", views.PaymentStatusList.as_view(), name="payment-status-list"),
       path("delivery-statuses/", views.DeliveryStatusList.as_view(), name="delivery-status-list"),
       path("fulfillment-methods/", views.FulfillmentMethodList.as_view(), name="fulfillment-method-list"),
   ]
   ```

3. **Create `backend/vendors/urls.py`:**
   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path("pos-vendors/", views.PosVendorList.as_view(), name="pos-vendor-list"),
   ]
   ```

4. **Create `backend/favorites/urls.py`:**
   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path("products/", views.FavoriteProductList.as_view(), name="favorite-product-list"),
       path("vendors/", views.FavoriteVendorList.as_view(), name="favorite-vendor-list"),
   ]
   ```

5. **Edit `backend/config/urls.py`:**
   ```python
   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("api/catalog/", include("catalog.urls")),
       path("api/orders/", include("orders.urls")),
       path("api/vendors/", include("vendors.urls")),
       path("api/favorites/", include("favorites.urls")),
   ]
   ```

6. **Run server and verify:**
   ```powershell
   python manage.py runserver
   ```
   Open in browser:
   - `http://127.0.0.1:8000/api/catalog/products/` → JSON list (DRF browsable UI)
   - `http://127.0.0.1:8000/api/catalog/products/?q=tomato` → filtered (3 tomato products, sorted by name)
   - `http://127.0.0.1:8000/api/catalog/products/1/` → detail
   - `http://127.0.0.1:8000/api/catalog/categories/` → 9 categories
   - `http://127.0.0.1:8000/api/catalog/vendors/` → 6 vendors
   - `http://127.0.0.1:8000/api/orders/transaction-statuses/` → 7 statuses
   - `http://127.0.0.1:8000/api/orders/fulfillment-methods/` → 3 methods
   - `http://127.0.0.1:8000/api/vendors/pos-vendors/` → 6 POS vendors

**Expected result.** All endpoints return real seeded data with ₱ intact.

**Verify.** Paste the JSON of `api/catalog/products/?q=tomato` (should include three tomato products).

**If it fails.**
- `No module named catalog.urls` → the file name is `urls.py` inside the app folder, not the project.
- `ModuleNotFoundError: No module named 'orders'` → check `INSTALLED_APPS` includes all 6 apps.
- 404 on an endpoint → check `include()` path matches the app's `urls.py` location.

> 📌 **CCS630 lesson — the API is the mockup's backend twin.** Each mockup screen from M0.10 names the data it
> needs; these endpoints are where that data starts to exist for real.

---

## Step M2.13 — OpenAPI schema + Swagger UI

**Goal.** Machine-readable API documentation, auto-generated from all endpoints.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. **Activate venv and install:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install drf-spectacular
   ```

2. **Edit `backend/config/settings.py`:**
   - Add `"drf_spectacular"` to `INSTALLED_APPS` (after `rest_framework`)
   - Add at the end of the file:
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
   }

   SPECTACULAR_SETTINGS = {
       "TITLE": "E-Compra API",
       "DESCRIPTION": "Public-market marketplace — CCS630 capstone",
       "VERSION": "0.1.0",
       "SERVE_INCLUDE_SCHEMA": False,
       "COMPONENT_SPLIT_REQUEST": True,
       "SCHEMA_PATH_PREFIX": "/api/",
   }
   ```

3. **Edit `backend/config/urls.py`:**
   ```python
   from django.contrib import admin
   from django.urls import path, include
   from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("api/catalog/", include("catalog.urls")),
       path("api/orders/", include("orders.urls")),
       path("api/vendors/", include("vendors.urls")),
       path("api/favorites/", include("favorites.urls")),
       # OpenAPI schema & docs
       path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
       path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
       path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
   ]
   ```

4. **Run server and verify:**
   ```powershell
   python manage.py runserver
   ```
   Open:
   - `http://127.0.0.1:8000/api/schema/swagger-ui/` → Swagger UI with all endpoints
   - `http://127.0.0.1:8000/api/schema/redoc/` → ReDoc alternative
   - `http://127.0.0.1:8000/api/schema/` → Raw OpenAPI 3.0 JSON

**Expected result.** Swagger UI renders with all 13 endpoints listed under catalog/orders/vendors/favorites.

**Verify.** Paste confirmation that Swagger UI loads and shows:
- `/api/catalog/products/` (GET, GET by ID)
- `/api/catalog/categories/`
- `/api/catalog/vendors/`
- `/api/catalog/units/`
- `/api/catalog/availability/`
- `/api/orders/transaction-statuses/`
- `/api/orders/transaction-types/`
- `/api/orders/payment-statuses/`
- `/api/orders/delivery-statuses/`
- `/api/orders/fulfillment-methods/`
- `/api/vendors/pos-vendors/`
- `/api/favorites/products/` (requires auth - will show 401)
- `/api/favorites/vendors/` (requires auth - will show 401)

**If it fails.**
- `spec invalid` warnings → note them; usually a serializer without a model field mapping or missing `fields`.
- `ImproperlyConfigured: Could not resolve URL` → `drf_spectacular` not in `INSTALLED_APPS` or `REST_FRAMEWORK` dict missing.
- Empty schema → `SCHEMA_PATH_PREFIX` doesn't match your URL pattern; adjust to `/api/`.

> 📌 **CCS630 lesson — documentation that cannot drift.** The schema is generated from the code; a stale API doc
> becomes impossible.

---

## Step M2.14 — CORS + SimpleJWT

**Goal.** CORS configured for future Vue frontend (localhost:5173); JWT authentication via SimpleJWT using Django's `auth_user` table (created in M2.6).

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. **Activate venv and install:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install django-cors-headers djangorestframework-simplejwt
   ```

2. **Edit `backend/config/settings.py`:**
   - Add to `INSTALLED_APPS` (order matters — `corsheaders` before `django.contrib.auth`):
     ```python
     INSTALLED_APPS = [
         "corsheaders",
         "rest_framework",
         "drf_spectacular",
         "django.contrib.admin",
         "django.contrib.auth",
         "django.contrib.contenttypes",
         "django.contrib.sessions",
         "django.contrib.messages",
         "django.contrib.staticfiles",
         # local apps
         "accounts",
         "catalog",
         "cart",
         "orders",
         "vendors",
         "favorites",
     ]
     ```
   - Add to `MIDDLEWARE` — **`CorsMiddleware` must be above `CommonMiddleware`:**
     ```python
     MIDDLEWARE = [
         "corsheaders.middleware.CorsMiddleware",
         "django.middleware.security.SecurityMiddleware",
         "django.contrib.sessions.middleware.SessionMiddleware",
         "django.middleware.common.CommonMiddleware",
         "django.middleware.csrf.CsrfViewMiddleware",
         "django.contrib.auth.middleware.AuthenticationMiddleware",
         "django.contrib.messages.middleware.MessageMiddleware",
         "django.middleware.clickjacking.XFrameOptionsMiddleware",
     ]
     ```
   - Add CORS settings:
     ```python
     CORS_ALLOWED_ORIGINS = [
         "http://localhost:5173",
         "http://127.0.0.1:5173",
     ]
     CORS_ALLOW_CREDENTIALS = True
     ```
   - Update `REST_FRAMEWORK` to include JWT authentication:
     ```python
     from datetime import timedelta

     REST_FRAMEWORK = {
         "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
         "DEFAULT_AUTHENTICATION_CLASSES": (
             "rest_framework_simplejwt.authentication.JWTAuthentication",
         ),
     }

     SIMPLE_JWT = {
         "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
         "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
         "ROTATE_REFRESH_TOKENS": True,
         "BLACKLIST_AFTER_ROTATION": True,
         "AUTH_HEADER_TYPES": ("Bearer",),
     }
     ```

3. **Edit `backend/config/urls.py`:**
   ```python
   from django.contrib import admin
   from django.urls import path, include
   from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
   from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("api/catalog/", include("catalog.urls")),
       path("api/orders/", include("orders.urls")),
       path("api/vendors/", include("vendors.urls")),
       path("api/favorites/", include("favorites.urls")),
       # OpenAPI schema & docs
       path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
       path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
       path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
       # JWT auth
       path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
       path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
   ]
   ```

4. **Run server and test JWT:**
   ```powershell
   python manage.py runserver
   ```
   In a **new PowerShell window** (keep server running):
   ```powershell
   $body = '{"username":"admin","password":"Admin2627"}'
   Invoke-RestMethod -Uri http://127.0.0.1:8000/api/token/ -Method Post -ContentType "application/json" -Body $body
   ```
   Expected: JSON with `access` and `refresh` keys (do not paste tokens).

5. **Test authenticated request:**
   ```powershell
   $token = "<paste_access_token_from_above>"
   $headers = @{ Authorization = "Bearer $token" }
   Invoke-RestMethod -Uri http://127.0.0.1:8000/api/favorites/products/ -Headers $headers
   ```
   Should return `[]` (empty list for new user) or 200 OK.

**Expected result.** POST `/api/token/` returns `access` + `refresh`; authenticated requests work.

**Verify.** Paste confirmation that:
- Token endpoint returns both keys
- Authenticated request to `/api/favorites/products/` returns 200 (not 401)

**If it fails.**
- 401 Unauthorized → wrong credentials; superuser must exist in `auth_user` (M2.9).
- 404 Not Found → URLs not saved or server not restarted.
- `corsheaders` import error → middleware order; `CorsMiddleware` must be **first** or above `CommonMiddleware`.
- `AttributeError: 'User' object has no attribute '...'` → SimpleJWT uses Django's `auth_user`; our custom `AuthUser` is mapped to that table via `db_table='auth_user'` so it works.

> 📌 **CCS630 lesson — CORS is the browser's rule, JWT is yours.** CORS protects the *user's* browser from other
> sites; JWT is how *your* API knows who is calling. Both will be load-bearing in M3.

---

## Step M2.15 — pytest + first database tests

**Goal.** A test runner wired to Django, with a seeded test database (cloned from `ecompra`), proving the schema and seed data invariants from the test side.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. **Activate venv and install:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install pytest pytest-django
   ```

2. **Create `backend/pytest.ini`:**
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = config.settings
   python_files = test_*.py
   python_functions = test_*
   addopts = --reuse-db -v
   ```

3. **Create the test database as a clone of `ecompra`** (migrations only know Django's tables; the 27 domain tables are SQL-managed, so the test DB inherits them by clone):
   ```powershell
   cmd /c 'mysql -u root -p -e "DROP DATABASE IF EXISTS test_ecompra; CREATE DATABASE test_ecompra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
   cmd /c "mysqldump -u root -p ecompra > ..\backups\test_seed.sql"
   cmd /c 'mysql -u root -p test_ecompra < ..\backups\test_seed.sql'
   ```
   (`backups/` is gitignored — the dump must never be committed.)

4. **Edit `backend/config/settings.py`** — add at the end:
   ```python
   import sys
   if "pytest" in sys.modules:
       DATABASES["default"]["NAME"] = "test_ecompra"
   ```

5. **Create `backend/catalog/test_catalog.py`:**
   ```python
   import pytest
   from catalog.models import Product, Category, Vendor, UnitOfMeasure, AvailabilityStatus

   @pytest.mark.django_db
   def test_seed_counts():
       assert Product.objects.count() == 34
       assert Category.objects.count() == 9
       assert Vendor.objects.count() == 6
       assert UnitOfMeasure.objects.count() == 4
       assert AvailabilityStatus.objects.count() == 4

   @pytest.mark.django_db
   def test_tomato_price_comparison():
       rows = list(Product.objects.filter(name__istartswith="Tomato").order_by("price"))
       assert [r.price for r in rows] == [75, 78, 80]

   @pytest.mark.django_db
   def test_vendor_products_relation():
       villamor = Vendor.objects.get(name__contains="Villamor")
       assert villamor.product_set.count() >= 3  # seeded products
   ```

6. **Create `backend/orders/test_orders.py`:**
   ```python
   import pytest
   from orders.models import (
       TransactionStatus, PaymentStatus, DeliveryStatus,
       FulfillmentMethod, TransactionType
   )

   @pytest.mark.django_db
   def test_lookup_table_counts():
       assert TransactionStatus.objects.count() == 7
       assert PaymentStatus.objects.count() == 4
       assert DeliveryStatus.objects.count() == 5
       assert FulfillmentMethod.objects.count() == 3
       assert TransactionType.objects.count() == 3

   @pytest.mark.django_db
   def test_terminal_statuses():
       # At least one terminal status per type
       assert PaymentStatus.objects.filter(is_terminal=True).exists()
       assert DeliveryStatus.objects.filter(is_terminal=True).exists()
   ```

6. **Create `backend/orders/test_orders.py`:**
   ```python
   import pytest
   from orders.models import (
       TransactionStatus, PaymentStatus, DeliveryStatus,
       FulfillmentMethod, TransactionType
   )

   @pytest.mark.django_db
   def test_lookup_table_counts():
       assert TransactionStatus.objects.count() == 7
       assert PaymentStatus.objects.count() == 4
       assert DeliveryStatus.objects.count() == 5
       assert FulfillmentMethod.objects.count() == 3
       assert TransactionType.objects.count() == 3

   @pytest.mark.django_db
   def test_terminal_statuses():
       # At least one terminal status per type
       assert PaymentStatus.objects.filter(is_terminal=True).exists()
       assert DeliveryStatus.objects.filter(is_terminal=True).exists()
   ```

7. **Run tests from `backend/` folder:**
   ```powershell
   pytest
   ```

**Expected result.** 7 tests passed (5 catalog + 2 orders).

**Verify.** Paste the pytest summary line (e.g., `7 passed in 2.34s`).

**If it fails.**
- `pytest` collects 0 tests → `pytest.ini` not in the folder pytest runs from; run from `backend/`.
- `(1146) table doesn't exist` in tests → step 3's clone was skipped or pointed at the wrong dump; verify `test_ecompra` exists and has tables.
- `--reuse-db` keeps an old schema → drop `test_ecompra` (step 3) and re-clone.
- `ModuleNotFoundError` on models → check app is in `INSTALLED_APPS`.
- `django.db.utils.OperationalError: (1049, "Unknown database 'test_ecompra'")` → step 3 failed; re-run clone commands.

> 📌 **CCS630 lesson — test the invariant, not the implementation.** "34 products, tomato 75/78/80" is the seed
> contract from M0.9, now enforced forever by CI-able tests.

---

## Step M2.16 — ruff lint pass

**Goal.** A configured linter and a clean codebase with consistent style.

**Where.** Project root — PowerShell.

**Actions.**

1. **Activate venv and install:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install ruff
   ```

2. **Create `ruff.toml` at the project root:**
   ```toml
   line-length = 110
   exclude = [".venv", "backups", "tools", "backend/config/migrations", "backend/accounts/migrations", "backend/catalog/migrations", "backend/cart/migrations", "backend/orders/migrations", "backend/vendors/migrations", "backend/favorites/migrations"]

   [lint]
   select = ["E", "F", "W", "I", "UP", "B", "C4", "T20"]
   ignore = ["E501"]  # line-too-long handled by line-length

   [format]
   quote-style = "double"
   indent-style = "space"
   skip-magic-trailing-comma = false
   ```

3. **Run and fix:**
   ```powershell
   ruff check backend --fix
   ruff format backend
   ruff check backend
   ```

**Expected result.** `All checks passed!`

**Verify.** Paste the final `ruff check backend` output.

**If it fails.**
- Long lines in migrations → migrations are excluded in `ruff.toml`.
- `T20` (print found) → remove debug `print()` statements or add `# noqa: T20`.
- `UP` (pyupgrade) suggestions → apply with `--fix` or manually modernize (e.g., `super()` without args).
- `B` (bugbear) findings → review and fix; these catch real bugs like unused loop variables.

> 📌 **CCS630 lesson — lint is a review you get for free.** The import sorting alone (`I`) prevents a whole class
> of circular-import bugs in Django apps.

---

## Step M2.17 — Freeze requirements, `.gitattributes`, backend README

**Goal.** The exact environment recorded; line-ending noise ended; backend documented for handover.

**Where.** Project root, `backend/` — PowerShell, editor.

**Actions.**

1. **Activate venv and freeze exact versions for all project dependencies:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip freeze | Select-String -Pattern "asgiref|Django|sqlparse|PyMySQL|python-dotenv|djangorestframework|drf-spectacular|django-cors|PyJWT|pytest|ruff|typing-extensions|tzdata"
   ```
   Add those `name==version` lines to root `requirements.txt` (merge with existing, do not duplicate). Expected packages:
   - `Django==6.1.3`
   - `djangorestframework==3.18.3`
   - `drf-spectacular==0.28.0` (or latest compatible)
   - `django-cors-headers==4.7.0` (or latest)
   - `djangorestframework-simplejwt==5.5.0` (or latest)
   - `PyMySQL==1.2.4`
   - `python-dotenv==1.2.4`
   - `pytest==8.3.0` (or latest)
   - `pytest-django==4.8.0` (or latest)
   - `ruff==0.6.0` (or latest)
   - Plus transitive: `asgiref`, `sqlparse`, `tzdata`, `typing-extensions`, `PyJWT`, `packaging`

2. **Create `.gitattributes` at the project root** (ends LF/CRLF warnings from M1.9):
   ```gitattributes
   * text=auto
   *.sql text
   *.py text
   *.md text
   *.txt text
   *.toml text
   *.ini text
   ```

3. **Create `backend/README.md`:**
   ```markdown
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
   ```

**Expected result.** Pinned env reproducible from `requirements.txt` alone; `.gitattributes` ends line-ending noise; `backend/README.md` documents full setup.

**Verify.** Run and paste:
```powershell
Get-Content requirements.txt
git status --short
```
Expected: `requirements.txt` has pinned versions; `.gitattributes` and `backend/README.md` appear as new files.

**If it fails.**
- `pip freeze` lists extra junk (e.g. `pptx`, `pillow`) → only copy lines matching the pattern above.
- `requirements.txt` has duplicates → deduplicate manually.
- MySQL commands fail → ensure MySQL is in PATH and root password is correct.

> 📌 **CCS630 lesson — the environment is part of the schema.** `requirements.txt` is to Python what
> `01_schema.sql` is to MySQL: the script that rebuilds it from nothing.

---

## Step M2.18 — M2 exit review

**Goal.** Close the milestone: everything committed on `develop`, tagged `m2-complete`, merged to `master` via PR.

**Where.** Project root — PowerShell.

**Actions.**

1. **Final smoke pass (all must pass):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python manage.py check
   pytest
   ruff check backend
   ```

2. **Verify key files are present:**
   ```powershell
   git status --short
   ```
   Expected new/changed files:
   - `backend/config/settings.py` (JWT, CORS, Spectacular, DB config)
   - `backend/config/urls.py` (all app includes + schema + JWT)
   - `backend/accounts/{models.py, admin.py}`
   - `backend/catalog/{models.py, admin.py, serializers.py, views.py, urls.py, test_catalog.py}`
   - `backend/cart/{models.py, admin.py}`
   - `backend/orders/{models.py, admin.py, serializers.py, views.py, urls.py, test_orders.py}`
   - `backend/vendors/{models.py, admin.py, serializers.py, views.py, urls.py}`
   - `backend/favorites/{models.py, admin.py, serializers.py, views.py, urls.py}`
   - `backend/pytest.ini`
   - `ruff.toml`
   - `requirements.txt` (pinned)
   - `.gitattributes`
   - `backend/README.md`

3. **Commit and tag:**
   ```powershell
   git add .
   git commit -m "feat(m2): django backend core — models over M0 schema, admin, read-only API, jwt, tests"
   git tag m2-complete
   git push origin develop --tags
   ```

4. **Merge to `master` via PR** (branch protection requires it):
   - Open `https://github.com/davedy-cit/e-compraStage/pull/new/develop`
   - Create PR titled "M2: Django backend core complete"
   - **Solo-dev workaround:** In branch protection settings for `master`, temporarily set "Require approvals" to 0 or uncheck "Do not allow bypassing" → merge → restore protection.

**Expected result.** All checks green; tag `m2-complete` pushed; PR merged to `master`.

**Verify.** Run and paste:
```powershell
git log --oneline -5
git tag
git status --short
git log origin/master --oneline -3
```

Expected:
- `m2-complete` in the tag list
- Clean tree (`git status --short` empty)
- `origin/master` contains the merge commit

**If it fails.**
- PR merge blocked by protection → adjust the rule as in step 4, merge, restore the rule.
- `pytest` red → fix before tagging; never tag a red milestone.
- `python manage.py check` fails → model/field mismatch; fix before commit.
- `ruff check backend` fails → run `ruff check backend --fix` and `ruff format backend`.

> 📌 **CCS630 lesson — a milestone is a contract.** Tagging `m2-complete` says "this exact code passes every check."
> Future milestones build on this guarantee; if it's false, the whole tower leans.

> 📌 **CCS630 lesson — the milestone gate.** M2 done means: from a wiped machine, `git clone` + `pip install` +
> `.env` + three SQL scripts + `migrate` reproduces your entire backend with data. That is the deliverable, not
> "it runs on my laptop".

---

**Next.** M3 — Feature Build: write-path APIs (cart, checkout with cart-splitting, payments, vendor POS),
business logic in services, and the Vue 3 frontend.

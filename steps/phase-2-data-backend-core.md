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
`__str__`, and FKs pointing at Django's `auth.User`.

**Where.** `backend/<app>/models.py` — editor.

**Actions.**

For **each** app, move its classes from `_inspectdb_all.py` into `<app>/models.py` and fix them up:

1. **Rename classes** to CamelCase domain names: `UsersUserprofile` → `UserProfile`,
   `CatalogProduct` → `Product`, `CartCartitem` → `CartItem`, `OrdersOrder` → `Order`,
   `VendorsVendor` → `PosVendor` (it is the POS extension, not vendor identity), etc.

2. **Every model gets exactly**:

```python
    class Meta:
        managed = False          # M0 SQL scripts are the source of truth
        db_table = "<exact_table_name>"
```

3. **Add `__str__`** to each model — the human-meaningful field(s), e.g.:

```python
    def __str__(self):
        return self.name                     # Vendor, Category, Product
        # return self.code                   # lookups (TransactionStatus, UnitOfMeasure, …)
        # return f"Order {self.pk} ({self.status_code})"   # Order
```

4. **Re-point user FKs.** inspectdb generated classes for `auth_user`; delete those and change every FK that
   targeted them to Django's built-in user:

```python
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, models.PROTECT, db_column="user_id", blank=True, null=True)  # orders_order only — C5 walk-ins
```

   (`null=True` **only** on `Order.user`; every other user FK is `NOT NULL` per the schema.)

5. **Cross-app FKs** use string references so import order never matters:

```python
    vendor = models.ForeignKey("catalog.Vendor", models.PROTECT, db_column="vendor_id")
    order = models.ForeignKey("orders.Order", models.PROTECT, db_column="order_id")
```

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

**Goal.** Proof the models read the real data: every count matches M0.9, and the tomato query reproduces.

**Where.** `backend/` — `manage.py shell`.

**Actions.**

1. In `python manage.py shell`:

```python
from catalog.models import Product, Vendor, Category
from orders.models import TransactionStatus, PaymentStatus, DeliveryStatus, FulfillmentMethod, TransactionType
from catalog.models import AvailabilityStatus, UnitOfMeasure

print(TransactionStatus.objects.count(), PaymentStatus.objects.count(), DeliveryStatus.objects.count(),
      FulfillmentMethod.objects.count(), TransactionType.objects.count(), AvailabilityStatus.objects.count(),
      Category.objects.count(), Vendor.objects.count(), Product.objects.count())

for p in (Product.objects.filter(name__istartswith="Tomato")
          .select_related("vendor", "unit").order_by("price")):
    print(p, "|", p.vendor.name, "|", p.price, "|", p.unit.code)
```

2. Cross-check one relation end-to-end:

```python
v = Vendor.objects.get(name__contains="Villamor")
print(v.product_set.count())
print(User.objects.exists())   # from django.contrib.auth.models import User — should be [] (no users yet)
```

**Expected result.** Counts exactly `7 4 5 3 3 4 9 6 34`; three tomato rows ₱75, ₱78, ₱80 in order; user table empty.

**Verify.** Paste the shell output.

**If it fails.**
- `ProgrammingError (1146): table doesn't exist` → a `db_table` is misspelled in M2.5.
- Wrong counts → you are pointed at the wrong database; check `.env`.
- Tomato order differs → ordering fell back to the default; the `.order_by("price")` must be present.

> 📌 **CCS630 lesson — the ORM is a lens on the schema, not a replacement for it.** If the ORM and the seed data
> disagree, the bug is in the mapping — and this exact test is how you find it.

---

## Step M2.8 — Register the models in the admin

**Goal.** Every domain model visible and manageable in Django admin with useful columns.

**Where.** `backend/<app>/admin.py` — editor.

**Actions.**

1. Pattern per app (example for `catalog/admin.py`):

```python
from django.contrib import admin
from .models import Product, Vendor, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "category", "price", "unit", "stock_quantity", "availability")
    list_filter = ("category", "availability", "vendor")
    search_fields = ("name",)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "stall_location", "market_section", "user")
    search_fields = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {}  # slug is read-only here (managed=False tables are still writable)
```

2. Register **all** models in their apps' `admin.py` — the 5 order lookups and inventory tables get plain
   `admin.site.register(Model)`; the big tables (`Product`, `Order`, `Transaction`, `Payment`) get
   `list_display`/`list_filter`/`search_fields` as above.

**Expected result.** `/admin/` lists all 27 domain models grouped by app.

**Verify.** Run and paste:

```powershell
Select-String -Path accounts\admin.py,catalog\admin.py,cart\admin.py,orders\admin.py,vendors\admin.py,favorites\admin.py -Pattern "register" | Measure-Object -Line
```

Expected: ≥ 27 register lines.

**If it fails.**
- `AdminSite already registered` → a model registered twice; remove the duplicate.
- `list_display` field error → the field name does not exist on the model; check M2.5's rename.

> 📌 **CCS630 lesson — admin is the cheapest CRUD proof.** Before a single API exists, the admin demonstrates the
> full read/write path to every table — and later it is your data-fixing tool during the defense demo.

---

## Step M2.9 — Superuser + admin walkthrough

**Goal.** A superuser account, and a click-through of the seeded data in the admin.

**Where.** `backend/` — PowerShell, browser.

**Actions.**

1. Create the superuser:

```powershell
python manage.py createsuperuser
```

   (username `admin`, your email, a password you will remember for the defense).

2. `python manage.py runserver`, open `http://127.0.0.1:8000/admin/`, log in.

3. Walk and confirm: **Catalog → Products** shows the 34 seeded products with ₱ prices (no encoding garbage);
   **Orders → Orders** is empty (no orders yet — correct); **Auth → Users** shows only `admin`.

4. Add one row through the UI: **Catalog → Units of measure → Add** (`doz`, "Dozen", is_active ✓), then delete it
   again. This proves write access works on a `managed = False` table.

**Expected result.** Admin login works; seeded data renders; add/delete works.

**Verify.** Paste: the admin Products list count (should show 34) and confirm the ₱ sign renders correctly.

**If it fails.**
- `Superuser creation skipped` → answer `no` to the "bypass" prompt and provide a valid username.
- ₱ renders as `?` → the connection charset is wrong; check the `OPTIONS` in M2.3.

> 📌 **CCS630 lesson — utf8mb4 end to end.** The ₱ sign survived schema → seed → ORM → admin. One non-utf8mb4 hop
> anywhere would have mangled it; this walkthrough is the check.

---

## Step M2.10 — DRF + core serializers

**Goal.** REST framework installed and serializers for the customer-facing read model.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. Install (unpinned; versions get frozen in M2.17):

```powershell
pip install djangorestframework
```

2. `INSTALLED_APPS`: add `"rest_framework"`.

3. `backend/catalog/serializers.py`:

```python
from rest_framework import serializers
from .models import Product, Category, Vendor

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ("id", "name", "stall_location", "market_section")

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    unit = serializers.CharField(source="unit.code", read_only=True)
    availability = serializers.CharField(source="availability.code", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "vendor", "category", "unit", "price",
                  "stock_quantity", "availability")
```

**Expected result.** DRF installed; serializers import cleanly.

**Verify.**

```powershell
python manage.py shell -c "from catalog.serializers import ProductSerializer; print('serializers ok')"
```

Expected: `serializers ok`.

**If it fails.** `source="unit.code"` errors → the FK name differs from M2.5; align.

> 📌 **CCS630 lesson — the serializer is the API contract.** It decides exactly which columns leave the database —
> the API version of choosing a projection in SQL.

---

## Step M2.11 — Read-only API views

**Goal.** List/detail endpoints for products, plus category and vendor lists — the customer browse path.

**Where.** `backend/catalog/views.py` — editor.

**Actions.**

```python
from django.db.models import Q
from rest_framework import generics
from .models import Product, Category, Vendor
from .serializers import ProductSerializer, CategorySerializer, VendorSerializer

class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = (Product.objects.filter(availability__is_orderable=True)
              .select_related("vendor", "category", "unit", "availability"))
        q = self.request.query_params.get("q")
        cat = self.request.query_params.get("category")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(vendor__name__icontains=q))
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs.order_by("name")

class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("vendor", "category", "unit", "availability")
    serializer_class = ProductSerializer

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class VendorList(generics.ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
```

**Expected result.** Four working read-only views.

**Verify.** Paste the file's `Select-String "^class "` count → 4.

**If it fails.** `is_orderable` unknown → that field lives on `AvailabilityStatus` (M0 schema); the related name
traverses `availability__is_orderable`.

> 📌 **CCS630 lesson — search is a query plan.** `?q=` becomes a `LIKE %…%` over `catalog_product.name` — the
> exact query `ix_product_name` (M0.8) was built to serve. You will `EXPLAIN` this in M4.

---

## Step M2.12 — URLs + browsable API root

**Goal.** A tidy URL tree under `/api/` and a working browsable API.

**Where.** `backend/config/urls.py`, `backend/catalog/urls.py`.

**Actions.**

1. Create `backend/catalog/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductList.as_view(), name="product-list"),
    path("products/<int:pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("categories/", views.CategoryList.as_view(), name="category-list"),
    path("vendors/", views.VendorList.as_view(), name="vendor-list"),
]
```

2. Edit `backend/config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
]
```

3. `python manage.py runserver`, open:
   - `http://127.0.0.1:8000/api/products/` → JSON list (DRF browsable UI)
   - `http://127.0.0.1:8000/api/products/?q=tomato` → filtered
   - `http://127.0.0.1:8000/api/products/1/` → detail

**Expected result.** All three URLs return real seeded data with ₱ intact.

**Verify.** Paste the JSON of `?q=tomato` (should include the three tomato products, cheapest first when sorted).

**If it fails.** `No module named catalog.urls` → the file name is `urls.py` inside the app, not the project.

> 📌 **CCS630 lesson — the API is the mockup's backend twin.** Each mockup screen from M0.10 names the data it
> needs; these endpoints are where that data starts to exist for real.

---

## Step M2.13 — OpenAPI schema + Swagger UI

**Goal.** Machine-readable API documentation, auto-generated.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. `pip install drf-spectacular`; add `"drf_spectacular"` to `INSTALLED_APPS`.
2. In settings:

```python
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Compra API",
    "DESCRIPTION": "Public-market marketplace — CCS630 capstone",
    "VERSION": "0.1.0",
}
```

3. In `config/urls.py`:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
```

**Expected result.** Swagger UI renders with products/categories/vendors endpoints listed.

**Verify.** Paste confirmation that `http://127.0.0.1:8000/api/schema/swagger-ui/` renders (screenshot or describe).

**If it fails.** `spec invalid` warnings → note them; usually a serializer without a model field mapping.

> 📌 **CCS630 lesson — documentation that cannot drift.** The schema is generated from the code; a stale API doc
> becomes impossible.

---

## Step M2.14 — CORS + SimpleJWT

**Goal.** The future Vue frontend (localhost:5173) may call the API; users may authenticate with JWT.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. `pip install django-cors-headers djangorestframework-simplejwt`
2. `INSTALLED_APPS`: add `"corsheaders"`; `MIDDLEWARE`: `"corsheaders.middleware.CorsMiddleware"` — **above**
   `CommonMiddleware`.
3. Settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

from datetime import timedelta
REST_FRAMEWORK.update({
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
})
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
```

4. In `config/urls.py`:

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
```

**Expected result.** POSTing superuser credentials to `/api/token/` returns `access` + `refresh`.

**Verify.** In PowerShell:

```powershell
$body = '{"username":"admin","password":"<your superuser password>"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/token/ -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```

Expected: JSON with `access` and `refresh` keys. (Do **not** paste the tokens themselves — just confirm the keys exist.)

**If it fails.** 401 → wrong credentials; 404 → urls not saved; `corsheaders` import error → middleware order.

> 📌 **CCS630 lesson — CORS is the browser's rule, JWT is yours.** CORS protects the *user's* browser from other
> sites; JWT is how *your* API knows who is calling. Both will be load-bearing in M3.

---

## Step M2.15 — pytest + first database tests

**Goal.** A test runner wired to Django, with a seeded test database, proving the schema again from the test side.

**Where.** `backend/` — PowerShell, editor.

**Actions.**

1. `pip install pytest pytest-django`
2. Create `backend/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
```

3. Create the test database **as a copy of `ecompra`** (the migrations only know Django's own tables; the 27
   domain tables are SQL-managed, so the test DB inherits them by clone):

```powershell
cmd /c 'mysql -u root -p -e "DROP DATABASE IF EXISTS test_ecompra; CREATE DATABASE test_ecompra CHARACTER SET utf8mb4;"'
cmd /c "mysqldump -u root -p ecompra > ..\backups\test_seed.sql"
cmd /c 'mysql -u root -p test_ecompra < ..\backups\test_seed.sql'
```

   (`backups/` is gitignored — the dump must never be committed.)

4. Add to `config/settings.py`:

```python
import sys
if "pytest" in sys.modules:
    DATABASES["default"]["NAME"] = "test_ecompra"
```

5. Create `backend/catalog/test_catalog.py`:

```python
import pytest
from .models import Product

@pytest.mark.django_db
def test_seed_counts():
    assert Product.objects.count() == 34

@pytest.mark.django_db
def test_tomato_price_comparison():
    rows = list(Product.objects.filter(name__istartswith="Tomato").order_by("price"))
    assert [r.price for r in rows] == [75, 78, 80]
```

6. Run:

```powershell
pytest --reuse-db
```

**Expected result.** 2 passed.

**Verify.** Paste the pytest summary line.

**If it fails.**
- `pytest` collects 0 tests → `pytest.ini` not in the folder pytest runs from; run from `backend/`.
- `(1146) table doesn't exist` in tests → step 3's clone was skipped or pointed at the wrong dump.
- `--reuse-db` keeps an old schema → drop `test_ecompra` (step 3) and re-clone.

> 📌 **CCS630 lesson — test the invariant, not the implementation.** "34 products, tomato 75/78/80" is the seed
> contract from M0.9, now enforced forever by CI-able tests.

---

## Step M2.16 — ruff lint pass

**Goal.** A configured linter and a clean codebase.

**Where.** Project root — PowerShell.

**Actions.**

1. `pip install ruff`
2. Create `ruff.toml` at the project root:

```toml
line-length = 110
exclude = [".venv", "backups", "tools"]

[lint]
select = ["E", "F", "W", "I"]
```

3. Run and fix:

```powershell
ruff check backend --fix
ruff check backend
```

**Expected result.** `All checks passed!`

**Verify.** Paste the final `ruff check backend` output.

**If it fails.** Long lines in `migrations/` → add `"backend/config/settings.py"`-style excludes only for
generated code, never for your own.

> 📌 **CCS630 lesson — lint is a review you get for free.** The import sorting alone (`I`) prevents a whole class
> of circular-import bugs in Django apps.

---

## Step M2.17 — Freeze requirements, `.gitattributes`, backend README

**Goal.** The exact environment recorded; line-ending noise ended; backend documented.

**Where.** Project root, `backend/` — PowerShell, editor.

**Actions.**

1. Append the newly installed, actually-resolved versions to the root `requirements.txt`:

```powershell
pip freeze | Select-String -Pattern "asgiref|Django|sqlparse|PyMySQL|python-dotenv|djangorestframework|drf-spectacular|django-cors|PyJWT|pytest|ruff"
```

   Add those `name==version` lines to `requirements.txt` (merge, do not duplicate).

2. Create `.gitattributes` at the project root (ends the LF/CRLF warnings from M1.9):

```gitattributes
* text=auto
```

3. Create `backend/README.md`: stack, how to set up (venv → pip → .env from .env.example → migrate →
   handover SQL → createsuperuser → runserver), and the API surface so far.

**Expected result.** Pinned env reproducible from `requirements.txt` alone.

**Verify.** Run and paste:

```powershell
Get-Content requirements.txt
git status --short
```

**If it fails.** `pip freeze` lists extra junk (e.g. `pptx`) → only copy the lines matching the pattern above.

> 📌 **CCS630 lesson — the environment is part of the schema.** `requirements.txt` is to Python what
> `01_schema.sql` is to MySQL: the script that rebuilds it from nothing.

---

## Step M2.18 — M2 exit review

**Goal.** Close the milestone: everything committed on `develop`, tagged, merged to `master` via PR.

**Where.** Project root — PowerShell.

**Actions.**

1. Final smoke pass:

```powershell
python manage.py check
pytest --reuse-db
ruff check backend
```

2. Commit and tag:

```powershell
git add .
git commit -m "feat(m2): django backend core — models over M0 schema, admin, read-only API, jwt, tests"
git tag m2-complete
git push origin develop --tags
```

3. Merge to `master` via PR (branch protection requires it): open
   `https://github.com/davedy-cit/e-compraStage/pull/new/develop`, create the PR, and merge.
   **Solo-dev note:** "Require 1 approval" blocks self-approval — under the rule's settings tick
   *Do not allow bypassing* **off** (or set approvals to 0) so you can merge your own PR, then re-enable.

**Expected result.** All checks green; tag pushed; PR merged.

**Verify.** Run and paste:

```powershell
git log --oneline -5
git tag
git status --short
git log origin/master --oneline -3
```

Expected: `m2-complete` in the tag list; clean tree; `origin/master` contains the merge.

**If it fails.**
- PR merge blocked by protection → adjust the rule as in step 3, merge, restore the rule.
- `pytest` red → fix before tagging; never tag a red milestone.

> 📌 **CCS630 lesson — the milestone gate.** M2 done means: from a wiped machine, `git clone` + `pip install` +
> `.env` + three SQL scripts + `migrate` reproduces your entire backend with data. That is the deliverable, not
> "it runs on my laptop".

---

**Next.** M3 — Feature Build: write-path APIs (cart, checkout with cart-splitting, payments, vendor POS),
business logic in services, and the Vue 3 frontend.

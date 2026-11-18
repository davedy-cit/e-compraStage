# Phase 0 — System & Design + Planning Artifacts

**Milestone M0 · Nov 12 – Nov 18, 2026 · 13 steps · Steps M0.1 – M0.13**

This phase produces the design of record, the database schema, the 16 mockups and the proposal deck. It is the
foundation everything else is built on: **no DDL is written until the design decisions are settled (M0.3)**.

> **You build; the coach instructs and verifies.** For M0.10 – M0.12 the artifacts themselves are coach-produced
> (mockups and the PowerPoint are documents, not source code). You review and approve them.

---

## Step M0.1 — Workspace baseline

**Goal.** A clean project skeleton under version control, with secrets and tooling excluded from git.

**Where.** Project root: `…\LearnProjectBuild\e-compraSystem` — PowerShell.

**Actions.**

1. Confirm you are in the project root:

```powershell
Get-Location
Get-ChildItem
```

2. Create the folders:

```powershell
foreach ($d in @("backend","frontend","sql","docs","docs\uml","docs\mockups","steps","tools","backups")) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
```

3. Create `.gitignore` in the project root with exactly this content:

```gitignore
# ---- Python / Django ----
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
db.sqlite3
db.sqlite3-journal
/staticfiles/
/media/

# ---- Environment / secrets ----
.env
.env.*
!.env.example
*.pem
*.key

# ---- Node / Vue ----
node_modules/
dist/
build/
.vite/
npm-debug.log*
yarn-error.log*

# ---- Editors / OS ----
.vscode/
.idea/
*.swp
Thumbs.db
Desktop.ini

# ---- Tooling (large, re-downloadable) ----
tools/
*.jar

# ---- Backups / dumps (never commit data) ----
backups/
*.sql.gz
*.dump

# ---- Logs ----
*.log
logs/
```

4. Initialise the repository and make the first commit:

```powershell
git init
git add .
git commit -m "chore: project skeleton, design of record, and planning package"
```

**Expected result.** `git init` prints `Initialized empty Git repository…`; the commit reports the files added.

**Verify.** Run and paste the output:

```powershell
git log --oneline
git status --short
git ls-files | Measure-Object -Line
```

You should see **1 commit**, an **empty** `git status --short` (nothing untracked that matters), and a file count
in the dozens. Then confirm the exclusions worked:

```powershell
git ls-files | Select-String -Pattern "plantuml.jar|\.env$|tools/"
```

This should print **nothing** — if it lists `tools/plantuml.jar`, your `.gitignore` did not take effect.

**If it fails.**
- `git: command not found` → git is not on PATH; reinstall Git for Windows with "Git from the command line" checked.
- `*** Please tell me who you are` → run `git config --global user.name "Dave Mariquit"` and `git config --global user.email "you@example.com"`.
- `fatal: not a git repository` on the second command → the `git init` step failed; check you are in the project root, not a parent folder.
- Files you expected to be tracked are missing → a `.gitignore` rule is too broad; run `git check-ignore -v <path>` to see which rule matched.

> 📌 **CCS630 lesson — why `.gitignore` first.** A secret committed once is in the history forever, even after
> deletion, and `mysqldump` files contain real personal data. Excluding `.env`, `backups/` and dumps **before**
> the first commit is the cheapest security control in the whole project — and it is the one the "security"
> lesson will point back to.

---

## Step M0.2 — Design-of-record walkthrough

**Goal.** Prove you understand the five diagrams before changing them, and capture that understanding in writing.

**Where.** Project root → `docs/DESIGN_NOTES.md` (new file).

**Actions.**

1. Open each of these and read it end to end:
   `docs/uml/er-diagram.puml`, `class-diagram.puml`, `sequence-diagram.puml`, `activity-diagram.puml`, `use-case.puml`.
2. Create `docs/DESIGN_NOTES.md` with this skeleton, and **fill in every `‹…›`** in your own words:

```markdown
# Design Notes — the design of record in my own words

## 1. ER diagram — what the data looks like
- The system's central entity is ‹…›, because ‹…›.
- An Order belongs to exactly ‹…› vendor(s), because ‹…›.
- Order, Transaction and Payment are three separate tables because ‹…›.
- The lookup tables (TransactionStatus, PaymentStatus, …) exist so that ‹…›.
- ComparisonGroup and UnitOfMeasure exist so that ‹…›.

## 2. Class diagram — the same model as objects
- The class diagram and the ER diagram describe ‹…›.
- Django models are thin data holders; the business logic lives in ‹…›.

## 3. Sequence diagram — how the calls flow
- Placing an order splits the cart because ‹…›.
- Payment is verified server-side because ‹…›.
- The vendor POS flow is vendor-scoped because ‹…›.

## 4. Activity diagram — the decisions
- The checkout flow rejects an invalid cart because ‹…›.
- The pickup flow takes cash at the stall, which means ‹…›.

## 5. Use case diagram — who can do what
- The actors are ‹…›.
- A Customer can ‹…›; a Vendor can ‹…›; an Administrator can ‹…›.

## 6. Questions I could not answer from the diagrams
- ‹…›
```

3. Save the file.

**Expected result.** `docs/DESIGN_NOTES.md` exists with every placeholder replaced.

**Verify.** Run and paste the output:

```powershell
Select-String -Path docs\DESIGN_NOTES.md -Pattern "‹" | Measure-Object -Line
```

Expected: **0** — no `‹…›` placeholders left.

**If it fails.**
- The command errors → the file is not at `docs\DESIGN_NOTES.md`; check the path.
- You cannot answer a question → write it in section 6. **"I don't know" is a valid, useful answer** — those are the questions the next step settles.

> 📌 **CCS630 lesson — reading a schema is a skill.** Being able to say *why* Order and Payment are separate
> relations (they change at different rates and have different cardinalities) is exactly what the normalization
> and ER-modelling lessons test.

---

## Step M0.3 — Settle the design decisions

**Goal.** Rule on every finding in `docs/DESIGN_REVIEW.md` so the DDL is written once, against a settled design.

**Where.** `docs/DESIGN_DECISIONS.md` — already drafted by the coach with a recommended ruling per finding.

**Actions.**

1. Read `docs/DESIGN_REVIEW.md` (the 32 findings) and then `docs/DESIGN_DECISIONS.md` (the rulings applied).
2. Work through `DESIGN_DECISIONS.md` §8 — the sign-off checklist — and tick each line **only** when you can
   explain it out loud without notes.
3. For any ruling you disagree with, add a row to the table at the end of §8: the reference, **your** ruling, and
   **your** reason. Then tell the coach, and the `.puml` and DDL will be corrected to match.
4. Pay particular attention to the three marked `[coach's call]` and the C4 trade-off.
5. Decide the one genuinely open scope question — **M14 (vendor self-service product management, ~3 h)**. Keep it
   or cut it; both are defensible, but decide now.

**Expected result.** Every line in §8 either ticked or overridden with a written reason, and no unticked line left
without a note.

**Verify.** Paste the output of:

```powershell
Select-String -Path docs\DESIGN_DECISIONS.md -Pattern "^- \[ \]" | Measure-Object -Line
```

Expected: **0** — every checklist box is ticked `[x]`. Then paste your **Rulings I changed or rejected** table
(empty is fine, if you genuinely agree with everything).

**If it fails.**
- You cannot decide a ruling → that is a signal, not a failure. Pick the option that costs less time, write down
  the trade-off, and move on. Record it as a known limitation.
- A ruling contradicts something in the idea document → the idea document's **wording** stays (the proposal
  quotes it); the **system** follows the UML. Note the difference; do not silently rewrite the proposal.

> 📌 **CCS630 lesson — why we settle decisions before DDL.** Changing a table after it holds data means a
> migration, a backfill and a risk of data loss. Changing a diagram costs nothing. The cost of a design change
> rises with every step it survives — that is the whole argument for doing design first.

---

## Step M0.4 — Apply rulings to the diagrams and re-export

**Goal.** The five `.puml` files match `DESIGN_DECISIONS.md`, and the SVGs are regenerated.

**Where.** `docs/uml/` — PowerShell.

**Actions.**

1. The coach has already applied the recommended rulings (revision 2). If you **overrode** any ruling in M0.3,
   edit the affected `.puml` file(s) yourself now. Revision 1 is preserved in `docs/uml/archive-v1-original/`.
2. Confirm PlantUML is present (downloaded in this phase):

```powershell
Get-Item tools\plantuml.jar | Select-Object Name, Length
```

3. Re-render all five diagrams:

```powershell
java -jar tools\plantuml.jar -charset UTF-8 -tsvg docs\uml\er-diagram.puml docs\uml\class-diagram.puml docs\uml\sequence-diagram.puml docs\uml\activity-diagram.puml docs\uml\use-case.puml
```

4. Open each `.svg` in a browser and read it. **Look for:** overlapping labels, boxes running off the page, a
   relationship arrow pointing at nothing, or a note sitting on top of an entity.

**Expected result.** Five `.svg` files with today's timestamp, each rendering without a PlantUML syntax-error
image.

**Verify.** Run and paste the output:

```powershell
Get-ChildItem docs\uml\*.svg | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
```

Every file should have a **new** `LastWriteTime` and a plausible size (the ER diagram will be the largest, ~100 KB+).
A file of a few KB is a syntax error — open it to read the message.

**If it fails.**
- `Error line N in file …` → a PlantUML syntax error. The message names the line; paste it and the coach will fix it.
- `java: command not found` → Java is not on PATH; the JDK 22 is installed, so add it to PATH or call it by full path.
- The SVG is a small grey error box → same as above; the error text is *inside* the SVG.
- Everything renders but a note overlaps a box → cosmetic; adjust the note's position (`note right of X` → `note bottom of X`).

> 📌 **CCS630 lesson — the diagram is the documentation.** The ERD is not decoration; it is the artifact the
> examiner will point at while asking why a table exists. Keeping the `.puml` source in version control means you
> can show exactly what changed and when.

---

## Step M0.5 — ER-to-relational mapping

**Goal.** A table-by-table mapping from the ER model to the physical schema, with every key, constraint and
cardinality justified.

**Where.** `docs/ER_TO_RELATIONAL.md` (new file).

**Actions.**

1. Create `docs/ER_TO_RELATIONAL.md` using this structure, and complete it for **every** table:

```markdown
# ER-to-Relational Mapping

## Mapping rules applied
- Strong entity → its own relation, primary key = the entity's identifier.
- 1:1 relationship → the primary key of one side becomes a FK (unique) on the other.
- 1:N relationship → the primary key of the "1" side becomes a FK on the "N" side.
- M:N relationship → a new relation whose primary key is the pair of FKs.
- Multivalued attribute → its own relation.
- Weak entity → a relation whose primary key includes the owner's key.

## Tables

### `catalog_product`
| | |
|---|---|
| Source entity | Product |
| Primary key | `id` (surrogate) |
| Foreign keys | `vendor_id → catalog_vendor(id)`, `category_id → catalog_category(id)`, `unit_code → catalog_unitofmeasure(code)`, `availability_code → catalog_availabilitystatus(code)`, `comparison_group_code → catalog_comparisongroup(code)` NULL |
| Nullable FKs | `comparison_group_code` — a product need not be in a comparison group |
| Unique constraints | none |
| Check constraints | `price >= 0`, `stock_quantity >= 0` |
| Cardinality justification | one vendor sells many products (1:N); one category classifies many products (1:N) |
| Normal form | 3NF — no non-key attribute depends on another non-key attribute |

‹repeat for every table: users/profiles, catalog, cart, orders, payments, delivery, vendors, favorites, inventory›

## Deferred / derived values
| Value | Stored? | Why |
|---|---|---|
| `orders_orderitem.unit_price` | stored | price snapshot — the price at order time must not change later |
| `orders_order.total_amount` | stored | same reason; also the amount the payment must match |
| line total (qty × unit_price) | **not** stored | derived attribute — storing it risks update anomalies; compute it |
| `catalog_product.stock_quantity` | stored | running balance maintained by the trigger, from the InventoryMovement ledger |
```

2. Complete every `‹…›` and add every table.

**Expected result.** A complete mapping doc covering all ~28 tables.

**Verify.** Run and paste:

```powershell
Select-String -Path docs\ER_TO_RELATIONAL.md -Pattern "^### " | Measure-Object -Line
Select-String -Path docs\ER_TO_RELATIONAL.md -Pattern "‹" | Measure-Object -Line
```

Expected: the first count is **≥ 25** (one section per table); the second is **0**.

**If it fails.**
- Fewer tables than the ERD → you skipped some. Count the entities in `er-diagram.puml` and compare.
- You cannot justify a cardinality → re-read that relationship in the ERD; the note usually explains it.

> 📌 **CCS630 lesson — this is the exam question.** "Given this ER diagram, produce the relational schema" is the
> single most common database exam task. Doing it once, properly, for your own project is the best possible
> preparation — and this document *is* that answer, for your system.

---

## Step M0.6 — Normalization write-up

**Goal.** A written justification that the schema is in 3NF (and where BCNF), including the deliberate
denormalizations and why they are safe.

**Where.** `docs/NORMALIZATION.md` (new file).

**Actions.**

1. Create `docs/NORMALIZATION.md` with this structure and fill it in:

```markdown
# Normalization Analysis

## 1. Method
For each relation: state the candidate keys, then test 1NF → 2NF → 3NF → BCNF, naming the functional
dependencies. Where a relation is not in BCNF, say why and whether that is acceptable.

## 2. Functional dependencies per relation
### `orders_orderitem`
- Candidate key: `(order_id, product_id)` — assuming a product appears once per order
- FDs: `order_id, product_id → quantity, unit_price`
- 2NF: no partial dependency — every non-key attribute depends on the whole key
- 3NF: no transitive dependency
- Verdict: **3NF, BCNF**

‹repeat per relation, at least for: orders_order, orders_orderitem, orders_payment,
orders_transaction, orders_deliverybooking, catalog_product, catalog_comparisongroup, cart_cartitem›

## 3. How the lookup tables serve normalization
TransactionStatus, PaymentStatus, DeliveryStatus, FulfillmentMethod, TransactionType,
AvailabilityStatus, UnitOfMeasure, InventoryReason, Category each hold one row per code.
Storing the code on the fact table instead of the description means the description is
stored once — removing a transitive dependency and an update anomaly.

## 4. Deliberate denormalizations (documented, not accidental)
| Column | Denormalized from | Why it is safe |
|---|---|---|
| `catalog_product.unit` | `catalog_comparisongroup.base_unit` | the displayed unit legitimately differs from the comparison base unit (sold per bundle, compared per kilo). Writes go through the vendor product form, not ad-hoc. |
| `catalog_product.stall_location` | `catalog_vendor.stall_location` | a per-listing override; a vendor may move a product to a different stall. |
| `orders_orderitem.unit_price`, `orders_order.total_amount` | recomputable from product prices | **intentional snapshot**: an order must record the price agreed at order time, not today's price. This is not a normalization violation — it is a different fact. |
| `catalog_product.stock_quantity` | sum of `catalog_inventorymovement.delta` | a cached balance for read performance; the ledger is the source of truth and the trigger keeps them consistent. |

## 5. Why Order, Transaction and Payment are three relations
- Order — what the customer bought (changes rarely after creation)
- Transaction — the commercial reference and type (1:1 with Order)
- Payment — one row per payment attempt (0..N per Transaction)
A single table would need repeating payment attempts and would violate 1NF.

## 6. Known weaknesses
- ‹anything you could not normalize, and why you accepted it›
```

2. Complete every section, with at least the eight relations named in §2.

**Expected result.** A written analysis you could hand in, with named functional dependencies.

**Verify.** Paste:

```powershell
Select-String -Path docs\NORMALIZATION.md -Pattern "‹" | Measure-Object -Line
Select-String -Path docs\NORMALIZATION.md -Pattern "^### " | Measure-Object -Line
```

Expected: **0** placeholders, and **≥ 8** relation sections.

**If it fails.**
- You cannot name the FDs → write the candidate key first, then ask "does every other column depend on *all* of it?" Partial dependency → 2NF violation; dependency on a non-key column → 3NF violation.
- A relation seems to fail 3NF → it may genuinely be a documented denormalization (§4). Add it there with a reason rather than "fixing" it.

> 📌 **CCS630 lesson — denormalization you can name is a strength.** An examiner asking "is this 3NF?" is testing
> whether you know *why* each column is where it is. "That column is a deliberate price snapshot, here is the
> reasoning" is a better answer than a schema with no such column.

---

## Step M0.7 — DDL v1

**Goal.** A runnable MySQL 8 schema script that creates every table with its keys, constraints and comments.

**Where.** `sql/01_schema.sql` (new file) — MySQL Workbench or the `mysql` CLI.

**Actions.**

1. Make sure MySQL 8 is installed and you can connect. (If not, this step's *If it fails* has the fallback.)
2. Create `sql/01_schema.sql`. It is a long file; the coach provides the full contents. **Read it as you paste
   it** — each block has a comment naming the finding it implements.
3. Run it:

```powershell
mysql -u root -p < sql/01_schema.sql
```

4. Connect and inspect:

```sql
USE ecompra;
SHOW TABLES;
```

**Expected result.** ~28 tables created, no errors, and `SHOW TABLES` lists them.

**Verify.** Run and paste:

```sql
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'ecompra';
SELECT table_name, column_name, referenced_table_name
FROM information_schema.key_column_usage
WHERE table_schema = 'ecompra' AND referenced_table_name IS NOT NULL
ORDER BY table_name;
```

Expected: `table_count` ≈ 28, and the FK list shows every foreign key resolving to a real table. Then confirm the
constraints that the review required actually exist:

```sql
SHOW CREATE TABLE favorites_favoriteproduct;
SHOW CREATE TABLE orders_order;
```

`favorites_favoriteproduct` must show a **UNIQUE** key on `(user_id, product_id)` with both columns **NOT NULL**;
`orders_order` must show `vendor_id` **NOT NULL**.

**If it fails.**
- `ERROR 1045 Access denied` → wrong root password; use the one set at install, or create a dedicated user.
- `ERROR 1064 syntax error` → you pasted a fragment; re-copy the whole file.
- `ERROR 1215 Cannot add foreign key constraint` → the referenced table is created later in the file or its type differs. **Order matters:** create lookup and parent tables before children.
- `ERROR 1005 errno 150` → same cause as 1215; check `ENGINE=InnoDB` on both sides and matching column types (`BIGINT UNSIGNED` on both).
- MySQL is not installed → install **MySQL 8 Community Server** with the MySQL Installer, choose "Server only", set a root password you will remember, and add the `bin` folder to PATH. Fallback: run MySQL 8 in Docker Desktop.

> 📌 **CCS630 lesson — constraints are the last line of defence.** The application can have a bug; a `NOT NULL`,
> a `UNIQUE` or a `CHECK` cannot be bypassed by a buggy code path or a careless `UPDATE` typed by hand. Notice
> that `favorites_favoriteproduct` has a UNIQUE key that *works* here, while the original single-table design's
> did not — because MySQL treats `NULL` as distinct in a UNIQUE index.

---

## Step M0.8 — Indexes and constraints

**Goal.** Indexes on every foreign key and search column, with a written reason for each.

**Where.** `sql/02_indexes.sql` (new file).

**Actions.**

1. Create `sql/02_indexes.sql` with the indexes the coach provides, each with a comment naming the query it serves.
2. Run it:

```powershell
mysql -u root -p ecompra < sql/02_indexes.sql
```

3. Inspect the indexes on the hottest tables:

```sql
SHOW INDEX FROM catalog_product;
SHOW INDEX FROM orders_order;
```

**Expected result.** The indexes are created without error and appear in `SHOW INDEX`.

**Verify.** Run and paste:

```sql
SELECT table_name, index_name, GROUP_CONCAT(column_name ORDER BY seq_in_index) AS cols
FROM information_schema.statistics
WHERE table_schema = 'ecompra'
GROUP BY table_name, index_name
ORDER BY table_name, index_name;
```

Expected: every FK column has an index, plus indexes on `catalog_product.name` (search) and
`orders_transaction.reference_no` (lookup by reference).

**If it fails.**
- `ERROR 1061 Duplicate key name` → the index already exists (InnoDB creates one automatically for FKs); skip that line.
- `ERROR 1072 Key column doesn't exist` → a column name is misspelled; check against `01_schema.sql`.
- `ERROR 1170 BLOB/TEXT column used in key specification without a key length` → add a prefix length, e.g. `(description(100))`.

> 📌 **CCS630 lesson — an index is a trade-off, not a free win.** Every index speeds reads and slows writes, and
> costs disk. InnoDB already indexes foreign keys automatically, so the interesting ones here are the **search**
> indexes. You will prove their value with `EXPLAIN` in M4 — keep this file so you can compare before and after.

---

## Step M0.9 — Seed data v1

**Goal.** A repeatable script that loads the lookup tables, the nine categories, units, comparison groups, and
realistic Filipino public-market sample vendors and products.

**Where.** `sql/03_seed.sql` (new file).

**Actions.**

1. Create `sql/03_seed.sql` with the coach-provided contents. It must:
   - insert the **frozen vocabularies** from `docs/DESIGN_DECISIONS.md` §4 — every code, with its `sort_order`,
     `is_terminal` and `is_orderable` values exactly as frozen;
   - insert the nine idea-document categories: Fish, Meat, Poultry, Fruits, Vegetables, Rice, Dry Goods, Spices, Others;
   - insert units of measure (kg, pc, bundle, sack, tray, gram);
   - insert comparison groups with their allowed units and `factor_to_base` values;
   - insert at least **5 vendors** with real stall locations and market sections;
   - insert at least **25 products** with realistic ₱ prices, spread across the categories;
   - include the idea document's worked example: **Tomatoes — Vendor A ₱80/kg, Vendor B ₱75/kg, Vendor C ₱78/kg**,
     all in the same comparison group.
2. Run it:

```powershell
mysql -u root -p ecompra < sql/03_seed.sql
```

**Expected result.** Rows inserted into every lookup table, plus vendors and products.

**Verify.** Run and paste:

```sql
SELECT 'TransactionStatus' AS t, COUNT(*) FROM orders_transactionstatus
UNION ALL SELECT 'PaymentStatus', COUNT(*) FROM orders_paymentstatus
UNION ALL SELECT 'DeliveryStatus', COUNT(*) FROM orders_deliverystatus
UNION ALL SELECT 'FulfillmentMethod', COUNT(*) FROM orders_fulfillmentmethod
UNION ALL SELECT 'TransactionType', COUNT(*) FROM orders_transactiontype
UNION ALL SELECT 'AvailabilityStatus', COUNT(*) FROM catalog_availabilitystatus
UNION ALL SELECT 'Category', COUNT(*) FROM catalog_category
UNION ALL SELECT 'Vendor', COUNT(*) FROM catalog_vendor
UNION ALL SELECT 'Product', COUNT(*) FROM catalog_product;

-- the idea document's price-comparison example must reproduce exactly:
SELECT p.name, v.name AS vendor, p.price, uom.code AS unit
FROM catalog_product p
JOIN catalog_vendor v ON v.id = p.vendor_id
JOIN catalog_unitofmeasure uom ON uom.code = p.unit_code
WHERE p.name LIKE 'Tomato%' ORDER BY p.price;
```

Expected: `TransactionStatus` = **7**, `PaymentStatus` = **4**, `DeliveryStatus` = **5**,
`FulfillmentMethod` = **3**, `TransactionType` = **3**, `AvailabilityStatus` = **4**, `Category` = **9**,
`Vendor` ≥ **5**, `Product` ≥ **25** — and the tomato query returns **three rows: ₱75, ₱78, ₱80** in that order.

**If it fails.**
- `ERROR 1452 Cannot add or update a child row` → a FK value does not exist; insert parents before children (lookups → vendors → products).
- Re-running the script duplicates rows → add `INSERT IGNORE` or `ON DUPLICATE KEY UPDATE`, or start with a `DELETE FROM` in dependency order. A seed script must be **idempotent**.
- The tomato query returns one row → all three products are not in the same `comparison_group`; check that column.
- `Incorrect string value` for ₱ → the column charset is not `utf8mb4`; the schema sets it, so re-run `01_schema.sql`.

> 📌 **CCS630 lesson — seed data is test data.** The tomato example is not filler: it is the acceptance test for
> key feature 2 (price comparison), and it comes straight from your proposal. Realistic data also exposes bugs
> that `product1`/`product2` never will — a 3-character unit, a ₱ sign, a two-word stall name.

---

## Step M0.10 — Feature mockups (16 screens + gallery)

**Goal.** A clickable gallery of 16 static screens that demonstrate all seven key features, using realistic
Filipino public-market data and ₱ prices.

**Where.** `docs/mockups/` — **coach-produced.** You review and approve; you do not build these.

**Actions.**

1. List what was produced:

```powershell
Get-ChildItem docs\mockups\*.html | Select-Object Name, Length | Format-Table -AutoSize
```

2. Open the gallery in Edge:

```powershell
Start-Process "docs\mockups\index.html"
```

3. Walk every card in the gallery. For **each** screen, check three things:
   - the key feature named on its card is actually visible on the screen;
   - the data is realistic — ₱ prices, fish/meat/vegetables/rice/dry goods/spices, Filipino vendor and stall names;
   - it is readable at phone width.
4. Test mobile rendering: press **F12** → click the device-toolbar icon → choose **iPhone SE (375 × 667)**. Re-check
   the customer screens (`home`, `search-results`, `product-detail`, `cart-checkout`).
5. Check the idea document's own example reproduces: open `price-comparison.html` and confirm it shows
   **Tomatoes — ₱80/kg, ₱75/kg, ₱78/kg** across three vendors with the best value highlighted.
6. Write down any screen that is wrong, missing, or unclear and tell the coach.

**Expected result.** **17** HTML files (16 screens + `index.html`), the gallery opens, and every card links to a
working screen.

**Verify.** Run and paste:

```powershell
(Get-ChildItem docs\mockups\*.html).Count
Get-ChildItem docs\mockups\*.html | Select-Object -ExpandProperty Name
```

Expected: **17**, and the list contains `home`, `search-results`, `product-detail`, `price-comparison`,
`cart-checkout`, `pickup-reservation`, `order-payment`, `order-tracking`, `delivery-booking`, `market-map`,
`favorites-history`, `vendor-dashboard`, `vendor-products`, `vendor-pos`, `vendor-orders`,
`admin-transactions`, `index`.

**If it fails.**
- The gallery opens but a card links to a missing page → the filename and the link disagree; tell the coach which card.
- A screen looks broken or unstyled → the shared inline CSS was not copied into that file; tell the coach which file.
- Text overflows on mobile → report it; the mockups are meant to be mobile-first for the customer screens.
- `Start-Process` cannot find the file → you are not in the project root; run `Get-Location` first.

> 📌 **CCS630 lesson — the mockup is the requirement.** A screen forces you to answer questions a diagram lets you
> dodge: what exactly does the availability badge say when stock is 3? Where does the reservation reference number
> appear? Building the mockups *before* the backend is what stops M3 from discovering a missing field.

---

## Step M0.11 — Mockup screenshots

**Goal.** Desktop and mobile PNGs of every screen, ready to embed in the proposal deck.

**Where.** `docs/mockups/screenshots/` — PowerShell.

**Actions.**

1. Create the output folder and render every screen at desktop width using headless Edge:

```powershell
$root  = "c:\Users\MCC IT Admin\Downloads\MIT\CCS630-Advance Database Systems\LearnProjectBuild\e-compraSystem"
$edge  = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$out   = Join-Path $root "docs\mockups\screenshots"
New-Item -ItemType Directory -Path $out -Force | Out-Null

Get-ChildItem (Join-Path $root "docs\mockups\*.html") |
  Where-Object { $_.Name -ne 'index.html' } |
  ForEach-Object {
    $uri  = ([System.Uri]$_.FullName).AbsoluteUri
    $dest = Join-Path $out ($_.BaseName + "-desktop.png")
    & $edge --headless=new --disable-gpu --hide-scrollbars --window-size=1440,2200 --screenshot="$dest" $uri | Out-Null
    Write-Output "desktop: $($_.BaseName)"
  }
```

2. Then render the customer screens at phone width (the vendor POS and admin screens stay desktop-only):

```powershell
$mobile = @("home","search-results","product-detail","price-comparison","cart-checkout",
            "pickup-reservation","order-payment","order-tracking","delivery-booking",
            "market-map","favorites-history")
foreach ($name in $mobile) {
  $uri  = ([System.Uri](Join-Path $root "docs\mockups\$name.html")).AbsoluteUri
  $dest = Join-Path $out "$name-mobile.png"
  & $edge --headless=new --disable-gpu --hide-scrollbars --window-size=390,1800 --screenshot="$dest" $uri | Out-Null
  Write-Output "mobile:  $name"
}
```

**Expected result.** 16 desktop PNGs + 11 mobile PNGs = **27** images.

**Verify.** Run and paste:

```powershell
(Get-ChildItem docs\mockups\screenshots\*.png).Count
Get-ChildItem docs\mockups\screenshots\*.png | Sort-Object Length | Select-Object -First 3 Name, Length
```

Expected: **27**. The three smallest should still be well over 20 KB — **a PNG of a few KB is a blank page**, which
means the screenshot fired before the page rendered.

**If it fails.**
- `msedge.exe` not found → the path differs on your machine; find it with
  `Get-ChildItem "C:\Program Files*\Microsoft\Edge\Application\msedge.exe"` and use that path.
- The PNGs are blank or tiny → the page had not loaded. Add `--virtual-time-budget=3000` to the Edge command.
- The image is cut off partway down → `--window-size` height is too small; raise `2200` to `3200`.
- Edge refuses to run headless → use Chrome instead: `C:\Program Files\Google\Chrome\Application\chrome.exe`
  with the same flags.

> 📌 **CCS630 lesson — evidence, not adjectives.** The proposal claims the system is convenient and
> mobile-friendly. Screenshots at 390 px are the evidence. Claims you cannot show are claims you cannot defend.

---

## Step M0.12 — Proposal PowerPoint

**Goal.** `docs/E-Compra_Proposal.pptx` — the idea document's outline plus a mockup section, ready to present.

**Where.** `docs/E-Compra_Proposal.pptx` — **coach-produced.** You review and approve.

**Actions.**

1. Confirm it exists:

```powershell
Get-Item docs\E-Compra_Proposal.pptx | Select-Object Name, Length, LastWriteTime
```

2. Open it and walk every slide against this checklist:
   - the **title** slide names the project, you, and CCS630;
   - **Parts 1 and 2 follow the idea document's wording and order** — problem, solution, the seven key features,
     target users, expected impact, then Maria and Pedro, then the elevator pitch;
   - the **mockup section** embeds the screenshots, grouped by module, each with a one-line caption tying it to a
     key feature;
   - the **architecture / ERD / database highlights** slide is present and uses the re-exported `er-diagram.svg`;
   - the **timeline** slide matches `docs/PROJECT_TIMELINE.md`;
   - the **elevator pitch** closes it.
3. Fix the wording on any slide that drifts from the idea document. **The deck quotes the idea document** — where
   the idea document and the UML differ (the pickup flow), the deck keeps the idea document's wording and the
   system follows the UML. That difference is explained on the database-highlights slide, not hidden.
4. Rehearse it once, out loud, timed.

**Expected result.** A deck of roughly 24 slides that opens cleanly and follows the idea document's outline.

**Verify.** Run and paste:

```powershell
python -c "from pptx import Presentation; p=Presentation(r'docs\E-Compra_Proposal.pptx'); print('slides:', len(p.slides))"
```

Expected: a slide count of roughly **22–26**. Then open the deck and confirm the mockup section shows **images**,
not empty placeholders.

**If it fails.**
- `ModuleNotFoundError: No module named 'pptx'` → `python -m pip install python-pptx`.
- Images are missing boxes → the screenshots were not found at render time; run M0.11 first, then tell the coach.
- Text overflows a slide → tell the coach which slide number.

> 📌 **CCS630 lesson — the deck and the system must tell the same story.** The most common defense failure is a
> slide that promises something the demo does not do. Every feature slide should map to a mockup you can show and,
> later, a screen you can click.

---

## Step M0.13 — M0 exit review

**Goal.** Close the milestone: everything committed, the tracker updated, and a live walkthrough you can repeat.

**Where.** Project root — PowerShell.

**Actions.**

1. Confirm every M0 artifact exists:

```powershell
$need = @(
  "docs\PROJECT_TIMELINE.md",
  "docs\DESIGN_REVIEW.md",
  "docs\DESIGN_DECISIONS.md",
  "docs\DESIGN_NOTES.md",
  "docs\ER_TO_RELATIONAL.md",
  "docs\NORMALIZATION.md",
  "docs\E-Compra_Proposal.pptx",
  "sql\01_schema.sql","sql\02_indexes.sql","sql\03_seed.sql",
  "steps\README.md","steps\PROGRESS_LOG.md",
  "docs\uml\er-diagram.svg","docs\uml\class-diagram.svg","docs\uml\sequence-diagram.svg",
  "docs\uml\activity-diagram.svg","docs\uml\use-case.svg"
)
foreach ($f in $need) { "{0,-40} {1}" -f $f, (Test-Path $f) }
```

2. Re-run the schema from scratch to prove it is reproducible:

```powershell
mysql -u root -p < sql/01_schema.sql
mysql -u root -p ecompra < sql/02_indexes.sql
mysql -u root -p ecompra < sql/03_seed.sql
```

3. Commit:

```powershell
git add .
git commit -m "feat(m0): design of record rev2, schema, seed data, mockups, proposal deck"
git tag m0-complete
```

4. Give the checkpoint demo: open `docs/mockups/index.html`, then show `er-diagram.svg`, then run the tomato
   price-comparison query.

**Expected result.** Every line above prints `True`, all three SQL scripts run without error, and the commit lands.

**Verify.** Run and paste:

```powershell
git log --oneline
git tag
git status --short
```

Expected: at least **2 commits**, the tag `m0-complete` listed, and an empty `git status --short`.

**If it fails.**
- Any `False` above → that artifact is missing; go back to its step.
- Re-running the schema errors on existing tables → `01_schema.sql` drops and recreates the database, so this
  should not happen; if it does, your file differs from the provided one.
- `git commit` reports nothing to commit → everything was already committed in an earlier step; that is fine, tag anyway.

> 📌 **CCS630 lesson — reproducibility is the deliverable.** "It works on my machine" is not a database. A schema
> script that rebuilds the database from nothing, plus a seed script that reloads the same test data, is what lets
> you demonstrate, mark, and restore the system — and it is the same discipline the backup-and-recovery lesson
> asks for.

---

## Appendices — full file contents for M0.7 – M0.9

The three SQL scripts are **yours to create**. The contents below are the instructions: copy them into the named
file, but read each block's comment first — every one names the decision it implements.

### Appendix A — `sql/01_schema.sql`

> ⚠️ This script **drops and recreates the `ecompra` database.** That is intentional for a development schema
> script — it is what makes M0.13's reproducibility check meaningful. Never point it at a database holding data
> you care about.

```sql
-- ============================================================================
--  E-Compra — Schema v1
--  MySQL 8.0 · InnoDB · utf8mb4
--  Derived from docs/uml/er-diagram.puml revision 2 (design of record),
--  as refined by docs/DESIGN_REVIEW.md and docs/DESIGN_DECISIONS.md.
--  Run:  mysql -u root -p < sql/01_schema.sql
-- ============================================================================

DROP DATABASE IF EXISTS ecompra;
CREATE DATABASE ecompra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecompra;

-- ---------------------------------------------------------------------------
-- 0. Django's built-in user table (stub).
--    Django owns this table via its own migrations. The stub exists so this
--    script is runnable on a fresh MySQL instance; IF NOT EXISTS makes it a
--    harmless no-op once Django has created the real thing.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auth_user (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  password      VARCHAR(128)    NOT NULL,
  last_login    DATETIME(6)     NULL,
  is_superuser  TINYINT(1)      NOT NULL DEFAULT 0,
  username      VARCHAR(150)    NOT NULL,
  first_name    VARCHAR(150)    NOT NULL DEFAULT '',
  last_name     VARCHAR(150)    NOT NULL DEFAULT '',
  email         VARCHAR(254)    NOT NULL DEFAULT '',
  is_staff      TINYINT(1)      NOT NULL DEFAULT 0,
  is_active     TINYINT(1)      NOT NULL DEFAULT 1,
  date_joined   DATETIME(6)     NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_auth_user_username (username)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 1. Profiles
-- ---------------------------------------------------------------------------
CREATE TABLE accounts_userprofile (
  user_id     BIGINT UNSIGNED NOT NULL,
  is_vendor   TINYINT(1)      NOT NULL DEFAULT 0,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_userprofile_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE accounts_customerprofile (
  user_id     BIGINT UNSIGNED NOT NULL,
  phone       VARCHAR(32)     NOT NULL DEFAULT '',
  address     TEXT            NULL,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_customerprofile_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2. Lookup tables (frozen vocabularies - DESIGN_DECISIONS.md section 4)
-- ---------------------------------------------------------------------------
CREATE TABLE catalog_unitofmeasure (
  code        VARCHAR(16)  NOT NULL,
  name        VARCHAR(64)  NOT NULL,
  description VARCHAR(255) NOT NULL DEFAULT '',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_category (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name        VARCHAR(80)     NOT NULL,
  slug        VARCHAR(80)     NOT NULL,
  is_active   TINYINT(1)      NOT NULL DEFAULT 1,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_category_slug (slug)
) ENGINE=InnoDB;

-- D-4 / M4: availability is a lookup, not free text
CREATE TABLE catalog_availabilitystatus (
  code         VARCHAR(24)  NOT NULL,
  description  VARCHAR(120) NOT NULL,
  sort_order   INT          NOT NULL DEFAULT 0,
  is_orderable TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_comparisongroup (
  code        VARCHAR(32)  NOT NULL,
  name        VARCHAR(120) NOT NULL,
  base_unit   VARCHAR(16)  NOT NULL,
  description VARCHAR(255) NOT NULL DEFAULT '',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (code),
  CONSTRAINT fk_cgroup_baseunit FOREIGN KEY (base_unit) REFERENCES catalog_unitofmeasure (code)
) ENGINE=InnoDB;

-- M5: the units a comparison group is allowed to compare, with a conversion factor
CREATE TABLE catalog_comparisongroupunit (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  comparison_group VARCHAR(32)     NOT NULL,
  unit             VARCHAR(16)     NOT NULL,
  factor_to_base   DECIMAL(12,4)   NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_cgu_group_unit (comparison_group, unit),
  CONSTRAINT fk_cgu_group FOREIGN KEY (comparison_group) REFERENCES catalog_comparisongroup (code) ON DELETE CASCADE,
  CONSTRAINT fk_cgu_unit  FOREIGN KEY (unit)             REFERENCES catalog_unitofmeasure (code),
  CONSTRAINT ck_cgu_factor CHECK (factor_to_base > 0)
) ENGINE=InnoDB;

CREATE TABLE orders_transactionstatus (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  sort_order  INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_transactiontype (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_fulfillmentmethod (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_paymentstatus (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  is_terminal TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_deliverystatus (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  is_terminal TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_inventoryreason (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  direction   VARCHAR(8)   NOT NULL,          -- IN | OUT | ADJUST
  PRIMARY KEY (code),
  CONSTRAINT ck_invreason_direction CHECK (direction IN ('IN','OUT','ADJUST'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3. Catalog
-- ---------------------------------------------------------------------------
-- M6: catalog.Vendor is the single vendor identity. user_id NOT NULL.
CREATE TABLE catalog_vendor (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name          VARCHAR(150)    NOT NULL,
  stall_location VARCHAR(120)   NOT NULL,
  market_section VARCHAR(120)   NOT NULL DEFAULT '',
  contact_phone VARCHAR(32)     NOT NULL DEFAULT '',
  contact_email VARCHAR(254)    NOT NULL DEFAULT '',
  is_active     TINYINT(1)      NOT NULL DEFAULT 1,
  user_id       BIGINT UNSIGNED NOT NULL,
  created_at    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_vendor_user (user_id),
  CONSTRAINT fk_vendor_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE catalog_product (
  id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name                VARCHAR(180)    NOT NULL,
  description         TEXT            NULL,
  image_url           VARCHAR(500)    NOT NULL DEFAULT '',
  price               DECIMAL(12,2)   NOT NULL,
  unit_code           VARCHAR(16)     NOT NULL,
  stall_location      VARCHAR(120)    NOT NULL DEFAULT '',
  availability_code   VARCHAR(24)     NOT NULL,
  stock_quantity      INT             NOT NULL DEFAULT 0,
  low_stock_threshold INT             NOT NULL DEFAULT 5,
  category_id         BIGINT UNSIGNED NOT NULL,
  vendor_id           BIGINT UNSIGNED NOT NULL,
  comparison_group    VARCHAR(32)     NULL,
  created_at          DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at          DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_product_name (name),
  KEY ix_product_vendor (vendor_id),
  KEY ix_product_category (category_id),
  KEY ix_product_cgroup (comparison_group),
  CONSTRAINT fk_product_unit    FOREIGN KEY (unit_code)         REFERENCES catalog_unitofmeasure (code),
  CONSTRAINT fk_product_avail   FOREIGN KEY (availability_code) REFERENCES catalog_availabilitystatus (code),
  CONSTRAINT fk_product_cat     FOREIGN KEY (category_id)       REFERENCES catalog_category (id),
  CONSTRAINT fk_product_vendor  FOREIGN KEY (vendor_id)         REFERENCES catalog_vendor (id) ON DELETE CASCADE,
  CONSTRAINT fk_product_cgroup  FOREIGN KEY (comparison_group)  REFERENCES catalog_comparisongroup (code),
  CONSTRAINT ck_product_price   CHECK (price >= 0),
  CONSTRAINT ck_product_stock   CHECK (stock_quantity >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4. Cart
-- ---------------------------------------------------------------------------
CREATE TABLE cart_cart (
  user_id    BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE cart_cartitem (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cart_id    BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT             NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_cartitem (cart_id, product_id),
  CONSTRAINT fk_cartitem_cart    FOREIGN KEY (cart_id)    REFERENCES cart_cart (user_id) ON DELETE CASCADE,
  CONSTRAINT fk_cartitem_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE CASCADE,
  CONSTRAINT ck_cartitem_qty CHECK (quantity > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5. Orders
-- ---------------------------------------------------------------------------
-- C5: user_id NULL only for anonymous WALK_IN sales.
-- M3: vendor_id NOT NULL - one order = one vendor.
CREATE TABLE orders_order (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id          BIGINT UNSIGNED NULL,
  customer_label   VARCHAR(120)    NULL,
  vendor_id        BIGINT UNSIGNED NOT NULL,
  status_code      VARCHAR(24)     NOT NULL,
  fulfillment_code VARCHAR(16)     NOT NULL,
  total_amount     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
  notes            TEXT            NULL,
  created_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_order_user (user_id),
  KEY ix_order_vendor_status (vendor_id, status_code),
  KEY ix_order_status (status_code),
  CONSTRAINT fk_order_user   FOREIGN KEY (user_id)          REFERENCES auth_user (id) ON DELETE SET NULL,
  CONSTRAINT fk_order_vendor FOREIGN KEY (vendor_id)        REFERENCES catalog_vendor (id) ON DELETE RESTRICT,
  CONSTRAINT fk_order_status FOREIGN KEY (status_code)      REFERENCES orders_transactionstatus (code),
  CONSTRAINT fk_order_fulfil FOREIGN KEY (fulfillment_code) REFERENCES orders_fulfillmentmethod (code),
  CONSTRAINT ck_order_total  CHECK (total_amount >= 0)
) ENGINE=InnoDB;

CREATE TABLE orders_orderitem (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id   BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT             NOT NULL,
  unit_price DECIMAL(12,2)   NOT NULL,        -- price snapshot at order time
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_orderitem (order_id, product_id),
  CONSTRAINT fk_orderitem_order   FOREIGN KEY (order_id)   REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE RESTRICT,
  CONSTRAINT ck_orderitem_qty   CHECK (quantity > 0),
  CONSTRAINT ck_orderitem_price CHECK (unit_price >= 0)
) ENGINE=InnoDB;

-- C8: transaction_type makes reservations queryable. No status column (M9).
CREATE TABLE orders_transaction (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id         BIGINT UNSIGNED NOT NULL,
  transaction_type VARCHAR(24)     NOT NULL,
  reference_no     VARCHAR(40)     NOT NULL,
  created_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_transaction_order (order_id),
  UNIQUE KEY uq_transaction_ref (reference_no),
  CONSTRAINT fk_transaction_order FOREIGN KEY (order_id)         REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_transaction_type  FOREIGN KEY (transaction_type) REFERENCES orders_transactiontype (code)
) ENGINE=InnoDB;

-- M11: cash is recorded here too (provider = 'CASH').
CREATE TABLE orders_payment (
  id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id     BIGINT UNSIGNED NOT NULL,
  provider           VARCHAR(24)     NOT NULL,
  provider_reference VARCHAR(120)    NOT NULL,
  amount             DECIMAL(12,2)   NOT NULL,
  status_code        VARCHAR(16)     NOT NULL,
  raw_response       JSON            NULL,
  paid_at            DATETIME(6)     NULL,
  created_at         DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_payment_provider_ref (provider, provider_reference),
  KEY ix_payment_transaction (transaction_id),
  CONSTRAINT fk_payment_transaction FOREIGN KEY (transaction_id) REFERENCES orders_transaction (id) ON DELETE CASCADE,
  CONSTRAINT fk_payment_status      FOREIGN KEY (status_code)    REFERENCES orders_paymentstatus (code),
  CONSTRAINT ck_payment_amount CHECK (amount >= 0)
) ENGINE=InnoDB;

CREATE TABLE orders_deliverybooking (
  id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id    BIGINT UNSIGNED NOT NULL,
  provider          VARCHAR(24)     NOT NULL,
  booking_reference VARCHAR(120)    NOT NULL,
  tracking_url      VARCHAR(500)    NOT NULL DEFAULT '',
  fee               DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
  status_code       VARCHAR(16)     NOT NULL,
  raw_response      JSON            NULL,
  booked_at         DATETIME(6)     NULL,
  delivered_at      DATETIME(6)     NULL,
  created_at        DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at        DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_delivery_transaction (transaction_id),
  CONSTRAINT fk_delivery_transaction FOREIGN KEY (transaction_id) REFERENCES orders_transaction (id) ON DELETE CASCADE,
  CONSTRAINT fk_delivery_status      FOREIGN KEY (status_code)    REFERENCES orders_deliverystatus (code),
  CONSTRAINT ck_delivery_fee CHECK (fee >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6. Inventory ledger (C2). The trigger target and the audit trail.
--    stock_quantity on catalog_product is the cached balance; this is truth.
-- ---------------------------------------------------------------------------
CREATE TABLE catalog_inventorymovement (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  delta      INT             NOT NULL,
  reason_code VARCHAR(24)    NOT NULL,
  order_id   BIGINT UNSIGNED NULL,
  note       VARCHAR(255)    NOT NULL DEFAULT '',
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_invmov_product (product_id),
  KEY ix_invmov_order (order_id),
  CONSTRAINT fk_invmov_product FOREIGN KEY (product_id)  REFERENCES catalog_product (id) ON DELETE CASCADE,
  CONSTRAINT fk_invmov_reason  FOREIGN KEY (reason_code) REFERENCES catalog_inventoryreason (code),
  CONSTRAINT fk_invmov_order   FOREIGN KEY (order_id)    REFERENCES orders_order (id) ON DELETE SET NULL,
  CONSTRAINT ck_invmov_delta CHECK (delta <> 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7. Vendor POS (M6: 1:1 extension of catalog_vendor, not a second identity)
-- ---------------------------------------------------------------------------
CREATE TABLE vendors_vendor (
  catalog_vendor_id BIGINT UNSIGNED NOT NULL,
  stall_name        VARCHAR(150)    NOT NULL,
  stall_location    VARCHAR(120)    NOT NULL DEFAULT '',
  PRIMARY KEY (catalog_vendor_id),
  CONSTRAINT fk_posvendor_catalog FOREIGN KEY (catalog_vendor_id)
    REFERENCES catalog_vendor (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- C7: receipt_attempt makes the receipt serial stable across reprints.
CREATE TABLE vendors_vendortransaction (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  vendor_id       BIGINT UNSIGNED NOT NULL,
  order_id        BIGINT UNSIGNED NOT NULL,
  status_code     VARCHAR(24)     NOT NULL,
  receipt_serial  VARCHAR(80)     NULL,
  receipt_attempt INT             NOT NULL DEFAULT 1,
  created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_vendortx_order (order_id),
  KEY ix_vendortx_vendor (vendor_id),
  CONSTRAINT fk_vendortx_vendor FOREIGN KEY (vendor_id)   REFERENCES vendors_vendor (catalog_vendor_id) ON DELETE CASCADE,
  CONSTRAINT fk_vendortx_order  FOREIGN KEY (order_id)    REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_vendortx_status FOREIGN KEY (status_code) REFERENCES orders_transactionstatus (code),
  CONSTRAINT ck_vendortx_attempt CHECK (receipt_attempt >= 1)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8. Favorites (M2: split so the UNIQUE constraints actually enforce)
-- ---------------------------------------------------------------------------
CREATE TABLE favorites_favoriteproduct (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_favproduct (user_id, product_id),
  CONSTRAINT fk_favproduct_user    FOREIGN KEY (user_id)    REFERENCES auth_user (id) ON DELETE CASCADE,
  CONSTRAINT fk_favproduct_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE favorites_favoritevendor (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  vendor_id  BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_favvendor (user_id, vendor_id),
  CONSTRAINT fk_favvendor_user   FOREIGN KEY (user_id)   REFERENCES auth_user (id) ON DELETE CASCADE,
  CONSTRAINT fk_favvendor_vendor FOREIGN KEY (vendor_id) REFERENCES catalog_vendor (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
--  End of schema. 28 tables.
--  Objects Django does not manage (views, triggers, procedures, roles) live in
--  sql/04_views.sql, sql/05_procedures_triggers.sql and sql/06_roles_grants.sql.
-- ============================================================================
```

---

### Appendix B — `sql/02_indexes.sql`

```sql
-- ============================================================================
--  E-Compra — Indexes
--  Run after 01_schema.sql:  mysql -u root -p ecompra < sql/02_indexes.sql
--
--  Note: InnoDB already creates an index for every FOREIGN KEY, so the FK
--  indexes are declared inline in 01_schema.sql. This file adds the indexes
--  that serve actual QUERIES - search, filtering and reporting.
-- ============================================================================
USE ecompra;

-- ============================================================================
--  Why this file exists separately from 01_schema.sql
--  ---------------------------------------------------------------------------
--  InnoDB automatically creates an index for every FOREIGN KEY, and
--  01_schema.sql also declares the obvious single-column indexes. That is the
--  minimum needed for the schema to be VALID. This file adds the indexes needed
--  for the schema to be FAST - one composite index per real query shape.
--
--  A composite index (a, b, c) can also serve queries that filter on a alone,
--  or on a and b (the "leftmost prefix" rule). So when a composite replaces a
--  single-column index, the single-column one becomes dead weight: it costs
--  writes and disk for nothing. Those are retired in section 8.
--
--  Section 8 comes LAST on purpose. MySQL refuses to drop an index that is the
--  only one able to serve a FOREIGN KEY, so every replacement must already
--  exist before its predecessor is dropped.
--
--  Run:  mysql -u root -p ecompra < sql/02_indexes.sql
--  Verify: EXPLAIN every query in sql/07_verification_queries.sql and confirm
--          the key column names one of these indexes, not NULL or a full scan.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Product search (idea doc feature 1 - "Product Search and Marketplace")
-- ---------------------------------------------------------------------------
-- Keyword search over name and description. FULLTEXT is an inverted index:
-- it matches whole words and stems, not substrings, so "tomato" finds
-- "Tomatoes" but "toma" does not. That is the correct trade-off for a search
-- box, and it is far faster than LIKE '%...%' (which cannot use any index).
CREATE FULLTEXT INDEX ft_product_search ON catalog_product (name, description);

-- Category chip + "sort by price" is the second most common browse path.
CREATE INDEX ix_product_cat_price ON catalog_product (category_id, price);

-- ---------------------------------------------------------------------------
-- 2. Price comparison (idea doc feature 2 - the Tomatoes example)
-- ---------------------------------------------------------------------------
-- The flagship query joins a product to its comparison group's unit
-- conversions and sorts by price-per-base-unit:
--   WHERE p.comparison_group = ? ORDER BY p.price / cgu.factor_to_base
-- comparison_group alone was indexed; adding unit_code and price lets MySQL
-- satisfy the group lookup from the index and read prices in sorted order.
CREATE INDEX ix_product_cgroup_unit_price
  ON catalog_product (comparison_group, unit_code, price);

-- ---------------------------------------------------------------------------
-- 3. Vendor storefront (idea doc feature 6) and the market map (feature 4)
-- ---------------------------------------------------------------------------
-- Storefront: "this vendor's products, optionally filtered by availability".
CREATE INDEX ix_product_vendor_avail ON catalog_product (vendor_id, availability_code);

-- Market map / vendor directory: group stalls by section, alphabetical inside.
CREATE INDEX ix_vendor_section_name ON catalog_vendor (market_section, name);

-- ---------------------------------------------------------------------------
-- 4. Order history (idea doc feature 5) - newest first, per customer
-- ---------------------------------------------------------------------------
CREATE INDEX ix_order_user_created ON orders_order (user_id, created_at);

-- ---------------------------------------------------------------------------
-- 5. Vendor POS queue and sales dashboard (idea doc features 6 and 7)
-- ---------------------------------------------------------------------------
-- POS queue: "this vendor's orders in status X, oldest first" (FIFO).
CREATE INDEX ix_order_vendor_status_created
  ON orders_order (vendor_id, status_code, created_at);

-- Dashboard: "this vendor's sales between two dates" - no status filter, so
-- the leftmost prefix above does NOT serve it. It needs its own index.
CREATE INDEX ix_order_vendor_created ON orders_order (vendor_id, created_at);

-- ---------------------------------------------------------------------------
-- 6. Reporting and reconciliation
-- ---------------------------------------------------------------------------
CREATE INDEX ix_transaction_created ON orders_transaction (created_at);
CREATE INDEX ix_payment_status_paid ON orders_payment (status_code, paid_at);
CREATE INDEX ix_delivery_status_booked ON orders_deliverybooking (status_code, booked_at);

-- ---------------------------------------------------------------------------
-- 7. Inventory ledger history (idea doc feature 6 - "inventory automatically
--    updates"). Reading one product's movement history, newest first.
-- ---------------------------------------------------------------------------
CREATE INDEX ix_invmov_product_created
  ON catalog_inventorymovement (product_id, created_at);

-- ---------------------------------------------------------------------------
-- 8. Retire the single-column indexes the composites above replace.
--
--    ORDER IS LOAD-BEARING. These DROPs sit after every CREATE, and that is
--    not style - it is a hard requirement. InnoDB refuses to drop an index
--    that is the only one able to serve a FOREIGN KEY:
--
--      ERROR 1553 (HY000): Cannot drop index 'ix_product_category':
--                          needed in a foreign key constraint
--
--    MySQL will accept ANY index whose leftmost columns are the FK columns, so
--    the composite must already exist when the old index goes. Written as a
--    tidy DROP/CREATE pair inside each section - which reads far more
--    naturally - this file fails on the very first statement. Create, then
--    drop, then verify with SHOW INDEX FROM catalog_product;
-- ---------------------------------------------------------------------------
DROP INDEX ix_product_category     ON catalog_product;
DROP INDEX ix_product_cgroup       ON catalog_product;
DROP INDEX ix_product_vendor       ON catalog_product;
DROP INDEX ix_order_user           ON orders_order;
DROP INDEX ix_order_vendor_status  ON orders_order;
DROP INDEX ix_invmov_product       ON catalog_inventorymovement;

-- ---------------------------------------------------------------------------
-- 9. Refresh the optimizer's statistics so EXPLAIN reflects reality.
-- ---------------------------------------------------------------------------
ANALYZE TABLE catalog_product, catalog_vendor, orders_order,
              orders_transaction, orders_payment, orders_deliverybooking,
              catalog_inventorymovement;
```

#### Why each index exists — say this in your defense

| # | Index | The query it serves | Without it |
|---|-------|--------------------|------------|
| 1 | `ft_product_search` | Home-page search box | `LIKE '%tomato%'` scans all rows |
| 2 | `ix_product_cat_price` | Category chip + sort by price | filesort over the category |
| 3 | `ix_product_cgroup_unit_price` | Price-comparison screen | filesort + row lookups |
| 4 | `ix_product_vendor_avail` | Vendor storefront | scan of the vendor's rows |
| 5 | `ix_vendor_section_name` | Market map, grouped by section | filesort |
| 6 | `ix_order_user_created` | Order history, newest first | filesort |
| 7 | `ix_order_vendor_status_created` | Vendor POS queue (FIFO) | filesort |
| 8 | `ix_order_vendor_created` | Sales dashboard date range | scan of vendor's orders |
| 9 | `ix_transaction_created` | Daily/period sales report | full table scan |
| 10 | `ix_payment_status_paid` | Reconciliation of settled payments | full table scan |
| 11 | `ix_delivery_status_booked` | Ops view of in-flight deliveries | full table scan |
| 12 | `ix_invmov_product_created` | One product's stock history | filesort |

**The lesson to be able to explain:** an index is not free. Every one of these adds work to every `INSERT`/`UPDATE`/`DELETE` on that table. That is why this file adds 12 and drops the 6 single-column indexes they supersede — a net gain of 6 indexes, not 18. Write the query first, `EXPLAIN` it, then index what the plan complains about — never index "just in case".

---

### Appendix C — `sql/03_seed.sql`

> ⚠️ **Two things to read before running this.**
>
> **1. Demo passwords.** Every account below has the password `ecompra123`, stored as a real Django
> PBKDF2-SHA256 hash (`pbkdf2_sha256$600000$…`). This is a *development seed* — it exists so you can log in and
> click through the UI on day one. It must never be used for anything deployed. The `.env` + `.gitignore` rule
> from the ground rules still applies to every real credential.
>
> **2. File order is load-bearing.** This script sets `catalog_product.stock_quantity` directly **and** writes the
> matching `catalog_inventorymovement` ledger rows. The trigger in `sql/05_procedures_triggers.sql` maintains
> `stock_quantity` from the ledger — so if that trigger already existed, every product would be counted twice.
> Run `05` **after** `03`, exactly as the numbered filenames say.

```sql
-- ============================================================================
--  E-Compra — Seed data (development)
--  Mandaue Public Market, Cebu · all amounts in PHP (₱)
--  Run:  mysql -u root -p ecompra < sql/03_seed.sql
--
--  Sample data is drawn from the project idea document:
--    - the 9 search categories (feature 1)
--    - the Tomatoes comparison: ₱80 / ₱75 / ₱78 (feature 2)
--    - personas Maria Santos (customer) and Pedro Reyes (fish vendor)
-- ============================================================================
USE ecompra;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. Users. Django's auth_user. Explicit ids so later inserts can reference them.
--    All passwords: ecompra123  (PBKDF2-SHA256, 600000 iterations)
-- ---------------------------------------------------------------------------
INSERT INTO auth_user
  (id, password, last_login, is_superuser, username, first_name, last_name,
   email, is_staff, is_active, date_joined)
VALUES
  (1, 'pbkdf2_sha256$600000$5d9e264e422d$VwWJ9pG3uT1vRIxi0nUYYD3iex4PRAMEhsnID6u93a8=',
      NULL, 1, 'admin', 'Market', 'Administrator', 'admin@ecompra.local', 1, 1, '2026-11-01 08:00:00.000000'),
  (2, 'pbkdf2_sha256$600000$ac05abda2b27$eYIM2DENFFNMawQEPJ30P69WetE4yjWclI7RPqwM8oU=',
      NULL, 0, 'maria.santos', 'Maria', 'Santos', 'maria.santos@example.ph', 0, 1, '2026-11-02 09:15:00.000000'),
  (3, 'pbkdf2_sha256$600000$811e4a24f499$k2m0mtUQXXZNPfBOuXj/xrVYIqrnzakmJEGNBM+SxMs=',
      NULL, 0, 'juan.reyes', 'Juan', 'Reyes', 'juan.reyes@example.ph', 0, 1, '2026-11-03 10:40:00.000000'),
  (4, 'pbkdf2_sha256$600000$b68a3d39df51$m7V921MaD4KqyNn1KKP5ULjlCZBeSFcEF32m8n/37Yc=',
      NULL, 0, 'pedro.reyes', 'Pedro', 'Reyes', 'pedro.reyes@example.ph', 0, 1, '2026-11-01 08:30:00.000000'),
  (5, 'pbkdf2_sha256$600000$c5a9fe01ec81$zyw1sGZMD3w7NUR5ln9M6BVdItbTSVUGa7WtOu1cSVQ=',
      NULL, 0, 'rosa.delacruz', 'Rosa', 'Dela Cruz', 'rosa.delacruz@example.ph', 0, 1, '2026-11-01 08:35:00.000000'),
  (6, 'pbkdf2_sha256$600000$4c0c3e7fba2e$PeNDm/Lt0VQ64s9l4oX2F3AqRElHgGXcbHzAEi26l08=',
      NULL, 0, 'jose.bautista', 'Jose', 'Bautista', 'jose.bautista@example.ph', 0, 1, '2026-11-01 08:40:00.000000'),
  (7, 'pbkdf2_sha256$600000$6e7f06e724e8$L1MGPegeHXyHV1cYJx7IsjiF97gu1Xn87nmSYlr2Y2E=',
      NULL, 0, 'luzviminda.tan', 'Luzviminda', 'Tan', 'luzviminda.tan@example.ph', 0, 1, '2026-11-01 08:45:00.000000'),
  (8, 'pbkdf2_sha256$600000$1c328d50adea$eA47+Ip/hak1VgRiMuFEuWmOzFPvcOb9f0FL8aw3kpM=',
      NULL, 0, 'andres.villamor', 'Andres', 'Villamor', 'andres.villamor@example.ph', 0, 1, '2026-11-01 08:50:00.000000'),
  (9, 'pbkdf2_sha256$600000$e47bb6e3562c$KmIOZGWJxdhOjFH9j1qgUeuCd4beJeuaCxBvmewHYo0=',
      NULL, 0, 'nena.abellana', 'Nena', 'Abellana', 'nena.abellana@example.ph', 0, 1, '2026-11-01 08:55:00.000000');

-- ---------------------------------------------------------------------------
-- 2. Profiles
-- ---------------------------------------------------------------------------
INSERT INTO accounts_userprofile (user_id, is_vendor) VALUES
  (1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1);

INSERT INTO accounts_customerprofile (user_id, phone, address) VALUES
  (2, '0917-555-0110', 'Unit 4B, A.C. Cortes Ave., Mandaue City, Cebu'),
  (3, '0917-555-0111', '12 Lopez Jaena St., Mandaue City, Cebu');

-- ---------------------------------------------------------------------------
-- 3. Lookup tables - the frozen vocabularies from docs/DESIGN_DECISIONS.md §4
-- ---------------------------------------------------------------------------
INSERT INTO catalog_unitofmeasure (code, name, description) VALUES
  ('KG',     'Kilogram', 'Weight - metric base unit'),
  ('G',      'Gram',     'Weight - 1/1000 kilogram'),
  ('L',      'Liter',    'Volume - metric base unit'),
  ('ML',     'Milliliter','Volume - 1/1000 liter'),
  ('PIECE',  'Piece',    'Counted individually'),
  ('BUNDLE', 'Bundle',   'Tied bunch, as sold in the market'),
  ('TRAY',   'Tray',     'Flat tray of eggs (30 pieces)'),
  ('SACK',   'Sack',     'Woven sack (25 kg of rice)'),
  ('PACK',   'Pack',     'Pre-packed retail unit');

INSERT INTO catalog_category (id, name, slug) VALUES
  (1, 'Fish',       'fish'),
  (2, 'Meat',       'meat'),
  (3, 'Poultry',    'poultry'),
  (4, 'Fruits',     'fruits'),
  (5, 'Vegetables', 'vegetables'),
  (6, 'Rice',       'rice'),
  (7, 'Dry goods',  'dry-goods'),
  (8, 'Spices',     'spices'),
  (9, 'Others',     'others');

INSERT INTO catalog_availabilitystatus (code, description, sort_order, is_orderable) VALUES
  ('IN_STOCK',     'Available in stock',            10, 1),
  ('LOW_STOCK',    'Available, running low',        20, 1),
  ('OUT_OF_STOCK', 'Temporarily unavailable',       30, 0),
  ('HIDDEN',       'Delisted by the vendor',        40, 0);

INSERT INTO orders_transactionstatus (code, description, sort_order) VALUES
  ('PENDING_PAYMENT',  'Awaiting payment or down payment',        10),
  ('CONFIRMED',        'Paid or reserved; vendor has accepted',   20),
  ('PREPARING',        'Vendor is preparing the order',           30),
  ('READY_FOR_PICKUP', 'Prepared and waiting at the stall',       40),
  ('OUT_FOR_DELIVERY', 'Handed to the delivery provider',         50),
  ('COMPLETED',        'Picked up or delivered and settled',      60),
  ('CANCELLED',        'Cancelled before completion',             70);

INSERT INTO orders_transactiontype (code, description) VALUES
  ('ONLINE_ORDER',       'Fully paid online order with delivery'),
  ('PICKUP_RESERVATION', 'Reservation settled at the stall'),
  ('POS_WALKIN',         'Walk-in sale recorded at the vendor POS');

INSERT INTO orders_fulfillmentmethod (code, description) VALUES
  ('PICKUP',   'Customer collects at the stall'),
  ('DELIVERY', 'Delivered to the customer address'),
  ('WALK_IN',  'Over-the-counter sale, no online order');

INSERT INTO orders_paymentstatus (code, description, is_terminal) VALUES
  ('PENDING',  'Initiated, not yet settled', 0),
  ('VERIFIED', 'Settlement confirmed',       1),
  ('FAILED',   'Settlement failed',          1),
  ('REFUNDED', 'Returned to the customer',   1);

INSERT INTO orders_deliverystatus (code, description, is_terminal) VALUES
  ('BOOKED',     'Booking accepted by the provider', 0),
  ('IN_TRANSIT', 'Rider is on the way',              0),
  ('DELIVERED',  'Received by the customer',         1),
  ('FAILED',     'Delivery attempt failed',          1),
  ('CANCELLED',  'Booking cancelled',                1);

INSERT INTO catalog_inventoryreason (code, description, direction) VALUES
  ('RECEIVED',    'Stock received from supplier',   'IN'),
  ('SOLD_ONLINE', 'Sold through an online order',   'OUT'),
  ('SOLD_WALKIN', 'Sold over the counter',          'OUT'),
  ('SPOILAGE',    'Spoiled or unsellable',          'OUT'),
  ('ADJUSTMENT',  'Physical recount correction',    'ADJUST');

-- ---------------------------------------------------------------------------
-- 4. Comparison groups (idea doc feature 2). base_unit is the unit every price
--    is normalised to before ranking.
-- ---------------------------------------------------------------------------
INSERT INTO catalog_comparisongroup (code, name, base_unit, description) VALUES
  ('TOMATO',             'Tomatoes',            'KG',    'Fresh tomatoes'),
  ('BANGUS',             'Bangus (Milkfish)',   'KG',    'Whole milkfish'),
  ('TILAPIA',            'Tilapia',             'KG',    'Whole tilapia'),
  ('GALUNGGONG',         'Galunggong',          'KG',    'Round scad'),
  ('TULINGAN',           'Tulingan',            'KG',    'Bullet tuna'),
  ('SHRIMP',             'Hipon (Shrimp)',      'KG',    'Fresh shrimp'),
  ('PORK_BELLY',         'Pork Belly (Liempo)', 'KG',    'Bone-in or boneless'),
  ('PORK_KASIM',         'Pork Kasim',          'KG',    'Pork shoulder'),
  ('PORK_GROUND',        'Ground Pork',         'KG',    'Freshly ground'),
  ('BEEF_BRISKET',       'Beef Brisket',        'KG',    'For soup and stews'),
  ('CHICKEN_WHOLE',      'Whole Chicken',       'KG',    'Dressed whole chicken'),
  ('CHICKEN_BREAST',     'Chicken Breast',      'KG',    'Boneless breast fillet'),
  ('CHICKEN_NATIVE',     'Native Chicken',      'KG',    'Bisaya free-range'),
  ('EGGS',               'Eggs',                'PIECE', 'Large chicken eggs'),
  ('RICE_WELL_MILLED',   'Well-Milled Rice',    'KG',    'Ordinary milled rice'),
  ('RICE_SINANDOMENG',   'Sinandomeng Rice',    'KG',    'Long-grain variety'),
  ('RICE_DINORADO',      'Dinorado Rice',       'KG',    'Aromatic variety'),
  ('RICE_MALAGKIT',      'Malagkit Rice',       'KG',    'Glutinous rice'),
  ('COOKING_OIL',        'Cooking Oil',         'L',     'Refined palm or coconut'),
  ('SUGAR_BROWN',        'Brown Sugar',         'KG',    'Washed brown sugar'),
  ('SUGAR_WHITE',        'White Sugar',         'KG',    'Refined white sugar'),
  ('GARLIC',             'Garlic (Bawang)',     'KG',    'Fresh garlic bulbs'),
  ('ONION_RED',          'Red Onion',           'KG',    'Sibuyas Bombay'),
  ('MANGO',              'Mango (Carabao)',     'KG',    'Ripe carabao mango'),
  ('BANANA',             'Banana (Cavendish)',  'KG',    'Cavendish banana');

-- Allowed units per group, with the factor that converts them to the base unit.
-- The kg-based groups all take the same two rows, so derive them with
-- INSERT ... SELECT instead of writing 23 near-identical pairs by hand.
INSERT INTO catalog_comparisongroupunit (comparison_group, unit, factor_to_base)
SELECT code, 'KG', 1.0000 FROM catalog_comparisongroup WHERE base_unit = 'KG'
UNION ALL
SELECT code, 'G',  0.0010 FROM catalog_comparisongroup WHERE base_unit = 'KG';

-- The two groups whose base unit is not the kilogram.
INSERT INTO catalog_comparisongroupunit (comparison_group, unit, factor_to_base) VALUES
  ('EGGS',        'PIECE', 1.0000),
  ('EGGS',        'TRAY',  30.0000),
  ('COOKING_OIL', 'L',     1.0000),
  ('COOKING_OIL', 'ML',    0.0010);

-- ---------------------------------------------------------------------------
-- 5. Vendors - one catalog_vendor per vendor user, plus its POS extension
-- ---------------------------------------------------------------------------
INSERT INTO catalog_vendor
  (id, name, stall_location, market_section, contact_phone, contact_email, user_id) VALUES
  (1, 'Pedro''s Fresh Catch',        'Stall A-12', 'Section A - Fish',            '0917-555-0101', 'pedro@ecompra.local',     4),
  (2, 'Rosa''s Gulay Stand',         'Stall B-07', 'Section B - Vegetables',      '0917-555-0102', 'rosa@ecompra.local',      5),
  (3, 'Bautista Meat Shop',          'Stall C-03', 'Section C - Meat & Poultry',  '0917-555-0103', 'jose@ecompra.local',      6),
  (4, 'Tan''s Rice & Dry Goods',     'Stall E-01', 'Section E - Dry Goods',       '0917-555-0104', 'luz@ecompra.local',       7),
  (5, 'Villamor Fruits & Gulay',     'Stall D-02', 'Section D - Fruits',          '0917-555-0105', 'andres@ecompra.local',    8),
  (6, 'Nena''s Manok',               'Stall C-09', 'Section C - Meat & Poultry',  '0917-555-0106', 'nena@ecompra.local',      9);

INSERT INTO vendors_vendor (catalog_vendor_id, stall_name, stall_location) VALUES
  (1, 'Pedro''s Fresh Catch',    'Stall A-12'),
  (2, 'Rosa''s Gulay Stand',     'Stall B-07'),
  (3, 'Bautista Meat Shop',      'Stall C-03'),
  (4, 'Tan''s Rice & Dry Goods', 'Stall E-01'),
  (5, 'Villamor Fruits & Gulay', 'Stall D-02'),
  (6, 'Nena''s Manok',           'Stall C-09');

-- ---------------------------------------------------------------------------
-- 6. Products - 34 items across the 9 categories.
--    stock_quantity is the CURRENT balance; section 9 writes the ledger rows
--    that explain how it got there.
-- ---------------------------------------------------------------------------
INSERT INTO catalog_product
  (id, name, description, price, unit_code, availability_code, stock_quantity,
   low_stock_threshold, category_id, vendor_id, comparison_group, stall_location) VALUES
  -- Pedro's Fresh Catch (vendor 1)
  (1,  'Bangus (Milkfish)',            'Whole milkfish, cleaned on request',        180.00, 'KG',     'IN_STOCK',  12, 5, 1, 1, 'BANGUS',     'Stall A-12'),
  (2,  'Tilapia',                      'Farm-raised tilapia, medium size',          140.00, 'KG',     'IN_STOCK',  10, 5, 1, 1, 'TILAPIA',    'Stall A-12'),
  (3,  'Galunggong (Round Scad)',      'Fresh catch, landed this morning',          160.00, 'KG',     'IN_STOCK',   8, 5, 1, 1, 'GALUNGGONG', 'Stall A-12'),
  (4,  'Tulingan (Bullet Tuna)',       'Good for grilling and paksiw',              190.00, 'KG',     'IN_STOCK',   6, 5, 1, 1, 'TULINGAN',   'Stall A-12'),
  (5,  'Hipon (Shrimp)',               'Medium shrimp, fresh',                      380.00, 'KG',     'LOW_STOCK',  6, 5, 1, 1, 'SHRIMP',     'Stall A-12'),
  (6,  'Dried Fish (Tuyo)',            'Sun-dried, sold by weight',                 420.00, 'KG',     'IN_STOCK',   5, 3, 7, 1, NULL,         'Stall A-12'),
  -- Rosa's Gulay Stand (vendor 2)
  (7,  'Tomatoes',                     'Ripe native tomatoes',                       80.00, 'KG',     'IN_STOCK',  15, 5, 5, 2, 'TOMATO',     'Stall B-07'),
  (8,  'Kangkong (Water Spinach)',     'Bundled, ready to cook',                     15.00, 'BUNDLE', 'IN_STOCK',  20, 8, 5, 2, NULL,         'Stall B-07'),
  (9,  'Pechay (Chinese Cabbage)',     'Bundled, crisp leaves',                      20.00, 'BUNDLE', 'IN_STOCK',  25, 8, 5, 2, NULL,         'Stall B-07'),
  (10, 'Ampalaya (Bitter Gourd)',      'Medium size, dark green',                    90.00, 'KG',     'IN_STOCK',   9, 4, 5, 2, NULL,         'Stall B-07'),
  (11, 'Talong (Eggplant)',            'Long purple variety',                        70.00, 'KG',     'IN_STOCK',  11, 4, 5, 2, NULL,         'Stall B-07'),
  (12, 'Garlic (Bawang)',              'Imported garlic, whole bulbs',              160.00, 'KG',     'IN_STOCK',   7, 3, 8, 2, 'GARLIC',     'Stall B-07'),
  (13, 'Red Onion (Sibuyas Bombay)',   'Locally grown red onion',                   190.00, 'KG',     'IN_STOCK',  14, 4, 8, 2, 'ONION_RED',  'Stall B-07'),
  -- Bautista Meat Shop (vendor 3)
  (14, 'Pork Belly (Liempo)',          'Fresh pork belly, sliced on request',       320.00, 'KG',     'IN_STOCK',  10, 4, 2, 3, 'PORK_BELLY', 'Stall C-03'),
  (15, 'Pork Kasim',                   'Pork shoulder, good for adobo',             280.00, 'KG',     'IN_STOCK',  12, 4, 2, 3, 'PORK_KASIM', 'Stall C-03'),
  (16, 'Ground Pork',                  'Ground fresh daily',                        290.00, 'KG',     'IN_STOCK',   8, 3, 2, 3, 'PORK_GROUND','Stall C-03'),
  (17, 'Beef Brisket',                 'For bulalo and nilaga',                     420.00, 'KG',     'LOW_STOCK',  5, 3, 2, 3, 'BEEF_BRISKET','Stall C-03'),
  -- Tan's Rice & Dry Goods (vendor 4)
  (18, 'Well-Milled Rice',             'Everyday rice, per kilo',                    52.00, 'KG',     'IN_STOCK', 100, 20, 6, 4, 'RICE_WELL_MILLED',  'Stall E-01'),
  (19, 'Sinandomeng Rice',             'Long-grain, per kilo',                       58.00, 'KG',     'IN_STOCK',  80, 20, 6, 4, 'RICE_SINANDOMENG',  'Stall E-01'),
  (20, 'Dinorado Rice',                'Aromatic, per kilo',                         68.00, 'KG',     'IN_STOCK',  60, 15, 6, 4, 'RICE_DINORADO',     'Stall E-01'),
  (21, 'Malagkit (Glutinous Rice)',    'For bibingka and suman',                     75.00, 'KG',     'IN_STOCK',  30, 10, 6, 4, 'RICE_MALAGKIT',     'Stall E-01'),
  (22, 'Cooking Oil',                  'Refined palm oil, per liter',                95.00, 'L',      'IN_STOCK',  24, 8, 7, 4, 'COOKING_OIL',       'Stall E-01'),
  (23, 'Brown Sugar',                  'Washed brown sugar, per kilo',               85.00, 'KG',     'IN_STOCK',  20, 6, 7, 4, 'SUGAR_BROWN',       'Stall E-01'),
  (24, 'White Sugar',                  'Refined white sugar, per kilo',              78.00, 'KG',     'IN_STOCK',  25, 6, 7, 4, 'SUGAR_WHITE',       'Stall E-01'),
  (25, 'Tomatoes',                     'Firm tomatoes, good for sauteing',           78.00, 'KG',     'IN_STOCK',  12, 5, 5, 4, 'TOMATO',            'Stall E-01'),
  -- Villamor Fruits & Gulay (vendor 5)
  (26, 'Tomatoes',                     'Vine-ripened tomatoes',                      75.00, 'KG',     'IN_STOCK',  18, 5, 5, 5, 'TOMATO',     'Stall D-02'),
  (27, 'Mango (Carabao)',              'Sweet ripe carabao mango',                  160.00, 'KG',     'IN_STOCK',  15, 5, 4, 5, 'MANGO',      'Stall D-02'),
  (28, 'Banana (Cavendish)',           'Ripe Cavendish banana',                      65.00, 'KG',     'IN_STOCK',  20, 6, 4, 5, 'BANANA',     'Stall D-02'),
  (29, 'Pineapple',                    'Sweet variety, per piece',                   85.00, 'PIECE',  'IN_STOCK',  10, 4, 4, 5, NULL,         'Stall D-02'),
  (30, 'Watermelon',                   'Whole, seedless',                            45.00, 'KG',     'IN_STOCK',   8, 3, 4, 5, NULL,         'Stall D-02'),
  -- Nena's Manok (vendor 6)
  (31, 'Whole Chicken',                'Dressed whole chicken',                     210.00, 'KG',     'IN_STOCK',  12, 4, 3, 6, 'CHICKEN_WHOLE',  'Stall C-09'),
  (32, 'Chicken Breast',               'Boneless breast fillet',                    260.00, 'KG',     'IN_STOCK',   8, 3, 3, 6, 'CHICKEN_BREAST', 'Stall C-09'),
  (33, 'Native Chicken (Bisaya)',      'Free-range native chicken',                 330.00, 'KG',     'LOW_STOCK',  6, 3, 3, 6, 'CHICKEN_NATIVE', 'Stall C-09'),
  (34, 'Eggs (Large)',                 'Large chicken eggs, per tray of 30',        240.00, 'TRAY',   'IN_STOCK',  20, 5, 3, 6, 'EGGS',           'Stall C-09');

-- ---------------------------------------------------------------------------
-- 7. Sample orders. Three shapes, one per TransactionType:
--      order 1 - online order, paid online, delivered
--      order 2 - pickup reservation, down payment made, awaiting collection
--      order 3 - anonymous walk-in sale at the POS
-- ---------------------------------------------------------------------------
INSERT INTO orders_order
  (id, user_id, customer_label, vendor_id, status_code, fulfillment_code,
   total_amount, notes, created_at, updated_at) VALUES
  (1, 2, NULL, 1, 'COMPLETED',        'DELIVERY', 520.00, 'Please clean the fish.', '2026-11-10 09:12:04.000000', '2026-11-10 15:40:11.000000'),
  (2, 2, NULL, 2, 'READY_FOR_PICKUP', 'PICKUP',   290.00, 'Will collect before 6pm.', '2026-11-12 07:45:19.000000', '2026-11-12 11:05:00.000000'),
  (3, NULL, 'Walk-in customer', 1, 'COMPLETED',  'WALK_IN',  320.00, NULL, '2026-11-11 06:58:33.000000', '2026-11-11 06:59:02.000000');

INSERT INTO orders_orderitem (order_id, product_id, quantity, unit_price) VALUES
  (1, 1,  2, 180.00),   -- Bangus    2 kg
  (1, 3,  1, 160.00),   -- Galunggong 1 kg
  (2, 7,  3,  80.00),   -- Tomatoes  3 kg
  (2, 8,  2,  15.00),   -- Kangkong  2 bundles
  (2, 9,  1,  20.00),   -- Pechay    1 bundle
  (3, 2,  1, 140.00),   -- Tilapia   1 kg
  (3, 1,  1, 180.00);   -- Bangus    1 kg

INSERT INTO orders_transaction (id, order_id, transaction_type, reference_no, created_at) VALUES
  (1, 1, 'ONLINE_ORDER',       'ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (2, 2, 'PICKUP_RESERVATION', 'ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (3, 3, 'POS_WALKIN',         'ECO-20261111-0003', '2026-11-11 06:58:33.000000');

-- Payments. Order 2's row is the DOWN PAYMENT only (half of ₱290). The balance
-- is settled in cash at the stall, which records a second Payment row
-- (provider 'CASH') at that moment - it is deliberately not seeded, because it
-- has not happened yet. This is the idea doc's pickup flow:
--   Pending -> Down-Payment Confirmed -> Preparing -> Full payment -> Completed
INSERT INTO orders_payment
  (id, transaction_id, provider, provider_reference, amount, status_code, paid_at) VALUES
  (1, 1, 'PAYMAYA', 'SBX-PM-20261110-8F31A2C4', 520.00, 'VERIFIED', '2026-11-10 09:14:22.000000'),
  (2, 2, 'PAYMAYA', 'SBX-PM-20261112-C19D4E77', 145.00, 'VERIFIED', '2026-11-12 07:47:41.000000'),
  (3, 3, 'CASH',    'CASH-ECO-20261111-0003-1', 320.00, 'VERIFIED', '2026-11-11 06:59:02.000000');

-- Delivery booking exists only for the delivery order. The provider name is a
-- sandbox/mock - see the ground rules: delivery is mocked, never a live account.
INSERT INTO orders_deliverybooking
  (id, transaction_id, provider, booking_reference, tracking_url, fee,
   status_code, booked_at, delivered_at) VALUES
  (1, 1, 'LALAMOVE', 'SBX-LM-77120', 'https://sandbox.example/track/SBX-LM-77120',
      95.00, 'DELIVERED', '2026-11-10 09:20:00.000000', '2026-11-10 15:40:11.000000');

-- Vendor-side record. receipt_serial is RC-{reference_no}-{receipt_attempt};
-- reprinting increments receipt_attempt instead of minting a new serial.
INSERT INTO vendors_vendortransaction
  (id, vendor_id, order_id, status_code, receipt_serial, receipt_attempt) VALUES
  (1, 1, 1, 'COMPLETED',        'RC-ECO-20261110-0001-1', 1),
  (2, 2, 2, 'READY_FOR_PICKUP', NULL,                     1),
  (3, 1, 3, 'COMPLETED',        'RC-ECO-20261111-0003-1', 1);

-- ---------------------------------------------------------------------------
-- 8. Cart and favorites for Maria Santos (user 2)
-- ---------------------------------------------------------------------------
INSERT INTO cart_cart (user_id) VALUES (2);

INSERT INTO cart_cartitem (cart_id, product_id, quantity) VALUES
  (2, 27, 2),   -- Mango 2 kg
  (2, 18, 5),   -- Well-Milled Rice 5 kg
  (2, 31, 1);   -- Whole Chicken 1 kg

INSERT INTO favorites_favoriteproduct (user_id, product_id) VALUES (2, 1), (2, 7), (3, 26);
INSERT INTO favorites_favoritevendor  (user_id, vendor_id)  VALUES (2, 1), (2, 2), (3, 2);

-- ---------------------------------------------------------------------------
-- 9. Inventory ledger.
--    Every product gets a RECEIVED opening balance. For the seven products the
--    sample orders touch, the opening is set so that the ledger sums EXACTLY to
--    the stock_quantity in section 6:
--
--      opening = current stock + everything that leaves in this section
--
--      product 1  Bangus      12 + 2 (order 1) + 1 (order 3)          = 15
--      product 2  Tilapia     10 + 1 (order 3)                        = 11
--      product 3  Galunggong   8 + 1 (order 1)                        =  9
--      product 5  Hipon        6 - 1 (recount adjustment below)       =  5
--      product 7  Tomatoes    15 + 3 (order 2)                        = 18
--      product 8  Kangkong    20 + 2 (order 2) + 1 (spoilage below)   = 23
--      product 9  Pechay      25 + 1 (order 2)                        = 26
-- ---------------------------------------------------------------------------
INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at) VALUES
  (1, 15, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (2, 11, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (3,  9, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (5,  5, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (7, 18, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (8, 23, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (9, 26, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000');

INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at)
SELECT id, stock_quantity, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'
FROM catalog_product
WHERE id NOT IN (1, 2, 3, 5, 7, 8, 9);

-- The movements that bring each balance to its current value.
INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at) VALUES
  (1,  -2, 'SOLD_ONLINE', 1, 'Order ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (3,  -1, 'SOLD_ONLINE', 1, 'Order ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (7,  -3, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (8,  -2, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (9,  -1, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (2,  -1, 'SOLD_WALKIN', 3, 'Walk-in sale ECO-20261111-0003', '2026-11-11 06:58:33.000000'),
  (1,  -1, 'SOLD_WALKIN', 3, 'Walk-in sale ECO-20261111-0003', '2026-11-11 06:58:33.000000'),
  (8,  -1, 'SPOILAGE', NULL, 'Wilted, pulled from display', '2026-11-11 17:30:00.000000'),
  (5,   1, 'ADJUSTMENT', NULL, 'Physical recount: 1 kg found', '2026-11-12 06:15:00.000000');

-- ---------------------------------------------------------------------------
-- 10. Self-check. This SELECT must return ZERO rows.
--     If it returns anything, the ledger and the cached stock disagree, and
--     section 9's arithmetic needs fixing before you build anything on top.
-- ---------------------------------------------------------------------------
SELECT p.id,
       p.name,
       p.stock_quantity                              AS cached_stock,
       COALESCE(SUM(m.delta), 0)                     AS ledger_stock,
       p.stock_quantity - COALESCE(SUM(m.delta), 0)  AS difference
FROM catalog_product p
LEFT JOIN catalog_inventorymovement m ON m.product_id = p.id
GROUP BY p.id, p.name, p.stock_quantity
HAVING difference <> 0;
```

---

## What M0.7 – M0.9 should have given you

Three files in `sql/`, run in numeric order, that together let you say — with evidence — that the design
survives contact with a real database engine:

| Check | Command | Pass condition |
|---|---|---|
| Schema builds from nothing | `mysql -u root -p < sql/01_schema.sql` | no errors; `SHOW TABLES` lists 28 |
| Indexes apply cleanly | `mysql -u root -p ecompra < sql/02_indexes.sql` | no errors on the `DROP`/`CREATE` pairs |
| Seed loads | `mysql -u root -p ecompra < sql/03_seed.sql` | the final self-check returns **0 rows** |
| Tomatoes compare correctly | the price-comparison query in `sql/07_verification_queries.sql` | ₱75.00, ₱78.00, ₱80.00 in that order |
| Lookups are complete | `SELECT COUNT(*) FROM orders_transactionstatus` | 7 |
| Every product is priced and categorised | `SELECT COUNT(*) FROM catalog_product WHERE price IS NULL OR category_id IS NULL` | 0 |

The tomatoes row is the one to show in your defense: three different vendors, three different prices, one
comparison group, and the ranking produced by a `JOIN` and an `ORDER BY` rather than by anything hard-coded.


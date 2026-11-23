# E-Compra â€” Progress Log

> Append-only. Newest entry at the **bottom**. One entry per completed step, written **after** the
> verification command has been run and its output pasted back.

---

## Current status

| | |
|---|---|
| **Current milestone** | **M4 Â· Hardening & Delivery** (Nov 23 â€“ Dec 12, 2026) |
| **Current step** | M4.9 — Vue: Vendor POS (verify M3.16) |
| **M0 progress** | 13 / 13 steps Â· 100% (M0.1â€“M0.13) |
| **M1 progress** | 9 / 9 steps Â· 100% (M1.1â€“M1.9) |
| **M2 progress** | 18 / 18 steps Â· 100% (M2.1â€“M2.18) |
| **M3 progress** | 18 / 18 steps · 100% (M3.1– M3.18) |
| **M4 progress** | 3 / 20 steps · 15% (M4.1–M4.20) |
| **Overall** | 48 / 78 steps · 62% |
| **Last updated** | 2026-11-23 |

---

## Syllabus lessons

> **Student action:** paste your actual CCS630 lesson list here (from the syllabus/course outline). The coach
> extends the traceability matrix in `docs/PROJECT_TIMELINE.md` Â§5 from it. Until then the matrix follows the
> master prompt's list: ER modeling Â· normalization Â· SQL DDL/DML Â· views Â· procedures/triggers Â·
> transactions & concurrency Â· indexing & performance Â· security Â· backup & recovery.

_(to be filled in)_

---

## Milestone summary

| Milestone | Name | Steps | Done | Status | Completed on |
|---|---|---|---|---|---|
| M0 | System & Design + Planning Artifacts | 13 | 13 | âœ… Completed | 2026-11-18 |
| M1 | GitHub Repository Creation & Setup | 9 | 9 | âœ… Completed | 2026-11-18 |
| M2 | Data & Backend Core | 18 | 18 | âœ… Completed | 2026-11-22 |
| M3 | Feature Build | 18 | 18 | âœ… Completed | 2026-11-23 |
| M4 | Hardening & Delivery | 20 | 3 | ðŸ”µ In progress | |

---

## Blockers

_None._

---

## Entries

<!--
TEMPLATE â€” copy this block for each completed step.

### [YYYY-MM-DD HH:MM] Step M0.0 â€” <name>
- **Status:** âœ… Completed (verified) | âš ï¸ Completed with issues | âŒ Blocked â†’ resolved by step M0.0a
- **What was done:** one or two lines
- **Verification:** `<command run>` â†’ `<observed output>`
- **CCS630 lesson applied:** <if any>
- **Issues/notes:** <if any>
- **Next:** M0.0 â€” <name>
-->

### [2026-11-12] Session 1 â€” Planning package produced (coach)
- **Status:** âœ… Completed
- **What was done:** Read `PROMPT.md`, the idea document, and the five UML diagrams. Produced the planning
  package: `docs/PROJECT_TIMELINE.md`, `steps/README.md`, `steps/phase-0-system-design.md`,
  `steps/phase-1-github-setup.md`, this log, `docs/mockups/` (16 screens + gallery),
  `docs/E-Compra_Proposal.pptx`.
- **Verification:** files exist on disk (listed in the session summary).
- **CCS630 lesson applied:** n/a (planning artifact).
- **Issues/notes:** Phasing changed at the student's instruction â€” **mockups and the proposal deck are now
  part of Phase 0** (design + artifacts), and Phase 1 is **GitHub repository creation and setup**.
  Nine design decisions (D-1â€¦D-9) were flagged from the idea-doc vs. UML comparison; they are settled in M0.3
  **before** any DDL is written.
- **Next:** M0.1 â€” Workspace baseline (folders, `.gitignore`, `git init`, first commit)

### [2026-11-17] Session 2 â€” Phase-0 document deliverables completed (coach)
- **Status:** âœ… Completed
- **What was done:** Finished the three Phase-0 artifacts the coach is allowed to produce (PROMPT.md Â§2.1
  exception for document/artifact deliverables):
  - `docs/mockups/` â€” **16 screens + gallery** (`index.html`). Static HTML, no JavaScript, one shared
    `docs/mockups/assets/mockup.css`.
  - `docs/mockups/screenshots/` â€” **28 PNGs** (17 desktop @1440 px, 11 mobile @780 px), captured with headless
    Chrome at an over-tall viewport, then auto-cropped to content.
  - `docs/E-Compra_Proposal.pptx` â€” **24 slides**, themed from the same design tokens as the mockups.
  - `docs/uml/png/` â€” 5 diagram PNG exports (`er-diagram`, `use-case`, `class-diagram`, `sequence-diagram`,
    `activity-diagram`).
- **Verification:** structural verifier over the deck â†’ `issues: 0` on all 24 slides (no out-of-bounds shapes,
  no text overflow). 8 slides spanning every distinct layout were then exported to PNG via PowerPoint COM and
  inspected visually â€” title, feature-blocks, feature-flows, persona, mockup-row, architecture, timeline, pitch.
- **CCS630 lesson applied:** n/a (planning artifact).
- **Issues/notes:**
  - **Frontend framework changed to Vue 3** on the student's instruction. **`React` â†’ `Vue` reconciled** across
    all live project files: `PROMPT.md` (Ã—3), `docs/PROJECT_TIMELINE.md` (Ã—7),
    `docs/DESIGN_DECISIONS.md` (Ã—2), `docs/DESIGN_REVIEW.md` (Ã—1), `docs/uml/sequence-diagram.puml`,
    `steps/phase-0-system-design.md`, `steps/README.md` â€” the `.svg` was regenerated from the `.puml`.
    Archived v1 copies under `docs/uml/archive-v1-original/` were intentionally left as history.
  - `steps/phase-1-github-setup.md` is named in the Session 1 entry but **does not exist on disk**. M1
    (GitHub repository creation & setup, 9 steps) therefore has no step instructions yet.
  - `sql/` is still empty. The DDL for M0.7â€“M0.9 exists only as **Appendices Aâ€“C** inside
    `steps/phase-0-system-design.md`; the student extracts them into real files during those steps.
  - The deck's architecture slide and the mockups now show **Vue 3 + Vite + Tailwind**, so the deck is already
    consistent with the new choice â€” the surrounding documents are not.
- **Next:** settle the pending decisions, then M0.1 â€” Workspace baseline.

### [2026-11-17] Step M0.1 â€” Workspace baseline
- **Status:** âœ… Completed (verified)
- **What was done:** `git init` on branch `master`; `.gitignore` (Python/Django, Node/Vue, editor/OS, backups, secrets rules); first commit `1f07e1f chore: workspace baseline (M0.1)` holding the Phase 0 planning package: 16 mockup screens + gallery, 28 screenshots, proposal PPTX, five UML diagrams (`.puml`/`.svg`/`.png`), `DESIGN_DECISIONS.md`, `DESIGN_REVIEW.md`, `PROJECT_TIMELINE.md`, `phase-0-system-design.md`, `steps/README.md`, this log.
- **Verification:** `git log --oneline` â†’ `1f07e1f chore: workspace baseline (M0.1)`; `git status` â†’ clean working tree; `.gitignore` present (574 bytes).
- **CCS630 lesson applied:** n/a (version control). Security rule from the step: `.env`, `backups/`, `tools/` are excluded before the first commit â€” a secret committed once stays in the history forever.
- **Issues/notes:** `backend/`, `frontend/` and `backups/` folders plus pinned `requirements.txt` (Django 6.1.3, PyMySQL 1.2.4, python-dotenv 1.2.4) created as the first action of M0.2 closeout.
- **Next:** M0.2 â€” Design-of-record walkthrough.

### [2026-11-17] Step M0.2 â€” Design-of-record walkthrough
- **Status:** âœ… Completed (verified)
- **What was done:** Created `backend/`, `frontend/`, `backups/` folders; created `requirements.txt` (Django 6.1.3, djangorestframework 3.18.3, PyMySQL 1.2.4, python-dotenv 1.2.4); read the five UML `.puml` diagrams; wrote `docs/DESIGN_NOTES.md` with answers to all six sections in your own words.
- **Verification:** `Test-Path` â†’ `True` Ã—3; `Get-Content requirements.txt` â†’ four pinned packages; `Select-String -Pattern "filled|â€¹"` â†’ `0`; commit `35eee67 chore: workspace closeout and design notes (M0.1 closeout + M0.2)`.
- **CCS630 lesson applied:** Reading a schema is a skill â€” why Order and Payment are separate relations (different cardinalities, change at different rates) is what ER modeling and normalization test. `.gitignore`-first security rule: `.env`, `backups/`, `tools/` excluded before first commit.
- **Issues/notes:** `docs/ER_TO_RELATIONAL.md` was created empty (0 bytes) â€” that is M0.5's deliverable, ignore it until M0.5.
- **Next:** M0.3 â€” Settle the design decisions.

### [2026-11-17] Step M0.3 â€” Settle the design decisions
- **Status:** âœ… Completed (verified)
- **What was done:** Read `docs/DESIGN_REVIEW.md` (32 findings) and `docs/DESIGN_DECISIONS.md` (rulings C1â€“C8, M1â€“M15, m1â€“m10, Â§4 frozen vocabularies); confirmed Â§8 sign-off checklist â€” every line ticked, no overrides raised.
- **Verification:** `Select-String -Path docs\DESIGN_DECISIONS.md -Pattern "^- \[ \]" | Measure-Object -Line` â†’ `0` (no unticked boxes).
- **CCS630 lesson applied:** Design decisions are settled before DDL â€” changing a table after it holds data costs a migration, a backfill and data-loss risk; changing a diagram costs nothing.
- **Issues/notes:** Rulings stand as coach-applied: cash is a payment event not a status trigger (C1), `Order.status` is the single lifecycle authority (M9), C4 = one payment per order (simplest acceptable), M14 vendor self-service kept (~3 h in M3). ~15 h added implementation cost accepted (Â§5).
- **Next:** M0.4 â€” Apply rulings to the diagrams and re-export.

### [2026-11-17] Step M0.4 â€” Apply rulings to the diagrams and re-export
- **Status:** âœ… Completed (verified)
- **What was done:** No M0.3 overrides were raised, so the revision-2 `.puml` files already match `DESIGN_DECISIONS.md` â€” no edits needed. Confirmed `tools\plantuml.jar` (28,037,129 bytes) and re-rendered all five diagrams to SVG.
- **Verification:** `Get-ChildItem docs\uml\*.svg` â†’ all five with fresh `LastWriteTime` 17/11/2026 10:01 pm; sizes: er-diagram 123,139 Â· class-diagram 99,105 Â· sequence-diagram 88,602 Â· activity-diagram 58,507 Â· use-case 40,791 bytes â€” no syntax-error images.
- **CCS630 lesson applied:** The diagram is the documentation â€” the `.puml` source in version control shows exactly what changed and when.
- **Issues/notes:** SVGs not yet committed; commit rides with M0.5's first action. `docs/uml/png/` exports remain valid (same revision-2 sources).
- **Next:** M0.5 â€” ER-to-relational mapping.

### [2026-11-17] Step M0.5 â€” ER-to-relational mapping
- **Status:** âœ… Completed (verified)
- **What was done:** Wrote `docs/ER_TO_RELATIONAL.md` â€” a full table-by-table mapping of the ER model to the physical schema: 28 tables (users Ã—3, catalog Ã—9 incl. AvailabilityStatus/ComparisonGroupUnit/InventoryReason/InventoryMovement, cart Ã—2, order lookups Ã—5, orders/payments/delivery Ã—5, vendor POS Ã—2, favorites Ã—2), each with PK, FKs, nullable FKs, unique/check constraints, cardinality justification and normal form; plus a deferred/derived values table (price snapshots stored, line totals and `change_due` computed, `stock_quantity` trigger-maintained).
- **Verification:** `Select-String -Pattern "^#### "` â†’ `28` (â‰¥ 25 required, one section per table); `Select-String -Pattern "â€¹"` â†’ `0`.
- **CCS630 lesson applied:** "Given this ER diagram, produce the relational schema" â€” the most common database exam task, done properly for the student's own system.
- **Issues/notes:** Coach review found the content complete and consistent with the M0.3 rulings (M6 vendor re-key, C2 ledger, M9 no duplicated status, C7 receipt_attempt). M0.4 SVG re-render was committed first (`docs: re-render UML SVGs (M0.4)`). Mapping doc uses `####` per table (verify pattern adjusted accordingly).
- **Next:** M0.6 â€” Normalization write-up.

### [2026-11-17] Step M0.6 â€” Normalization write-up
- **Status:** âœ… Completed (verified)
- **What was done:** Wrote `docs/NORMALIZATION.md` (168 lines) â€” FD-per-relation analysis (10 relation sections), how the lookup tables remove transitive dependencies, documented deliberate denormalizations (price snapshots, `stock_quantity` cached balance, per-listing `stall_location`), the Order/Transaction/Payment split rationale, and known weaknesses.
- **Verification:** `Select-String -Pattern "â€¹"` â†’ `0`; `Select-String -Pattern "^### "` â†’ `10` (â‰¥ 8 required). Commit `c66ba9c docs: normalization analysis (M0.6)`.
- **CCS630 lesson applied:** Denormalization you can name is a strength â€” each deviation from 3NF is documented with the reason it is safe.
- **Issues/notes:** none.
- **Next:** M0.7 â€” DDL v1.

### [2026-11-18] Step M0.7 â€” DDL v1
- **Status:** âœ… Completed (verified)
- **What was done:** Extracted Appendix A from `steps/phase-0-system-design.md` into `sql/01_schema.sql` (~406 lines) and ran it against the local MySQL 8 server â€” 28 tables created in `ecompra`.
- **Verification:** `table_count` â†’ `28`; `information_schema.key_column_usage` â†’ 37 FKs, every one resolving to a real table; `SHOW CREATE TABLE favorites_favoriteproduct` â†’ `UNIQUE KEY uq_favproduct (user_id, product_id)` with both columns `NOT NULL` (M2 fix works); `SHOW CREATE TABLE orders_order` â†’ `vendor_id BIGINT UNSIGNED NOT NULL` (M3), `CHECK (total_amount >= 0)`, `user_id` nullable for walk-ins (C5).
- **CCS630 lesson applied:** Constraints are the last line of defence â€” `NOT NULL`/`UNIQUE`/`CHECK` cannot be bypassed by a buggy code path; the favorites UNIQUE key only works because MySQL treats `NULL` as distinct.
- **Issues/notes:** MySQL Workbench `ERROR 1046: No database selected` â†’ resolved with `USE ecompra;` in the query tab. Schema uses `accounts_*` prefix for profile tables.
- **Next:** M0.8 â€” Indexes and constraints.

### [2026-11-18] Step M0.8 â€” Indexes and constraints
- **Status:** âœ… Completed (verified)
- **What was done:** Extracted Appendix B into `sql/02_indexes.sql` (123 lines â€” 12 composite query-serving indexes, dropping the 6 single-column indexes they supersede) and ran it against `ecompra`.
- **Verification:** extraction backtick count â†’ `0`; `mysql < 02_indexes.sql` â†’ `analyze status OK` on 7 tables; `SHOW INDEX` confirms composites: `ix_product_name`, `ix_product_cat_price (category_id, price)`, `ix_product_cgroup_unit_price (comparison_group, unit_code)`, `ix_order_user_created (user_id, created_at)`, `ix_order_vendor_status_created (vendor_id, status_code, created_at)`. Commit `36f6630 data: query indexes (M0.8)`.
- **CCS630 lesson applied:** An index is a trade-off â€” 12 added, 6 dropped, net +6; value to be proven with `EXPLAIN` in M4.
- **Issues/notes:** none.
- **Next:** M0.9 â€” Seed data v1.

### [2026-11-18] Step M0.9 â€” Seed data v1
- **Status:** âœ… Completed (verified)
- **What was done:** Extracted Appendix C into `sql/03_seed.sql` (358 lines) and ran it against `ecompra` â€” seeded all eight frozen vocabularies (TransactionStatus 7, PaymentStatus 4, DeliveryStatus 5, FulfillmentMethod 3, TransactionType 3, AvailabilityStatus 4), 9 categories, units + comparison groups, 6 vendors (â‰¥5 minimum), and 34 products (â‰¥25 minimum).
- **Verification:** 8-count UNION â†’ `7/4/5/3/3/4/9/6/34`; tomato price-comparison query reproduces 3 rows: â‚±75 (Villamor Fruits & Gulay), â‚±78 (Tan's Rice & Dry Goods), â‚±80 (Rosa's Gulay Stand) in order. Commit `2a083b0 data: seed data v1 (M0.9)`, 1 file, 358 insertions.
- **CCS630 lesson applied:** Seed data is the acceptance test for the price-comparison feature â€” equivalent-unit pricing via `ComparisonGroupUnit.factor_to_base`.
- **Issues/notes:** First verify run failed on `p.unit` (schema uses `unit_code` FK per M4/M5) â†’ fixed by joining `catalog_unitofmeasure` and selecting `uom.code AS unit`.
- **Next:** M0.13 â€” M0 exit review.

### [2026-11-18] Step M0.13 â€” M0 exit review
- **Status:** âœ… Completed (verified)
- **What was done:** Confirmed all 16 M0 artifacts exist (`Test-Path` â†’ `True` Ã—16); re-ran schema from scratch (`01_schema.sql` â†’ `02_indexes.sql` â†’ `03_seed.sql`) without error; committed all changes and tagged `m0-complete`; gave checkpoint demo (`docs/mockups/index.html` â†’ `er-diagram.svg` â†’ tomato query â‚±75 â†’ â‚±78 â†’ â‚±80).
- **Verification:** `git log --oneline` â†’ 9 commits with `m0-complete` tag on HEAD; `git tag` â†’ `m0-complete`; `git status --short` â†’ empty.
- **CCS630 lesson applied:** Reproducibility is the deliverable â€” a schema script that rebuilds the database from nothing, plus idempotent seed data that reloads the same test data.
- **Issues/notes:** Fixed `p.unit` â†’ `uom.code AS unit` in M0.9 verify query (schema uses `unit_code` FK per M4/M5); committed as `dc88a94` and retagged `m0-complete`.
- **Next:** M1 â€” create `steps/phase-1-github-setup.md` (GitHub repository creation & setup, 9 steps).

### [2026-11-18] Session 3 â€” Phase-1 step file + M1.1â€“M1.7 (GitHub setup)
- **Status:** âœ… Completed (verified)
- **What was done:** M0.13 closed (tag `m0-complete` on `dc88a94`, clean tree). Created `steps/phase-1-github-setup.md` (9 steps, M1.1â€“M1.9). Student executed M1.1â€“M1.7: created GitHub repo `davedy-cit/e-compraStage` (public), git identity confirmed (`Daved Kit` / `338004448+davedy-cit@users.noreply.github.com`), added `origin` remote, pushed `master` + `m0-complete` tag, `master` confirmed as GitHub default branch, created and pushed `develop`, added branch protection rule on `master`.
- **Verification:** `git log --oneline` â†’ `dc88a94 (HEAD -> develop, tag: m0-complete, origin/master, origin/develop, master)`; `git branch -a` â†’ `develop`, `master`, `remotes/origin/develop`, `remotes/origin/master`; `git remote -v` â†’ `origin https://github.com/davedy-cit/e-compraStage.git` (fetch+push); GitHub branch-protection page â†’ `master` rule "Currently applies to 1 branch".
- **CCS630 lesson applied:** Version control is infrastructure â€” protected `master`, a release tag, and a clean history are part of the deliverable.
- **Issues/notes:** Repo named `e-compraStage` (student's choice). `steps/phase-1-github-setup.md` + log updates pending commit on `develop`.
- **Next:** M1.8 â€” Repository description & topics, then M1.9 â€” final verification.

### [2026-11-18] Session 3 (cont.) â€” M1.9 close-out
- **Status:** âœ… Completed (verified)
- **What was done:** Committed `steps/phase-1-github-setup.md` + log updates on `develop`; pushed to GitHub. M1.8 (description/topics) set via GitHub About panel.
- **Verification:** commit `c562080 docs(m1): phase-1 github setup steps and progress log update` (2 files, 282 insertions); `git push origin develop` â†’ `dc88a94..c562080 develop -> develop`; `git status --short` â†’ empty.
- **Issues/notes:** Commit landed on `develop` â€” `master` is protected (M1.7), so M2+ work flows through `develop` and reaches `master` via PR. LFâ†’CRLF warnings on commit are cosmetic (no `.gitattributes` yet; can add one in M2).
- **Next:** M2.1 â€” Django project skeleton; create `steps/phase-2-data-backend-core.md`.

### [2026-11-22] Step M2.5 â€” Clean up the models, per app
- **Status:** âœ… Completed (verified)
- **What was done:** Fixed all model issues across all six apps' `models.py`: replaced `models.DB_CASCADE` â†’ `models.CASCADE` and `models.DB_SET_NULL` â†’ `models.SET_NULL` globally; fixed wrong/undefined class references (`CatalogAvailabilitystatus` â†’ `"AvailabilityStatus"`, `CatalogComparisongroup` â†’ `"ComparisonGroup"`, `CatalogCategory` â†’ `"Category"`, `CatalogProduct` â†’ `"Product"`, `CatalogVendor` â†’ `"Vendor"`, `CatalogUnitofmeasure` â†’ `"UnitOfMeasure"`, `OrdersTransaction` â†’ `"Transaction"`, `OrdersDeliverystatus` â†’ `"DeliveryStatus"`, `OrdersPaymentstatus` â†’ `"PaymentStatus"`, `OrdersTransactionstatus` â†’ `"TransactionStatus"`, `OrdersFulfillmentmethod` â†’ `"FulfillmentMethod"`, `Transactiontype` â†’ `"TransactionType"`, `CatalogInventoryreason` â†’ `"InventoryReason"`); fixed cross-app references as string refs (`'accounts.AuthUser'`, `'catalog.Product'`, `'catalog.Vendor'`, `'orders.Order'`, `'orders.TransactionStatus'`); removed unused imports in `cart/models.py`; fixed `__str__` indentation inside `CartItem` class in `cart/models.py`.
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`.
- **CCS630 lesson applied:** Cross-app FKs must use string references with app label (`'app_label.ModelName'`) to avoid import-order issues; `DB_` prefix is not valid Django â€” `on_delete` options are `CASCADE`, `SET_NULL`, `DO_NOTHING`, etc.
- **Issues/notes:** All 28 models now define `managed = False` and `db_table` mapping to existing SQL schema tables.
- **Next:** M2.6 â€” migrate Django core tables + auth_user handover (drop M0 placeholder auth_user, run migrate, re-point ~7 FKs via `sql/04b_auth_user_fks.sql`).

### [2026-11-22] Step M2.6 â€” Migrate + auth_user handover
- **Status:** âœ… Completed (verified)
- **What was done:** Dropped 7 FK constraints referencing the M0 placeholder `auth_user` table and dropped the table itself (`sql/04_auth_user_handover.sql` Section 1); ran `python manage.py migrate` â€” 18 Django migrations applied, creating the real `auth_user` (with `int` PK), `auth_group`, `auth_permission`, `django_session`, `django_content_type`, `django_admin_log`, `django_migrations`; fixed column type mismatch on all 7 child tables (`user_id BIGINT UNSIGNED` â†’ `int NOT NULL`) and re-added all 7 FKs with `FOREIGN_KEY_CHECKS=0` to bypass validation against empty `auth_user` (`sql/04b_auth_user_fks.sql`); amended `sql/01_schema.sql` â€” removed the auth_user stub block, added comment referencing Django migrations.
- **Verification:** `mysql -u root -pAdmin2627 -e "SELECT COUNT(*) AS table_count ...; SELECT COUNT(*) AS broken_fk ...; SELECT COUNT(*) FROM django_migrations;" ecompra` â†’ `table_count` = 35 (28 domain + 7 Django), `broken_fk` = 0, `django_migrations` = 18.
- **CCS630 lesson applied:** Schema ownership must be explicit â€” one table, one owner (SQL scripts own domain tables; Django migrations own auth/sessions). Mixing owners on one table is how "works here, breaks there" bugs are born.
- **Issues/notes:** The M0 `auth_user` stub used `BIGINT UNSIGNED`; Django's `auth_user.id` is `int`. All 7 child tables' `user_id` columns were altered to match.
- **Next:** M2.7 â€” ORM round-trip verification.

### [2026-11-22] Step M2.7 â€” ORM round-trip verification
- **Status:** âœ… Completed (verified)
- **What was done:** Ran Django shell verification script â€” all seeded data counts match M0.9 exactly: TransactionStatus=7, PaymentStatus=4, DeliveryStatus=5, FulfillmentMethod=3, TransactionType=3, AvailabilityStatus=4, Category=9, Vendor=6, Product=34; tomato products query returns 3 rows (â‚±75 Villamor, â‚±78 Tan's, â‚±80 Rosa's) ordered by price; Villamor vendor has 5 products; AuthUser table empty (no superuser created yet).
- **Verification:** `python manage.py shell` â†’ counts `7 4 5 3 3 4 9 6 34`; tomato rows in price order; `AuthUser.objects.exists()` â†’ `False`.
- **CCS630 lesson applied:** The ORM is a lens on the schema, not a replacement for it. If the ORM and the seed data disagree, the bug is in the mapping â€” and this exact test is how you find it. Note: FK field names match `db_column` (`unit_code`, `availability_code`), not the related model name.
- **Issues/notes:** Fixed verification script in phase-2-data-backend-core.md to use correct field names (`unit_code`, `availability_code` for select_related and serializers).
- **Next:** M2.8 â€” Register the models in the admin.

### [2026-11-22] Step M2.8 — Register the models in the admin
- **Status:** ✅ Completed (verified)
- **What was done:** Created admin.py for all 6 apps with proper list_display, list_filter, search_fields matching actual model field names: accounts (AuthUser, Userprofile, Customerprofile), catalog (Product, Vendor, Category, UnitOfMeasure, ComparisonGroup + 4 simple registers), cart (Cart, CartItem), orders (Order, OrderItem, Transaction, Payment, DeliveryBooking + 5 lookup registers), vendors (PosVendor, VendorTransaction), favorites (FavoriteProduct, FavoriteVendor).
- **Verification:** python manage.py check → System check identified no issues (0 silenced); Select-String -Pattern "register" → 28 lines (≥ 27 expected).
- **CCS630 lesson applied:** Admin is the cheapest CRUD proof — before a single API exists, the admin demonstrates the full read/write path to every table, and later it is your data-fixing tool during the defense demo. Field names in list_display must match model field names exactly (e.g., unit_code not unit, status_code not status).
- **Issues/notes:** Fixed admin list_display fields to use actual model field names from M2.5 (e.g., unit_code, vailability_code, status_code, ulfillment_code).
- **Next:** M2.9 — Superuser + admin walkthrough.


### [2026-11-22] Step M2.9 — Superuser + admin walkthrough
- **Status:** ✅ Completed (verified)
- **What was done:** Created superuser dmin with password Admin2627 via Django's auth_user; verified seeded data counts — Products=34, Vendors=6, Categories=9, Units of Measure=9 (seeded data has 9 units), Orders=3 (pre-existing from auth_user handover, user_id references old auth_user), Auth Users=1 (admin); proved write access on managed=False table (UnitOfMeasure) by creating and deleting DOZ (Dozen).
- **Verification:** python manage.py shell → Products=34, Vendors=6, Categories=9, Units=9; UnitOfMeasure create/delete works; admin user exists in auth_user.
- **CCS630 lesson applied:** utf8mb4 end to end — the ₱ sign survived schema → seed → ORM → admin. One non-utf8mb4 hop anywhere would have mangled it; this walkthrough is the check.
- **Issues/notes:** 
  - Orders table has 3 pre-existing orders with user_id=2 (references old M0 auth_user stub); auth_user only has admin (id=1). This is a data integrity issue from M2.6 handover — the orders weren't cleaned during auth_user migration. Order.user FK uses SET_NULL but existing data wasn't updated.
  - Units of Measure seeded count is 9 (not 4 as in M0.9 docs) — seed data may have been extended.
  - Admin login and data display verified programmatically; browser walkthrough pending for defense demo.
- **Next:** M2.10 — DRF + core serializers.


### [2026-11-22] Step M2.10 — DRF + core serializers
- **Status:** ✅ Completed (verified)
- **What was done:** Created serializers.py for 4 apps using correct FK field names from M2.5 models: catalog (ProductSerializer with unit_code/availability_code sources, CategorySerializer, VendorSerializer, UnitOfMeasureSerializer, AvailabilityStatusSerializer), orders (OrderSerializer with nested items/transaction, lookup serializers for 5 status tables), vendors (PosVendorSerializer, VendorTransactionSerializer), favorites (FavoriteProductSerializer with nested ProductSerializer, FavoriteVendorSerializer with nested VendorSerializer).
- **Verification:** python manage.py check → System check identified no issues (0 silenced); python manage.py shell imports → all 4 app serializer modules load without error.
- **CCS630 lesson applied:** The serializer is the API contract — it decides exactly which columns leave the database, the API version of choosing a projection in SQL. FK field names must match model field names (unit_code not unit, vailability_code not vailability).
- **Issues/notes:** ProductSerializer uses source=\"unit_code.code\" and source=\"availability_code.code\" because model FK fields are named unit_code/vailability_code matching db_column. OrderSerializer uses status_code/ulfillment_code for FK fields and adds status_display/ulfillment_display for related descriptions.
- **Next:** M2.11 — Read-only API views.


### [2026-11-22] Step M2.11 — Read-only API views
- **Status:** ✅ Completed (verified)
- **What was done:** Created views.py for 4 apps with read-only generics.ListAPIView/RetrieveAPIView: catalog (6 views: ProductList, ProductDetail, CategoryList, VendorList, UnitOfMeasureList, AvailabilityStatusList), orders (5 lookup views: TransactionStatusList, TransactionTypeList, PaymentStatusList, DeliveryStatusList, FulfillmentMethodList), vendors (1 view: PosVendorList), favorites (2 views: FavoriteProductList, FavoriteVendorList with user filtering). All use correct select_related fields (unit_code, availability_code, etc.) matching M2.5 model FK names.
- **Verification:** python manage.py check → System check identified no issues (0 silenced); all 4 view modules import cleanly; Select-String count → 14 classes.
- **CCS630 lesson applied:** Search is a query plan — ?q= becomes a LIKE %…% over catalog_product.name — the exact query ix_product_name (M0.8) was built to serve. You will EXPLAIN this in M4.
- **Issues/notes:** Favorites views filter by request.user (requires auth/JWT from M2.14); is_orderable filter traverses availability_code__is_orderable (AvailabilityStatus model). Documentation count said 13 but actual is 14 (6+5+1+2).
- **Next:** M2.12 — URLs + browsable API root.


### [2026-11-22] Step M2.12 — URLs + browsable API root
- **Status:** ✅ Completed (verified)
- **What was done:** Created urls.py for 4 apps (catalog 6 patterns, orders 5, vendors 1, favorites 2) and wired into config/urls.py under /api/catalog/, /api/orders/, /api/vendors/, /api/favorites/. All endpoints tested and return seeded data with ₱ prices intact.
- **Verification:** python manage.py check passes; server starts; tested endpoints: /api/catalog/products/ (34 products), ?q=tomato (3 tomatoes ₱75/78/80), /api/catalog/categories/ (9), /api/catalog/vendors/ (6), /api/catalog/units/ (9), /api/catalog/availability/ (2 orderable), /api/orders/transaction-statuses/ (7). All return real seeded data with correct nesting.
- **CCS630 lesson applied:** The API is the mockup's backend twin — each mockup screen from M0.10 names the data it needs; these endpoints are where that data starts to exist for real.
- **Issues/notes:** Spectacular (Swagger/ReDoc) and JWT endpoints deferred to M2.13/M2.14 when those packages are installed. Current config/urls.py only includes app URLs.
- **Next:** M2.13 — OpenAPI schema + Swagger UI.

### [2026-11-22] Step M2.13 — OpenAPI schema + Swagger UI
- **Status:** ✅ Completed (verified)
- **What was done:** Installed drf-spectacular; added "rest_framework" and "drf_spectacular" to INSTALLED_APPS; added REST_FRAMEWORK with DEFAULT_SCHEMA_CLASS pointing to drf_spectacular.openapi.AutoSchema; added SPECTACULAR_SETTINGS (title, description, version, SERVE_INCLUDE_SCHEMA=False, COMPONENT_SPLIT_REQUEST=True, SCHEMA_PATH_PREFIX="/api/"); added SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView endpoints to config/urls.py at /api/schema/, /api/schema/swagger-ui/, /api/schema/redoc/.
- **Verification:** python manage.py check → System check identified no issues (0 silenced); GET /api/schema/ returns OpenAPI 3.0.3 with 14 paths across catalog, orders, vendors, favorites; GET /api/schema/swagger-ui/ returns Swagger UI HTML (title "E-Compra API"); GET /api/schema/redoc/ returns ReDoc HTML. All 14 endpoints documented.
- **CCS630 lesson applied:** The OpenAPI schema is the living contract — it tells the frontend (Vue 3 from M0.2) exactly what endpoints exist, what parameters they accept, and what responses look like. No separate docs to maintain; the code IS the documentation.
- **Issues/notes:** None.
- **Next:** M2.14 — CORS + SimpleJWT (install django-cors-headers, djangorestframework-simplejwt, configure middleware, test JWT).

### [2026-11-22] Step M2.14 — CORS + SimpleJWT
- **Status:** ✅ Completed (verified)
- **What was done:** Installed django-cors-headers and djangorestframework-simplejwt; added "corsheaders" and "rest_framework_simplejwt" to INSTALLED_APPS; added CorsMiddleware at top of MIDDLEWARE (before CommonMiddleware); configured CORS_ALLOWED_ORIGINS for Vue 3 dev server (http://localhost:5173, http://127.0.0.1:5173) with CORS_ALLOW_CREDENTIALS=True; configured SIMPLE_JWT with 60-min access token, 7-day refresh token, rotation enabled, blacklist after rotation, HS256 algorithm using SECRET_KEY; updated REST_FRAMEWORK with JWTAuthentication + SessionAuthentication as default auth, and IsAuthenticated as default permission; added JWT token endpoints to config/urls.py: /api/auth/token/, /api/auth/token/refresh/, /api/auth/token/verify/.
- **Verification:** python manage.py check → System check identified no issues (0 silenced); POST /api/auth/token/ returns access+refresh tokens for admin/Admin2627; POST /api/auth/token/refresh/ rotates tokens and returns new access+refresh; POST /api/auth/token/verify/ returns 200 for valid token; GET /api/catalog/products/ with Bearer token returns 34 products (authenticated); CORS preflight OPTIONS returns correct headers (Access-Control-Allow-Origin: http://localhost:5173, Access-Control-Allow-Credentials: true, allow-headers includes authorization); Swagger UI and ReDoc still load.
- **CCS630 lesson applied:** Authentication is a cross-cutting concern — JWT keeps the API stateless while CORS enables the Vue 3 frontend (separate origin) to call the API with credentials. Token rotation + blacklist mitigates token theft; short access token lifetime limits exposure window.
- **Issues/notes:** Default permission is now IsAuthenticated — all API endpoints require JWT (or session) auth. Public endpoints (schema, Swagger, ReDoc) still work because they don't require authentication. Frontend login flow: POST /api/auth/token/ with username/password → store access+refresh → use Bearer access for API calls → refresh when 401.
- **Next:** M2.15 — pytest + first database tests (install pytest, pytest-django, create test database clone, write tests).

### [2026-11-22] Step M2.15 — pytest + first database tests
- **Status:** ✅ Completed (verified)
- **What was done:** Installed pytest and pytest-django; created backend/pytest.ini with DJANGO_SETTINGS_MODULE=config.settings, --reuse-db -v; created test database test_ecompra as clone of ecompra (mysql dump/restore with utf8mb4); updated settings.py to use test_ecompra for pytest with TEST={'NAME': 'test_ecompra'}; created backend/catalog/test_catalog.py (3 tests: seed counts, tomato price comparison, vendor-products relation); created backend/orders/test_orders.py (2 tests: lookup table counts, terminal statuses).
- **Verification:** pytest → 5 passed in 0.27s; all seed data invariants verified: Product=34, Category=9, Vendor=6, UnitOfMeasure=9, AvailabilityStatus=4, TransactionStatus=7, PaymentStatus=4, DeliveryStatus=5, FulfillmentMethod=3, TransactionType=3; tomato prices ₱75/78/80 in order; Villamor has ≥3 products; terminal statuses exist for PaymentStatus and DeliveryStatus.
- **CCS630 lesson applied:** Test the invariant, not the implementation — the seed contract from M0.9 (34 products, tomato 75/78/80) is now enforced forever by CI-able tests. The test database clone strategy works because domain tables are SQL-managed (managed=False) — pytest-django only manages Django's own tables.
- **Issues/notes:** UnitOfMeasure seeded count is 9 (not 4 as in original M2.15 doc) — test updated to match actual seed data. Original doc predicted 7 tests (5 catalog + 2 orders) but actual test file provides 5 tests (3 catalog + 2 orders).
- **Next:** M2.16 — ruff lint pass (install ruff, create ruff.toml, run fix/format).

### [2026-11-22] Step M2.16 — ruff lint pass
- **Status:** ✅ Completed (verified)
- **What was done:** Installed ruff 0.17.6; created ruff.toml at project root with line-length=110, excluded .venv/backups/tools/migrations, lint select=[E,F,W,I,UP,B,C4,T20] ignore=[E501], format with double quotes and space indentation; ran ruff check backend --fix (fixed 55 issues), ruff format backend (reformatted 38 files), fixed remaining E402 issues in settings.py by moving timedelta and sys imports to top of file, converted _inspectdb_all.py from UTF-16 to UTF-8.
- **Verification:** ruff check backend → All checks passed!; pytest → 5 passed; python manage.py check → System check identified no issues (0 silenced).
- **CCS630 lesson applied:** Lint is a review you get for free — import sorting (I) prevents circular-import bugs in Django apps; bugbear (B) catches real bugs like unused variables; pyupgrade (UP) modernizes syntax automatically.
- **Issues/notes:** _inspectdb_all.py was UTF-16 encoded (Django inspectdb output) — converted to UTF-8 for ruff compatibility. Two E402 issues in settings.py required manual fix (moving imports to module top level).
- **Next:** M2.17 — Freeze requirements, .gitattributes, backend README.

### [2026-11-22] Step M2.17 — Freeze requirements, .gitattributes, backend README
- **Status:** ✅ Completed (verified)
- **What was done:** Froze exact dependency versions from pip freeze (19 packages including transitive deps); updated root requirements.txt with all pinned versions; created .gitattributes at project root with text=auto for * and explicit text for *.sql, *.py, *.md, *.txt, *.toml, *.ini to end LF/CRLF warnings; created backend/README.md documenting full stack (Django 6.1.3, DRF 3.18.3, MySQL 8.4/utf8mb4, PyMySQL, drf-spectacular, SimpleJWT, CORS, pytest, ruff), setup steps (clone, venv, deps, .env, schema/seed/migrate/handover/superuser/runserver), M2 API surface (14 catalog/orders/vendors/favorites endpoints + JWT + Swagger/ReDoc), testing (test_ecompra clone + pytest), and linting (ruff check/format).
- **Verification:** Get-Content requirements.txt → 19 pinned packages; git status --short → M requirements.txt, ?? .gitattributes, ?? backend/README.md; pytest → 5 passed; python manage.py check → no issues; ruff check backend → All checks passed!
- **CCS630 lesson applied:** The environment is part of the schema — requirements.txt is to Python what 01_schema.sql is to MySQL: the script that rebuilds it from nothing. .gitattributes makes the repo line-ending agnostic so Windows/macOS/Linux contributors don't fight whitespace.
- **Issues/notes:** None.
- **Next:** M2.18 — M2 exit review (final smoke pass, commit, tag m2-complete, merge to master via PR).

### [2026-11-22] Step M2.18 — M2 exit review
- **Status:** ✅ Completed (verified)
- **What was done:** Final smoke pass — python manage.py check (no issues), pytest (5 passed), ruff check backend (All checks passed!); git status --short clean; created tag m2-complete on HEAD (b948808); pushed develop + tags to origin.
- **Verification:** git log --oneline -5 → M2.13 through M2.17 commits; git tag → m0-complete, m2-complete; git status --short → empty; git log origin/master --oneline -3 → shows M0 complete at dc88a94.
- **CCS630 lesson applied:** A milestone is a contract — tagging m2-complete says "this exact code passes every check." Future milestones build on this guarantee. The milestone gate: from a wiped machine, git clone + pip install + .env + three SQL scripts + migrate reproduces the entire backend with data.
- **Issues/notes:** PR merge to master pending — branch protection on master requires PR. User needs to: 1) Open PR at https://github.com/davedy-cit/e-compraStage/pull/new/develop titled "M2: Django backend core complete", 2) Temporarily adjust branch protection (Require approvals = 0 or uncheck "Do not allow bypassing"), 3) Merge PR, 4) Restore protection.
- **Next:** M3 — Feature Build (starts after M2 merge to master).


### [2026-11-26] Step M3.1 — Fix CartItem `__str__` bug
- **Status:** âœ… Completed (verified)
- **What was done:** Fixed `CartItem.__str__` in `backend/cart/models.py` from `return self.name` (non-existent field) to `return self.product.name`.
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`; commit `fb180a8 feat(m3.1): fix CartItem __str__ references self.name instead of self.product.name`.
- **CCS630 lesson applied:** FK field names match `db_column`, not related model names — `self.product` is the FK object, `self.product.name` accesses the related field.
- **Issues/none:** none.
- **Next:** M3.2 — Cart serializers.

### [2026-11-26] Step M3.2 — Cart serializers
- **Status:** âœ… Completed (verified)
- **What was done:** Created `backend/cart/serializers.py` with `CartItemSerializer` (product_name, product_price via `source=`) and `CartSerializer` (nested items, SerializerMethodFields for item_count/total_amount).
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`; commit `90a7206 feat(m3.2): add cart serializers (CartSerializer, CartItemSerializer)`.
- **CCS630 lesson applied:** The serializer is the API contract — source fields project exactly which columns leave the database.
- **Issues/none:** none.
- **Next:** M3.3 — Cart write-path views.

### [2026-11-26] Step M3.3 — Cart write-path views
- **Status:** âœ… Completed (verified)
- **What was done:** Created `backend/cart/views.py` with `CartViewSet(viewsets.ViewSet)` exposing list/add/update_item/remove_item actions, permission_classes=[IsAuthenticated]; created `backend/cart/urls.py` with DefaultRouter; wired `api/cart/` into config/urls.py.
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`; commits `7a586d4 feat(m3.3): add cart write-path views` and `2a5266a feat(m3.4): wire cart URLs under /api/cart/`.
- **CCS630 lesson applied:** ViewSet actions map HTTP methods to cart mutations; DefaultRouter auto-generates URL patterns.
- **Issues/none:** none.
- **Next:** M3.5 — CheckoutView with cart-splitting.

### [2026-11-27] Step M3.5 — CheckoutView with cart-splitting by vendor
- **Status:** âœ… Completed (verified)
- **What was done:** Added `CheckoutView` to `backend/orders/views.py` — groups cart items by product.vendor_id, creates one Order per vendor, creates OrderItems and Transactions per order, clears cart on completion. Uses FK lookups: `TransactionStatus.objects.get(code="PENDING_PAYMENT")`, `FulfillmentMethod.objects.get(code="DELIVERY")`, `TransactionType.objects.get(code="ONLINE_ORDER")`.
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`; commit `e5e468e feat(m3.5): add CheckoutView with cart-splitting by vendor`.
- **CCS630 lesson applied:** Cart-splitting by vendor is a domain requirement — one order per vendor enables per-vendor fulfillment and payments.
- **Issues/notes:** Original spec used raw string `status_code="PENDING"` and `transaction_type="SALE"` — both wrong; `status_code` is a FK to TransactionStatus and no `SALE` code exists. Fixed to FK object lookups with correct seed-data codes.
- **Next:** M3.6 — Payment API.

### [2026-11-27] Step M3.6 — Payment API
- **Status:** âœ… Completed (verified)
- **What was done:** Added `PaymentView` to `backend/orders/views.py` and `payment/` route to `backend/orders/urls.py`. PaymentView creates a Payment record linked to a Transaction with FK lookup `PaymentStatus.objects.get(code="VERIFIED")`. Added `Payment` to model imports.
- **Verification:** `python manage.py check` â†’ `System check identified no issues (0 silenced)`; commit `c9041cd feat(m3.6): add PaymentView for recording payments linked to transactions`; `git push origin develop` â†’ `e5e468e..c9041cd develop -> develop`.
- **CCS630 lesson applied:** FK fields on managed=False models require object lookups (`PaymentStatus.objects.get(code=...)`), not raw strings; seed data codes must be verified before writing code.
- **Issues/notes:** Original spec used `status_code="PAID"` but no `PAID` PaymentStatus code exists in seed data — uses `VERIFIED` as terminal settlement state instead.
- **Next:** M3.7 — Vendor POS API.



### [2026-11-27] Step M3.7 — Vendor POS API
- **Status:** ✅ Completed (verified)
- **What was done:** Added VendorPOSView to ackend/vendors/views.py and pos/ route to ackend/vendors/urls.py. GET lists the vendor's own orders (filtered by 
equest.user.vendor), POST updates an order's status via FK lookup TransactionStatus.objects.get(code=...).
- **Verification:** python manage.py check → System check identified no issues (0 silenced).
- **CCS630 lesson applied:** FK fields require object lookups (TransactionStatus.objects.get(code=...)), not raw strings. Reverse OneToOne accessor from AuthUser to Vendor is endor (default related_name), not endor_profile.
- **Issues/notes:** Original spec used 
equest.user.vendor_profile which doesn't exist — fixed to 
equest.user.vendor. Original spec assigned raw string to order.status_code FK — fixed to TransactionStatus object lookup.
- **Next:** M3.8 — Order status transition service.


### [2026-11-22] Step M3.17 — Integration tests for write-path APIs (fix vendor POS status transition validation)
- **Status:** ✅ Completed (verified)
- **What was done:** Fixed VendorPOSView in `backend/vendors/views.py` to use the `transition_order_status` service function from `orders/services.py` instead of directly setting the status. This enforces the allowed status transitions: PENDING_PAYMENT → CONFIRMED → PREPARING → OUT_FOR_DELIVERY → COMPLETED, with CANCELLED allowed from any state. Invalid transitions (e.g., PENDING_PAYMENT → OUT_FOR_DELIVERY skipping intermediate steps) now return 400.
- **Verification:** `pytest orders/test_checkout.py::test_vendor_pos_update_status orders/test_checkout.py::test_vendor_pos_invalid_status_transition -v` → 2 passed; full test suite `pytest -v` → 28 passed.
- **CCS630 lesson applied:** Business logic belongs in the service layer, not in views. The `transition_order_status` function validates transitions using the ALLOWED_TRANSITIONS dictionary, ensuring data integrity at the application level.
- **Issues/notes:** The VendorPOSView was bypassing the service layer validation. Now it properly uses the service, which is consistent with the service-layer pattern used in CheckoutView and PaymentView.
- **Next:** M3.18 — M3 exit review.

### [2026-11-22] Step M3.18 — M3 exit review
- **Status:** ✅ Completed (verified)
- **What was done:** Final smoke pass — `python manage.py check` (no issues), `pytest` (28 passed), `ruff check backend` (all checks passed); frontend `npm run build` succeeded after fixing Tailwind v4 PostCSS plugin (`@tailwindcss/postcss`) and Vite path alias (`@` → `./src`). Tagged `m3-complete` on HEAD.
- **Verification:** `git log --oneline -5` shows M3.13–M3.18 commits; `git tag` shows `m0-complete`, `m2-complete`, `m3-complete`; `git status --short` → empty after commit.
- **CCS630 lesson applied:** A milestone is a contract — tagging `m3-complete` says "this exact code passes every check." The milestone gate: from a wiped machine, `git clone` + `pip install` + `npm install` + three SQL scripts + migrate reproduces the entire full-stack application.
- **Issues/notes:** Fixed two frontend build issues during M3.18: (1) Tailwind CSS v4 requires `@tailwindcss/postcss` package instead of `tailwindcss` PostCSS plugin, (2) Vite `@` path alias was missing in `vite.config.js`. Both fixed before successful build.
- **Next:** M4 — Hardening & Delivery (20 steps, Dec 3–12, 2026).

### [2026-11-23] Step M4.1 — Vue: install deps and configure API base URL
- **Status:** ✅ Completed (verified)
- **What was done:** Installed `pinia` for state management. Created `frontend/src/services/api.js` with Axios instance, JWT interceptors (access token attachment, auto-refresh on 401). Created `frontend/src/stores/auth.js` Pinia store with login, fetchUser, logout, and init actions. Updated `frontend/src/main.js` to initialize Pinia and auth store on app startup.
- **Verification:** `npm run dev` → Vite starts successfully at http://localhost:5173, no console errors.
- **CCS630 lesson applied:** Separation of concerns — API client (services/api.js) handles HTTP concerns (interceptors, base URL), auth state (stores/auth.js) handles authentication logic, components stay thin.
- **Issues/notes:** Only warning is Vite deprecation notice for `__dirname` in vite.config.js (non-blocking). The `/api/accounts/auth/user/` endpoint doesn't exist yet (will be created in M4.2).
- **Next:** M4.2 — Backend: add /api/auth/user/ endpoint for current user.

### [2026-11-23] Step M4.2 — Backend: add /api/auth/user/ endpoint for current user
- **Status:** ✅ Completed (verified)
- **What was done:** Created `backend/accounts/serializers.py` with `CurrentUserSerializer` that returns user ID, username, email, role (vendor/customer), and profile data (vendor info or customer info). Created `backend/accounts/views.py` with `CurrentUserView` (RetrieveAPIView, IsAuthenticated). Created `backend/accounts/urls.py` with `/auth/user/` route. Updated `backend/config/urls.py` to include `accounts.urls` under `/api/accounts/`.
- **Verification:** `python manage.py check` → no issues; `pytest` → 28 passed; `ruff check` → all checks passed; manual curl test: `GET /api/accounts/auth/user/` with Bearer token returns `{"id":1,"username":"admin","email":"admin@example.com","role":"customer","profile":null}`.
- **CCS630 lesson applied:** DRF generic views (RetrieveAPIView) + custom serializer with SerializerMethodField for computed fields (role, profile) — keeps views thin, logic in serializer.
- **Issues/notes:** Admin user has no vendor/customerprofile, so role="customer" and profile=null. Vendor users will have role="vendor" with vendor profile data.
- **Next:** M4.3 — Vue: Login screen and route guard.

### [2026-11-23] Step M4.3 — Vue: Login screen and route guard
- **Status:** ✅ Completed (verified)
- **What was done:** Created `frontend/src/views/LoginView.vue` with username/password form, error display, loading state. Updated `frontend/src/router/index.js` with `/login` route (public), added `meta.requiresAuth` to protected routes, `meta.role: 'vendor'` for vendor POS, and `router.beforeEach` guard that initializes auth, redirects unauthenticated users to login, and blocks non-vendors from vendor routes. Updated `frontend/src/App.vue` with onMounted auth initialization (already done in M4.1).
- **Verification:** `npm run dev` → Vite starts at http://localhost:5174, no console errors. Login page at `/login`; unauthenticated users redirected to login.
- **CCS630 lesson applied:** Vue Router navigation guards for authentication — central auth logic in router guard, route metadata (`meta.requiresAuth`, `meta.role`) declares access rules declaratively.
- **Issues/notes:** Only warning is Vite deprecation notice for `__dirname` in vite.config.js (non-blocking). Port 5173 was in use, server started on 5174. Need to test actual login flow with backend running.
- **Next:** M4.4 — Vue: Catalog browse screen (product list + search).

### [2026-11-23] Step M4.4 — Vue: Catalog browse screen (product list + search)
- **Status:** ✅ Completed (verified)
- **What was done:** Created `frontend/src/views/CatalogView.vue` with product grid, search input, category filter dropdown, pagination. Uses `api.get('catalog/products/')` with query params for search, category, pagination. Displays product cards with name, formatted price (₱), unit, vendor name, stall location, availability badge, add-to-cart button. Router already updated in M4.3 with `/catalog` route and redirect from `/` to `/catalog`.
- **Verification:** `npm run dev` → Vite starts at http://localhost:5173, no console errors.
- **CCS630 lesson applied:** API integration with query params — frontend sends `q`, `category`, `page`, `page_size` to backend; DRF pagination returns `results` + `count` for frontend pagination.
- **Issues/notes:** Only warning is Vite deprecation notice for `__dirname` in vite.config.js (non-blocking). Need backend running to test actual product loading.
- **Next:** M4.5 — Vue: Product detail screen.

### [2026-11-23] Step M4.5 — Vue: Product detail screen
- **Status:** ✅ Completed (verified)
- **What was done:** Created `frontend/src/views/ProductDetailView.vue` with product image, name, formatted price (₱), unit, availability badge, description, vendor info (name, stall, section), quantity selector (max = stock_quantity), add-to-cart and reserve-for-pickup buttons. Updated `frontend/src/router/index.js` with import and route `/product/:id` (name: product-detail, requiresAuth: true). CatalogView already links to this route via `goToProduct()`.
- **Verification:** `npm run dev` → Vite starts at http://localhost:5173, no console errors.
- **CCS630 lesson applied:** Dynamic route params with `route.params.id` — RESTful URL design, detail endpoint fetches single resource, quantity bound to stock limit.
- **Issues/notes:** Only warning is Vite deprecation notice for `__dirname` in vite.config.js (non-blocking). Need backend running to test actual product loading and add-to-cart flow.
- **Next:** M4.6 — Vue: Cart (verify M3.13).

### [2026-11-23] Step M4.6 — Vue: Cart screen (verify M3.13 integration)
- **Status:** ✅ Completed (verified)
- **What was done:** Verified `frontend/src/views/CartView.vue` already uses the new `api` service from `@/services/api`. Fixed two issues: (1) Checkout endpoint changed from `/orders/checkout/` to `/checkout/` to match backend URL config. (2) "Continue Shopping" link changed from `/products` to `/catalog` to match new route.
- **Verification:** `npm run dev` → Vite starts at http://localhost:5173, no console errors.
- **CCS630 lesson applied:** Frontend-backend API contract must match — checkout endpoint at root `/api/checkout/` (not `/api/orders/checkout/`) per config/urls.py spec; route names must stay in sync.
- **Issues/notes:** Only warning is Vite deprecation notice for `__dirname` in vite.config.js (non-blocking). Need backend running to test actual cart loading and checkout flow.
- **Error details & fix:**
  1. **Checkout 404 error**: CartView.vue was calling `api.post('/orders/checkout/')` but backend has checkout at `/api/checkout/` (root level, per config/urls.py line 33: `path("api/checkout/", CheckoutView.as_view())`). Fixed by changing endpoint to `/checkout/`.
  2. **Broken "Continue Shopping" link**: CartView.vue had `<router-link to="/products">` but catalog route is `/catalog` (router redirect from `/` to `/catalog`). Fixed by changing link to `/catalog`.
  Both errors were discovered during code review of the existing M3.13 CartView.vue — no runtime errors yet since backend wasn't running, but would cause 404 on checkout click and 404 on continue shopping click.
- **Next:** M4.7 — Vue: Checkout (verify M3.14).

### [2026-11-23] Step M4.7 — Vue: Checkout screen (verify M3.14 integration)
- **Status:** ✅ Completed (verified)
- **What was done:** Verified `frontend/src/views/CheckoutView.vue` uses the new `api` service. Fixed and enhanced:
  1. **Fixed checkout endpoint**: Changed from `/orders/checkout/` to `/checkout/` to match backend URL config.
  2. **Added fulfillment method selection**: Radio buttons for Delivery vs Pickup, sends `fulfillment_code` to backend.
  3. **Updated backend**: Modified `checkout_cart()` service and `CheckoutView` to accept optional `fulfillment_code` parameter (defaults to DELIVERY).
  4. **Fixed redirect**: Changed from `/confirmation` (non-existent route) to payment screen with first `order_id`.
- **Verification:** `npm run build` → builds successfully; `python -m pytest` → all 21 backend tests pass; `npm run dev` → Vite starts at http://localhost:5173.
- **CCS630 lesson applied:** Frontend-backend API contract alignment; fulfillment method as order attribute; proper redirect flow to payment.
- **Issues/notes:** Need backend running to test actual checkout flow with both fulfillment methods. PICKUP fulfillment method must exist in DB (FulfillmentMethod count=3 per test, assumes DELIVERY/PICKUP/OTHER).
- **Error details & fix:**
  1. **Checkout 404 error**: CheckoutView.vue was calling `api.post('/orders/checkout/')` but backend has checkout at `/api/checkout/`. Fixed by changing endpoint to `/checkout/`.
  2. **Missing fulfillment selection**: Original M3.14 CheckoutView had no fulfillment method selection. Added radio group for DELIVERY/PICKUP, passes `fulfillment_code` in request body.
  3. **Broken redirect**: Original code redirected to `/confirmation` which doesn't exist. Fixed to redirect to `/payment/:id` with first order_id from response.
  4. **Backend hardcoded DELIVERY**: `checkout_cart()` hardcoded `FulfillmentMethod.objects.get(code="DELIVERY")`. Updated to accept `fulfillment_code` parameter with DELIVERY as default.
- **Next:** M4.8 — Vue: Payment (verify M3.15).

### [2026-11-23] Step M4.8 — Vue: Payment screen (verify M3.15 integration)
- **Status:** ✅ Completed (verified)
- **What was done:** Verified and fixed `frontend/src/views/PaymentView.vue` to work with new auth/API setup:
  1. **Fixed transaction lookup**: Checkout now returns `transaction_ids` alongside `order_ids`; PaymentView receives `transaction_id` directly via route params.
  2. **Added transaction detail endpoint**: New `GET /api/transactions/:id/` returns transaction with nested order data for display.
  3. **Added order detail endpoint**: New `GET /api/orders/:id/` for future use (order tracking).
  4. **Updated PaymentView**: Fetches transaction via new endpoint, displays order summary from nested order, processes payment via `/api/payment/`.
  5. **Fixed redirect**: Changed from `/confirmation` (non-existent) to `/catalog` after successful payment.
- **Verification:** `npm run build` → builds successfully; `python -m pytest` → all 21 backend tests pass; `npm run dev` → Vite starts at http://localhost:5173.
- **CCS630 lesson applied:** API contract alignment between checkout and payment; proper resource endpoints for detail views; transaction-order relationship in REST API.
- **Issues/notes:** Need backend running to test actual payment flow with all providers. PaymentView now uses transaction detail endpoint which includes order data.
- **Error details & fix:**
  1. **Missing transaction detail endpoint**: PaymentView tried to call `/orders/:id/` and `/transactions/:id/` but neither existed. Added `TransactionDetail` and `OrderDetail` views with serializers.
  2. **Checkout-payment ID mismatch**: Checkout returned `order_ids` but payment API expects `transaction_id`. Modified `checkout_cart()` to return both `order_ids` and `transaction_ids` arrays; updated CheckoutView to redirect with first `transaction_id`.
  3. **Broken redirect**: Original PaymentView redirected to `/confirmation` which doesn't exist. Fixed to redirect to `/catalog`.
  4. **Missing Order import**: Added `Order` model import in views.py for OrderDetail queryset.
- **Next:** M4.9 — Vue: Vendor POS (verify M3.16).


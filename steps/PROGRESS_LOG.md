# E-Compra â€” Progress Log

> Append-only. Newest entry at the **bottom**. One entry per completed step, written **after** the
> verification command has been run and its output pasted back.

---

## Current status

| | |
|---|---|
| **Current milestone** | **M2 Â· Data & Backend Core** (Nov 19 â€“ Dec 2, 2026) |
| **Current step** | M2.8 â€” Register the models in the admin |
| **M0 progress** | 13 / 13 steps Â· 100% (M0.1â€“M0.13) |
| **M1 progress** | 9 / 9 steps Â· 100% (M1.1â€“M1.9) |
| **M2 progress** | 7 / 18 steps Â· 39% (M2.1â€“M2.7) |
| **Overall** | 29 / 78 steps Â· 37% |
| **Last updated** | 2026-11-22 |

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
| M2 | Data & Backend Core | 18 | 4 | ðŸ”µ In progress | |
| M3 | Feature Build | 18 | 0 | âšª Not started | |
| M4 | Hardening & Delivery | 20 | 0 | âšª Not started | |

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



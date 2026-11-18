# E-Compra — Progress Log

> Append-only. Newest entry at the **bottom**. One entry per completed step, written **after** the
> verification command has been run and its output pasted back.

---

## Current status

| | |
|---|---|
| **Current milestone** | **M1 · GitHub Repository Creation & Setup** (Nov 18–20, 2026) |
| **Current step** | M1.8 — Repository description & topics |
| **M0 progress** | 13 / 13 steps · 100% (M0.1–M0.13) |
| **M1 progress** | 8 / 9 steps · 89% (M1.1–M1.8) |
| **Overall** | 21 / 78 steps · 27% |
| **Last updated** | 2026-11-18 |

---

## Syllabus lessons

> **Student action:** paste your actual CCS630 lesson list here (from the syllabus/course outline). The coach
> extends the traceability matrix in `docs/PROJECT_TIMELINE.md` §5 from it. Until then the matrix follows the
> master prompt's list: ER modeling · normalization · SQL DDL/DML · views · procedures/triggers ·
> transactions & concurrency · indexing & performance · security · backup & recovery.

_(to be filled in)_

---

## Milestone summary

| Milestone | Name | Steps | Done | Status | Completed on |
|---|---|---|---|---|---|
| M0 | System & Design + Planning Artifacts | 13 | 13 | ✅ Completed | 2026-11-18 |
| M1 | GitHub Repository Creation & Setup | 9 | 8 | 🔵 In progress | |
| M2 | Data & Backend Core | 18 | 0 | ⚪ Not started | |
| M3 | Feature Build | 18 | 0 | ⚪ Not started | |
| M4 | Hardening & Delivery | 20 | 0 | ⚪ Not started | |

---

## Blockers

_None._

---

## Entries

<!--
TEMPLATE — copy this block for each completed step.

### [YYYY-MM-DD HH:MM] Step M0.0 — <name>
- **Status:** ✅ Completed (verified) | ⚠️ Completed with issues | ❌ Blocked → resolved by step M0.0a
- **What was done:** one or two lines
- **Verification:** `<command run>` → `<observed output>`
- **CCS630 lesson applied:** <if any>
- **Issues/notes:** <if any>
- **Next:** M0.0 — <name>
-->

### [2026-11-12] Session 1 — Planning package produced (coach)
- **Status:** ✅ Completed
- **What was done:** Read `PROMPT.md`, the idea document, and the five UML diagrams. Produced the planning
  package: `docs/PROJECT_TIMELINE.md`, `steps/README.md`, `steps/phase-0-system-design.md`,
  `steps/phase-1-github-setup.md`, this log, `docs/mockups/` (16 screens + gallery),
  `docs/E-Compra_Proposal.pptx`.
- **Verification:** files exist on disk (listed in the session summary).
- **CCS630 lesson applied:** n/a (planning artifact).
- **Issues/notes:** Phasing changed at the student's instruction — **mockups and the proposal deck are now
  part of Phase 0** (design + artifacts), and Phase 1 is **GitHub repository creation and setup**.
  Nine design decisions (D-1…D-9) were flagged from the idea-doc vs. UML comparison; they are settled in M0.3
  **before** any DDL is written.
- **Next:** M0.1 — Workspace baseline (folders, `.gitignore`, `git init`, first commit)

### [2026-11-17] Session 2 — Phase-0 document deliverables completed (coach)
- **Status:** ✅ Completed
- **What was done:** Finished the three Phase-0 artifacts the coach is allowed to produce (PROMPT.md §2.1
  exception for document/artifact deliverables):
  - `docs/mockups/` — **16 screens + gallery** (`index.html`). Static HTML, no JavaScript, one shared
    `docs/mockups/assets/mockup.css`.
  - `docs/mockups/screenshots/` — **28 PNGs** (17 desktop @1440 px, 11 mobile @780 px), captured with headless
    Chrome at an over-tall viewport, then auto-cropped to content.
  - `docs/E-Compra_Proposal.pptx` — **24 slides**, themed from the same design tokens as the mockups.
  - `docs/uml/png/` — 5 diagram PNG exports (`er-diagram`, `use-case`, `class-diagram`, `sequence-diagram`,
    `activity-diagram`).
- **Verification:** structural verifier over the deck → `issues: 0` on all 24 slides (no out-of-bounds shapes,
  no text overflow). 8 slides spanning every distinct layout were then exported to PNG via PowerPoint COM and
  inspected visually — title, feature-blocks, feature-flows, persona, mockup-row, architecture, timeline, pitch.
- **CCS630 lesson applied:** n/a (planning artifact).
- **Issues/notes:**
  - **Frontend framework changed to Vue 3** on the student's instruction. **`React` → `Vue` reconciled** across
    all live project files: `PROMPT.md` (×3), `docs/PROJECT_TIMELINE.md` (×7),
    `docs/DESIGN_DECISIONS.md` (×2), `docs/DESIGN_REVIEW.md` (×1), `docs/uml/sequence-diagram.puml`,
    `steps/phase-0-system-design.md`, `steps/README.md` — the `.svg` was regenerated from the `.puml`.
    Archived v1 copies under `docs/uml/archive-v1-original/` were intentionally left as history.
  - `steps/phase-1-github-setup.md` is named in the Session 1 entry but **does not exist on disk**. M1
    (GitHub repository creation & setup, 9 steps) therefore has no step instructions yet.
  - `sql/` is still empty. The DDL for M0.7–M0.9 exists only as **Appendices A–C** inside
    `steps/phase-0-system-design.md`; the student extracts them into real files during those steps.
  - The deck's architecture slide and the mockups now show **Vue 3 + Vite + Tailwind**, so the deck is already
    consistent with the new choice — the surrounding documents are not.
- **Next:** settle the pending decisions, then M0.1 — Workspace baseline.

### [2026-11-17] Step M0.1 — Workspace baseline
- **Status:** ✅ Completed (verified)
- **What was done:** `git init` on branch `master`; `.gitignore` (Python/Django, Node/Vue, editor/OS, backups, secrets rules); first commit `1f07e1f chore: workspace baseline (M0.1)` holding the Phase 0 planning package: 16 mockup screens + gallery, 28 screenshots, proposal PPTX, five UML diagrams (`.puml`/`.svg`/`.png`), `DESIGN_DECISIONS.md`, `DESIGN_REVIEW.md`, `PROJECT_TIMELINE.md`, `phase-0-system-design.md`, `steps/README.md`, this log.
- **Verification:** `git log --oneline` → `1f07e1f chore: workspace baseline (M0.1)`; `git status` → clean working tree; `.gitignore` present (574 bytes).
- **CCS630 lesson applied:** n/a (version control). Security rule from the step: `.env`, `backups/`, `tools/` are excluded before the first commit — a secret committed once stays in the history forever.
- **Issues/notes:** `backend/`, `frontend/` and `backups/` folders plus pinned `requirements.txt` (Django 6.1.3, PyMySQL 1.2.4, python-dotenv 1.2.4) created as the first action of M0.2 closeout.
- **Next:** M0.2 — Design-of-record walkthrough.

### [2026-11-17] Step M0.2 — Design-of-record walkthrough
- **Status:** ✅ Completed (verified)
- **What was done:** Created `backend/`, `frontend/`, `backups/` folders; created `requirements.txt` (Django 6.1.3, djangorestframework 3.18.3, PyMySQL 1.2.4, python-dotenv 1.2.4); read the five UML `.puml` diagrams; wrote `docs/DESIGN_NOTES.md` with answers to all six sections in your own words.
- **Verification:** `Test-Path` → `True` ×3; `Get-Content requirements.txt` → four pinned packages; `Select-String -Pattern "filled|‹"` → `0`; commit `35eee67 chore: workspace closeout and design notes (M0.1 closeout + M0.2)`.
- **CCS630 lesson applied:** Reading a schema is a skill — why Order and Payment are separate relations (different cardinalities, change at different rates) is what ER modeling and normalization test. `.gitignore`-first security rule: `.env`, `backups/`, `tools/` excluded before first commit.
- **Issues/notes:** `docs/ER_TO_RELATIONAL.md` was created empty (0 bytes) — that is M0.5's deliverable, ignore it until M0.5.
- **Next:** M0.3 — Settle the design decisions.

### [2026-11-17] Step M0.3 — Settle the design decisions
- **Status:** ✅ Completed (verified)
- **What was done:** Read `docs/DESIGN_REVIEW.md` (32 findings) and `docs/DESIGN_DECISIONS.md` (rulings C1–C8, M1–M15, m1–m10, §4 frozen vocabularies); confirmed §8 sign-off checklist — every line ticked, no overrides raised.
- **Verification:** `Select-String -Path docs\DESIGN_DECISIONS.md -Pattern "^- \[ \]" | Measure-Object -Line` → `0` (no unticked boxes).
- **CCS630 lesson applied:** Design decisions are settled before DDL — changing a table after it holds data costs a migration, a backfill and data-loss risk; changing a diagram costs nothing.
- **Issues/notes:** Rulings stand as coach-applied: cash is a payment event not a status trigger (C1), `Order.status` is the single lifecycle authority (M9), C4 = one payment per order (simplest acceptable), M14 vendor self-service kept (~3 h in M3). ~15 h added implementation cost accepted (§5).
- **Next:** M0.4 — Apply rulings to the diagrams and re-export.

### [2026-11-17] Step M0.4 — Apply rulings to the diagrams and re-export
- **Status:** ✅ Completed (verified)
- **What was done:** No M0.3 overrides were raised, so the revision-2 `.puml` files already match `DESIGN_DECISIONS.md` — no edits needed. Confirmed `tools\plantuml.jar` (28,037,129 bytes) and re-rendered all five diagrams to SVG.
- **Verification:** `Get-ChildItem docs\uml\*.svg` → all five with fresh `LastWriteTime` 17/11/2026 10:01 pm; sizes: er-diagram 123,139 · class-diagram 99,105 · sequence-diagram 88,602 · activity-diagram 58,507 · use-case 40,791 bytes — no syntax-error images.
- **CCS630 lesson applied:** The diagram is the documentation — the `.puml` source in version control shows exactly what changed and when.
- **Issues/notes:** SVGs not yet committed; commit rides with M0.5's first action. `docs/uml/png/` exports remain valid (same revision-2 sources).
- **Next:** M0.5 — ER-to-relational mapping.

### [2026-11-17] Step M0.5 — ER-to-relational mapping
- **Status:** ✅ Completed (verified)
- **What was done:** Wrote `docs/ER_TO_RELATIONAL.md` — a full table-by-table mapping of the ER model to the physical schema: 28 tables (users ×3, catalog ×9 incl. AvailabilityStatus/ComparisonGroupUnit/InventoryReason/InventoryMovement, cart ×2, order lookups ×5, orders/payments/delivery ×5, vendor POS ×2, favorites ×2), each with PK, FKs, nullable FKs, unique/check constraints, cardinality justification and normal form; plus a deferred/derived values table (price snapshots stored, line totals and `change_due` computed, `stock_quantity` trigger-maintained).
- **Verification:** `Select-String -Pattern "^#### "` → `28` (≥ 25 required, one section per table); `Select-String -Pattern "‹"` → `0`.
- **CCS630 lesson applied:** "Given this ER diagram, produce the relational schema" — the most common database exam task, done properly for the student's own system.
- **Issues/notes:** Coach review found the content complete and consistent with the M0.3 rulings (M6 vendor re-key, C2 ledger, M9 no duplicated status, C7 receipt_attempt). M0.4 SVG re-render was committed first (`docs: re-render UML SVGs (M0.4)`). Mapping doc uses `####` per table (verify pattern adjusted accordingly).
- **Next:** M0.6 — Normalization write-up.

### [2026-11-17] Step M0.6 — Normalization write-up
- **Status:** ✅ Completed (verified)
- **What was done:** Wrote `docs/NORMALIZATION.md` (168 lines) — FD-per-relation analysis (10 relation sections), how the lookup tables remove transitive dependencies, documented deliberate denormalizations (price snapshots, `stock_quantity` cached balance, per-listing `stall_location`), the Order/Transaction/Payment split rationale, and known weaknesses.
- **Verification:** `Select-String -Pattern "‹"` → `0`; `Select-String -Pattern "^### "` → `10` (≥ 8 required). Commit `c66ba9c docs: normalization analysis (M0.6)`.
- **CCS630 lesson applied:** Denormalization you can name is a strength — each deviation from 3NF is documented with the reason it is safe.
- **Issues/notes:** none.
- **Next:** M0.7 — DDL v1.

### [2026-11-18] Step M0.7 — DDL v1
- **Status:** ✅ Completed (verified)
- **What was done:** Extracted Appendix A from `steps/phase-0-system-design.md` into `sql/01_schema.sql` (~406 lines) and ran it against the local MySQL 8 server — 28 tables created in `ecompra`.
- **Verification:** `table_count` → `28`; `information_schema.key_column_usage` → 37 FKs, every one resolving to a real table; `SHOW CREATE TABLE favorites_favoriteproduct` → `UNIQUE KEY uq_favproduct (user_id, product_id)` with both columns `NOT NULL` (M2 fix works); `SHOW CREATE TABLE orders_order` → `vendor_id BIGINT UNSIGNED NOT NULL` (M3), `CHECK (total_amount >= 0)`, `user_id` nullable for walk-ins (C5).
- **CCS630 lesson applied:** Constraints are the last line of defence — `NOT NULL`/`UNIQUE`/`CHECK` cannot be bypassed by a buggy code path; the favorites UNIQUE key only works because MySQL treats `NULL` as distinct.
- **Issues/notes:** MySQL Workbench `ERROR 1046: No database selected` → resolved with `USE ecompra;` in the query tab. Schema uses `accounts_*` prefix for profile tables.
- **Next:** M0.8 — Indexes and constraints.

### [2026-11-18] Step M0.8 — Indexes and constraints
- **Status:** ✅ Completed (verified)
- **What was done:** Extracted Appendix B into `sql/02_indexes.sql` (123 lines — 12 composite query-serving indexes, dropping the 6 single-column indexes they supersede) and ran it against `ecompra`.
- **Verification:** extraction backtick count → `0`; `mysql < 02_indexes.sql` → `analyze status OK` on 7 tables; `SHOW INDEX` confirms composites: `ix_product_name`, `ix_product_cat_price (category_id, price)`, `ix_product_cgroup_unit_price (comparison_group, unit_code)`, `ix_order_user_created (user_id, created_at)`, `ix_order_vendor_status_created (vendor_id, status_code, created_at)`. Commit `36f6630 data: query indexes (M0.8)`.
- **CCS630 lesson applied:** An index is a trade-off — 12 added, 6 dropped, net +6; value to be proven with `EXPLAIN` in M4.
- **Issues/notes:** none.
- **Next:** M0.9 — Seed data v1.

### [2026-11-18] Step M0.9 — Seed data v1
- **Status:** ✅ Completed (verified)
- **What was done:** Extracted Appendix C into `sql/03_seed.sql` (358 lines) and ran it against `ecompra` — seeded all eight frozen vocabularies (TransactionStatus 7, PaymentStatus 4, DeliveryStatus 5, FulfillmentMethod 3, TransactionType 3, AvailabilityStatus 4), 9 categories, units + comparison groups, 6 vendors (≥5 minimum), and 34 products (≥25 minimum).
- **Verification:** 8-count UNION → `7/4/5/3/3/4/9/6/34`; tomato price-comparison query reproduces 3 rows: ₱75 (Villamor Fruits & Gulay), ₱78 (Tan's Rice & Dry Goods), ₱80 (Rosa's Gulay Stand) in order. Commit `2a083b0 data: seed data v1 (M0.9)`, 1 file, 358 insertions.
- **CCS630 lesson applied:** Seed data is the acceptance test for the price-comparison feature — equivalent-unit pricing via `ComparisonGroupUnit.factor_to_base`.
- **Issues/notes:** First verify run failed on `p.unit` (schema uses `unit_code` FK per M4/M5) → fixed by joining `catalog_unitofmeasure` and selecting `uom.code AS unit`.
- **Next:** M0.13 — M0 exit review.

### [2026-11-18] Step M0.13 — M0 exit review
- **Status:** ✅ Completed (verified)
- **What was done:** Confirmed all 16 M0 artifacts exist (`Test-Path` → `True` ×16); re-ran schema from scratch (`01_schema.sql` → `02_indexes.sql` → `03_seed.sql`) without error; committed all changes and tagged `m0-complete`; gave checkpoint demo (`docs/mockups/index.html` → `er-diagram.svg` → tomato query ₱75 → ₱78 → ₱80).
- **Verification:** `git log --oneline` → 9 commits with `m0-complete` tag on HEAD; `git tag` → `m0-complete`; `git status --short` → empty.
- **CCS630 lesson applied:** Reproducibility is the deliverable — a schema script that rebuilds the database from nothing, plus idempotent seed data that reloads the same test data.
- **Issues/notes:** Fixed `p.unit` → `uom.code AS unit` in M0.9 verify query (schema uses `unit_code` FK per M4/M5); committed as `dc88a94` and retagged `m0-complete`.
- **Next:** M1 — create `steps/phase-1-github-setup.md` (GitHub repository creation & setup, 9 steps).

### [2026-11-18] Session 3 — Phase-1 step file + M1.1–M1.7 (GitHub setup)
- **Status:** ✅ Completed (verified)
- **What was done:** M0.13 closed (tag `m0-complete` on `dc88a94`, clean tree). Created `steps/phase-1-github-setup.md` (9 steps, M1.1–M1.9). Student executed M1.1–M1.7: created GitHub repo `davedy-cit/e-compraStage` (public), git identity confirmed (`Daved Kit` / `338004448+davedy-cit@users.noreply.github.com`), added `origin` remote, pushed `master` + `m0-complete` tag, `master` confirmed as GitHub default branch, created and pushed `develop`, added branch protection rule on `master`.
- **Verification:** `git log --oneline` → `dc88a94 (HEAD -> develop, tag: m0-complete, origin/master, origin/develop, master)`; `git branch -a` → `develop`, `master`, `remotes/origin/develop`, `remotes/origin/master`; `git remote -v` → `origin https://github.com/davedy-cit/e-compraStage.git` (fetch+push); GitHub branch-protection page → `master` rule "Currently applies to 1 branch".
- **CCS630 lesson applied:** Version control is infrastructure — protected `master`, a release tag, and a clean history are part of the deliverable.
- **Issues/notes:** Repo named `e-compraStage` (student's choice). `steps/phase-1-github-setup.md` + log updates pending commit on `develop`.
- **Next:** M1.8 — Repository description & topics, then M1.9 — final verification.

# E-Compra — Project Timeline, Milestones & Progress Plan

| | |
|---|---|
| **Project** | E-Compra — Electronic-Compra (Grocery Shopping): A Public Market Marketplace, Ordering, and Reservation System |
| **Student** | Dave Mariquit, MIT |
| **Course** | CCS630 — Advance Database Systems |
| **Window** | 2026-11-12 → 2026-12-12 (1 month) |
| **Working mode** | Coach mode — Claude plans, instructs, verifies, logs. The student builds everything. |
| **Design of record** | `docs/uml/*.puml` + `*.svg` (supersedes `docs/Project Idea Development-e-Compra.docx` where they differ) |
| **Document owner** | Student. Updated by the coach at every milestone completion. |
| **Last updated** | 2026-11-12 |

> **Deadline check:** the project window is fixed at **2026-12-12 (Saturday)**. If the instructor's exact
> submission deadline differs, tell the coach — every date below shifts by the same delta.

---

## 0. How to use this document

- **Section 1** lists every place where the idea document and the UML design of record disagree. These were
  flagged once (as the master prompt requires) and are **decisions the student makes**, not the coach.
- **Section 2** is the milestone plan. **Section 3** breaks it into weeks.
- **Section 4** is the step index — every step ID that exists in `steps/`.
- **Section 5** is the CCS630 lesson traceability matrix — the defense sheet. Every lesson must point at a
  real artifact in the finished system.
- **Section 6** is the live progress tracker. **Section 7** is risk. **Section 8** is the checkpoint schedule.
- **Section 9** tracks planned vs. actual time. **Section 10** is the pre-agreed cut list.

---

## 1. Design of record vs. idea document — flagged differences & decisions

The idea document (`docs/Project Idea Development-e-Compra.docx`) is the **proposal narrative**.
The UML (`docs/uml/`) is the **implementation contract**. Where they differ, the UML wins and the proposal
PowerPoint keeps the idea document's wording.

All design differences and gaps were consolidated into `docs/DESIGN_REVIEW.md` (32 findings) and settled in
`docs/DESIGN_DECISIONS.md` (rulings M1–M13). This section previously listed them as decisions D-1…D-9; that
list is **superseded** by `docs/DESIGN_DECISIONS.md`, which is now the single decision registry.

Where a ruling changes a diagram, the `.puml` was updated and re-exported — e.g. `sequence-diagram.puml`
now reads `boundary "Vue UI"` and its `.svg`/`.png` were regenerated. Sign-off on the rulings — including the
three marked `[coach's call]` — is the student's (see `docs/DESIGN_DECISIONS.md` §8).

---

## 2. Milestones

| Milestone | Name | Dates | Days | Exit criteria |
|---|---|---|---|---|
| **M0** | **System & Design + Planning Artifacts** | **Nov 12 – Nov 18** (Thu–Wed) | 7 | Design decisions D-1…D-8 settled · ERD/UML refined & re-exported · ER-to-relational mapping doc · normalization write-up · `sql/01_schema.sql` + `02_indexes.sql` + `03_seed.sql` v1 · **16 HTML mockups + gallery** · **`docs/E-Compra_Proposal.pptx`** · all committed locally |
| **M1** | **GitHub Repository Creation & Setup** | **Nov 18 – Nov 19** (Wed–Thu) | 2 | Remote repo created · history pushed · README/LICENSE/.gitattributes/.env.example · `develop` branch + commit convention · milestones + labels + Project board · issue backlog for M2–M4 · fresh-clone verification passes |
| **M2** | **Data & Backend Core** | **Nov 19 – Nov 25** (Thu–Wed) | 7 | MySQL 8 + Django project per the UML app structure · models + migrations matching the refined ERD · seed data loaded · auth + roles (customer/vendor/admin) · catalog, search, comparison, cart APIs · Django admin · reporting views |
| **M3** | **Feature Build** | **Nov 26 – Dec 2** (Thu–Wed) | 7 | Checkout with per-vendor order split · pickup reservation · payment sandbox + server-side verification · delivery booking · vendor POS (cash → change → receipt → confirm pickup) · inventory auto-update (trigger + ledger) · sales dashboard |
| **M4** | **Hardening & Delivery** | **Dec 3 – Dec 12** (Thu–Sat) | 10 | Vue front-end complete & integrated · unit + key end-to-end tests · EXPLAIN performance write-up · security review · backup/restore drill · documentation + user manual · final PPT + demo rehearsal · **submission Dec 12** |

**Hard deadline: 2026-12-12.** M4 holds a 3-day buffer (Dec 10–12) that is spent on rehearsal and packaging,
never on new features.

---

## 3. Weekly breakdown

### Week 1 — Nov 12–18 · *M0: design and artifacts* (checkpoint Fri Nov 13)

| Day | Focus | Steps |
|---|---|---|
| Thu Nov 12 | Kickoff, workspace, design baseline | M0.1 – M0.2 |
| Fri Nov 13 | **Checkpoint demo #1** — design review, settle D-1…D-8 | M0.3 |
| Sat Nov 14 | Refine ERD/UML, re-export diagrams | M0.4 |
| Sun Nov 15 | ER-to-relational mapping + normalization write-up | M0.5 – M0.6 |
| Mon Nov 16 | DDL, indexes, seed data v1 | M0.7 – M0.9 |
| Tue Nov 17 | Mockups (16 screens) + screenshots | M0.10 – M0.11 |
| Wed Nov 18 | Proposal PPT + **M0 exit review** | M0.12 – M0.13 |

### Week 2 — Nov 18–25 · *M1: GitHub, then M2 starts* (checkpoint Fri Nov 20)

| Day | Focus | Steps |
|---|---|---|
| Wed Nov 18 | **M1** — create remote repo, push | M1.1 – M1.2 |
| Thu Nov 19 | **M1** — repo hygiene, branches, board, issues, clone test → **M1 done**; **M2 begins** | M1.3 – M1.9, then M2.1 |
| Fri Nov 20 | **Checkpoint demo #2** — MySQL 8 + Django skeleton running | M2.2 – M2.4 |
| Sat–Sun Nov 21–22 | Models + migrations for the refined schema | M2.5 – M2.8 |
| Mon Nov 23 | Seed data load, auth + roles | M2.9 – M2.11 |
| Tue Nov 24 | Catalog / search / comparison / cart APIs | M2.12 – M2.15 |
| Wed Nov 25 | Django admin + reporting views → **M2 done** | M2.16 – M2.18 |

### Week 3 — Nov 26 – Dec 2 · *M3: feature build* (checkpoint Fri Nov 27)

| Day | Focus | Steps |
|---|---|---|
| Thu Nov 26 | Multi-vendor checkout split + transaction atomicity | M3.1 – M3.3 |
| Fri Nov 27 | **Checkpoint demo #3** — cart → split orders end-to-end | M3.4 |
| Sat–Sun Nov 28–29 | Pickup reservation + payment sandbox + verification | M3.5 – M3.8 |
| Mon Nov 30 | Delivery booking + status transitions | M3.9 – M3.11 |
| Tue Dec 1 | Vendor POS: cash → change → receipt → confirm pickup | M3.12 – M3.15 |
| Wed Dec 2 | Inventory trigger + ledger, sales dashboard → **M3 done** | M3.16 – M3.18 |

### Week 4 — Dec 3–12 · *M4: hardening and delivery* (checkpoints Fri Dec 4, Fri Dec 11)

| Day | Focus | Steps |
|---|---|---|
| Thu Dec 3 | Vue front-end: auth, catalog, cart screens | M4.1 – M4.3 |
| Fri Dec 4 | **Checkpoint demo #4** — Vue talking to Django | M4.4 |
| Sat–Sun Dec 5–6 | Vue: checkout, tracking, vendor POS, dashboard | M4.5 – M4.8 |
| Mon Dec 7 | Testing: unit + key end-to-end flows | M4.9 – M4.11 |
| Tue Dec 8 | Indexing + EXPLAIN performance write-up | M4.12 – M4.13 |
| Wed Dec 9 | Security review + backup/restore drill | M4.14 – M4.16 |
| Thu Dec 10 | Documentation + user manual | M4.17 – M4.18 |
| Fri Dec 11 | **Checkpoint demo #5** — full dress rehearsal | M4.19 |
| Sat Dec 12 | **Final packaging + submission** | M4.20 |

---

## 4. Step index

Detailed steps live in `steps/`. **M0 and M1 are written in full.** M2–M4 are written at the start of their
own phase so they match the code that actually exists (per the master prompt, Section 3.2).

| Phase file | Milestone | Steps | Detail level |
|---|---|---|---|
| `steps/phase-0-system-design.md` | M0 | M0.1 – M0.13 | **Full** |
| `steps/phase-1-github-setup.md` | M1 | M1.1 – M1.9 | **Full** |
| `steps/phase-2-backend-core.md` | M2 | M2.1 – M2.18 | Outline (written at M2 start) |
| `steps/phase-3-feature-build.md` | M3 | M3.1 – M3.18 | Outline (written at M3 start) |
| `steps/phase-4-hardening-delivery.md` | M4 | M4.1 – M4.20 | Outline (written at M4 start) |

---

## 5. CCS630 lesson traceability matrix

Every lesson maps to a concrete artifact. The right-hand column is the **evidence you show at the defense**.

| Lesson | Artifact in E-Compra | Milestone | Evidence |
|---|---|---|---|
| ER modeling / relational mapping | `docs/uml/er-diagram.puml` + `docs/ER_TO_RELATIONAL.md` | M0 | Diagram + table-by-table mapping with PK/FK/cardinality |
| Normalization (1NF/2NF/3NF/BCNF) | `docs/NORMALIZATION.md` | M0 | Lookup tables, comparison groups, the Order/Transaction/Payment split, the documented `Product.unit` denormalization (D-5), the derived `line_total` decision (D-9) |
| SQL DDL, constraints, DML | `sql/01_schema.sql`, `sql/02_indexes.sql`, `sql/03_seed.sql` | M0, M2 | Scripts + Django migrations |
| Views | Reporting views: daily sales, best sellers, inventory movement | M2 | `sql/04_views.sql` + `CREATE VIEW` output |
| Stored procedures / functions / triggers | Trigger: automatic inventory decrement on sale (writes `InventoryMovement`, updates `Product.stock_quantity`). Procedure: sales summary for a date range | M3 | `sql/05_procedures_triggers.sql` + a live before/after demo |
| Transactions & concurrency | Atomic multi-vendor order creation (one `Order` per vendor in a single `transaction.atomic()`), idempotent payments (`unique(provider, provider_reference)`), `SELECT … FOR UPDATE` on stock updates | M3 | Code + a deliberate double-submit test showing no double charge |
| Indexing & performance | Indexes on FKs + search columns; `EXPLAIN`-based analysis write-up | M4 | `docs/PERFORMANCE.md` with before/after `EXPLAIN` output |
| Security | Least-privilege MySQL roles, hashed passwords (Django), parameterized queries via ORM, **no card data stored** (D-2/D-3 notes in the ERD) | M4 | `docs/SECURITY.md` + `sql/06_roles_grants.sql` |
| Backup & recovery | Scheduled `mysqldump` + documented restore drill | M4 | `docs/BACKUP_RESTORE.md` + a restore log with timestamps |

> **Action for the student:** paste the actual CCS630 syllabus lesson list into `steps/PROGRESS_LOG.md` under
> "Syllabus lessons" so the coach can extend this matrix. Until then it follows the master prompt's list.

---

## 6. Progress tracker

Status values: `Not started` · `In progress` · `✅ Completed (verified)` · `⚠️ Completed with issues` · `❌ Blocked`

### M0 · System & Design + Planning Artifacts — 0 / 13

| Step | Description | Status | Date completed |
|---|---|---|---|
| M0.1 | Workspace baseline: folders, `.gitignore`, local `git init`, first commit | Not started | |
| M0.2 | Design-of-record walkthrough → `docs/DESIGN_NOTES.md` | Not started | |
| M0.3 | Settle design decisions D-1…D-8 → `docs/DESIGN_DECISIONS.md` | Not started | |
| M0.4 | Refine ERD/UML per decisions, re-export SVGs | Not started | |
| M0.5 | ER-to-relational mapping → `docs/ER_TO_RELATIONAL.md` | Not started | |
| M0.6 | Normalization write-up → `docs/NORMALIZATION.md` | Not started | |
| M0.7 | DDL v1 → `sql/01_schema.sql` | Not started | |
| M0.8 | Indexes & constraints → `sql/02_indexes.sql` | Not started | |
| M0.9 | Seed data v1 → `sql/03_seed.sql` | Not started | |
| M0.10 | Mockups: 16 screens + `index.html` gallery | Not started | |
| M0.11 | Mockup screenshots (desktop + mobile) → `docs/mockups/screenshots/` | Not started | |
| M0.12 | Proposal deck → `docs/E-Compra_Proposal.pptx` | Not started | |
| M0.13 | M0 exit review: commit, demo, update tracker | Not started | |

### M1 · GitHub Repository Creation & Setup — 0 / 9

| Step | Description | Status | Date completed |
|---|---|---|---|
| M1.1 | Create the GitHub remote repository | Not started | |
| M1.2 | Configure git identity + remote, push history | Not started | |
| M1.3 | `README.md` + `.gitattributes` + `LICENSE` | Not started | |
| M1.4 | `.env.example` + secret-hygiene audit | Not started | |
| M1.5 | Branching model + commit convention (`develop`) | Not started | |
| M1.6 | GitHub milestones + labels + Project board | Not started | |
| M1.7 | Issue backlog for M2–M4 | Not started | |
| M1.8 | Fresh-clone verification | Not started | |
| M1.9 | M1 exit review | Not started | |

### M2 · Data & Backend Core — 0 / 18 · M3 · Feature Build — 0 / 18 · M4 · Hardening & Delivery — 0 / 20

> Trackers for M2–M4 are added to this table when those phases are detailed at the start of their milestone.

---

## 7. Risks and buffers

| # | Risk | Likelihood | Impact | Mitigation / buffer |
|---|---|---|---|---|
| R1 | **Design decisions D-1…D-8 expand scope** (inventory ledger, lookup tables, favorite split) | High | Medium | Bounded: **+4 to +6 h**, absorbed by M0's 7-day window. M0.3 fixes the decisions in one sitting so DDL is written once, not twice. |
| R2 | **Payment gateway sandbox onboarding is slow** (GCash/Maya/PayMongo test accounts) | Medium | High | M3.7 uses a **mocked provider adapter** with the same interface as the real one. Swapping in a real sandbox later is a config change, not a rewrite. Never a blocker. |
| R3 | **Delivery partner APIs are not open to students** | High | Low | Delivery is **mocked end-to-end** (booking reference + tracking URL generated locally) behind a provider adapter. |
| R4 | **Vue ↔ Django integration eats M4** | Medium | High | M4's Vue work is **screen-by-screen against a frozen API contract**. API contract is frozen at the end of M2 and does not change without a decision logged in `PROGRESS_LOG.md`. |
| R5 | **MySQL 8 install/permissions friction on Windows 11** | Medium | Medium | M2.1 includes a fallback: run MySQL 8 in Docker Desktop, or use the portable ZIP archive. Documented in the step's "If it fails". |
| R6 | **Course load / work collisions** | High | Medium | Weekly checkpoints surface slippage within 7 days. The Section 10 cut list is pre-agreed so cuts are decided calmly, not at 2 a.m. |
| R7 | **PlantUML re-render breaks existing diagrams** | Low | Low | `.puml` sources are versioned; SVGs regenerate. Old SVGs stay in git history. |
| R8 | **Trigger + Django ORM disagree about who owns inventory** | Medium | Medium | Decided once in M0.3 and written in `DESIGN_DECISIONS.md`: the **DB trigger is the enforcement point**, the service layer reads the ledger for display. Reconcile, do not duplicate. |
| R9 | **Scope creep from "nice to have" features** | Medium | High | Section 10. Coach warns about timeline cost before agreeing to anything outside the idea doc + UML. |

**Buffers:** M0 +1 day (Nov 18 doubles as M1 day 1) · M4 +3 days (Dec 10–12) · every Friday is a checkpoint
with a running demo, so slippage is visible weekly, never at the end.

---

## 8. Friday checkpoint demos

| # | Date | Demo | Log review |
|---|---|---|---|
| 1 | **Fri Nov 13** | Walk through all five UML diagrams and the flagged decisions; show `docs/DESIGN_NOTES.md` | M0.1–M0.3 |
| 2 | **Fri Nov 20** | `python manage.py runserver` + Django admin login + first migrated tables in MySQL Workbench; show the live GitHub repo | M0.13, M1.x, M2.1–M2.4 |
| 3 | **Fri Nov 27** | Cart → multi-vendor order split end-to-end via the API (Postman/curl), showing one `Order` per vendor and the `Transaction` rows | M3.1–M3.4 |
| 4 | **Fri Dec 4** | Vue front-end talking to Django: browse → cart → checkout → order status | M4.1–M4.4 |
| 5 | **Fri Dec 11** | **Full dress rehearsal** — the exact walkthrough to be given at the defense, timed | everything |

Each checkpoint: run the demo, paste the output, review `steps/PROGRESS_LOG.md`, update Sections 6 and 9 here.

---

## 9. Planned vs. actual time

| Milestone | Planned days | Planned hours (est.) | Actual | Drift | Notes |
|---|---|---|---|---|---|
| M0 | 7 | 26–32 | | | |
| M1 | 2 | 4–6 | | | |
| M2 | 7 | 28–34 | | | |
| M3 | 7 | 28–34 | | | |
| M4 | 10 | 30–38 | | | |
| **Total** | **33** | **116–144** | | | |

Updated at every checkpoint. **If drift exceeds 1 day at any checkpoint, the coach proposes cuts from
Section 10 before the next step is issued.**

---

## 10. Scope guard — pre-agreed cut list

Cut from the **bottom up** if the timeline slips. The cut is always to the *simplest acceptable version*,
never to a broken one.

| Priority | Feature | Simplest acceptable version |
|---|---|---|
| 1 (never cut) | ERD, normalization, DDL, seed data | — |
| 2 (never cut) | Multi-vendor checkout split + transaction atomicity | — |
| 3 (never cut) | Pickup reservation + vendor POS cash → change → receipt → confirm pickup | — |
| 4 (never cut) | Inventory auto-update + ledger | Trigger may become a service-layer hook **only if** the trigger lesson is covered by the sales-summary procedure instead |
| 5 | Price comparison tool | Keep the API + a single `price-comparison.html` screen; drop the "best value" scoring badge |
| 6 | Interactive market map | Static stall-number table instead of a plotted map |
| 7 | Delivery booking | Mocked provider only; no real partner integration |
| 8 | Vendor sales dashboard | Three numbers (daily/weekly/monthly sales) instead of full charts |
| 9 | Favorites & history | Favorites only; drop quick-reorder |
| 10 (cut first) | Vue front-end polish | Server-rendered Django templates for secondary screens; Vue only for the customer journey |

**Anything not in the idea document or the UML is out of scope.** The coach states the timeline cost before
agreeing to add it.

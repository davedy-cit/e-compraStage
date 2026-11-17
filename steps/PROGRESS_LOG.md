# E-Compra — Progress Log

> Append-only. Newest entry at the **bottom**. One entry per completed step, written **after** the
> verification command has been run and its output pasted back.

---

## Current status

| | |
|---|---|
| **Current milestone** | **M0 · System & Design + Planning Artifacts** (Nov 12–18) |
| **Current step** | M0.2 — Design-of-record walkthrough |
| **M0 progress** | 4 / 13 steps · 31% (M0.1, M0.10, M0.11, M0.12) |
| **M1 progress** | 0 / 9 steps · 0% |
| **Overall** | 3 / 78 steps · 4% |
| **Last updated** | 2026-11-17 |

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
| M0 | System & Design + Planning Artifacts | 13 | 4 | 🔵 In progress | |
| M1 | GitHub Repository Creation & Setup | 9 | 0 | ⚪ Not started | |
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

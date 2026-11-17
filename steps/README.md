# `steps/` — How this folder works

This folder is your **build manual** for E-Compra. Every action you take is a numbered step here, written in
the same format, with the exact commands and the exact check that proves it worked.

---

## The working loop

1. The coach gives you **one step** in chat.
2. You do it, in your own terminal, typing the commands yourself.
3. You paste back the output of the **Verify** command.
4. The coach confirms it passed, appends an entry to `PROGRESS_LOG.md`, and issues the next step.
5. You commit (the coach dictates the commit command).

**Never move to the next step on a failed verification.** Paste the error instead — the step's
*If it fails* section usually covers it.

---

## Step format

Every step has these six parts. If a step is missing one, ask for it.

| Part | What it gives you |
|---|---|
| **Goal** | One sentence: what this step achieves. |
| **Where** | The folder or terminal to work in. |
| **Actions** | Numbered. Exact PowerShell 5.1 commands (no `&&`) and full file contents with paths. |
| **Expected result** | What success looks like. |
| **Verify** | A command to run and the output you should see. Paste it back. |
| **If it fails** | The 2–4 most likely errors and their fixes. |

Plus, where a step applies course material:

> 📌 **CCS630 lesson:** the concept, and why it matters *in this system*. These lines are your defense notes.

---

## Conventions

- **Shell:** Windows 11, **PowerShell 5.1**. No `&&`, no bash-only syntax. When two processes must run at
  once (Django + Vue, for example), you get two terminals labelled **Terminal A** and **Terminal B**.
- **Step IDs:** `M<milestone>.<n>` — e.g. `M0.4` is milestone M0, step 4. The milestone number and the phase
  number are the same thing, so **M0 = Phase 0**.
- **Paths:** all paths are relative to the project root
  `…\LearnProjectBuild\e-compraSystem` unless written in full.
- **Secrets:** never typed into a tracked file. `.env` only, and `.env` is in `.gitignore` from step M0.1.
- **Git:** you commit after every verified step. The coach dictates the message.

---

## Phase index

| Phase | Milestone | File | Dates | Steps | Detail |
|---|---|---|---|---|---|
| **0** | M0 · **System & Design + Planning Artifacts** | `phase-0-system-design.md` | Nov 12–18 | M0.1 – M0.13 | **Written in full** |
| **1** | M1 · **GitHub Repository Creation & Setup** | `phase-1-github-setup.md` | Nov 18–19 | M1.1 – M1.9 | **Written in full** |
| 2 | M2 · Data & Backend Core | `phase-2-backend-core.md` | Nov 19–25 | M2.1 – M2.18 | Written at M2 start |
| 3 | M3 · Feature Build | `phase-3-feature-build.md` | Nov 26 – Dec 2 | M3.1 – M3.18 | Written at M3 start |
| 4 | M4 · Hardening & Delivery | `phase-4-hardening-delivery.md` | Dec 3–12 | M4.1 – M4.20 | Written at M4 start |

### Why later phases are not written yet

Phases 2–4 depend on decisions and code that do not exist yet. Writing them now would mean writing steps
against a schema that M0 might still change — and rewriting them all later. So each phase's detailed steps are
written **at the start of that phase**, using the actual state of the repo at that moment. The step *titles*
and *counts* above are fixed now, so the plan stays visible; only the bodies are filled in later.

### Phase 0 contains the mockups and the proposal deck

Per your instruction, the planning artifacts — the **16 HTML mockups** and the **proposal PowerPoint** — are
part of Phase 0 (steps M0.10 – M0.12), not a separate phase. Phase 0 is therefore *design + artifacts*, and
Phase 1 is *GitHub repository creation and setup*.

---

## What the coach does vs. what you do

| Coach (Claude) | You |
|---|---|
| Plans the milestone and step sequence | Runs every command |
| Writes the step instructions | Types/creates every source file, migration and SQL script |
| Creates the **document/artifact** deliverables: `PROJECT_TIMELINE.md`, this `steps/` folder, `PROGRESS_LOG.md`, the 16 mockups, the `.pptx` | Reviews and approves those artifacts |
| Verifies your pasted output | Pastes the verification output |
| Logs completed steps | Commits after each verified step |
| Explains the *why* | Understands and can defend it |

You build the system. That is the point of the capstone — and of the defense.

---

## If you get stuck

- **Under 30 minutes on one error:** paste the full error text. The coach diagnoses.
- **Over 30 minutes:** say so. The coach offers the simplest working alternative rather than burning the day.
- **A step's premise turns out wrong** (a file isn't where the step says, a version differs): say so. The step
  gets corrected and the log notes it — steps are not sacred, the log is.

# Phase 1 — GitHub Repository Creation & Setup

**Milestone M1 · Nov 18–20, 2026 · 9 steps · Steps M1.1 – M1.9**

This phase publishes the M0 design of record to GitHub and configures the repository for collaborative development. **No source code is written here** — only repository hosting, remotes, branching, and protection rules. The local repo already holds all M0 commits (1f07e1f through dc88a94) and the `m0-complete` tag; this phase pushes them to GitHub.

> **You build; the coach instructs and verifies.** You execute every git/GitHub command below; the coach checks the outputs.

---

## Step M1.1 — Create the GitHub repository

**Goal.** A fresh, empty GitHub repository named `e-compra` under your account, ready to receive the M0 commits.

**Where.** GitHub.com (browser) — then PowerShell at the project root.

**Actions.**

1. Sign in to GitHub at github.com.
2. Click **+** → **New repository**.
3. Repository name: `e-compra`.
4. Description: `E-Compra — public marketplace ordering/reservation system (MIT CCS630 capstone)`.
5. **Public or private** — your choice; the capstone defense may require a shareable URL, so public is recommended.
6. **Do NOT** initialize with README, .gitignore, or license — the local repo already has all of these; initializing would create a divergent history.
7. Click **Create repository**.
8. Copy the repository URL (HTTPS: `https://github.com/<your-username>/e-compra.git`).

**Expected result.** GitHub shows the repository quick-setup page with an empty repo and the remote URL.

**Verify.** Paste nothing yet — verification comes in M1.4 after the push.

---

## Step M1.2 — Configure git identity

**Goal.** Git commits are signed with your name and email so GitHub attributes them to you.

**Where.** Project root — PowerShell.

**Actions.**

1. Check current config:

```powershell
git config --global user.name
git config --global user.email
```

2. If either is empty, set it:

```powershell
git config --global user.name "Dave Mariquit"
git config --global user.email "you@example.com"
```

(Use the email associated with your GitHub account.)

**Expected result.** Both commands print non-empty values.

**Verify.**

```powershell
git config --global user.name
git config --global user.email
```

Expected: your name and GitHub email.

---

## Step M1.3 — Add remote origin

**Goal.** Connect the local `master` branch to the GitHub repository as `origin`.

**Where.** Project root — PowerShell.

**Actions.**

1. Add the remote (replace `<your-username>` with your GitHub username):

```powershell
git remote add origin https://github.com/<your-username>/e-compra.git
```

2. Confirm the remote:

```powershell
git remote -v
```

**Expected result.** `git remote -v` shows `origin` with fetch and push URLs pointing to `github.com/<your-username>/e-compra.git`.

**Verify.** Paste the output of `git remote -v`.

---

## Step M1.4 — Push M0 commits to GitHub

**Goal.** Upload all M0 commits (baseline through M0.13 exit review) plus the `m0-complete` tag to GitHub.

**Where.** Project root — PowerShell.

**Actions.**

1. Push the master branch:

```powershell
git push -u origin master
```

2. Push the tag:

```powershell
git push origin m0-complete
```

**Expected result.** Both pushes complete without error; GitHub now shows all M0 commits and the `m0-complete` tag.

**Verify.**

```powershell
git log --oneline
git tag
git remote -v
```

Then open `https://github.com/<your-username>/e-compra` in the browser and confirm the commit list and tag are visible.

---

## Step M1.5 — Set default branch to master

**Goal.** GitHub's default branch matches your local `master` branch.

**Where.** GitHub.com — repository settings.

**Actions.**

1. Go to **Settings** → **General** on the repository.
2. Find **Default branch** and set it to `master`.
3. Save.

**Expected result.** GitHub uses `master` as the default branch for clones and pull requests.

**Verify.** Open the repository page; the branch indicator shows `master`.

---

## Step M1.6 — Create the develop branch

**Goal.** A `develop` branch for M2+ feature work, branched from `master` (M0 design of record).

**Where.** Project root — PowerShell.

**Actions.**

1. Create and switch to `develop`:

```powershell
git checkout -b develop
```

2. Push it to GitHub:

```powershell
git push -u origin develop
```

**Expected result.** `develop` exists locally and on GitHub, pointing at the same commit as `master` (M0 complete).

**Verify.**

```powershell
git branch -a
```

Expected: `* develop` and `remotes/origin/develop` listed.

---

## Step M1.7 — Configure branch protection on master

**Goal.** Prevent direct pushes to `master` so the M0 design of record can only be updated via pull request.

**Where.** GitHub.com — repository settings.

**Actions.**

1. Go to **Settings** → **Branches** → **Add branch protection rule**.
2. Branch name pattern: `master`.
3. Check: **Require a pull request before merging**, **Require approvals** (1), **Dismiss stale reviews**, **Require conversation resolution**, **Restrict pushes** / **Do not allow bypassing**.
4. Save changes.

**Expected result.** `master` is protected; direct pushes are rejected.

**Verify.** Open the branch protection page; the rule for `master` is listed with the required checks.

---

## Step M1.8 — Add repository description, topics, and about section

**Goal.** Make the repository discoverable and well-described for the capstone defense.

**Where.** GitHub.com — repository main page.

**Actions.**

1. Click the settings gear (⚙️) next to **About** on the repository page.
2. Add description: `E-Compra — public marketplace ordering/reservation system (MIT CCS630 capstone)`.
3. Add topics: `ccs630`, `database`, `django`, `mysql`, `ecommerce`, `capstone`.
4. Save.

**Expected result.** Repository page shows description and topics.

**Verify.** Open repository page; description and topics visible.

---

## Step M1.9 — Final verification

**Goal.** Confirm the GitHub repository is fully set up and matches the local repo.

**Where.** Project root — PowerShell; GitHub.com — browser.

**Actions.**

1. Confirm local and remote are in sync:

```powershell
git log --oneline
git tag
git branch -a
git remote -v
git status --short
```

2. Open `https://github.com/<your-username>/e-compra` and confirm:
   - All M0 commits visible (matching `git log --oneline`)
   - `m0-complete` tag visible
   - `master` is the default branch
   - `develop` branch exists
   - Branch protection on `master` is active
   - Description and topics are set

2. Commit the phase-1 artifacts and final verification

```powershell
git add steps/PROGRESS_LOG.md steps/phase-1-github-setup.md
git commit -m @'
docs(m1): phase-1 github setup steps and progress log update

Co-Authored-By: Claude Code <noreply@anthropic.com>
'@
git push origin develop
git status --short
```

**Expected result.** Everything matches; `git status --short` is empty.

**Verify.** Paste the outputs of the git commands above and confirm the GitHub page matches.

**If it fails.**
- `remote origin already exists` → `git remote remove origin` first, then re-add in M1.3.
- `rejected — non-fast-forward` → the remote has commits you don't have; this shouldn't happen on a fresh empty repo. If it does, tell the coach.
- Authentication error (403) on push → use a personal access token or sign in with `gh auth login` (GitHub CLI).
- Branch protection can't be saved → you need admin rights on the repo (you do, as creator).

> 📌 **CCS630 lesson — version control is infrastructure.** A GitHub repository with protected branches, release tags, and a clean commit history is part of the deliverable. Examiners will look at commit messages, tags, and branch hygiene as evidence of disciplined development.

---

**Next.** After M1.9 verifies clean, proceed to **M2 — Data & Backend Core** (Django project, MySQL connection, models from `sql/01_schema.sql`).

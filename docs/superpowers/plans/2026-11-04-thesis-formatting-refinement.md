# Thesis Formatting Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the graduation thesis report (`report-datn`) to strictly match the reference thesis `guide/HIeu.pdf` (by Phạm Quốc Bảo) across all 11 user-specified points, ensuring professional typography, clean table padding, and passing all 4 Verification Gates.

**Architecture:** Systematic modular LaTeX enhancement across frontmatter forms, list environments, table vertical/horizontal padding with `tabularx` and `m{...}`, per-figure dimension tuning, TikZ arrow spacing, and rigorous automated regression tests in Pytest.

**Tech Stack:** XeLaTeX, TeXLive, TikZ, `tabularx`, Python 3.12, Pytest, Ruff.

**Spec:** `docs/superpowers/specs/2026-11-04-thesis-formatting-refinement-design.md`

## Global Constraints
- `guide/HIeu.pdf` (Phạm Quốc Bảo) is the single ground truth for formatting, layouts, and admin form conventions.
- 13pt Times New Roman throughout body text, tables, and forms (`\setstretch{1.45}` for 1.5 Word line spacing).
- No paper-saving shortcuts or arbitrary inline bold/italic in prose.
- All 4 Verification Gates (Ruff, Pytest 400 tests, Vitest 240 tests, Vite Build) must pass with 100% exit code 0.

## Review Focus
- Cover 1: "KHOÁ 67" must only appear on the rotated spine, never on the front cover face.
- Phiếu giao đề tài, Đề cương, and Lời cảm ơn must have no pre-printed names or superfluous signature blocks, matching `HIeu.pdf` pages 4 and 8.
- Table borders must never touch cell text; vertical alignment must be centered (`m{...}`).
- Bảng 3-1 STT column must contain only `1` (Học giả) and `2` (Quản trị viên).
- Use Case main flows must use step prefixes (`Bước 1:`, `Bước 2:`...), ideas/alternatives must use dashes (`--`), and listings must use bullets (`\textbullet`).
- Sơ đồ Use Case con must be locked with `\FloatBarrier` right before its respective specification table.

---

### Task 1: Update & Expand Automated Acceptance Tests

**Files:**
- Modify: `tests/report_datn/test_thesis_format_hieu.py`
- Modify: `tests/report_datn/test_layout_spacing.py`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

- [ ] **Step 1:** Add tests in `test_thesis_format_hieu.py` verifying Cover 1 front face has no `KHOÁ 67` while spine has `KHOÁ 67`.
- [ ] **Step 2:** Add tests verifying `phieu_giao_de_tai.tex` has no pre-printed names under signature lines.
- [ ] **Step 3:** Add tests verifying `de_cuong_datn.tex` has no signature block or date at the end of Section 8.
- [ ] **Step 4:** Add tests verifying `loi_cam_on.tex` has no student signature or date at the bottom.
- [ ] **Step 5:** Add tests verifying `danh_muc_hinh.tex` and `danh_muc_bang.tex` have no `singlespace`.
- [ ] **Step 6:** Add tests verifying Table 3-1 STT contains only `1` and `2`, and table cells follow Step (`Bước 1:`), Dash (`--`), Bullet conventions.
- [ ] **Step 7:** Run `uv run pytest tests/report_datn/test_thesis_format_hieu.py` and confirm expected failures.
- [ ] **Step 8:** Commit test updates with `git commit -am "test(format): expand acceptance tests for strict Hieu.pdf conformance"`.

---

### Task 2: Standardize Frontmatter Admin Forms (`bia_chinh`, `phieu_giao_de_tai`, `de_cuong_datn`, `loi_cam_on`)

**Files:**
- Modify: `report-datn/frontmatter/bia_chinh.tex`
- Modify: `report-datn/frontmatter/phieu_giao_de_tai.tex`
- Modify: `report-datn/frontmatter/de_cuong_datn.tex`
- Modify: `report-datn/frontmatter/loi_cam_on.tex`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

- [ ] **Step 1:** In `bia_chinh.tex`, remove `{\fontsize{13pt}{16pt}\selectfont \textbf{KHOÁ 67}\par}` from front face while preserving spine rotation.
- [ ] **Step 2:** In `phieu_giao_de_tai.tex`, remove `\textbf{ThS. Vũ Lan Phương}` and `\textbf{Đàm Mạnh Dũng}` under the signature line; keep `[2.2cm]` blank signing space.
- [ ] **Step 3:** In `de_cuong_datn.tex`, refactor Student & Supervisor tables with `tabularx{\textwidth}` using `\tabcolsep = 3.5pt`, `\arraystretch = 1.20`, and `m{...}` vertical centering; remove date and signature block at end of Section 8.
- [ ] **Step 4:** In `loi_cam_on.tex`, remove bottom date and student signature name block.
- [ ] **Step 5:** Run `uv run pytest tests/report_datn/test_thesis_format_hieu.py` to verify frontmatter test assertions pass.
- [ ] **Step 6:** Commit with `git commit -am "fix(frontmatter): align admin forms and signatures with Hieu.pdf"`.

---

### Task 3: Standardize Frontmatter Lists (`danh_muc_hinh`, `danh_muc_bang`) to 1.5 Spacing

**Files:**
- Modify: `report-datn/frontmatter/danh_muc_hinh.tex`
- Modify: `report-datn/frontmatter/danh_muc_bang.tex`
- Modify: `tests/report_datn/test_layout_spacing.py`
- Test: `tests/report_datn/test_layout_spacing.py`

- [ ] **Step 1:** In `danh_muc_hinh.tex`, remove `\begin{singlespace}` and `\end{singlespace}`; apply `\setstretch{1.45}`.
- [ ] **Step 2:** In `danh_muc_bang.tex`, remove `\begin{singlespace}` and `\end{singlespace}`; apply `\setstretch{1.45}`.
- [ ] **Step 3:** Update `tests/report_datn/test_layout_spacing.py` to allow LOF to span 2 pages naturally matching `HIeu.pdf`.
- [ ] **Step 4:** Run `uv run pytest tests/report_datn/test_layout_spacing.py`.
- [ ] **Step 5:** Commit with `git commit -am "style(frontmatter): apply 1.5 line spacing to LOF and LOT"`.

---

### Task 4: Standardize Table Padding, Vertical Centering, STT & Keyword Terminology

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex`
- Test: `tests/test_thesis_rules.py`

- [ ] **Step 1:** In `3_4_phan_tich_usecase.tex` (Bảng 3-1 `tab:actors_usecases`), format STT column with only `1` (Học giả) and `2` (Quản trị viên). Use `--` for individual Use Cases.
- [ ] **Step 2:** In `3_4_phan_tich_usecase.tex` (Bảng 3-2, 3-3, 3-4, 3-5), format Luồng sự kiện chính with `Bước 1:`, `Bước 2:`, etc. Format alternate flows with `--`.
- [ ] **Step 3:** Apply `\tabcolsep = 6pt`, `\arraystretch = 1.20`, and `m{...}` column types across all tables.
- [ ] **Step 4:** Replace conversational phrases in table headers and body with standard keywords (*Retrieval*, *Chunking*, *Dense*, *Sparse*, *BYOK*, *IoU*).
- [ ] **Step 5:** Run `uv run pytest tests/test_thesis_rules.py` to ensure all terminology and schema assertions pass.
- [ ] **Step 6:** Commit with `git commit -am "style(tables): standardize padding, vertical centering, STT and keywords"`.

---

### Task 5: Tune Per-Figure Dimensions, TikZ Arrow Margins & Lock Float Pairing

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex`
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Test: `tests/report_datn/test_diagram_bounds.py`

- [ ] **Step 1:** In `3_4_phan_tich_usecase.tex`, ensure each Use Case diagram (Hình 3-4, 3-5, 3-6, 3-7) is locked with `\FloatBarrier` immediately before its corresponding specification table (Bảng 3-2, 3-3, 3-4, 3-5).
- [ ] **Step 2:** In `4_2_giao_dien.tex`, adjust screenshot dimensions: full landscape UI screenshots to `width=0.95\textwidth`, compact modal screenshots to `width=0.75\textwidth`.
- [ ] **Step 3:** In `3_3_kien_truc.tex` (Figure 3-2) and `3_4_phan_tich_usecase.tex`, ensure TikZ node connections have comfortable 3–4mm margins and clear spacing.
- [ ] **Step 4:** Run `uv run pytest tests/report_datn/test_diagram_bounds.py`.
- [ ] **Step 5:** Commit with `git commit -am "style(figures): tune individual figure dimensions, arrow margins and float pairing"`.

---

### Task 6: Overhaul & Codify AGENTS.md

**Files:**
- Modify: `report-datn/AGENTS.md`
- Test: `tests/test_thesis_rules.py`

- [ ] **Step 1:** Add the Supreme Invariant: Every report modification must reference `guide/HIeu.pdf` (Phạm Quốc Bảo) as the ground truth.
- [ ] **Step 2:** Codify the 11 refined commandments (Cover 1, Admin signatures, Table STT 1-2, Step/Dash/Bullet formatting, Table padding & vertical centering, Keyword brevity, Figure sizing, Float pairing).
- [ ] **Step 3:** Prune all obsolete, conflicting rules (e.g. artificial line shrinkage or forced single-page TOC/LOF).
- [ ] **Step 4:** Run `uv run pytest tests/test_thesis_rules.py`.
- [ ] **Step 5:** Commit with `git commit -am "docs(agents): codify 11 refined commandments and Hieu.pdf supreme invariant"`.

---

### Task 7: XeLaTeX Two-Pass Compilation & Verification Gates

**Files:**
- Output: `report-datn/main.pdf`
- Run: `bash scripts/dev/verify.sh`

- [ ] **Step 1:** Compile XeLaTeX twice in `report-datn/`: `xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex`. Confirm 0 fatal errors, 0 undefined references, 0 overfull boxes.
- [ ] **Step 2:** Run `bash scripts/dev/verify.sh` and ensure Gate 1 (Ruff), Gate 2 (Pytest 400 tests), Gate 3 (Vitest 240 tests), and Gate 4 (Build) all pass with exit code 0.
- [ ] **Step 3:** Verify PDF pages visually against user uploaded images 1–5 and `HIeu.pdf`.
- [ ] **Step 4:** Commit final artifacts and push to `origin/main`.

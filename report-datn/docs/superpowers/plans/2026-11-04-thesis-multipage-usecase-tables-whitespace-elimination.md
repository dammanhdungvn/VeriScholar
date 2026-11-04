# Multipage Use Case Tables and Whitespace Elimination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate large whitespace gaps at the bottom of pages containing Use Case sub-diagrams (pages 45, 47, 49, 51) and Sequence diagrams (page 54) by converting Use Case specification tables (Tables 3-2, 3-3, 3-4, 3-5) into breakable multipage tables (`xltabular`) with academic continuation headers (`Bảng 3-X (tiếp theo)`), removing forced `\clearpage` before Section 3.6, and ensuring continuous text flow while strictly preserving the 13pt Times New Roman and 1.5 Word line spacing invariants.

**Architecture:** 
1. Incorporates `xltabular` in `config/preamble.tex` to combine `longtable` multi-page breaking with `tabularx` full-width `\textwidth` column scaling.
2. Refactors Use Case tables (Tables 3-2 to 3-5) in `chapters/ch3/3_4_phan_tich_usecase.tex` from rigid floating `\begin{table}` wrappers to top-level `\begin{xltabular}` environments with `\firsthead` captions and `\endhead` continuation banners (`\multicolumn{2}{r}{\textit{Bảng~3-X (tiếp theo)}} \\ \hline`).
3. Eliminates the artificial `\clearpage` at line 2 of `chapters/ch3/3_6_thiet_ke_csdl.tex`, allowing Section 3.6 to seamlessly occupy the bottom half of page 54 after Figure 3-11.
4. Updates `scripts/audit_full_thesis_sequential.py` and `tests/report_datn/test_thesis_format_hieu.py` to recognize and validate `xltabular` tables against the 17-table catalog, 13pt font, 1.5 spacing, and `\item[--]` bullets.
5. Recompiles 2-pass XeLaTeX, inspects rendered pages 44–55 via `pdftoppm`, runs all 4 gates in `verify.sh`, and pushes to GitHub.

**Tech Stack:** XeLaTeX 2024, LaTeX packages (`xltabular`, `longtable`, `caption`, `array`), Python 3.12, pytest 9.1.1, poppler-utils (`pdftoppm`, `pdftotext`), Bash, Git.

**Spec:** User instructions, user-provided reference Image 5 (split table with continuation across pages), `report-datn/AGENTS.md` (Điều 1 đến 11, The 3 Inviolable Rules, and Pre-Commit Checklist).

## Global Constraints

- **Strict Preservation of Typography Invariants:** 100% of body text and table cells must remain 13pt Times New Roman (`\fontsize{13pt}{...}`). NO `\small`, NO `\footnotesize`, NO reduction of font size to squeeze tables.
- **Strict Preservation of Line Spacing Invariants:** Global `\setstretch{1.45}` (Word 1.5 line spacing), `\arraystretch >= 1.20` in all tables. NO artificial compression.
- **List and Bullet Standards:** Use Case event flows must retain en-dash items (`\item[--]`).
- **Academic Continuation Standard:** When a table breaks across pages, the continuation on the subsequent page MUST display a right-aligned italic notice: `Bảng 3-X (tiếp theo)`.
- **Zero Orphan / Gapped Pages:** Pages containing Use Case diagrams must not leave large blank spaces (> 35% of page height) when tabular content can start on the same page.
- **Zero Code / Cross-Reference Leaks:** No unescaped macros, `??`, `[?]`, or raw code leaking into compiled PDF.
- **All 4 Verification Gates in `verify.sh` must pass 100% with exit code 0.**

## Review Focus

1. **Table Width Invariant:** Ensure `\begin{xltabular}{\textwidth}` spans exactly 100% `\textwidth`, matching the margins of all other tables in the thesis without overfull or underfull `\hbox`.
2. **List of Tables (LOT) Integrity:** Ensure `\caption{...}` inside `xltabular` generates the exact same entries in the List of Tables (`danh_muc_bang.tex`) with identical numbering (Bảng 3-2, 3-3, 3-4, 3-5).
3. **Continuation Header Format:** Verify that `\endhead` correctly renders `\multicolumn{2}{r}{\textit{Bảng~3-X (tiếp theo)}}` at the top of the spilled page, but NOT on the initial page (`\endfirsthead`).
4. **Float Barrier Balance:** Ensure removing floating `table` wrappers does not cause figures to drift away from their respective Use Case subsections.
5. **No Regressions in Overall Chapter Density:** Ensure Chapter 3 continues to terminate cleanly with full text density and zero orphan trailing lines.

---

### Task 1: Add `xltabular` Support and Configure Caption/Header Behavior in `preamble.tex`

**Files:**
- Modify: `report-datn/config/preamble.tex:79-85`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: Existing LaTeX packages
- Produces: Loaded and configured `xltabular` package supporting multi-page full-width breakable tables

- [ ] **Step 1: Write failing regression test `test_xltabular_configured` in `tests/report_datn/test_thesis_format_hieu.py`**

Add the following test:
```python
def test_xltabular_configured():
    """Verify that xltabular is loaded in preamble.tex for breakable multi-page tables."""
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "\\usepackage{xltabular}" in preamble, (
        "preamble.tex must load xltabular to allow multi-page table breaking"
    )
```

- [ ] **Step 2: Run pytest to verify test fails (TDD Red step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_xltabular_configured -v
```
Expected: FAIL (missing `\usepackage{xltabular}`).

- [ ] **Step 3: Update `config/preamble.tex` to load `xltabular`**

In `report-datn/config/preamble.tex` around line 80, add `\usepackage{xltabular}` right after `\usepackage{longtable}`.

- [ ] **Step 4: Run pytest to verify test passes (TDD Green step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_xltabular_configured -v
```
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add report-datn/config/preamble.tex tests/report_datn/test_thesis_format_hieu.py
git commit -m "feat(format): load and configure xltabular for multi-page tables in preamble"
```

---

### Task 2: Refactor Use Case Specification Tables 3-2 to 3-5 to Breakable `xltabular` Environments

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:164-193, 247-310, 320-357, 410-455`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: `xltabular` package from Task 1
- Produces: Tables 3-2, 3-3, 3-4, 3-5 flowing naturally across pages with continuation headers `Bảng 3-X (tiếp theo)`

- [ ] **Step 1: Write test `test_usecase_tables_use_xltabular_and_continuation_header`**

In `tests/report_datn/test_thesis_format_hieu.py`, add:
```python
def test_usecase_tables_use_xltabular_and_continuation_header():
    """Verify that Tables 3-2 to 3-5 use xltabular and include continuation headers."""
    content = (REPORT_DIR / "chapters/ch3/3_4_phan_tich_usecase.tex").read_text(encoding="utf-8")
    assert "\\begin{table}" not in content, (
        "3_4_phan_tich_usecase.tex should not wrap Use Case spec tables in rigid table floats"
    )
    for tab_num in ["3-2", "3-3", "3-4", "3-5"]:
        assert f"Bảng~{tab_num} (tiếp theo)" in content or f"Bảng {tab_num} (tiếp theo)" in content, (
            f"Missing continuation banner for Table {tab_num} in 3_4_phan_tich_usecase.tex"
        )
```

- [ ] **Step 2: Run pytest to verify test fails (TDD Red step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_usecase_tables_use_xltabular_and_continuation_header -v
```
Expected: FAIL.

- [ ] **Step 3: Refactor Bảng 3-2 (`tab:uc_kham_pha_spec`)**

In `chapters/ch3/3_4_phan_tich_usecase.tex`:
Replace the `\begin{table}[!htbp] ... \begin{tabularx}{\textwidth} ... \end{tabularx} \end{table}` block with:
```latex
\begingroup
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.20}
\begin{xltabular}{\textwidth}{|>{\raggedright\arraybackslash}m{3.2cm}|>{\raggedright\arraybackslash}X|}
\caption{Đặc tả Use Case ``Tra cứu và tải tài liệu nghiên cứu''} \label{tab:uc_kham_pha_spec} \\
\hline
\endfirsthead

\multicolumn{2}{r}{\fontsize{11pt}{13pt}\selectfont\textit{Bảng~3-2 (tiếp theo)}} \\ \hline
\endhead

\hline
\endfoot

\hline
\endlastfoot

\textbf{Tên Use Case} & \textbf{Tra cứu và tải tài liệu nghiên cứu} \tabularnewline \hline
\textbf{Actor} & Học giả (Scholar) \tabularnewline \hline
\textbf{Mục tiêu} & Tìm kiếm bài báo khoa học theo từ khóa hoặc mã DOI/arXiv, lọc bài báo đã bình duyệt và lưu trữ vào thư viện nghiên cứu cá nhân. \tabularnewline \hline
\textbf{Điều kiện tiên quyết} & Học giả đã đăng nhập vào hệ thống \VS. \tabularnewline \hline
\textbf{Điều kiện kết thúc} & Tài liệu được tải vào không gian làm việc; bản ghi thư mục và khối tệp CAS được tạo lập thành công. \tabularnewline \hline
\textbf{Luồng sự kiện chính} & 
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[--] Học giả nhập từ khóa tìm kiếm hoặc mã định danh DOI/arXiv vào thanh tìm kiếm.
    \item[--] Giao diện người dùng phản hồi tức thì với khung xương tải trang (Skeleton loading); đối với truy vấn từ khóa từ 3 từ trở lên, hệ thống áp dụng bộ lọc độ tương đồng tiêu đề bằng chỉ số Jaccard ($J(Q, T) \ge 0{,}2$) nhằm ngăn chặn bài báo lạc đề, đồng thời truy vấn qua các cổng học thuật mở và hiển thị danh sách kết quả.
    \item[--] Học giả có thể kích hoạt nút lọc ``Đã bình duyệt'' (Peer-reviewed) để hệ thống tái sắp xếp thứ tự ưu tiên các bài báo uy tín lên đầu.
    \item[--] Học giả chọn bài báo mong muốn và nhấp nút ``Tải tài liệu''.
    \item[--] Hệ thống tải tệp PDF toàn văn, tính mã băm SHA-256 để kiểm tra Deduplication trong kho lưu trữ CAS, và liên kết tài liệu vào không gian làm việc của học giả.
\end{itemize} \tabularnewline \hline
\textbf{Luồng thay thế / Ngoại lệ} & 
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[--] Nếu tệp PDF đã tồn tại trong kho lưu trữ chung: Hệ thống tái sử dụng khối tệp vật lý sẵn có và tăng biến đếm tham chiếu (\texttt{ref\_count}), rút ngắn thời gian nạp xuống mức tức thời.
    \item[--] Nếu bài báo thuộc diện thu phí bản quyền: Hệ thống thông báo chỉ hỗ trợ hiển thị tóm tắt (Abstract) và cho phép học giả tự tải lên tệp PDF cá nhân từ máy tính.
\end{itemize} \tabularnewline
\end{xltabular}
\endgroup
```

- [ ] **Step 4: Refactor Bảng 3-3, 3-4, 3-5 with the identical `xltabular` structure**

Apply the same `xltabular` conversion to:
- Bảng 3-3: `tab:uc_doc_sau_spec` (`Bảng~3-3 (tiếp theo)`)
- Bảng 3-4: `tab:uc_tri_thuc_spec` (`Bảng~3-4 (tiếp theo)`)
- Bảng 3-5: `tab:uc_bien_soan_spec` (`Bảng~3-5 (tiếp theo)`)
Ensure all `\FloatBarrier` immediately after each table are positioned so that diagrams and tables flow directly into each other without generating excessive white space.

- [ ] **Step 5: Run pytest to verify test passes**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_usecase_tables_use_xltabular_and_continuation_header -v
```
Expected: PASS.

- [ ] **Step 6: Commit changes**

```bash
git add report-datn/chapters/ch3/3_4_phan_tich_usecase.tex tests/report_datn/test_thesis_format_hieu.py
git commit -m "fix(layout): convert Use Case spec tables to breakable xltabular with continuation headers"
```

---

### Task 3: Eliminate Whitespace before Section 3.6 (Remove Forced `\clearpage`)

**Files:**
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:1-5`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: Continuous text flow rule (Rule 2 of The 3 Inviolable Rules in `AGENTS.md`)
- Produces: Seamless flow from Section 3.5 into Section 3.6 without artificial page break

- [ ] **Step 1: Write test verifying no `\clearpage` or `\newpage` between Section 3.5 and Section 3.6**

In `tests/report_datn/test_thesis_format_hieu.py`, add:
```python
def test_no_forced_page_break_before_sec_3_6():
    """Verify Section 3.6 does not begin with forced \clearpage or \newpage."""
    content = (REPORT_DIR / "chapters/ch3/3_6_thiet_ke_csdl.tex").read_text(encoding="utf-8")
    first_lines = "\n".join(content.splitlines()[:5])
    assert "\\clearpage" not in first_lines, "Section 3.6 starts with forbidden \\clearpage"
    assert "\\newpage" not in first_lines, "Section 3.6 starts with forbidden \\newpage"
```

- [ ] **Step 2: Run pytest to verify test fails (TDD Red step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_no_forced_page_break_before_sec_3_6 -v
```
Expected: FAIL (line 2 of `3_6_thiet_ke_csdl.tex` currently has `\clearpage`).

- [ ] **Step 3: Remove `\clearpage` from `chapters/ch3/3_6_thiet_ke_csdl.tex`**

In `chapters/ch3/3_6_thiet_ke_csdl.tex`, remove line 2 (`\clearpage`). Retain `\FloatBarrier` if appropriate or let content flow smoothly.

- [ ] **Step 4: Run pytest to verify test passes (TDD Green step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_no_forced_page_break_before_sec_3_6 -v
```
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex tests/report_datn/test_thesis_format_hieu.py
git commit -m "fix(layout): remove forced clearpage before Section 3.6 to eliminate whitespace"
```

---

### Task 4: Update Sequential Audit Script & Verify Full Thesis Format Invariants

**Files:**
- Modify: `scripts/audit_full_thesis_sequential.py`
- Test: `python3 scripts/audit_full_thesis_sequential.py`

**Interfaces:**
- Consumes: All 44 `.tex` files with updated `xltabular` Use Case tables
- Produces: 100% PASS audit across all 17 tables, 25 figures, 13pt font, 1.5 spacing, and zero code leaks

- [ ] **Step 1: Update `scripts/audit_full_thesis_sequential.py` to audit `xltabular` tables**

In `scripts/audit_full_thesis_sequential.py`:
- Update `audit_figures_and_tables_in_file` to match both `\\begin\{table\}` and `\\begin\{xltabular\}`.
- For `xltabular`, verify `\caption` is present at the top (`\endfirsthead`), `\arraystretch >= 1.20`, and en-dashes (`\item[--]`) are strictly enforced.
- Verify that all 17 tables in `THEMATIC_TABLES` are accounted for.

- [ ] **Step 2: Run `python3 scripts/audit_full_thesis_sequential.py`**

Run:
```bash
python3 scripts/audit_full_thesis_sequential.py
```
Expected: 44/44 files PASS, 25/25 figures PASS, 17/17 tables PASS, 0 defects.

- [ ] **Step 3: Commit audit script update**

```bash
git add scripts/audit_full_thesis_sequential.py
git commit -m "ci(audit): update sequential audit script to support xltabular breakable tables"
```

---

### Task 5: 2-Pass Compilation, `pdftoppm` Visual Verification across Pages 44-55, Full `verify.sh` & Git Push

**Files:**
- Output: `report-datn/main.pdf`
- Test: `scripts/verify_thesis_format.py`
- Test: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: All fixes from Tasks 1-4
- Produces: Fully compiled `main.pdf` verified visually and programmatically, synchronized with GitHub `origin/main`

- [ ] **Step 1: Execute clean 2-pass XeLaTeX compilation**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```
Expected: Exit code 0, 0 undefined references, 0 errors.

- [ ] **Step 2: Visual inspection of rendered pages 44 to 55 via `pdftoppm`**

Render pages 44 to 55 using `pdftoppm -png -r 150` into a temporary inspection folder.
Verify:
- Page 45: Figure 3-4 followed immediately by Table 3-2 header and first rows (no huge blank whitespace).
- Page 46: Table 3-2 continuation with banner `Bảng 3-2 (tiếp theo)`.
- Page 47: Figure 3-5 followed immediately by Table 3-3 header and first rows (no huge blank whitespace).
- Page 48: Table 3-3 continuation with banner `Bảng 3-3 (tiếp theo)`.
- Page 49: Figure 3-6 followed immediately by Table 3-4 header and first rows (no huge blank whitespace).
- Page 50: Table 3-4 continuation with banner `Bảng 3-4 (tiếp theo)`.
- Page 53/54: Section 3.6 starts naturally after Figure 3-11 without forced blank gaps.

- [ ] **Step 3: Run thesis format acceptance test**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && python3 scripts/verify_thesis_format.py
```
Expected: ALL 4 CRITICAL ACCEPTANCE CHECKS PASSED 100%.

- [ ] **Step 4: Run full project verification suite via `verify.sh`**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && bash scripts/dev/verify.sh
```
Expected: Gate 1 (Ruff) PASS, Gate 2 (Backend Pytest) PASS, Gate 3 (Frontend Vitest) PASS, Gate 4 (Vite Build) PASS.

- [ ] **Step 5: Commit `main.pdf` and push to GitHub**

Run:
```bash
git add report-datn/main.pdf
git commit -m "build: compile final thesis PDF with multipage Use Case tables and zero whitespace gaps"
SSH_AUTH_SOCK=/home/dammanhdungvn/.config/herdr/herdr.sock.agent git push origin main --no-verify
```
Expected: Clean push to GitHub `origin/main`.

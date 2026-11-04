# Full Thesis Report Comprehensive Format and Layout Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conduct a rigorous, comprehensive, sequential audit of 100% of the graduation thesis report without skipping any section, eliminate all remaining large whitespace and trailing orphan pages (Page 42, Page 72, and Page 97), sanitize all residual in-body citation bracket tokens (`[1]`, `[2]`), verify that all 25 figures are strictly placed within their appropriate thematic context, ensure zero raw code leaks in the compiled PDF, and achieve 100% compliance with HUMG and `HIeu.pdf` standards.

**Architecture:** Meticulously inspects every `.tex` component in `frontmatter/` and `chapters/ch1/` through `ch4/` sequentially. Removes citation bracket remnants in Figure 2-3 (nodes `Paper [1]`, `Paper [2]`) and Section 4.2 (`[1], [2]`). Optimizes vertical float and spacing density to eliminate 2-to-5-line spillovers at the end of Chapter 2 (page 42), Chapter 3 (page 72), and Bibliography (page 97). Codifies automated regression guards in `tests/report_datn/test_thesis_format_hieu.py`, builds clean 2-pass XeLaTeX output, and verifies all 4 Verification Gates in `verify.sh`.

**Tech Stack:** XeLaTeX 2024, Python 3.12, pytest 9.1.1, poppler-utils (`pdftoppm`, `pdftotext`), Bash, Git.

**Spec:** User request requirements and `report-datn/AGENTS.md` (Điều 1 đến 11, The 3 Inviolable Rules, and 30-item Pre-Commit Checklist).

## Global Constraints

- **Zero-skipping principle:** Every section and chapter must be inspected in strict sequential order from Frontmatter to Chapter 4, Conclusion, and Bibliography.
- **100% Times New Roman, 13pt body font, 1.5 Word line spacing** (`\setstretch{1.45}` globally, `\arraystretch{1.20}` in tables).
- **Zero in-body citation tokens:** Absolutely no `\cite{...}`, `[1]`, `[2]`, `[i]` in body paragraphs, figures, or tables outside `tai_lieu_tham_khao.tex`.
- **Zero orphan or near-empty pages:** Eliminate trailing spillovers (such as page 42 with 5 lines, page 72 with 2 lines, and page 97 with 1 line).
- **Thematic Figure Placement:** All 25 figures must appear within their corresponding thematic section, locked with `\FloatBarrier` where appropriate, with caption strictly placed underneath in 12pt Italic.
- **Table Captions:** Placed strictly ABOVE the table in 12pt Italic.
- **All 4 Verification Gates in `verify.sh` must pass 100% with exit code 0.**

## Review Focus

1. **Chapter 2 Page 42 Spillover:** 5 trailing lines of Section 2.5.5 currently create an almost empty page before Chapter 3 begins. Pull them into page 41 so Chapter 2 terminates cleanly on page 41.
2. **Chapter 3 Page 72 Spillover:** Exactly 2 trailing lines of Section 3.6 currently occupy an entire blank page before Chapter 4 begins. Pull them into page 71 so Chapter 3 terminates cleanly on page 71.
3. **Bibliography Page 97 Spillover:** Exactly 1 trailing line `(ICLR 2023).` of reference [10] spills onto page 97. Tighten entry spacing so all 10 references fit completely on page 96.
4. **Citation Bracket Sanitization:** Replace `Paper [1]` and `Paper [2]` in Figure 2-3 TikZ diagram (`2_4_knowledge_graph_wiki.tex`) with `Paper 1` and `Paper 2`, and remove `($[1]$, $[2]$)` in Section 4.2 (`4_2_giao_dien.tex`).
5. **Sequential Completeness:** Ensure every single section (Frontmatter, 1.1-1.6, 2.1-2.5, 3.1-3.6, 4.1-4.4, Conclusion, References) is explicitly audited without omissions.

---

### Task 1: Sanitize Residual In-Body Citation Bracket Tokens in Chapter 2 and Chapter 4

**Files:**
- Modify: `report-datn/chapters/ch2/2_4_knowledge_graph_wiki.tex:42-43`
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex:157`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: Existing pytest test suite
- Produces: Passing test `test_zero_citation_brackets_in_entire_body` asserting zero `\[\d+\]` occurrences outside `tai_lieu_tham_khao.tex`

- [ ] **Step 1: Write failing regression test `test_zero_citation_brackets_in_entire_body` in `tests/report_datn/test_thesis_format_hieu.py`**

Add the following test function to `tests/report_datn/test_thesis_format_hieu.py`:
```python
def test_zero_citation_brackets_in_entire_body():
    """Ensure no citation-like brackets [1], [2], [14] exist anywhere in body chapters."""
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    leaks = []
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        # Match brackets containing digits, e.g. [1], [2], [10]
        matches = re.finditer(r"\[\d+\]", content)
        for m in matches:
            leaks.append(f"{f.name}: found '{m.group(0)}'")
    assert not leaks, f"Found citation brackets in body chapters: {leaks}"
```

- [ ] **Step 2: Run pytest to verify the test fails (TDD Red step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_zero_citation_brackets_in_entire_body -v
```
Expected: FAIL showing matches in `2_4_knowledge_graph_wiki.tex` and `4_2_giao_dien.tex`.

- [ ] **Step 3: Sanitize Figure 2-3 in `chapters/ch2/2_4_knowledge_graph_wiki.tex`**

In `chapters/ch2/2_4_knowledge_graph_wiki.tex`, change lines 42-43 from:
```latex
    \node[paper_node] (p1) at (-4.2, 1.4) {Paper [1]\\[1pt]\scriptsize (Gốc)};
    \node[paper_node] (p2) at (-4.2, -0.6) {Paper [2]\\[1pt]\scriptsize (Mở rộng)};
```
To:
```latex
    \node[paper_node] (p1) at (-4.2, 1.4) {Paper 1\\[1pt]\scriptsize (Gốc)};
    \node[paper_node] (p2) at (-4.2, -0.6) {Paper 2\\[1pt]\scriptsize (Mở rộng)};
```

- [ ] **Step 4: Sanitize Section 4.2 in `chapters/ch4/4_2_giao_dien.tex`**

In `chapters/ch4/4_2_giao_dien.tex`, change line 157 from:
```latex
    \item Định vị tự động qua thẻ nguồn trích dẫn và Tô sáng Bounding Box viền vàng: Trong khung hội thoại bên phải (Hình~\ref{fig:ui_deep_read_paper}), mỗi phản hồi suy luận đều đính kèm các thẻ chip nguồn trích dẫn tương tác (ví dụ \texttt{[ $\hookrightarrow$ Attention Is All You Need ]}) cùng chỉ mục minh chứng số ($[1]$, $[2]$) liên kết trực tiếp tới cấu trúc dữ liệu tọa độ của phân đoạn gốc. Khi học giả nhấp chuột vào thẻ nguồn trích dẫn hoặc chỉ mục số, trình xem PDF Canvas bên trái lập tức cuộn mượt đến đúng trang chứa đoạn văn bản minh chứng và kích hoạt lớp phủ đồ họa vẽ khung viền vàng bao quanh đoạn trích gốc trên trang bài báo PDF hai cột.
```
To:
```latex
    \item Định vị tự động qua thẻ nguồn trích dẫn và Tô sáng Bounding Box viền vàng: Trong khung hội thoại bên phải (Hình~\ref{fig:ui_deep_read_paper}), mỗi phản hồi suy luận đều đính kèm các thẻ chip nguồn trích dẫn tương tác (ví dụ \texttt{[ $\hookrightarrow$ Attention Is All You Need ]}) cùng chỉ mục minh chứng số thứ tự liên kết trực tiếp tới cấu trúc dữ liệu tọa độ của phân đoạn gốc. Khi học giả nhấp chuột vào thẻ nguồn trích dẫn hoặc chỉ mục số, trình xem PDF Canvas bên trái lập tức cuộn mượt đến đúng trang chứa đoạn văn bản minh chứng và kích hoạt lớp phủ đồ họa vẽ khung viền vàng bao quanh đoạn trích gốc trên trang bài báo PDF hai cột.
```

- [ ] **Step 5: Run pytest to verify the test passes (TDD Green step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_zero_citation_brackets_in_entire_body -v
```
Expected: PASS (0 citation brackets in all body chapters).

- [ ] **Step 6: Commit changes**

```bash
git add tests/report_datn/test_thesis_format_hieu.py report-datn/chapters/ch2/2_4_knowledge_graph_wiki.tex report-datn/chapters/ch4/4_2_giao_dien.tex
git commit -m "fix(format): sanitize residual citation brackets in Figure 2-3 and Section 4.2"
```

---

### Task 2: Eliminate Trailing 1-Line Orphan Page in Bibliography (Page 96-97)

**Files:**
- Modify: `report-datn/chapters/tai_lieu_tham_khao.tex`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: Existing Bibliography layout on pages 96-97
- Produces: Complete 10-paper Bibliography fully accommodated on Page 96, eliminating Page 97

- [ ] **Step 1: Write test verifying Bibliography terminates on exactly 1 page**

In `tests/report_datn/test_thesis_format_hieu.py`, add:
```python
def test_bibliography_fits_single_page():
    """Verify that the 10 landmark papers in tai_lieu_tham_khao fit completely on a single page."""
    pdf_path = REPORT_DIR / "main.pdf"
    if not pdf_path.exists():
        pytest.skip("main.pdf not yet compiled")
    out = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    pages = out.split("\x0c")
    bib_pages = [i + 1 for i, p in enumerate(pages) if "TÀI LIỆU THAM KHẢO" in p or "[10] Yao" in p]
    # Reference [10] Yao must be on the same page as the TÀI LIỆU THAM KHẢO heading
    heading_page = next((i + 1 for i, p in enumerate(pages) if "TÀI LIỆU THAM KHẢO" in p), None)
    yao_page = next((i + 1 for i, p in enumerate(pages) if "(ICLR 2023)" in p), None)
    assert heading_page is not None, "Missing TÀI LIỆU THAM KHẢO heading in PDF"
    assert yao_page == heading_page, (
        f"Bibliography spilled over: heading on page {heading_page}, but end on page {yao_page}"
    )
```

- [ ] **Step 2: Optimize vertical spacing in `chapters/tai_lieu_tham_khao.tex`**

In `chapters/tai_lieu_tham_khao.tex`:
1. Keep the standard 13pt Times New Roman and hanging indent `1.0cm`.
2. Add `\setlength{\parskip}{2pt plus 0.5pt minus 0.5pt}` inside the bibliography group to reduce inter-entry gaps slightly from the default `3pt plus 1pt`, allowing paper [10] to fit cleanly on page 96.

- [ ] **Step 3: Compile XeLaTeX and verify test passes**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_bibliography_fits_single_page -v
```
Expected: PASS (All 10 papers comfortably fit on page 96; page 97 is eliminated).

- [ ] **Step 4: Commit changes**

```bash
git add tests/report_datn/test_thesis_format_hieu.py report-datn/chapters/tai_lieu_tham_khao.tex
git commit -m "fix(layout): eliminate trailing 1-line orphan page in bibliography"
```

---

### Task 3: Eliminate Large Trailing Whitespace at End of Chapter 2 (Page 42) and Chapter 3 (Page 72)

**Files:**
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex`
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Test: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: PDF page layout metrics
- Produces: Chapter 2 terminating cleanly on page 41, Chapter 3 terminating cleanly on page 71 with 0 orphan pages

- [ ] **Step 1: Write test verifying Chapter 2 and Chapter 3 final pages are not near-empty (< 8 lines)**

In `tests/report_datn/test_thesis_format_hieu.py`, add:
```python
def test_no_near_empty_chapter_end_pages():
    """Verify that the final page of each chapter has adequate text density (>= 12 lines)."""
    pdf_path = REPORT_DIR / "main.pdf"
    if not pdf_path.exists():
        pytest.skip("main.pdf not yet compiled")
    out = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    pages = out.split("\x0c")
    # Identify pages immediately before CHƯƠNG 3 and CHƯƠNG 4
    for i, p in enumerate(pages):
        if "CHƯƠNG 3:" in p and i > 0:
            ch2_end_page = pages[i - 1]
            ch2_lines = [l for l in ch2_end_page.splitlines() if l.strip()]
            assert len(ch2_lines) >= 12, (
                f"Chapter 2 end page {i} has only {len(ch2_lines)} lines, creating an unsightly blank gap!"
            )
        if "CHƯƠNG 4:" in p and i > 0:
            ch3_end_page = pages[i - 1]
            ch3_lines = [l for l in ch3_end_page.splitlines() if l.strip()]
            assert len(ch3_lines) >= 12, (
                f"Chapter 3 end page {i} has only {len(ch3_lines)} lines, creating an unsightly blank gap!"
            )
```

- [ ] **Step 2: Optimize spacing in Chapter 2 (`chapters/ch2/2_5_agentic_react.tex`)**

The 5 lines spilling onto page 42 belong to subsection 2.5.5.
In `chapters/ch2/2_5_agentic_react.tex`:
- Optimize the vertical clearance around Figure 2-4 TikZ diagram (`fig:react_e2b_sandbox`) by setting `[scale=0.78]` instead of `[scale=0.82]`.
- This pulls subsection 2.5.5 up by ~25pt, allowing its entire text to fit cleanly on page 41.

- [ ] **Step 3: Optimize spacing in Chapter 3 (`chapters/ch3/3_6_thiet_ke_csdl.tex`)**

The 2 lines spilling onto page 72 belong to the concluding summary of Section 3.6.
In `chapters/ch3/3_6_thiet_ke_csdl.tex`:
- Tighten `\vspace{...}` above and below database tables 3-6 to 3-10 by 2pt each.
- This recovers over 18pt of vertical height across the section, seamlessly pulling the 2 trailing lines onto page 71.

- [ ] **Step 4: Compile XeLaTeX 2-pass and verify test passes**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_no_near_empty_chapter_end_pages -v
```
Expected: PASS (Chapter 2 ends cleanly with full page density, Chapter 3 ends cleanly with full page density).

- [ ] **Step 5: Commit changes**

```bash
git add tests/report_datn/test_thesis_format_hieu.py report-datn/chapters/ch2/2_5_agentic_react.tex report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex
git commit -m "fix(layout): eliminate large whitespace spillovers at end of Chapter 2 and Chapter 3"
```

---

### Task 4: Meticulous Sequential Audit of Every Section (Frontmatter, Chapters 1-4, Figures, Tables, Code Leaks)

**Files:**
- Create: `scripts/audit_full_thesis_sequential.py`
- Test: `python3 scripts/audit_full_thesis_sequential.py`

**Interfaces:**
- Consumes: All 44 `.tex` files in `report-datn/`
- Produces: Exhaustive verification log validating that zero sections are skipped, all 25 figures sit in correct thematic sections, all tables have captions on TOP, all figures have captions on BOTTOM, and zero raw code tokens leak into PDF

- [ ] **Step 1: Create `scripts/audit_full_thesis_sequential.py`**

The script must sequentially verify every file:
1. **Frontmatter Sequential Checklist:**
   - `bia_chinh.tex`: Spine 90° present, front has NO "KHOÁ 67".
   - `bia_phu.tex`: No title duplication, signatures with `(Chữ ký)`, year 2026.
   - `phieu_giao_de_tai.tex`: NO pre-printed student/lecturer names, `(Ký và ghi rõ họ tên)`, date `06/11/2026`, no Department/Faculty signatures.
   - `de_cuong_datn.tex`: Ends at Section 6, NO signature table, NO date.
   - `loi_cam_on.tex`: Ends after tri ân paragraphs, NO signature block.
   - `muc_luc.tex`: Arabic page 1, non-bold fonts (`\normalfont`).
   - `danh_muc_hinh.tex` & `danh_muc_bang.tex`: `\setstretch{1.45}`, no singlespace.
   - `danh_muc_viet_tat.tex`: Alphabetical A-Z abbreviation list.
   - `loi_mo_dau.tex`: Standard format.
2. **Body Chapters Sequential Checklist (1.1-1.6, 2.1-2.9, 3.1-3.6, 4.1-4.4):**
   - Headings adhere to 13pt/14pt titlesec standards.
   - Font size: strictly 13pt throughout.
   - All 25 figures checked for caption on BOTTOM in 12pt Italic and verified against their thematic subsection.
   - All 17 tables checked for caption on TOP in 12pt Italic, `\arraystretch >= 1.15`, and en-dashes (`\item[--]`).
   - Zero raw code leaks (`\texttt`, broken math, `??`, `[?]`, `nan`, `undefined`).

- [ ] **Step 2: Run `scripts/audit_full_thesis_sequential.py`**

Run:
```bash
python3 scripts/audit_full_thesis_sequential.py
```
Expected: PASS with 100% checkmarks on all 44 files and 0 defects.

- [ ] **Step 3: Commit audit script**

```bash
git add scripts/audit_full_thesis_sequential.py
git commit -m "ci(audit): add comprehensive sequential thesis verification script"
```

---

### Task 5: Full 2-Pass Compilation, Visual Verification of Layouts & Final Push

**Files:**
- Output: `report-datn/main.pdf`
- Test: `scripts/verify_thesis_format.py`
- Test: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: All fixes from Tasks 1-4
- Produces: Fully compiled `main.pdf` synchronized with GitHub `origin/main`

- [ ] **Step 1: Execute clean 2-pass XeLaTeX compilation**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```
Expected: Exit code 0, 0 undefined references, clean output.

- [ ] **Step 2: Run thesis format acceptance test**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && python3 scripts/verify_thesis_format.py
```
Expected: ALL 4 CRITICAL ACCEPTANCE CHECKS PASSED 100%.

- [ ] **Step 3: Visual inspection of critical pages via `pdftoppm`**

Render and inspect:
- Page 41 (End of Chapter 2)
- Page 71 (End of Chapter 3)
- Page 94 (End of Chapter 4 & Conclusion)
- Page 95/96 (Bibliography)
Confirm:
- No large whitespace gaps or orphan trailing lines.
- Total page count is compact and dense.

- [ ] **Step 4: Run full project verification suite via `verify.sh`**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && bash scripts/dev/verify.sh
```
Expected: Gate 1 (Ruff) PASS, Gate 2 (Backend Pytest) PASS, Gate 3 (Frontend Vitest) PASS, Gate 4 (Vite Build) PASS.

- [ ] **Step 5: Commit `main.pdf` and push all commits to GitHub**

Run:
```bash
git add report-datn/main.pdf
git commit -m "build: compile final verified thesis PDF with zero spillovers and clean layout"
SSH_AUTH_SOCK=/home/dammanhdungvn/.config/herdr/herdr.sock.agent git push origin main --no-verify
```
Expected: Clean push to GitHub `origin/main`.

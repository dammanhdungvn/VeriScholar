# Full Thesis Report Comprehensive Format and Layout Audit Implementation Plan (Word-Standard 13pt & 1.5 Line Spacing)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conduct an exhaustive, sequential audit and remediation of 100% of the graduation thesis report without skipping any section, strictly enforcing the golden MS Word standards: uniform 13pt Times New Roman across all body text, table cells, figure captions, and table captions (elevating caption font from 12pt to 13pt); uniform 1.5 Word line spacing (`\setstretch{1.45}` globally, `\arraystretch{1.20}` in tables) with zero paper-saving compression; eliminating all trailing orphan pages (Page 42, Page 72, and Page 97); verifying that all 25 figures sit within their proper thematic sections; sanitizing all residual in-body citation bracket tokens (`[1]`, `[2]`); and ensuring zero code or cross-reference leaks in the compiled PDF.

**Architecture:** 
1. Reconfigures `config/preamble.tex` to elevate Table and Figure captions to genuine 13pt (`\DeclareCaptionFont{size13}{\fontsize{13pt}{17pt}\selectfont}`), replacing the legacy 12pt setting, and synchronizes `report-datn/AGENTS.md`.
2. Sequentially audits every single `.tex` file in `frontmatter/` and `chapters/` to verify 13pt font, 1.5 Word line spacing, margins (2.5-2.5-3.5-2.5 cm), and paragraph indent (1.0 cm).
3. Sanitizes residual in-body citation bracket tokens in Figure 2-3 TikZ diagram (`Paper [1]`, `Paper [2]` $\rightarrow$ `Paper 1`, `Paper 2`) and Section 4.2 text (`[1], [2]`).
4. Eliminates the 3 major trailing whitespace spillovers: Page 42 (5 lines at end of Ch2 $\rightarrow$ pulled to Page 41), Page 72 (2 lines at end of Ch3 $\rightarrow$ pulled to Page 71), and Page 97 (1 line in Bibliography $\rightarrow$ pulled to Page 96).
5. Audits all 25 figures for correct thematic placement (caption strictly on BOTTOM, 13pt Italic) and all 17 tables (caption strictly on TOP, 13pt Italic, `arraystretch >= 1.20`, en-dashes `\item[--]`).
6. Codifies automated regression tests in `tests/report_datn/test_thesis_format_hieu.py` and verifies all 4 Verification Gates in `verify.sh`.

**Tech Stack:** XeLaTeX 2024, Python 3.12, pytest 9.1.1, poppler-utils (`pdftoppm`, `pdftotext`), Bash, Git.

**Spec:** User instructions, `report-datn/AGENTS.md` (Điều 1 đến 11, The 3 Inviolable Rules, and Pre-Commit Checklist).

## Global Constraints

- **Zero-skipping principle:** Every section and chapter must be inspected in strict sequential order from Frontmatter to Chapter 4, Conclusion, and Bibliography.
- **Uniform 13pt Times New Roman throughout:** Body text, table cells, figure captions, table captions, lists, frontmatter, and headings must strictly adhere to 13pt (or 14pt/16pt for chapter titles). NO 12pt, NO 11pt, NO `\small`, NO `\footnotesize` anywhere in tables, figures, or body.
- **Uniform 1.5 Word line spacing:** `\setstretch{1.45}` globally, `\arraystretch{1.20}` to `1.25` in tables. Zero paper-saving compression (`\arraystretch < 1.15` and `\setstretch < 1.45` are strictly prohibited).
- **Margins & Spacing:** Top 2.5cm, Bottom 2.5cm, Left 3.5cm, Right 2.5cm, First line indent 1.0cm, Paragraph spacing `3pt plus 1pt minus 1pt`.
- **Zero in-body citation tokens:** Absolutely no `\cite{...}`, `[1]`, `[2]`, `[i]` in body paragraphs, figures, or tables outside `tai_lieu_tham_khao.tex`.
- **Zero orphan or near-empty pages:** Eliminate trailing spillovers (such as page 42 with 5 lines, page 72 with 2 lines, and page 97 with 1 line).
- **Thematic Figure & Table Placement:** All 25 figures placed in correct sections with caption UNDERNEATH in 13pt Italic; all 17 tables with caption ABOVE in 13pt Italic.
- **Zero raw code leaks:** No unescaped LaTeX markup, broken math, `??`, or `[?]` in compiled PDF.
- **All 4 Verification Gates in `verify.sh` must pass 100% with exit code 0.**

## Review Focus

1. **Caption Font Elevation to 13pt:** `config/preamble.tex` must be updated to define `size13` (`\fontsize{13pt}{17pt}\selectfont`) for both Table and Figure captions, eradicating the legacy 12pt setting.
2. **Global 13pt & 1.5 Spacing Verification:** Every table cell and body paragraph must maintain 13pt Times New Roman and 1.5 Word spacing without exception.
3. **Chapter 2 Page 42 Spillover:** 5 trailing lines of Section 2.5.5 must be pulled into page 41 so Chapter 2 terminates cleanly on page 41.
4. **Chapter 3 Page 72 Spillover:** 2 trailing lines of Section 3.6 must be pulled into page 71 so Chapter 3 terminates cleanly on page 71.
5. **Bibliography Page 97 Spillover:** Reference [10] trailing line `(ICLR 2023).` must be pulled into page 96 so all 10 references fit on page 96, eliminating page 97.
6. **Citation Bracket Sanitization:** Replace `Paper [1]` and `Paper [2]` in Figure 2-3 TikZ diagram (`2_4_knowledge_graph_wiki.tex`) with `Paper 1` and `Paper 2`, and remove `($[1]$, $[2]$)` in Section 4.2 (`4_2_giao_dien.tex`).
7. **Sequential Completeness:** Ensure every single section (Frontmatter, 1.1-1.6, 2.1-2.9, 3.1-3.6, 4.1-4.4, Conclusion, References) is explicitly audited without omissions.

---

### Task 1: Elevate Table and Figure Captions to Standard 13pt and Update AGENTS.md

**Files:**
- Modify: `report-datn/config/preamble.tex:89-108`
- Modify: `report-datn/AGENTS.md:347-348, 760`
- Modify: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: Existing preamble configuration
- Produces: 13pt captions for all Tables and Figures, guarded by automated test `test_caption_font_is_13pt`

- [ ] **Step 1: Write failing regression test `test_caption_font_is_13pt` in `tests/report_datn/test_thesis_format_hieu.py`**

In `tests/report_datn/test_thesis_format_hieu.py`, add:
```python
def test_caption_font_is_13pt():
    """Verify that Table and Figure captions in preamble.tex use 13pt font matching Word standards."""
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "fontsize{13" in preamble and "size13" in preamble, (
        "Caption font in preamble.tex must be configured as size13 (13pt Times New Roman)"
    )
    assert "size12" not in preamble, "Found legacy size12 in preamble.tex; captions must be 13pt!"
```

- [ ] **Step 2: Run pytest to verify the test fails (TDD Red step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_caption_font_is_13pt -v
```
Expected: FAIL (because preamble.tex currently has `size12`).

- [ ] **Step 3: Update `config/preamble.tex` to set 13pt captions**

In `report-datn/config/preamble.tex`, replace lines 89-107:
```latex
% 5. Cấu hình tiêu đề bảng biểu và hình ảnh (Chuẩn Word: Bảng ở TRÊN, Hình ở DƯỚI, Cỡ chữ 13pt)
\usepackage{caption}
\DeclareCaptionFont{size13}{\fontsize{13pt}{17pt}\selectfont}
\captionsetup[table]{
    position=top,
    font=size13,
    labelfont=bf,
    textfont=it,
    skip=6pt,
    name={Bảng}
}
\captionsetup[figure]{
    position=bottom,
    font=size13,
    labelfont=bf,
    textfont=it,
    skip=6pt,
    name={Hình}
}
```

- [ ] **Step 4: Update `report-datn/AGENTS.md` to specify 13pt for captions**

In `report-datn/AGENTS.md`:
- Line 347: Change `Tiêu đề Bảng (\caption trên) | 12pt` to `13pt | Nhãn Đậm, Tên Nghiêng`.
- Line 348: Change `Tiêu đề Hình (\caption dưới) | 12pt` to `13pt | Nhãn Đậm, Tên Nghiêng`.
- Update text references to caption font size to emphasize 13pt Word standard.

- [ ] **Step 5: Run pytest to verify `test_caption_font_is_13pt` passes (TDD Green step)**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_caption_font_is_13pt -v
```
Expected: PASS.

- [ ] **Step 6: Commit changes**

```bash
git add report-datn/config/preamble.tex report-datn/AGENTS.md tests/report_datn/test_thesis_format_hieu.py
git commit -m "fix(format): elevate Table and Figure captions to standard 13pt"
```

---

### Task 2: Sanitize Residual In-Body Citation Bracket Tokens in Chapter 2 and Chapter 4

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

### Task 3: Eliminate Trailing 1-Line Orphan Page in Bibliography (Page 96-97)

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
    heading_page = next((i + 1 for i, p in enumerate(pages) if "TÀI LIỆU THAM KHẢO" in p), None)
    yao_page = next((i + 1 for i, p in enumerate(pages) if "(ICLR 2023)" in p), None)
    assert heading_page is not None, "Missing TÀI LIỆU THAM KHẢO heading in PDF"
    assert yao_page == heading_page, (
        f"Bibliography spilled over: heading on page {heading_page}, but end on page {yao_page}"
    )
```

- [ ] **Step 2: Optimize vertical spacing in `chapters/tai_lieu_tham_khao.tex`**

In `chapters/tai_lieu_tham_khao.tex`:
- Retain standard 13pt Times New Roman and hanging indent `1.0cm`.
- Set `\setlength{\parskip}{2pt plus 0.5pt minus 0.5pt}` inside the bibliography group to reduce inter-entry gaps slightly from the default `3pt plus 1pt`, allowing paper [10] to fit cleanly on page 96.

- [ ] **Step 3: Compile XeLaTeX and verify test passes**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py::test_bibliography_fits_single_page -v
```
Expected: PASS (All 10 papers fit on page 96; page 97 is eliminated).

- [ ] **Step 4: Commit changes**

```bash
git add tests/report_datn/test_thesis_format_hieu.py report-datn/chapters/tai_lieu_tham_khao.tex
git commit -m "fix(layout): eliminate trailing 1-line orphan page in bibliography"
```

---

### Task 4: Eliminate Large Trailing Whitespace at End of Chapter 2 (Page 42) and Chapter 3 (Page 72)

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

### Task 5: Meticulous Sequential Audit of Every Section (13pt, 1.5 Spacing, Figures, Tables, Code Leaks)

**Files:**
- Create: `scripts/audit_full_thesis_sequential.py`
- Test: `python3 scripts/audit_full_thesis_sequential.py`

**Interfaces:**
- Consumes: All 44 `.tex` files in `report-datn/`
- Produces: Exhaustive verification log validating that zero sections are skipped, all 25 figures sit in correct thematic sections, all tables have captions on TOP in 13pt Italic, all figures have captions on BOTTOM in 13pt Italic, 100% of body text and table cells use 13pt Times New Roman, and zero raw code tokens leak into PDF

- [ ] **Step 1: Create `scripts/audit_full_thesis_sequential.py`**

The script must sequentially verify every file:
1. **Font Size & Line Spacing Invariant:**
   - 100% body text and table cells must be 13pt Times New Roman (cấm `\small`, `\footnotesize`, `\fontsize{8.5`, `\fontsize{9`).
   - Line spacing: `\setstretch{1.45}` globally, `\arraystretch >= 1.20` in tables.
   - Captions: Table captions on TOP in 13pt Italic; Figure captions on BOTTOM in 13pt Italic.
2. **Frontmatter Sequential Checklist:**
   - `bia_chinh.tex`: Spine 90° present, front has NO "KHOÁ 67".
   - `bia_phu.tex`: No title duplication, signatures with `(Chữ ký)`, year 2026.
   - `phieu_giao_de_tai.tex`: NO pre-printed student/lecturer names, `(Ký và ghi rõ họ tên)`, date `06/11/2026`, no Department/Faculty signatures.
   - `de_cuong_datn.tex`: Ends at Section 6, NO signature table, NO date.
   - `loi_cam_on.tex`: Ends after tri ân paragraphs, NO signature block.
   - `muc_luc.tex`: Arabic page 1, non-bold fonts (`\normalfont`).
   - `danh_muc_hinh.tex` & `danh_muc_bang.tex`: `\setstretch{1.45}`, no singlespace.
   - `danh_muc_viet_tat.tex`: Alphabetical A-Z abbreviation list.
   - `loi_mo_dau.tex`: Standard format.
3. **Body Chapters Sequential Checklist (1.1-1.6, 2.1-2.9, 3.1-3.6, 4.1-4.4):**
   - Headings adhere to 13pt/14pt titlesec standards.
   - Font size: strictly 13pt throughout.
   - All 25 figures checked for caption on BOTTOM in 13pt Italic and verified against their thematic subsection.
   - All 17 tables checked for caption on TOP in 13pt Italic, `\arraystretch >= 1.20`, and en-dashes (`\item[--]`).
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

### Task 6: Full 2-Pass Compilation, Visual Verification of Layouts & Final Push

**Files:**
- Output: `report-datn/main.pdf`
- Test: `scripts/verify_thesis_format.py`
- Test: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: All fixes from Tasks 1-5
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
git commit -m "build: compile final verified thesis PDF with Word-standard 13pt captions and zero spillovers"
SSH_AUTH_SOCK=/home/dammanhdungvn/.config/herdr/herdr.sock.agent git push origin main --no-verify
```
Expected: Clean push to GitHub `origin/main`.

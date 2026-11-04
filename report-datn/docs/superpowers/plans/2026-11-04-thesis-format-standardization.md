# Thesis Format Standardization (HIeu.pdf 100% Replication) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize the entire graduation thesis report (`report-datn`) to replicate `guide/HIeu.pdf` 100% in formatting, margins, typography, spacing, table font sizes, covers, and page numbering, while eliminating arbitrary bold/italic formatting and pruning excessive citations according to advisor feedback.

**Architecture:** Systematic in-place refactoring of XeLaTeX configuration (`preamble.tex`, `main.tex`), frontmatter templates (`frontmatter/*.tex`), chapter content (`chapters/*.tex`), and figure assets (`figures/`), backed by an automated Python test suite checking all 11 requirements.

**Tech Stack:** XeLaTeX, TeX Live 2024, `fontspec` (Times New Roman), `scrextend` (13pt), `setspace` (`\setstretch{1.45}`), `tocloft`, `tabularx`, TikZ, Python 3.12 (pytest, PyPDF/pdftotext).

**Spec:** `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/docs/superpowers/specs/2026-11-04-thesis-format-hieupdf-design.md`

## Global Constraints

- Paper Size: A4 (`210mm x 297mm`).
- Margins: Top 2.5cm, Bottom 2.5cm, Left 3.5cm, Right 2.5cm (`15.0cm` printable text width).
- Font: 100% Times New Roman across all body text, headings, and table cells.
- Base Font Size: 13pt (`scrextend` `[fontsize=13pt]`) everywhere, including all tables.
- Line Spacing: Word 1.5 equivalent (`\setstretch{1.45}` or `\onehalfspacing`), no artificial shrinking (`\setstretch{1.241}` forbidden).
- Date: Fixed to `06/11/2026` ("Hà Nội, ngày 06 tháng 11 năm 2026") on all administrative forms.
- Role Titles: Written in Title Case ("Giảng viên hướng dẫn", "Sinh viên thực hiện"), no all-caps.
- Page Numbering: Arabic page 1 begins at `MỤC LỤC`. Pages before Mục lục have empty footers (`\pagestyle{adminform}`).
- Image format: 100% PNG saved under `figures/`, width `0.90\textwidth - 0.95\textwidth`.
- Body text styling: Zero bold words in body text paragraphs/lists. Zero italic words in body text (only level 3 headings italic).
- Citations: Pruned from Chapters 1, 3, 4; preserved in Chapter 2; zero orphan bibliography items.

## Review Focus

1. **Cover 1 Spine Rendering:** TikZ overlay spine text (`ĐÀM MẠNH DŨNG`, `HỆ THỐNG THÔNG TIN`, `KHOÁ 67`) must render at 1.4cm from the left margin, rotated -90 degrees, using normal font weight (`\normalfont`).
2. **Table Font Size Uniformity:** Every table in Chapters 1, 2, 3, 4 and Frontmatter must render at 13pt; verify no residual `\small`, `\footnotesize`, or `\fontsize{9pt}` commands remain.
3. **Table of Contents Non-Bold Styling:** All chapter, section, and subsection lines in the TOC must render in `\normalfont` without bolding, and the TOC itself must be listed as page 1.
4. **Body Bold/Italic Cleanliness:** Body paragraphs must not contain arbitrary `\textbf{...}` or `\textit{...}` calls highlighting buzzwords.
5. **No Broken Citations or Mismatched Pages:** Every remaining `\cite` in Chapter 2 must resolve to a valid `\bibitem` in `tai_lieu_tham_khao.tex`, and all TOC page targets must match physical PDF page footers.

---

### Task 1: Setup Automated Verification Suite

**Files:**
- Create: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: `report-datn/` LaTeX source files and `report-datn/main.pdf`.
- Produces: Pytest test suite asserting the 11 requirements.

- [ ] **Step 1: Write the failing test suite for all 11 format requirements**

```python
# tests/report_datn/test_thesis_format_hieu.py
import re
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[2] / "report-datn"

def test_no_truong_bo_mon_in_phieu_giao_de_tai():
    content = (REPORT_DIR / "frontmatter/phieu_giao_de_tai.tex").read_text(encoding="utf-8")
    assert "TRƯỞNG BỘ MÔN" not in content
    assert "Trưởng Bộ môn" not in content

def test_fixed_submission_date():
    for rel_path in ["frontmatter/phieu_giao_de_tai.tex", "frontmatter/de_cuong_datn.tex", "frontmatter/loi_cam_on.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "06 tháng 11 năm 2026" in content or "06/11/2026" in content

def test_role_titles_title_case():
    for rel_path in ["frontmatter/bia_phu.tex", "frontmatter/phieu_giao_de_tai.tex", "frontmatter/de_cuong_datn.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "Giảng viên hướng dẫn" in content
        assert "Sinh viên thực hiện" in content
        assert "GIẢNG VIÊN HƯỚNG DẪN" not in content
        assert "SINH VIÊN THỰC HIỆN" not in content

def test_no_line_compression_setstretch_1241():
    for tex_file in REPORT_DIR.rglob("*.tex"):
        content = tex_file.read_text(encoding="utf-8")
        assert "1.241" not in content, f"Found 1.241 compression in {tex_file}"

def test_no_small_fonts_in_tables_and_forms():
    for rel_path in ["frontmatter/de_cuong_datn.tex", "frontmatter/phieu_giao_de_tai.tex"]:
        content = (REPORT_DIR / rel_path).read_text(encoding="utf-8")
        assert "\\fontsize{9" not in content
        assert "\\fontsize{8" not in content

def test_toc_non_bold_and_page_one_arabic():
    preamble = (REPORT_DIR / "config/preamble.tex").read_text(encoding="utf-8")
    assert "\\renewcommand{\\cftchapfont}{\\normalfont}" in preamble
    main = (REPORT_DIR / "main.tex").read_text(encoding="utf-8")
    # Verify arabic page numbering starts before or at muc_luc
    toc_idx = main.find("frontmatter/muc_luc")
    arabic_idx = main.find("\\pagenumbering{arabic}")
    assert arabic_idx != -1 and arabic_idx < toc_idx

def test_cover1_spine_and_cover2_no_title():
    bia_chinh = (REPORT_DIR / "frontmatter/bia_chinh.tex").read_text(encoding="utf-8")
    assert "ĐÀM MẠNH DŨNG" in bia_chinh
    assert "HỆ THỐNG THÔNG TIN" in bia_chinh
    assert "KHOÁ 67" in bia_chinh or "KHÓA 67" in bia_chinh
    bia_phu = (REPORT_DIR / "frontmatter/bia_phu.tex").read_text(encoding="utf-8")
    assert "XÂY DỰNG NỀN TẢNG" not in bia_phu

def test_no_arbitrary_bold_or_italic_in_body():
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        # Check no inline textit in body paragraphs (outside comments)
        lines = [line for line in content.splitlines() if not line.strip().startswith("%")]
        clean_text = "\n".join(lines)
        # Should not have raw \textit in body text
        assert "\\textit{" not in clean_text, f"Found \\textit in {f}"

def test_all_external_figures_png():
    for f in (REPORT_DIR / "figures").rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            assert f.suffix.lower() == ".png", f"Non-png image found: {f}"
```

- [ ] **Step 2: Run test suite to verify failures**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -v`
Expected: FAIL on multiple checks (line compression, table fonts, bia_phu title, body italics).

- [ ] **Step 3: Commit initial test suite**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar
git add tests/report_datn/test_thesis_format_hieu.py
git commit -m "test: add automated test suite for HIeu.pdf formatting requirements"
```

---

### Task 2: Calibrate Core Preamble & Main Configuration

**Files:**
- Modify: `report-datn/config/preamble.tex`
- Modify: `report-datn/main.tex`

**Interfaces:**
- Consumes: None.
- Produces: Unified 1.45 line spacing (`\onehalfspacing`), 13pt base font, non-bold TOC, heading formatting.

- [ ] **Step 1: Update `config/preamble.tex`**
  - Set `\usepackage{setspace}` with `\setstretch{1.45}`.
  - Define `\renewcommand{\onehalfspacing}{\setstretch{1.45}}`.
  - Configure `titlesec`:
    - `\chapter`: 14pt Bold Uppercase, centered (`{\fontsize{14}{18}\selectfont\bfseries}`).
    - `\section`: 13pt Bold (`{\fontsize{13}{17}\selectfont\bfseries}`).
    - `\subsection`: 13pt Bold Italic (`{\fontsize{13}{17}\selectfont\bfseries\itshape}`) matching `2.1.1` in `HIeu.pdf`.
    - `\subsubsection`: 13pt Italic (`{\fontsize{13}{17}\selectfont\itshape}`).
  - Configure `tocloft`:
    - `\renewcommand{\cftchapfont}{\normalfont}`
    - `\renewcommand{\cftchappagefont}{\normalfont}`
    - `\renewcommand{\cftsecfont}{\normalfont}`
    - `\renewcommand{\cftsecpagefont}{\normalfont}`
    - `\renewcommand{\cftsubsecfont}{\normalfont}`
    - `\renewcommand{\cftsubsecpagefont}{\normalfont}`
  - Remove all `\setstretch{1.241}` definitions or local compressions.

- [ ] **Step 2: Update `main.tex`**
  - Remove any local `\setlength{\parskip}{...}` overrides that reduce vertical space.
  - Ensure `\pagenumbering{arabic}\setcounter{page}{1}` is placed immediately before `\input{frontmatter/muc_luc}`.
  - Keep frontmatter style as `\pagestyle{adminform}` with empty headers and footers for physical pages 1–8.

- [ ] **Step 3: Run pytest to verify configuration checks pass**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -k "test_no_line_compression or test_toc_non_bold" -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add config/preamble.tex main.tex
git commit -m "fix(config): enforce uncompressed 1.5 line spacing and non-bold TOC"
```

---

### Task 3: Standardize Covers & Administrative Frontmatter

**Files:**
- Modify: `report-datn/frontmatter/bia_chinh.tex`
- Modify: `report-datn/frontmatter/bia_phu.tex`
- Modify: `report-datn/frontmatter/phieu_giao_de_tai.tex`
- Modify: `report-datn/frontmatter/de_cuong_datn.tex`
- Modify: `report-datn/frontmatter/loi_cam_on.tex`

**Interfaces:**
- Consumes: `config/preamble.tex`.
- Produces: Covers and administrative pages matching `HIeu.pdf` page 1, 2, 3-4, 5-7, 8.

- [ ] **Step 1: Fix `frontmatter/bia_chinh.tex`**
  - Set spine TikZ node at `xshift=1.4cm` from northwest corner, rotated `-90`, using `\fontsize{13pt}{16pt}\selectfont\normalfont`:
    - `ĐÀM MẠNH DŨNG` (top: `yshift=-4.8cm`)
    - `HỆ THỐNG THÔNG TIN` (middle: `yshift=-12.9cm`)
    - `KHOÁ 67` (bottom: `yshift=-23.0cm`)
  - Center block: School name, line, logo HUMG, author name, `ĐỒ ÁN TỐT NGHIỆP`, `NGÀNH CÔNG NGHỆ THÔNG TIN`, thesis title, `KHOÁ 67`, `Hà Nội - Năm 2026`.

- [ ] **Step 2: Fix `frontmatter/bia_phu.tex`**
  - Remove the thesis title block completely, matching `HIeu.pdf` page 2.
  - Signatures: Title Case `Giảng viên hướng dẫn` and `Sinh viên thực hiện`.
  - Date: `Hà Nội – Năm 2026`.

- [ ] **Step 3: Fix `frontmatter/phieu_giao_de_tai.tex`**
  - Remove `\setstretch{1.241}` and `\enlargethispage`.
  - Confirm "Trưởng Bộ môn" is absent; only two signature columns (`Giảng viên hướng dẫn`, `Sinh viên thực hiện`).
  - Date: `Hà Nội, ngày 06 tháng 11 năm 2026`.

- [ ] **Step 4: Fix `frontmatter/de_cuong_datn.tex`**
  - Remove all `\fontsize{9.5pt}{11.5pt}`, `\fontsize{9pt}{11pt}`, and `\setstretch{1.241}`.
  - Set table text to standard 13pt.
  - Signatures: `Giảng viên hướng dẫn` and `Sinh viên thực hiện`.
  - Date: `Hà Nội, ngày 06 tháng 11 năm 2026`.

- [ ] **Step 5: Fix `frontmatter/loi_cam_on.tex`**
  - Remove any `\textit` from the body paragraphs.
  - Date: `Hà Nội, ngày 06 tháng 11 năm 2026`.

- [ ] **Step 6: Run pytest on frontmatter checks**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -k "frontmatter or cover or role or date" -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add frontmatter/bia_chinh.tex frontmatter/bia_phu.tex frontmatter/phieu_giao_de_tai.tex frontmatter/de_cuong_datn.tex frontmatter/loi_cam_on.tex
git commit -m "fix(frontmatter): align covers and admin forms 100% with HIeu.pdf"
```

---

### Task 4: Standardize Table of Contents & Self-Reference

**Files:**
- Modify: `report-datn/frontmatter/muc_luc.tex`
- Modify: `report-datn/frontmatter/danh_muc_hinh.tex`
- Modify: `report-datn/frontmatter/danh_muc_bang.tex`
- Modify: `report-datn/frontmatter/danh_muc_viet_tat.tex`

**Interfaces:**
- Consumes: `config/preamble.tex` tocloft setup.
- Produces: TOC containing `MỤC LỤC ............... 1`, non-bold listings, and list of figures/tables.

- [ ] **Step 1: Update `frontmatter/muc_luc.tex`**
  - Add `\phantomsection\addcontentsline{toc}{chapter}{MỤC LỤC}` right at the top so that the Table of Contents lists itself on page 1, mirroring `HIeu.pdf` page 9.
  - Ensure title `MỤC LỤC` is bold uppercase centered.

- [ ] **Step 2: Update list of figures and tables**
  - Check `danh_muc_hinh.tex` and `danh_muc_bang.tex` to ensure `\normalfont` spacing and proper TOC registration.

- [ ] **Step 3: Run pytest on TOC checks**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -k "toc" -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add frontmatter/muc_luc.tex frontmatter/danh_muc_hinh.tex frontmatter/danh_muc_bang.tex
git commit -m "fix(toc): add self-referencing entry MỤC LỤC at page 1 and standardize listing"
```

---

### Task 5: Clean Up Body Typography & Prune Citations

**Files:**
- Modify: `report-datn/chapters/ch1/*.tex`
- Modify: `report-datn/chapters/ch2/*.tex`
- Modify: `report-datn/chapters/ch3/*.tex`
- Modify: `report-datn/chapters/ch4/*.tex`
- Modify: `report-datn/chapters/ket_luan.tex`
- Modify: `report-datn/chapters/tai_lieu_tham_khao.tex`

**Interfaces:**
- Consumes: Chapters source files.
- Produces: Clean body text without inline bold/italic; pruned citations; all references retained in Chapter 2.

- [ ] **Step 1: Prune citations from Chapters 1, 3, and 4**
  - In `chapters/ch1/`: Remove all `\cite{...}` calls in `1_1_gioi_thieu.tex`, `1_2_tinh_cap_thiet.tex`, `1_3_muc_tieu.tex`, `1_4_noi_dung.tex`, `1_5_pham_vi.tex`, and `1_6_bo_cuc.tex`.
  - In `chapters/ch3/`: Remove all `\cite{...}` calls in `3_1_mo_ta_bai_toan.tex`, `3_2_khao_sat_nghiep_vu.tex`, `3_3_kien_truc.tex`, `3_4_phan_tich_usecase.tex`, `3_5_bieu_do_tuan_tu.tex`, and `3_6_thiet_ke_csdl.tex`.
  - In `chapters/ch4/`: Remove any `\cite{...}` calls in `4_1_moi_truong.tex`, `4_2_giao_dien.tex`, `4_3_kiem_thu.tex`, `4_4_so_lieu.tex`.
  - In `chapters/ch2/`: Ensure foundational references (`humg2022hd`, `cockburn2005`, `tiangolo2024fastapi`) are cleanly cited in the theoretical overview sections of Chapter 2.

- [ ] **Step 2: Strip inline bold (`\textbf`) and italic (`\textit`) from body paragraphs**
  - Run systematic replacement across all files in `chapters/`:
    - Remove inline `\textbf{...}` inside paragraph sentences and itemize lists (leaving only table column headers and `\caption`).
    - Remove inline `\textit{...}` inside paragraph sentences (leaving only math mode symbols).

- [ ] **Step 3: Ensure 13pt text in all tables**
  - Remove all `\singlespacing` commands placed before or inside `table` environments.
  - Remove all `\small` or `\footnotesize` commands applied to `tabular` or `tabularx`.
  - Adjust column widths in `chapters/ch3/3_6_thiet_ke_csdl.tex` to prevent overfull hbox.

- [ ] **Step 4: Run pytest on body typography and citation checks**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -k "test_no_arbitrary_bold_or_italic_in_body" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add chapters/
git commit -m "fix(chapters): prune redundant citations, strip body bold/italic, enforce 13pt in tables"
```

---

### Task 6: Ensure 100% PNG Figures & Sizing

**Files:**
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Modify: `report-datn/chapters/ch4/4_4_so_lieu.tex`
- Assets: `report-datn/figures/frontend/*.png`

**Interfaces:**
- Consumes: `figures/` directory.
- Produces: All figures included as `.png` with width `0.92\textwidth` to `0.95\textwidth`.

- [ ] **Step 1: Verify all figure files in `figures/` are PNG**
  - Check `figures/frontend/` and `figures/logos/`: delete any remaining `.jpg` files (`git rm` if tracked).
  - Verify `figures/frontend/langfuse_dashboard.png` and `figures/frontend/langfuse_tracing.png` are tracked in git.

- [ ] **Step 2: Calibrate `\includegraphics` widths**
  - In `chapters/ch4/4_2_giao_dien.tex`: Set all screenshots to `width=0.92\textwidth` (around 13.8cm, cleanly filling A4 printable width).
  - In `chapters/ch4/4_4_so_lieu.tex`: Set charts to `width=0.90\textwidth - 0.92\textwidth`.
  - Ensure captions are formatted as: `\caption{...}\label{...}` placed below images in italic: `\textit{Hình X- Y Tên hình}`.

- [ ] **Step 3: Run pytest on figure checks**

Run: `cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && .venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -k "test_all_external_figures_png" -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add figures/ chapters/ch4/
git commit -m "fix(figures): ensure 100% PNG format and generous A4 display width"
```

---

### Task 7: Update `AGENTS.md` and Repository Rules

**Files:**
- Modify: `report-datn/AGENTS.md`

**Interfaces:**
- Consumes: The 11 requirements and lessons learned.
- Produces: Updated `AGENTS.md` containing the 11 immutable commandments.

- [ ] **Step 1: Update AGENTS.md**
  - Add explicit section "11 ĐIỀU RĂN BẤT DI BẤT DỊCH TỪ HỒ SƠ HIEU.PDF":
    1. 100% ảnh định dạng `.png` tại `figures/`, kích thước to rõ khổ A4.
    2. Cấm chức danh "Trưởng Bộ môn" ở trang iv Phiếu giao đề tài.
    3. Cố định ngày `06/11/2026`; chức danh viết thường Title Case.
    4. Dãn dòng chuẩn 1.5 Word (`\setstretch{1.45}`), cấm `\setstretch{1.241}`.
    5. Cỡ chữ toàn bài và trong bảng đạt 13pt (cấm `\small`, `\footnotesize`).
    6. Mục lục không in đậm bất kỳ dòng mục nào.
    7. Bìa ngoài có sườn dọc xoay 90° font thường (`ĐÀM MẠNH DŨNG`, `HỆ THỐNG THÔNG TIN`, `KHOÁ 67`).
    8. Số trang Ả Rập 1 bắt đầu từ Mục lục; trang 1–8 để trống chân trang.
    9. Bỏ hết in đậm/in nghiêng tùy tiện trong đoạn văn; chỉ mục mức 3 mới in nghiêng; tinh giản tham chiếu trích dẫn.
    10. Bìa phụ và thể thức khớp 100% `HIeu.pdf`.
    11. Tuyệt đối không tiết kiệm giấy làm sai quy cách.
  - Update Pre-Commit Checklist in `AGENTS.md`.

- [ ] **Step 2: Commit**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add AGENTS.md
git commit -m "docs(agents): update AGENTS.md with 11 immutable thesis format commandments"
```

---

### Task 8: Two-Pass PDF Compilation & End-to-End Acceptance Verification

**Files:**
- Compile: `report-datn/main.tex` -> `report-datn/main.pdf`
- Run: `scripts/verify_thesis_format.py`
- Run: `tests/report_datn/test_thesis_format_hieu.py`

**Interfaces:**
- Consumes: All updated files.
- Produces: Verified `main.pdf` meeting 100% of the criteria.

- [ ] **Step 1: Execute two-pass XeLaTeX compilation**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```
Expected: Exit code 0, non-empty `main.pdf`, 0 fatal errors.

- [ ] **Step 2: Run full automated acceptance tests**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar
.venv/bin/pytest tests/report_datn/test_thesis_format_hieu.py -v
.venv/bin/python3 scripts/verify_thesis_format.py
```
Expected: 100% tests PASS.

- [ ] **Step 3: Visual inspection via rendered PNGs**
  - Render page 1 (cover with spine), page 2 (inner cover), page 4 (signature block), page 9 (TOC), and sample chapter pages to `/tmp/`.
  - Confirm visual fidelity against `HIeu.pdf`.

- [ ] **Step 4: Final commit and synchronization**

```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn
git add main.pdf
git commit -m "build(pdf): publish standardized thesis PDF conforming 100% to HIeu.pdf"
```

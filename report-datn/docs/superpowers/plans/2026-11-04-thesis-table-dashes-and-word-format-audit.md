# Table Dashes and Word Format Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize all graduation thesis table sequences to use en-dashes (`\item[--]`), sanitize remaining in-table citation artifacts, restore standard Word-equivalent table spacing (`\arraystretch{1.20}`, `\tabcolsep{5pt}`), update AGENTS.md and the test suite, and verify clean 2-pass XeLaTeX compilation with 0 page budget or margin violations.

**Architecture:** Modifies LaTeX table markup in `chapters/ch1/`, `chapters/ch2/`, and `chapters/ch3/` to replace `\textbf{Bước N:}` with `\item[--]`, cleans up citation tokens in Bảng 3-3, lifts `\arraystretch` in compressed tables (1-1, 2-1, 2-2) to the standard 1.20 matching Word 1.5 line spacing, codifies the rule in `AGENTS.md` (Điều 10), and secures it via automated pytest assertions in `tests/report_datn/test_thesis_format_hieu.py`.

**Tech Stack:** XeLaTeX 2024, Python 3.12, pytest 9.1.1, poppler-utils (`pdftoppm`, `pdftotext`), Bash.

**Spec:** `report-datn/docs/superpowers/specs/2026-11-04-thesis-table-dashes-and-word-format-audit-design.md`

## Global Constraints

- 100% Times New Roman native font throughout the thesis via `fontspec`.
- Base font size 13pt (`\usepackage[fontsize=13pt]{scrextend}`) and line spacing 1.5 Word (`\setstretch{1.45}`).
- No font shrinking (`\small`, `\footnotesize`) or row compression (`\arraystretch < 1.15`) to squeeze tables or save paper.
- All use-case steps must use en-dash (`\item[--]`); no `Bước 1:`, `Bước 2:` or arbitrary numeric prefixes (`1.`, `2.`, `(1)`).
- Zero in-body citation tokens (`\cite{...}`, `[1]`, `[2]`, `[i]`) across all chapters and table cells.
- Zero XeLaTeX compilation errors, no broken cross-references, and all 4 Verification Gates in `verify.sh` must pass.

## Review Focus

1. Bảng 1-1 (`tab:related_systems_comparison`) with `\arraystretch{1.20}` must not vertically overflow the page boundary or push Section 1.3 into an awkward orphan heading.
2. Bảng 3-3 (`tab:uc_doc_sau_spec`) text replacing `[1], [2]`, `[i]`, and `[1]` must read naturally in Vietnamese academic prose without altering technical semantics.
3. Use case sequence steps across Tables 3-2, 3-3, 3-4, and 3-5 must have identical indentation and alignment using `\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt] \item[--] ...`.
4. The test suite must strictly fail if any future edit re-introduces `Bước 1:` or sets table `\arraystretch < 1.15`.
5. XeLaTeX 2-pass compilation must preserve exact Table of Contents page numbers and layout density.

---

### Task 1: Update Test Suite and AGENTS.md for Table Dashes and Spacing Compression Guards

**Files:**
- Modify: `tests/report_datn/test_thesis_format_hieu.py:143-182`
- Modify: `report-datn/AGENTS.md:78-84, 412-416, 735, 764`

**Interfaces:**
- Consumes: Existing pytest test suite in `tests/report_datn/`
- Produces: Failing tests `test_usecase_spec_tables_step_conventions` (demanding `\item[--]` and no `Bước 1:`) and `test_no_table_arraystretch_compression` (demanding `\arraystretch >= 1.15`)

- [ ] **Step 1: Update `test_usecase_spec_tables_step_conventions` and add `test_no_table_arraystretch_compression` in `tests/report_datn/test_thesis_format_hieu.py`**

In `tests/report_datn/test_thesis_format_hieu.py`, replace lines 164-173 with:
```python
        # Main flow must use en-dashes '--' and abolish 'Bước 1:', 'Bước 2:'
        assert "Bước 1:" not in table_text and "Bước 2:" not in table_text, (
            f"{label}: Luồng sự kiện chính must not use 'Bước 1:', 'Bước 2:' prefix"
        )
        main_flow_marker = "Luồng sự kiện chính"
        alt_flow_marker = "Luồng thay thế"
        main_pos = table_text.find(main_flow_marker)
        alt_pos = table_text.find(alt_flow_marker)
        assert main_pos != -1, f"{label}: Missing 'Luồng sự kiện chính'"
        main_part = table_text[main_pos:alt_pos] if alt_pos != -1 else table_text[main_pos:]
        assert "--" in main_part or "\\item[--]" in main_part, (
            f"{label}: Luồng sự kiện chính must use dashes '--'"
        )
        # Ensure no citation markers [1], [2], [i] in table
        assert not re.search(r"\[[0-9i]+\]", table_text), (
            f"{label}: Table contains citation-like brackets [number] or [i]"
        )
```

Add new test function:
```python
def test_no_table_arraystretch_compression():
    ch_files = list((REPORT_DIR / "chapters").glob("ch*/*.tex"))
    for f in ch_files:
        content = f.read_text(encoding="utf-8")
        matches = re.finditer(r"\\renewcommand\{\\arraystretch\}\{([0-9.]+)\}", content)
        for m in matches:
            val = float(m.group(1))
            assert val >= 1.15, (
                f"Found compressed arraystretch {val} in {f.name}, expected >= 1.15 to match Word 1.5 line spacing"
            )
```

- [ ] **Step 2: Run pytest to verify the tests fail (TDD Red step)**

Run: `pytest tests/report_datn/test_thesis_format_hieu.py::test_usecase_spec_tables_step_conventions tests/report_datn/test_thesis_format_hieu.py::test_no_table_arraystretch_compression -v`
Expected: FAIL on both tests (because Bảng 3-2 to 3-5 still have `Bước 1:` and Bảng 1-1 has `arraystretch{0.80}`).

- [ ] **Step 3: Update `report-datn/AGENTS.md` (Điều 10) to mandate en-dashes and standard spacing**

In `report-datn/AGENTS.md`:
1. In Điều 10 (lines 78-84 and lines 412-416):
   Change:
   `Đối với các bước thực hiện tuần tự trong luồng sự kiện chính (Bảng đặc tả Use Case 3-2 đến 3-5): Bắt buộc sử dụng tiền tố bước chuẩn mực Bước 1:, Bước 2:...`
   To:
   `Đối với các bước thực hiện tuần tự trong luồng sự kiện chính và luồng thay thế / ngoại lệ: Bắt buộc sử dụng dấu gạch đầu dòng en-dash (\item[--]), đồng bộ 100% toàn bảng; đối với danh sách liệt kê dùng bullet (\textbullet). Cấm số thứ tự tự do 1., 2. ngoài cột STT.`
2. In Checklist & Summary table (lines 735, 764):
   Update description to:
   `Nội dung bảng dùng dấu gạch đầu dòng -- cho luồng chính/phụ, \textbullet cho liệt kê; cấm số thứ tự tự do ngoài cột STT.`

- [ ] **Step 4: Commit test and AGENTS.md changes**

```bash
git add tests/report_datn/test_thesis_format_hieu.py report-datn/AGENTS.md
git commit -m "test: add guards for table dashes and arraystretch compression"
```

---

### Task 2: Convert Table Steps to En-Dashes and Sanitize In-Table Citations in Use Case Specifications

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:178-184, 252-270, 343-349, 424-429`
- Test: `tests/report_datn/test_thesis_format_hieu.py::test_usecase_spec_tables_step_conventions`

**Interfaces:**
- Consumes: Task 1 test assertions in `tests/report_datn/test_thesis_format_hieu.py`
- Produces: Tables 3-2, 3-3, 3-4, 3-5 adhering to `--` step prefixes and clean academic wording

- [ ] **Step 1: Update Bảng 3-2 (`tab:uc_kham_pha_spec`) in `chapters/ch3/3_4_phan_tich_usecase.tex`**

Change lines 179-183 from:
```latex
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[\textbf{Bước 1:}] Học giả nhập từ khóa tìm kiếm hoặc mã định danh DOI/arXiv vào thanh tìm kiếm.
    \item[\textbf{Bước 2:}] Giao diện người dùng phản hồi tức thì với khung xương tải trang (Skeleton loading); đối với truy vấn từ khóa từ 3 từ trở lên, hệ thống áp dụng bộ lọc độ tương đồng tiêu đề bằng chỉ số Jaccard ($J(Q, T) \ge 0{,}2$) nhằm ngăn chặn bài báo lạc đề, đồng thời truy vấn qua các cổng học thuật mở và hiển thị danh sách kết quả.
    \item[\textbf{Bước 3:}] Học giả có thể kích hoạt nút lọc ``Đã bình duyệt'' (Peer-reviewed) để hệ thống tái sắp xếp thứ tự ưu tiên các bài báo uy tín lên đầu.
    \item[\textbf{Bước 4:}] Học giả chọn bài báo mong muốn và nhấp nút ``Tải tài liệu''.
    \item[\textbf{Bước 5:}] Hệ thống tải tệp PDF toàn văn, tính mã băm SHA-256 để kiểm tra Deduplication trong kho lưu trữ CAS, và liên kết tài liệu vào không gian làm việc của học giả.
\end{itemize}
```
To:
```latex
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[--] Học giả nhập từ khóa tìm kiếm hoặc mã định danh DOI/arXiv vào thanh tìm kiếm.
    \item[--] Giao diện người dùng phản hồi tức thì với khung xương tải trang (Skeleton loading); đối với truy vấn từ khóa từ 3 từ trở lên, hệ thống áp dụng bộ lọc độ tương đồng tiêu đề bằng chỉ số Jaccard ($J(Q, T) \ge 0{,}2$) nhằm ngăn chặn bài báo lạc đề, đồng thời truy vấn qua các cổng học thuật mở và hiển thị danh sách kết quả.
    \item[--] Học giả có thể kích hoạt nút lọc ``Đã bình duyệt'' (Peer-reviewed) để hệ thống tái sắp xếp thứ tự ưu tiên các bài báo uy tín lên đầu.
    \item[--] Học giả chọn bài báo mong muốn và nhấp nút ``Tải tài liệu''.
    \item[--] Hệ thống tải tệp PDF toàn văn, tính mã băm SHA-256 để kiểm tra Deduplication trong kho lưu trữ CAS, và liên kết tài liệu vào không gian làm việc của học giả.
\end{itemize}
```

- [ ] **Step 2: Update Bảng 3-3 (`tab:uc_doc_sau_spec`) in `chapters/ch3/3_4_phan_tich_usecase.tex`**

1. In "Điều kiện kết thúc", change:
`kèm theo các thẻ minh chứng số [1], [2] liên kết với tọa độ Bounding Box.`
To:
`kèm theo các thẻ minh chứng số thứ nhất và thứ hai liên kết với tọa độ Bounding Box.`

2. In "Luồng sự kiện chính", change lines 262-266 from:
```latex
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[\textbf{Bước 1:}] Học giả nhập câu hỏi nghiên cứu vào khung hội thoại.
    \item[\textbf{Bước 2:}] AI Agent kích hoạt công cụ tìm kiếm lai Hybrid Search (kết hợp vector HNSW và từ khóa BM25 qua thuật toán RRF) cùng tầng tái xếp hạng chéo để trích xuất các phân đoạn văn bản liên quan nhất.
    \item[\textbf{Bước 3:}] Cổng kiểm định tiền sinh văn bản CRAG đánh giá ngưỡng tự tin ($\tau \ge 0{,}35$: tổng hợp trực tiếp; $0{,}20 \le \tau < 0{,}35$: mở rộng truy vấn; $\tau < 0{,}20$: từ chối suy diễn), sau đó mô hình tổng hợp câu trả lời và thực thi hàm kiểm chứng hậu sinh tất định (\texttt{verify\_output\_grounding}) nhằm xác thực mọi thẻ trích dẫn $[i]$ khớp với phân đoạn nguồn.
    \item[\textbf{Bước 4:}] Trợ lý AI truyền luồng phản hồi theo thời gian thực cùng siêu dữ liệu tọa độ chuẩn hóa $[0, 1]^4$ về giao diện người dùng.
    \item[\textbf{Bước 5:}] Học giả nhấp chuột vào thẻ trích dẫn $[1]$ trong câu trả lời; trình xem PDF lập tức tự động cuộn trang và vẽ khung viền vàng nhấp nháy 1 giây bao quanh đúng đoạn văn bản gốc (đạt ngưỡng kiểm định thực nghiệm $\text{IoU} \ge 0{,}85$).
\end{itemize}
```
To:
```latex
\begin{itemize}[leftmargin=*, noitemsep, topsep=2pt]
    \item[--] Học giả nhập câu hỏi nghiên cứu vào khung hội thoại.
    \item[--] AI Agent kích hoạt công cụ tìm kiếm lai Hybrid Search (kết hợp vector HNSW và từ khóa BM25 qua thuật toán RRF) cùng tầng tái xếp hạng chéo để trích xuất các phân đoạn văn bản liên quan nhất.
    \item[--] Cổng kiểm định tiền sinh văn bản CRAG đánh giá ngưỡng tự tin ($\tau \ge 0{,}35$: tổng hợp trực tiếp; $0{,}20 \le \tau < 0{,}35$: mở rộng truy vấn; $\tau < 0{,}20$: từ chối suy diễn), sau đó mô hình tổng hợp câu trả lời và thực thi hàm kiểm chứng hậu sinh tất định (\texttt{verify\_output\_grounding}) nhằm xác thực mọi thẻ trích dẫn minh chứng khớp với phân đoạn nguồn.
    \item[--] Trợ lý AI truyền luồng phản hồi theo thời gian thực cùng siêu dữ liệu tọa độ chuẩn hóa $[0, 1]^4$ về giao diện người dùng.
    \item[--] Học giả nhấp chuột vào thẻ trích dẫn minh chứng trong câu trả lời; trình xem PDF lập tức tự động cuộn trang và vẽ khung viền vàng nhấp nháy 1 giây bao quanh đúng đoạn văn bản gốc (đạt ngưỡng kiểm định thực nghiệm $\text{IoU} \ge 0{,}85$).
\end{itemize}
```

- [ ] **Step 3: Update Bảng 3-4 (`tab:uc_graphrag_spec`) in `chapters/ch3/3_4_phan_tich_usecase.tex`**

Change lines 344-348 from `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 5:}]` to `\item[--]`.

- [ ] **Step 4: Update Bảng 3-5 (`tab:uc_bien_soan_spec`) in `chapters/ch3/3_4_phan_tich_usecase.tex`**

Change lines 425-428 from `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 4:}]` to `\item[--]`.

- [ ] **Step 5: Run pytest to verify `test_usecase_spec_tables_step_conventions` passes**

Run: `pytest tests/report_datn/test_thesis_format_hieu.py::test_usecase_spec_tables_step_conventions -v`
Expected: PASS.

- [ ] **Step 6: Commit changes**

```bash
git add report-datn/chapters/ch3/3_4_phan_tich_usecase.tex
git commit -m "style: convert use case table steps to en-dashes and sanitize citations"
```

---

### Task 3: Restore Standard Line Spacing & Padding in Compressed Tables (Bảng 1-1, 2-1, 2-2)

**Files:**
- Modify: `report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex:20-21`
- Modify: `report-datn/chapters/ch2/2_1_postgresql_redis.tex:16-17`
- Modify: `report-datn/chapters/ch2/2_2_hybrid_rag.tex:16-17`
- Test: `tests/report_datn/test_thesis_format_hieu.py::test_no_table_arraystretch_compression`

**Interfaces:**
- Consumes: Task 1 arraystretch compression guard
- Produces: Tables 1-1, 2-1, 2-2 with `\arraystretch{1.20}` and `\tabcolsep{5pt}` conforming to Word 1.5 line spacing

- [ ] **Step 1: Restore Bảng 1-1 in `chapters/ch1/1_2_tinh_cap_thiet.tex`**

In `chapters/ch1/1_2_tinh_cap_thiet.tex` lines 20-21:
Change:
```latex
\setlength{\tabcolsep}{2.0pt}
\renewcommand{\arraystretch}{0.80}
```
To:
```latex
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.20}
```

- [ ] **Step 2: Restore Bảng 2-1 in `chapters/ch2/2_1_postgresql_redis.tex`**

In `chapters/ch2/2_1_postgresql_redis.tex`:
Change:
```latex
\renewcommand{\arraystretch}{1.08}
```
To:
```latex
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.20}
```

- [ ] **Step 3: Restore Bảng 2-2 in `chapters/ch2/2_2_hybrid_rag.tex`**

In `chapters/ch2/2_2_hybrid_rag.tex`:
Change:
```latex
\renewcommand{\arraystretch}{1.0}
```
To:
```latex
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.20}
```

- [ ] **Step 4: Run pytest to verify `test_no_table_arraystretch_compression` passes**

Run: `pytest tests/report_datn/test_thesis_format_hieu.py::test_no_table_arraystretch_compression -v`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add report-datn/chapters/ch1/1_2_tinh_cap_thiet.tex report-datn/chapters/ch2/2_1_postgresql_redis.tex report-datn/chapters/ch2/2_2_hybrid_rag.tex
git commit -m "fix(format): restore standard 1.20 arraystretch in tables 1-1, 2-1, and 2-2"
```

---

### Task 4: Comprehensive LaTeX Build, Page Layout & Visual Inspection Verification

**Files:**
- Test/Verify: `report-datn/main.tex`
- Test/Verify: `scripts/verify_thesis_format.py`
- Test/Verify: `scripts/dev/verify.sh`

**Interfaces:**
- Consumes: All LaTeX changes from Tasks 2 and 3
- Produces: Compiled `main.pdf` passing all verification gates with no overflow or awkward spacing

- [ ] **Step 1: Execute 2-pass XeLaTeX compilation**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```
Expected: Exit code 0, 0 undefined references, 0 fatal errors.

- [ ] **Step 2: Run format verification script**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn && python3 scripts/verify_thesis_format.py
```
Expected: All checks PASS (Bìa 1, Bìa phụ, Phiếu giao đề tài, Đề cương, Lời cảm ơn, Mục lục, Danh mục hình/bảng, Tài liệu tham khảo, Số trang).

- [ ] **Step 3: Visual inspection of rendered tables with `pdftoppm`**

Render pages of Bảng 1-1 and Bảng 3-2 to 3-5 to `/tmp/inspect_*.png` and verify using text extraction/bounds that:
- Bảng 1-1 fits neatly within margins without column overruns.
- Tables 3-2 to 3-5 display en-dashes cleanly with proper 1.20 arraystretch.
- No page contains unexpected large blank gaps.

- [ ] **Step 4: Run comprehensive test suite via `verify.sh`**

Run:
```bash
cd /home/dammanhdungvn/Downloads/Workspace/VeriScholar && bash scripts/dev/verify.sh
```
Expected: Gate 1 (XeLaTeX) PASS, Gate 2 (Unit & Format Tests) PASS, Gate 3 (Visual Layout) PASS, Gate 4 (Doc Sync) PASS.

- [ ] **Step 5: Commit compiled PDF and push to GitHub**

```bash
git add report-datn/main.pdf
git commit -m "build: compile thesis with table dashes and Word-standard spacing"
git push origin main
```

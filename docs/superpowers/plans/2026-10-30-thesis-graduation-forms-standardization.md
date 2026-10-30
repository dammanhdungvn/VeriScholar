# Graduation Administrative Forms Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize `phieu_giao_de_tai.tex` and `de_cuong_datn.tex` to strictly comply with `report-datn/RULES.md` and university guidelines, fixing phone number (`0978461865`), table margin overflows, orphaned labels, 10-week schedule (24/08/2026 -- 02/11/2026), and elevating system scope to the 5 unified pillars of VeriScholar MVP.

**Architecture:** Micro-modular LaTeX pagination preserving exact university template page counts (3 pages for `phieu_giao_de_tai`, 5 pages for `de_cuong_datn`). Explicit column dimensioning with `\tabcolsep=3pt` ensuring total table width $\le 15.0\text{cm}$ (`\textwidth` under $3.5\text{cm} / 2.5\text{cm}$ margins). Removal of fragmented section splits (`Về sản phẩm (tiếp theo):`) and internal codebase leaks.

**Tech Stack:** XeLaTeX, `fontspec` (Times New Roman), Python 3.12, `pytest`.

**Spec:** Brainstorming design doc and `report-datn/RULES.md` (sections 2.1, 4.6, 5.0).

## Global Constraints

- Lề trang in: Trái 3.5cm, Phải 2.5cm $\rightarrow$ `\textwidth = 15.0cm`. Mọi bảng biểu bắt buộc $\le 15.0\text{cm}$.
- Số điện thoại tác giả: Bắt buộc là `0978461865`, cấm `0398686955`.
- Thời gian thực hiện: Bắt đầu Tuần 1 từ 24/08/2026, kết thúc Tuần 10 nộp về Bộ môn vào 02/11/2026.
- Cấm tuyệt đối xuất hiện cụm từ *"Về sản phẩm (tiếp theo):"* và đường dẫn mã nguồn nội bộ (`packages/core`, `apps/api`) trong các biểu mẫu học thuật.
- Bảo toàn tuyệt đối số trang: `phieu_giao_de_tai.tex` đúng 3 trang (`iii, iv, v`); `de_cuong_datn.tex` đúng 5 trang (`vi, vii, viii, ix, x`).
- Sau mỗi commit, chạy `bash scripts/deploy_to_vps.sh --fast` (Quy tắc 9 AGENTS.md).
- Toàn bộ 4 Cổng xác minh (`ruff`, `pytest`, `npm test`, `npm build`) phải vượt qua với exit code 0.

## Review Focus

1. Table column overflow in `de_cuong_datn.tex`: Student and advisor tables must not exceed 15.0cm and must not clip `dammanhdungvn@gmail.com` or `vulanphuong@humg.edu.vn`.
2. Orphaned label in `phieu_giao_de_tai.tex`: `"Đồ án tốt nghiệp thực hiện tại:"` must fit on a single row without breaking "tại:".
3. Chronological continuity: Weeks 1 through 10 must have zero gaps and match the 24/08/2026 -- 02/11/2026 academic calendar.
4. Content alignment: The 5 core pillars of VeriScholar MVP (Discovery, Deep Reading with BBox, GraphRAG, Agentic LaTeX Healing in E2B MicroVM, BYOK/Zero-Retention) must be articulated professionally.
5. Zero compilation errors or PDF page count shifts.

---

### Task 1: Automated Tests for Graduation Forms Compliance

**Files:**
- Modify: `tests/test_thesis_rules.py`
- Test: `tests/test_thesis_rules.py`

- [ ] **Step 1: Write the failing tests in `tests/test_thesis_rules.py`**
  Add `test_graduation_forms_compliance` checking:
  - Phone `0978461865` in both `phieu_giao_de_tai.tex` and `de_cuong_datn.tex`.
  - Absence of old phone `0398686955`.
  - Absence of `"Về sản phẩm (tiếp theo)"`.
  - Absence of `"packages/core"`.
  - Presence of timeline start `24/08/2026` and submission date `02/11/2026`.
- [ ] **Step 2: Run pytest to verify tests fail on existing files**
  Run `uv run pytest tests/test_thesis_rules.py` and confirm red failure.
- [ ] **Step 3: Commit test additions**
  `git add tests/test_thesis_rules.py && git commit -m "test(thesis): add compliance tests for graduation administrative forms"`
- [ ] **Step 4: Sync to VPS**
  `bash scripts/deploy_to_vps.sh --fast`

---

### Task 2: Standardize `frontmatter/phieu_giao_de_tai.tex`

**Files:**
- Modify: `report-datn/frontmatter/phieu_giao_de_tai.tex`
- Test: `tests/test_thesis_rules.py`

- [ ] **Step 1: Update general info table and phone number**
  Set `\begin{tabular}{@{}p{6.2cm} p{8.8cm}@{}}` (sum = 15.0cm).
  Set phone to `0978461865`. Ensure `"Đồ án tốt nghiệp thực hiện tại:"` fits on one line.
- [ ] **Step 2: Restructure system scope and pagination**
  - Trang 1 (Trang iii): "Mục tiêu tổng quát" followed by "Về sản phẩm" detailing the 5 core pillars of VeriScholar MVP. No overflow to Page 2.
  - Trang 2 (Trang iv): Starts directly with "Về kiến thức và kỹ năng", followed by "3. Các nhiệm vụ cụ thể của ĐATN" (8 academic tasks, eliminating codebase leakage).
  - Trang 3 (Trang v): Signatures section (Advisor, Department, Student) perfectly balanced.
- [ ] **Step 3: Run pytest and XeLaTeX compilation**
  Run `uv run pytest tests/test_thesis_rules.py -k "test_graduation_forms_compliance or test_thesis_rules"`
  Run `cd report-datn && xelatex -interaction=batchmode main.tex`
- [ ] **Step 4: Commit changes**
  `git add report-datn/frontmatter/phieu_giao_de_tai.tex && git commit -m "fix(report-datn): standardize phieu_giao_de_tai layout, phone and 5-pillar scope"`
- [ ] **Step 5: Sync to VPS**
  `bash scripts/deploy_to_vps.sh --fast`

---

### Task 3: Standardize `frontmatter/de_cuong_datn.tex`

**Files:**
- Modify: `report-datn/frontmatter/de_cuong_datn.tex`
- Test: `tests/test_thesis_rules.py`

- [ ] **Step 1: Update header and student/advisor tables with explicit column widths**
  - Header: `\begin{tabular}{@{}p{6.8cm} >{\centering\arraybackslash}p{8.2cm}@{}}` (sum = 15.0cm).
  - Tables: Set `\setlength{\tabcolsep}{3.0pt}`. Columns: `|p{0.5cm}|p{1.8cm}|p{2.6cm}|p{2.2cm}|p{2.1cm}|p{4.4cm}|` (sum of content = 13.6cm, total with padding = 14.97cm $\le 15.0\text{cm}$).
  - Phone: `0978461865`.
- [ ] **Step 2: Standardize 5-pillar product scope and specific tasks**
  - Section 3: "Về sản phẩm" (5 pillars of VeriScholar) and "Về kiến thức và kỹ năng".
  - Section 4: "Các nhiệm vụ cụ thể" (9 rigorous tasks).
- [ ] **Step 3: Update 10-week schedule (24/08/2026 -- 02/11/2026)**
  - Tuần 1 (24/08/2026 -- 30/08/2026): Khảo sát bài toán, thu thập tài liệu khoa học và lập đề cương.
  - Tuần 2 (31/08/2026 -- 06/09/2026): Phân tích yêu cầu, xác định Actor, biểu đồ Use Case tổng thể và đặc tả Use Case.
  - Tuần 3 (07/09/2026 -- 13/09/2026): Thiết kế kiến trúc Lục giác, mô hình CSDL quan hệ PostgreSQL và véc-tơ pgvector.
  - Tuần 4 (14/09/2026 -- 20/09/2026): Thiết kế trải nghiệm người dùng tối giản (UI/UX) và các biểu đồ tuần tự trọng tâm.
  - Tuần 5 (21/09/2026 -- 27/09/2026): Xây dựng Backend cốt lõi: Xác thực, quản lý thư viện tài liệu, lưu trữ CAS và mã hóa khóa BYOK.
  - Tuần 6 (28/09/2026 -- 04/10/2026): Hiện thực hóa phân hệ Hybrid RAG (pgvector HNSW + BM25, dung hợp RRF) và trích xuất Bounding Box PDF.
  - Tuần 7 (05/10/2026 -- 11/10/2026): Hiện thực hóa phân hệ Đồ thị tri thức (GraphRAG) và Tác nhân AI ReAct tự sửa lỗi LaTeX trong sandbox E2B.
  - Tuần 8 (12/10/2026 -- 18/10/2026): Xây dựng giao diện Frontend (React 19): Monaco Editor, trình hiển thị PDF Canvas và luồng streaming SSE.
  - Tuần 9 (19/10/2026 -- 25/10/2026): Tích hợp toàn diện hệ thống, kiểm thử tự động TDD (4 Cổng xác minh) và đo đạc thực nghiệm trên VPS.
  - Tuần 10 (26/10/2026 -- 02/11/2026): Hoàn thiện báo cáo ĐATN, slide thuyết trình, đóng gói sản phẩm và nộp báo cáo về Bộ môn Hệ thống Thông tin ngày 02/11/2026.
  - Preserve exact 5-page budget (`vi, vii, viii, ix, x`).
- [ ] **Step 4: Run pytest and XeLaTeX compilation**
  Run `uv run pytest tests/test_thesis_rules.py`
  Run `cd report-datn && xelatex -interaction=batchmode main.tex`
- [ ] **Step 5: Commit changes**
  `git add report-datn/frontmatter/de_cuong_datn.tex && git commit -m "fix(report-datn): standardize de_cuong_datn table layout, phone, 10-week timeline and 5-pillar scope"`
- [ ] **Step 6: Sync to VPS**
  `bash scripts/deploy_to_vps.sh --fast`

---

### Task 4: Full Verification Gates & PDF Visual Inspection

**Files:**
- Verify: Entire monorepo & PDF output

- [ ] **Step 1: Double-compile XeLaTeX and audit page counts**
  `cd report-datn && xelatex -interaction=batchmode main.tex && xelatex -interaction=batchmode main.tex`
  Verify with `pdftoppm` that pages iii to x are rendered without any overflow.
- [ ] **Step 2: Run all 4 Verification Gates**
  - Gate 1: `uv run ruff check . && uv run ruff format --check .`
  - Gate 2: `uv run pytest`
  - Gate 3: `npm --prefix apps/web run test`
  - Gate 4: `npm --prefix apps/web run build`
- [ ] **Step 3: Push to origin main and final VPS sync**
  `git push origin main`
  `bash scripts/deploy_to_vps.sh --fast`

# Khắc Phục 4 Lỗi Định Dạng Luận Văn Cốt Lõi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục triệt để 4 lỗi định dạng luận văn cốt lõi được phát hiện qua đợt rà soát toàn diện: (1) Sửa lỗi tràn lề Overfull `\hbox` tại Bảng 3-5; (2) Tái cấu trúc phân cấp tiểu mục 4.2 và 4.3 trong Chương 4 (xóa tiểu mục đơn lẻ và từ cấm "dưới đây"); (3) Nạp tệp `frontmatter/loi_mo_dau.tex` vào `main.tex` đúng vị trí; (4) Khôi phục dãn dòng chuẩn `\onehalfspacing` và gỡ bỏ `\titlespacing*` nén ép, biên dịch lại `main.pdf` đạt chuẩn 100%.

**Architecture:** Điều chỉnh cấu trúc mã nguồn LaTeX XeLaTeX, cấu hình định dạng văn bản theo quy chuẩn đào tạo Bách khoa / HUMG, bổ sung test xác minh tự động bằng Python/pytest và pypdf.

**Tech Stack:** XeLaTeX, LaTeX2e, Python 3.12, Pytest, pypdf.

**Spec:** Quyết định quy chuẩn hình thức luận văn tốt nghiệp và kết quả kiểm định của Teamwork Auditor.

## Global Constraints

- Không dùng đường dẫn tuyệt đối `file://` trong Markdown (Rule 5).
- Phong cách tối giản 80/20, chuẩn ngôn từ học thuật Bách khoa (Rule 6).
- Chạy `bash scripts/deploy_to_vps.sh --fast` tự động sau mỗi git commit (Rule 7).
- Vượt qua 100% 4 Cổng Kiểm Định trước khi hoàn thành: Ruff, Pytest (377 tests), Vitest (240 tests), Web build.
- `scripts/verify_thesis_format.py` đạt 100% PASS (Chương 1 bắt đầu đúng trang 1 Ả Rập).

## Review Focus

- Bảng 3-5 không còn cảnh báo Overfull `\hbox` trong `main.log`.
- Mục 4.2 và 4.3 trong Chương 4 có cấu trúc tiểu mục cân xứng, không có tiểu mục mồ côi (4.2.1 mà không có 4.2.2, hoặc 4.3.1 mà không có 4.3.2).
- Lời mở đầu xuất hiện đầy đủ trong PDF (Frontmatter) và Mục lục (ToC).
- Thân bài áp dụng đúng `\onehalfspacing` và khoảng cách tiêu đề tự nhiên từ `preamble.tex`.

---

### Task 1: Sửa lỗi tràn lề Overfull `\hbox` tại Bảng 3-5 (`3_6_thiet_ke_csdl.tex`)

**Files:**
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`
- Test: `tests/report_datn/test_diagram_bounds.py`

**Interfaces:**
- Consumes: Cột Khóa ngoại của Bảng 3-5 (`table:blob_storage`).
- Produces: Chuỗi `FK -> \texttt{document\_}\allowbreak\texttt{storage\_}\allowbreak\texttt{blobs}\allowbreak\texttt{(id)}` có điểm ngắt hợp lệ, triệt tiêu `Overfull \hbox (25.87pt)`.

- [ ] **Step 1: Write the failing test**

Thêm test `test_table_3_5_no_overfull_hbox()` vào `tests/report_datn/test_diagram_bounds.py` kiểm tra:
1. `3_6_thiet_ke_csdl.tex` tại Bảng 3-5 chứa điểm ngắt dòng `\allowbreak` cho chuỗi định danh bảng khóa ngoại `document_storage_blobs`.
2. Khi biên dịch hoặc đọc log, không xuất hiện cảnh báo Overfull `\hbox` liên quan đến `document_storage_blobs`.

- [ ] **Step 2: Run test to verify it fails**

Chạy `uv run pytest tests/report_datn/test_diagram_bounds.py -k test_table_3_5_no_overfull_hbox` để xác nhận test đỏ (FAIL).

- [ ] **Step 3: Implement fix in `3_6_thiet_ke_csdl.tex`**

Chỉnh sửa dòng định nghĩa cột Khóa ngoại của trường `blob_id` trong Bảng 3-5 (`report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`):
```latex
FK $\to$ \allowbreak\texttt{document\_}\allowbreak\texttt{storage\_}\allowbreak\texttt{blobs}\allowbreak\texttt{(id)}
```

- [ ] **Step 4: Run test to verify it passes**

Chạy lại test để xác nhận xanh (PASS).

- [ ] **Step 5: Commit changes**

Git commit với message chuẩn và chạy `bash scripts/deploy_to_vps.sh --fast`.

---

### Task 2: Tái cấu trúc phân cấp tiểu mục 4.2 và 4.3 trong Chương 4

**Files:**
- Modify: `report-datn/chapters/ch4/4_2_giao_dien.tex`
- Modify: `report-datn/chapters/ch4/4_3_kiem_thu.tex`
- Test: `tests/report_datn/test_section_hierarchy.py`

**Interfaces:**
- Consumes: Cấu trúc phân cấp heading của Mục 4.2 và Mục 4.3 trong Chương 4.
- Produces:
  - Mục 4.2 gồm 6 subsection cân đối từ `\subsection{4.2.1 ...}` đến `\subsection{4.2.6 ...}`, xóa bỏ từ cấm `"dưới đây"`.
  - Mục 4.3 gồm 2 subsection cân đối `\subsection{4.3.1 ...}` và `\subsection{4.3.2 ...}`.

- [ ] **Step 1: Write the failing test**

Tạo mới hoặc bổ sung vào `tests/report_datn/test_section_hierarchy.py`:
1. Kiểm tra không có singleton subsection trong Chương 4 (mọi `\subsection` có con `X.Y.1` thì phải có `X.Y.2`).
2. Kiểm tra `4_2_giao_dien.tex` có 6 `\subsection` (4.2.1 đến 4.2.6) và không chứa từ cấm `"dưới đây"`.
3. Kiểm tra `4_3_kiem_thu.tex` có cả `4.3.1` và `4.3.2`.

- [ ] **Step 2: Run test to verify it fails**

Chạy `uv run pytest tests/report_datn/test_section_hierarchy.py` để xác nhận test đỏ (FAIL).

- [ ] **Step 3: Implement section hierarchy restructuring**

- Trong `report-datn/chapters/ch4/4_2_giao_dien.tex`:
  - Nâng các `\subsubsection{4.2.1.1 ...}` thành `\subsection{4.2.1 ...}` đến `\subsection{4.2.6 ...}`.
  - Xóa đoạn văn chứa từ cấm `"dưới đây"` và thay bằng câu văn học thuật chuẩn mực.
- Trong `report-datn/chapters/ch4/4_3_kiem_thu.tex`:
  - Tách nội dung thành `\subsection{4.3.1 Kịch bản kiểm thử tích hợp và kiểm thử hệ thống}` và `\subsection{4.3.2 Đánh giá kết quả kiểm thử và độ tin cậy}`.

- [ ] **Step 4: Run test to verify it passes**

Chạy lại test để xác nhận xanh (PASS).

- [ ] **Step 5: Commit changes**

Git commit với message chuẩn và chạy `bash scripts/deploy_to_vps.sh --fast`.

---

### Task 3: Nạp tệp `frontmatter/loi_mo_dau.tex` vào `main.tex`

**Files:**
- Modify: `report-datn/main.tex`
- Test: `tests/report_datn/test_thesis_structure.py`

**Interfaces:**
- Consumes: `report-datn/frontmatter/loi_mo_dau.tex`.
- Produces: `\input{frontmatter/loi_mo_dau}` được đặt ngay sau `danh_muc_viet_tat.tex` trong `main.tex`, xuất hiện trong Mục lục và Frontmatter.

- [ ] **Step 1: Write the failing test**

Thêm test `test_loi_mo_dau_included_in_main()` vào `tests/report_datn/test_thesis_structure.py` kiểm tra:
1. `report-datn/main.tex` có dòng `\input{frontmatter/loi_mo_dau}`.
2. Vị trí nạp nằm trong phần Frontmatter (trước `\pagenumbering{arabic}`).

- [ ] **Step 2: Run test to verify it fails**

Chạy `uv run pytest tests/report_datn/test_thesis_structure.py -k test_loi_mo_dau_included_in_main` để xác nhận FAIL.

- [ ] **Step 3: Add `\input{frontmatter/loi_mo_dau}` to `main.tex`**

Chèn `\input{frontmatter/loi_mo_dau}` ngay sau `\input{frontmatter/danh_muc_viet_tat}` trong `report-datn/main.tex`.

- [ ] **Step 4: Run test to verify it passes**

Chạy lại test để xác nhận PASS.

- [ ] **Step 5: Commit changes**

Git commit với message chuẩn và chạy `bash scripts/deploy_to_vps.sh --fast`.

---

### Task 4: Khôi phục dãn dòng chuẩn `\onehalfspacing`, gỡ bỏ `\titlespacing*` nén ép và biên dịch `main.pdf`

**Files:**
- Modify: `report-datn/main.tex`
- Modify: `report-datn/main.pdf`
- Test: `scripts/verify_thesis_format.py`
- Test: Toàn bộ suite `tests/report_datn/`

**Interfaces:**
- Consumes: Cấu hình `\onehalfspacing` trong `main.tex`.
- Produces: Tài liệu PDF hoàn chỉnh được biên dịch sạch sẽ bằng XeLaTeX, vượt qua 100% kiểm định hình thức luận văn.

- [ ] **Step 1: Update line spacing and heading spacing in `main.tex`**

1. Thay `\setstretch{1.02}` thành `\onehalfspacing`.
2. Xóa 3 dòng nén ép `\titlespacing*` trong `main.tex`.

- [ ] **Step 2: Recompile `main.pdf` with XeLaTeX**

Thực thi 2 lượt biên dịch XeLaTeX để cập nhật toàn bộ mục lục, liên kết chéo và số trang:
```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```

- [ ] **Step 3: Run comprehensive verification**

Chạy các lệnh kiểm thử:
```bash
uv run python scripts/verify_thesis_format.py
uv run pytest tests/report_datn/
```
Xác nhận 100% PASS và không có lỗi Overfull `\hbox` nào mới.

- [ ] **Step 4: Commit changes**

Git commit với message chuẩn và chạy `bash scripts/deploy_to_vps.sh --fast`.

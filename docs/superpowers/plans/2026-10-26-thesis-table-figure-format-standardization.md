# Thesis Table & Figure Format Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa toàn bộ định dạng Danh mục Bảng biểu (`\listoftables`) và Danh mục Hình ảnh (`\listoffigures`) trong báo cáo đồ án tốt nghiệp `report-datn` về chuẩn HUMG (tiền tố in đậm `\textbf{Bảng X-Y:}` và `\textbf{Hình X-Y:}`).

**Architecture:** Sử dụng macro `\thetable` và `\thefigure` để chuyển sang quy chuẩn gạch nối `Chương-Số` (`3-1`, `2-1`), kết hợp cấu hình `tocloft` (`\cfttabpresnum`, `\cfttabaftersnum`, `\cftfigpresnum`, `\cftfigaftersnum`) và `caption` trong `report-datn/config/preamble.tex`.

**Tech Stack:** XeLaTeX, LaTeX2e, `tocloft`, `caption`, `pdf2image` / `pdftoppm`.

**Spec:** [`docs/superpowers/specs/2026-10-26-thesis-table-figure-format-standardization-design.md`](../specs/2026-10-26-thesis-table-figure-format-standardization-design.md).

## Global Constraints

- Chỉ chỉnh sửa file `report-datn/config/preamble.tex`, không hardcode vào các file nội dung trong `report-datn/chapters/`.
- Không làm xáo trộn các cấu hình Mục lục, lề trang, header đôi, footer đã chuẩn hóa.
- Biên dịch bằng `xelatex` không sinh lỗi cú pháp (exit code 0).

## Review Focus

- Độ rộng thụt lề `\cfttabnumwidth` và `\cftfignumwidth` đủ rộng để nhãn `Bảng 9-99:` không đè lên tiêu đề bảng khi tiêu đề dài xuống dòng.
- Tiêu đề caption trong thân bài tự động hiển thị `Bảng X-Y:` và `Hình X-Y:` in đậm nhất quán với danh mục.

---

### Task 1: Cấu hình Preamble cho Đánh Số & Danh Mục Bảng Biểu / Hình Ảnh

**Files:**
- Modify: `report-datn/config/preamble.tex`

**Interfaces:**
- Consumes: Gói `tocloft`, `caption` trong `preamble.tex`.
- Produces: `\thetable`, `\thefigure`, `\cfttabpresnum`, `\cfttabaftersnum`, `\cfttabnumwidth`, `\cftfigpresnum`, `\cftfigaftersnum`, `\cftfignumwidth`.

- [ ] **Step 1: Cập nhật macro đánh số và cấu hình tocloft trong `report-datn/config/preamble.tex`**

Bổ sung cấu hình:
```latex
% --- Quy chuẩn đánh số Bảng và Hình dùng dấu gạch nối (Chương-Số: 3-1, 3-2) ---
\renewcommand{\thetable}{\thechapter-\arabic{table}}
\renewcommand{\thefigure}{\thechapter-\arabic{figure}}

% --- Cấu hình Danh mục Bảng biểu (LoT) chuẩn HUMG (Ảnh 1) ---
\renewcommand{\cfttabpresnum}{\bfseries Bảng~}
\renewcommand{\cfttabaftersnum}{:}
\newlength{\cfttablen}
\settowidth{\cfttablen}{\bfseries Bảng~9-99:~}
\setlength{\cfttabnumwidth}{\cfttablen}
\cftsetindents{table}{0pt}{\cfttablen}
\renewcommand{\cfttableader}{\cftdotfill{\cftdotsep}}

% --- Cấu hình Danh mục Hình ảnh (LoF) chuẩn HUMG ---
\renewcommand{\cftfigpresnum}{\bfseries Hình~}
\renewcommand{\cftfigaftersnum}{:}
\newlength{\cftfiglen}
\settowidth{\cftfiglen}{\bfseries Hình~9-99:~}
\setlength{\cftfignumwidth}{\cftfiglen}
\cftsetindents{figure}{0pt}{\cftfiglen}
\renewcommand{\cftfigleader}{\cftdotfill{\cftdotsep}}
```

- [ ] **Step 2: Kiểm tra cú pháp preamble**

Đảm bảo các lệnh không bị trùng lặp hoặc xung đột với cấu hình `tocloft` của Mục lục.

---

### Task 2: Biên Dịch XeLaTeX & Kiểm Chứng Trực Quan Đối Chiếu

**Files:**
- Modify: `report-datn/main.pdf` (sinh ra sau biên dịch)
- Verify: `report-datn/main.lot`, `report-datn/main.lof`

- [ ] **Step 1: Biên dịch 2 lượt XeLaTeX để làm mới tệp phụ trợ**

Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex`
Expected: Biên dịch thành công với exit code 0.

- [ ] **Step 2: Kiểm tra nội dung `report-datn/main.lot` và `report-datn/main.lof`**

Xác nhận các dòng đã có số hiệu dạng `2-1`, `3-1` và nhãn `Bảng 2-1:`, `Bảng 3-1:`.

- [ ] **Step 3: Render trang Danh mục Bảng biểu và Danh mục Hình ảnh ra file ảnh để kiểm tra trực quan**

Run: `pdftoppm -png -r 150 -f 4 -l 6 report-datn/main.pdf report-datn/preview_page`
Kiểm tra ảnh trang Danh mục Bảng biểu để xác nhận giống 100% format Ảnh 1.

# Điều chỉnh Mục lục, Header/Footer và Lời cảm ơn ĐATN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Điều chỉnh báo cáo đồ án tốt nghiệp `report-datn/main.pdf` đáp ứng chính xác 3 yêu cầu: in đậm tiêu đề cấp chương trong Mục lục (giữ tiền tố `CHƯƠNG X: ` và số trang nét thường theo Ảnh 1), hiển thị header và footer kèm đường kẻ đôi liên tục từ Mục lục đến hết báo cáo theo Ảnh 2, và xóa bỏ phần ngày tháng ký tên ở Lời cảm ơn.

**Architecture:** Cấu hình tập trung trong `config/preamble.tex` sử dụng các gói `tocloft` và `fancyhdr`. Cô lập kiểu trang hành chính `adminform` để không làm mất header/footer của kiểu `fancy` trên các trang nội dung, đồng thời cập nhật trực tiếp `frontmatter/loi_cam_on.tex`.

**Tech Stack:** XeLaTeX, `tocloft`, `fancyhdr`, `latexmk`, `pdftotext` / Python verification scripts.

**Spec:** `docs/superpowers/specs/2026-10-30-datn-toc-headers-design.md`

## Global Constraints

- Biên dịch bằng `xelatex` (hoặc `latexmk -xelatex`) trong thư mục `report-datn`.
- Giữ nguyên toàn bộ nội dung học thuật và cấu hình đánh số trang (La Mã thường cho frontmatter, Ả Rập từ Lời cảm ơn).
- Không làm thay đổi kiểu trang `adminform` áp dụng cho Phiếu giao đề tài và Đề cương trước Mục lục.

## Review Focus

1. Tiêu đề cấp chương trong Mục lục: Phải in đậm (`\bfseries`) cả phần tiền tố `CHƯƠNG X: ` lẫn tên chương, cũng như các mục hồ sơ `PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP`, `ĐỀ CƯƠNG`, `LỜI CẢM ƠN`, `DANH MỤC...`. Số trang ở cột phải giữ nét thường (`\normalfont`).
2. Header và Footer sau Mục lục: Phải xuất hiện đầy đủ trên 100% các trang từ Mục lục (trang `ix`) cho đến trang cuối cùng của tài liệu, bao gồm cả trang đầu chương (`plain`) và các trang giữa chương (`fancy`).
3. Khối chữ ký Lời cảm ơn: Phải được xóa sạch không để lại khoảng trống bất thường hoặc cảnh báo lỗi biên dịch.
4. Lề số thứ tự chương: Đảm bảo độ rộng thụt lề `\cftchapnumwidth` tính toán trên phông chữ đậm `\bfseries CHƯƠNG 1:\ ` để tránh dính chữ vào tiêu đề chương.
5. Không phát sinh lỗi biên dịch XeLaTeX (exit code 0, không có fatal error).

---

### Task 1: Xóa khối ngày tháng và ký tên trong Lời cảm ơn

**Files:**
- Modify: `report-datn/frontmatter/loi_cam_on.tex:15-20`

**Interfaces:**
- Consumes: `report-datn/frontmatter/loi_cam_on.tex`
- Produces: `report-datn/frontmatter/loi_cam_on.tex` không còn khối `\begin{flushright} ... \end{flushright}`

- [ ] **Step 1: Xác nhận nội dung hiện tại cần xóa trong `loi_cam_on.tex`**

Kiểm tra đoạn mã từ dòng 15 đến 20:
```latex
\vspace{1.5cm}
\begin{flushright}
\textit{Hà Nội, tháng 10 năm 2026} \\
\textbf{Sinh viên thực hiện} \\[1.5cm]
\textbf{Đàm Mạnh Dũng}
\end{flushright}
```

- [ ] **Step 2: Xóa khối ký tên và ngày tháng khỏi `report-datn/frontmatter/loi_cam_on.tex`**

Xóa bỏ đoạn mã trên, chỉ giữ lại nội dung lời cảm ơn kết thúc ở đoạn văn trước đó.

- [ ] **Step 3: Kiểm tra tệp sau chỉnh sửa**

Chạy: `grep -rn "Sinh viên thực hiện" report-datn/frontmatter/loi_cam_on.tex`
Expected: Không có kết quả nào trả về.

- [ ] **Step 4: Commit thay đổi Task 1**

```bash
git add report-datn/frontmatter/loi_cam_on.tex
git commit -m "style(datn): remove signature and date block from loi cam on"
```

---

### Task 2: Cấu hình in đậm tiêu đề chương trong Mục lục (Ảnh 1)

**Files:**
- Modify: `report-datn/config/preamble.tex:152-191`

**Interfaces:**
- Consumes: Cấu hình `tocloft` trong `preamble.tex`
- Produces: Tiêu đề chương in đậm trong TOC (`\cftchapfont{\bfseries}`), số trang nét thường (`\cftchappagefont{\normalfont}`)

- [ ] **Step 1: Viết script kiểm tra hiện trạng định dạng Mục lục**

Chạy script kiểm tra `report-datn/main.toc` hoặc kiểm tra phông chữ `\cftchapfont` trong `preamble.tex`.
Expected: Hiện tại `\cftchapfont` đang là `\normalfont`.

- [ ] **Step 2: Cập nhật định dạng mục lục trong `report-datn/config/preamble.tex`**

1. Cập nhật `\cftchapfont`:
```latex
\renewcommand{\cftchapfont}{\bfseries}
\renewcommand{\cftchappagefont}{\normalfont}
```
2. Cập nhật tính toán chiều rộng tiền tố để phù hợp phông chữ in đậm:
```latex
\settowidth{\cftchaplen}{\bfseries CHƯƠNG 1:\ }
\setlength{\cftchapnumwidth}{\cftchaplen}
\cftsetindents{chapter}{0pt}{\cftchaplen}
```
Giữ nguyên tiền tố `\renewcommand{\cftchappresnum}{CHƯƠNG }` và `\renewcommand{\cftchapaftersnum}{:\ }`.

- [ ] **Step 3: Biên dịch thử và kiểm tra mục lục**

Chạy lệnh biên dịch:
```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && cd ..
```
Kiểm tra bằng pdftotext trên các trang Mục lục xem các dòng `CHƯƠNG`, `PHIẾU GIAO ĐỀ TÀI TỐT NGHIỆP`, `ĐỀ CƯƠNG`, `LỜI CẢM ƠN` được render đầy đủ.

- [ ] **Step 4: Commit thay đổi Task 2**

```bash
git add report-datn/config/preamble.tex
git commit -m "style(datn): bold chapter and frontmatter titles in table of contents"
```

---

### Task 3: Cấu hình hiển thị Header & Footer đồng bộ từ Mục lục đến hết báo cáo (Ảnh 2)

**Files:**
- Modify: `report-datn/config/preamble.tex:101-141`
- Modify: `report-datn/main.tex:52-54`

**Interfaces:**
- Consumes: Thiết lập `fancyhdr` trong `preamble.tex` và lệnh kích hoạt trong `main.tex`
- Produces: Header ("Đồ án tốt nghiệp ngành Công nghệ thông tin") và footer ("SVTH: Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B" + số trang + đường kẻ đôi) xuất hiện trên 100% các trang từ Mục lục đến trang cuối cùng.

- [ ] **Step 1: Xác định nguyên nhân mất header/footer ở các trang nội dung**

Kiểm tra `\fancypagestyle{adminform}`: Lệnh này đang thực hiện `\fancyhf{}` và `\renewcommand{\headrule}{}` / `\renewcommand{\footrule}{}` trên phạm vi toàn cục, khiến kiểu `fancy` bị mất cấu hình khi kích hoạt lại tại dòng 53 của `main.tex`.

- [ ] **Step 2: Tái cấu trúc cấu hình Header/Footer trong `report-datn/config/preamble.tex`**

Định nghĩa lệnh `\setupdatnheaders` chuẩn hóa tiêu đề và đường kẻ đôi:
```latex
\newcommand{\setupdatnheaders}{%
    \fancyhf{}%
    \fancyhead[L]{\fontsize{10}{12}\selectfont\textbf{Đồ án tốt nghiệp ngành Công nghệ thông tin}}%
    \renewcommand{\headrule}{%
        \hrule width \headwidth height 1.2pt \vspace{1.5pt}%
        \hrule width \headwidth height 0.4pt%
    }%
    \fancyfoot[L]{\fontsize{10}{12}\selectfont\textit{SVTH: Đàm Mạnh Dũng - 2221050359 -- Lớp: DCCTCT67\_09B}}%
    \fancyfoot[R]{\fontsize{10}{12}\selectfont\textit{\thepage}}%
    \renewcommand{\footrule}{%
        \hrule width \headwidth height 0.4pt \vspace{1.5pt}%
        \hrule width \headwidth height 1.2pt%
    }%
}
```
Áp dụng `\setupdatnheaders` cho cả style `fancy` và style `plain`:
```latex
\pagestyle{fancy}
\setupdatnheaders

\fancypagestyle{plain}{%
    \setupdatnheaders
}
```
Đồng thời cấu hình lại `adminform` sao cho an toàn:
```latex
\fancypagestyle{adminform}{%
    \fancyhf{}%
    \fancyfoot[R]{\fontsize{10}{12}\selectfont\textit{\thepage}}%
    \renewcommand{\headrule}{}%
    \renewcommand{\footrule}{}%
}
```
Tại `report-datn/main.tex` dòng 53, đảm bảo gọi lại `\setupdatnheaders` và `\pagestyle{fancy}` ngay trước khi nạp Mục lục:
```latex
% Kích hoạt lại fancy headers từ Mục lục trở đi
\setupdatnheaders
\pagestyle{fancy}
```

- [ ] **Step 3: Biên dịch toàn diện và kiểm tra tự động độ phủ Header/Footer**

Chạy lệnh biên dịch XeLaTeX 2 lượt để cập nhật đủ số trang và bookmarks:
```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex && cd ..
```
Chạy script Python duyệt qua từng trang từ trang Mục lục (`ix`) đến trang cuối cùng của `report-datn/main.pdf`, kiểm tra:
1. Header có chứa chuỗi `"Đồ án tốt nghiệp ngành Công nghệ thông tin"` không.
2. Footer có chứa chuỗi `"SVTH: Đàm Mạnh Dũng - 2221050359"` không.
Expected: 100% các trang từ Mục lục đến hết tài liệu đều PASS.

- [ ] **Step 4: Commit thay đổi Task 3**

```bash
git add report-datn/config/preamble.tex report-datn/main.tex
git commit -m "fix(datn): ensure header and footer appear on all pages from toc onward"
```

---

### Task 4: Biên dịch hoàn thiện và Nghiệm thu tổng thể

**Files:**
- Output: `report-datn/main.pdf`

**Interfaces:**
- Consumes: Toàn bộ mã nguồn `report-datn`
- Produces: File `report-datn/main.pdf` hoàn chỉnh đáp ứng đầy đủ 3 yêu cầu.

- [ ] **Step 1: Biên dịch sạch bản PDF cuối cùng**

```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex && cd ..
```
Xác nhận exit code = 0.

- [ ] **Step 2: Chạy kiểm thử tự động toàn diện trên file PDF xuất xưởng**

Viết và thực thi script kiểm tra:
1. Trang bìa và hồ sơ (trang 1 đến 8): Không có header/footer ĐATN (đúng quy chuẩn hồ sơ hành chính).
2. Trang 9 (Mục lục đầu tiên) đến trang cuối: 100% trang có header và footer.
3. Phần Lời cảm ơn: Không còn chuỗi "Hà Nội, tháng 10 năm 2026" và "Sinh viên thực hiện".
4. Mục lục: Tiêu đề các chương đều in đậm.

- [ ] **Step 3: Commit bản PDF hoàn chỉnh (nếu được theo dõi)**

```bash
git add report-datn/main.pdf
git commit -m "build(datn): compile finalized thesis pdf with updated toc and headers"
```

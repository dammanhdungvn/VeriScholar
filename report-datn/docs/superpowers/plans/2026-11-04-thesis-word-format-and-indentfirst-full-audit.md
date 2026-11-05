# Kế Hoạch Chuẩn Hóa Định Dạng Báo Cáo ĐATN Theo Chuẩn Microsoft Word và HIeu.pdf

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

---

## Tổng Quan Kiến Trúc & Mục Tiêu

Kế hoạch này thực hiện rà soát và chuẩn hóa triệt để 100% định dạng của toàn bộ ấn phẩm học thuật Đồ án Tốt nghiệp VeriScholar theo đúng quy chuẩn Microsoft Word và hồ sơ mẫu chuẩn mực `guide/HIeu.pdf` (sinh viên Phạm Quốc Bảo, HUMG):
1. **Cỡ chữ 13pt & Font Times New Roman:** Áp dụng đồng nhất cho toàn bộ thân bài, nội dung bảng biểu, tiêu đề hình/bảng và danh mục. Không co ép cỡ chữ để chữa khoảng trắng. Sửa các continuation header đang dùng 11pt thành 13pt.
2. **Dãn dòng 1.5 lines:** `\setstretch{1.45}` toàn cục, `\arraystretch >= 1.20` trong bảng biểu; loại bỏ triệt để `singlespace` còn sót lại trong `frontmatter/danh_muc_viet_tat.tex`.
3. **Thụt lề dòng đầu 1.0cm (`indentfirst`):** Sửa lỗi đoạn văn đầu tiên sau mọi tiêu đề (`\chapter*`, `\section`, `\subsection`) không thụt lề bằng cách nạp `\usepackage{indentfirst}`.
4. **Biểu mẫu Phiếu giao đề tài & Đề cương ĐATN:** Khớp 100% biểu mẫu khoa và `guide/HIeu.pdf` (thông tin chung, mục tiêu, nhiệm vụ, cam đoan, chữ ký `Xác nhận của GVHD` và `Tác giả ĐATN`, bảng kế hoạch `\arraystretch = 1.20`, kết thúc đúng quy cách không chữ ký thừa ở cuối đề cương).
5. **Đánh số trang:** Số trang Ả Rập bắt đầu số 1 từ **MỤC LỤC**, vị trí dưới cùng bên phải.
6. **Văn phong & Bố cục:** Không in đậm tùy tiện trong văn xuôi (`scan_inline_bolds`), khóa cứng hình/bảng không để trôi nổi, không chèn `\clearpage` ép buộc giữa các tiểu mục.

---

## Cấu Trúc Tệp Thay Đổi

- `config/preamble.tex`: Nạp `\usepackage{indentfirst}`, bảo đảm cấu hình thụt lề dòng đầu tự động cho mọi đoạn văn.
- `frontmatter/phieu_giao_de_tai.tex`: Chuẩn hóa bố cục thông tin chung, lời cam đoan và khối chữ ký khớp `HIeu.pdf` trang 3-4.
- `frontmatter/de_cuong_datn.tex`: Chuẩn hóa bảng SV/GVHD 6 cột có `\allowbreak` email, dãn dòng bảng kế hoạch `\arraystretch = 1.20`, kiểm tra kết thúc mục 8.
- `frontmatter/danh_muc_viet_tat.tex`: Xóa bỏ `\begin{singlespace}` và `\end{singlespace}`, cấu hình `\setstretch{1.45}` và `\arraystretch{1.20}`.
- `chapters/ch3/3_4_phan_tich_usecase.tex`: Sửa continuation header của Bảng 3-2, 3-3, 3-4, 3-5 từ 11pt thành 13pt (`\textit{Bảng 3-X (tiếp theo)}`).
- `scripts/test_tables_and_spacing.py`: Bổ sung các bài kiểm tra tự động cho `indentfirst`, không dùng `singlespace`, cỡ chữ 13pt trong continuation headers, và chuẩn hóa biểu mẫu frontmatter.
- `scripts/audit_full_thesis_sequential.py`: Bổ sung kiểm tra toàn vẹn định dạng mới.

---

## Danh Sách Các Task Cần Thực Hiện

### Task 1: Sửa lỗi Thụt lề dòng đầu đoạn văn (`indentfirst`) trên toàn bộ đồ án
- [ ] Bổ sung bài kiểm tra trong `scripts/test_tables_and_spacing.py`:
  - `test_indentfirst_loaded_in_preamble`: Xác nhận `config/preamble.tex` có `\usepackage{indentfirst}`.
  - `test_global_parindent_is_1cm`: Xác nhận `\setlength{\parindent}{1.0cm}` tồn tại và hợp lệ.
- [ ] Thêm `\usepackage{indentfirst}` vào `config/preamble.tex` (ngay sau dòng cấu hình `\setlength{\parindent}{1.0cm}`).
- [ ] Chạy `uv run pytest scripts/test_tables_and_spacing.py` để xác nhận test pass.
- [ ] Biên dịch thử và kiểm tra với `pdftotext` trên `frontmatter/loi_cam_on.tex` xác nhận đoạn đầu ("Để hoàn thành bản đồ án...") đã được thụt lề dòng đầu đồng bộ với đoạn 2 ("Em xin trân trọng...").
- [ ] Commit với thông điệp: `fix(layout): load indentfirst package to ensure 1.0cm paragraph indent on all initial paragraphs`.

### Task 2: Chuẩn hóa 100% Phiếu giao đề tài & Đề cương ĐATN theo mẫu khoa & `HIeu.pdf`
- [ ] Bổ sung bài kiểm tra trong `scripts/test_tables_and_spacing.py`:
  - `test_phieu_giao_de_tai_matches_hieu_pdf`: Kiểm tra chữ ký `Xác nhận của GVHD` và `Tác giả ĐATN`, không in sẵn họ tên, thông tin chung đầy đủ.
  - `test_de_cuong_datn_structure`: Kiểm tra bảng SV/GVHD 6 cột dùng `tabularx`, có `\allowbreak` cho email, bảng kế hoạch có `\arraystretch >= 1.20`, kết thúc tại mục 8 không có chữ ký.
- [ ] Cập nhật `frontmatter/phieu_giao_de_tai.tex`:
  - Bố cục phần `1. Thông tin chung` dạng bảng gọn gàng khớp `HIeu.pdf` trang 3.
  - Bố cục phần `4. Lời cam đoan của sinh viên`: văn phong cam đoan chuẩn, ngày tháng `06 tháng 11 năm 2026`, chữ ký `Xác nhận của GVHD` (trái) và `Tác giả ĐATN` (phải), khoảng trống 2.2cm, không in sẵn họ tên.
- [ ] Cập nhật `frontmatter/de_cuong_datn.tex`:
  - Kiểm tra bảng SV/GVHD 6 cột với `\tabcolsep = 3.5pt`, `\arraystretch = 1.20`, độ rộng TT (0.7cm), Mã SV/Cán bộ (2.3cm), Họ và tên (2.8cm), Lớp/Đơn vị (2.2cm), Điện thoại (2.1cm), E-mail (`X`), chèn `\allowbreak` trước `@` và `.`.
  - Cập nhật bảng kế hoạch 10 tuần: đổi `\renewcommand{\arraystretch}{1.0}` thành `\renewcommand{\arraystretch}{1.20}`.
  - Xác nhận mục 8 kết thúc tại `Nơi thực hiện đồ án: Trường Đại học Mỏ -- Địa chất`, không có khối chữ ký.
- [ ] Chạy `uv run pytest scripts/test_tables_and_spacing.py` xác nhận pass 100%.
- [ ] Commit với thông điệp: `fix(frontmatter): standardize assignment sheet and thesis proposal according to faculty form and HIeu.pdf`.

### Task 3: Loại bỏ `singlespace` và chuẩn hóa dãn dòng 1.5 lines toàn diện
- [ ] Bổ sung bài kiểm tra trong `scripts/test_tables_and_spacing.py`:
  - `test_no_singlespace_in_frontmatter`: Quét toàn bộ `frontmatter/` bảo đảm 0 sự xuất hiện của `\begin{singlespace}`.
  - `test_usecase_continuation_headers_13pt`: Quét `chapters/ch3/3_4_phan_tich_usecase.tex` bảo đảm các continuation header `Bảng 3-X (tiếp theo)` không chứa `\fontsize{11pt}`.
- [ ] Cập nhật `frontmatter/danh_muc_viet_tat.tex`:
  - Gỡ bỏ hoàn toàn `\begin{singlespace}` và `\end{singlespace}`.
  - Thiết lập `\setstretch{1.45}` và `\renewcommand{\arraystretch}{1.20}` cho các bảng chữ viết tắt để đồng nhất 1.5 lines.
- [ ] Cập nhật `chapters/ch3/3_4_phan_tich_usecase.tex`:
  - Sửa 4 continuation headers của Bảng 3-2, 3-3, 3-4, 3-5: thay `\fontsize{11pt}{13pt}\selectfont\textit{Bảng~3-X (tiếp theo)}` bằng `\fontsize{13pt}{17pt}\selectfont\textit{Bảng~3-X (tiếp theo)}` (hoặc `\textit{Bảng~3-X (tiếp theo)}`).
- [ ] Chạy `uv run pytest scripts/test_tables_and_spacing.py` xác nhận pass 100%.
- [ ] Commit với thông điệp: `fix(formatting): eliminate singlespace from abbreviations and standardize continuation headers to 13pt`.

### Task 4: Rà soát & Đảm bảo font 13pt, cấm in đậm tùy tiện, cấm co ép cỡ chữ chữa khoảng trắng
- [ ] Bổ sung bài kiểm tra trong `scripts/test_tables_and_spacing.py`:
  - `test_no_reduced_font_in_tables`: Quét toàn bộ 17 bảng trong `chapters/` bảo đảm không có `\small`, `\footnotesize`, `\scriptsize`, `\fontsize{10pt}`, `\fontsize{11pt}` nào trong nội dung ô bảng.
  - `test_casual_inline_bolds`: Chạy logic tương đương `scan_inline_bolds.py` xác nhận 0 thẻ `\textbf` dùng tùy tiện trong văn xuôi.
- [ ] Chạy `python3 /home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/scan_inline_bolds.py` xác nhận 0 vi phạm.
- [ ] Kiểm tra đánh số trang: Xác nhận Mục lục bắt đầu bằng số 1 Ả Rập, các trang hồ sơ trước Mục lục không đánh số Ả Rập, Chương 1 nối tiếp đánh số liên tục.
- [ ] Chạy `uv run pytest scripts/test_tables_and_spacing.py` xác nhận pass 100%.
- [ ] Commit với thông điệp: `test(audit): add comprehensive assertions for 13pt table fonts, zero casual bolds, and continuous Arabic numbering`.

### Task 5: Chạy toàn diện 4 Verification Gates và kiểm tra trực quan sản phẩm PDF cuối cùng
- [ ] Cập nhật `scripts/audit_full_thesis_sequential.py` tích hợp các kiểm tra mới về `indentfirst`, `singlespace`, và continuation headers.
- [ ] Chạy `python3 /home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/audit_full_thesis_sequential.py` (yêu cầu 100% 44/44 files pass).
- [ ] Biên dịch 2-pass XeLaTeX ra `main.pdf`:
  - Lệnh: `xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex`.
  - Xác nhận exit code 0, không có lỗi cú pháp.
- [ ] Render PDF các trang quan trọng bằng `pdftoppm`:
  - Trang iii, iv: Phiếu giao đề tài
  - Trang v, vi, vii: Đề cương ĐATN
  - Trang viii: Lời cảm ơn (kiểm tra thụt đầu dòng đoạn 1)
  - Trang 1, 2, 3, 4: Mục lục
  - Trang 8, 9: Danh mục viết tắt (dãn dòng 1.5 lines)
  - Trang 45, 46, 47, 48, 49, 50: Các bảng Use Case đa trang xltabular
- [ ] Chạy 4 Cổng Xác Minh Bắt Buộc (The 4 Verification Gates):
  ```bash
  uv run pytest scripts/test_tables_and_spacing.py
  python3 /home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/audit_full_thesis_sequential.py
  ```
- [ ] Commit và đẩy thay đổi lên `origin/main`.

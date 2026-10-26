# Thiết Kế: Chuẩn Hóa Định Dạng Danh Mục Bảng Biểu & Hình Ảnh Báo Cáo Đồ Án (HUMG)

- **Ngày lập:** 2026-10-26
- **Trạng thái:** Chờ phê duyệt (Pending Approval)
- **Tệp tin tác động:**
  - `report-datn/config/preamble.tex`

---

## 1. Mục Đích & Bối Cảnh (Intent & Why)

Trang **DANH MỤC BẢNG BIỂU** hiện tại của báo cáo đồ án tốt nghiệp (`report-datn/` - Ảnh 2) đang sử dụng cấu hình mặc định của LaTeX, chỉ hiển thị số thứ tự trần (`2.1`, `3.1`), không có chữ "Bảng", không in đậm và dùng dấu chấm phân cách.

Khuôn mẫu chuẩn của đồ án tốt nghiệp HUMG (Ảnh 1 - theo đồ án mẫu `2121050196_NguyenTrungHieu_BaoCaoDATN.md`) yêu cầu:
- Mỗi mục trong Danh mục Bảng biểu bắt buộc có tiền tố in đậm kèm dấu gạch nối và dấu hai chấm: `\textbf{Bảng X-Y:} <Tên bảng>`.
- Tương tự, Danh mục Hình ảnh đồng bộ chuẩn hóa: `\textbf{Hình X-Y:} <Tên hình>`.
- Dấu chấm dẫn trang (leader dots) nối liền sang số trang căn lề phải.
- Tiêu đề caption trong thân bài cũng đồng bộ hiển thị `Bảng X-Y:` và `Hình X-Y:`.

---

## 2. Mục Tiêu & Phạm Vi (Goals, Non-Goals & Anti-Goals)

### Mục tiêu (Goals)
1. **Danh mục Bảng biểu (`\listoftables`):** Định dạng hiển thị chính xác theo mẫu Ảnh 1: `\textbf{Bảng X-Y:} <Tên bảng>`.
2. **Danh mục Hình ảnh (`\listoffigures`):** Định dạng đồng bộ: `\textbf{Hình X-Y:} <Tên hình>`.
3. **Quy chuẩn đánh số toàn cục:** Thay đổi từ `Chương.Số` (`3.1`) sang `Chương-Số` (`3-1`) qua macro `\thetable` và `\thefigure`.
4. **Đồng bộ tiêu đề trong thân bài:** Gói `caption` hiển thị đúng `Bảng X-Y:` và `Hình X-Y:` in đậm ở đầu bảng/dưới hình.
5. **Căn lề số hiệu chuẩn xác:** Sử dụng `tocloft` tính toán độ rộng nhãn (`\cfttabnumwidth`, `\cftfignumwidth`) để các dòng tên bảng/hình dài xuống hàng tự động thụt lề chuẩn, không đè lên nhãn số hiệu.

### Không thuộc phạm vi (Non-Goals)
- Không chỉnh sửa nội dung văn bản học thuật trong các chương (`report-datn/chapters/`).
- Không thay đổi định dạng Mục lục chính (`\tableofcontents`), trang bìa, hay các phần khác.

### Ràng buộc cấm (Anti-Goals)
- Tuyệt đối không hard-code thủ công tên bảng trong file `.lot` hay file frontmatter; mọi thứ phải sinh tự động qua lệnh `\listoftables` và `\listoffigures` của LaTeX.

---

## 3. Các Phương Án Kỹ Thuật Đã Xem Xét (Approaches)

### Phương án 1: Cấu hình toàn cục qua `tocloft` và `caption` trong `preamble.tex` (ĐÃ CHỌN)
- **Ưu điểm:** Nhất quán 100% từ danh mục đến nội dung; tự động hóa hoàn toàn; không can thiệp vào các chương; tuân thủ đúng kiến trúc LaTeX mô-đun hóa của `report-datn`.
- **Đánh đổi:** Cần chạy biên dịch `XeLaTeX` 2 lượt để làm mới các tệp chỉ mục phụ trợ (`.aux`, `.lot`, `.lof`).

### Phương án 2: Hook cục bộ tại `frontmatter/danh_muc_bang.tex` qua `\numberline` (Loại bỏ)
- **Lý do loại bỏ:** Gây bất nhất giữa tiêu đề bảng trong thân bài (`Bảng 3.1`) và danh mục (`Bảng 3-1`), dễ phát sinh lỗi macro khi ghi đè `.lot`.

---

## 4. Chi Tiết Kỹ Thuật Triển Khai (Implementation Details)

Cập nhật `report-datn/config/preamble.tex`:

```latex
% --- Quy chuẩn đánh số Bảng và Hình dùng dấu gạch nối (Chương-Số: 3-1, 3-2) ---
\renewcommand{\thetable}{\thechapter-\arabic{table}}
\renewcommand{\thefigure}{\thechapter-\arabic{figure}}

% --- Cấu hình Danh mục Bảng biểu (LoT) chuẩn HUMG (Ảnh 1) ---
\renewcommand{\cfttabpresnum}{\bfseries Bảng~}
\renewcommand{\cfttabaftersnum}{:}
\newlength{\cfttablen}
\settowidth{\cfttablen}{\bfseries Bảng~99-99:~}
\setlength{\cfttabnumwidth}{\cfttablen}
\cftsetindents{table}{0pt}{\cfttablen}
\renewcommand{\cfttableader}{\cftdotfill{\cftdotsep}}

% --- Cấu hình Danh mục Hình ảnh (LoF) chuẩn HUMG ---
\renewcommand{\cftfigpresnum}{\bfseries Hình~}
\renewcommand{\cftfigaftersnum}{:}
\newlength{\cftfiglen}
\settowidth{\cftfiglen}{\bfseries Hình~99-99:~}
\setlength{\cftfignumwidth}{\cftfiglen}
\cftsetindents{figure}{0pt}{\cftfiglen}
\renewcommand{\cftfigleader}{\cftdotfill{\cftdotsep}}
```

Sau đó thực hiện biên dịch lại báo cáo:
```bash
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex
```

Kiểm tra trực quan tệp `main.pdf` (chuyển trang Danh mục Bảng biểu sang ảnh để đối chiếu trực tiếp với Ảnh 1).

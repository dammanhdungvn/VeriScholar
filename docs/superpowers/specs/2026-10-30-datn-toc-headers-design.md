# Thiết kế điều chỉnh định dạng Mục lục, Header/Footer và Lời cảm ơn ĐATN

## 1. Mục đích và Ý nghĩa (Intent & Why)
Bản báo cáo đồ án tốt nghiệp cần đáp ứng đúng quy chuẩn định dạng hình thức của khoa Công nghệ Thông tin - HUMG:
- Các mục cấp chương và hồ sơ đầu khóa trong Mục lục nổi bật, dễ tra cứu theo mẫu trực quan (Ảnh 1).
- Tiêu đề đầu trang (header) và chân trang (footer) kèm đường kẻ đôi xuất hiện đồng nhất từ Mục lục đến hết báo cáo (Ảnh 2), nhận diện rõ tên đề tài và tác giả sinh viên.
- Phần Lời cảm ơn bỏ phần ký tên theo yêu cầu định dạng thực tế.

## 2. Mục tiêu, Phi mục tiêu và Rủi ro cần tránh (Goals, Non-goals, Anti-goals)
- **Goals:**
  - Mục lục: Các mục cấp chương (CHƯƠNG, PHIẾU GIAO ĐỀ TÀI, ĐỀ CƯƠNG, LỜI CẢM ƠN, LỜI MỞ ĐẦU, DANH MỤC..., KẾT LUẬN, TÀI LIỆU THAM KHẢO) được in đậm (`\bfseries`). Giữ tiền tố `CHƯƠNG X: ` (có dấu hai chấm) và giữ số trang nét thường (`\normalfont`).
  - Header & Footer: Toàn bộ các trang từ Mục lục (bắt đầu trang `ix`) đến hết đồ án đều hiển thị đầy đủ header (`Đồ án tốt nghiệp ngành Công nghệ thông tin`) và footer (`SVTH: Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B` cùng số trang), kèm đường kẻ đôi trên dưới.
  - Lời cảm ơn: Xóa hoàn toàn khối ngày tháng, "Sinh viên thực hiện" và tên sinh viên ở cuối `frontmatter/loi_cam_on.tex`.
  - Biên dịch thành công `main.pdf` không phát sinh lỗi hoặc cảnh báo tràn khung (overfull/underfull) mới.
- **Non-goals:**
  - Không thay đổi nội dung học thuật bên trong các chương.
  - Không thay đổi định dạng bìa chính, bìa phụ, phiếu giao đề tài và đề cương đồ án (giữ nguyên phong cách `adminform` cho hồ sơ trước Mục lục).
- **Anti-goals:**
  - Tránh làm vỡ cấu trúc đánh số trang (La Mã thường cho frontmatter, Ả Rập bắt đầu từ Lời cảm ơn).
  - Tránh để kiểu trang `adminform` can thiệp và xóa tiêu đề trang ở các trang sau Mục lục.

## 3. Ràng buộc kỹ thuật (Constraints)
- Sử dụng công cụ biên dịch XeLaTeX hiện có qua `latexmk` hoặc `xelatex`.
- Duy trì định dạng bảng và các gói lệnh hiện có (`tocloft`, `fancyhdr`, `geometry`).

## 4. Các phương án đã cân nhắc (Approaches)
- **Phương án 1 (Đã chọn):**
  - Cấu hình tập trung trong `config/preamble.tex`: dùng `\cftchapfont{\bfseries}`, giữ `\cftchappagefont{\normalfont}`, tính lại khoảng cách tiền tố `\settowidth{\cftchaplen}{\bfseries CHƯƠNG 1:\ }`.
  - Chuẩn hóa cấu hình `fancyhdr` thành hàm kích hoạt tập trung hoặc cấu hình lại `\fancypagestyle{fancy}`, đảm bảo sau khi thoát khỏi các trang hành chính và gọi `\pagestyle{fancy}` trước Mục lục thì mọi trang đều áp dụng đúng quy chuẩn.
  - Xóa dòng 15-20 trong `frontmatter/loi_cam_on.tex`.
  - *Lý do chọn:* Tác động đúng điểm gốc rễ, đảm bảo tính ổn định và tính mở rộng nếu có thêm trang mới.
- **Phương án 2 (Loại bỏ):**
  - In đậm cả số trang ở Mục lục (`\cftchappagefont{\bfseries}`) và gọi lệnh đổi trang thủ công ở đầu từng tệp tex.
  - *Lý do loại:* Không khớp với ảnh mẫu 1 (ảnh 1 số trang nét thường) và dễ gây sót trang khi có chỉnh sửa tài liệu.

## 5. Quyết định kỹ thuật chi tiết (Decisions)
- **Mục lục:** Giữ nguyên tiền tố `CHƯƠNG X: ` (có dấu hai chấm) theo xác nhận của người dùng.
- **Header/Footer:** Áp dụng liên tục từ trang bắt đầu Mục lục đến hết tài liệu.
- **Tệp chỉnh sửa:**
  - `report-datn/config/preamble.tex`
  - `report-datn/frontmatter/loi_cam_on.tex`

## 6. Nhiệm vụ cho khâu thực thi (Left to Builder)
- Cập nhật mã nguồn LaTeX theo Phương án 1.
- Biên dịch lại tài liệu `report-datn/main.pdf` bằng XeLaTeX.
- Trích xuất và kiểm tra tự động các trang đại diện (Mục lục các trang, Danh mục hình ảnh/bảng biểu, các trang nội dung giữa chương) để nghiệm thu đầy đủ header/footer và độ in đậm của Mục lục.

# Thiết Kế Kỹ Thuật: Chuẩn Hóa Dấu Gạch Đầu Dòng Trong Bảng & Rà Soát Toàn Diện Thể Thức Báo Cáo Theo Chuẩn MS Word

## 1. Mục Đích & Bối Cảnh (Intent & The Why)
- **Bối cảnh:** Trong các phiên làm việc trước, các bảng đặc tả Use Case (Bảng 3-2, 3-3, 3-4, 3-5) tại `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex` đang sử dụng tiền tố `\textbf{Bước 1:}`, `\textbf{Bước 2:}`... cho luồng sự kiện chính. Người dùng yêu cầu loại bỏ hoàn toàn chữ "Bước" để chuyển sang sử dụng dấu gạch đầu dòng (`-` / `--`), đồng thời làm sạch các ký hiệu trích dẫn số học còn sót lại như `[1], [2]` trong Bảng 3-3.
- **Yêu cầu thể thức theo MS Word:** Toàn bộ báo cáo ĐATN phải phản ánh chính xác các quy định về thể thức của Trường Đại học Mỏ - Địa chất (HUMG) vốn được thiết kế trên hệ quy chuẩn Microsoft Word:
  - Cỡ chữ toàn văn và trong bảng: **13pt** Times New Roman.
  - Dãn dòng: **1.5 lines chuẩn Word** (tương đương `\setstretch{1.45}` trong XeLaTeX).
  - Nghiêm cấm mọi hành vi co ép dãn dòng hoặc giảm cỡ chữ trong bảng để tiết kiệm giấy (như các bảng đang bị đặt `\arraystretch{0.80}` hoặc `\tabcolsep{2.0pt}`).
  - Lấy `guide/HIeu.pdf` (sinh viên Phạm Quốc Bảo) làm bản mẫu tham chiếu vàng đối chiếu trực tiếp.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals, Anti-Goals)

### 2.1. Mục Tiêu (Goals)
1. **Loại bỏ chữ "Bước" trong toàn bộ bảng:** Chuyển đổi 100% các bước trong luồng sự kiện chính tại 4 bảng đặc tả Use Case (Bảng 3-2, 3-3, 3-4, 3-5) sang dấu gạch đầu dòng en-dash (`\item[--]`), đồng bộ hoàn hảo với luồng thay thế / ngoại lệ.
2. **Làm sạch ký hiệu trích dẫn sót lại trong bảng:** Chuẩn hóa các ký hiệu trích dẫn `[1], [2]` trong Bảng 3-3 thành thuật ngữ kỹ thuật rõ ràng (*"thẻ minh chứng thứ nhất, thứ hai"* hoặc *"thẻ minh chứng tọa độ"*).
3. **Khôi phục dãn dòng chuẩn 1.5 Word cho các bảng bị co ép:**
   - Bảng 1-1 (`tab:related_systems_comparison`): Nâng từ `\arraystretch{0.80}` và `\tabcolsep{2.0pt}` lên `\arraystretch{1.20}` và `\tabcolsep{5pt}`.
   - Bảng 2-1 (`tab:vector_db_comparison`): Nâng từ `\arraystretch{1.08}` lên `\arraystretch{1.20}`.
   - Bảng 2-2 (`tab:search_comparison`): Nâng từ `\arraystretch{1.0}` lên `\arraystretch{1.20}`.
4. **Rà soát 100% thể thức toàn văn theo chuẩn Word:**
   - Cỡ chữ: 13pt toàn văn bản và trong các ô bảng.
   - Dãn dòng: `\setstretch{1.45}` (1.5 lines Word).
   - Lề trang: Top 2.5cm, Bottom 2.5cm, Left 3.5cm, Right 2.5cm.
   - Thụt lề đoạn: 1.0cm; khoảng cách đoạn: `3pt plus 1pt minus 1pt`.
   - Vị trí caption: Bảng ở trên, Hình ở dưới, 12pt nghiêng.
   - Mục lục không đậm, Danh mục Hình/Bảng dãn dòng 1.5 không nén `singlespace`.
5. **Đồng bộ hóa AGENTS.md và Bộ Kiểm Thử Tự Động:**
   - Cập nhật Điều 10 trong `report-datn/AGENTS.md` (chuyển quy định luồng chính dùng `Bước 1:` sang dùng dấu gạch đầu dòng `--`).
   - Cập nhật test `test_usecase_spec_tables_step_conventions` trong `tests/report_datn/test_thesis_format_hieu.py` để assert `\item[--]` thay vì `Bước 1:`.
   - Bổ sung bài test kiểm tra không bảng nào bị bóp `\arraystretch < 1.15`.
6. **Vượt qua 100% Verification Gates:**
   - Biên dịch 2-pass XeLaTeX thành công 0 lỗi.
   - `python3 scripts/verify_thesis_format.py` đạt 100%.
   - `bash scripts/dev/verify.sh` đạt 100%.

### 2.2. Phi Mục Tiêu (Non-Goals)
- Không thay đổi cấu trúc chương hồi hoặc viết lại nội dung học thuật lớn.
- Không thay đổi danh mục 10 bài báo tham khảo đã chốt.
- Không sửa đổi đồ họa sơ đồ TikZ nếu không bị tràn lề.

### 2.3. Chống Mục Tiêu (Anti-Goals)
- **CẤM** co nhỏ phông chữ (`\small`, `\footnotesize`) hoặc hạ dãn dòng (`\arraystretch < 1.15`, `\setstretch < 1.45`) để cố tình ép bảng vào 1 trang hoặc tiết kiệm giấy.
- **CẤM** sử dụng số thứ tự tự do (`1.`, `2.`, `(1)`) trong nội dung bảng.
- **CẤM** đưa lại bất kỳ lệnh `\cite{...}` hoặc ký hiệu `[1]`, `[2]` nào vào thân bài.

---

## 3. Ràng Buộc Kỹ Thuật (Constraints)
- Trình biên dịch: XeLaTeX Unicode bản địa với phông `Times New Roman` chuẩn.
- Phù hợp 100% `guide/HIeu.pdf` và Quy định ĐATN của Khoa CNTT — HUMG.
- Mọi thay đổi phải vượt qua bộ kiểm thử tự động của dự án.

---

## 4. Các Phương Án Kỹ Thuật Đã Cân Nhắc & Lựa Chọn (Approaches)

### Phương án A: Sử dụng dấu chấm tròn bullet (`\item[\textbullet]`) cho luồng chính
- *Mô tả:* Chuyển `Bước 1:` thành dấu bullet tròn.
- *Đánh giá:* Phân biệt luồng chính (bullet) và luồng phụ (gạch đầu dòng), nhưng làm nội dung bảng có nhiều loại ký hiệu đầu dòng khác nhau.

### Phương án B: Sử dụng dấu gạch đầu dòng en-dash (`\item[--]`) đồng bộ toàn bảng (ĐÃ CHỌN)
- *Mô tả:* Toàn bộ các bước tuần tự và các ý trong ô bảng đều sử dụng dấu gạch đầu dòng en-dash (`--`).
- *Lý do chọn:* Khớp hoàn toàn với bản mẫu `HIeu.pdf` trang 36, tạo sự nhất quán, gọn gàng và tinh tế trong toàn bộ các bảng đặc tả Use Case. Người dùng đã lựa chọn phương án này.

---

## 5. Chi Tiết Thực Hiện (Detailed Execution Specifications)

### 5.1. Bốn Bảng Đặc Tả Use Case (`chapters/ch3/3_4_phan_tich_usecase.tex`)
- **Bảng 3-2 (`tab:uc_kham_pha_spec`):**
  - Đổi 5 dòng `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 5:}]` thành `\item[--]`.
- **Bảng 3-3 (`tab:uc_doc_sau_spec`):**
  - Đổi 5 dòng `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 5:}]` thành `\item[--]`.
  - Thay thế `[1], [2]` tại ô "Điều kiện kết thúc" thành: *"kèm theo các thẻ minh chứng số thứ nhất và thứ hai liên kết với tọa độ Bounding Box."*
  - Thay thế `[i]` tại Bước 3 thành: *"xác thực mọi thẻ trích dẫn minh chứng khớp với phân đoạn nguồn."*
  - Thay thế `[1]` tại Bước 5 thành: *"Học giả nhấp chuột vào thẻ trích dẫn minh chứng trong câu trả lời..."*
- **Bảng 3-4 (`tab:uc_graphrag_spec`):**
  - Đổi 5 dòng `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 5:}]` thành `\item[--]`.
- **Bảng 3-5 (`tab:uc_bien_soan_spec`):**
  - Đổi 4 dòng `\item[\textbf{Bước 1:}]` $\dots$ `\item[\textbf{Bước 4:}]` thành `\item[--]`.

### 5.2. Chuẩn Hóa Dãn Dòng & Đệm Ô Bảng Biểu (Chống Co Ép Tiết Kiệm Giấy)
- **Bảng 1-1 (`chapters/ch1/1_2_tinh_cap_thiet.tex`):**
  - Thay `\arraystretch{0.80}` bằng `\arraystretch{1.20}`.
  - Thay `\tabcolsep{2.0pt}` bằng `\tabcolsep{5pt}`.
- **Bảng 2-1 (`chapters/ch2/2_1_postgresql_redis.tex`):**
  - Thay `\arraystretch{1.08}` bằng `\arraystretch{1.20}`.
  - Đặt `\tabcolsep = 5pt`.
- **Bảng 2-2 (`chapters/ch2/2_2_hybrid_rag.tex`):**
  - Thay `\arraystretch{1.0}` bằng `\arraystretch{1.20}`.
  - Đặt `\tabcolsep = 5pt`.

### 5.3. Cập Nhật SSOT & Bộ Kiểm Thử
- **`report-datn/AGENTS.md`:** Cập nhật Điều 10 ("Quy cách trình bày nội dung bảng: Dùng dấu gạch đầu dòng `--` cho các bước thực hiện và luồng thay thế, dùng `\textbullet` cho liệt kê đặc tính; cấm số thứ tự tự do ngoài cột STT").
- **`tests/report_datn/test_thesis_format_hieu.py`:**
  - Sửa `test_usecase_spec_tables_step_conventions` để kiểm tra sự hiện diện của `\item[--]` thay vì `Bước 1:`.
  - Bổ sung test kiểm tra không có bảng nào bị đặt `\arraystretch < 1.15`.

---

## 6. Phân Công & Các Việc Cần Thực Hiện Bởi Kỹ Sư (What's Left to the Builder)
1. Thực hiện các chỉnh sửa mã nguồn LaTeX trong các tệp tương ứng.
2. Cập nhật bài test và tài liệu cẩm nang `AGENTS.md`.
3. Biên dịch XeLaTeX 2-pass, rà soát trang in PDF đầu ra bằng `pdftoppm` để bảo đảm các bảng không tràn lề và không tạo khoảng trắng bất thường.
4. Chạy toàn bộ các cổng kiểm thử tự động, commit và push lên repository.

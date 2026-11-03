# BẢN THIẾT KẾ KỸ THUẬT: TINH GỌN CƠ SỞ DỮ LIỆU, XÓA PHỤ LỤC A VÀ CHUẨN HÓA BỐ CỤC ĐỒ HỌA BÁO CÁO ĐỒ ÁN TỐT NGHIỆP

> **Tài liệu:** Design Specification Document  
> **Dự án:** VeriScholar — Nền tảng AI Hỗ trợ Nghiên cứu Khoa học  
> **Tác giả:** Đàm Mạnh Dũng  
> **Thời điểm lập:** 03/11/2026  

---

## 1. Mục Tiêu & Bối Cảnh (Intent & Why)

Qua rà soát thực tế các bản in và phản hồi của người dùng:
1. **Phần Cơ sở Dữ liệu (Mục 3.6):** Quá ôm đồm và lộn xộn. Bảng tổng hợp 20 bảng bị gộp chung dài dòng, 2 sơ đồ ERD (Hình 3-13 và 3-14) có mật độ quá dày đặc, chữ nhòe không đọc được và ký hiệu không chuẩn mực.
2. **Phụ lục A (`chapters/phu_luc.tex`):** Kéo dài 5 trang (328 dòng) sau danh mục Tài liệu tham khảo, vi phạm quy định chuẩn của Khoa/Bộ môn (báo cáo kết thúc sau Tài liệu tham khảo).
3. **Căn chỉnh bảng biểu:** Toàn bộ các bảng trong đồ án đang bị lệch sang trái ở các cột ngắn (STT, Tên cột, Kiểu dữ liệu, Ràng buộc, Bản số), không đồng bộ với tiêu đề cột căn giữa.
4. **Lỗi sơ đồ đồ họa:** Hình 2-4 bị chèn đè chữ lên mũi tên; Hình 3-2 có cỡ chữ quá bé do scale 0.58; Hình 3-5 có các hình oval Use Case con bị dính chùm vào nhau; Hình 3-12 (Class Diagram) có đường kẻ cắt chéo mạng nhện.

**Mục tiêu cốt lõi:** Tinh gọn triệt để theo nguyên tắc 80/20, xóa bỏ các phần thừa, chuẩn hóa thẩm mỹ đạt chuẩn xuất bản khoa học, giữ tổng số trang báo cáo trong khung 75–80 trang.

---

## 2. Phạm Vi Thay Đổi (Scope of Work)

### 2.1. Tái cấu trúc phần Cơ sở Dữ liệu (Mục 3.6 trong `chapters/ch3/3_6_thiet_ke_csdl.tex`)
* **XÓA BỎ HOÀN TOÀN:**
  * 2 sơ đồ ERD: `Hình 3-13` (ERD Phân hệ Định danh, CAS và Đọc sâu) và `Hình 3-14` (ERD Phân hệ Đồ thị Tri thức và Bản thảo).
  * `Bảng 3-7: Tổng hợp 20 bảng cơ sở dữ liệu` (bảng gộp 20 hàng gây rối). Thay vào đó, tóm tắt 5 nhóm phân hệ bằng văn phong súc tích kèm danh sách ngắn gọn.
  * Toàn bộ các câu văn dẫn chiếu đến Phụ lục A.
* **GIỮ VÀ CHUẨN HÓA:**
  * **Bảng 3-6: Phân tích các lớp thực thể miền và mối quan hệ cấu trúc** (chuẩn hóa bản số $1-1$, $1-N$, $N-N$, căn giữa các cột Lớp A, Lớp B, Kiểu quan hệ, Bản số).
  * **4 Bảng đặc tả CSDL hạt nhân phân theo từng phân hệ rõ ràng (không gộp):**
    1. *Phân hệ Thư viện & CAS:* Đặc tả bảng `documents` (Khóa ngoại CAS Blob, DOI, metadata).
    2. *Phân hệ Đọc sâu & BBox:* Đặc tả bảng `document_chunks` (Tọa độ BBox $[0, 1]^4$, `VECTOR(1536)`, `TSVECTOR`).
    3. *Phân hệ Đồ thị Tri thức GraphRAG:* Đặc tả bảng `graph_nodes` (4 loại thực thể học thuật, vector nhúng).
    4. *Phân hệ Soạn thảo học thuật & Agent:* Đặc tả bảng `drafts` (Bản thảo LaTeX, mã kết xuất biên dịch).
  * Tối ưu lại **Hình 3-12 (Biểu đồ lớp UML):** Tăng khoảng cách giữa các node, tách luồng đường nối để không bị đè lên bản số và không cắt chéo nhau dạng mạng nhện.

### 2.2. Xóa bỏ hoàn toàn Phụ lục A
* Xóa lệnh `\input{chapters/phu_luc}` khỏi `report-datn/main.tex`.
* Xóa tệp `report-datn/chapters/phu_luc.tex` (328 dòng).
* Dọn dẹp tất cả các `\ref{tab:spec_...}` và nhãn trỏ tới Phụ lục A trong toàn bộ các chương, bảo đảm 0 warning "reference undefined".

### 2.3. Chuẩn hóa căn giữa (Center) nội dung các bảng
* Toàn bộ bảng trong báo cáo (Chương 1, 2, 3, 4) được cấu hình cột theo chuẩn:
  * Cột `STT`: `>{\centering\arraybackslash}m{1.0cm}` hoặc `c` (Căn giữa cả ngang và dọc).
  * Cột định danh, kiểu dữ liệu, bản số, ràng buộc, trạng thái: `>{\centering\arraybackslash}m{...}` (Căn giữa).
  * Cột mô tả, văn bản dài: `>{\raggedright\arraybackslash}X` (Căn lề trái hoặc đều).
* Tăng `\arraystretch` lên $1.15$ – $1.2$ và `\tabcolsep` hợp lý để các hàng không bị dính sát vào đường kẻ `\hline`.

### 2.4. Sửa lỗi hiển thị các sơ đồ đồ họa (Figures)
1. **Hình 2-4 (`2_5_agentic_react.tex`):**
   * Tăng khoảng cách từ nút Quyết định (`cond`) xuống hộp kết quả (`final`) từ `-1.5` $\to$ `-3.6` thành giãn cách an toàn, dịch nhãn `Yes (Exit 0)` sang bên cạnh mũi tên, không đè lên viền hộp.
   * Dãn rộng bán kính cong của mũi tên phản hồi `obs` $\to$ `agent` để nhãn `Phản hồi vòng lặp sửa cú pháp` nằm tách biệt, không dính vào đường nét đứt.
   * Đồng bộ màu sắc thành bảng màu học thuật tinh giản (Teal / Blue / Slate / Orange).
2. **Hình 3-2 (`3_3_kien_truc.tex`):**
   * Tăng `scale` từ `0.58` lên `0.72` hoặc bố trí lại dạng lưới 3 tầng rõ ràng để chữ giải thích to rõ, đọc tốt khi in A4.
   * Hạ vị trí tiêu đề `LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT` vào bên trong khung, không chạm mép viền trên.
3. **Hình 3-5 (`3_4_phan_tich_usecase.tex`):**
   * Tăng khoảng cách trục dọc giữa các Use Case con từ $\Delta y = 0.75$ lên $\Delta y = 1.15$.
   * Tách điểm xuất phát của các đường `<<include>>` để nhãn không đè lên nhau.

---

## 3. Các Ràng Buộc & Tiêu Chí Nghiệm Thu (Acceptance Criteria)

1. **Gate 1 (Không lỗi biên dịch):** XeLaTeX biên dịch thành công 100% với 0 lỗi cú pháp, 0 undefined references.
2. **Gate 2 (Cấu trúc phân trang chuẩn):** Báo cáo kết thúc ngay sau Tài liệu tham khảo. Số trang nằm trong khoảng 74–78 trang in.
3. **Gate 3 (Quy chuẩn định dạng):** `scripts/verify_thesis_format.py` đạt 100% Pass.
4. **Gate 4 (Kiểm định toàn diện):** 4 Verification Gates (Ruff, Pytest, Vitest, Web build) đạt 100% Exit code 0.

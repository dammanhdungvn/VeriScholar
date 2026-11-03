# Thiết Kế Chi Tiết: Chuẩn Hóa Ngôn Từ Kỹ Thuật Học Thuật & Thuật Ngữ BYOK Trong Luận Văn (Academic Terminology Radical Polish)

**Mã tài liệu:** `SPEC-2026-11-03-THESIS-TERMINOLOGY-POLISH`  
**Dự án:** Luận văn tốt nghiệp VeriScholar — Đại học Mỏ - Địa chất (HUMG)  
**Tác giả:** VeriScholar Core Team & Google Antigravity Agent  
**Ngày lập:** 03/11/2026  
**Trạng thái:** Chờ phê duyệt (Pending Approval)

---

## 1. Bối Cảnh & Mục Tiêu (Intent & The Why)

Trong quá trình rà soát Mục lục và các chương nội dung của luận văn tốt nghiệp, một số thuật ngữ chuyên ngành Công nghệ thông tin và An toàn thông tin đang bị dịch nghĩa đen thô ráp (dịch máy từng từ hoặc gán ghép từ ngữ đời sống), gây mất tính trang trọng và giảm sút độ tin cậy học thuật của công trình:

1. **"Két an toàn khóa cá nhân" (Personal Key Safe/Vault):**
   - *Vấn đề:* "Két an toàn" là đồ vật gia dụng/ngân hàng, hoàn toàn không phải thuật ngữ khoa học máy tính để chỉ cơ chế quản lý khóa mã hóa API.
   - *Yêu cầu của người dùng:* Viết rõ ràng khái niệm gốc tiếng Anh, giải thích bản chất B-Y-O-K (*Bring Your Own Key*) bằng tiếng Việt học thuật, và thể hiện chuyên nghiệp trên Mục lục cũng như nội dung bài viết.
2. **"Môi trường MicroVM cô lập hạt nhân" (Kernel-level Isolation):**
   - *Vấn đề:* Thuật ngữ hệ điều hành *Kernel* (nhân hệ điều hành) bị dịch nhầm thành "hạt nhân" (thuộc về vật lý nguyên tử), gây cảm giác phi lý và thiếu hiểu biết về hệ thống máy tính.
3. **Các từ ngữ mang văn phong quảng bá hoặc dịch thô khác:**
   - Cần rà soát và chuẩn hóa toàn bộ các cụm từ liên quan như "két khóa", "hộp cát", bảo đảm đạt chuẩn ngôn từ kỹ thuật phần mềm cao cấp theo quy chuẩn Quốc tế và Bộ môn Hệ thống thông tin.

---

## 2. Bảng Chuẩn Hóa Thuật Ngữ (Terminology Mapping Matrix)

| Thuật ngữ gốc tiếng Anh | Ngôn từ cũ (Bị loại bỏ) | Ngôn từ học thuật chuẩn mới | Vị trí áp dụng |
| :--- | :--- | :--- | :--- |
| **Bring Your Own Key (BYOK)** | Két an toàn khóa cá nhân BYOK / Két khóa cá nhân | **Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK)** | Tiêu đề Mục 2.5.4, Mục lục, Chương 1, Chương 3, Kết luận |
| **Kernel-level Isolation** | Cô lập hạt nhân | **Cô lập cấp nhân hệ điều hành** (hoặc *Cô lập mức nhân*) | Tiêu đề Mục 2.5.3, Thân bài Mục 2.5.3, Hình 2-4 |
| **Personal Encrypted Key Storage** | Két khóa BYOK / Két an toàn | **Kho lưu trữ khóa mã hóa cá nhân** | Mục 1.3, Mục 3.3 (Hình 3-2), Mục 3.6 |
| **E2B MicroVM Sandbox** | Môi trường MicroVM cô lập hạt nhân E2B | **Môi trường máy ảo MicroVM E2B cô lập cấp hệ điều hành** | Tiêu đề Mục 2.5.3, Mục lục, Hình 2-4 |
| **BYOK Abbreviation Entry** | (Chưa có hoặc giải thích thô) | **BYOK** — *Bring Your Own Key* — *Mô hình quản lý khóa bảo mật do người dùng tự cung cấp* | Danh mục từ viết tắt |

---

## 3. Chi Tiết Thay Đổi Theo Từng Tệp Văn Bản

### 3.1. Chương 2: Cơ Sở Lý Thuyết (`report-datn/chapters/ch2/2_5_agentic_react.tex`)
- **Mục 2.5.3:**
  - Tiêu đề cũ: `\subsection{Môi trường MicroVM cô lập hạt nhân E2B và vòng lặp tự sửa lỗi LaTeX}`
  - Tiêu đề mới: `\subsection{Môi trường máy ảo MicroVM E2B cô lập cấp hệ điều hành và vòng lặp tự sửa lỗi LaTeX}`
  - Dòng 44: Sửa `Cô lập ranh giới hạt nhân` $\to$ `Cô lập mức nhân hệ điều hành (\textit{Kernel-level Isolation})`
  - Hình 2-4 (dòng 86): Sửa `Môi trường Linux cô lập hạt nhân` $\to$ `Môi trường Linux cô lập cấp nhân`
- **Mục 2.5.4:**
  - Tiêu đề cũ: `\subsection{Két an toàn khóa cá nhân BYOK và chuẩn mã hóa xác thực AES-256-GCM}`
  - Tiêu đề mới: `\subsection{Mô hình quản lý khóa người dùng tự cấp Bring Your Own Key (BYOK) và chuẩn mã hóa AES-256-GCM}`
  - Nội dung dòng 128: Sửa `Để bảo vệ tuyệt đối quyền riêng tư và chi phí sử dụng mô hình của học giả, hệ thống \VS triển khai mô hình két an toàn khóa cá nhân (BYOK -- \textit{Bring Your Own Key})...` $\to$ `Để bảo đảm an toàn quyền riêng tư và quyền chủ động kiểm soát chi phí của học giả, hệ thống \VS triển khai mô hình quản lý khóa người dùng tự cấp (BYOK -- \textit{Bring Your Own Key})...`

### 3.2. Chương 1: Tổng Quan (`report-datn/chapters/ch1/1_3_muc_tieu.tex`)
- Dòng 17: Sửa `Thiết lập cơ chế két khóa bảo mật cá nhân (BYOK -- \textit{Bring Your Own Key})...` $\to$ `Thiết lập cơ chế quản lý khóa người dùng tự cấp theo mô hình Bring Your Own Key (BYOK) mã hóa bằng chuẩn AES-256-GCM...`

### 3.3. Chương 3: Thiết Kế Hệ Thống
- **Mục 3.3 (`report-datn/chapters/ch3/3_3_kien_truc.tex:83`):**
  - Sửa `Quy tắc nghiệp vụ miền $\bullet$ Quản trị phiên $\bullet$ Két khóa BYOK Envelope` $\to$ `Quy tắc nghiệp vụ miền $\bullet$ Quản trị phiên $\bullet$ Quản lý khóa BYOK Envelope`
- **Mục 3.6 (`report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:291`):**
  - Sửa `...và két khóa API cá nhân (\texttt{users}, \texttt{scholar\_profiles}, \texttt{user\_api\_keys}).` $\to$ `...và kho lưu trữ khóa API cá nhân theo mô hình BYOK (\texttt{users}, \texttt{scholar\_profiles}, \texttt{user\_api\_keys}).`

### 3.4. Chương Kết Luận (`report-datn/chapters/ket_luan.tex:13`)
- Sửa `...Bảo mật két khóa BYOK:...đi kèm cơ chế két khóa cá nhân BYOK...` $\to$ `...Bảo mật khóa API theo mô hình BYOK:...đi kèm cơ chế quản lý khóa người dùng tự cấp BYOK...`

### 3.5. Danh Mục Từ Viết Tắt (`report-datn/frontmatter/danh_muc_viet_tat.tex`)
- Bổ sung / chuẩn hóa định nghĩa:
  - `BYOK` & `Bring Your Own Key -- Mô hình quản lý khóa bảo mật do người dùng tự cung cấp`
  - `AES-GCM` & `Advanced Encryption Standard -- Galois/Counter Mode -- Chuẩn mã hóa xác thực khóa API BYOK`

---

## 4. Kế Hoạch Xác Minh (Verification Plan)

1. **Biên dịch XeLaTeX:** Thực thi biên dịch 2 lần để cập nhật toàn bộ Mục lục (`main.toc`), tệp phụ trợ (`main.aux`), và xuất ra [`report-datn/main.pdf`](../../../report-datn/main.pdf).
2. **Kiểm tra trực quan Mục lục:** Trích xuất và render trang chứa Mục lục (trang x hoặc xi) để kiểm tra dòng 2.5.3 và 2.5.4 hiển thị chuẩn xác, không bị tràn dòng, không còn chữ "Két an toàn" hay "hạt nhân".
3. **Quét tự động:** Chạy `grep` rà soát toàn bộ thư mục `report-datn/chapters/` để xác nhận số lượng xuất hiện của "Két an toàn", "két khóa", "cô lập hạt nhân" bằng **0**.
4. **Bốn Cổng Xác Minh:** Đảm bảo 100% exit code 0 cho `ruff`, `pytest`, `npm test`, `npm build` và `verify_thesis_format.py`.

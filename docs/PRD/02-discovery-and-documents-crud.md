# MODULE 02: KHÁM PHÁ ĐỀ TÀI (DISCOVERY) & QUẢN LÝ TÀI LIỆU PDF (DOCUMENTS CRUD)
# (FILE 02: TOPIC DISCOVERY & DOCUMENTS CRUD)

---

## 1. Mục Tiêu Module
Giúp người dùng bắt đầu nghiên cứu ngay cả khi chưa có sẵn file PDF trong máy (thông qua tìm kiếm chủ đề bằng Exa AI / Semantic Scholar / arXiv), đồng thời cung cấp đầy đủ các thao tác quản lý vòng đời file PDF (`Upload`, `Xem danh sách`, `Xem chi tiết/mục lục`, `Xóa`).

---

## 2. Bước Mở Đầu: Tìm & Mở Đọc Bài Báo Khi Chưa Có Sẵn File PDF (Zero-to-Reading)

### A. Điểm chạm giao diện (UI Entry Points)
Tính năng tìm kiếm bài báo theo chủ đề hoạt động đồng nhất tại **2 nơi**:
1. **Ô nhập trung tâm ở Màn hình chính (`DashboardHeroSection.tsx`):** Khi người dùng vừa mở ứng dụng (chưa chọn phiên đọc và chưa đính kèm file PDF), nếu gõ một chủ đề hoặc câu hỏi tìm bài báo vào ô nhập chính giữa màn hình.
2. **Trang Khám phá (`DiscoveryPage.tsx`):** Giao diện chuyên biệt để tìm kiếm bài báo mới.

### B. Luồng hoạt động chi tiết
1. Người dùng nhập chủ đề đang quan tâm bằng Tiếng Việt hoặc Tiếng Anh (ví dụ: *"Phát hiện gian lận thẻ tín dụng bằng Graph Neural Network"*).
2. Hệ thống truy vấn kết hợp qua **Exa AI**, **Semantic Scholar** và **arXiv** để trả về danh sách các bài báo khoa học sát nhất.
3. Mỗi thẻ kết quả bài báo hiển thị rõ:
   * **Tiêu đề bài báo**, **Tác giả**, **Năm xuất bản**, **Mã DOI / arXiv ID**.
   * **Tóm tắt ngắn (Abstract / Highlights)**.
   * Nhãn trạng thái: **`[🟢 Có sẵn PDF Open Access]`** (hoặc `[🟡 Chỉ có Tóm tắt]` nếu bài bị khóa thu phí).
4. Khi người dùng bấm nút **`[📖 Mở đọc ngay]`** trên một bài báo có sẵn PDF:
   * Hệ thống tự động tải file PDF về máy chủ, tạo mới một Phiên đọc (`ResearchSession`) và chuyển thẳng người dùng vào màn hình Đọc sâu (Module 03) mà không cần tải thủ công về máy tính.

---

## 3. Quản Lý Tài Liệu PDF — Đầy Đủ Thao Tác CRUD (`documents`)

### A. Tải lên & Bóc tách Tài liệu (`Create / Ingest`)
1. **Upload file PDF từ máy tính (`POST /api/v1/documents`):**
   * Cho phép kéo thả hoặc chọn file PDF từ máy tính (tối đa `50 MB`, tối đa `100 trang`).
   * Kiểm tra tính hợp lệ: phải là file PDF chuẩn có lớp văn bản (Digital PDF), không nhận file ảnh scan trống chữ.
   * **Chống lưu trùng lặp (CAS Deduplication):** Tính mã băm `SHA-256` (`content_hash`) của file PDF để tái sử dụng blob vật lý trong `storage/blobs/` nếu file đã tồn tại.
2. **Bóc tách cấu trúc & đoạn trích (`POST /api/v1/documents/{document_id}:parse`):**
   * Sử dụng `PyMuPDF` (`fitz`) bóc tách bài báo thành:
     * **Cấu trúc mục lục (`DocumentStructure`):** Tiêu đề bài báo, Abstract, danh sách các mục lớn/nhỏ (`Sections`) kèm số trang.
     * **Các khối văn bản (`DocumentChunk`):** Sắp xếp chuẩn thứ tự đọc 2 cột (trái sang phải, trên xuống dưới), nối các câu bị ngắt dòng, lưu kèm số trang (`page_number`), tọa độ khung viền (`bounding_boxes: [x0, y0, x1, y1, page]`) và vector nhúng (`embedding`).

### B. Xem Danh sách, Chi tiết & Trạng thái Tài liệu (`Read`)
1. **Xem danh sách tài liệu của tôi (`GET /api/v1/documents`):**
   * Hỗ trợ phân trang (`page`, `per_page`), tìm kiếm theo tên bài/tác giả (`search`), lọc theo thư mục (`folder_id`) hoặc trạng thái yêu thích (`starred`).
2. **Xem thông tin chi tiết & tiến độ xử lý (`GET /api/v1/documents/{document_id}`, `GET /api/v1/documents/{document_id}/status`):**
   * Trả về metadata (Tiêu đề, Tác giả, Năm, DOI, Số trang, Số chunks) và tiến độ bóc tách (`stage`, `progress: 0..100%`).
3. **Đọc luồng dữ liệu file PDF gốc (`GET /api/v1/documents/{document_id}/file`):**
   * Phục vụ trình đọc `PdfCanvasViewer.tsx` hiển thị trang PDF trên trình duyệt.
4. **Xem mục lục, đoạn trích & bản tóm tắt bài báo:**
   * `GET /api/v1/documents/{document_id}/structure`: Lấy cây mục lục bài báo.
   * `GET /api/v1/documents/{document_id}/chunks`: Lấy danh sách các đoạn trích và tọa độ Bounding Box.
   * `GET /api/v1/documents/{document_id}/summary` & `POST /api/v1/documents/{document_id}/summary:generate` (hoặc `:stream`): Xem và tạo bản tóm tắt tổng quan có gắn trích dẫn của bài báo.

### C. Xóa Tài liệu (`Delete`)
1. **Xóa bài báo (`DELETE /api/v1/documents/{document_id}`):**
   * Xóa bài báo khỏi danh sách của người dùng (kèm xóa cascade các `document_chunks`, `reference_items`, `notes`, `graph_nodes` gắn với bài báo đó).
   * Tự động gỡ bài báo khỏi thanh Tab PDF của mọi phiên đọc đang mở (`session_documents` `ON DELETE CASCADE`) để không bao giờ để lại Tab PDF trống hoặc lỗi 404.
   * Hiển thị hộp thoại xác nhận trước khi xóa để tránh bấm nhầm.

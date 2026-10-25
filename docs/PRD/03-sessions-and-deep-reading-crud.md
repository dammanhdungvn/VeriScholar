# MODULE 03: QUẢN LÝ PHIÊN ĐỌC (SESSION CRUD), ĐỌC SÂU PDF & HỎI ĐÁP RAG BOUNDING BOX
# (FILE 03: SESSIONS CRUD, PDF READER, RAG CHAT & NOTES CRUD)

---

## 1. Mục Tiêu Module
Cung cấp không gian làm việc trung tâm gồm **Khung đọc PDF gốc bên trái** và **Khung Chat AI Sư phạm bên phải**, đi kèm đầy đủ các thao tác quản lý Phiên đọc (`Session CRUD`), quản lý các Tab bài báo trong phiên (`tối đa 5 bài`), quản lý Lịch sử tin nhắn (`Chat CRUD`) và Sổ tay ghi chú (`Notes CRUD`).

> **Lưu ý phạm vi MVP:** Khung đọc bên trái chỉ hiển thị **Bản gốc PDF (`PdfCanvasViewer.tsx`)** (không làm chế độ hiển thị toàn văn PDF/HTML Tiếng Việt trong MVP). Mọi nhu cầu dịch đoạn khó hoặc giải thích khái niệm bằng Tiếng Việt được thực hiện trực tiếp qua khung Chat AI bên phải.

---

## 2. Quản Lý Phiên Đọc — Đầy Đủ Thao Tác CRUD (`research_sessions`)

Trên thanh điều hướng bên trái (Sidebar), người dùng quản lý toàn bộ các phiên học/đọc bài báo của mình:
1. **Tạo phiên đọc mới (`POST /api/v1/sessions`):**
   * Tự động tạo khi người dùng tải lên một file PDF mới, bấm `[📖 Mở đọc ngay]` từ màn hình Discovery, hoặc bấm nút `[➕ Phiên nghiên cứu mới]`.
2. **Xem danh sách & Chi tiết phiên đọc (`GET /api/v1/sessions`, `GET /api/v1/sessions/{id}`):**
   * Hiển thị danh sách các phiên đọc sắp xếp theo thời gian cập nhật gần nhất, có ô tìm kiếm tên phiên và bộ lọc xem các phiên đã lưu trữ (`is_archived`).
3. **Đổi tên phiên & Lưu trữ / Khôi phục (`PATCH /api/v1/sessions/{id}`, `POST /api/v1/sessions/{id}:restore-archived`):**
   * Cho phép đổi tên phiên đọc (ví dụ: *"Đọc hiểu kiến trúc Transformer"*).
   * Cho phép Lưu trữ (Archive) phiên đã học xong để gọn danh sách, và Khôi phục lại bất kỳ lúc nào.
4. **Lưu trạng thái khung đọc (`PATCH /api/v1/sessions/{id}/viewport`):**
   * Tự động ghi nhớ bài báo đang mở (`active_document_id`), số trang đang đọc (`page`), và tỷ lệ phóng to (`zoom_ratio`) để khi mở lại phiên đọc vẫn ở đúng vị trí cũ.
5. **Xóa vĩnh viễn phiên đọc (`DELETE /api/v1/sessions/{id}`):**
   * Xóa phiên đọc và toàn bộ lịch sử tin nhắn trong phiên đó (có hộp thoại xác nhận trước khi xóa; các file PDF gốc trong Kho vẫn được giữ an toàn).

---

## 3. Quản Lý Thanh Tab Bài Báo Trong Phiên (`session_documents` — Tối Đa 5 Bài)

Một phiên đọc cho phép mở và đối chiếu đồng thời **tối đa 5 bài báo** trên Thanh Tab PDF (`DocumentTabBar.tsx`):
1. **Thêm bài báo vào phiên (`POST /api/v1/sessions/{id}/documents`):**
   * Thêm bài báo từ danh sách tài liệu đã tải hoặc từ Bảng Context 3 Cột (Module 04) vào phiên hiện tại.
   * Nếu phiên đã đủ `5/5 bài báo`, hệ thống chặn thêm mới và thông báo rõ: *"Phiên đọc chỉ hỗ trợ tối đa 5 bài báo cùng lúc để đảm bảo độ chính xác của AI. Vui lòng đóng bớt 1 bài báo trước khi thêm mới."*
2. **Chuyển đổi Tab bài báo:**
   * Bấm vào Tab bài báo nào trên `DocumentTabBar`, khung PDF bên trái hiển thị ngay bài báo đó.
3. **Đóng / Gỡ 1 bài báo khỏi phiên (`DELETE /api/v1/sessions/{id}/documents/{document_id}`):**
   * Trên mỗi Tab bài báo (hoặc trong Bảng Context 3 Cột) có nút đóng `[✕]` / `[🗑️ Xóa khỏi chat]` để gỡ bài báo đó ra khỏi ngữ cảnh của phiên đọc hiện tại (giải phóng chỗ trống trong giới hạn 5 bài).

---

## 4. Trình Đọc PDF Gốc (`PdfCanvasViewer.tsx`) & Thanh Công Cụ Bôi Đen (`ScholarSelectionMenu.tsx`)

### A. Tính năng trên khung đọc PDF gốc
* Phóng to / Thu nhỏ (`50%` – `300%`), vừa khít chiều ngang trang, xoay trang, nhảy nhanh đến số trang bất kỳ.
* Bảng **Mục lục bài báo (`DocumentStructureSheet.tsx`)**: Bấm vào tên mục nào (ví dụ *3.2 Scaled Dot-Product Attention*) tự động cuộn PDF đến đúng trang đó.
* **Lớp vẽ Khung viền vàng (`BboxHighlightLayer.tsx`)**: Tô sáng chính xác vùng văn bản/bảng biểu theo tọa độ chuẩn hóa `[x0, y0, x1, y1, page]`.

### B. Thanh công cụ nổi khi bôi đen văn bản trên PDF (`ScholarSelectionMenu.tsx`)
Khi người dùng dùng chuột bôi đen bất kỳ đoạn văn hoặc công thức nào trên trang PDF, thanh menu nhỏ hiện ra ngay bên trên với **3 nút thao tác nhanh**:
1. **`[💬 Đưa vào Chat]`**: Đính kèm đoạn văn vừa bôi đen (kèm số trang) vào ô nhập Chat bên phải để người dùng yêu cầu AI dịch sang Tiếng Việt hoặc giải thích chi tiết đoạn đó.
2. **`[📝 Vào sổ tay]`**: Mở hộp lưu đoạn trích đó (kèm tọa độ Bounding Box và số trang) vào Sổ tay ghi chú cá nhân.
3. **`[📋 Trích dẫn]`**: Sao chép nhanh đoạn văn kèm trích dẫn `[Tên bài báo, Trang X]` vào Clipboard.

---

## 5. Hỏi Đáp Học Sâu Qua RAG Chuyên Biệt & Quản Lý Lịch Sử Chat (`session_messages`)

### A. CRUD Lịch sử Hội thoại trong Phiên
1. **Xem lịch sử tin nhắn (`GET /api/v1/sessions/{id}/messages`):** Tải toàn bộ các lượt hỏi đáp trước đó của phiên đọc.
2. **Gửi câu hỏi & Nhận phản hồi Streaming SSE (`POST /api/v1/sessions/{id}/messages`):**
   * Trả lời bằng Tiếng Việt rõ ràng, mạch lạc, hiển thị công thức toán chuẩn LaTeX qua KaTeX.
   * Có nút **`[⏹️ Dừng trả lời]` (`Stop Generation`)** nếu người dùng muốn ngắt câu trả lời giữa chừng.
3. **Làm mới / Xóa lịch sử đoạn chat (`DELETE /api/v1/sessions/{id}/messages`):**
   * Nút **`[🔄 Làm mới đoạn chat]` (`Reset Chat`)** giúp xóa sạch các tin nhắn cũ trong phiên để hỏi lại từ đầu mà không phải tạo phiên mới.

### B. Cơ chế Phối hợp AI Knowledge & RAG Chống Ảo Giác (Visual Grounding)
* **AI Knowledge (Kiến thức nền của mô hình):** Dùng để giải thích trực quan ý nghĩa toán học của các ký hiệu, công thức và bối cảnh thuật toán bằng ngôn ngữ dễ hiểu như một người hướng dẫn.
* **RAG Grounding (Bám sát tài liệu gốc):** Mọi con số thực nghiệm, tên bộ dữ liệu, cấu hình siêu tham số và kết luận của tác giả bắt buộc trích xuất từ `document_chunks` của các bài báo đang mở trong phiên.
* **Huy hiệu Bounding Box Bấm-Để-Kiểm-Chứng:**
  * Cuối mỗi luận điểm hoặc số liệu thực nghiệm trong câu trả lời của AI đều gắn huy hiệu **`[📄 Tên bài • Trang X]`**.
  * Khi người dùng bấm vào huy hiệu này: Khung đọc PDF bên trái tự động chuyển sang đúng Tab bài báo đó, cuộn mượt tới Trang X và **vẽ khung viền màu vàng (`Bounding Box`)** bao quanh đúng đoạn văn gốc để người dùng kiểm chứng bằng mắt thường trong 1 giây.

---

## 6. Sổ Tay Ghi Chú Nghiên Cứu — Đầy Đủ Thao Tác CRUD (`notes`)

Người dùng có thể mở ngăn **Sổ tay (`NotesPanelContainer.tsx`)** ngay trong phiên đọc để quản lý các ý tưởng và đoạn trích quan trọng:
1. **Tạo ghi chú mới (`POST /api/v1/notes`):** Lưu tiêu đề, nội dung ghi chú, thẻ phân loại (`tags`), liên kết với `document_id`, `page_number` và tọa độ `bounding_box` trên trang PDF.
2. **Xem danh sách & Chi tiết ghi chú (`GET /api/v1/notes`, `GET /api/v1/notes/{id}`):** Lọc ghi chú theo bài báo hiện tại, tìm kiếm theo từ khóa hoặc thẻ tag. Bấm vào ghi chú có gắn tọa độ sẽ cuộn trang PDF về đúng vị trí Bounding Box đó.
3. **Chỉnh sửa ghi chú (`PATCH /api/v1/notes/{id}`):** Sửa tiêu đề, nội dung hoặc thẻ tag của ghi chú.
4. **Xóa ghi chú (`DELETE /api/v1/notes/{id}`):** Xóa ghi chú không còn cần thiết.

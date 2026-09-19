# Kế Hoạch Thiết Kế Kỹ Thuật: POST /api/v1/sessions/{id}:export-bundle

> **Mã tính năng**: `FEAT-M1-API-POST-SESSION-EXPORT-BUNDLE`  
> **Endpoint**: `POST /api/v1/sessions/{id}:export-bundle`  
> **STT API PRD**: `#56. Xuất Gói Nghiên Cứu Ngoại Tuyến Trọn Gói (Full Offline Research Bundle .zip)`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: Google AIP-136 (Custom Methods), RFC 9110 (HTTP Semantics), ZIP File Format Specification (PKWARE / ISO 21320-1), Self-Contained Offline Knowledge Bundle, Multi-Tenancy & Zero Data Leakage.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Một tính năng trọng tâm của VeriScholar là hỗ trợ nghiên cứu ngoại tuyến (Offline Research) cho các nhà khoa học khi làm việc tại những khu vực hạn chế kết nối internet (trên máy bay, thực địa, phòng thí nghiệm kín).

Endpoint `POST /api/v1/sessions/{id}:export-bundle` đảm nhiệm vai trò đóng gói toàn bộ tài sản nghiên cứu phát sinh trong phiên thành một tệp nén ZIP độc lập duy nhất (`application/zip`), bao gồm:
1. **Thư mục tài liệu gốc (`documents/`)**:
   - Toàn bộ các bài báo khoa học PDF đã nạp vào phiên.
   - Các tệp PDF được bảo lưu cấu trúc chuẩn `%PDF-1.4`, sẵn sàng để tra cứu trực tiếp bằng bất kỳ phần mềm đọc PDF ngoại tuyến nào (Acrobat, Preview, PDF.js).
2. **Bài học tổng hợp tri thức (`master_lesson.md`)**:
   - Tệp Markdown hoàn chỉnh chứa YAML frontmatter ghi nhận metadata phiên: `session_id`, `title`, `exported_at`, `documents_count`, `turns_count`.
   - Cấu trúc 3 phần rõ ràng: Danh mục tài liệu trong phiên, Các luận điểm nghiên cứu & đối thoại theo từng câu hỏi Q&A, và Phần bản quyền/trích dẫn.
3. **Trình đọc lịch sử đối thoại độc lập (`chat_transcript.html`)**:
   - Bảng tra cứu lịch sử hội thoại tự chứa (self-contained HTML card viewer) tích hợp style CSS hiện đại.
   - Hiển thị từng cặp câu hỏi (User Q) và phản hồi của VeriScholar kèm trích dẫn đối sánh mà không cần kết nối mạng hay tải thêm tài nguyên bên ngoài.

---

## 2. 6 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **ZIP MIME Type & Content-Disposition Invariant**:
   - Phản hồi thành công bắt buộc phải có `Content-Type: application/zip` và header `Content-Disposition: attachment; filename="verischolar_session_{id}.zip"`.
2. **ZIP Internal Structure Integrity Invariant**:
   - Tệp ZIP phải hợp lệ (không bị hỏng cấu trúc PKWARE `PK\x03\x04`).
   - Phải chứa đầy đủ 2 tệp cốt lõi: `master_lesson.md` và `chat_transcript.html`.
   - Nếu phiên có tài liệu, các tệp PDF phải nằm trong thư mục con `documents/`.
3. **Master Lesson Content & Metadata Invariant**:
   - Tệp `master_lesson.md` bên trong gói ZIP phải có YAML frontmatter hợp lệ chứa `session_id` chính xác của phiên và phản ánh đúng số lượng câu hỏi/tài liệu.
4. **Multi-Tenant Shielding (Zero Data Exfiltration)**:
   - Người dùng lạ (Alien Tenant) cố tình xuất gói tài nguyên của phiên thuộc quyền sở hữu của người khác sẽ bị từ chối với mã `HTTP 404 Not Found` (`SESSION_NOT_FOUND`), bảo đảm tuyệt đối không rò rỉ dữ liệu hoặc mã nhị phân tài liệu của người khác.
5. **Non-Existent Session Guard**:
   - Khi gọi lệnh xuất bundle với session UUID không tồn tại trên hệ thống, phản hồi trả về bắt buộc phải là `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
6. **UUID Format Validation Guard**:
   - Định danh `id` trên đường dẫn nếu sai định dạng UUIDv4 (RFC 4122) phải bị chặn tại tầng schema validation với mã `HTTP 422 Unprocessable Content`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `POST`
- **Route**: `/api/v1/sessions/{id}:export-bundle`
- **Headers**:
  - `Authorization`: `Bearer <token>`
- **Status Code Thành Công**: `HTTP 200 OK`

### 3.2. Response Headers
- `Content-Type`: `application/zip`
- `Content-Disposition`: `attachment; filename="verischolar_session_{id}.zip"`
- `Content-Length`: `<kích_thước_tính_bằng_bytes>`

### 3.3. Cấu Trúc Gói Tệp ZIP (`verischolar_session_{id}.zip`)
```text
verischolar_session_{id}.zip
├── documents/
│   ├── attention_is_all_you_need.pdf
│   └── bert_pretraining.pdf
├── master_lesson.md
└── chat_transcript.html
```

### 3.4. Error Responses
- **`404 Not Found`**:
  ```json
  {
    "detail": {
      "code": "SESSION_NOT_FOUND",
      "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
      "action": "Verify session ID."
    }
  }
  ```
- **`422 Unprocessable Content`**: Mã lỗi validation của FastAPI khi `id` không phải UUID.

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`post_session_export_bundle.py`)

| STT | Kịch Bản Kiểm Thử | Hành Động & Tham Số | HTTP Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Active Bundle Export & MIME Invariant** | Xuất bundle từ phiên có đủ tài liệu và hội thoại | `200 OK` | Header `Content-Type: application/zip`, `Content-Disposition` có filename chuẩn |
| **02** | **ZIP Archive Structural Verification** | Đọc dữ liệu nhị phân vào `zipfile.ZipFile` và đọc danh sách tệp | `200 OK` | `ZipFile.testzip() is None`, tồn tại `master_lesson.md` và `chat_transcript.html` |
| **03** | **Master Lesson Markdown & Metadata Integrity** | Đọc nội dung `master_lesson.md` trong ZIP | `200 OK` | Chứa YAML frontmatter với đúng `session_id`, tiêu đề phiên và nội dung Q&A |
| **04** | **Multi-Tenant Isolation Guard** | Tenant lạ gửi request export bundle với session của user khác | `404 Not Found` | `code == "SESSION_NOT_FOUND"`, không lộ luồng nhị phân |
| **05** | **Non-Existent Session Guard** | Export bundle với session UUID ngẫu nhiên | `404 Not Found` | `code == "SESSION_NOT_FOUND"` |
| **06** | **UUID Format Validation Guard** | Export bundle với `id="invalid-uuid-string"` | `422 Unprocessable` | Bị từ chối tại validation guard trước khi tạo luồng zip |

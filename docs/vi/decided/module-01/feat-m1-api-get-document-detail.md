# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Chi Tiết Bài Báo Khoa Học & Bố Cục Không Gian Trang (Document Detail)

* **Tên Branch:** `feat/m1-api-get-document-detail`
* **API Endpoint:** `GET /api/v1/documents/{id}`
* **Mã Phản Hồi:** `200 OK`
* **Loại Endpoint:** Standard REST Entity Endpoint (Detail Resource)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.5: API Lấy thông tin chi tiết bài báo khoa học)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, các trường `title`, `authors`, `doi`, `publication_year`, `total_pages`, `parsed_metadata`)
  - [`docs/vi/techstack-backend-module-01.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/techstack-backend-module-01.md) (Quy chuẩn kích thước trang và tọa độ Bounding Box)
  - [`AGENTS.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md) (SingleResponseEnvelope chuẩn)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Khi người dùng mở một bài báo khoa học trên giao diện đọc sâu (Deep Reader), ứng dụng web cần đầy đủ hai nhóm thông tin thiết yếu:
1. **Thông tin thư mục học thuật (Scholarly Bibliographic Metadata):** Tiêu đề bài báo, danh sách tác giả, DOI, năm xuất bản, tạp chí/hội nghị, và tóm tắt (abstract).
2. **Metadata không gian trang (Spatial Page Geometry Metadata):** Tổng số trang, kích thước chiều rộng (`width`), chiều cao (`height`), độ phân giải (`dpi`), và góc xoay (`rotation`) của từng trang trong tệp PDF.
Nếu thiếu thông số không gian trang, trình đọc PDF Canvas trên web sẽ không thể tính toán tỉ lệ hiển thị (aspect ratio) và vẽ các hộp bao viền đối chiếu trích dẫn (evidence bounding boxes) chính xác với tọa độ gốc của tài liệu.

### 1.2 Quyết định kiến trúc (Decisions)
1. **Cung Cấp Siêu Dữ Liệu Trang Linh Hoạt (`pages_metadata`):**
   - Lưu trữ dạng mảng các đối tượng trang bên trong cột JSONB `parsed_metadata["pages"]` của bảng `documents`.
   - Mỗi phần tử trang bao gồm: `page_number` (1-indexed), `width` (pt), `height` (pt), `dpi` (mặc định 72.0 cho PDF chuẩn), `rotation` (0, 90, 180, 270).
   - Thiết kế tương thích ngược linh hoạt: Hỗ trợ cả định dạng danh sách `list[dict]` và định dạng từ điển theo số trang `dict[str, dict]`. Nếu tài liệu chưa hoàn tất bóc tách hoặc chưa có metadata, trả về mảng rỗng `[]` thay vì gây lỗi sập endpoint.
2. **Định Danh & Trạng Thái Lưu Trữ:**
   - Trả về cờ `is_persistent` để client biết tài liệu đang là tệp tạm thời (trong phiên làm việc ngắn hạn) hay đã được người dùng lưu trữ vĩnh viễn vào thư viện cá nhân (`starred`).
   - Cung cấp `folder_id` để biết tài liệu đang thuộc thư mục chuyên đề nào.
3. **Bảo Mật Đa Người Dùng:**
   - Luôn truy vấn theo `(id == document_id AND user_id == current_user.id)`.
   - Ngăn chặn triệt để hành vi quét ID (enumeration attack); trả về `404 DOCUMENT_NOT_FOUND` nếu không thuộc quyền sở hữu.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-get-document-detail`.

### Bước 2: Thiết Kế Pydantic Schemas
Trong `apps/api/src/api/schemas/document.py`:
1. `PageGeometryMetadata`:
   - `page_number: int`
   - `width: float`
   - `height: float`
   - `dpi: float = 72.0`
   - `rotation: int = 0`
2. `DocumentDetailResponseData`:
   - `id: UUID`
   - `filename: str`
   - `file_size_bytes: int`
   - `content_hash: str`
   - `title: str | None`
   - `authors: list[str] | None`
   - `doi: str | None`
   - `publication_year: int | None`
   - `total_pages: int | None`
   - `status: str`
   - `is_persistent: bool`
   - `folder_id: UUID | None`
   - `created_at: datetime`
   - `updated_at: datetime`
   - `pages: list[PageGeometryMetadata]`
   - `links: DocumentDetailLinks` (`file_url`, `status_url`, `self_url`)
3. `DocumentDetailEnvelope`:
   - Kế thừa `SingleResponseEnvelope[DocumentDetailResponseData]`.

### Bước 3: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `get_document_detail(document_id: UUID, user_id: UUID, db: AsyncSession) -> DocumentDetailResponseData`:
   - Truy vấn `DocumentModel` theo `id` và `user_id`.
   - Nếu không tìm thấy: Raise `HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND", ...})`.
   - Chuẩn hóa trường `pages`: Đọc từ `parsed_metadata.get("pages")`. Xử lý an toàn cả trường hợp None, dictionary hoặc list rỗng.
   - Chuyển đổi danh sách tác giả `authors`: Đảm bảo là danh sách chuỗi ký tự chuẩn.
   - Trả về `DocumentDetailResponseData`.

### Bước 4: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.get("/{document_id}", response_model=DocumentDetailEnvelope)`
2. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Lấy thông tin chi tiết của bài báo khoa học bao gồm thông tin thư mục và metadata không gian từng trang.
   - **Đầu vào:** `document_id: UUID` (Path parameter).
   - **Đầu ra:** HTTP `200 OK` chứa đầy đủ thông tin bài báo, danh sách trang và liên kết HATEOAS.
   - **Lưu ý:** Cô lập theo `user_id`; trả về 404 nếu không tìm thấy bài báo.

### Bước 5: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_detail.py`.
   - Các ca kiểm thử bao phủ:
     - Lấy chi tiết tài liệu thành công với đầy đủ metadata và thông số trang `pages`.
     - Xử lý tương thích khi `pages` lưu dạng dictionary theo số trang thay vì list.
     - Xử lý khi tài liệu chưa có `pages_metadata` trả về mảng rỗng `[]`.
     - Trả về `404 DOCUMENT_NOT_FOUND` khi `document_id` không tồn tại.
     - Cô lập multi-tenant: User B không thể xem chi tiết tài liệu của User A.
     - Xử lý UUID sai định dạng trả về mã `422 Unprocessable Entity`.
     - Kiểm tra endpoint xuất hiện trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy kiểm thử tự động toàn diện qua `apps/api/tests/run_all_api_tests.py`.

### Bước 6: Quy Trình Hoàn Tất
1. Commit code: `[api] feat: implement GET /api/v1/documents/{id} with spatial metadata and autotests`.
2. Cập nhật tài liệu offline tại `docs/vi/swagger.md` (uncommitted) để user review.

# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Bóc Tách Danh Mục Tài Liệu Tham Khảo (Document Reference Extraction API)

* **Tên Branch:** `feat/m1-api-extract-references`
* **API Endpoint:** `POST /api/v1/documents/{id}:extract-references`
* **Mã Phản Hồi:** `200 OK`
* **Loại Endpoint:** Custom Action Method Endpoint (Google AIP-136 Standard)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.9: `POST /api/v1/documents/{id}:extract-references`)
  - [`docs/vi/design-database.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-database.md) (Mục 3.6: Bảng `reference_items` và các chỉ mục DDL)
  - [`docs/vi/design-architecture.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-architecture.md) (Mục 3.1 & 3.3: Khai thác trích dẫn & Hexagonal Architecture)
  - [`docs/vi/PRD.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/PRD.md) (Module 1 & Module 3: Khai thác tài liệu tham khảo và đồ thị tri thức)
  - [`.agents/skills/regex-vs-llm-structured-text/SKILL.md`](file:///home/VeriScholar/Workspace/VeriScholar/.agents/skills/regex-vs-llm-structured-text/SKILL.md) (Kiến trúc phân tích cú pháp kết hợp Regex Fast-Path)
  - [`AGENTS.md`](file:///home/VeriScholar/Workspace/VeriScholar/AGENTS.md) (Quy chuẩn code sạch, kiểm thử độc lập và quản lý tiến trình)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decisions)

### 1.1 Bài toán nghiệp vụ
Sau khi bài báo PDF được bóc tách và phân đoạn nội dung (Chunking), người dùng cần tra cứu toàn bộ danh mục tài liệu tham khảo (References / Bibliography) để:
1. Xem danh sách các công trình tiền nhiệm được trích dẫn trong bài báo.
2. Trích xuất chính xác các trường siêu dữ liệu học thuật: Tiêu đề bài báo (`title`), Tác giả (`authors`), Năm xuất bản (`year`), Định danh số arXiv (`arxiv_id`), và Định danh đối tượng kỹ thuật số (`doi`).
3. Chuẩn bị dữ liệu cho Module 3 (Batch Resolving qua Crossref / Semantic Scholar và dựng Đồ thị Tri thức Trích dẫn - Citation Graph).

### 1.2 Quyết định kiến trúc cốt lõi

1. **Chuẩn Hóa Google AIP-136 Custom Method:**
   - Sử dụng định dạng URI chuẩn hóa: `POST /api/v1/documents/{id}:extract-references`.
   - Trả về mã phản hồi `200 OK` kèm `SingleResponseEnvelope[DocumentExtractReferencesResponseData]`.
   - Hỗ trợ tham số tùy chọn trong request body: `{"force_reextract": false}` để điều khiển việc tái bóc tách hoặc tận dụng bộ nhớ đệm cơ sở dữ liệu.

2. **Mô Hình Cơ Sở Dữ Liệu `reference_items` (PostgreSQL 18 DDL Alignment):**
   - Triển khai SQLAlchemy Model `ReferenceItemModel` tại `apps/api/src/api/db/models/reference.py`:
     - `id`: UUID PRIMARY KEY (gen_random_uuid).
     - `document_id`: UUID NOT NULL REFERENCES `documents(id)` ON DELETE CASCADE.
     - `ref_index`: INT NOT NULL CHECK (`ref_index >= 1`).
     - `raw_text`: TEXT NOT NULL (toàn văn đoạn trích dẫn gốc).
     - `parsed_title`: TEXT NULL (tiêu đề bài báo được bóc tách).
     - `parsed_authors`: JSONType NULL (danh sách tác giả dạng chuỗi).
     - `parsed_year`: INT NULL (năm xuất bản, ví dụ 2016).
     - `doi`: VARCHAR(255) NULL (mã DOI chuẩn).
     - `arxiv_id`: VARCHAR(50) NULL (ví dụ: `1607.06450`).
     - `resolved_document_id`: UUID NULL REFERENCES `documents(id)` ON DELETE SET NULL (liên kết chéo nếu bài báo đã có sẵn trong kho hệ thống).
     - `created_at`: TIMESTAMPTZ NOT NULL DEFAULT NOW().
     - Ràng buộc bất biến: `UNIQUE (document_id, ref_index)`.
     - Chỉ mục hiệu năng cao: `idx_reference_items_doc`, `idx_reference_items_doi`, `idx_reference_items_arxiv`.

3. **Cơ Chế Bộ Đệm Cơ Sở Dữ Liệu & Idempotency (Database Caching Pattern):**
   - Khi API được gọi:
     - Kiểm tra trong bảng `reference_items` xem tài liệu này đã được bóc tách tham khảo trước đó chưa.
     - Nếu đã có và `not force_reextract`: Trả về ngay danh sách tham khảo từ database (đáp ứng SLA dưới 15ms, không tốn tài nguyên I/O đọc PDF).
     - Nếu chưa có hoặc `force_reextract == true`: Đọc blob PDF từ `IStoragePort`, trích xuất văn bản mục References, phân tích cú pháp, xóa dữ liệu cũ trong transaction và ghi lại toàn bộ danh mục mới.

4. **Thuật Toán Bóc Tách Kết Hợp Regex Fast-Path (Theo Skill `regex-vs-llm-structured-text`):**
   - **Giai đoạn 1 (Định vị phân vùng References):**
     - Quét từ các trang cuối của tài liệu (khoảng 30% số trang cuối cùng) để tìm tiêu đề mục tham khảo:
       `(?im)^\s*(?:\[\d+\]\s*)?(?:references|bibliography|works\s+cited|literature\s+cited)\s*$`
   - **Giai đoạn 2 (Tách các khối tham khảo riêng biệt - Block Segmentation):**
     - Dạng số trong ngoặc vuông: `\[\d+\]\s+.+?(?=\[\d+\]|\Z)` (phổ biến trong IEEE, ACM, NeurIPS, ví dụ `[1] Jimmy Lei Ba... [2] Dzmitry Bahdanau...`).
     - Dạng số có dấu chấm: `^\s*\d+\.\s+.+?(?=^\s*\d+\.|\Z)`.
     - Dạng tác giả - năm: `\[?[A-Z][a-zA-Z\s]+(?:et\s+al\.?)?,\s*(?:19|20)\d{2}\]?`.
   - **Giai đoạn 3 (Phân tích cú pháp chi tiết từng khối - Field Extraction):**
     - `arxiv_id`: Regex `(?i)(?:arxiv[:\s]|abs/)?(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[a-z\-]+)?/\d{7})`.
     - `doi`: Regex `\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)`.
     - `year`: Regex `\b(19\d{2}|20\d{2})\b` (lấy năm hợp lệ nằm gần cuối chuỗi trích dẫn).
     - `authors` & `title`: Phân tích theo cấu trúc dấu câu chuẩn học thuật (Tác giả kết thúc trước dấu chấm phân cách với Tiêu đề).
   - **Giai đoạn 4 (Xử lý không đồng bộ an toàn - Non-blocking Execution):**
     - Quá trình đọc stream PDF và phân tích chuỗi regex CPU-bound được bao bọc an toàn trong `asyncio.to_thread()` để không làm block FastAPI event loop.

5. **Cách Ly Đa Người Dùng Tuyệt Đối (Multi-Tenant Isolation):**
   - Chỉ chủ sở hữu tài liệu (`document.user_id == current_user.id`) mới có quyền truy cập và kích hoạt bóc tách tham khảo.
   - Nếu tài liệu không thuộc về người dùng, hệ thống trả về mã lỗi `404 Not Found` (`DOCUMENT_NOT_FOUND`) theo chuẩn bảo mật chống rò rỉ ID.

---

## 2. Thiết Kế Hợp Đồng API (API Schema Specification)

### 2.1 Request Schema (`DocumentExtractReferencesRequest`)
```python
class DocumentExtractReferencesRequest(BaseModel):
    """Payload tuy chon cho endpoint trich xuat tai lieu tham khao."""

    model_config = ConfigDict(extra="forbid")

    force_reextract: bool = Field(
        default=False,
        description="Neu True, bo qua cache database va thuc hien boc tach lai tu file PDF",
    )
```

### 2.2 Response Schema (`DocumentExtractReferencesEnvelope`)
Theo đúng đặc tả trong `docs/vi/design-api.md` Mục 3.9:
```json
{
  "success": true,
  "data": {
    "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "total_extracted": 38,
    "references": [
      {
        "ref_index": 1,
        "raw_text": "Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.",
        "parsed": {
          "title": "Layer normalization",
          "authors": ["Jimmy Lei Ba", "Jamie Ryan Kiros", "Geoffrey E Hinton"],
          "year": 2016,
          "arxiv_id": "1607.06450",
          "doi": null
        }
      }
    ]
  },
  "meta": {
    "request_id": "req_01HP...",
    "timestamp": "2026-03-31T09:00:00Z"
  }
}
```

---

## 3. Kế Hoạch Triển Khai Từng Bước (Step-by-Step Implementation Tasks)

### Bước 1: Khởi tạo Git Branch
* Tạo và chuyển sang nhánh mới:
  ```bash
  git checkout -b feat/m1-api-extract-references
  ```

### Bước 2: Xây dựng Mô hình Cơ sở Dữ liệu (`ReferenceItemModel`)
* Tạo file `apps/api/src/api/db/models/reference.py`:
  - Định nghĩa `ReferenceItemModel` kế thừa `IdentifiableTimestampedModel`.
  - Khai báo foreign keys, unique constraint `(document_id, ref_index)`, và các chỉ mục `doi`, `arxiv_id`.
* Cập nhật `apps/api/src/api/db/models/__init__.py`:
  - Re-export `ReferenceItemModel`.

### Bước 3: Xây dựng Core Domain Entities & Regex Reference Extractor
* Tạo file `packages/core/src/core/domain/entities/reference.py`:
  - Dataclass `ParsedReference`: `title`, `authors`, `year`, `arxiv_id`, `doi`.
  - Dataclass `ReferenceItem`: `ref_index`, `raw_text`, `parsed`.
  - Hàm `extract_references_from_text(text: str) -> list[ReferenceItem]`: Thuật toán bóc tách regex mạnh mẽ, lọc sạch nhiễu và trích xuất trường học thuật.
* Kiểm thử unit test in-memory 100% trong `packages/core/tests/domain/test_reference_extraction.py`.

### Bước 4: Xây dựng Schemas & Service Layer
* Tạo schema trong `apps/api/src/api/schemas/document.py` (hoặc `apps/api/src/api/schemas/reference.py`):
  - `ParsedReferenceInfo`, `ReferenceItemResponse`, `DocumentExtractReferencesRequest`, `DocumentExtractReferencesResponseData`, `DocumentExtractReferencesEnvelope`.
* Bổ sung phương thức nghiệp vụ trong `apps/api/src/api/services/document_service.py`:
  - `extract_document_references(document_id, user_id, force_reextract, session)`:
    - Xác thực quyền sở hữu (multi-tenant isolation).
    - Kiểm tra cache cơ sở dữ liệu nếu không bật `force_reextract`.
    - Tải blob nhị phân từ `IStoragePort`.
    - Gọi trích xuất text và parser qua `asyncio.to_thread`.
    - Lưu các bản ghi vào `reference_items` trong transaction `async with session.begin():`.

### Bước 5: Đăng ký Endpoint API
* Cập nhật `apps/api/src/api/v1/endpoints/documents.py`:
  - Đăng ký route: `POST /{document_id}:extract-references`.
  - Dependency injection: `CurrentUserDep`, `AsyncSessionDep`, `DocumentServiceDep`.
  - Trả về mã `200 OK` kèm `DocumentExtractReferencesEnvelope`.

### Bước 6: Xây dựng Bộ Autotest Đạt Đủ 2 Điều Kiện Bắt Buộc
1. **Điều kiện 1 (Autotest riêng biệt của API):**
   - Tạo file `apps/api/tests/test_documents_extract_references.py` gồm các kịch bản:
     - `test_extract_references_success_from_stored_pdf`: Trích xuất thành công từ tài liệu PDF mẫu (có cả `arxiv_id`, `year`, `authors`, `title`).
     - `test_extract_references_idempotent_database_cache`: Lần gọi thứ 2 trả về ngay dữ liệu từ database cache mà không cần đọc lại storage.
     - `test_extract_references_force_reextract_overwrites_cache`: Khi `force_reextract=true`, hệ thống làm mới và cập nhật lại danh mục tham khảo trong DB.
     - `test_extract_references_pdf_without_references_returns_empty`: Xử lý mượt mà tài liệu không có mục References (trả về `total_extracted: 0`, danh sách rỗng).
     - `test_extract_references_multi_tenant_isolation`: Người dùng khác không thể xem/trích xuất tài liệu của người khác (`404 DOCUMENT_NOT_FOUND`).
     - `test_extract_references_not_found`: Trả về `404` khi ID tài liệu không tồn tại.
     - `test_extract_references_invalid_uuid`: Trả về `400` khi UUID sai định dạng.
     - `test_openapi_schema_contains_extract_references_endpoint`: Kiểm tra OpenAPI / Swagger schema phản ánh chính xác endpoint.
2. **Điều kiện 2 (Master Autotest Runner Toàn Bộ API):**
   - Cập nhật file [`apps/api/tests/run_all_api_tests.py`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/tests/run_all_api_tests.py):
     - Đăng ký file `test_documents_extract_references.py` vào danh sách `TEST_MODULES`.
     - Chạy lệnh duy nhất `uv run python apps/api/tests/run_all_api_tests.py` để thực thi toàn bộ 10 bộ test của tất cả các endpoint Module 1 (đạt trên 100 tests pass đồng loạt).

### Bước 7: Kiểm Thử Với MCP Tools
* Kiểm thử Postman MCP: Bổ sung request `POST /api/v1/documents/{{document_id}}:extract-references` vào Postman Collection `VeriScholar - Module 1 Deep Reading & Parse APIs`.
* Kiểm tra chất lượng mã nguồn: `uv run ruff check .` và `uv run ruff format --check .`.
* Tắt toàn bộ tiến trình ngầm trước khi báo cáo.

---

## 4. Kế Hoạch Đánh Giá Rủi Ro & Biên Ngoại Lệ (Risk & Edge Cases)

| Rủi Ro / Ngoại Lệ | Mức Độ | Giải Pháp Phòng Ngừa |
| :--- | :---: | :--- |
| File PDF scan dạng ảnh không có text layer | Trung bình | Trả về `total_extracted: 0` an toàn kèm thông điệp hướng dẫn chạy OCR qua Parse API trước. |
| Mục References định dạng khác thường (Author-Year thay vì Numeric) | Thấp | Regex hỗ trợ fallback đa mẫu (Multiple Regex Fallbacks) nhận diện cả `[1]`, `1.`, và `Author, Year`. |
| Cạnh tranh ghi đồng thời nhiều request `extract-references` | Trung bình | Sử dụng ràng buộc cơ sở dữ liệu `UNIQUE (document_id, ref_index)` và xử lý `upsert` hoặc xóa ghi lại an toàn trong transaction. |
| Không đọc được PDF do Blob bị xóa trên đĩa | Thấp | Bắt lỗi `StorageFileNotFoundError` và trả về `404 FILE_NOT_FOUND`. |

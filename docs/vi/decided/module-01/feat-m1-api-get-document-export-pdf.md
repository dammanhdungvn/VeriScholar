# Kế Hoạch Kỹ Thuật: Xuất File PDF Kèm Native Annotations Chuẩn ISO (GET /api/v1/documents/{id}/export-pdf)

> **Mã tài liệu:** `FEAT-M1-API-15`  
> **Trạng thái:** `PLANNING / CHỜ PHÊ DUYỆT (CHƯA VIẾT CODE TRIỂN KHAI)`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 16/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-document-export-pdf`  
> **API Canonical:** `GET /api/v1/documents/{id}/export-pdf`  
> **Chuẩn thiết kế:** ISO 32000-1 / ISO 32000-2 (PDF Specification - Text Markup Annotations), RFC 7807 (Problem Details), RFC 6266 (Content-Disposition), Hexagonal Architecture.

---

## 1. Hiện Trạng & Đánh Giá Mức Độ Sẵn Sàng (Gap Analysis)

### 1.1. Những thành phần ĐÃ CÓ (Kế thừa từ Feature 1 đến Feature 14):
1. **Lưu trữ nhị phân Content-Addressable Storage (CAS):**
   - File PDF gốc được lưu trữ theo hàm băm `content_hash` trong `ILocalStoragePort` (`apps/storage/blobs/...`).
   - Phương thức `read_blob(content_hash)` trong `DocumentService` cho phép đọc toàn vẹn mảng byte PDF gốc.
2. **Dữ liệu Tóm tắt Bằng chứng Học thuật (3-Point Grounded Summary):**
   - Bảng `document_summaries` lưu trữ đầy đủ `problem_statement`, `problem_citations`, `contributions`, `contribution_citations`, `limitations`, `limitation_citations`.
   - Mỗi mảng trích dẫn `*_citations` lưu các Bounding Box chuẩn hóa 5 phần tử: `[x0, y0, x1, y1, page]` (với tọa độ $[0.0, 1.0]$ và trang 1-indexed).
3. **Thư viện xử lý PDF cốt lõi (PyMuPDF / fitz):**
   - `pymupdf>=1.28.2` đã được tích hợp trong `packages/core` và sẵn sàng hỗ trợ thao tác chèn Text Markup Annotations (`page.add_highlight_annot`, `annot.set_colors`, `annot.set_info`, `annot.update`).
4. **Kiểm soát Đa người dùng & Phân quyền (Tenant Isolation):**
   - Lớp `DocumentModel` liên kết chặt chẽ với `user_id`, bảo đảm người dùng chỉ có thể xuất tài liệu của chính mình.

### 1.2. Những thành phần CHƯA CÓ (Cần xây dựng trong Feature 15):
1. **Port & Adapter cho PDF Annotation (Hexagonal Clean Architecture):**
   - Chưa có Value Object `PdfAnnotation` và Interface `IPdfAnnotatorPort` trong `packages/core/src/core/ports/`.
   - Chưa có Adapter `PyMuPdfAnnotator` để thực hiện ánh xạ tọa độ chuẩn hóa $[0.0, 1.0]$ sang điểm ảnh PDF thực tế (Points) và nhúng Native ISO Highlights.
2. **Nghiệp vụ Xuất PDF trong Service (`DocumentService.export_annotated_pdf`):**
   - Chưa có phương thức xử lý kiểm tra trạng thái tài liệu, nạp bytes gốc từ storage, nạp tóm tắt/ghi chú, chuyển đổi tọa độ, gắn annotations và đóng gói stream nhị phân.
3. **Driving Adapter Endpoint (`GET /api/v1/documents/{id}/export-pdf`):**
   - Chưa có router endpoint trong `apps/api/src/api/v1/endpoints/documents.py`.
   - Cần hỗ trợ query parameter `include_highlights: bool = True`.
   - Cần trả về headers chuẩn: `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="..."`, `X-Annotation-Count: <int>`, `Cache-Control: private, no-transform`.
4. **Hệ thống Kiểm thử 2 cấp độ:**
   - Chưa có Unit/Integration tests: `apps/api/tests/test_documents_export_pdf.py`.
   - Chưa có Autotest Snapshot Runner: `scripts/eval/runners/get_documents_export_pdf.py`.
   - Chưa tích hợp runner vào `scripts/eval_api.py` và cập nhật tài liệu `swagger.md` + `design-api-eval-snapshots.md`.

---

## 2. Khảo Sát & Giải Pháp Của Cộng Đồng AI / PDF Engineering Thế Giới

### 2.1. Cách Các Hệ Thống Nghiên Cứu Hàng Đầu Giải Quyết (Zotero, Mendeley, SciSpace, Elicit):
* **Vấn đề cốt tử của "PDF In-Browser Canvas":** Nhiều hệ thống hiện đại chỉ hiển thị highlight trên giao diện web (dùng SVG hoặc Canvas DOM layer đè lên PDF.js). Khi người dùng nhấn nút "Tải PDF về máy", file tải về lại là file PDF trắng tinh không có bất kỳ highlight hay ghi chú nào!
* **Tiêu chuẩn công nghiệp (ISO 32000 Native Annotations):** Các phần mềm quản lý học thuật uy tín như Zotero 7 và Mendeley Reference Manager giải quyết bài toán này bằng cách nhúng **Native PDF Annotations** trực tiếp vào cây đối tượng đối xứng của tệp PDF (`/Annots` dictionary).
* **Trải nghiệm người dùng đa nền tảng:**
  - Khi mở bằng **Adobe Acrobat Reader**, **Foxit Reader**, **Apple Preview**, **GoodNotes**, hoặc **Chrome/Firefox PDF Viewer**, các đoạn trích dẫn được tô màu nổi bật.
  - Khi di chuột hoặc click vào vùng tô sáng, một **Popup Note / Comment** lập tức hiển thị giải thích chi tiết của AI hoặc ghi chú của người dùng.

### 2.2. Áp Dụng & Tinh Chỉnh (Customization) Cho VeriScholar:

```
VeriScholar Visual Grounding Bounding Boxes
[x0, y0, x1, y1, page] (Normalized 0.0 - 1.0)
                     │
                     ▼
Coordinate Transformation to Absolute PDF Points
rect = fitz.Rect(x0 * page_width, y0 * page_height, x1 * page_width, y1 * page_height)
                     │
                     ▼
ISO 32000-1 / ISO 32000-2 Text Markup Construction
annot = page.add_highlight_annot(rect)
                     │
                     ▼
Semantic Color-Coding & Rich Scholarly Metadata
├── Problem Statement : Coral / Red-Orange  (0.95, 0.40, 0.35)
├── Contributions     : Emerald / Green     (0.15, 0.75, 0.45)
├── Limitations       : Violet / Purple     (0.65, 0.35, 0.85)
└── Research Notes    : Cyan / Blue         (0.20, 0.60, 0.90)
                     │
                     ▼
annot.set_info(title="VeriScholar AI [{Dimension}]", content="{Rich Synthesis Text}")
annot.set_opacity(0.40)  <-- Giữ độ sắc nét của chữ gốc bên dưới highlight
                     │
                     ▼
Optimized PDF Byte Stream Serialization
doc.tobytes(garbage=3, deflate=True)  <-- Nén nhỏ file, dọn dẹp đối tượng rác
```

1. **Chuẩn hóa Tọa độ (Coordinate Math):**
   - Hệ tọa độ PDF gốc có gốc tọa độ $(0, 0)$ ở góc trên-trái trong PyMuPDF (`fitz`), đơn vị là Points ($1\text{ inch} = 72\text{ points}$).
   - Công thức quy đổi:
     $$\text{Rect}(x0 \cdot W, y0 \cdot H, x1 \cdot W, y1 \cdot H)$$
2. **Khắc phục Giới Hạn Tọa Độ Biên (Clamping Invariants):**
   - Tọa độ chuẩn hóa được ép biên chặt chẽ trong khoảng $[0.0, 1.0]$ và kiểm tra $x0 < x1, y0 < y1$ để ngăn ngừa lỗi dựng hình trên các trình đọc PDF cũ.
3. **Khả Năng Tương Thích Ngược & Tùy Chọn Linh Hoạt (`include_highlights`):**
   - Khi `include_highlights=false`: Trả về trực tiếp bản PDF gốc sạch sẽ mà không qua khâu xử lý nạp/ghi annotation, tối ưu hóa tốc độ tải về.
   - Khi `include_highlights=true` (mặc định): Nhúng toàn bộ AI Grounded Highlights có sẵn.

---

## 3. Rà Soát Biến Môi Trường (.env.example)

- **Nguyên tắc bảo mật:** TUYỆT ĐỐI KHÔNG ĐỌC FILE `.env`.
- **Đối chiếu `.env.example`:**
  - Tính năng `export-pdf` sử dụng hoàn toàn năng lực xử lý cục bộ thông qua thư viện `PyMuPDF` (đã có sẵn trong hệ thống) và đọc dữ liệu từ Storage CAS + Database.
  - **Không phát sinh bất kỳ biến môi trường mới nào.** Không cần bổ sung API key bên ngoài.

---

## 4. Phân Tích Rủi Ro & Đánh Đổi Kỹ Thuật (Risk Analysis & Trade-offs)

| Rủi ro kỹ thuật | Mức độ | Giải pháp kỹ thuật xử lý triệt để |
| :--- | :---: | :--- |
| **Rò rỉ bộ nhớ C-level (Memory Leak / Segfault) khi PyMuPDF mở nhiều stream** | **CAO** | Quản lý vòng đời tài liệu PDF bằng ngữ cảnh `with pymupdf.open(...) as doc:` hoặc gọi tường minh `doc.close()` trước khi trả kết quả, bảo đảm giải phóng 100% con trỏ bộ nhớ C của MuPDF. |
| **Phình to dung lượng tệp PDF khi thêm nhiều Annotations** | **TRUNG BÌNH** | Áp dụng tham số nén tối ưu khi xuất byte stream: `doc.tobytes(garbage=3, deflate=True)`. Điều này giúp loại bỏ đối tượng mồ côi (orphaned objects) và nén luồng nhị phân, kích thước tệp chỉ tăng không quá 1-2% so với bản gốc. |
| **Tài liệu chưa phân tích hoặc chưa có Tóm tắt 3 ý** | **THẤP** | Nếu `include_highlights=true` nhưng tài liệu chưa có tóm tắt trong `document_summaries`, hệ thống sẽ trả về file PDF gốc bình thường kèm header `X-Annotation-Count: 0` mà không gây lỗi hoặc bắt người dùng chờ sinh AI. |
| **Xung đột Header Tên tệp Tiếng Việt / Ký tự đặc biệt (RFC 6266)** | **TRUNG BÌNH** | Sử dụng mã hóa chuẩn `Content-Disposition: attachment; filename="{ascii_filename}.pdf"; filename*=UTF-8''{encoded_filename}.pdf` để mọi trình duyệt (Chrome, Safari, Firefox) đều tải về đúng tên file bài báo. |
| **Tấn công Đa người dùng (Multi-Tenant Data Leakage)** | **CAO** | Ràng buộc điều kiện truy vấn `WHERE id = :document_id AND user_id = :user_id`. Nếu không khớp, trả về ngay `404 DOCUMENT_NOT_FOUND`. |

---

## 5. Phân Rã Kiến Trúc Lục Giác (Hexagonal Architecture Decomposition)

```
apps/api/src/api/v1/endpoints/documents.py  <-- [Driving Adapter: GET /{id}/export-pdf]
               │
               ▼
apps/api/src/api/services/document_service.py <-- [Application Use Case: export_annotated_pdf]
         │                       │
         ▼                       ▼
core.ports.storage      core.ports.pdf_annotator <-- [Domain Ports]
(ILocalStoragePort)     (IPdfAnnotatorPort)
         │                       │
         ▼                       ▼
core.adapters.storage   api.adapters.pdf_annotator <-- [Driven Adapters: PyMuPdfAnnotator]
```

### 5.1. Tầng Database & Persistence (`apps/api/src/api/db/`):
- Không yêu cầu thay đổi DDL/migration mới.
- Tận dụng bảng hiện hữu:
  - `documents`: Lấy `filename`, `content_hash`, `blob_id`, xác thực quyền sở hữu `user_id`.
  - `document_summaries`: Lấy `problem_citations`, `contribution_citations`, `limitation_citations` cùng văn bản tóm tắt tương ứng.

### 5.2. Tầng Core Domain & Ports (`packages/core/`):
1. **Value Objects (`packages/core/src/core/domain/value_objects/pdf_annotation.py`):**
   ```python
   class AnnotationCategory(str, Enum):
       PROBLEM_STATEMENT = "problem_statement"
       CONTRIBUTION = "contribution"
       LIMITATION = "limitation"
       USER_NOTE = "user_note"

   @dataclass(frozen=True)
   class PdfAnnotation:
       page_number: int  # 1-indexed
       bounding_box: BoundingBox
       title: str
       content: str
       category: AnnotationCategory
       color_rgb: tuple[float, float, float]
       opacity: float = 0.4
   ```
2. **Port Interface (`packages/core/src/core/ports/pdf_annotator.py`):**
   ```python
   class IPdfAnnotatorPort(Protocol):
       def annotate_pdf(
           self,
           pdf_bytes: bytes,
           annotations: list[PdfAnnotation],
       ) -> bytes:
           """Embed ISO 32000-1 native highlight annotations into PDF byte stream."""
           ...
   ```

### 5.3. Tầng Driven Adapter (`apps/api/src/api/adapters/pdf_annotator.py`):
- Cài đặt `PyMuPdfAnnotator` hiện thực hóa `IPdfAnnotatorPort`.
- Ánh xạ tọa độ $[0.0, 1.0]$ sang kích thước trang PDF thực tế.
- Khởi tạo Annotation Type `/Highlight`, thiết lập màu sắc chuẩn hóa RGB, gán `title` và `content` vào thuộc tính Info của annotation.
- Cấu hình nén `garbage=3, deflate=True` và giải phóng bộ nhớ.

### 5.4. Tầng Application Use Cases (`apps/api/src/api/services/document_service.py`):
- Phương thức `export_annotated_pdf(document_id: UUID, user_id: UUID, include_highlights: bool = True) -> tuple[bytes, str, int]`:
  1. Kiểm tra tài liệu tồn tại và thuộc quyền sở hữu của `user_id` (nếu không -> `404 DOCUMENT_NOT_FOUND`).
  2. Đọc luồng nhị phân PDF từ storage CAS bằng `content_hash`.
  3. Nếu `include_highlights=True`:
     - Truy vấn `document_summaries` của tài liệu.
     - Chuyển đổi các tọa độ trích dẫn thành danh sách `PdfAnnotation` kèm màu sắc và nội dung.
     - Gọi `IPdfAnnotatorPort.annotate_pdf(pdf_bytes, annotations)`.
     - Đếm số lượng annotations đã nhúng thành công.
  4. Nếu `include_highlights=False`:
     - Giữ nguyên `pdf_bytes` gốc, `annotation_count = 0`.
  5. Tạo tên tệp xuất chuẩn hóa (ví dụ: `{original_name_stem}_annotated.pdf`).
  6. Trả về `(annotated_bytes, safe_filename, annotation_count)`.

### 5.5. Tầng Driving Adapter (`apps/api/src/api/v1/endpoints/documents.py`):
- Endpoint: `GET /api/v1/documents/{document_id}/export-pdf`
- Query Params: `include_highlights: bool = Query(True, description="Whether to embed AI grounded highlights")`
- Phản hồi: `Response(content=pdf_bytes, media_type="application/pdf", headers=...)`
- Headers trả về:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="{ascii_filename}"; filename*=UTF-8''{encoded_filename}`
  - `Content-Length: str(len(pdf_bytes))`
  - `X-Annotation-Count: str(annotation_count)`
  - `Cache-Control: private, no-transform`

---

## 6. Kế Hoạch Kiểm Thử 2 Cấp Độ (Unitest & Autotest Snapshot)

> **Nguyên tắc bất di bất dịch:** Tuyệt đối KHÔNG thiết kế endpoint backdoor `/api/v1/testing/...`. Mọi kiểm thử đều đi qua luồng REST công khai.

### 6.1. Cấp Độ 1: Integration / Unit Tests (`apps/api/tests/test_documents_export_pdf.py`):
1. `test_export_pdf_with_highlights_success`: Xuất tài liệu có tóm tắt, kiểm tra `200 OK`, `Content-Type: application/pdf`, `X-Annotation-Count > 0`, và dùng PyMuPDF mở lại byte stream để xác minh tồn tại đúng số lượng `/Highlight` annotations trên các trang tương ứng.
2. `test_export_pdf_without_highlights_success`: Gọi với `include_highlights=false`, kiểm tra byte stream trả về nguyên vẹn, `X-Annotation-Count: 0`, không chứa annotations nhân tạo.
3. `test_export_pdf_when_summary_absent`: Tài liệu chưa có tóm tắt gọi với `include_highlights=true`, hệ thống vẫn trả về `200 OK` với `X-Annotation-Count: 0` mà không gây lỗi.
4. `test_export_pdf_multi_tenant_isolation`: Người dùng B không thể xuất PDF của người dùng A (trả về `404 DOCUMENT_NOT_FOUND`).
5. `test_export_pdf_nonexistent_document`: UUID không tồn tại trả về `404 DOCUMENT_NOT_FOUND`.
6. `test_export_pdf_invalid_uuid`: Định dạng UUID sai trả về `422 UNPROCESSABLE_ENTITY`.
7. `test_export_pdf_content_disposition_header_encoding`: Kiểm tra định dạng header `Content-Disposition` xử lý an toàn tên file chứa dấu cách và ký tự đặc biệt.

### 6.2. Cấp Độ 2: Autotest Snapshot Runner Độc Lập (`scripts/eval/runners/get_documents_export_pdf.py`):
- Xây dựng lớp `DocumentExportPdfAPIRunner(BaseAPIRunner)`:
  - Upload tài liệu benchmark chuẩn.
  - Sinh tóm tắt 3 ý (`POST .../summary:generate`).
  - Gửi request `GET /api/v1/documents/{id}/export-pdf?include_highlights=true`.
  - Kiểm chứng:
    - HTTP Status = 200.
    - Media-Type = `application/pdf`.
    - `X-Annotation-Count >= 3`.
    - Dùng PyMuPDF đọc lại tệp xuất, xác minh các đối tượng `/Highlight` có chứa đầy đủ thuộc tính Info (`title`, `content`).
    - Lưu tệp PDF xuất ra thư mục artifacts kèm mã băm SHA-256 để nghiệm thu chất lượng trực quan.
  - Tự động ghi lại báo cáo chi tiết vào `temp/output/test/get_documents_export_pdf.md`.

### 6.3. Tích Hợp Runner Tổng (`scripts/eval_api.py`):
- Đăng ký alias `export-pdf` trong `scripts/eval/runners/__init__.py`.
- Tích hợp để khi chạy `uv run python scripts/eval_api.py --all --ci-gate`, hệ thống sẽ kích hoạt toàn bộ 15 API của Module 1 và đánh giá Quality Gate 15/15 PASS.

### 6.4. Cập Nhật Tài Liệu Kèm Theo:
- Bổ sung đặc tả endpoint 15 vào [`docs/vi/swagger.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md).
- Bổ sung cấu trúc snapshot vào [`docs/vi/design-api-eval-snapshots.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api-eval-snapshots.md).
- Cập nhật hướng dẫn chạy lệnh trong [`scripts/README.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/scripts/README.md).

---

## 7. Kế Hoạch Phân Kỳ Thực Thi Chi Tiết (Execution Roadmap)

```
[BƯỚC 1: NHÁNH & CORE PORTS]
├── Tạo nhánh: feat/m1-api-document-export-pdf
├── Tạo Value Object: PdfAnnotation, AnnotationCategory (core/domain/value_objects/pdf_annotation.py)
└── Tạo Port Interface: IPdfAnnotatorPort (core/ports/pdf_annotator.py)

[BƯỚC 2: ADAPTER & DEPENDENCY INJECTION]
├── Tạo Driven Adapter: PyMuPdfAnnotator (apps/api/src/api/adapters/pdf_annotator.py)
└── Đăng ký Dependency: get_pdf_annotator() trong apps/api/src/api/deps.py

[BƯỚC 3: APPLICATION SERVICE & DRIVING ROUTER]
├── Bổ sung export_annotated_pdf() trong apps/api/src/api/services/document_service.py
└── Khai báo GET /{document_id}/export-pdf trong apps/api/src/api/v1/endpoints/documents.py

[BƯỚC 4: KIỂM THỬ TỰ ĐỘNG & EVAL RUNNER]
├── Viết 7+ Unit/Integration test cases: apps/api/tests/test_documents_export_pdf.py
├── Tạo Snapshot Runner: scripts/eval/runners/get_documents_export_pdf.py
└── Đăng ký export-pdf vào scripts/eval_api.py

[BƯỚC 5: TÀI LIỆU HÓA & GATE REVIEW]
├── Cập nhật swagger.md, design-api-eval-snapshots.md, scripts/README.md
├── Chạy --all --ci-gate đạt 15/15 APIs PASS
├── Dọn sạch dữ liệu (purge_all.py)
└── Trình báo cáo kết quả và đợi lệnh của Người dùng.
```

---

## 8. Kết Luận

Kế hoạch trên bảo đảm tính toàn vẹn 100% của kiến trúc Lục giác (Hexagonal Architecture), tuân thủ tiêu chuẩn ISO 32000 quốc tế về tài liệu học thuật, không vi phạm các ràng buộc an toàn (không đọc `.env`, không sửa mã nguồn trước khi duyệt, không có backdoor).

**Kế hoạch đã sẵn sàng để chuyển sang giai đoạn thực thi ngay khi nhận được lệnh phê duyệt của bạn.**


---

## 8. Các Nâng Cấp Kỹ Thuật Đạt Chuẩn Production (Production Enhancements)

Nhằm đáp ứng trải nghiệm nghiên cứu học thuật cao cấp tương đương các công cụ quản lý thư mục uy tín (Zotero, Mendeley, ReadCube), hệ thống đã được nâng cấp bổ sung 3 tính năng cốt lõi:

### 8.1. PDF Bookmarks / Outlines Navigation Tree (Điều hướng Mục lục Sidebar)
* **Cơ chế:** Tự động tạo cây thư mục PDF Bookmarks theo phân cấp chuẩn:
  ```text
  📑 VeriScholar AI Grounded Summary
     ├── 🟧 Problem Statement (Nhảy ngay đến vị trí câu văn làm bằng chứng ở Trang N)
     ├── 🟩 Contributions     (Nhảy ngay đến vị trí câu văn làm bằng chứng ở Trang N)
     └── 🟪 Limitations       (Nhảy ngay đến vị trí câu văn làm bằng chứng ở Trang N)
  ```
* **Lợi ích:** Người đọc khi mở bài báo bằng Adobe Acrobat, Foxit Reader, Chrome hoặc Apple Preview chỉ cần bấm vào thanh sidebar bên trái là PDF tự động nhảy vọt đến đúng vị trí câu văn quan trọng mà không phải cuộn tìm thủ công trên tài liệu 20-50 trang.

### 8.2. Chuẩn Hóa PDF Metadata (Zotero / Mendeley Interoperability)
* **Cơ chế:** Cập nhật trực tiếp siêu dữ liệu nhị phân của tệp PDF:
  - `Title`: Tên bài báo chuẩn (`doc.title`).
  - `Author`: Tác giả bài báo (`doc.authors`).
  - `Subject`: `"VeriScholar AI Grounded Summary (ISO 32000)"`.
  - `Keywords`: `"VeriScholar, AI Summary, Visual Grounding, ISO 32000"`.
  - `Producer`: `"VeriScholar AI Research Assistant (verischolar.org)"`.
  - `Creator`: `"VeriScholar PDF Engine"`.
* **Lợi ích:** Tương thích hoàn hảo khi người dùng kéo thả tài liệu vào các phần mềm trích dẫn nghiên cứu quốc tế.

### 8.3. Lọc Highlight Theo Danh Mục Linh Hoạt (`categories` Query Param)
* **Cơ chế:** Endpoint chấp nhận tham số `categories` (ví dụ: `?categories=contributions` hoặc `?categories=problem_statement,contributions`).
* **Lợi ích:** Cho phép Frontend UI linh hoạt bật/tắt hoặc tải về phiên bản tài liệu chỉ chứa đúng nhóm highlight mà độc giả quan tâm.

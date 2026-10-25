# ĐẶC TẢ KỸ THUẬT: PHÂN HỆ KHÁM PHÁ ĐỀ TÀI & NẠP TÀI LIỆU 2 TẦNG
# (SCHOLARLY DISCOVERY, 2-TIER INGESTION & DOCUMENTS CRUD SPECIFICATION)

**Trạng thái:** DỰ THẢO CHÍNH THỨC (TECHNICAL SPECIFICATION V1)  
**Nguồn tham chiếu PRD:** [`docs/PRD/02-discovery-and-documents-crud.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/PRD/02-discovery-and-documents-crud.md)  
**Phân hệ kỹ thuật:** Phân Hệ Khám Phá & Nạp Tài Liệu (Discovery & Ingestion)  
**File nền tảng liên đới:** [`docs/specs/00-foundation-architecture-and-db.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/specs/00-foundation-architecture-and-db.md)

---

## 1. Usecase & Bối Cảnh Người Dùng (Real-World User Journey & Value)

### A. Usecase 1: Khám Phá Đề Tài Từ Con Số Không (Zero-to-Reading Across Open Access & Paywalls)
- **Bối cảnh & Vấn đề thực tế:** Khi bắt đầu một đề tài nghiên cứu mới, học giả không biết nên tìm bài báo ở đâu ngoài Google Scholar. Tuy nhiên, rất nhiều bài báo quan trọng nằm sau bức tường phí (Paywall) của IEEE, Springer hay Elsevier. Khi người dùng gặp bài bị khóa, đa số các công cụ AI khác sẽ báo lỗi hoặc bỏ cuộc, khiến học giả mất dấu tài liệu quan trọng.
- **Giải pháp của phân hệ:**
  - Tích hợp tìm kiếm đa nguồn học thuật (Exa AI, Semantic Scholar, arXiv) với cơ chế phân loại trạng thái linh hoạt 2 chế độ:
    - **Bài Open Access:** Hiển thị nút `[📖 Mở Đọc Sâu (Full PDF)]` để mở xem toàn văn PDF kèm Bounding Box vàng.
    - **Bài Paywall:** Không chặn người dùng mà hiển thị nút `[📄 Xem Tóm Tắt (Abstract)]` cho phép đọc tóm tắt, mục tiêu nghiên cứu và trích dẫn, kèm nút `[📤 Tải lên file PDF]` để người dùng tự tải bản PDF có sẵn của mình lên tiếp tục phân tích.

### B. Usecase 2: Trải Nghiệm Nạp 2 Tầng Không Chờ Đợi (Instant Zero-Waiting 2-Tier Ingestion)
- **Bối cảnh & Vấn đề thực tế:** Một file PDF bài báo khoa học 30–50 trang chứa nhiều hình ảnh, công thức và bảng biểu. Nếu bắt người dùng chờ hệ thống tải file, bóc tách OCR, chia đoạn chunking và tạo vector embedding (thường mất 20–40 giây), người dùng sẽ cảm thấy ứng dụng bị đơ và rời bỏ.
- **Giải pháp của phân hệ:**
  - Thiết kế đường ống nạp 2 tầng bất đối xứng:
    - **Tầng 1 (Tức thì < 500ms):** Lưu ngay tiêu đề, tác giả, DOI và tóm tắt vào CSDL, khởi tạo ngay phiên đọc và đưa người dùng vào màn hình làm việc tức thì.
    - **Tầng 2 (Chạy ngầm BackgroundTasks):** Hệ thống âm thầm tải file PDF về kho CAS, dùng PyMuPDF bóc tách từng khối văn bản gắn tọa độ hình học (Bounding Box) và tính toán vector embedding `Vector(1536)` mà không làm nghẽn giao diện người dùng.

### C. Usecase 3: Tải Lên & Quản Lý Tài Liệu PDF Cá Nhân (Personal PDF Upload & CAS Dedup)
- **Bối cảnh & Vấn đề thực tế:** Người dùng có tài liệu nội bộ, báo cáo kỹ thuật riêng tải từ trường đại học muốn đối thoại với AI. Họ cần tải file lên dễ dàng (`<= 50MB`, `<= 100 trang`) và muốn tài liệu của mình được bảo mật, không bị trùng lặp lãng phí dung lượng ổ đĩa.
- **Giải pháp của phân hệ:**
  - Hỗ trợ tải file PDF trực tiếp qua `POST /api/v1/documents/upload` với kiểm tra MIME type và giới hạn dung lượng chặt chẽ. Áp dụng Content-Addressable Storage (CAS) tự động khử trùng lặp qua mã băm SHA-256 giúp tiết kiệm tối đa dung lượng máy chủ.

---

## 2. Phạm Vi & Bảng Đối Chiếu Hiện Trạng (`As-Is` vs `Delta`)

Phân hệ này giải quyết bài toán khởi đầu nghiên cứu khoa học từ con số 0 (**Zero-to-Reading**): tìm kiếm bài báo ngoài theo chủ đề (Exa AI, Semantic Scholar, arXiv), nạp bài báo 2 tầng linh hoạt theo 2 trạng thái (**Full PDF** hoặc **Abstract-Only**), tải lên tài liệu PDF cá nhân (`<= 50MB`, `<= 100 trang`), bóc tách khối văn bản gắn tọa độ Bounding Box và lưu trữ vào kho CAS.

```mermaid
flowchart TD
    subgraph DiscoveryFlow ["<b>Luồng Khám Phá Bài Báo Mới (Zero-to-Reading)</b>"]
        QueryInput["Người dùng nhập chủ đề nghiên cứu<br/>(DiscoveryPage.tsx)"]
        SearchAPI["POST /api/v1/discovery/search<br/>(Exa AI + Semantic Scholar + arXiv)"]
        CardDisplay{"Phân loại quyền truy cập bài báo"}
        
        OpenAccessCard["Thẻ có PDF mở (Open Access)<br/>Nút: [📖 Mở Đọc Sâu (Full PDF)]"]
        PaywallCard["Thẻ chỉ có tóm tắt (Paywall)<br/>Nút: [📄 Xem Tóm Tắt (Abstract)]"]
        
        QueryInput --> SearchAPI --> CardDisplay
        CardDisplay -->|Có Open Access URL| OpenAccessCard
        CardDisplay -->|Không có PDF mở| PaywallCard
    end

    subgraph IngestionFlow ["<b>Đường Ống Nạp 2 Tầng (2-Tier Ingestion)</b>"]
        OpenReadingAPI["POST /api/v1/discovery/open-reading"]
        Tier1Meta["Tầng 1 (< 500ms): Lưu Metadata & Abstract<br/>Tạo Document & ResearchSession"]
        Tier2Background["Tầng 2 (BackgroundTasks): Tải PDF về CAS<br/>PyMuPDF Chunking & Bounding Box & Vector(1536)"]
        
        OpenAccessCard --> OpenReadingAPI
        PaywallCard --> OpenReadingAPI
        OpenReadingAPI --> Tier1Meta
        Tier1Meta -->|Nếu có PDF URL| Tier2Background
        Tier1Meta --> Navigate["Frontend chuyển thẳng sang /dashboard/{sessionId}"]
    end
```

### Bảng Kiểm Kê Thành Phần Mã Nguồn
| Thành phần | Đường dẫn File | Trạng thái | Nội dung chi tiết |
|---|---|---|---|
| **Discovery API** | `apps/api/src/api/v1/endpoints/discovery.py` | **CREATE** | Tạo mới 2 endpoint: `POST /api/v1/discovery/search` (tìm bài báo ngoài) và `POST /api/v1/discovery/open-reading` (khởi tạo phiên đọc từ kết quả tìm kiếm). Mount vào `api_v1_router`. |
| **Documents API** | [`apps/api/src/api/v1/endpoints/documents.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/v1/endpoints/documents.py) | **KEEP** | Giữ nguyên CRUD tài liệu: `POST /upload`, `GET /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`, `POST /{id}:parse`. |
| **Ingestion Pipeline** | [`apps/api/src/api/services/document_service.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/services/document_service.py) | **MODIFY** | Bổ sung logic phân biệt 2 trạng thái `ready` (cho abstract-only) và `parsing` $\rightarrow$ `ready` (cho full PDF), bóc tách Bounding Box PyMuPDF và sinh embedding `Vector(1536)`. |
| **Exa & arXiv Adapter** | `packages/core/src/core/services/` & `apps/api/src/api/adapters/` | **MODIFY** | Tách cổng trừu tượng `IScholarlySearchPort` trong Core và cài đặt Adapter gọi Exa AI SDK (`category="research paper"`) + Semantic Scholar + arXiv. |
| **Discovery UI** | [`apps/web/src/features/discovery/components/DiscoveryPage.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/discovery/components/DiscoveryPage.tsx) | **MODIFY** | Thay thế code tìm kiếm nhầm trong danh sách tài liệu local cũ bằng gọi API `POST /api/v1/discovery/search`, hiển thị thẻ kết quả với 2 nút tương ứng. |
| **Documents UI** | `apps/web/src/features/documents/` | **KEEP** | Danh sách tài liệu, Modal upload PDF kéo thả, thanh tiến trình parse tài liệu. |

---

## 3. Mô Hình Dữ Liệu & Ràng Buộc Trạng Thái (`Database Schema & Status Lifecycle`)

### A. Vòng Đời Trạng Thái Tài Liệu (`documents.status`)
Bảng `documents` (đã đặc tả ở Spec 00) quản lý trạng thái tài liệu qua 4 giá trị bất biến:
1. `status = 'abstract_only'`: Bài báo được tạo từ kết quả tìm kiếm không có link PDF. Chỉ có metadata và Abstract (được lưu trong `document_chunks` chunk 0). Khung đọc bên trái hiển thị thẻ học thuật `AbstractCardViewer.tsx`.
2. `status = 'parsing'`: Bài báo đang tải file PDF ngầm hoặc đang chạy PyMuPDF bóc tách văn bản. Khung đọc bên trái hiển thị thanh tiến trình `progress: 0..100%`.
3. `status = 'ready'`: Toàn bộ các trang PDF đã được bóc tách xong thành các chunks, tính đủ tọa độ Bounding Box và hoàn tất nhúng vector `Vector(1536)`.
4. `status = 'failed'`: Xảy ra lỗi khi tải PDF hoặc file không phải là Digital PDF (PDF scan/ảnh không có text layer). Kèm thông điệp `error_message`.

```mermaid
stateDiagram-v2
    [*] --> abstract_only : Nạp bài không có PDF mở
    [*] --> parsing : Nạp bài Open Access hoặc Upload PDF
    
    abstract_only --> parsing : Người dùng upload file PDF đầy đủ
    parsing --> ready : PyMuPDF parse & Vector(1536) hoàn tất
    parsing --> failed : Lỗi tải mạng / PDF scan không có text
    
    failed --> parsing : Bấm Thử lại (force_reparse=true)
    ready --> [*] : Xóa tài liệu (Cascade CAS)
```

### B. Ràng Buộc Kiểm Tra Hợp Lệ Của File Tải Lên (Validation Invariants)
- **Định dạng file:** Bắt buộc là file PDF nhị phân hợp lệ (Magic bytes `%PDF-`).
- **Dung lượng tối đa:** `50 MB` ($52.428.800$ bytes). Vượt quá trả về `413 PAYLOAD_TOO_LARGE`.
- **Số trang tối đa:** `<= 100 trang`. Vượt quá trả về `422 UNPROCESSABLE_ENTITY`.
- **Lớp văn bản (Text Layer Check):** Kiểm tra trang 1 có ít nhất 50 ký tự văn bản có thể trích xuất. Nếu trang 1 không có text (PDF scan thuần ảnh), trả về lỗi `PDF_NO_TEXT_LAYER` và hướng dẫn người dùng cung cấp bản số hóa có OCR.

---

## 4. Hợp Đồng API REST & Streaming Events (REST Contracts)

### A. API Khám Phá Bài Báo (`apps/api/src/api/v1/endpoints/discovery.py`)

#### 1. Tìm kiếm bài báo học thuật (`POST /api/v1/discovery/search`)
- **Headers:** `Authorization: Bearer <token>`, `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "query": "Direct Preference Optimization language models",
    "limit": 10
  }
  ```
- **Response (HTTP 200 OK):**
  ```json
  {
    "data": [
      {
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": ["Rafael Rafailov", "Archit Sharma", "Eric Mitchell", "Stefano Ermon"],
        "publication_year": 2023,
        "venue": "NeurIPS 2023",
        "doi": "10.48550/arXiv.2305.18290",
        "arxiv_id": "2305.18290",
        "abstract": "While standard RLHF pipelines are complex and unstable...",
        "access_status": "open_access_pdf",
        "pdf_url": "https://arxiv.org/pdf/2305.18290.pdf"
      },
      {
        "title": "A general theoretical paradigm for preference learning",
        "authors": ["Author A", "Author B"],
        "publication_year": 2024,
        "venue": "Nature Machine Intelligence",
        "doi": "10.1038/s42256-024-00800-x",
        "arxiv_id": null,
        "abstract": "Preference optimization has become the standard technique...",
        "access_status": "abstract_only",
        "pdf_url": null
      }
    ],
    "meta": {
      "total_results": 2,
      "trace_id": "trace-disc-892a01"
    }
  }
  ```

#### 2. Mở phiên đọc từ kết quả tìm kiếm (`POST /api/v1/discovery/open-reading`)
- **Mục đích:** Tạo tức thì bài báo và phiên đọc sâu mới (Zero-to-Reading) chỉ trong 1 request duy nhất.
- **Request Body:**
  ```json
  {
    "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
    "authors": ["Rafael Rafailov", "Archit Sharma"],
    "publication_year": 2023,
    "doi": "10.48550/arXiv.2305.18290",
    "arxiv_id": "2305.18290",
    "abstract": "While standard RLHF pipelines are complex...",
    "pdf_url": "https://arxiv.org/pdf/2305.18290.pdf"
  }
  ```
- **Response (HTTP 201 Created):**
  ```json
  {
    "session_id": "8a9b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d",
    "document_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "status": "parsing",
    "access_status": "open_access_pdf"
  }
  ```
  *(Nếu `pdf_url` là `null`, trả về `status: "abstract_only"`, `access_status: "abstract_only"`).*

---

### B. API Quản Lý Tài Liệu PDF (`apps/api/src/api/v1/endpoints/documents.py`)

#### 1. Tải lên tài liệu PDF cá nhân (`POST /api/v1/documents` hoặc alias `/upload`)
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
  - `file`: File nhị phân (`.pdf`)
  - `title`: Chuỗi tiêu đề tùy chọn (mặc định lấy tên file)
  - `folder_id`: UUID thư mục tùy chọn
- **Xử lý:**
  - Tính băm SHA-256. Kiểm tra `document_storage_blobs`.
  - Lưu file vào `storage/blobs/ab/cd/hash.pdf`.
  - Tạo `DocumentModel` với `status="parsing"`, kích hoạt tác vụ ngầm bóc tách.
- **Response (HTTP 202 Accepted):**
  ```json
  {
    "id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "filename": "dpo_paper.pdf",
    "file_size_bytes": 1420580,
    "status": "parsing",
    "stage": "validation",
    "progress": 0
  }
  ```

#### 2. Lấy chi tiết tài liệu & Bounding Boxes (`GET /api/v1/documents/{id}`)
- **Response (HTTP 200 OK):**
  Trả về metadata tài liệu, tóm tắt 3 phần `DocumentSummary`, danh mục trích dẫn `references`, và mảng chunks kèm tọa độ `bounding_boxes: [[x0, y0, x1, y1]]` của từng đoạn văn bản.

#### 3. Bổ sung PDF cho bài báo Abstract-Only (`POST /api/v1/documents/{id}/attach-pdf`)
- **Mục đích:** Nâng cấp bài báo từ `status="abstract_only"` lên `status="ready"` bằng cách nạp file PDF đầy đủ.
- **Headers:** `Content-Type: multipart/form-data`
- **Xử lý:** Lưu file PDF vào CAS, chuyển `status` sang `parsing`, kích hoạt PyMuPDF trích xuất toàn bài và thông báo qua WebSocket/Polling để Frontend tự động chuyển sang `PdfCanvasViewer`.

---

## 5. Thiết Kế Đường Ống Bóc Tách Kỹ Thuật (Ingestion & PyMuPDF Chunking)

### A. Thuật Toán Trích Xuất Khối Văn Bản & Bounding Box
Trong [`apps/api/src/api/adapters/chunk_extractor.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/adapters/chunk_extractor.py), sử dụng PyMuPDF (`pymupdf`):
1. **Lấy khối chữ theo trang (Page Blocks):**
   ```python
   page = doc.load_page(page_num)
   blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
   ```
2. **Chuẩn hóa Tọa độ Hệ số Tương đối (Normalized 0..1000):**
   Để hiển thị lớp phủ Bounding Box chuẩn xác trên mọi độ phân giải màn hình và mức độ zoom, tọa độ pixel điểm ảnh được chuẩn hóa theo tỷ lệ kích thước trang:
   $$x0_{\text{norm}} = \frac{x0}{\text{page\_width}} \times 1000, \quad y0_{\text{norm}} = \frac{y0}{\text{page\_height}} \times 1000$$
3. **Cắt đoạn theo ngưỡng Token (Chunking Invariant):**
   - Kích thước mục tiêu: `512 tokens` (khoảng 1.800–2.200 ký tự).
   - Độ gối đầu (Overlap): `50 tokens` để bảo tồn mạch ngữ nghĩa giữa các đoạn liền kề.
   - Gắn kết mảng tọa độ `bounding_boxes: [[x0, y0, x1, y1], ...]` tương ứng với các dòng chữ nằm trong chunk đó.

### B. Sinh Vector Nhúng (Embedding Generation)
1. Gọi OpenAI Embedding API với mô hình cố định `text-embedding-3-small`.
2. Đầu ra là vector `1536 chiều`. Lưu trực tiếp vào cột `document_chunks.embedding` kiểu `Vector(1536)`.
3. Tự động kích hoạt cập nhật chỉ mục `HNSW` trong PostgreSQL.

---

## 6. Thiết Kế Giao Diện & Tương Tác Frontend (`apps/web`)

### A. Giao Diện Khám Phá Bài Báo (`DiscoveryPage.tsx`)
1. **Thanh tìm kiếm trung tâm lớn:** Ô tìm kiếm với gợi ý từ khóa học thuật phổ biến (Deep Learning, NLP, Quantum Computing, CRISPR...).
2. **Thẻ kết quả bài báo (Scholarly Result Card):**
   - Tiêu đề in đậm font Serif (Playfair Display / Merriweather).
   - Danh sách tác giả, năm xuất bản, tên hội nghị/tạp chí (`venue`).
   - Huy hiệu trạng thái truy cập:
     - Xanh lá: `🟢 Open Access PDF`
     - Xám: `🔒 Abstract Only (Paywall)`
   - Nút hành động chính:
     - Nếu có PDF: Nút xanh `[📖 Mở Đọc Sâu (Full PDF)]` $\rightarrow$ gọi `open-reading` $\rightarrow$ chuyển sang `/dashboard/{sessionId}`.
     - Nếu không có PDF: Nút viền xám `[📄 Xem Tóm Tắt (Abstract)]` $\rightarrow$ gọi `open-reading` $\rightarrow$ mở phiên đọc ở chế độ xem thẻ tóm tắt.

### B. Trình Xem Thẻ Tóm Tắt (`AbstractCardViewer.tsx`)
Khi bài báo ở trạng thái `status="abstract_only"`:
- Khung bên trái hiển thị một giao diện thẻ bài báo trang trọng:
  - Header: Tiêu đề bài báo, Tác giả, Năm, Link DOI chuyển hướng sang trang web gốc của nhà xuất bản.
  - Body: Toàn văn đoạn Abstract được định dạng đẹp mắt với khoảng cách dòng thoáng (leading-relaxed).
  - Callout Banner màu hổ phách (Amber Warning): *"Bài báo này hiện mới có đoạn tóm tắt. Bạn có thể hỏi đáp với AI về ý tưởng chính hoặc tải file PDF gốc lên để mở khóa toàn bộ bài báo."*
  - Nút bấm lớn trung tâm: `[📤 Tải lên file PDF đầy đủ]` mở hộp thoại chọn file nạp vào endpoint `POST /api/v1/documents/{id}/attach-pdf`.

---

## 7. Ma Trận Kiểm Thử TDD Bắt Buộc (Discovery & Documents TDD Matrix)

```mermaid
flowchart TD
    subgraph CoreTests ["<b>Tầng Core / Domain Tests</b>"]
        D1["Test PDF Validator Gate<br/>(Reject file > 50MB, > 100 pages, scanned PDF)"]
        D2["Test Bounding Box Normalizer<br/>(Transform raw points to 0..1000 range)"]
    end

    subgraph ServiceTests ["<b>Tầng API Discovery & Ingestion Tests</b>"]
        E1["Test Search Deduplication<br/>(Merge Exa + Semantic Scholar + arXiv by DOI)"]
        E2["Test Ingestion 2-Tier Timing<br/>(Tier 1 responds < 500ms, Tier 2 background)"]
        E3["Test Abstract-Only to Ready Transition<br/>(Attach PDF switches status and parses chunks)"]
    end

    subgraph IntegrationTests ["<b>Tầng Integration Tests (PostgreSQL + CAS Real)</b>"]
        F1["Test CAS Upload Deduplication<br/>(Two uploads with same hash share blob_id)"]
        F2["Test Document Cascading Deletion<br/>(Delete document purges chunks and triggers CAS unlink)"]
    end

    CoreTests --> ServiceTests --> IntegrationTests
```

| Tên Test Case | File Kiểm Thử | Mục tiêu kiểm chứng | Kỳ vọng nghiệm thu |
|---|---|---|---|
| `test_validate_pdf_file_limits` | `packages/core/tests/test_pdf_validator.py` | Kiểm tra file > 50MB hoặc > 100 trang | Ném lỗi `FileLimitExceededException`. |
| `test_discovery_search_and_classify_access` | `apps/api/tests/test_discovery_endpoints.py` | Gọi `POST /api/v1/discovery/search` với mock search port | Trả về danh sách bài có phân loại đúng `open_access_pdf` và `abstract_only`. |
| `test_open_reading_creates_session_and_document` | `apps/api/tests/test_discovery_endpoints.py` | Gọi `POST /api/v1/discovery/open-reading` | Trả về `session_id` và `document_id` hợp lệ, liên kết đúng trong DB. |
| `test_document_upload_and_cas_deduplication` | `apps/api/tests/test_document_upload.py` | Tải lên 2 file PDF có cùng nội dung | Chỉ tạo 1 file nhị phân trong `storage/blobs/`, `ref_count=2`. |
| `test_attach_pdf_to_abstract_only_document` | `apps/api/tests/test_document_attach.py` | Nạp file PDF vào bài báo `abstract_only` | Chuyển trạng thái sang `parsing`, bóc tách chunks và hoàn tất sang `ready`. |
| `test_document_delete_purges_chunks_and_blob` | `apps/api/tests/test_document_delete.py` | Xóa bài báo duy nhất của blob đó | Bảng `documents` và `document_chunks` sạch bản ghi, file trên đĩa bị xóa. |

---

## 8. Tiêu Chí Nghiệm Thu Kỹ Thuật (Definition of Done)

- [ ] 2 API `POST /api/v1/discovery/search` và `POST /api/v1/discovery/open-reading` được cài đặt hoàn chỉnh và mount vào API router.
- [ ] Giao diện `DiscoveryPage.tsx` tìm kiếm được bài báo thực tế từ internet và hiển thị đúng 2 loại nút bấm (`Full PDF` vs `Abstract`).
- [ ] Quy trình nạp bài 2 tầng đảm bảo phản hồi tức thì (`< 500ms`) cho người dùng trước khi tải ngầm PDF.
- [ ] Hỗ trợ đầy đủ luồng nâng cấp bài báo `abstract_only` sang `ready` qua `attach-pdf`.
- [ ] Toàn bộ kịch bản kiểm thử trong Ma trận Kiểm thử Mục 6 đạt `100% PASS`.

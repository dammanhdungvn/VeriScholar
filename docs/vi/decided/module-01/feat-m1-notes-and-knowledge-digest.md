# Kế Hoạch Kỹ Thuật: Sổ Tay Nghiên Cứu & AI Tổng Hợp Tri Thức (Smart Notebook & Knowledge Digest)

> **Mã tài liệu:** `FEAT-M1-NOTES-AND-KNOWLEDGE-DIGEST`  
> **Trạng thái:** `PLANNING / CHỜ PHÊ DUYỆT (CHƯA VIẾT CODE TRIỂN KHAI)`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 17/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-notes-and-knowledge-digest`  
> **Phạm vi TARGET:** 6 APIs cốt lõi của Sổ tay nghiên cứu & AI Tổng hợp (Module 1):
> 1. `POST   /api/v1/notes`                              # 16. Lưu trích dẫn & ghi chú cá nhân (Add to Note)
> 2. `GET    /api/v1/notes`                              # 17. Danh sách ghi chú (lọc theo document_id, tag, folder_id)
> 3. `GET    /api/v1/notes/{id}`                         # 18. Chi tiết ghi chú kèm Frozen Evidence Snapshot
> 4. `PATCH  /api/v1/notes/{id}`                         # 19. Sửa ghi chú / tag (Kiểm soát đồng thời OCC If-Match)
> 5. `DELETE /api/v1/notes/{id}`                         # 20. Xóa ghi chú khỏi sổ tay
> 6. `POST   /api/v1/notes:synthesize`                   # 21. AI Tổng hợp ghi chú thành bài học (3 modes + Badges)  
> **Chuẩn thiết kế:** RFC 9110 / RFC 7232 (OCC ETag / If-Match), W3C Web Annotation Data Model, RFC 7807 (Problem Details), Google AIP-136 / AIP-158, Hexagonal Clean Architecture.

---

## 1. Khảo Sát Nghiên Cứu Thế Giới & Tùy Biến Cho VeriScholar (State of the Art & Customization)

### 1.1. Cách Các Nền Tảng Hàng Đầu Thế Giới Giải Quyết Bài Toán Ghi Chú & Tổng Hợp Học Thuật

1. **Chuẩn W3C Web Annotation Architecture & Hypothes.is:**
   - **Vấn đề toàn cầu:** Khi đánh dấu (highlight) văn bản trên tài liệu số, việc chỉ lưu tọa độ ký tự offset (`start_offset`, `end_offset`) hoặc chỉ lưu tọa độ bounding box đồ họa thường bị gãy khi tài liệu được hiển thị trên các màn hình có tỉ lệ khác nhau hoặc khi PDF được bóc tách bằng các engine khác nhau.
   - **Giải pháp W3C:** Sử dụng kiến trúc bộ chọn đa tầng (Compound Selectors):
     - `TextQuoteSelector`: Lưu chuỗi văn bản chính xác (`exact`), chuỗi ngữ cảnh đứng trước (`prefix`), chuỗi ngữ cảnh đứng sau (`suffix`).
     - `FragmentSelector`: Lưu tọa độ hộp bao trực quan `[ymin, xmin, ymax, xmax, page]`.
   - **Ứng dụng cho VeriScholar:** Kế thừa nguyên lý này vào trường `frozen_snapshot` và `bounding_boxes` nhằm bảo đảm việc highlight và neo ngữ cảnh (Context Re-anchoring) không bao giờ bị sai lệch vị trí.

2. **Readwise, LiquidText & Zotero 7 (Vấn nạn "Ghost Highlight" & Bảo Toàn Bằng Chứng):**
   - **Vấn đề:** Khi một bài báo hoặc cuốn sách bị xóa khỏi thư viện người dùng, các ghi chú và suy nghĩ cá nhân của người đọc nếu gắn cứng (`ON DELETE CASCADE`) sẽ bị xóa vĩnh viễn, phá hủy công sức nghiên cứu; hoặc nếu để `NULL` mà không lưu dữ liệu dự phòng sẽ gây ra lỗi `404 Not Found` / vỡ giao diện (Dangling References).
   - **Giải pháp thế giới:** Tách rời vòng đời của *Bằng chứng tư duy (Cognitive Evidence)* khỏi *File vật lý (Physical Storage)*.
   - **Ứng dụng cho VeriScholar:** Áp dụng mô hình **Frozen Evidence Snapshot & Source Detachment**. Khi tài liệu gốc bị xóa sổ, cơ sở dữ liệu chuyển `document_id -> NULL` (`ON DELETE SET NULL`), trigger tự động kích hoạt `is_source_detached = TRUE`. Mọi trích dẫn gốc, số trang, tác giả, năm và ghi chú cá nhân được "đóng băng" nguyên vẹn trong `frozen_snapshot JSONB`. Giao diện hiển thị huy hiệu `[⚠️ Nguồn đã ngắt]` và cho phép mở Evidence Card popup xem lại trọn vẹn, không bao giờ bị lỗi.

3. **Google NotebookLM & Notion AI (Knowledge Digest & Grounded Badges):**
   - **Vấn đề:** Người dùng lưu trữ hàng trăm ghi chú rời rạc nhưng hiếm khi đọc lại (hiện tượng "nghĩa địa highlight" - Highlight Graveyard).
   - **Giải pháp thế giới:** AI đọc sâu tập hợp ghi chú được chọn và tổng hợp thành bản đúc kết có cấu trúc (Study Guides, Briefing Docs), trong đó mỗi nhận định đều gắn huy hiệu trích dẫn có thể nhấp chuột để nhảy về đúng vị trí nguồn.
   - **Ứng dụng cho VeriScholar:** Cung cấp API `POST /api/v1/notes:synthesize` với **3 chế độ tổng hợp chuyên sâu**:
     - `concept_lesson`: Bài học khái niệm theo kỹ thuật Feynman (giải thích trực quan, dễ hiểu, có ví dụ phản chứng).
     - `literature_review`: Đoạn văn tổng quan tài liệu học thuật trang trọng (so sánh đối chiếu phương pháp, trường phái, trích dẫn tác giả - năm chuẩn APA/IEEE).
     - `research_gap`: Phân tích phê bình khoảng trống nghiên cứu (chỉ ra giới hạn thực nghiệm, mâu thuẫn giữa các bài báo, gợi mở đề tài mới).
     - **Interactive Citation Badges**: Trả về mảng `interactive_badges` kẹp tọa độ Bounding Box và số trang để frontend hỗ trợ nhấp chuột nhảy mượt về PDF gốc hoặc mở popup nếu nguồn đã ngắt.

4. **Kiểm Soát Đồng Thời Lạc Quan (Optimistic Concurrency Control - OCC theo RFC 7232):**
   - Khi người dùng chỉnh sửa ghi chú trên nhiều thiết bị (iPad khi đọc trên giảng đường và Laptop khi viết bài tại phòng lab), yêu cầu bắt buộc header `If-Match: "v{version}"` loại bỏ hoàn toàn nguy cơ ghi đè mất dữ liệu (Lost Updates).

---

## 2. Kiến Trúc Lục Giác Tổng Thể & Luồng Xử Lý (Hexagonal Architecture)

```text
                                FRONTEND DUAL-PANE WORKSPACE
                     ┌────────────────────────────────────────────────────────┐
                     │ Trái: PDF Canvas Viewer   │ Phải: Smart Notes Panel    │
                     │ - Text Selection Event    │ - Tag / Folder Filtering   │
                     │ - Bounding Box Capture    │ - Personal Memo Input      │
                     │ - Highlight Persistence   │ - AI Synthesis Trigger     │
                     │ - Jump-to-Source On Click │ - Frozen Evidence Card     │
                     └────────────────────────────────────────────────────────┘
                                       │                      │
                   POST /notes (Add)   │                      │ POST /notes:synthesize
                                       ▼                      ▼
                     ┌────────────────────────────────────────────────────────┐
                     │          FASTAPI DRIVING ADAPTER (apps/api)            │
                     │ - OCC Validator (RFC 7232 If-Match vs ETag)            │
                     │ - Idempotency Guard (RFC 7382 Idempotency-Key)         │
                     │ - Multi-Tenant Authorization & Envelope Serializer     │
                     └────────────────────────────────────────────────────────┘
                                       │                      │
                                       ▼                      ▼
                     ┌────────────────────────────────────────────────────────┐
                     │          APPLICATION SERVICE (apps/api/services)       │
                     │ - NoteService: CRUD, Tag GIN Query, Snapshot Packing   │
                     │ - NoteSynthesisService: Multi-Mode Prompt Orchestrator,│
                     │   Grounded Badge Extractor, JSON Cache                 │
                     └────────────────────────────────────────────────────────┘
                                       │                      │
                                       ▼                      ▼
                     ┌────────────────────────────────────────────────────────┐
                     │          CORE DOMAIN LAYER (packages/core)             │
                     │ - ResearchNote Aggregate Root                          │
                     │ - Value Objects: FrozenSnapshot, BoundingBox, TagList  │
                     │ - NoteSynthesis Aggregate Root & InteractiveBadge VO   │
                     │ - Port Interfaces: INotePort, INoteSynthesisPort       │
                     └────────────────────────────────────────────────────────┘
                                       │                      │
                                       ▼                      ▼
                     ┌────────────────────────────────────────────────────────┐
                     │          DRIVEN ADAPTERS (packages/core / db)          │
                     │ - SQLAlchemy 2.0 Async Session Adapter                 │
                     │ - LLM Inference Gateway (DMR / OpenAI / Gemini)        │
                     │ - PostgreSQL 18 Engine & Triggers (ACID Persistence)   │
                     └────────────────────────────────────────────────────────┘
```

---

## 3. Thiết Kế Cơ Sở Dữ Liệu & Persistence Layer (Database Schema)

### 3.1. Rà Soát & Hoàn Thiện DDL Các Bảng Liên Quan

Theo đúng đặc tả trong [`docs/vi/design-database.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-database.md), hệ thống sử dụng 2 bảng chính:

```sql
-- 1. Bảng research_notes: Lưu trích dẫn, ghi chú cá nhân và bằng chứng đóng băng
CREATE TABLE IF NOT EXISTS research_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NULL REFERENCES documents(id) ON DELETE SET NULL,
    chunk_id UUID NULL REFERENCES document_chunks(id) ON DELETE SET NULL,
    selected_text TEXT NOT NULL,
    bounding_boxes JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_number INT NOT NULL CHECK (page_number >= 1),
    user_note TEXT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    frozen_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_source_detached BOOLEAN NOT NULL DEFAULT FALSE,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chỉ mục tối ưu hóa hiệu năng & tìm kiếm
CREATE INDEX IF NOT EXISTS idx_research_notes_doc_fk ON research_notes(document_id);
CREATE INDEX IF NOT EXISTS idx_research_notes_chunk_fk ON research_notes(chunk_id);
CREATE INDEX IF NOT EXISTS idx_research_notes_user_doc ON research_notes(user_id, document_id);
CREATE INDEX IF NOT EXISTS idx_research_notes_tags ON research_notes USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_research_notes_created ON research_notes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_notes_user_created ON research_notes(user_id, created_at DESC);

-- Trigger kiểm soát phiên bản đồng thời (OCC) và cập nhật updated_at
CREATE TRIGGER trg_research_notes_occ
BEFORE UPDATE ON research_notes
FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();

-- Trigger tự động kích hoạt is_source_detached = TRUE khi document_id bị SET NULL
CREATE OR REPLACE FUNCTION handle_note_source_detached()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.document_id IS NOT NULL AND NEW.document_id IS NULL THEN
        NEW.is_source_detached = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_research_notes_detached
BEFORE UPDATE OF document_id ON research_notes
FOR EACH ROW EXECUTE FUNCTION handle_note_source_detached();

-- 2. Bảng note_syntheses: Lưu trữ kết quả AI Tổng hợp ghi chú thành bài học
CREATE TABLE IF NOT EXISTS note_syntheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('concept_lesson', 'literature_review', 'research_gap')),
    language VARCHAR(10) NOT NULL DEFAULT 'vi',
    markdown_content TEXT NOT NULL,
    interactive_badges JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_note_ids UUID[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_note_syntheses_user ON note_syntheses(user_id, created_at DESC);

CREATE TRIGGER trg_note_syntheses_updated_at
BEFORE UPDATE ON note_syntheses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3.2. Cấu Trúc Bất Biến Của `frozen_snapshot` (JSONB Contract)

Khi người dùng lưu một ghi chú mới, hệ thống truy xuất metadata hiện tại của tài liệu từ bảng `documents` và đóng gói thành snapshot bất biến:

```json
{
  "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
  "document_title": "Attention Is All You Need",
  "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
  "year": 2017,
  "doi": "10.48550/arXiv.1706.03762",
  "arxiv_id": "1706.03762",
  "source_filename": "1706.03762.pdf",
  "page_number": 4,
  "chunk_id": "8f3b110e-8f20-4e09-91dc-879e9508d812",
  "chunk_section": "3.2.1 Scaled Dot-Product Attention",
  "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
  "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
  "captured_at": "2026-09-17T03:00:00.000000Z"
}
```

**Lợi ích sản xuất:**
- Khi tài liệu gốc bị xóa, `documents` bị xóa bản ghi, nhưng `research_notes` không bao giờ mất thông tin nguồn trích dẫn.
- Khi người dùng xuất sổ tay ra Markdown/BibTeX, hệ thống luôn có đủ thông tin trích dẫn học thuật chuẩn xác mà không cần truy vấn bảng `documents`.

---

## 4. Tầng Miền Cốt Lõi & Giao Diện Cổng (Core Domain & Ports)

### 4.1. Domain Entities & Value Objects (`packages/core`)

1. **`BoundingBox` (Value Object):**
   - Chứa tọa độ chuẩn hóa `[ymin, xmin, ymax, xmax, page]`.
   - Invariant: `0.0 <= ymin <= ymax <= 1.0`, `0.0 <= xmin <= xmax <= 1.0`, `page >= 1`.
2. **`FrozenSnapshot` (Value Object):**
   - Đóng gói dữ liệu bài báo tại thời điểm chụp, không thể thay đổi sau khi khởi tạo (Frozen Dataclass).
3. **`ResearchNote` (Aggregate Root):**
   - Thuộc tính: `id`, `user_id`, `document_id`, `chunk_id`, `selected_text`, `bounding_boxes`, `page_number`, `user_note`, `tags`, `frozen_snapshot`, `is_source_detached`, `version`, `created_at`, `updated_at`.
   - Hành vi miền:
     - `update_content(user_note: str | None, tags: list[str], expected_version: int)`: Kiểm tra OCC invariant trước khi cập nhật.
     - `mark_source_detached()`: Đổi cờ `is_source_detached = True`.
     - `re_attach_source(new_document_id: UUID, new_chunk_id: UUID | None)`: Nối lại nguồn khi tài liệu được tải lại.
4. **`NoteSynthesis` (Aggregate Root):**
   - Thuộc tính: `id`, `user_id`, `title`, `mode`, `language`, `markdown_content`, `interactive_badges`, `source_note_ids`, `created_at`, `updated_at`.
5. **`InteractiveBadge` (Value Object):**
   - Thuộc tính: `badge_id`, `note_id`, `document_id`, `citation_label`, `page_number`, `bounding_boxes`, `quote_text`, `is_source_detached`.

### 4.2. Port Interfaces (`packages/core/ports/note.py`)

```python
class INotePort(ABC):
    """Port trừu tượng cho thao tác lưu trữ và truy vấn ghi chú cá nhân."""

    @abstractmethod
    async def create_note(self, note: ResearchNote) -> ResearchNote: ...

    @abstractmethod
    async def get_note_by_id(self, note_id: UUID, user_id: UUID) -> ResearchNote | None: ...

    @abstractmethod
    async def list_notes(
        self,
        user_id: UUID,
        document_id: UUID | None = None,
        tag: str | None = None,
        folder_id: UUID | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[ResearchNote], int]: ...

    @abstractmethod
    async def update_note(self, note: ResearchNote, expected_version: int) -> ResearchNote: ...

    @abstractmethod
    async def delete_note(self, note_id: UUID, user_id: UUID) -> bool: ...


class INoteSynthesisPort(ABC):
    """Port trừu tượng cho việc tổng hợp ghi chú bằng LLM và quản lý bài học."""

    @abstractmethod
    async def synthesize(
        self,
        notes: list[ResearchNote],
        mode: SynthesisMode,
        language: str,
        target_title: str | None,
    ) -> tuple[str, list[InteractiveBadge]]: ...

    @abstractmethod
    async def save_synthesis(self, synthesis: NoteSynthesis) -> NoteSynthesis: ...

    @abstractmethod
    async def get_synthesis_by_id(self, synthesis_id: UUID, user_id: UUID) -> NoteSynthesis | None: ...
```

---

## 5. Tầng Dịch Vụ Ứng Dụng & Luồng Nghiệp Vụ (Application Services)

### 5.1. Dịch Vụ Ghi Chú Cá Nhân (`NoteService`)

1. **`create_note` (Tạo ghi chú mới - API #16):**
   - Kiểm tra `document_id`: Nếu có truyền, xác thực quyền sở hữu của `user_id` qua `DocumentModel`.
   - Nếu tài liệu tồn tại: Trích xuất `title`, `authors`, `year`, `doi`, `arxiv_id`, `filename` để lập tức đóng gói vào `frozen_snapshot`.
   - Kiểm tra tính hợp lệ của `selected_text` (không được rỗng) và mảng `bounding_boxes`.
   - Khởi tạo `version = 1`, lưu vào DB, trả về entity kèm `ETag: "v1"`.
2. **`list_notes` (Danh sách ghi chú - API #17):**
   - Hỗ trợ lọc theo `document_id` (nếu xem ghi chú trong tab PDF hiện tại).
   - Hỗ trợ lọc theo `tag` bằng toán tử mảng PostgreSQL `tags @> ARRAY[:tag]`.
   - Hỗ trợ lọc theo `folder_id` (truy vấn kết hợp bảng `documents.folder_id`).
   - Phân trang chuẩn với `page` và `per_page` (mặc định 50, tối đa 100).
   - Trả về envelope `PaginatedResponseEnvelope[NoteListItemResponse]`.
3. **`get_note_detail` (Chi tiết ghi chú - API #18):**
   - Truy vấn ghi chú theo `id` và `user_id`. Nếu không tồn tại -> `404 Not Found`.
   - Trả về toàn bộ chi tiết bao gồm `frozen_snapshot`, `is_source_detached`, và header `ETag: "v{version}"`.
4. **`update_note` (Cập nhật ghi chú có OCC - API #19):**
   - Đọc header `If-Match`:
     - Nếu thiếu header -> Bắn lỗi `PreconditionRequiredError` (HTTP 428).
     - Bóc tách chuỗi version (ví dụ `"v2"` -> số nguyên `2`).
   - Thực hiện kiểm tra OCC: Nếu version trong DB khác `expected_version` -> Bắn lỗi `ConcurrencyConflictError` (HTTP 412).
   - Cập nhật `user_note` và/hoặc `tags`. Trigger DB tự động tăng `version` lên `expected_version + 1`.
   - Trả về đối tượng đã cập nhật kèm header `ETag: "v{new_version}"`.
5. **`delete_note` (Xóa ghi chú - API #20):**
   - Xóa an toàn theo `id` và `user_id`. Trả về `HTTP 204 No Content` mang tính chất lũy đẳng (Idempotent).

### 5.2. Dịch Vụ AI Tổng Hợp Tri Thức (`NoteSynthesisService` - API #21)

1. **Xác thực đầu vào:**
   - Client gửi mảng `note_ids: list[UUID]` (tối thiểu 1 ghi chú, khuyến nghị từ 2 - 30 ghi chú).
   - Hệ thống tải toàn bộ các ghi chú tương ứng thuộc sở hữu của `user_id`. Bỏ qua hoặc báo lỗi nếu có ID không hợp lệ.
2. **Orchestration Prompt Theo 3 Chế Độ (Synthesis Modes):**
   - **Chế độ 1: `concept_lesson` (Bài học khái niệm Feynman):**
     - Cấu trúc đầu ra: (1) Trực giác cốt lõi & Khái niệm đơn giản, (2) Công thức / Nguyên lý từng bước, (3) Ví dụ minh họa thực tế & Phản ví dụ, (4) Những hiểu lầm phổ biến cần tránh.
   - **Chế độ 2: `literature_review` (Đoạn văn Tổng quan học thuật):**
     - Cấu trúc đầu ra: Ma trận tổng hợp (Synthesis Matrix) so sánh các quan điểm khoa học, nhóm các tác giả đồng thuận/bất đồng thuận, văn phong học thuật trang trọng (in-text citation).
   - **Chế độ 3: `research_gap` (Phân tích khoảng trống nghiên cứu):**
     - Cấu trúc đầu ra: (1) Những giả định chưa được chứng minh đầy đủ, (2) Giới hạn của tập dữ liệu / phương pháp đo lường, (3) Cơ hội phát triển đề tài nghiên cứu mới.
3. **Cơ chế Gắn Huy Hiệu Trích Dẫn Tương Tác (Interactive Citation Badges):**
   - Khi gửi ngữ cảnh vào LLM, mỗi ghi chú được gán một token định danh duy nhất:
     `[NOTE_INDEX: 1 | ID: uuid1 | Doc: Attention Is All You Need | Page: 4]`
   - Yêu cầu LLM khi đưa ra một luận điểm hoặc công thức phải trích xuất đúng thẻ `[[badge:uuid1]]`.
   - Hậu xử lý (Post-Processing): Bộ phân tích cú pháp (Parser) bóc tách các thẻ `[[badge:uuid1]]`, đối chiếu với dữ liệu ghi chú để sinh ra danh sách `InteractiveBadge`:
     ```json
     {
       "badge_id": "badge_1",
       "note_id": "3d10c24e-7212-40f9-b883-cf3da8490a15",
       "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
       "citation_label": "Vaswani et al., 2017 • Tr. 4",
       "page_number": 4,
       "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
       "quote_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
       "is_source_detached": false
     }
     ```
   - Trong văn bản Markdown, thẻ được thay thế bằng dạng badge tương tác tương thích trình render frontend:
     `[^1: Vaswani et al., 2017 • Tr. 4]`
4. **Lưu trữ & Phản hồi:**
   - Kết quả được lưu vào bảng `note_syntheses`.
   - Trả về payload hoàn chỉnh cho frontend kèm tiêu đề, định dạng Markdown, danh sách badges và thời gian tạo.

---

## 6. Driving Adapters & Đặc Tả API Hợp Đồng (FastAPI Routers & Schemas)

### 6.1. Endpoint #16: `POST /api/v1/notes` (Lưu Trích Dẫn & Ghi Chú Cá Nhân)

- **Đường dẫn:** `POST /api/v1/notes`
- **Mã HTTP:** `201 Created`
- **Headers:** `Location: /api/v1/notes/{id}`, `ETag: "v1"`
- **Request Body (JSON):**
  ```json
  {
    "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "chunk_id": "8f3b110e-8f20-4e09-91dc-879e9508d812",
    "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
    "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
    "page_number": 4,
    "user_note": "Công thức cốt lõi cần dùng cho phần phương pháp.",
    "tags": ["methodology", "core-formula"]
  }
  ```
- **Response Payload (`201 Created`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "3d10c24e-7212-40f9-b883-cf3da8490a15",
      "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "chunk_id": "8f3b110e-8f20-4e09-91dc-879e9508d812",
      "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
      "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
      "page_number": 4,
      "user_note": "Công thức cốt lõi cần dùng cho phần phương pháp.",
      "tags": ["methodology", "core-formula"],
      "frozen_snapshot": {
        "document_title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani et al."],
        "year": 2017,
        "doi": "10.48550/arXiv.1706.03762",
        "arxiv_id": "1706.03762",
        "page_number": 4
      },
      "is_source_detached": false,
      "version": 1,
      "created_at": "2026-09-17T03:10:00.000000Z",
      "updated_at": "2026-09-17T03:10:00.000000Z"
    },
    "meta": {
      "request_id": "req_a1b2c3d4e5f6",
      "timestamp": "2026-09-17T03:10:00.005000Z"
    }
  }
  ```

---

### 6.2. Endpoint #17: `GET /api/v1/notes` (Danh Sách Ghi Chú Có Phân Trang & Bộ Lọc)

- **Đường dẫn:** `GET /api/v1/notes`
- **Query Parameters:**
  - `document_id`: UUID (Tùy chọn - lọc theo bài báo)
  - `tag`: String (Tùy chọn - lọc theo thẻ học thuật)
  - `folder_id`: UUID (Tùy chọn - lọc theo thư mục đề tài)
  - `page`: Int (Mặc định: 1)
  - `per_page`: Int (Mặc định: 50, tối đa: 100)
- **Response Payload (`200 OK` - Paginated Collection Envelope):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "3d10c24e-7212-40f9-b883-cf3da8490a15",
        "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "document_title": "Attention Is All You Need",
        "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
        "page_number": 4,
        "user_note": "Công thức cốt lõi cần dùng cho phần phương pháp.",
        "tags": ["methodology", "core-formula"],
        "is_source_detached": false,
        "version": 1,
        "created_at": "2026-09-17T03:10:00.000000Z",
        "updated_at": "2026-09-17T03:10:00.000000Z"
      }
    ],
    "meta": {
      "total": 1,
      "page": 1,
      "per_page": 50,
      "total_pages": 1,
      "request_id": "req_b2c3d4e5f6a1",
      "timestamp": "2026-09-17T03:10:05.000000Z"
    },
    "links": {
      "first": "/api/v1/notes?page=1&per_page=50",
      "prev": null,
      "self": "/api/v1/notes?page=1&per_page=50",
      "next": null,
      "last": "/api/v1/notes?page=1&per_page=50"
    }
  }
  ```

---

### 6.3. Endpoint #18: `GET /api/v1/notes/{id}` (Chi Tiết Ghi Chú Kèm Frozen Snapshot)

- **Đường dẫn:** `GET /api/v1/notes/{id}`
- **Headers Trả Về:** `ETag: "v1"`
- **Response Payload (`200 OK`):**
  - Trả về toàn bộ chi tiết bao gồm `bounding_boxes` và `frozen_snapshot` đầy đủ.

---

### 6.4. Endpoint #19: `PATCH /api/v1/notes/{id}` (Cập Nhật Ghi Chú / Tag - OCC If-Match)

- **Đường dẫn:** `PATCH /api/v1/notes/{id}`
- **Headers Bắt Buộc:** `If-Match: "v1"` (hoặc `"1"`)
- **Request Body (JSON):**
  ```json
  {
    "user_note": "Đã đối chiếu với mã nguồn gốc của Tensor2Tensor.",
    "tags": ["methodology", "verified", "core-formula"]
  }
  ```
- **Xử lý mã lỗi:**
  - `428 Precondition Required`: Khi thiếu header `If-Match`.
  - `412 Precondition Failed`: Khi version truyền vào khác với version hiện tại trong DB (`CONCURRENCY_CONFLICT`).
- **Response Payload (`200 OK`):**
  - Trả về note đã cập nhật, trường `version` tăng lên `2`, header `ETag: "v2"`.

---

### 6.5. Endpoint #20: `DELETE /api/v1/notes/{id}` (Xóa Ghi Chú Khỏi Sổ Tay)

- **Đường dẫn:** `DELETE /api/v1/notes/{id}`
- **Mã HTTP:** `204 No Content` (Empty body).
- **Tính chất:** Lũy đẳng (Idempotent) - xóa ghi chú không ảnh hưởng đến tài liệu PDF gốc.

---

### 6.6. Endpoint #21: `POST /api/v1/notes:synthesize` (AI Tổng Hợp Ghi Chú Thành Bản Đúc Kết)

- **Đường dẫn:** `POST /api/v1/notes:synthesize` (Custom Verb theo Google AIP-136)
- **Headers:** `Idempotency-Key: <UUID>` (Tùy chọn)
- **Request Body (JSON):**
  ```json
  {
    "note_ids": [
      "3d10c24e-7212-40f9-b883-cf3da8490a15",
      "4e21d35f-8323-41a0-c994-df4eb9501b26"
    ],
    "mode": "concept_lesson",
    "language": "vi",
    "target_title": "Bản Đúc Kết Cơ Chế Scaled Dot-Product Attention"
  }
  ```
- **Response Payload (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d",
      "title": "Bản Đúc Kết Cơ Chế Scaled Dot-Product Attention",
      "mode": "concept_lesson",
      "language": "vi",
      "markdown_content": "# Bài Học: Cơ Chế Scaled Dot-Product Attention\n\n## 1. Bản Chất Trực Quan\nCơ chế Attention hoạt động như một hệ thống tra cứu từ điển mềm [^1]. Thay vì tìm kiếm cứng, nó gán trọng số tương quan giữa truy vấn và các khóa...\n\n## 2. Công Thức Cốt Lõi\n$$Attention(Q, K, V) = softmax\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$\n\nYếu tố $\\sqrt{d_k}$ đóng vai trò điều hòa phương sai để ngăn chặn gradient biến mất [^2].",
      "interactive_badges": [
        {
          "badge_id": "badge_1",
          "note_id": "3d10c24e-7212-40f9-b883-cf3da8490a15",
          "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
          "citation_label": "Vaswani et al., 2017 • Tr. 4",
          "page_number": 4,
          "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
          "quote_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
          "is_source_detached": false
        }
      ],
      "source_note_ids": [
        "3d10c24e-7212-40f9-b883-cf3da8490a15",
        "4e21d35f-8323-41a0-c994-df4eb9501b26"
      ],
      "created_at": "2026-09-17T03:15:00.000000Z",
      "updated_at": "2026-09-17T03:15:00.000000Z"
    },
    "meta": {
      "request_id": "req_c3d4e5f6a1b2",
      "timestamp": "2026-09-17T03:15:02.500000Z"
    }
  }
  ```

---

## 7. Các Ý Tưởng Nâng Cấp Giá Trị Cao Đề Xuất Bổ Sung (Value-Added Enhancements)

Sau khi nghiên cứu sâu các công cụ Obsidian, Logseq, Zotero 7 và Notion AI, chúng tôi đề xuất **3 nâng cấp kỹ thuật thực sự giá trị** để đưa Smart Notebook của VeriScholar lên tầm đẳng cấp thế giới:

1. **Ý tưởng Nâng cấp 1: Cơ Chế Tái Kết Nối Nguồn Trích Dẫn Thông Minh (`POST /api/v1/notes/{id}:re-attach`):**
   - *Tình huống:* Người dùng lỡ tay xóa file PDF, note chuyển sang `is_source_detached = true`. Vài ngày sau, người dùng tải lại bài báo đó lên hệ thống.
   - *Nâng cấp:* Cung cấp endpoint hỗ trợ đối chiếu hash nội dung hoặc DOI/arXiv ID. Nếu trùng khớp, hệ thống tự động tái liên kết `document_id` mới vào ghi chú, khôi phục lại khả năng nhấp chuột nhảy highlight trực tiếp trên PDF Canvas!
2. **Ý tưởng Nâng cấp 2: Xuất Sổ Tay Sang Markdown Chuẩn Obsidian & Logseq (`GET /api/v1/notes:export?format=obsidian`):**
   - *Nâng cấp:* Hỗ trợ xuất toàn bộ ghi chú và bài học tổng hợp thành tệp `.md` đính kèm YAML Frontmatter chuẩn học thuật:
     ```yaml
     ---
     title: "Attention Is All You Need"
     authors: ["Ashish Vaswani", "Noam Shazeer"]
     year: 2017
     doi: "10.48550/arXiv.1706.03762"
     citekey: "vaswani2017attention"
     tags: ["#methodology", "#deeplearning"]
     ---
     ```
     Giúp nhà nghiên cứu lập tức đồng bộ vào Second Brain cá nhân (Zettelkasten / PKM) mà không tốn công biên tập lại.
3. **Ý tưởng Nâng cấp 3: Tương Thích Chuẩn W3C Web Annotation JSON-LD (`GET /api/v1/notes/{id}/w3c`):**
   - *Nâng cấp:* Cho phép xuất annotation theo chuẩn `application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"`, tương thích trực tiếp với Hypothes.is và PDF.js native annotation export.

---

## 8. Chiến Lược Kiểm Thử, Autotest Snapshot & Đánh Giá Không Gian Lận

Tuân thủ nghiêm ngặt [`docs/vi/design-api-eval-snapshots.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-api-eval-snapshots.md), hệ thống kiểm chuẩn gồm 2 tầng:

### 8.1. Tầng 1: Pytest Unit & Integration Tests (`apps/api/tests/`)
- `test_notes_crud.py`:
  - Kiểm thử tạo note thành công với đầy đủ bounding boxes, page number, tags.
  - Kiểm thử lưu trữ `frozen_snapshot` nguyên vẹn khi tạo.
  - Kiểm thử danh sách ghi chú với các bộ lọc `document_id`, `tag`, `folder_id` và phân trang.
  - Kiểm thử OCC `If-Match`:
    - Thiếu `If-Match` -> `428 Precondition Required`.
    - `If-Match` sai lệch -> `412 Precondition Failed` (`CONCURRENCY_CONFLICT`).
    - `If-Match` đúng -> `200 OK`, `version` tăng nguyên tử lên 2, trả về `ETag: "v2"`.
  - Kiểm thử xóa note thành công (`204 No Content`), kiểm tra bảo vệ tài liệu PDF gốc không bị xóa.
  - Kiểm thử cô lập dữ liệu người dùng (Multi-tenant isolation: người dùng A không thể đọc/sửa/xóa note của người dùng B -> trả về `404 Not Found`).
- `test_notes_synthesize.py`:
  - Kiểm thử tổng hợp 3 chế độ: `concept_lesson`, `literature_review`, `research_gap`.
  - Kiểm thử trích xuất và ánh xạ đúng mảng `interactive_badges`.
  - Kiểm thử khi ghi chú trong danh sách ở trạng thái `is_source_detached = true` thì badge vẫn bảo toàn thông tin và không gây lỗi crash.

### 8.2. Tầng 2: Autotest Snapshot Runner & Báo Cáo Tự Động (`scripts/eval/`)
- Xây dựng runner chuyên biệt: `scripts/eval/runners/notes_and_synthesis_runner.py`.
- Đăng ký alias trong `scripts/eval/runners/__init__.py`: `notes`, `smart-notes`, `notes-synthesis`.
- Runner thực thi trên PostgreSQL thực tế gồm 12 kịch bản:
  1. `POST /api/v1/notes` (Tạo note kèm frozen snapshot và bounding boxes) -> `201`
  2. `GET /api/v1/notes` (Lấy danh sách, phân trang envelope) -> `200`
  3. `GET /api/v1/notes?tag=methodology` (Lọc theo thẻ qua GIN index) -> `200`
  4. `GET /api/v1/notes/{id}` (Chi tiết note, kiểm tra snapshot và ETag) -> `200`
  5. `PATCH /api/v1/notes/{id}` (Thiếu If-Match) -> `428`
  6. `PATCH /api/v1/notes/{id}` (If-Match lỗi thời "v999") -> `412`
  7. `PATCH /api/v1/notes/{id}` (If-Match hợp lệ "v1") -> `200`, version = 2
  8. `POST /api/v1/notes:synthesize` (Chế độ concept_lesson) -> `200`
  9. `POST /api/v1/notes:synthesize` (Chế độ literature_review) -> `200`
  10. `POST /api/v1/notes:synthesize` (Chế độ research_gap) -> `200`
  11. `DELETE /api/v1/documents/{doc_id}` -> Xác minh trigger `trg_research_notes_detached` kích hoạt `is_source_detached = true` trên note tương ứng!
  12. `DELETE /api/v1/notes/{id}` (Xóa note) -> `204` -> `GET` lại trả về `404`
- Tạo báo cáo tự động: `temp/output/test/notes_and_synthesis.md` kèm mã băm SHA-256 đối soát chống fake report.

---

## 9. Rà Soát Biến Môi Trường & An Toàn Vận Hành

1. **Rà soát `.env.example`:**
   - Đã kiểm tra tệp `.env.example`: Hệ thống hiện tại đã có đầy đủ cấu hình cho PostgreSQL (`DATABASE_URL`), Redis, và LLM Inference (`LLM_PROVIDER`, `DMR_BASE_URL`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).
   - **Kết luận:** TARGET này KHÔNG cần thêm biến môi trường mới nào vào `.env.example`. Không đọc tệp `.env`.
2. **Quy tắc an toàn Git & Quy trình duyệt:**
   - Tuyệt đối KHÔNG tự ý chạy `git add`, `git commit` hoặc tạo Pull Request.
   - Khi được người dùng phê duyệt, sẽ tạo và chuyển sang nhánh mới:
     `git checkout -b feat/m1-notes-and-knowledge-digest`
   - Tuyệt đối KHÔNG tạo endpoint backdoor `/api/v1/testing/...`.
   - Toàn bộ các tiến trình terminal ngầm đã được dọn dẹp sạch sẽ.

---

## 10. Kế Hoạch Triển Khai Chi Tiết (Khi Được Phê Duyệt)

| Giai đoạn | Nội dung công việc cụ thể | Tệp tin tác động chính |
|---|---|---|
| **P1. Database & Migrations** | Định nghĩa SQLAlchemy Models `ResearchNoteModel`, `NoteSynthesisModel`; cập nhật `init_db.py` với DDL và triggers OCC/Detached. | `apps/api/src/api/db/models/note.py`, `apps/api/src/api/db/models/__init__.py`, `apps/api/src/api/db/init_db.py` |
| **P2. Domain Layer** | Tạo Domain Entities, Value Objects (`BoundingBox`, `FrozenSnapshot`, `InteractiveBadge`) và Port Interfaces. | `packages/core/src/core/domain/entities/note.py`, `packages/core/src/core/domain/entities/note_synthesis.py`, `packages/core/src/core/ports/note.py` |
| **P3. Application Services** | Triển khai `NoteService` (CRUD, OCC If-Match, filtering) và `NoteSynthesisService` (3 synthesis modes, prompt template, badge extractor). | `apps/api/src/api/services/note_service.py`, `apps/api/src/api/services/note_synthesis_service.py` |
| **P4. Driving Routers** | Tạo Router `notes.py` (6 endpoints #16 - #21), Schemas Pydantic v2, dependency injection. | `apps/api/src/api/v1/endpoints/notes.py`, `apps/api/src/api/schemas/note.py`, `apps/api/src/api/v1/api.py`, `apps/api/src/api/deps.py` |
| **P5. Testing Suite** | Viết bộ Unit & Integration tests đạt độ bao phủ >= 80%. | `apps/api/tests/test_notes_crud.py`, `apps/api/tests/test_notes_synthesize.py` |
| **P6. Eval Harness** | Xây dựng Snapshot Runner 12 kịch bản, đăng ký vào `eval_api.py`, tạo báo cáo snapshot. | `scripts/eval/runners/notes_and_synthesis_runner.py`, `scripts/eval/runners/__init__.py` |
| **P7. Documentation** | Bổ sung đặc tả kỹ thuật chi tiết 6 endpoints vào `swagger.md`, cập nhật `design-api-eval-snapshots.md`. | `docs/vi/swagger.md`, `docs/vi/design-api-eval-snapshots.md` |

# ĐẶC TẢ KỸ THUẬT NỀN TẢNG: KIẾN TRÚC HỆ THỐNG, CSDL 16 BẢNG & LƯU TRỮ CAS
# (FILE 00: FOUNDATION ARCHITECTURE, POSTGRESQL SCHEMA & CAS STORAGE SPEC)

**Trạng thái:** DỰ THẢO CHÍNH THỨC (TECHNICAL SPECIFICATION V1)  
**Nguồn tham chiếu PRD:** [`docs/PRD/00-overview-and-cleanup.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/PRD/00-overview-and-cleanup.md)  
**Module liên đới:** Toàn bộ hệ thống (`specs/01` $\rightarrow$ `specs/07`)

---

## 1. Ranh Giới Kiến Trúc Lục Giác & Ràng Buộc Toàn Cục (Hexagonal Boundaries & Invariants)

Hệ thống VeriScholar tuân thủ nghiêm ngặt mô hình **Kiến trúc Lục giác (Hexagonal Architecture / Ports & Adapters)** trong monorepo `uv workspace`:

```mermaid
flowchart LR
    subgraph DrivingAdapters ["<b>Driving Adapters (apps/api)</b>"]
        FastAPI["FastAPI HTTP Endpoints<br/>(AIP-136 REST / JSON)"]
        SSEStream["Unbuffered SSE Stream<br/>(Chat RAG & Agent Writing)"]
        AuthMiddleware["JWT & Rate-Limit Middleware<br/>(Redis 7 OTP)"]
    end

    subgraph CoreDomain ["<b>Core Business Domain (packages/core)</b>"]
        Entities["Domain Entities & VOs<br/>(User, Document, Chunk, Draft...)"]
        Ports["Abstract Ports (Interfaces)<br/>(ILatexCompilerPort, IDocumentStoragePort...)"]
        BusinessServices["Domain Logic & AST Linters<br/>(FastLatexAstLinter, ChunkTokenizer)"]
    end

    subgraph DrivenAdapters ["<b>Driven Adapters (apps/api)</b>"]
        PG["PostgreSQL 16+ pgvector<br/>(16 Tables, HNSW & GIN Indexes)"]
        CASDisk["CAS File Storage<br/>(storage/blobs/ SHA-256)"]
        RedisClient["Redis 7 Client<br/>(OTP, Idempotency, Session Locks)"]
        E2BClient["E2B Sandbox Runner<br/>(Isolated Firecracker Micro-VM)"]
        ExaClient["Exa AI & arXiv SDK<br/>(Scholarly Search Adapters)"]
        LangfuseClient["Langfuse Tracing SDK<br/>(PureASGITracingMiddleware)"]
    end

    FastAPI --> Ports
    SSEStream --> Ports
    AuthMiddleware --> Ports
    Ports --> Entities
    BusinessServices --> Entities

    PG -.implements.-> Ports
    CASDisk -.implements.-> Ports
    RedisClient -.implements.-> Ports
    E2BClient -.implements.-> Ports
    ExaClient -.implements.-> Ports
    LangfuseClient -.implements.-> Ports
```

### A. Ràng Buộc Bất Biến Của Core (`packages/core`)
1. **Thuần Python (Pure Python 3.12):** `packages/core/src/core/domain/` và `packages/core/src/core/ports/` tuyệt đối **không được import** bất kỳ thư viện framework nào: cấm `fastapi`, `sqlalchemy`, `httpx`, `fitz` (`pymupdf`), `redis`, `langfuse`, `e2b`.
2. **Quy tắc phụ thuộc một chiều (Dependency Inversion):** Mọi chiều phụ thuộc chỉ đi từ ngoài (`apps/api`) vào trong (`packages/core`). Core định nghĩa các giao diện trừu tượng (`Ports`), Adapters trong API cài đặt các giao diện đó.
3. **Tốc độ thực thi Unit Test:** Mọi bài test trong `packages/core/tests/` phải chạy độc lập trên RAM với Fake/Mock ports, không mở socket mạng và không phụ thuộc CSDL (tổng thời gian chạy `< 1 giây`).

### B. Ràng Buộc Bất Biến Của Adapters & API (`apps/api`)
1. **Cô lập Đa người dùng Tuyệt đối (Multi-Tenant Isolation):**
   Mọi bảng dữ liệu nghiệp vụ đều có khóa ngoại `user_id FK users.id ON DELETE CASCADE`. Mọi câu lệnh SQL truy vấn hoặc thao tác dữ liệu đều bắt buộc có điều kiện lọc:
   $$\text{WHERE } user_id = :current\_user\_id$$
   Cố gắng truy cập tài nguyên của người dùng khác hoặc tài nguyên không tồn tại phải trả về mã lỗi `404 NOT_FOUND` đồng nhất (tránh lộ thông tin tồn tại qua `403`).
2. **Tô pô Tiến trình Đơn máy chủ (Single Async Uvicorn Worker Topology):**
   Trên môi trường máy chủ đơn (VPS), API chạy duy nhất **1 async Uvicorn worker** để đảm bảo bộ đếm metrics trong RAM (`PureASGITracingMiddleware`), cache xem trước và các tác vụ ngầm không bị phân mảnh thành nhiều không gian nhớ độc lập.
3. **Phân Vùng Tác Vụ Ngầm (BackgroundTasks Session Safety):**
   Mọi tác vụ chạy ngầm qua `BackgroundTasks` (tải PDF Tầng 2, trích xuất GraphRAG) **tuyệt đối không dùng chung `AsyncSession` của HTTP request** (vì session này sẽ bị đóng khi request kết thúc). Tác vụ ngầm phải tự mở `AsyncSessionLocal()` độc lập trong context manager `async with`.

---

## 2. Kiểm Kê Toàn Diện & Lược Đồ 16 Bảng CSDL PostgreSQL 16+

Toàn bộ hệ thống VeriScholar MVP gồm đúng **16 bảng PostgreSQL** (12 bảng hiện có + 4 bảng tạo mới trong `Delta`).

```mermaid
erDiagram
    users ||--o{ documents : owns
    users ||--o{ research_sessions : creates
    users ||--o{ folders : organizes
    users ||--o{ drafts : writes
    users ||--o{ research_notes : writes
    users ||--o{ graph_nodes : extracts
    users ||--o{ graph_edges : links

    document_storage_blobs ||--o{ documents : stores_pdf
    document_storage_blobs ||--o{ draft_assets : stores_asset

    documents ||--o{ document_chunks : contains
    documents ||--o| document_summaries : summarizes
    documents ||--o{ reference_items : references
    documents ||--o{ session_documents : joins
    documents ||--o{ graph_nodes : anchors

    research_sessions ||--o{ session_documents : includes
    research_sessions ||--o{ session_turns : records
    research_sessions ||--o{ research_notes : attaches
    research_sessions ||--o{ drafts : derives

    drafts ||--o{ draft_assets : holds
    drafts ||--o{ draft_messages : history

    graph_nodes ||--o{ graph_edges : source
    graph_nodes ||--o{ graph_edges : target
```

### A. Danh Mục 12 Bảng Hiện Có (`As-Is` $\rightarrow$ `Refactor`)

| # | Bảng PostgreSQL | File Model hiện tại | Trạng thái | Nâng cấp cần thực hiện trong `Delta` |
|---|---|---|---|---|
| **1** | `users` | [`user.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/user.py) | **MODIFY** | Bổ sung cột `theme_preference VARCHAR(20) DEFAULT 'system'`, `byok_api_key_encrypted TEXT NULL`. |
| **2** | `documents` | [`document.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/document.py) | **MODIFY** | Bổ sung cột `is_starred BOOLEAN DEFAULT FALSE INDEX`, `folder_id UUID FK folders.id SET NULL`. |
| **3** | `document_chunks` | [`chunk.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/chunk.py) | **MODIFY** | Bổ sung cột `user_id UUID FK users.id CASCADE INDEX`, chuyển `embedding` từ `JSONType` sang `Vector(1536)` kèm chỉ mục `HNSW`, thêm cột `content_tsv TSVECTOR` kèm chỉ mục `GIN`. |
| **4** | `document_storage_blobs` | [`blob.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/blob.py) | **KEEP** | Lưu trữ mã băm SHA-256 (`content_hash`), kích thước byte, đường dẫn lưu file, và bộ đếm `ref_count`. |
| **5** | `document_summaries` | [`summary.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/summary.py) | **KEEP** | Tóm tắt 3 phần (Problem, Contribution, Limitations) gắn trích dẫn Bounding Box. |
| **6** | `reference_items` | [`reference.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/reference.py) | **KEEP** | Danh mục tài liệu tham khảo bóc tách từ cuối bài báo (DOI, arXiv, title, authors, year). |
| **7** | `research_sessions` | [`session.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/session.py) | **KEEP** | Phiên đọc sâu đa bài báo (1–5 PDF đồng thời), lưu trạng thái viewport và active tab. |
| **8** | `session_documents` | [`session.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/session.py) | **KEEP** | Bảng liên kết Many-to-Many giữa `research_sessions` và `documents`, kiểm soát giới hạn 5 bài. |
| **9** | `session_turns` | [`session.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/session.py) | **MODIFY** | Bổ sung cột `trace_id VARCHAR(64) NULL` để gắn kết trực tiếp với vết giám sát Langfuse. |
| **10** | `research_notes` | [`note.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/note.py) | **KEEP** | Ghi chú học thuật có đối chiếu Bounding Box và bản chụp chứng cứ đóng băng (`frozen_snapshot`). |
| **11** | `folders` | [`folder.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/folder.py) | **KEEP** | Cây thư mục đề tài phân cấp trong Kho Yêu thích (`parent_id FK folders.id CASCADE`). |
| **12** | `drafts` | [`draft.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/models/draft.py) | **MODIFY** | Bổ sung cột `bib_content TEXT DEFAULT ''`, `source_session_id UUID FK research_sessions.id SET NULL`, `pdf_preview_storage_path TEXT NULL`, `previous_snapshot JSONB NULL`. |

---

### B. Danh Mục 4 Bảng Tạo Mới (`Delta`)

#### 13. Bảng `graph_nodes` (Đỉnh Tri Thức GraphRAG 4 Thực Thể)
- **Vị trí file:** `apps/api/src/api/db/models/graph.py`
- **Mục đích:** Lưu trữ các thực thể học thuật được trích xuất từ bài báo khoa học phục vụ tìm kiếm ngữ nghĩa và tổng hợp tri thức chéo.
```sql
CREATE TABLE graph_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    node_type VARCHAR(30) NOT NULL CHECK (node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult')),
    canonical_name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_chunk_id UUID NULL REFERENCES document_chunks(id) ON DELETE SET NULL,
    page_number INT NULL,
    embedding vector(1536) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_graph_nodes_user_doc ON graph_nodes(user_id, document_id);
CREATE INDEX idx_graph_nodes_user_type ON graph_nodes(user_id, node_type);
CREATE INDEX idx_graph_nodes_embedding ON graph_nodes USING hnsw (embedding vector_cosine_ops);
```

#### 14. Bảng `graph_edges` (Cạnh Quan Hệ GraphRAG 4 Loại Cố Định)
- **Vị trí file:** `apps/api/src/api/db/models/graph.py`
- **Mục đích:** Kết nối các đỉnh tri thức theo 4 quan hệ học thuật chuẩn mực.
```sql
CREATE TABLE graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_node_id UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    edge_type VARCHAR(30) NOT NULL CHECK (edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')),
    evidence_chunk_id UUID NULL REFERENCES document_chunks(id) ON DELETE SET NULL,
    page_number INT NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_graph_edges_user_source ON graph_edges(user_id, source_node_id);
CREATE INDEX idx_graph_edges_user_target ON graph_edges(user_id, target_node_id);
CREATE INDEX idx_graph_edges_user_type ON graph_edges(user_id, edge_type);
```

#### 15. Bảng `draft_assets` (Tài Sản & Hình Ảnh Bản Thảo LaTeX)
- **Vị trí file:** `apps/api/src/api/db/models/draft_asset.py`
- **Mục đích:** Quản lý các file đính kèm trong thư mục `figures/` của bản thảo, tích hợp Content-Addressable Storage.
```sql
CREATE TABLE draft_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL CHECK (mime_type IN ('image/png', 'image/jpeg', 'image/webp', 'application/pdf')),
    file_size_bytes BIGINT NOT NULL,
    blob_id UUID NULL REFERENCES document_storage_blobs(id) ON DELETE SET NULL,
    storage_path TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_draft_assets_draft_filename UNIQUE (draft_id, filename)
);

CREATE INDEX idx_draft_assets_user_draft ON draft_assets(user_id, draft_id);
```

#### 16. Bảng `draft_messages` (Lịch Sử Hội Thoại Với LangGraph Writing Agent)
- **Vị trí file:** `apps/api/src/api/db/models/draft_message.py`
- **Mục đích:** Lưu trữ lịch sử hội thoại trợ lý AI bên Cột 3 của không gian viết bài, kèm dấu vết công cụ và lượt biên dịch.
```sql
CREATE TABLE draft_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB NULL,
    compile_attempts SMALLINT NOT NULL DEFAULT 0,
    trace_id VARCHAR(64) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_draft_messages_user_draft_time ON draft_messages(user_id, draft_id, created_at);
```

---

## 3. Quản Lý Lưu Trữ File Vật Lý (Content-Addressable Storage — CAS)

Hệ thống sử dụng cơ chế lưu trữ nội dung định danh theo băm (**Content-Addressable Storage - CAS**) tại `storage/blobs/`:

```text
storage/blobs/
├── e3/
│   └── b0/
│       └── e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.pdf
└── 4f/
    └── a1/
        └── 4fa1...892.png
```

### A. Thuật Toán Sinh Khóa & Đường Dẫn
1. Mọi file nhị phân (PDF tải lên hoặc ảnh figures) đều được tính băm SHA-256 trên nội dung thô:
   $$\text{hash} = \text{SHA-256}(\text{raw\_bytes})$$
2. Đường dẫn lưu trữ được phân tán theo 2 ký tự đầu và 2 ký tự kế tiếp để tránh nghẽn inode filesystem:
   $$\text{path} = \text{storage/blobs/} + \text{hash}[0:2] + \text{/} + \text{hash}[2:4] + \text{/} + \text{hash} + \text{ext}$$

### B. Vòng Đời & Tiêu Hủy Đồng Bộ (Zero-Retention Guarantee)
1. **Khử trùng lặp khi ghi (Upload Deduplication):**
   - Khi người dùng nạp file, kiểm tra trong `document_storage_blobs` theo `content_hash`.
   - Nếu đã tồn tại file: Tăng `ref_count += 1` và trỏ bản ghi mới vào `blob_id` sẵn có mà không ghi thêm file vật lý xuống đĩa.
2. **Tiêu hủy tức thì khi xóa (Synchronous Purge):**
   - Khi người dùng xóa tài liệu (`DELETE /api/v1/documents/{id}`):
   - Xóa thực thể `documents` (PostgreSQL cascade xóa chunks, summaries, references).
   - Kiểm tra `document_storage_blobs`: giảm `ref_count -= 1`.
   - Khi `ref_count <= 0`: Xóa bản ghi trong `document_storage_blobs` và gọi `unlink` xóa ngay file vật lý trên đĩa. Không để lại file mồ côi.

---

## 4. Cơ Chế Khởi Tạo CSDL Idempotent (`ensure_database_schema`)

Dự án không duy trì hệ thống migration Alembic đa phiên bản phức tạp cho cấu trúc đơn giản của MVP. Thay vào đó, toàn bộ quy trình khởi tạo và vá cột được tự động thực thi khi API khởi động thông qua hàm `ensure_database_schema()` trong [`init_db.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/api/src/api/db/init_db.py):

```python
async def ensure_database_schema(engine: AsyncEngine) -> None:
    """Idempotently bootstrap and patch PostgreSQL database schema."""
    async with engine.begin() as conn:
        # 1. Bật extension pgvector bắt buộc
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # 2. Tạo toàn bộ 16 bảng nếu chưa tồn tại
        await conn.run_sync(Base.metadata.create_all)

        # 3. Vá cột mới an toàn trên các volume CSDL cũ (Idempotent ALTER TABLE)
        ddl_patches = [
            # Nâng cấp users
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS theme_preference VARCHAR(20) DEFAULT 'system';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS byok_api_key_encrypted TEXT NULL;",

            # Nâng cấp documents
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_starred BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS folder_id UUID NULL REFERENCES folders(id) ON DELETE SET NULL;",

            # Nâng cấp document_chunks (Hybrid RAG)
            "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS user_id UUID NULL REFERENCES users(id) ON DELETE CASCADE;",
            "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;",

            # Nâng cấp drafts
            "ALTER TABLE drafts ADD COLUMN IF NOT EXISTS bib_content TEXT DEFAULT '';",
            "ALTER TABLE drafts ADD COLUMN IF NOT EXISTS source_session_id UUID NULL REFERENCES research_sessions(id) ON DELETE SET NULL;",
            "ALTER TABLE drafts ADD COLUMN IF NOT EXISTS pdf_preview_storage_path TEXT NULL;",
            "ALTER TABLE drafts ADD COLUMN IF NOT EXISTS previous_snapshot JSONB NULL;",

            # Nâng cấp session_turns
            "ALTER TABLE session_turns ADD COLUMN IF NOT EXISTS trace_id VARCHAR(64) NULL;",
        ]

        for ddl in ddl_patches:
            try:
                await conn.execute(text(ddl))
            except Exception as e:
                logger.warning("schema_patch_warning", ddl=ddl, error=str(e))

        # 4. Tạo chỉ mục HNSW và GIN nếu chưa có
        index_patches = [
            "CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);",
            "CREATE INDEX IF NOT EXISTS idx_chunks_content_tsv_gin ON document_chunks USING gin (content_tsv);",
            "CREATE INDEX IF NOT EXISTS idx_documents_starred ON documents(user_id, is_starred);",
        ]
        for idx in index_patches:
            await conn.execute(text(idx))
```

> [!CAUTION]
> **Loại bỏ vĩnh viễn SQLite Fallback:**  
> Tuyệt đối không gọi hàm `init_sqlite_fallback()` hay import `aiosqlite`. Nếu kết nối PostgreSQL thất bại lúc khởi động, API bắt buộc phải fail-fast với thông điệp lỗi rõ ràng yêu cầu người vận hành kiểm tra container PostgreSQL.

---

## 5. Cấu Hình Môi Trường & Tô Pô Vận Hành (Configuration & Topology)

### A. Bảng Biến Môi Trường Cốt Lõi (`.env`)

| Tên biến môi trường | Giá trị chuẩn mực | Mục đích sử dụng |
|---|---|---|
| `ENVIRONMENT` | `development` hoặc `production` | Duy nhất 2 môi trường; kiểm thử tự gán `ENVIRONMENT=test`. |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/verischolar` | Chuỗi kết nối PostgreSQL 16+ kèm `pgvector`. |
| `TEST_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/verischolar_test` | Database riêng biệt cho pytest integration tests. |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache OTP, khóa Idempotency và rate-limiting. |
| `JWT_SECRET_KEY` | Hex string 64 ký tự ngẫu nhiên | Ký và xác thực token JWT người dùng. |
| `BYOK_ENCRYPTION_KEY` | Hex string 32 bytes (256 bits) | Khóa chủ server dùng mã hóa AES-256-GCM các khóa cá nhân của user. |
| `EMBEDDING_PROVIDER` | `openai` | Cố định nhà cung cấp embedding để bảo toàn số chiều 1536. |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Cố định mô hình embedding chuẩn chi phí thấp. |
| `EMBEDDING_DIM` | `1536` | Số chiều vector khớp cứng với `vector(1536)`. |
| `E2B_API_KEY` | `e2b_...` | Khóa API chạy sandbox Firecracker biên dịch LaTeX. |
| `E2B_LATEX_TEMPLATE` | `verischolar-latex` | Tên E2B custom template chứa sẵn TeX Live / tectonic. |
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-...` | Khóa công khai Langfuse. |
| `LANGFUSE_SECRET_KEY` | `sk-lf-...` | Khóa bí mật Langfuse. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Máy chủ Langfuse Cloud. |
| `ALERT_WEBHOOK_URL` | `https://api.telegram.org/...` | Webhook bắn cảnh báo lỗi 500 trên `production`. |

---

## 6. Ma Trận Kiểm Thử TDD Nền Tảng (Foundation TDD Matrix)

Mọi thay đổi kỹ thuật thuộc Trụ cột 1 phải vượt qua đầy đủ các kịch bản kiểm thử sau:

```mermaid
flowchart TD
    subgraph RAMTests ["<b>Tầng 1: Pure In-Memory Core Tests (< 1s)</b>"]
        T1["Test Entity Immutability & Validation<br/>(User, Document, Chunk entities)"]
        T2["Test Hexagonal Import Guard<br/>(Cấm import fastapi/sqlalchemy trong packages/core)"]
        T3["Test CAS Hash Calculation<br/>(SHA-256 deterministic path generator)"]
    end

    subgraph PGTests ["<b>Tầng 2: PostgreSQL Real Integration Tests (< 5s)</b>"]
        T4["Test Idempotent DDL Execution<br/>(ensure_database_schema chạy 2 lần không lỗi)"]
        T5["Test 16-Table Schema & Foreign Keys<br/>(ON DELETE CASCADE & SET NULL)"]
        T6["Test Multi-Tenant user_id Scoping<br/>(User A không thể select document của User B)"]
        T7["Test pgvector HNSW & Full-Text Search<br/>(Vector cosine query & tsvector match)"]
        T8["Test CAS Zero-Retention Purge<br/>(ref_count -= 1, file xóa khi ref_count=0)"]
    end

    RAMTests --> PGTests
```

| Tên Test Case | File Kiểm Thử | Mục tiêu kiểm chứng | Kỳ vọng nghiệm thu |
|---|---|---|---|
| `test_core_has_zero_framework_imports` | `packages/core/tests/test_hexagonal_guard.py` | Quét AST toàn bộ thư mục `packages/core/src/core/domain/` | 0 dòng import `fastapi`, `sqlalchemy`, `redis`, `fitz`. |
| `test_cas_path_distribution` | `packages/core/tests/test_cas_storage.py` | Kiểm tra thuật toán băm SHA-256 và chia nhánh thư mục | Đúng định dạng `storage/blobs/ab/cd/abcd...`. |
| `test_ensure_database_schema_idempotency` | `apps/api/tests/test_db_bootstrap.py` | Chạy `ensure_database_schema()` 2 lần liên tiếp trên test DB | Không nổ ngoại lệ, toàn bộ 16 bảng và extension sẵn sàng. |
| `test_multi_tenant_user_isolation` | `apps/api/tests/test_multi_tenant_isolation.py` | Tạo User 1 và User 2, User 1 tạo Document, User 2 cố gắng query | Trả về `404 NOT_FOUND` hoặc rỗng, không rò rỉ dữ liệu. |
| `test_cas_blob_reference_counting_purge` | `apps/api/tests/test_cas_lifecycle.py` | Nạp 2 tài liệu cùng file băm (`ref_count=2`), xóa lần 1 còn file, xóa lần 2 file bị unlink | File nhị phân vật lý bị xóa sạch khi `ref_count=0`. |
| `test_hybrid_search_vector_and_fts` | `apps/api/tests/test_pgvector_fts.py` | Chèn chunk có embedding và text, truy vấn vector cosine và `to_tsquery` | Trả về đúng thứ tự độ tương đồng ngữ nghĩa. |

---

## 7. Tiêu Chí Nghiệm Thu Kỹ Thuật (Definition of Done)

- [ ] Toàn bộ 16 bảng PostgreSQL và các chỉ mục HNSW/GIN được định nghĩa tường minh bằng SQLAlchemy và DDL SQL.
- [ ] Không còn bất kỳ tham chiếu hay hàm gọi nào tới `aiosqlite` hoặc SQLite fallback trong toàn bộ codebase.
- [ ] Hàm `ensure_database_schema()` chạy thành công và an toàn trên cả database trống lẫn database đã có dữ liệu.
- [ ] Cơ chế CAS đảm bảo tiêu hủy file vật lý ngay lập tức khi không còn tài liệu nào trỏ tới.
- [ ] Toàn bộ ma trận kiểm thử tại Mục 6 vượt qua `100% PASS` trên môi trường kiểm thử với PostgreSQL thật.

# TÀI LIỆU THIẾT KẾ: KIẾN TRÚC NỀN TẢNG, CSDL 18 BẢNG POSTGRESQL + PGVECTOR, CAS STORAGE & OCC TRIGGERS
# (FOUNDATION ARCHITECTURE, 18 POSTGRESQL TABLES, CAS STORAGE & OCC TRIGGERS DESIGN)

**Mã tài liệu:** `DESIGN-00`  
**Ngày lập:** 2026-10-25  
**Trạng thái:** DỰ THẢO THIẾT KẾ CHỜ DUYỆT (PENDING APPROVAL)  
**Tài liệu tham chiếu:**
- PRD Nghiệp vụ: [`docs/PRD/00-overview-and-cleanup.md`](../../PRD/00-overview-and-cleanup.md)
- Đặc tả Kỹ thuật: [`docs/specs/00-foundation-architecture-and-db.md`](../../specs/00-foundation-architecture-and-db.md)
- Hiến pháp Hệ thống: [`.agents/AGENTS.md`](../../../.agents/AGENTS.md)
- Nguyên tắc Kiến trúc: [`.agents/ARCHITECTURE_PRINCIPLES.md`](../../../.agents/ARCHITECTURE_PRINCIPLES.md)

---

## 1. Mục Đích & Bối Cảnh (Intent & The Why)

VeriScholar là nền tảng Trợ lý AI Nghiên cứu Khoa học Toàn trình hoạt động theo mô hình Monorepo với Kiến trúc Lục giác (Hexagonal Architecture). Để toàn bộ 7 phân hệ nghiệp vụ cấp cao (Xác thực & BYOK, Khám phá & Nạp PDF, Đọc sâu & Bounding Box, Bảng Ngữ cảnh 3 Cột, Kho Yêu thích & GraphRAG, Soạn thảo LaTeX E2B, và Giám sát Langfuse) có thể vận hành ổn định mà không bị xung đột cấu trúc dữ liệu:
- Hệ thống cần một tầng nền tảng CSDL quan hệ chuẩn mực trên **PostgreSQL 16+ với extension `pgvector`** (18 bảng hoàn chỉnh), bảo đảm 100% bảng dữ liệu nghiệp vụ có `user_id` để cô lập đa khách hàng (multi-tenant isolation).
- Hệ thống cần cơ chế lưu trữ file nhị phân vật lý định danh theo mã băm nội dung (**Content-Addressable Storage - CAS**) tại `storage/blobs/` với giao thức `IBlobStoragePort` hỗ trợ đọc phân đoạn byte range cho PDF Canvas, kết hợp quản lý vòng đời tham chiếu `ref_count` tại CSDL và tiêu hủy đồng bộ tức thì (*Zero-Retention Guarantee*).
- Hệ thống cần cơ chế kiểm soát tương tranh lạc quan (**OCC - Optimistic Concurrency Control**) bằng PostgreSQL PL/pgSQL triggers (`handle_occ_and_timestamp()`) trên `research_notes` và `drafts` để chống xung đột ghi đè dữ liệu.
- Hệ thống cần hàm khởi tạo schema CSDL an toàn, lặp lại nhiều lần không sinh lỗi (**Idempotent Database Bootstrap**) qua `ensure_database_schema()`.

---

## 2. Mục Tiêu, Phạm Vi & Ranh Giới (Goals, Non-Goals & Anti-Goals)

### A. Mục Tiêu (Goals)
1. Xây dựng đầy đủ 18 models SQLAlchemy 2.0 Async kế thừa chuẩn mực từ `IdentifiableTimestampedModel` trong `apps/api/src/api/db/models/`.
2. Khai báo chính xác các kiểu dữ liệu nâng cao: `Vector(1536)` cho `document_chunks` và `graph_nodes`, cột FTS lưu trữ tính sẵn `content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', text_content)) STORED`, mảng `JSONB`, `ARRAY(String)` cho danh sách tác giả và sở thích nghiên cứu.
3. Cài đặt các ràng buộc toàn vẹn dữ liệu cơ học: Khóa duy nhất `UNIQUE(user_id, node_type, canonical_name)` cho Graph Hub, `UNIQUE(user_id, provider)` cho API keys, và giới hạn trạng thái qua `CHECK constraints`.
4. Duy trì adapter lưu trữ CAS `LocalStorageAdapter` trong `packages/core/src/core/adapters/storage/local.py` tuân thủ protocol `IBlobStoragePort`: sinh đường dẫn phân tán 2 cấp (`storage/blobs/ab/cd/abcd...`), hỗ trợ stream range byte phục vụ PDF lazy loading, và xóa file vật lý (`unlink()`) khi `document_storage_blobs.ref_count <= 0`.
5. Hoàn thiện hàm `ensure_database_schema(conn: AsyncConnection)` trong `apps/api/src/api/db/init_db.py`: tạo extension `vector`, 18 bảng, 3 trigger functions, chỉ mục HNSW Cosine và chỉ mục GIN text search.
6. Thiết lập bộ kiểm thử TDD nền tảng đạt 100% Pass và vượt qua 4 Cổng Xác Minh Bắt Buộc.

### B. Ngoài Phạm Vi (Non-Goals)
1. Chưa triển khai các Business Services hoặc REST Endpoints cụ thể của các phân hệ cấp cao (như Authentication flow, RAG search, LaTeX compilation, hay Langfuse telemetry) — những phần này sẽ được triển khai độc lập theo từng phân hệ tương ứng.
2. Không xây dựng migration rollback phức tạp cho các cơ sở dữ liệu di sản trước thời điểm MVP refactor.

### C. Điều Cấm Kỵ (Anti-Goals)
1. **Tuyệt đối cấm SQLite Fallback:** Không cho phép bất kỳ cơ chế fallback ngầm nào sang SQLite khi thiếu PostgreSQL. Nếu không kết nối được PostgreSQL 16+ `pgvector`, hệ thống bắt buộc phải fail-fast.
2. **Tuyệt đối cấm vi phạm Kiến trúc Lục giác:** `packages/core/` chỉ sử dụng thư viện chuẩn Python và `pydantic`. Không được import `sqlalchemy`, `fastapi`, `pymupdf` vào `packages/core/src/core/domain/` hoặc `ports/`.
3. **Tuyệt đối cấm file mồ côi (Zero Orphan Blobs):** Khi tài liệu bị xóa, file PDF vật lý tương ứng trên đĩa cứng không được phép tồn tại nếu không còn bản ghi nào tham chiếu tới.

---

## 3. Các Ràng Buộc Kỹ Thuật (Constraints)

- **Cơ sở dữ liệu:** PostgreSQL 16+ với extension `pgvector` phiên bản 0.8.0+.
- **ORM & Driver:** SQLAlchemy 2.0 Async với driver `asyncpg`.
- **Cấu trúc lưu trữ CAS:** `storage/blobs/<hash[0:2]>/<hash[2:4]>/<hash>.<ext>`.
- **Độ phân giải Vector:** 1536 chiều (chuẩn OpenAI `text-embedding-3-small` / standard dense embeddings).
- **Quy chuẩn Markdown:** Toàn bộ liên kết tham chiếu tài liệu nội bộ dùng đường dẫn tương đối (`../...`, `./...`), không dùng URL tuyệt đối `file:///...`.

---

## 4. Các Phương Án Tiếp Cận Đã Cân Nhắc & Đánh Đổi (Approaches Considered)

### Phương án A: Tạo Sửa Đồng Loạt Toàn Bộ (Big-Bang Monolithic Update)
- Tạo và sửa đồng thời cả 18 models và hàm khởi tạo `init_db.py` trong 1 lượt duy nhất.
- *Đánh đổi:* Dễ phát sinh lỗi xung đột vòng tròn khóa ngoại (Circular Foreign Keys) và khó khoanh vùng lỗi khi kiểm thử TDD.

### Phương án B: Phân Tầng Dữ Liệu Từ Gốc Lên Ngọn (Bottom-Up Topological Layering) — **ĐÃ ĐƯỢC CHỌN**
- Phân rã tiến trình triển khai thành 4 tầng kế thừa phụ thuộc:
  - **Tầng 1: Lõi Lưu Trữ Vật Lý CAS (`packages/core`)**: Đảm bảo `IBlobStoragePort` và `LocalStorageAdapter` hoạt động độc lập với streaming và range support.
  - **Tầng 2: Thực Thể Danh Tính & Tài Liệu Gốc (`apps/api`)**: `users`, `scholar_profiles`, `user_api_keys`, `document_storage_blobs`, `documents`, `document_chunks` (vector 1536 + `content_tsv`), `document_summaries` (3 phần luận điểm), `reference_items`.
  - **Tầng 3: Thực Thể Tương Tác & Mạng Tri Thức GraphRAG**: `research_sessions`, `session_documents`, `session_turns`, `research_notes` (kèm `frozen_snapshot`), `folders`, `graph_nodes`, `graph_edges`.
  - **Tầng 4: Thực Thể Soạn Thảo & Khởi Tạo Idempotent Schema**: `drafts`, `draft_assets`, `draft_messages`, hoàn thiện `ensure_database_schema()` trong `init_db.py` với PL/pgSQL triggers, chỉ mục HNSW và GIN.
- *Lý do chọn:* Đảm bảo kiểm soát rủi ro tuyệt đối, test xanh từng tầng, triệt tiêu nguy cơ circular dependency.

---

## 5. Thiết Kế Chi Tiết Từng Tầng Hiện Thực (Detailed Layer Specifications)

### Tầng 1: Lõi Lưu Trữ Vật Lý CAS (Content-Addressable Storage Layer)
- **Tập tin:**
  - `packages/core/src/core/ports/storage.py` (`IBlobStoragePort`)
  - `packages/core/src/core/adapters/storage/local.py` (`LocalStorageAdapter`)
- **Giao thức Port chuẩn (`IBlobStoragePort`):**
  - `save_blob(stream: AsyncIterator[bytes], content_hash: str) -> tuple[str, int]`: Stream nội dung ghi xuống file, trả về `(storage_path, total_byte_size)`.
  - `blob_exists(content_hash: str) -> bool`: Kiểm tra tồn tại file vật lý trên đĩa.
  - `get_blob_path(content_hash: str) -> str`: Sinh đường dẫn phân tán 2 tầng: `storage/blobs/<h[0:2]>/<h[2:4]>/<h>`.
  - `delete_blob(content_hash: str) -> bool`: Gọi `unlink()` xóa vĩnh viễn file trên đĩa cứng; tự động dọn thư mục cha rỗng nếu có.
  - `read_blob(content_hash: str) -> bytes`: Đọc toàn bộ nội dung file nhị phân.
  - `stream_blob_range(content_hash: str, start_byte: int = 0, end_byte: int | None = None, chunk_size: int = 64 * 1024) -> AsyncIterator[bytes]`: Stream byte slices phục vụ HTTP 206 Partial Content cho PDF Canvas viewer.
- **Ranh giới trách nhiệm (Architectural Separation):**
  - `LocalStorageAdapter` hoàn toàn stateless, không kết nối DB.
  - Cơ chế đếm tham chiếu `ref_count` được quản lý bởi CSDL (`document_storage_blobs.ref_count`) tại tầng Service của `apps/api`.

---

### Tầng 2: Thực Thể Định Danh & Tài Liệu Gốc (Identity & Document Entities)
- **Tập tin:** `apps/api/src/api/db/models/`
  1. [`user.py`](../../apps/api/src/api/db/models/user.py): `UserModel` (bảng `users`):
     - `id`: UUID khóa chính.
     - `email`: String(255) (`UNIQUE`, `INDEX`).
     - `hashed_password`: String(255).
     - `full_name`: String(100).
     - `avatar_url`: String(500) Nullable.
     - `role`: String(30) default 'researcher'.
     - `is_active`: Boolean default True.
     - `is_verified`: Boolean default False.
     - *Giữ các trường tương thích ngược tạm thời:* `institution`, `department`, `academic_rank`, `orcid_id`.
  2. `scholar_profile.py`: `ScholarProfileModel` (bảng `scholar_profiles`):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`, `UNIQUE`).
     - `institution`: String(255) Nullable.
     - `department`: String(255) Nullable.
     - `academic_rank`: String(100) Nullable.
     - `orcid_id`: String(50) Nullable.
     - `google_scholar_url`: String(500) Nullable.
     - `research_interests`: `ARRAY(String)` hoặc `JSONB`.
     - `bio`: TEXT Nullable.
  3. `user_api_key.py`: `UserApiKeyModel` (bảng `user_api_keys`):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`).
     - `provider`: String(50) (`CHECK (provider IN ('openai', 'anthropic', 'google', 'exa'))`).
     - `encrypted_key`: String(500).
     - `key_hint`: String(10).
     - `is_active`: Boolean default True.
     - `CONSTRAINT uq_user_api_keys_user_provider UNIQUE (user_id, provider)`.
  4. [`blob.py`](../../apps/api/src/api/db/models/blob.py): `DocumentStorageBlobModel` (bảng `document_storage_blobs`):
     - `content_hash`: String(64) (`UNIQUE`, `INDEX`).
     - `storage_path`: String(500).
     - `byte_size`: Integer.
     - `mime_type`: String(100).
     - `ref_count`: Integer default 1.
  5. [`document.py`](../../apps/api/src/api/db/models/document.py): `DocumentModel` (bảng `documents`):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`, `INDEX`).
     - `blob_id`: UUID Khóa ngoại trỏ `document_storage_blobs.id` (`ON DELETE RESTRICT`). Nullable khi ở trạng thái `abstract_only`.
     - `title`, `authors`, `year`, `doi`, `arxiv_id`, `venue`.
     - `status`: String(30) (`CHECK (status IN ('uploaded', 'parsing', 'indexing', 'ready', 'failed', 'abstract_only'))`).
     - `access_status`: String(30) (`CHECK (access_status IN ('open_access_pdf', 'abstract_only', 'user_uploaded'))`).
  6. [`chunk.py`](../../apps/api/src/api/db/models/chunk.py): `DocumentChunkModel` (bảng `document_chunks`):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`, `INDEX` - đảm bảo multi-tenant filter).
     - `document_id`: UUID Khóa ngoại trỏ `documents.id` (`ON DELETE CASCADE`).
     - `chunk_index`: Integer.
     - `page_number`: Integer.
     - `text_content`: TEXT.
     - `bbox_json`: JSONB (tọa độ `[x0, y0, x1, y1]`).
     - `embedding`: `Vector(1536)` (pgvector).
     - `content_tsv`: `TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', text_content)) STORED`.
  7. [`summary.py`](../../apps/api/src/api/db/models/summary.py): `DocumentSummaryModel` (bảng `document_summaries` - Cấu trúc 3 Luận điểm theo SPEC-00):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`, `INDEX`).
     - `document_id`: UUID Khóa ngoại trỏ `documents.id` (`ON DELETE CASCADE`, `UNIQUE`).
     - `problem_statement`: TEXT.
     - `problem_citations`: JSONB (danh sách trích dẫn và bbox).
     - `contributions`: TEXT.
     - `contribution_citations`: JSONB.
     - `limitations`: TEXT.
     - `limitation_citations`: JSONB.
     - `total_tokens`: Integer default 0.
     - `latency_ms`: Integer default 0.
  8. [`reference.py`](../../apps/api/src/api/db/models/reference.py): `ReferenceItemModel` (bảng `reference_items`):
     - `user_id`: UUID Khóa ngoại trỏ `users.id` (`ON DELETE CASCADE`, `INDEX`).
     - `document_id`: UUID Khóa ngoại trỏ `documents.id` (`ON DELETE CASCADE`).
     - `ref_index`: Integer.
     - `raw_text`: TEXT.
     - `parsed_title`, `parsed_authors`, `parsed_year`, `doi`, `arxiv_id`.
     - `resolved_document_id`: UUID Nullable (`ON DELETE SET NULL`).

---

### Tầng 3: Thực Thể Tương Tác & Mạng Tri Thức GraphRAG (Interaction & Graph Entities)
- **Tập tin:** `apps/api/src/api/db/models/`
  1. [`session.py`](../../apps/api/src/api/db/models/session.py):
     - `ResearchSessionModel` (bảng `research_sessions`):
       - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
       - `title`: String(255).
       - `active_document_id`: UUID Nullable (`ON DELETE SET NULL`).
       - `viewport_state`: JSONB (`{"active_document_id": "...", "page": 1, "zoom_ratio": 1.0}`).
     - `SessionDocumentModel` (bảng `session_documents` - bảng nối tab phiên đọc):
       - `session_id`: UUID (`ON DELETE CASCADE`).
       - `document_id`: UUID (`ON DELETE CASCADE`).
       - `display_order`: Integer default 0.
       - `added_at`: TIMESTAMPTZ.
       - Khóa chính tổng hợp `(session_id, document_id)`.
     - `SessionTurnModel` (bảng `session_turns` - lịch sử hỏi đáp nguyên tử 1NF):
       - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
       - `session_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
       - `question`: TEXT.
       - `answer`: TEXT.
       - `citations`: JSONB (chứa tags trích dẫn và bbox coordinates).
       - `prompt_tokens`: Integer default 0.
       - `completion_tokens`: Integer default 0.
       - `latency_ms`: Integer default 0.
       - `finish_reason`: String(30) default 'stop'.
       - `trace_id`: String(64) Nullable.
  2. [`note.py`](../../apps/api/src/api/db/models/note.py): `ResearchNoteModel` (bảng `research_notes` - bảo toàn bằng chứng học thuật):
     - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `document_id`: UUID Nullable (`ON DELETE SET NULL`).
     - `chunk_id`: UUID Nullable (`ON DELETE SET NULL`).
     - `selected_text`: TEXT NOT NULL.
     - `bounding_boxes`: JSONB NOT NULL DEFAULT '[]'.
     - `page_number`: Integer NOT NULL CHECK (page_number >= 1).
     - `user_note`: TEXT Nullable.
     - `tags`: `TEXT[]` NOT NULL DEFAULT '{}'.
     - `frozen_snapshot`: JSONB NOT NULL DEFAULT '{}'.
     - `is_source_detached`: Boolean NOT NULL DEFAULT FALSE.
     - `version`: Integer NOT NULL DEFAULT 1 (OCC Version).
  3. [`folder.py`](../../apps/api/src/api/db/models/folder.py): `FolderModel` (bảng `folders`):
     - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `parent_id`: UUID Nullable (`ON DELETE CASCADE`).
     - `name`: String(100) NOT NULL.
     - `color`: String(20) default '#3B82F6'.
     - `description`: String(500) Nullable.
  4. `graph.py`: Tạo mới `GraphNodeModel` và `GraphEdgeModel` (bảng `graph_nodes` và `graph_edges`):
     - `GraphNodeModel`:
       - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
       - `document_id`: UUID Nullable (`ON DELETE SET NULL`).
       - `node_type`: String(30) (`CHECK (node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult'))`).
       - `canonical_name`: String(255) NOT NULL.
       - `display_name`: String(255) NOT NULL.
       - `description`: TEXT Nullable.
       - `metadata_json`: JSONB Nullable.
       - `embedding`: `Vector(1536)` (pgvector).
       - `CONSTRAINT uq_graph_nodes_user_type_canonical UNIQUE (user_id, node_type, canonical_name)`.
     - `GraphEdgeModel`:
       - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
       - `document_id`: UUID Nullable (`ON DELETE SET NULL`).
       - `source_node_id`: UUID (`ON DELETE CASCADE`).
       - `target_node_id`: UUID (`ON DELETE CASCADE`).
       - `edge_type`: String(30) (`CHECK (edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES'))`).
       - `weight`: Float default 1.0.
       - `evidence_chunk_id`: UUID Nullable.

---

### Tầng 4: Thực Thể Soạn Thảo & Khởi Tạo Idempotent Schema (Writing Entities & Bootstrap)
- **Tập tin:**
  1. [`draft.py`](../../apps/api/src/api/db/models/draft.py): `DraftModel` (bảng `drafts`):
     - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `source_session_id`: UUID Nullable (`ON DELETE SET NULL`).
     - `title`: String(255) NOT NULL.
     - `content`: TEXT NOT NULL (mã `main.tex`).
     - `bib_content`: TEXT NOT NULL DEFAULT '' (mã `references.bib`).
     - `version`: Integer NOT NULL DEFAULT 1 (OCC Version).
     - `previous_snapshot`: JSONB Nullable (`{"content": "...", "bib_content": "...", "version": X}`).
     - `pdf_preview_storage_path`: String(500) Nullable.
  2. `draft_asset.py`: Tạo mới `DraftAssetModel` (bảng `draft_assets` - thư mục `figures/`):
     - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `draft_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `blob_id`: UUID (`ON DELETE RESTRICT`).
     - `file_name`: String(255) NOT NULL (ví dụ: `figures/architecture.png`).
     - `mime_type`: String(100) NOT NULL.
     - `byte_size`: Integer NOT NULL.
     - `CONSTRAINT uq_draft_assets_draft_filename UNIQUE (draft_id, file_name)`.
  3. `draft_message.py`: Tạo mới `DraftMessageModel` (bảng `draft_messages` - lịch sử chat Agent Soạn thảo):
     - `user_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `draft_id`: UUID (`ON DELETE CASCADE`, `INDEX`).
     - `role`: String(20) (`CHECK (role IN ('user', 'assistant', 'tool'))`).
     - `content`: TEXT NOT NULL.
     - `tool_calls`: JSONB Nullable.
     - `compile_attempts`: SmallInteger NOT NULL DEFAULT 0.
     - `trace_id`: String(64) Nullable.
  4. [`init_db.py`](../../apps/api/src/api/db/init_db.py): Hàm `ensure_database_schema(conn: AsyncConnection)`:
     - Tạo extension `vector`.
     - Tạo hàm trigger `handle_occ_and_timestamp()` và gắn trigger `trg_drafts_occ` vào `drafts`, `trg_research_notes_occ` vào `research_notes`.
     - Tạo trigger vô điều kiện `BEFORE UPDATE ON research_notes` gọi `handle_note_source_detached()` để đảm bảo tự động bật `is_source_detached = TRUE` khi `documents` bị xóa kéo theo `ON DELETE SET NULL`.
     - Tạo chỉ mục HNSW Cosine:
       - `idx_document_chunks_embedding_hnsw` trên `document_chunks USING hnsw (embedding vector_cosine_ops)`.
       - `idx_graph_nodes_embedding_hnsw` trên `graph_nodes USING hnsw (embedding vector_cosine_ops)`.
     - Tạo chỉ mục GIN:
       - `idx_document_chunks_tsv` trên `document_chunks USING gin (content_tsv)`.
     - Đăng ký export toàn bộ 18 models vào `apps/api/src/api/db/models/__init__.py`.

---

## 6. Ma Trận Kiểm Thử TDD Bắt Buộc (TDD Verification Plan)

| Test Case | Tập tin kiểm thử | Trọng tâm kiểm chứng |
| :--- | :--- | :--- |
| `test_cas_path_distribution` | `packages/core/tests/test_cas_storage.py` | Kiểm tra SHA-256 băm ra đúng đường dẫn phân tán 2 cấp (`storage/blobs/ab/cd/...`). |
| `test_cas_stream_range_reading` | `packages/core/tests/test_cas_storage.py` | Kiểm tra stream_blob_range đọc đúng byte offset cho PDF canvas. |
| `test_cas_blob_reference_counting_purge` | `apps/api/tests/test_cas_lifecycle.py` | Kiểm tra tăng `ref_count` khi trùng hash, và gọi `unlink` xóa file vật lý khi `ref_count=0`. |
| `test_ensure_database_schema_idempotency` | `apps/api/tests/test_db_bootstrap.py` | Chạy `ensure_database_schema()` 2 lần liên tiếp: không ném ngoại lệ, 18 bảng sẵn sàng. |
| `test_occ_trigger_increments_version` | `apps/api/tests/test_drafts_occ.py` | Cập nhật draft trực tiếp trong CSDL: trigger tự động tăng `version` và cập nhật `updated_at`. |
| `test_note_source_detached_trigger` | `apps/api/tests/test_notes_trigger.py` | Xóa tài liệu: trigger tự động bật cờ `is_source_detached = TRUE` trên `research_notes`. |
| `test_graph_canonical_unique_constraint` | `apps/api/tests/test_graph_models.py` | Chèn 2 nút cùng `(user_id, node_type, canonical_name)`: CSDL ném lỗi `IntegrityError`. |
| `test_multi_tenant_user_isolation` | `apps/api/tests/test_multi_tenant_isolation.py` | Kiểm chứng 100% bảng nghiệp vụ lọc chính xác theo `user_id`. |
| `test_architecture_boundary_pure_domain` | `apps/api/tests/test_architecture_boundary.py` | Rào chắn AST: 0 vi phạm import trong `packages/core`. |
| `test_no_absolute_file_urls_in_markdown` | `apps/api/tests/test_architecture_boundary.py` | 0 liên kết URL tuyệt đối máy chủ trong tài liệu Markdown. |

---

## 7. Các Quyết Định Đã Chốt & Việc Giao Cho Kỹ Sư Thực Thi (Decisions & Builder Handoff)

### Quyết định kiến trúc đã chốt:
1. **Khóa gộp Đỉnh GraphRAG:** Gộp Hub duy nhất theo `(user_id, node_type, canonical_name)`, cột `document_id` trong `graph_nodes` là `NULLABLE` với `ON DELETE SET NULL`.
2. **CAS Storage:** Giữ nguyên giao thức `IBlobStoragePort` hỗ trợ streaming và byte-range (`stream_blob_range`); quản lý `ref_count` và xóa file vật lý đồng bộ ở tầng DB/Service của `apps/api`.
3. **Multi-Tenant Filter:** Toàn bộ các bảng con (`document_chunks`, `document_summaries`, `reference_items`, `session_turns`) bắt buộc mang trực tiếp `user_id` để tăng tốc chỉ mục vector HNSW.
4. **Full-Text Search:** Dùng cột `content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', text_content)) STORED` kèm chỉ mục GIN.
5. **OCC Triggers:** Dùng PL/pgSQL native trigger trong PostgreSQL cho `research_notes` và `drafts`. Ứng dụng kiểm tra `WHERE id = :id AND version = :expected_version` để sinh mã lỗi HTTP 412 khi xung đột.
6. **4 Cổng Xác Minh:** Mọi bước triển khai phải giữ vững trạng thái pass 100% của `ruff`, `pytest`, `npm test`, `npm build`.

### Những việc giao cho Kỹ sư Lập trình (Builder):
- Triển khai code theo đúng 4 tầng Topo từ Tầng 1 đến Tầng 4.
- Tuân thủ nghiêm ngặt quy trình TDD: viết test trước, viết code tối thiểu, refactor.
- Đảm bảo commit cục bộ sau khi hoàn thành từng tầng; không push code lên remote.

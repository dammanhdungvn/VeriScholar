# Thiết Kế Hệ Thống Tài Liệu Đặc Tả Kỹ Thuật VeriScholar MVP (`docs/specs/`)

**Ngày tạo:** 2026-10-25  
**Nguồn tham chiếu gốc (Product Source of Truth):** `docs/PRD/00-overview-and-cleanup.md` $\rightarrow$ `docs/PRD/07-monitoring-and-langfuse.md`  
**Thư mục đích:** `docs/specs/` (thay thế hoàn toàn các thư mục tài liệu cũ `docs/01-architecture/`, `docs/03-frontend-engineering/`, `docs/04-operations-and-cicd/`, `docs/05-testing-and-qa/`)

---

## 1. Mục Đích & Lý Do Thiết Kế (Intent & The Why)

Sau khi dọn dẹp toàn bộ mã nguồn dư thừa của kiến trúc 5-Pillar cũ và xóa trắng toàn bộ bộ unit test cũ (vốn bám vào SQLite `aiosqlite` và các tính năng ngoài phạm vi), dự án VeriScholar cần một bộ **Đặc tả Kỹ thuật (`Technical Specs`) tại `docs/specs/`** đóng vai trò cầu nối trực tiếp từ yêu cầu sản phẩm (`docs/PRD/00..07`) sang mã nguồn thực thi và bộ kiểm thử mới.

Mục tiêu cốt lõi của bộ `docs/specs/` là để bất kỳ kỹ sư hoặc AI agent nào (như Member 2 phụ trách Backend/Core và Member 3 phụ trách Frontend qua `herdr`) khi nhận 1 module cụ thể chỉ cần đọc đúng cặp file `docs/PRD/0X-*.md` + `docs/specs/0X-*.md` (+ `docs/specs/00-*.md`) là nắm rõ 100%:
1. Phần nào trong codebase hiện tại đã khớp chuẩn (`As-Is`) và phần nào đang thiếu/lệch cần xây mới hoặc nâng cấp (`Delta`).
2. Lược đồ bảng PostgreSQL + `pgvector`, kiểu dữ liệu, khóa ngoại `ON DELETE`, chỉ mục HNSW/GIN và quy tắc cô lập `user_id`.
3. Hợp đồng API/SSE chính xác tới từng tên trường JSON, HTTP status code, mã lỗi `ErrorResponse` và sự kiện streaming.
4. Kiến trúc xử lý nội bộ (Prompts lưu trong code Python, luồng Hybrid RAG + Exa 2 Tầng, GraphRAG 4 Thực thể, `StateGraph` của LangGraph + vòng lặp tự sửa lỗi E2B tối đa 3 lần, và Monitoring 3 Tầng).
5. Cấu trúc Component/Route/Zustand/TanStack Query phía Frontend và danh mục **Unit + Integration Test Cases** bắt buộc của module đó.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals & Anti-Goals)

### A. Mục tiêu (Goals)
- Tạo mới thư mục `docs/specs/` gồm **8 file đặc tả kỹ thuật (`00` đến `07`)** ánh xạ 1-1 với `docs/PRD/00..07`.
- Xóa bỏ hoàn toàn 4 thư mục tài liệu cũ (`docs/01-architecture/`, `docs/03-frontend-engineering/`, `docs/04-operations-and-cicd/`, `docs/05-testing-and-qa/`) và cập nhật `docs/README.md` chỉ trỏ tới `docs/PRD/` và `docs/specs/`.
- Đồng bộ lại câu chữ còn nhắc tới `SQLite fallback` trong `docs/PRD/00-overview-and-cleanup.md`, `docs/PRD/05-favorite-library-and-graphrag.md`, `docs/PRD/07-monitoring-and-langfuse.md` về thuần **PostgreSQL + `pgvector`** (và ghi nhận nhiệm vụ gỡ bỏ `init_sqlite_fallback()` khỏi `apps/api/src/api/db/session.py`, `init_db.py`, `api/__init__.py` trong `Delta` của `specs/00`).
- Khóa chặt mọi hợp đồng giao tiếp giữa Backend và Frontend cho các tính năng `Delta` chưa có trong code để khi chia việc song song không xảy ra lệch tên trường hay lệch route.

### B. Phi mục tiêu (Non-Goals)
- Giai đoạn tạo `docs/specs/` này **chỉ thiết kế và biên soạn bộ tài liệu đặc tả kỹ thuật** (cùng dọn sạch thư mục `docs/` cũ), chưa viết code tính năng mới hay viết file unit test mới trong cùng một bước (việc code từng module và viết test mới sẽ chạy theo các plan triển khai riêng dựa trên `docs/specs/`).
- Không thiết kế hệ thống microservices, Neo4j, Prometheus/Grafana, ARQ worker rời hay Prompt Management trên đám mây.

### C. Chống mục tiêu (Anti-Goals — Coi là thất bại nếu xuất hiện trong `docs/specs/`)
- Đặc tả chung chung kiểu văn xuôi ("xử lý lỗi phù hợp", "trả về thông tin bài báo") khiến người lập trình phải tự đoán tên cột DB, tên trường JSON hoặc tên event SSE.
- Chép nguyên xi code cũ đang sai lệch với PRD vào spec như thể nó đã hoàn chỉnh (bỏ sót việc chỉ rõ `As-Is` vs `Delta`).
- Đưa lại bất kỳ thành phần nào đã bị loại bỏ khỏi MVP (SQLite/`aiosqlite`, Comparison Matrix, SAFE NLI/DeBERTa, chia sẻ/bình luận Draft, nhảy sang Overleaf ngoài, `export-pdf`, phiên `export-bundle`, `notes:synthesize`, `uat`/`staging`/`enterprise`).

---

## 3. Ràng Buộc Kỹ Thuật Cứng (Global Constraints)

1. **Môi trường vận hành:** Duy nhất `development` (`LANGFUSE_ENVIRONMENT=verischolar-dev`), `production` (`LANGFUSE_ENVIRONMENT=verischolar-prod`), và chế độ nội bộ `test` khi chạy `pytest` (`LANGFUSE_ENABLED=false`).
2. **Cơ sở dữ liệu & Lưu trữ:** Thuần **PostgreSQL 16+ kèm extension `vector` (`pgvector`)** (embedding `1536` chiều với `text-embedding-3-small`), Redis 7 cho OTP/rate-limit/idempotency cache, và lưu trữ file vật lý theo CAS (`SHA-256`) tại `storage/blobs/` — **tuyệt đối không có SQLite fallback**.
3. **Ranh giới Kiến trúc Lục giác (Hexagonal Architecture):** `packages/core/src/core/domain/` chỉ chứa pure Python domain entities, value objects, exceptions (không import `fastapi`, `sqlalchemy`, `httpx`, `pymupdf`/`fitz`, `redis`, `langfuse`, `e2b`).
4. **Giới hạn nghiệp vụ bất biến:**
   - Upload PDF: Digital PDF có lớp văn bản, `<= 50 MB`, `<= 100 trang`.
   - Phiên đọc sâu (`session_documents`): tối đa `5 bài báo` đồng thời / phiên.
   - Biên dịch LaTeX trên E2B Sandbox: chạy cô lập với `--no-shell-escape`, `allow_internet_access=False`, timeout cứng `15 giây` / lượt, tối đa `3 vòng lặp` tự sửa lỗi liên tiếp.
5. **Điều hướng Giao diện Toàn cục (`DashboardTaskbar.tsx`):** Cố định đúng 4 mục (`🔍 Khám phá & Phiên đọc`, `⭐ Kho Yêu thích`, `✍️ Soạn thảo LaTeX`, `👤 Tài khoản & Giao diện`).

---

## 4. Các Phương Án Đã Cân Nhắc (Approaches)

1. **Phương án 1 (Đã chọn): Cắt dọc 1-1 theo Module PRD + 1 File Nền tảng Chung (`docs/specs/00..07`)**  
   Mỗi module PRD (`01..07`) có đúng 1 file Technical Spec tự chứa trọn vẹn từ `As-Is vs Delta` $\rightarrow$ `DB` $\rightarrow$ `Backend/AI` $\rightarrow$ `API/SSE` $\rightarrow$ `Frontend` $\rightarrow$ `Test Matrix`, đi kèm 1 file nền tảng `00-foundation-architecture-and-db.md`. Tối ưu ngữ cảnh khi giao việc song song theo module và bám sát TDD.
2. **Phương án 2 (Loại bỏ): Cắt ngang theo Tầng Công nghệ (5 file ngang)**  
   Gom toàn bộ DB vào 1 file, toàn bộ API vào 1 file, toàn bộ UI vào 1 file. Bị loại vì buộc kỹ sư/agent phải đọc cả 5 file lớn cho mỗi tính năng nhỏ, gây tốn token và dễ lệch contract.
3. **Phương án 3 (Loại bỏ): Cắt dọc `00..07` + tách riêng `08-test-suite-spec.md`**  
   Tách kịch bản kiểm thử khỏi đặc tả module. Bị loại vì làm đứt quy trình TDD khi triển khai từng module.

---

## 5. Quyết Định Thiết Kế Đã Chốt & Đề Xuất Kỹ Thuật Mặc Định

### A. Các quyết định của người dùng (User Decisions)
- Tạo mới `docs/specs/` theo **Phương án 1** (`00` + `01..07`).
- Xóa toàn bộ 4 thư mục tài liệu cũ (`01-architecture`, `03-frontend-engineering`, `04-operations-and-cicd`, `05-testing-and-qa`) để không còn tài liệu trùng lặp.
- Bám sát 100% phạm vi `docs/PRD/00..07` đã chốt và loại bỏ hoàn toàn cơ chế SQLite fallback.

### B. Các lựa chọn kỹ thuật chi tiết do Kiến trúc sư đề xuất (`[Đề xuất kỹ thuật / Our Call]`)
Để người viết spec và người lập trình sau này không phải tự đoán, bản thiết kế chốt rõ các quyết định kỹ thuật cụ thể sau cho các phần `Delta`:

1. **`[Our Call]` Chiến lược CSDL cho Kiểm thử (`specs/00`):**
   - Unit test tầng `packages/core` và unit test logic dịch vụ/schema chạy thuần trong bộ nhớ với fake ports / mock repositories (tốc độ `< 1s`).
   - Integration test tầng `apps/api` (kiểm thử SQL thật, `pgvector` cosine/RRF, cascade delete, cô lập `user_id`) chạy trực tiếp trên database PostgreSQL kiểm thử riêng `TEST_DATABASE_URL` (`verischolar_test` với extension `vector`), dùng transaction rollback sau mỗi test thay vì `aiosqlite`.

2. **`[Our Call]` Hợp đồng API cho Khám phá Đề tài Zero-to-Reading (`specs/02`):**
   - Hiện tại `DiscoveryPage.tsx` đang tìm nhầm trong danh sách tài liệu đã tải lên máy chủ và Backend chưa có endpoint tìm bài báo mới theo chủ đề.
   - Bổ sung 2 endpoint chuẩn tại `apps/api/src/api/v1/endpoints/discovery.py` (mount vào `api_v1_router`):
     - `POST /api/v1/discovery/search`: Nhận `{ query, limit = 10 }`, truy vấn song song **Exa AI (`category="research paper"`) + Semantic Scholar + arXiv** (dedupe theo `doi` / `arxiv_id` / normalized title), trả về danh sách thẻ kết quả kèm cờ `open_access_pdf_url: str | None` và `access_status: "open_access_pdf" | "abstract_only"`.
     - `POST /api/v1/discovery/open-reading`: Nhận `{ title, authors, year, doi, arxiv_id, pdf_url, abstract }`, tải PDF về CAS `storage/blobs/` (kiểm tra `<= 50MB`, `<= 100 trang`, Digital PDF), kích hoạt parse, tạo `ResearchSession` mới gắn bài báo đó và trả về `{ session_id, document_id }` để Frontend điều hướng thẳng sang `/dashboard/{session_id}`.

3. **`[Our Call]` Hợp đồng đóng Tab PDF & tra cứu References (`specs/03` & `specs/04`):**
   - Bổ sung `DELETE /api/v1/sessions/{id}/documents/{document_id}` (Module 03) để đóng 1 bài báo khỏi thanh `DocumentTabBar.tsx` (giải phóng slot trong giới hạn 5 bài mà không xóa file PDF gốc).
   - Bổ sung `GET /api/v1/documents/{document_id}/references` (Module 04) trả về danh sách `reference_items` đã trích xuất/xác thực của bài báo để hiển thị tức thì Bảng 3 Cột mà không cần gọi lại `:extract-references` tốn phí.
   - Chuẩn hóa sự kiện SSE trên `POST /api/v1/sessions/{id}/messages`: bổ sung event/payload `bridge_hint` (`{ ref_index, concept_name, paper_title, authors, year, can_ingest }`) cho Lộ trình học tuần tự A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ D, và kiểm tra trạng thái `document.status` của các bài báo Tầng 2 đang tải dở (`progress < 100%`) hoặc `abstract_only` ngay tại bước Guardrail trước khi gọi LLM.

4. **`[Our Call]` Lược đồ Bảng `graph_nodes` & `graph_edges` cho GraphRAG 4 Thực thể (`specs/05`):**
   - Tạo `apps/api/src/api/db/models/graph.py` với 2 bảng thuần PostgreSQL + `pgvector`:
     - `graph_nodes`: `id (UUID PK)`, `user_id (UUID FK users.id ON DELETE CASCADE)`, `document_id (UUID FK documents.id ON DELETE CASCADE)`, `node_type` (`CHECK IN ('Paper', 'Method', 'Dataset', 'MetricResult')`), `canonical_name (Text)`, `description (Text | None)`, `metadata_json (JSONB)`, `source_chunk_id (UUID FK document_chunks.id ON DELETE SET NULL)`, `page_number (Int | None)`, `embedding (Vector(1536))` kèm chỉ mục HNSW.
     - `graph_edges`: `id (UUID PK)`, `user_id (UUID FK users.id ON DELETE CASCADE)`, `document_id (UUID FK documents.id ON DELETE CASCADE)`, `source_node_id (UUID FK graph_nodes.id ON DELETE CASCADE)`, `target_node_id (UUID FK graph_nodes.id ON DELETE CASCADE)`, `edge_type` (`CHECK IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')`), `evidence_chunk_id (UUID FK document_chunks.id ON DELETE SET NULL)`, `page_number (Int | None)`, `weight (Float)`.
   - Quy tắc vòng đời: Bấm `Star` kích hoạt `BackgroundTasks` trích xuất đồ thị cho bài báo; khi `Unstar` mà `is_starred = False` và `folder_id IS NULL` thì xóa các dòng `graph_nodes`/`graph_edges` của `(user_id, document_id)` đó để không bao giờ lộ vào truy vấn GraphRAG.

5. **`[Our Call]` Lược đồ `drafts`, `draft_assets`, `draft_messages` & Kiến trúc LangGraph + E2B (`specs/06`):**
   - Nâng cấp bảng `drafts`: thêm cột `bib_content (Text, default="")` và `source_session_id (UUID FK research_sessions.id ON DELETE SET NULL, nullable=True)`. Khi `POST /api/v1/drafts` có `source_session_id`, Backend tự động sinh nội dung `@article{...}` vào `bib_content` từ các bài báo trong phiên đọc (Cầu nối Đọc-sang-Viết).
   - Thay thế cơ chế lưu tạm asset hiện tại bằng bảng `draft_assets` (`id`, `draft_id FK CASCADE`, `user_id FK CASCADE`, `filename` chuẩn hóa an toàn trong `figures/`, `mime_type` thuộc `image/png | image/jpeg | application/pdf`, `byte_size`, `blob_hash FK document_storage_blobs`) với 3 API đầy đủ: `POST /api/v1/drafts/{id}/assets` (`multipart/form-data`), `GET /api/v1/drafts/{id}/assets`, `DELETE /api/v1/drafts/{id}/assets/{asset_id}`.
   - Thêm bảng `draft_messages` (`id`, `draft_id FK CASCADE`, `user_id FK CASCADE`, `role` thuộc `user | assistant | tool`, `content`, `tool_calls JSONB`, `compile_attempts Int`, `trace_id`, `created_at`) phục vụ `GET / POST / DELETE /api/v1/drafts/{id}/messages`.
   - Thêm dependency `langgraph` vào `apps/api/pyproject.toml`; cài đặt `WritingAgentGraph` (`StateGraph`) phát luồng SSE thời gian thực (`step_status` $\rightarrow$ `file_patch` $\rightarrow$ `compile_result` $\rightarrow$ `assistant_delta` $\rightarrow$ `done`) với đúng 4 tools (`edit_latex_files`, `list_project_files`, `query_library_graph_rag`, `compile_latex_e2b`) và bộ đếm `compile_attempts <= 3`. `compile_latex_e2b` ghi cả `main.tex`, `references.bib` và toàn bộ binary `figures/*` vào `/tmp/verischolar-latex/` trên E2B Sandbox rồi chạy chuỗi biên dịch có `bibtex` / `tectonic` với `--no-shell-escape`, timeout `15s`.

6. **`[Our Call]` Hợp đồng Giám sát 3 Tầng (`specs/07`):**
   - Thêm `sentry-sdk[fastapi]` ở Backend và `@sentry/react` ở Frontend (chỉ kích hoạt khi `SENTRY_DSN` có giá trị).
   - Mở rộng `PureASGITracingMiddleware` lưu bộ đếm trong bộ nhớ (`uptime_seconds`, tổng request, `2xx`/`4xx`/`5xx`, `avg_duration_ms`, `avg_ttfb_ms`, và `collections.deque(maxlen=20)` cho 20 lỗi gần nhất kèm `trace_id`) phục vụ `GET /api/v1/system/status`.
   - Thêm `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` nhận `{ score: 1 | 0, comment?: str }` đẩy điểm `user_feedback` gắn với `trace_id` của lượt chat đó lên Langfuse.
   - Bổ sung `AlertWebhookDispatcher` gửi cảnh báo bất đồng bộ (timeout 3s, chống bão cảnh báo trùng lặp theo cooldown 60s) tới Telegram/Discord qua `ALERT_WEBHOOK_URL` khi xảy ra lỗi `500` hoặc lỗi kết nối hạ tầng trên môi trường `production`.

### C. Kiểm Kê Toàn Diện CSDL (16 Bảng) & 6 Giải Pháp Khóa Rủi Ro Kỹ Thuật Ngầm (`[Rủi ro & Biện pháp giảm thiểu]`)

#### 1. Kiểm kê chính xác 16 bảng CSDL PostgreSQL MVP
Toàn bộ hệ thống VeriScholar MVP gồm đúng **16 bảng PostgreSQL** (12 bảng hiện có + 4 bảng tạo mới trong `Delta`), xóa bỏ hoàn toàn rủi ro thiếu bảng khi chia task:
- **12 Bảng hiện có** (`apps/api/src/api/db/models/`):
  1. `users` (`user.py`): Tài khoản học giả, mật khẩu bcrypt, BYOK AES-256-GCM.
  2. `documents` (`document.py`): Metadata tài liệu PDF, số trang, dung lượng, trạng thái parse.
  3. `document_chunks` (`chunk.py`): Các đoạn văn trích xuất, tọa độ bbox, nâng cấp cột `embedding` sang `Vector(1536)`.
  4. `document_storage_blobs` (`blob.py`): Quản lý file CAS theo mã băm SHA-256.
  5. `document_summaries` (`summary.py`): Tóm tắt cấu trúc và takeaways của tài liệu.
  6. `reference_items` (`reference.py`): Danh mục trích dẫn đã trích xuất/xác thực của bài báo.
  7. `research_sessions` (`session.py`): Phiên đọc sâu học thuật.
  8. `session_documents` (`session.py`): Bảng liên kết đa bài báo trong phiên (tối đa 5 bài đồng thời).
  9. `session_turns` (`session.py`): Lịch sử hội thoại hỏi đáp trong phiên đọc.
  10. `research_notes` (`note.py`): Sổ tay ghi chú học thuật gắn phiên đọc.
  11. `folders` (`folder.py`): Cây thư mục đề tài phân cấp trong Kho Yêu thích.
  12. `drafts` (`draft.py`): Không gian soạn thảo LaTeX; nâng cấp thêm `bib_content` và `source_session_id`.
- **4 Bảng tạo mới (`Delta`)**:
  13. `graph_nodes` (`graph.py`): Đỉnh tri thức 4 nhãn (`Paper`, `Method`, `Dataset`, `MetricResult`) kèm `Vector(1536)`.
  14. `graph_edges` (`graph.py`): Cạnh quan hệ 4 loại (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`).
  15. `draft_assets` (`draft.py` hoặc `draft_asset.py`): Quản lý hình ảnh/file tài sản đính kèm trong thư mục `figures/`.
  16. `draft_messages` (`draft.py` hoặc `draft_message.py`): Lịch sử hội thoại và phản hồi của LangGraph Co-Author Agent.

#### 2. Sáu (6) Rủi ro kỹ thuật ngầm & Giải pháp kiến trúc bắt buộc
1. **Rủi ro 1 — E2B `"base"` Template thiếu LaTeX & Fallback PyMuPDF giả lập:**
   - *Thực trạng:* `E2B_LATEX_TEMPLATE="base"` không có `pdflatex`/`bibtex`/`tectonic` và tắt internet. Hàm `_generate_in_memory_pdf_preview()` dùng PyMuPDF vẽ chữ thô lên trang trắng rồi trả về `success=True`, làm vô hiệu hóa cơ chế tự sửa lỗi 3 lần của LangGraph.
   - *Giải pháp:* Đặc tả `deploy/e2b.Dockerfile` dựng sẵn TeX Live / `tectonic`. Nâng cấp `ILatexCompilerPort` nhận trọn bộ `(main_tex, bib_content, figures/*)` với `--no-shell-escape`, timeout 15s. **Xóa vĩnh viễn `_generate_in_memory_pdf_preview()`**. Ở môi trường `development` chưa cấu hình `E2B_API_KEY`: Cho phép fallback sang CLI `tectonic` / `pdflatex` cài cục bộ; nếu máy local cũng không có CLI thì trả về lỗi rõ ràng (`success=False`, thông báo cấu hình E2B hoặc cài CLI) thay vì vẽ PDF giả.
2. **Rủi ro 2 — `document_chunks.embedding` là `JSONType` & lệ thuộc `LLM_PROVIDER`:**
   - *Thực trạng:* Hiện cột embedding lưu JSON text và truy vấn rank chunks trong RAM bằng Python. Gắn model embedding chung với `LLM_PROVIDER="docker-model-runner"` gây lỗi số chiều.
   - *Giải pháp:* Chuyển đổi cột sang `pgvector.sqlalchemy.Vector(1536)` + `content_tsv TSVECTOR` + chỉ mục `HNSW` & `GIN`. Viết truy vấn Hybrid Search (Cosine Vector + Full-Text Search + RRF `k=60`) trực tiếp trong PostgreSQL. Tách riêng biến cấu hình: `EMBEDDING_PROVIDER="openai"`, `EMBEDDING_MODEL="text-embedding-3-small"`, `EMBEDDING_DIM=1536`.
3. **Rủi ro 3 — Thiếu Alembic DDL & `init_sqlite_fallback()` crash runtime:**
   - *Thực trạng:* Không có Alembic khiến cột mới không tự cập nhật trên database cũ. `api/__init__.py` và `session.py` vẫn gọi `init_sqlite_fallback()` gây lỗi `ModuleNotFoundError: aiosqlite`. `draft_service.py` còn sót cache chia sẻ cũ.
   - *Giải pháp:* Đặc tả hàm `ensure_database_schema()` chạy các câu lệnh DDL idempotent (`CREATE EXTENSION IF NOT EXISTS vector`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`). Xóa hoàn toàn `init_sqlite_fallback()` (báo lỗi kết nối ngay nếu PostgreSQL chưa sẵn sàng) và xóa bỏ `_draft_share_cache`.
4. **Rủi ro 4 — Phân mảnh RAM đa worker Uvicorn & vòng đời `BackgroundTasks`:**
   - *Thực trạng:* `Dockerfile.api` chạy `--workers 4` khiến bộ nhớ cache và metrics bị chia cắt; `docker-compose.yml` thiếu Redis; `BackgroundTasks` nếu dùng chung `AsyncSession` của HTTP request sẽ lỗi khi request đóng.
   - *Giải pháp:* Lưu PDF biên dịch của Draft xuống đĩa CAS qua `drafts.pdf_preview_storage_path` (bỏ `_draft_pdf_cache` trong RAM); bổ sung `redis:7-alpine` vào `docker-compose.yml`; chuẩn hóa 1 async Uvicorn worker cho MVP; bắt buộc mọi tác vụ ngầm tự mở `AsyncSessionLocal()` độc lập; khi server khởi động tự động quét và chuyển các tài liệu kẹt `status="parsing"` quá 10 phút về `failed`.
5. **Rủi ro 5 — Ghi đè snapshot Undo & xung đột OCC `version` trong LangGraph retry:**
   - *Thực trạng:* Nếu LangGraph retry 3 lần mà mỗi lần đều ghi đè `previous_snapshot`, nút Undo sẽ khôi phục về bản lỗi của lần retry trước; thiếu `new_version` trong SSE khiến lần lưu tay tiếp theo bị lỗi `409 Conflict`.
   - *Giải pháp:* Chụp `previous_snapshot` **đúng 1 lần duy nhất trước Attempt 1** của mỗi phiên Agent. Đính kèm `new_version` trong sự kiện SSE `file_patch` / `done` để Frontend cập nhật state ngay lập tức.
6. **Rủi ro 6 — GitHub Actions CI thiếu service containers PostgreSQL & Redis:**
   - *Thực trạng:* Job `backend-checks` trong `.github/workflows/ci.yml` chưa khai báo container dịch vụ nên Integration Test với PostgreSQL thật sẽ thất bại trên CI.
   - *Giải pháp:* Bổ sung cấu hình `services: postgres (pgvector/pgvector:0.8.6-pg18)` và `redis (redis:7-alpine)` trong `.github/workflows/ci.yml`.

---

## 6. Cấu Trúc Thư Mục & Khuôn Mẫu Chuẩn Của Từng File Trong `docs/specs/`

### A. Sơ đồ cây thư mục `docs/` sau khi hoàn tất
```text
docs/
├── README.md                                          # Cổng điều hướng duy nhất trỏ tới PRD/ và specs/
├── PRD/                                               # Yêu cầu sản phẩm (Why & What) — đã dọn sạch chữ SQLite
│   ├── 00-overview-and-cleanup.md
│   ├── 01-auth-and-user.md
│   ├── 02-discovery-and-documents-crud.md
│   ├── 03-sessions-and-deep-reading-crud.md
│   ├── 04-context-table-and-roadmap.md
│   ├── 05-favorite-library-and-graphrag.md
│   ├── 06-agentic-overleaf-writing.md
│   └── 07-monitoring-and-langfuse.md
└── specs/                                             # Đặc tả kỹ thuật (How & Contracts & Tests)
    ├── 00-foundation-architecture-and-db.md
    ├── 01-auth-and-user-spec.md
    ├── 02-discovery-and-documents-spec.md
    ├── 03-sessions-and-deep-reading-spec.md
    ├── 04-context-table-and-roadmap-spec.md
    ├── 05-favorite-library-and-graphrag-spec.md
    ├── 06-agentic-overleaf-writing-spec.md
    └── 07-monitoring-and-langfuse-spec.md
```
*(Đã hoàn tất xóa sạch `docs/PRD/audit-backend-member2.md`, `docs/PRD/audit-frontend-member3.md`, và xóa toàn bộ 4 thư mục tài liệu cũ `docs/01-architecture/`, `docs/03-frontend-engineering/`, `docs/04-operations-and-cicd/`, `docs/05-testing-and-qa/`).*

### B. Khuôn mẫu 7 mục bắt buộc cho mỗi file `docs/specs/01..07`
Mỗi file `01..07` phải tuân thủ đúng cấu trúc chuẩn sau để kỹ sư/agent đọc và lập trình được ngay:
1. **Phạm vi & Bảng Đối Chiếu Hiện Trạng (`As-Is` vs `Delta`):** Liệt kê từng file Backend/Core/Frontend hiện có, đánh dấu rõ `[KEEP]`, `[MODIFY]`, `[CREATE]`, `[DELETE]`.
2. **Mô Hình Dữ Liệu & Ràng Buộc PostgreSQL (`Database Schema & Invariants`):** Bảng cột, kiểu SQL/SQLAlchemy, khóa ngoại `ON DELETE`, chỉ mục, và điều kiện lọc `WHERE user_id = :current_user_id`.
3. **Hợp Đồng API & Luồng Streaming (`REST & SSE Contracts`):** Method + Path, Auth requirement, Pydantic Request/Response schemas, cấu trúc các event SSE, và bảng mã lỗi HTTP (`400`, `401`, `403`, `404`, `409`, `422`, `500`, `503`).
4. **Thiết Kế Xử Lý Backend, Domain & AI Pipeline:** Sequence/State flow, giao diện Port trong `packages/core`, logic Service trong `apps/api`, khung Prompt tiếng Việt/Anh nhúng trong code và quy tắc Guardrails/Langfuse spans.
5. **Thiết Kế Giao Diện, State & Tương Tác Frontend (`apps/web`):** Cây Component, Route, Zustand store slice, TanStack Query keys/mutations, xử lý loading/empty/error (hiển thị `trace_id` + nút copy).
6. **Danh Mục Kịch Bản Kiểm Thử Bắt Buộc (`TDD Test Matrix`):** Liệt kê cụ thể tên nhóm test cho `packages/core/tests/`, `apps/api/tests/` (trên PostgreSQL test DB) và `apps/web/src/**/*.test.tsx` (Vitest), bao gồm cả happy path, multi-user isolation và edge cases cứng của PRD.
7. **Tiêu Chí Nghiệm Thu Kỹ Thuật (`Definition of Done`):** Danh sách kiểm tra ngắn gọn xác nhận module hoàn thành 100%.

---

## 7. Phần Dành Cho Người Biên Soạn Chi Tiết (What's Left to the Builder)

Khi thực thi kế hoạch viết 8 file `docs/specs/00..07`, người biên soạn sẽ:
- Đọc trực tiếp từng file code thực tế tương ứng trong `packages/core/src/`, `apps/api/src/` và `apps/web/src/` để ghi chính xác tên class, hàm, schema hiện có vào mục `As-Is`, tránh bịa tên file không tồn tại.
- Thiết kế chi tiết tên trường Pydantic/TypeScript và câu lệnh SQL/ORM cho các phần `Delta` tuân thủ đúng các quyết định ở Mục 5.
- Kiểm tra tự động toàn bộ liên kết Markdown nội bộ trong `docs/README.md`, `docs/PRD/` và `docs/specs/` đảm bảo 0 liên kết gãy và 0 từ khóa cấm (`Neo4j`, `aiosqlite`, `ComparisonMatrix`, `DeBERTa`).

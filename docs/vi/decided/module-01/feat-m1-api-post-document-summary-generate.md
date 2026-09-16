# Kế Hoạch Kỹ Thuật: Custom Method Sinh Mới Tóm Tắt 3 Ý (POST /api/v1/documents/{id}/summary:generate)

> **Mã tài liệu:** `FEAT-M1-API-14`  
> **Trạng thái:** `PLANNING / CHỜ PHÊ DUYỆT`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 16/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-document-summary-generate`  
> **API Canonical:** `POST /api/v1/documents/{id}/summary:generate`  
> **Chuẩn thiết kế:** Google AIP-136 (Custom Methods), RFC 7807 (Problem Details), RFC 7232 (Idempotency), Hexagonal Architecture.

---

## 1. Hiện Trạng & Đánh Giá Mức Độ Sẵn Sàng (Gap Analysis)

### 1.1. Những thành phần ĐÃ CÓ (Kế thừa từ Feature 13):
1. **Database Schema:** Bảng `document_summaries` đã được định nghĩa trong `docs/vi/design-database.md` và cài đặt hoàn chỉnh với PostgreSQL 16:
   - Các cột: `id (UUID PK)`, `document_id (UUID FK, UNIQUE, ON DELETE CASCADE)`, `problem_statement (TEXT)`, `problem_citations (JSONB)`, `contributions (TEXT)`, `contribution_citations (JSONB)`, `limitations (TEXT)`, `limitation_citations (JSONB)`, `total_tokens (INT)`, `latency_ms (INT)`, `created_at`, `updated_at`.
2. **Domain Entities & Value Objects:**
   - `DocumentSummary` và `SummaryPoint` tại `packages/core/src/core/domain/entities/summary.py`.
   - `BoundingBox` tại `packages/core/src/core/domain/value_objects/bounding_box.py`.
3. **Port Interface:** `IDocumentSummarizerPort` tại `packages/core/src/core/ports/summary.py` với phương thức bất đồng bộ `async def summarize(...)`.
4. **Idempotency Infrastructure:**
   - Cổng `IIdempotencyPort` (`packages/core/src/core/ports/idempotency.py`).
   - Cài đặt `RedisIdempotencyAdapter` và `InMemoryIdempotencyAdapter` (`packages/core/src/core/adapters/cache/idempotency.py`).
   - Dependency `get_idempotency_port()` trong `apps/api/src/api/deps.py`.
5. **Heuristic Summarizer Adapter:** `HeuristicGroundedSummarizer` với khả năng bóc tách offline và tìm kiếm tọa độ vi mô (Micro-precision search via PyMuPDF).

### 1.2. Những thành phần CHƯA CÓ (Cần xây dựng trong Feature 14):
1. **Pydantic Request Schema:** Chưa có schema `DocumentSummaryGenerateRequest` (`force: bool = False`) cho body của `POST .../summary:generate`.
2. **Endpoint Router:** Chưa có route `POST /{document_id}/summary:generate` trong `apps/api/src/api/v1/endpoints/documents.py`.
3. **Service Logic cho Custom Method:** Chưa có hàm `generate_document_summary()` trong `DocumentService` để xử lý logic:
   - Kiểm tra khóa khử trùng lặp `Idempotency-Key` qua Header.
   - Kiểm tra cờ `force`: nếu `false` và đã có tóm tắt trong DB -> trả về cache hit; nếu `true` -> ép buộc tính toán/tổng hợp lại (re-synthesis) và cập nhật bản ghi trong DB (`updated_at = NOW()`).
4. **Adapter LLM Thực Tế (Cost-Aware & Grounded):**
   - Tạo adapter `LLMGroundedSummarizer` có khả năng giao tiếp với LLM Provider (OpenAI API / Docker Model Runner / Ollama) trích xuất 3 luận điểm kèm câu dẫn chứng nguyên văn (verbatim quotes) để khớp tọa độ PDF.
   - Cơ chế Fallback an toàn (Zero-Downtime Resilience): nếu LLM service offline hoặc chưa cấu hình API key, tự động fallback về `HeuristicGroundedSummarizer` để CI và luồng kiểm thử không bao giờ bị gián đoạn.
5. **Bộ Kiểm Thử Tự Động (Unit/Integration Test):** File `apps/api/tests/test_documents_summary_generate.py`.
6. **Evaluation Runner & Báo Cáo Markdown:** File `scripts/eval/runners/post_documents_summary_generate.py` và tích hợp vào `scripts/eval_api.py`.

---

## 2. Rà Soát Biến Môi Trường (.env.example)

Tuân thủ nguyên tắc bảo mật **TUYỆT ĐỐI KHÔNG ĐỌC FILE `.env`**, đối chiếu với `.env.example`:

### Các biến hiện có trong `.env.example`:
- `LLM_PROVIDER=openai` (hoặc `docker-model-runner`)
- `OPENAI_API_KEY=`
- `OPENAI_BASE_URL=https://api.openai.com/v1`
- `OPENAI_MODEL=5.6-luna`

### Cập nhật cần thiết vào mã nguồn cấu hình (`Settings` trong `apps/api/src/api/core/config.py`):
- Trong `apps/api/src/api/core/config.py`, thuộc tính `OPENAI_BASE_URL` hiện chưa được khai báo (mới chỉ có `OPENAI_API_KEY` và `OPENAI_MODEL`).
- Cần bổ sung vào `Settings`:
  ```python
  OPENAI_BASE_URL: str = "https://api.openai.com/v1"
  ```
- **Không cần tạo biến môi trường mới vào `.env.example`** vì các biến này đã được khai báo sẵn đầy đủ. Khi người dùng muốn chạy kiểm thử thực tế với LLM, người dùng chỉ cần điền `OPENAI_API_KEY` vào `.env` cá nhân của họ.

---

## 3. Phân Tích Rủi Ro & Đánh Đổi Kỹ Thuật (Risk Analysis & Trade-offs)

| Rủi ro kỹ thuật | Mức độ | Giải pháp kỹ thuật xử lý triệt để |
| :--- | :---: | :--- |
| **Gửi yêu cầu trùng lặp khi tính toán nặng** (Thao tác LLM/tính toán tốn thời gian, người dùng click liên tục) | **CAO** | Bắt buộc hỗ trợ Header `Idempotency-Key: <UUID>`. Lưu response trong Redis/Memory cache với TTL 24 giờ. Trả về ngay `X-Cache: Idempotent-Hit` nếu nhận cùng một key trong vòng 24h. |
| **LLM Call Timeout hoặc Rớt Mạng / Hết Quota API** | **CAO** | Áp dụng mẫu hình **Hybrid Resilient Fallback**: Bọc cuộc gọi LLM trong khối `try-except` với `httpx.TimeoutException` (giới hạn 30s). Nếu thất bại, ghi log cảnh báo và tự động fallback sang `HeuristicGroundedSummarizer`. Người dùng luôn nhận được tóm tắt có tọa độ dẫn chứng mà không bao giờ bị trả về mã lỗi 500. |
| **Hallucination trong Tọa độ Bounding Box của LLM** | **CAO** | **Không yêu cầu LLM đoán số tọa độ bounding box**. Thay vào đó, yêu cầu LLM trích xuất **câu văn bằng chứng nguyên văn (exact verbatim quote)** từ văn bản của chunk. Sau đó, adapter sử dụng PyMuPDF (`page.search_for`) để tính toán tọa độ vật lý chính xác 100% trên trang PDF. |
| **Xung đột ghi đồng thời (Race Condition) khi `force=true`** | **TRUNG BÌNH** | Sử dụng câu lệnh Upsert (`INSERT ... ON CONFLICT (document_id) DO UPDATE`) hoặc truy vấn khóa dòng `with_for_update()` trong phiên giao dịch SQLAlchemy Async, đảm bảo không bao giờ sinh ra 2 bản ghi cho cùng 1 tài liệu. |
| **Ảnh hưởng tới SLA của toàn hệ thống** | **THẤP** | Khi `force=false` (mặc định), hệ thống kiểm tra bảng `document_summaries` trước. Nếu đã có dữ liệu, trả về ngay lập tức (< 10ms) với header `X-Cache: Cache-Hit`. Chỉ kích hoạt tổng hợp mới khi chưa có tóm tắt hoặc người dùng chủ động truyền `force=true`. |

---

## 4. Phân Rã Thiết Kế Theo Kiến Trúc Lục Giác (Hexagonal Architecture)

### 4.1. Tầng Core Domain & Ports (`packages/core`)
- **Entities & Value Objects:** Sử dụng `DocumentSummary` và `SummaryPoint` tại `packages/core/src/core/domain/entities/summary.py`.
- **Port Interface:** Giữ vững giao ước hợp đồng trong `packages/core/src/core/ports/summary.py`:
  ```python
  class IDocumentSummarizerPort(Protocol):
      async def summarize(
          self,
          document_id: UUID,
          title: str | None,
          abstract: str | None,
          chunks: list[DocumentChunk],
          pdf_bytes: bytes | None = None,
      ) -> DocumentSummary:
          ...
  ```
- **Ràng buộc:** Tuyệt đối không import thư viện I/O (FastAPI, SQLAlchemy, httpx, fitz) vào tầng Domain entities.

### 4.2. Tầng Driven Adapters (Hạ Tầng Suy Luận & Tóm Tắt)
Xây dựng lớp `LLMGroundedSummarizer` kế thừa `IDocumentSummarizerPort`:
- **Vị trí file:** `apps/api/src/api/adapters/llm_summarizer.py`.
- **Cơ chế hoạt động:**
  1. Gửi request bất đồng bộ tới endpoint OpenAI-compatible (`/chat/completions`) sử dụng `httpx.AsyncClient`.
  2. Sử dụng Structured Output / JSON Mode với schema:
     ```json
     {
       "problem_statement": "Mô tả vấn đề nghiên cứu",
       "problem_quote": "Câu trích dẫn nguyên văn từ bài báo",
       "contributions": "Mô tả đóng góp cốt lõi",
       "contribution_quote": "Câu trích dẫn nguyên văn từ bài báo",
       "limitations": "Mô tả hạn chế và hướng phát triển",
       "limitation_quote": "Câu trích dẫn nguyên văn từ bài báo"
     }
     ```
  3. Lấy các `_quote` đối chiếu với file PDF gốc qua PyMuPDF (`page.search_for`) để sinh ra danh sách `BoundingBox` chuẩn hóa `[x0, y0, x1, y1, page]`.
  4. Nếu `OPENAI_API_KEY` trống hoặc cuộc gọi LLM gặp lỗi mạng/timeout: Tự động chuyển giao sang `HeuristicGroundedSummarizer` thực thi mượt mà.

### 4.3. Tầng Application Services (`DocumentService`)
Thêm phương thức `generate_document_summary` vào `apps/api/src/api/services/document_service.py`:
```python
async def generate_document_summary(
    self,
    document_id: UUID,
    user_id: str,
    force: bool,
    db: AsyncSession,
) -> tuple[DocumentSummaryEnvelope, str]:
    """
    Sinh mới hoặc lấy lại bản tóm tắt 3 ý cốt lõi.
    Trả về: (DocumentSummaryEnvelope, cache_status: 'Cache-Hit' | 'Generated')
    """
```
**Quy trình nghiệp vụ 6 bước:**
1. **Multi-tenant & Document Guard:** Kiểm tra sự tồn tại của tài liệu theo `document_id`. Nếu không thấy hoặc `doc.user_id != user_id` -> ném lỗi `404 DOCUMENT_NOT_FOUND`.
2. **Lifecycle Status Guard:**
   - Nếu tài liệu đang ở trạng thái `pending` hoặc `processing` -> ném lỗi `409 DOCUMENT_PROCESSING`.
   - Nếu tài liệu ở trạng thái `failed` -> ném lỗi `422 DOCUMENT_FAILED`.
3. **Kiểm tra Cache khi `force=false`:**
   - Truy vấn bảng `document_summaries`.
   - Nếu đã tồn tại bản ghi -> Ánh xạ sang `DocumentSummaryEnvelope`, trả về kèm nhãn `Cache-Hit` (SLA < 10ms).
4. **Thực thi Re-synthesis (khi `force=true` hoặc chưa có bản tóm tắt):**
   - Đảm bảo danh sách chunks tồn tại (trích xuất on-demand từ blob storage nếu thiếu).
   - Đọc luồng `pdf_bytes` từ CAS Storage.
   - Gọi `await self.summarizer.summarize(...)` tính toán 3 ý và tọa độ vi mô.
5. **Cập nhật / Lưu trữ Database (Upsert):**
   - Nếu đã có bản ghi `DocumentSummaryModel`: cập nhật toàn bộ các trường `problem_statement`, `problem_citations`, `contributions`, `contribution_citations`, `limitations`, `limitation_citations`, `total_tokens`, `latency_ms`, và đặt `updated_at = datetime.now(UTC)`.
   - Nếu chưa có: tạo bản ghi mới và thêm vào session.
   - Thực hiện `await db.commit()` và `await db.refresh(...)`.
6. **Đóng gói dữ liệu:** Ánh xạ dữ liệu sang `DocumentSummaryEnvelope` với đầy đủ metadata và trả về kèm nhãn `Generated`.

### 4.4. Tầng Driving Adapter (API Controller / Router)
Thêm endpoint mới vào `apps/api/src/api/v1/endpoints/documents.py`:
- **URI:** `POST /api/v1/documents/{document_id}/summary:generate`
- **Headers:**
  - `Idempotency-Key: Optional[str]` (Header alias)
  - `X-User-Id: str` (User context)
- **Request Body:** `DocumentSummaryGenerateRequest` (`force: bool = False`)
- **Dependencies:**
  - `current_user: UserModel = Depends(get_current_user)`
  - `doc_service: DocumentService = Depends(get_document_service)`
  - `idempotency: IIdempotencyPort = Depends(get_idempotency_port)`
  - `db: AsyncSession = Depends(get_async_db)`
- **Xử lý Idempotency:**
  ```python
  if idempotency_key:
      cache_key = f"idempotency:summary_generate:{current_user.id}:{document_id}:{idempotency_key}"
      cached_resp = await idempotency.get_response(cache_key)
      if cached_resp:
          return JSONResponse(content=cached_resp, headers={"X-Cache": "Idempotent-Hit"})
  ```
  Sau khi sinh thành công, nếu có `idempotency_key`, lưu kết quả vào `idempotency.store_response(...)` với TTL 24 giờ (86,400 giây).
- **HTTP Headers trả về:**
  - `X-Cache: Idempotent-Hit | Cache-Hit | Generated`

---

## 5. Hệ Thống Kiểm Chuẩn 2 Cấp Độ (Unit Test & Evaluation Snapshot)

Tuyệt đối **KHÔNG** tạo endpoint backdoor `/api/v1/testing/...`. Mọi kiểm thử đều đi qua luồng REST API công khai.

### 5.1. Cấp độ 1: Unit & Integration Pytest Suite
Tạo file kiểm thử `apps/api/tests/test_documents_summary_generate.py` bao phủ 9 kịch bản kiểm thử:
1. `test_generate_summary_default_cache_hit`: Gọi với `force=False` khi đã có summary trong DB -> trả về dữ liệu cũ với header `X-Cache: Cache-Hit`.
2. `test_generate_summary_forced_resynthesis`: Gọi với `force=True` -> cập nhật bản ghi trong DB, trả về `X-Cache: Generated`, thời gian `updated_at` được làm mới.
3. `test_generate_summary_initial_synthesis`: Gọi lần đầu khi chưa có summary trong DB -> tự động tạo mới thành công.
4. `test_generate_summary_idempotency_hit`: Gửi cùng 1 `Idempotency-Key` 2 lần liên tiếp -> lần 2 nhận lại chính xác payload cũ với header `X-Cache: Idempotent-Hit`.
5. `test_generate_summary_bounding_boxes_validity`: Kiểm tra toàn bộ tọa độ trong 3 luận điểm tuân thủ đúng chuẩn 5-tuple `[x0, y0, x1, y1, page]`, `0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`.
6. `test_generate_summary_not_found`: Truy vấn document UUID ngẫu nhiên -> trả về `404 DOCUMENT_NOT_FOUND`.
7. `test_generate_summary_multi_tenant_isolation`: Truy vấn document của người dùng khác -> trả về `404 DOCUMENT_NOT_FOUND`.
8. `test_generate_summary_conflict_processing`: Document có status `processing` -> trả về `409 DOCUMENT_PROCESSING`.
9. `test_generate_summary_unprocessable_failed_or_invalid_uuid`: Document có status `failed` -> `422 DOCUMENT_FAILED`, UUID sai định dạng -> `422 Unprocessable Entity`.

### 5.2. Cấp độ 2: Autotest Snapshot Runner & Báo Cáo Nghiệp Vụ
Xây dựng runner `scripts/eval/runners/post_documents_summary_generate.py`:
- Chạy qua giao thức chuẩn `In-Process ASGI` hoặc `HTTP Live Server`.
- Thực hiện chuỗi kịch bản end-to-end:
  - Seed tài liệu benchmark PDF.
  - Lần 1: Gọi `POST .../summary:generate` với `force=false` -> Ghi nhận phản hồi và thời gian trích xuất ban đầu.
  - Lần 2: Gọi `POST .../summary:generate` với `force=false` kèm `Idempotency-Key` -> Xác thực phản hồi Cache Hit siêu tốc (< 10ms).
  - Lần 3: Gọi lại với cùng `Idempotency-Key` -> Xác thực phản hồi Idempotency Hit.
  - Lần 4: Gọi `POST .../summary:generate` với `force=true` -> Xác thực cơ chế ép buộc tái tổng hợp (Forced Re-synthesis).
  - Kiểm tra các trường hợp biên: Document không tồn tại (404), UUID sai định dạng (422).
- Xuất báo cáo tự động sang: `temp/output/test/post_documents_summary_generate.md`.
- Tích hợp runner vào `scripts/eval_api.py` với alias ngắn `--api summary_generate` hoặc `generate_summary`.
- Cập nhật tài liệu hướng dẫn:
  - `scripts/README.md`.
  - `docs/vi/design-api-eval-snapshots.md`.
  - `docs/vi/swagger.md`.

---

## 6. Tiêu Chí Nghiệm Thu Chất Lượng (Quality Gates)

Một tính năng chỉ được xem là hoàn tất khi vượt qua 100% các tiêu chí sau:
1. **Pytest Coverage:** Toàn bộ test suite `apps/api/tests/` đạt tỷ lệ thành công 100% (124+ passed, 0 failures).
2. **Lint & Formatting:** `uv run ruff check .` và `uv run ruff format --check .` đều không có bất kỳ lỗi nào.
3. **Evaluation Harness CI Gate:** `uv run python scripts/eval_api.py --all --ci-gate` đạt **14/14 APIs PASSED**.
4. **Zero-Retention Guarantee:** Chạy `uv run python scripts/eval/purge_all.py` dọn dẹp sạch toàn bộ tài liệu thử nghiệm sau kiểm thử, trả về trạng thái database 0 bản ghi.

---

## 7. Quy Trình Các Bước Thực Thi (Step-by-Step Execution Plan)

1. **Bước 1: Tạo Git branch** `feat/m1-api-document-summary-generate`.
2. **Bước 2: Cập nhật config & schemas:**
   - Thêm `OPENAI_BASE_URL` vào `Settings` (`apps/api/src/api/core/config.py`).
   - Thêm `DocumentSummaryGenerateRequest` vào `apps/api/src/api/schemas/document.py`.
3. **Bước 3: Xây dựng LLMGroundedSummarizer với Hybrid Fallback:**
   - Tạo file `apps/api/src/api/adapters/llm_summarizer.py`.
   - Kết nối OpenAI-compatible API, cấu trúc trích dẫn verbatim quotes và khớp vi mô tọa độ PDF.
   - Fallback an toàn sang `HeuristicGroundedSummarizer` khi offline.
4. **Bước 4: Cài đặt logic Service:**
   - Thêm `generate_document_summary()` vào `DocumentService`.
5. **Bước 5: Thêm Router Endpoint & Idempotency:**
   - Thêm `POST /api/v1/documents/{document_id}/summary:generate` với header `Idempotency-Key` vào `apps/api/src/api/v1/endpoints/documents.py`.
6. **Bước 6: Viết Unit & Integration Tests:**
   - Tạo file `apps/api/tests/test_documents_summary_generate.py` (9 kịch bản).
7. **Bước 7: Viết Eval Runner:**
   - Tạo file `scripts/eval/runners/post_documents_summary_generate.py`.
   - Đăng ký runner vào `scripts/eval/runners/__init__.py` và `scripts/eval_api.py`.
8. **Bước 8: Cập nhật Documentation:**
   - Bổ sung endpoint vào `docs/vi/swagger.md`, `scripts/README.md`, `docs/vi/design-api-eval-snapshots.md`.
9. **Bước 9: Kiểm tra chất lượng & Dọn dẹp dữ liệu:**
   - `uv run ruff check .` & `uv run ruff format .`
   - `uv run pytest apps/api/tests/`
   - `uv run python scripts/eval_api.py --all --ci-gate`
   - `uv run python scripts/eval/purge_all.py`
10. **Bước 10: Báo cáo kết quả và chờ lệnh git commit / tạo PR từ người dùng.**

---

## 8. Trạng Thái Hiện Tại

- Kế hoạch kỹ thuật đã được lập chi tiết và hoàn chỉnh.
- **TUYỆT ĐỐI CHƯA CÓ DÒNG CODE NÀO ĐƯỢC VIẾT.**
- Hệ thống đang dừng lại chờ bạn xem xét và phê duyệt kế hoạch.

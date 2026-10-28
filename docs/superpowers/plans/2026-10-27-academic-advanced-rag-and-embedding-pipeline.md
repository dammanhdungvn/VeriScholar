# Academic Advanced RAG & Embedding Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triệt tiêu hoàn toàn điểm mù truy vấn học thuật, khắc phục 100% lỗi "AI bảo không có công thức" và "Lệch Bounding Box" bằng kiến trúc Agentic Dual-Index Advanced RAG chuẩn production (Batch Embedding 1536d, Query Condense Type II, HyDE Cross-Lingual Bridging, Dual-Stream HNSW Cosine + BM25 RRF $k=60$, CRAG Window Expansion $[i-1, i+1]$ và Golden Bounding Box $\text{IoU} \ge 0.85$).

**Architecture:** Tách biệt 2 tầng: Tầng 1 (Offline Ingestion & Dual Indexing) bắt buộc sinh vector 1536 chiều (`text-embedding-3-small`) và lưu Bounding Box $[0..1000]$ vào `pgvector` HNSW và PostgreSQL GIN; Tầng 2 (Online Agentic Inference) sử dụng Condense Chat History + HyDE để xóa nhòa rào cản đa ngôn ngữ (Hỏi Tiếng Việt trên tài liệu Tiếng Anh), hợp nhất xếp hạng RRF $k=60$ và kiểm định CRAG với mở rộng cửa sổ lân cận $[i-1, i+1]$ để bảo toàn công thức toán học đa dòng.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16 `pgvector` (HNSW) + `tsvector` (GIN), OpenAI API (`text-embedding-3-small`), PyMuPDF, Langfuse Observability, React 19 Canvas.

**Spec:** [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md) và [`docs/PRD/03-sessions-and-deep-reading-crud.md`](../../PRD/03-sessions-and-deep-reading-crud.md).

## Global Constraints

- **Bất biến Vector Không Rỗng:** Tuyệt đối cấm lưu `embedding = NULL` trong bảng `document_chunks`. Mọi chunk phải có vector 1536 chiều.
- **Bất biến TDD:** Luôn viết test đỏ trước $\rightarrow$ Viết code xanh tối thiểu $\rightarrow$ Refactor.
- **Bất biến Kiến trúc Lục giác:** `packages/core/` chỉ dùng Standard Library và `pydantic`, cấm import DB hay FastAPI.
- **Chuẩn hóa Bounding Box:** Tọa độ chuẩn hóa trong dải $[0..1000]$ dạng mảng 5 phần tử `[x0, y0, x1, y1, page]` tương thích 100% với `DocumentChunkModel` và `BboxHighlightLayer`.
- **Quy chuẩn Markdown:** Chỉ sử dụng đường dẫn tương đối trong toàn bộ tài liệu và code docs, cấm dùng `file://`.
- **Đồng bộ VPS tự động (Rule 9):** Chạy `bash scripts/deploy_to_vps.sh --fast` sau mỗi commit trong plan.

## Review Focus

1. **Truy vấn Tiếng Việt trên bài báo Tiếng Anh (Cross-lingual retrieval failure):** Khi học giả hỏi *"Công thức AR trong paper là gì?"*, HyDE phải sinh Virtual Document Tiếng Anh để vector cosine khớp trúng Chunk 19/20 ở Trang 3 thay vì Abstract Trang 1.
2. **Công thức toán học bị cắt đôi qua 2 chunks (Multiline equation boundary split):** Khi công thức toán nằm ở cuối chunk $i$ và tràn sang đầu chunk $i+1$, cơ chế CRAG Window Expansion phải tự động gom cả $[i-1, i+1]$ để cấp đủ biểu thức.
3. **Bài báo "Mở Đọc Sâu" từ Discovery bị kẹt 0 chunks:** `open_reading_session` phải kích hoạt `BackgroundTasks` bóc tách PyMuPDF và sinh embedding, không để tài liệu kẹt mãi ở `status='parsing'`.
4. **Active Abstention khi thông tin không có trong bài:** Khi câu hỏi yêu cầu dữ liệu ngoài luồng với độ tin cậy $\tau < 0.20$, hệ thống phải chủ động từ chối, tuyệt đối không bịa đặt.
5. **Độ trễ truy vấn Hybrid Search:** Câu lệnh SQL CTE RRF $k=60$ phải chạy trực tiếp trong PostgreSQL dưới 80ms trên tập chỉ mục HNSW và GIN.

---

### Task 1: OpenAI Batch Embedding Service (`embedding_service.py`)

**Files:**
- Create: `apps/api/src/api/services/embedding_service.py`
- Test: `apps/api/tests/unit/test_embedding_service.py`

**Interfaces:**
- Consumes: `settings.OPENAI_API_KEY` từ `api.core.config`
- Produces: `EmbeddingService.get_embedding(text: str) -> list[float]`, `EmbeddingService.get_embeddings_batch(texts: list[str], batch_size: int = 128) -> list[list[float]]` (vector 1536 chiều).

- [x] **Step 1: Write the failing unit test for `EmbeddingService`**

```python
# apps/api/tests/unit/test_embedding_service.py
import pytest
from unittest.mock import AsyncMock, patch
from api.services.embedding_service import EmbeddingService

@pytest.mark.asyncio
async def test_get_embedding_returns_1536_dim_vector():
    service = EmbeddingService(api_key="test-key")
    with patch.object(service, "_call_openai_embedding", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = [[0.01] * 1536]
        vec = await service.get_embedding("Answer Relevance formula")
        assert len(vec) == 1536
        assert isinstance(vec[0], float)

@pytest.mark.asyncio
async def test_get_embeddings_batch_handles_chunking():
    service = EmbeddingService(api_key="test-key")
    texts = ["text1", "text2", "text3"]
    with patch.object(service, "_call_openai_embedding", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = [[0.01] * 1536, [0.02] * 1536, [0.03] * 1536]
        results = await service.get_embeddings_batch(texts, batch_size=2)
        assert len(results) == 3
        assert len(results[0]) == 1536
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/unit/test_embedding_service.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'api.services.embedding_service'`

- [x] **Step 3: Implement `EmbeddingService` in `apps/api/src/api/services/embedding_service.py`**

Triển khai client gọi OpenAI Embedding API model `text-embedding-3-small` (1536 dimensions), có cơ chế batching phân đoạn ($\le 128$ texts/lần), kiểm tra rỗng và xử lý ngoại lệ mạng.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/unit/test_embedding_service.py -v`  
Expected: PASS with 2 tests passed.

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/api/src/api/services/embedding_service.py apps/api/tests/unit/test_embedding_service.py
git commit -m "feat(rag): add openai batch embedding service with 1536 dimensions"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Background Ingestion Fix & Chunk Embedding Backfill Script

**Files:**
- Modify: `apps/api/src/api/services/document_service.py:1034, 1857, 2014, 2315, 2492` (Toàn bộ 5 vị trí gán `embedding=None`)
- Modify: `apps/api/src/api/v1/endpoints/discovery.py:80-165`
- Create: `scripts/backfill_chunk_embeddings.py`
- Test: `apps/api/tests/test_open_reading_pdf_ingestion.py`

**Interfaces:**
- Consumes: `EmbeddingService` từ Task 1
- Produces: `DocumentService.parse_document_background` tạo chunks với `embedding != None`; `open_reading_session` kích hoạt `background_tasks.add_task`.

- [x] **Step 1: Write failing test verifying `open_reading_session` schedules background ingestion**

```python
# apps/api/tests/test_open_reading_pdf_ingestion.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from api.v1.endpoints.discovery import open_reading_session
from api.schemas.discovery import OpenReadingRequest

@pytest.mark.asyncio
async def test_open_reading_schedules_background_parsing(db_session, test_user):
    bg_tasks = MagicMock()
    payload = OpenReadingRequest(
        title="Ragas Evaluation Paper",
        pdf_url="https://arxiv.org/pdf/2309.15217.pdf",
        authors=["Es et al."],
        publication_year=2023,
    )
    with patch("api.services.document_service.DocumentService.ingest_pdf_from_url", new_callable=AsyncMock) as mock_ingest:
        mock_ingest.return_value = ("fake_hash_123", 102400)
        res = await open_reading_session(
            payload=payload,
            background_tasks=bg_tasks,
            current_user=test_user,
            db=db_session,
        )
        assert res.data.document_status in ["parsing", "processing"]
        assert bg_tasks.add_task.called
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_open_reading_pdf_ingestion.py -v`  
Expected: FAIL because `open_reading_session` does not accept `background_tasks` or does not call `add_task`.

- [x] **Step 3: Implement fixes in `discovery.py`, `document_service.py`, and create `backfill_chunk_embeddings.py`**

1. Cập nhật `open_reading_session` nhận `background_tasks: BackgroundTasks` và gọi `background_tasks.add_task(service.parse_document_background, doc_id, current_user.id)`.
2. Trong `document_service.py`, quét sạch toàn bộ 5 vị trí `embedding=None` (dòng 1034, 1857, 2014, 2315, 2492), tạo hàm helper `_generate_chunk_embeddings(...)` gọi `embedding_service.get_embeddings_batch([c.text for c in chunks])`.
3. Bổ sung bóc tách **4 Trụ Cột Summary Index** (`original_problem`, `proposed_solution`, `key_insights`, `quantitative_results`) lưu vào `documents.parsed_metadata["summary_metadata"]`.
4. Viết script `scripts/backfill_chunk_embeddings.py` quét toàn bộ chunks có `embedding IS NULL` trong database, gọi OpenAI tính vector 1536d và cập nhật lại.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_open_reading_pdf_ingestion.py -v`  
Expected: PASS

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/api/src/api/v1/endpoints/discovery.py apps/api/src/api/services/document_service.py scripts/backfill_chunk_embeddings.py apps/api/tests/test_open_reading_pdf_ingestion.py
git commit -m "fix(ingestion): schedule background parsing in open-reading and eliminate all null embeddings"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Query Improvement Engine (Condense Type II & HyDE Cross-Lingual Generator)

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:150-250`
- Test: `apps/api/tests/unit/test_query_transformation_and_hyde.py`

**Interfaces:**
- Consumes: `EmbeddingService` từ Task 1, `session_turns` (chat history)
- Produces: `SessionChatService.transform_query(raw_query: str, chat_history: list[dict]) -> tuple[str, list[float]]` trả về `(condensed_query, hyde_embedding)`.

- [x] **Step 1: Write failing unit test for `transform_query` with HyDE**

```python
# apps/api/tests/unit/test_query_transformation_and_hyde.py
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from api.services.session_chat_service import SessionChatService

@pytest.mark.asyncio
async def test_transform_query_generates_condensed_and_hyde_vector(db_session):
    service = SessionChatService(db=db_session)
    with patch.object(service, "_generate_hyde_doc", new_callable=AsyncMock) as mock_hyde, \
         patch("api.services.embedding_service.EmbeddingService.get_embedding", new_callable=AsyncMock) as mock_embed:
        mock_hyde.return_value = "Answer Relevance (AR) formula in Ragas evaluates cosine similarity..."
        mock_embed.return_value = [0.05] * 1536
        
        condensed_q, hyde_vec = await service.transform_query(
            raw_query="Công thức AR của nó là gì?",
            chat_history=[{"role": "user", "content": "Tôi đang đọc bài báo Ragas"}]
        )
        assert "Ragas" in condensed_q or "AR" in condensed_q
        assert len(hyde_vec) == 1536
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/unit/test_query_transformation_and_hyde.py -v`  
Expected: FAIL with `AttributeError: 'SessionChatService' object has no attribute 'transform_query'`

- [x] **Step 3: Implement `transform_query` and HyDE in `session_chat_service.py`**

Xây dựng hàm Condense kết hợp lịch sử chat 5 lượt gần nhất, sau đó sinh Virtual English Document học thuật (100-150 từ) và gọi `embedding_service` để tính vector 1536 chiều.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/unit/test_query_transformation_and_hyde.py -v`  
Expected: PASS

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/unit/test_query_transformation_and_hyde.py
git commit -m "feat(rag): add chat engine type II condense query and hyde cross-lingual generator"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Dual-Stream HNSW + BM25 RRF Search & CRAG Window Expansion

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:153-220, 1070-1120`
- Test: `apps/api/tests/unit/test_crag_and_window_expansion.py`

**Interfaces:**
- Consumes: `query_embedding` từ Task 3, `document_chunks` table
- Produces: `retrieve_hybrid_chunks` truyền vector vào CTE `embedding <=> :query_vec`; `evaluate_crag_and_expand` mở rộng lân cận $[i-1, i+1]$ khi $\tau \in [0.20, 0.35)$.

- [x] **Step 1: Write failing test for CRAG Window Expansion**

```python
# apps/api/tests/unit/test_crag_and_window_expansion.py
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from api.services.session_chat_service import SessionChatService

@pytest.mark.asyncio
async def test_crag_expands_adjacent_chunks_when_ambiguous(db_session):
    service = SessionChatService(db=db_session)
    doc_id = uuid4()
    candidate_chunks = [
        {"chunk_id": uuid4(), "document_id": doc_id, "chunk_index": 19, "page_number": 3, "cosine_sim": 0.28, "content": "AR = (1/n) * sum("}
    ]
    with patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj:
        mock_adj.return_value = [
            {"chunk_id": uuid4(), "document_id": doc_id, "chunk_index": 20, "page_number": 3, "content": "cos(q, q_i)) where q is query"}
        ]
        verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
        assert verdict == "AMBIGUOUS_EXPANDED"
        assert len(final_chunks) == 2
        assert not abstain
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/unit/test_crag_and_window_expansion.py -v`  
Expected: FAIL with `AttributeError: 'SessionChatService' object has no attribute 'evaluate_crag_and_expand'`

- [x] **Step 3: Implement CTE Vector Search & CRAG Evaluation in `session_chat_service.py`**

1. Cập nhật `retrieve_hybrid_chunks` để truyền `query_embedding` bắt buộc vào câu lệnh CTE PostgreSQL RRF $k=60$. Ép kiểu `CAST(:hyde_vector AS vector)`, sắp xếp `ORDER BY` trước khi lấy `LIMIT 25` để kích hoạt chỉ mục HNSW/GIN, sử dụng `= ANY(:active_doc_ids)` và `JOIN documents d` để lấy tiêu đề bài báo:
   ```sql
   WITH vector_ranks AS (
       SELECT id, document_id, chunk_index, page_number, content, bounding_boxes,
              (1.0 - (embedding <=> CAST(:hyde_vector AS vector))) AS cosine_sim,
              ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:hyde_vector AS vector)) AS rank_vec
       FROM document_chunks
       WHERE document_id = ANY(:active_doc_ids) AND user_id = :user_id
         AND embedding IS NOT NULL
       ORDER BY embedding <=> CAST(:hyde_vector AS vector)
       LIMIT 25
   ),
   fts_ranks AS (
       SELECT id, document_id, chunk_index, page_number, content, bounding_boxes,
              ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query)) AS fts_score,
              ROW_NUMBER() OVER (ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query)) DESC) AS rank_fts
       FROM document_chunks
       WHERE document_id = ANY(:active_doc_ids) AND user_id = :user_id
         AND content_tsv @@ plainto_tsquery('english', :fts_query)
       ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('english', :fts_query)) DESC
       LIMIT 25
   ),
   combined AS (
       SELECT COALESCE(v.id, f.id) AS chunk_id,
              COALESCE(v.cosine_sim, 0.0) AS max_cosine_sim,
              (COALESCE(1.0 / (60.0 + v.rank_vec), 0.0) + COALESCE(1.0 / (60.0 + f.rank_fts), 0.0)) AS rrf_score
       FROM vector_ranks v
       FULL OUTER JOIN fts_ranks f ON v.id = f.id
   )
   SELECT c.id AS chunk_id, c.document_id, c.chunk_index, c.page_number,
          c.content AS text_content, c.bounding_boxes,
          d.title AS document_title, d.filename,
          cb.max_cosine_sim, cb.rrf_score
   FROM combined cb
   JOIN document_chunks c ON cb.chunk_id = c.id
   JOIN documents d ON c.document_id = d.id
   ORDER BY cb.rrf_score DESC
   LIMIT :limit;
   ```
2. Triển khai logic CRAG:
   - Nếu $\tau \ge 0.35 \rightarrow$ Giữ nguyên Top candidates (`CORRECT`).
   - Nếu $0.20 \le \tau < 0.35 \rightarrow$ Gọi `_fetch_adjacent_chunks` lấy $[i-1, i+1]$, khử trùng lặp và áp trần `MAX_EVIDENCE_TOKENS = 3500` (`AMBIGUOUS_EXPANDED`).
   - Nếu $\tau < 0.20 \rightarrow$ Bật `abstain = True` (`ACTIVE_ABSTENTION`).

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/unit/test_crag_and_window_expansion.py -v`  
Expected: PASS

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/unit/test_crag_and_window_expansion.py
git commit -m "feat(rag): wire hnsw vector in rrf cte and implement crag multiline window expansion"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Frontend Reasoning Thinking UI, CacheStorage & Refined Bounding Box TDD

**Files:**
- Create: `apps/web/src/features/reader/components/ReasoningThinkingAccordion.tsx`
- Test: `apps/web/src/features/reader/__tests__/ReasoningThinkingAccordion.test.tsx`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx`
- Modify: `apps/web/src/features/reader/components/BboxHighlightLayer.tsx`

**Interfaces:**
- Consumes: SSE events stream (phân biệt reasoning delta và answer delta)
- Produces: `ReasoningThinkingAccordion` component gập gọn tư duy `✓ Thinking Finished`, `PdfCanvasViewer` với `window.caches` 0ms load, và viền BBox nét đứt vàng ánh kim.

- [x] **Step 1: Write failing frontend test for `ReasoningThinkingAccordion`**

```tsx
// apps/web/src/features/reader/__tests__/ReasoningThinkingAccordion.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ReasoningThinkingAccordion } from "../ReasoningThinkingAccordion";

describe("ReasoningThinkingAccordion Component", () => {
  it("renders thinking loading state when isStreaming is true", () => {
    render(<ReasoningThinkingAccordion thoughtContent="Đang phân tích..." isStreaming={true} />);
    expect(screen.getByText(/Thinking/i)).toBeInTheDocument();
  });

  it("renders collapsible finished state and expands on click", () => {
    render(<ReasoningThinkingAccordion thoughtContent="Bắt đầu suy luận công thức..." isStreaming={false} />);
    const trigger = screen.getByText(/Thinking Finished/i);
    expect(trigger).toBeInTheDocument();
    fireEvent.click(trigger);
    expect(screen.getByText(/Bắt đầu suy luận công thức.../i)).toBeVisible();
  });
});
```

- [x] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/ReasoningThinkingAccordion.test.tsx`  
Expected: FAIL with component not found.

- [x] **Step 3: Implement `ReasoningThinkingAccordion.tsx`, CacheStorage & BBox style**

1. Tạo `ReasoningThinkingAccordion.tsx` với CSS shimmer animation và Accordion thu gọn.
2. Thêm logic `window.caches.open("verischolar-pdfs-v1")` trong `PdfCanvasViewer.tsx` để lưu nhị phân PDF và tải tức thì $0$ms.
3. Cập nhật `BboxHighlightLayer.tsx` sang style viền nét đứt vàng ánh kim (`border: 2px dashed #f59e0b; background: rgba(245, 158, 11, 0.12); border-radius: 6px`).

- [x] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/ReasoningThinkingAccordion.test.tsx`  
Expected: PASS (2/2 tests).

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/web/src/features/reader/
git commit -m "feat(ui): add reasoning thinking accordion, pdf browser cache, and refined bbox styling"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: End-to-End TDD Grounded Chat Verification (The "Ragas AR Formula" Benchmark)

**Files:**
- Modify: `apps/api/tests/test_session_hybrid_rag_chat.py`
- Test: `apps/api/tests/test_session_hybrid_rag_chat.py`

**Interfaces:**
- Consumes: Toàn bộ pipeline từ Task 1 đến Task 5
- Produces: Xác nhận end-to-end phiên đọc sâu trả về công thức $AR$ trên Trang 3 kèm Bounding Box vàng dạng mảng `[x0, y0, x1, y1, page]`.

- [x] **Step 1: Write integration test for Vietnamese query on Ragas paper with concrete fixtures**

```python
# Trong apps/api/tests/test_session_hybrid_rag_chat.py
@pytest.fixture
async def setup_ragas_document(db_session, test_user):
    doc_id = uuid4()
    session_id = uuid4()
    # Chèn DocumentModel Ragas và 2 chunks công thức AR Trang 3
    doc = DocumentModel(id=doc_id, user_id=test_user.id, title="Ragas Paper", filename="ragas.pdf", status="ready")
    c19 = DocumentChunkModel(
        id=uuid4(), document_id=doc_id, user_id=test_user.id, chunk_index=19, page_number=3,
        content="Answer Relevance (AR) is formulated as: AR = (1/n) * sum(sim(q, q_i))",
        embedding=[0.05] * 1536,
        bounding_boxes=[[120.0, 450.0, 530.0, 535.0, 3]]
    )
    db_session.add_all([doc, c19])
    await db_session.commit()
    return session_id, doc_id

@pytest.mark.asyncio
async def test_ask_ragas_formula_ar_retrieves_page_3_with_bounding_box(db_session, test_user, setup_ragas_document):
    session_id, doc_id = setup_ragas_document
    chat_service = SessionChatService(db=db_session)
    
    chunks, citations, abstain = await chat_service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=test_user.id,
        question="Công thức Answer Relevance (AR) trong paper là gì?",
        target_doc_ids=[doc_id],
    )
    assert not abstain
    assert any(c["page_number"] == 3 for c in citations)
    assert any(c["chunk_index"] == 19 for c in chunks)
    # Kiểm tra Bounding Box dạng mảng [x0, y0, x1, y1, page]
    bbox = citations[0]["bounding_boxes"][0]
    assert len(bbox) == 5
    assert 0 <= bbox[0] <= 1000 and 0 <= bbox[1] <= 1000
```

- [x] **Step 2: Run test to verify it fails if pipeline is broken**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py -k test_ask_ragas_formula_ar -v`  
Expected: PASS (nếu Task 1-4 hoàn tất chuẩn xác) hoặc FAIL chỉ rõ điểm nghẽn.

- [x] **Step 3: Refactor & tune prompt guardrail in `session_chat_service.py`**

Đảm bảo System Prompt yêu cầu LLM trích xuất công thức dạng LaTeX KaTeX `$$AR = ...$$` và gắn thẻ neo ngữ nghĩa `[cite:chunk_id:page:concept_name]`.

- [x] **Step 4: Run full session tests**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py -v`  
Expected: PASS (100% test cases).

- [x] **Step 5: Commit and Sync VPS**

```bash
git add apps/api/tests/test_session_hybrid_rag_chat.py apps/api/src/api/services/session_chat_service.py
git commit -m "test(rag): add end-to-end verification for ragas ar formula grounding"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 7: Verification Gates, Production Backfill Execution & VPS Deployment

**Files:**
- Execute: `scripts/backfill_chunk_embeddings.py`
- Execute: 4 verification gates
- Execute: `scripts/deploy_to_vps.sh`

**Interfaces:**
- Consumes: CSDL PostgreSQL local và remote VPS
- Produces: 100% chunks trên hệ thống có vector embedding 1536 chiều, build production xanh hoàn toàn.

- [x] **Step 1: Run 4 Verification Gates locally**

```bash
uv run ruff check . && uv run ruff format --check .  # Gate 1: Lint & Format
uv run pytest                                        # Gate 2: Toàn bộ Backend Tests
npm --prefix apps/web run test                       # Gate 3: Frontend Unit Tests
npm --prefix apps/web run build                      # Gate 4: Production Web Build
```
Expected: 100% exit code 0.

- [x] **Step 2: Run backfill script on local database**

```bash
uv run python scripts/backfill_chunk_embeddings.py
```
Expected: Cập nhật thành công 100% chunks có `embedding IS NULL` thành vector 1536-dim.

- [x] **Step 3: Deploy to VPS and execute remote backfill**

```bash
bash scripts/deploy_to_vps.sh --fast
ssh -i /home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem VeriScholar@48.193.46.15 \
  "docker exec -i verischolar-api-dev uv run python scripts/backfill_chunk_embeddings.py"
```
Expected: Toàn bộ 90 chunks của bài báo Ragas trên VPS có vector đầy đủ; kiểm tra `SELECT count(*) FROM document_chunks WHERE embedding IS NULL;` trả về `0`.

- [x] **Step 4: Final commit of operational logs**

```bash
git add docs/
git commit -m "docs: finalize production advanced rag implementation and verification logs"
bash scripts/deploy_to_vps.sh --fast
```

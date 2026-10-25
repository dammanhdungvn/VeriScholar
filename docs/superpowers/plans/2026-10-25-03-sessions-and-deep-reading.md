# Deep Reading Sessions, Multi-Tab Workspace (1–5 Docs) & Grounded Hybrid RAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa không gian Phiên Đọc Sâu đa bài báo (tối đa 5 tab đồng thời), truy vấn Hybrid RAG trực tiếp trên PostgreSQL (`pgvector` Cosine + `tsvector` GIN qua RRF $k=60$), luồng streaming SSE có huy hiệu bảo chứng Khung viền vàng (`Bounding Box`) và Sổ tay Ghi chú Học thuật đóng băng chứng cứ.

**Architecture:** Áp dụng Kiến trúc Lục giác (Hexagonal Isolation): Bộ phân tích thẻ trích dẫn `[[cite:id]]` và quy tắc giới hạn 5 tab nằm trong `packages/core`; tầng dịch vụ `SessionChatService` trong `apps/api` thực thi SQL Hybrid RRF và phát luồng SSE không bộ đệm (`citation`, `token`, `bridge_hint`, `done`, `error`); tầng giao diện `apps/web` đồng bộ hai chiều giữa `CitationBadge`, `PdfCanvasViewer` (`BboxHighlightLayer`), `AbstractCardViewer` và `NotesPanelContainer`.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+ (`pgvector` + `tsvector`), React 19, TypeScript, Tailwind CSS, Zustand, `@microsoft/fetch-event-source`, KaTeX.

**Spec:** [`docs/specs/03-sessions-and-deep-reading-spec.md`](../../specs/03-sessions-and-deep-reading-spec.md) & [`docs/PRD/03-sessions-and-deep-reading-crud.md`](../../PRD/03-sessions-and-deep-reading-crud.md).

---

## Global Constraints

- 100% mã nguồn trong `packages/core/` chỉ dùng Python Standard Library và `pydantic`, cấm tuyệt đối import `fastapi`, `sqlalchemy`, `redis`, `fitz`.
- Mọi truy vấn trên `research_sessions`, `session_documents`, `session_turns`, `document_chunks`, `research_notes` bắt buộc lọc theo `WHERE user_id = :current_user_id`.
- Mỗi phiên đọc (`session_documents`) chỉ cho phép tối đa **5 bài báo** mở đồng thời; vượt quá phải trả về `HTTP 409 CONFLICT` với mã `MAX_SESSION_DOCUMENTS_REACHED`.
- Khi đóng một tab bài báo (`DELETE /api/v1/sessions/{id}/documents/{doc_id}`), chỉ xóa bản ghi liên kết trong `session_documents`, tuyệt đối không xóa `DocumentModel` gốc.
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối (`./...`, `../...`, `../../...`).
- Bốn Cổng Xác Minh Bắt Buộc (`uv run ruff check .`, `uv run pytest`, `npm --prefix apps/web run test`, `npm --prefix apps/web run build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Active Tab Reassignment When Closing Active Document:** Khi người dùng đóng chính tab bài báo đang hiển thị (`document_id == session.active_document_id`), hệ thống phải tự động gán `active_document_id` sang bài báo liền kề còn lại trong phiên (hoặc `None` nếu phiên trống) thay vì để lại UUID mồ côi.
2. **Zero-Hallucination on Out-of-Scope Empirical Queries:** Khi truy vấn Hybrid RAG không tìm thấy đoạn trích nào đạt ngưỡng liên quan hoặc người dùng hỏi số liệu không có trong bài, luồng SSE phải trả về phản hồi từ chối suy đoán trung thực, tuyệt đối không phát sự kiện `citation` giả.
3. **Abstract-Only & Parsing Document Guardrail:** Khi bài báo trong phiên có `status == 'abstract_only'` hoặc `status == 'parsing'`, `SessionChatService` chỉ nạp phần Tóm tắt vào prompt và chèn cảnh báo rõ ràng để mô hình không bịa đặt công thức thân bài.
4. **Reset Chat Preserves Session & Notes:** Khi gọi `DELETE /api/v1/sessions/{id}/messages`, chỉ xóa các bản ghi trong `session_turns`; danh sách tab `session_documents`, `viewport_state` và các ghi chú trong `research_notes` phải giữ nguyên 100%.
5. **Detached Note Evidence Preservation:** Khi bài báo gốc bị xóa khỏi kho tài liệu, các ghi chú trong `research_notes` thuộc phiên đọc vẫn hiển thị đầy đủ `selected_text`, `page_number` và `frozen_snapshot` với cờ `is_source_detached = True`.

---

## Implementation Tasks

### Task 1: Core Domain Session Tab Guard & Citation Tag Parser (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/citation_parser.py`
- Modify: `packages/core/src/core/domain/entities/session.py`
- Test: `packages/core/tests/test_session_citation_core.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, ` dataclasses`, `uuid.UUID`), `pydantic.BaseModel`.
- Produces:
  - `MAX_SESSION_DOCUMENTS = 5`
  - `validate_session_tab_capacity(current_doc_ids: list[UUID], new_doc_id: UUID) -> None` (raises `SessionTabLimitExceededError` hoặc `DocumentAlreadyInSessionError`)
  - `extract_citation_markers(markdown_text: str) -> list[int]` (bóc tách toàn bộ `[[cite:N]]` theo thứ tự xuất hiện duy nhất).

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_session_citation_core.py`:
```python
import pytest
from uuid import uuid4
from core.services.citation_parser import (
    MAX_SESSION_DOCUMENTS,
    SessionTabLimitExceededError,
    DocumentAlreadyInSessionError,
    validate_session_tab_capacity,
    extract_citation_markers,
)


def test_validate_session_tab_capacity_enforces_max_5():
    existing = [uuid4() for _ in range(MAX_SESSION_DOCUMENTS)]
    with pytest.raises(SessionTabLimitExceededError) as exc_info:
        validate_session_tab_capacity(existing, uuid4())
    assert exc_info.value.code == "MAX_SESSION_DOCUMENTS_REACHED"


def test_validate_session_tab_capacity_detects_duplicate():
    doc_id = uuid4()
    with pytest.raises(DocumentAlreadyInSessionError) as exc_info:
        validate_session_tab_capacity([doc_id], doc_id)
    assert exc_info.value.code == "REFERENCE_ALREADY_IN_SESSION"


def test_extract_citation_markers_preserves_order_and_uniqueness():
    sample = "Kết quả BLEU đạt 28.4 [[cite:2]] vượt qua baseline [[cite:1]] và [[cite:2]]."
    assert extract_citation_markers(sample) == [2, 1]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_session_citation_core.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.citation_parser'`

- [ ] **Step 3: Implement `packages/core/src/core/services/citation_parser.py`**

Cài đặt hằng số `MAX_SESSION_DOCUMENTS = 5`, các lớp ngoại lệ miền nghiệp vụ `SessionTabLimitExceededError`, `DocumentAlreadyInSessionError`, hàm `validate_session_tab_capacity()` và hàm `extract_citation_markers()` sử dụng biểu thức chính quy `r"\[\[cite:(\d+)\]\]"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_session_citation_core.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/services/citation_parser.py packages/core/tests/test_session_citation_core.py
git commit -m "feat(core): add session 5-tab capacity validator and citation marker parser"
```

---

### Task 2: Session Tab Management & Viewport Persistence Endpoints (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/v1/endpoints/sessions.py`
- Modify: `apps/api/src/api/schemas/session.py`
- Test: `apps/api/tests/test_session_tabs_and_viewport.py`

**Interfaces:**
- Consumes: `validate_session_tab_capacity` từ `core.services.citation_parser`, `ResearchSessionModel`, `SessionDocumentModel` từ `api.db.models.session`.
- Produces:
  - `POST /api/v1/sessions/{session_id}/documents` (kiểm tra giới hạn 5 bài, trả về `409 MAX_SESSION_DOCUMENTS_REACHED` nếu vượt).
  - `DELETE /api/v1/sessions/{session_id}/documents/{document_id}` (xóa liên kết tab, tự động cập nhật `active_document_id` nếu tab đang mở bị đóng, trả về `204 No Content`).
  - `PATCH /api/v1/sessions/{session_id}/viewport` (lưu `active_document_id`, `page`, `zoom_ratio`, `scroll_top`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_session_tabs_and_viewport.py`:
```python
import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_session_tab_limit_and_active_reassignment(async_client, auth_headers, db_session, test_user):
    res_sess = await async_client.post("/api/v1/sessions", headers=auth_headers, json={"title": "Multi-Tab Test"})
    assert res_sess.status_code == 201
    session_id = res_sess.json()["data"]["id"]
    doc_ids = []
    for idx in range(5):
        pdf_bytes = f"%PDF-1.4 sample paper {idx} ".encode() + (b"word " * 100)
        res_doc = await async_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": (f"paper_{idx}.pdf", pdf_bytes, "application/pdf")},
        )
        doc_id = res_doc.json()["data"]["id"]
        doc_ids.append(doc_id)
        res_add = await async_client.post(
            f"/api/v1/sessions/{session_id}/documents",
            headers=auth_headers,
            json={"document_id": doc_id},
        )
        assert res_add.status_code in (200, 201)

    # Adding 6th document must return 409 MAX_SESSION_DOCUMENTS_REACHED
    extra_pdf = b"%PDF-1.4 extra paper 6 " + (b"word " * 100)
    res_extra = await async_client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("paper_6.pdf", extra_pdf, "application/pdf")},
    )
    extra_id = res_extra.json()["data"]["id"]
    res_conflict = await async_client.post(
        f"/api/v1/sessions/{session_id}/documents",
        headers=auth_headers,
        json={"document_id": extra_id},
    )
    assert res_conflict.status_code == 409
    assert res_conflict.json()["error"]["code"] == "MAX_SESSION_DOCUMENTS_REACHED"

    # Closing active tab reassigns active_document_id to remaining tab
    res_close = await async_client.delete(
        f"/api/v1/sessions/{session_id}/documents/{doc_ids[0]}",
        headers=auth_headers,
    )
    assert res_close.status_code == 204
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_session_tabs_and_viewport.py -v`
Expected: FAIL (thiếu route `DELETE /api/v1/sessions/{id}/documents/{doc_id}` hoặc `PATCH /api/v1/sessions/{id}/viewport`).

- [ ] **Step 3: Implement tab close, 5-tab guard, and viewport endpoints in `apps/api/src/api/v1/endpoints/sessions.py`**

Cập nhật `sessions.py` và `schemas/session.py` (`ViewportStateUpdateSchema`), đảm bảo mọi truy vấn lọc `user_id == current_user.id` và trả đúng mã lỗi trong Ma trận Mã lỗi Chuẩn hóa của `SPEC-03`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_session_tabs_and_viewport.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/v1/endpoints/sessions.py apps/api/src/api/schemas/session.py apps/api/tests/test_session_tabs_and_viewport.py
git commit -m "feat(api): enforce 5-tab session limit, active tab reassignment, and viewport persistence"
```

---

### Task 3: PostgreSQL Hybrid RAG (Vector + FTS RRF k=60) & Unbuffered SSE Chat (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py`
- Modify: `apps/api/src/api/v1/endpoints/sessions.py`
- Test: `apps/api/tests/test_session_hybrid_rag_chat.py`

**Interfaces:**
- Consumes: `DocumentChunkModel` (`embedding`, `content_tsv`, `text_content`, `bbox_json`), `SessionTurnModel` (`trace_id`), `extract_citation_markers`.
- Produces:
  - `SessionChatService.retrieve_hybrid_chunks(session_id: UUID, user_id: UUID, query_text: str, query_embedding: list[float], limit: int = 5)`
  - `POST /api/v1/sessions/{session_id}/messages` (SSE stream: `citation` $\rightarrow$ `token` $\rightarrow$ `bridge_hint` $\rightarrow$ `done`)
  - `DELETE /api/v1/sessions/{session_id}/messages` (`204 No Content`, chỉ xóa `session_turns`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_session_hybrid_rag_chat.py` kiểm tra:
1. Kết hợp điểm RRF $k=60$ giữa `embedding <=> :query_vector` và `ts_rank_cd(content_tsv, plainto_tsquery('simple', :query))`.
2. Hàng rào chống ảo giác khi tài liệu ở trạng thái `abstract_only` hoặc câu hỏi không có dẫn chứng.
3. `DELETE /api/v1/sessions/{id}/messages` xóa sạch `session_turns` nhưng bảo toàn `research_sessions` và `research_notes`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py -v`
Expected: FAIL

- [ ] **Step 3: Implement PostgreSQL Hybrid RRF & SSE Event Sequencer in `session_chat_service.py`**

Triển khai câu lệnh CTE `vector_ranks` + `fts_ranks` `FULL OUTER JOIN` với công thức RRF `1.0 / (60 + rank_vec) + 1.0 / (60 + rank_fts)`, kèm guardrail cho `status == 'abstract_only'` và endpoint `DELETE /api/v1/sessions/{id}/messages`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_session_hybrid_rag_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/src/api/v1/endpoints/sessions.py apps/api/tests/test_session_hybrid_rag_chat.py
git commit -m "feat(api): implement PostgreSQL hybrid RRF search and grounded SSE chat stream"
```

---

### Task 4: Frontend Multi-Tab Reader, Golden Bounding Box Highlight & Abstract Card Viewer (`apps/web`)

**Files:**
- Create: `apps/web/src/features/reader/components/AbstractCardViewer.tsx`
- Modify: `apps/web/src/features/reader/components/DocumentTabBar.tsx`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx`
- Modify: `apps/web/src/features/reader/components/ScholarSelectionMenu.tsx`
- Test: `apps/web/src/features/reader/__tests__/DeepReadingWorkspace.test.tsx`

**Interfaces:**
- Consumes: Sự kiện toàn cục `window.dispatchEvent(new CustomEvent("scholar:focus-bbox", { detail: { documentId, pageNumber, boundingBoxes } }))`.
- Produces:
  - `AbstractCardViewer` hiển thị tóm tắt và nút tải PDF cá nhân khi `document.status === 'abstract_only'`.
  - `DocumentTabBar` hiển thị tối đa 5 tab kèm hộp thoại **Tab Eviction Dialog** khi nhận mã lỗi `MAX_SESSION_DOCUMENTS_REACHED`.
  - `PdfCanvasViewer` tự động chuyển tab, cuộn tới `pageNumber` và kích hoạt khung viền vàng nhấp nháy trên `BboxHighlightLayer`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/reader/__tests__/DeepReadingWorkspace.test.tsx` kiểm tra:
1. Render `AbstractCardViewer` khi `status === 'abstract_only'`.
2. Bấm vào huy hiệu dẫn chứng phát sự kiện `scholar:focus-bbox` làm chuyển tab và vẽ khung viền vàng.
3. Hiển thị hộp thoại chọn đóng bớt tab khi mở bài thứ 6.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DeepReadingWorkspace`
Expected: FAIL

- [ ] **Step 3: Implement `AbstractCardViewer.tsx` and update `DocumentTabBar.tsx` & `PdfCanvasViewer.tsx`**

Cài đặt giao diện thẻ tóm tắt học thuật, hộp thoại chọn đóng tab khi đầy 5/5 bài, và kết nối sự kiện `scholar:focus-bbox` để cuộn trang + vẽ khung viền vàng.

- [ ] **Step 4: Run test and build to verify all 4 verification gates pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/
git commit -m "feat(web): add AbstractCardViewer, 5-tab eviction dialog, and golden bbox focus navigation"
```

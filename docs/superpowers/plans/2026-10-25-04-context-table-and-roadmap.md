# 3-Column Context Table, 2-Tier Fast Ingestion (< 500ms) & Socratic Learning Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Bảng Quản Lý Ngữ Cảnh 3 Cột (`SmartReferenceDrawer`), cơ chế Nạp 2 Tầng tức thì dưới 500ms (`POST /api/v1/sessions/{id}/references:ingest`) và Động cơ Gợi ý Lộ trình Học tuần tự Socratic ($A \rightarrow B \rightarrow C \rightarrow D$ qua sự kiện SSE `bridge_hint` và `BridgeHintCard`).

**Architecture:** Tuân thủ Kiến trúc Lục giác: Bộ phân tích thẻ `<bridge_hint>` và trích xuất mã định danh chuẩn DOI/arXiv nằm trong `packages/core/src/core/services/socratic_roadmap.py`; tầng API trong `apps/api` cung cấp endpoint truy xuất danh mục tham khảo kèm cờ `is_in_session` và endpoint nạp nhanh 2 tầng (Tầng 1 ghi DB mở Tab trong `< 500ms`, Tầng 2 chạy `BackgroundTasks` tải PDF và cắt chunks); tầng giao diện `apps/web` hiển thị ngăn trượt 3 cột và thẻ lộ trình học màu vàng hổ phách.

**Tech Stack:** Python 3.12, FastAPI (`BackgroundTasks`), SQLAlchemy 2.0 Async, PostgreSQL 16+, React 19, TypeScript, Tailwind CSS, Zustand.

**Spec:** [`docs/specs/04-context-table-and-roadmap-spec.md`](../../specs/04-context-table-and-roadmap-spec.md) & [`docs/PRD/04-context-table-and-roadmap.md`](../../PRD/04-context-table-and-roadmap.md).

---

## Global Constraints

- `packages/core/src/core/services/socratic_roadmap.py` chỉ sử dụng Python Standard Library (`re`, `xml.etree.ElementTree`, `dataclasses`) và `pydantic`.
- Thao tác nạp bài tham khảo Tầng 1 (`POST /api/v1/sessions/{id}/references:ingest`) bắt buộc phản hồi HTTP `201 Created` trong dưới **500ms**; việc tải PDF và sinh vector embedding bắt buộc chạy bất đồng bộ ở Tầng 2.
- Tuân thủ nghiêm ngặt giới hạn tối đa **5 bài báo / phiên đọc**: nếu phiên đã đủ 5 bài, trả về `HTTP 409 CONFLICT` với mã `MAX_SESSION_DOCUMENTS_REACHED`.
- Nếu bài tham khảo bị khóa thu phí hoặc lỗi tải PDF ở Tầng 2, hệ thống tự động giữ trạng thái `status = 'abstract_only'` (`TIER2_PAYWALL_ABSTRACT_ONLY`) để học giả vẫn hỏi đáp được trên bản Tóm tắt mà không làm gián đoạn phiên đọc.
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối.
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Malformed or Missing Reference Identifiers (Books / Legacy Citations):** Khi một mục tài liệu tham khảo là sách chuyên khảo hoặc không có DOI/arXiv ID, bộ regex không được văng ngoại lệ mà giữ nguyên `raw_text`, đặt `access_status = 'abstract_only'` và tạo link tra cứu tiêu đề an toàn.
2. **Tier-2 Background Task DB Session Isolation:** Tác vụ nền Tầng 2 tải PDF và lưu chunks bắt buộc phải mở phiên giao dịch `AsyncSessionLocal()` độc lập, tuyệt đối không tái sử dụng `db: AsyncSession` của request HTTP đã đóng.
3. **Bridge Hint XML Tag Stripping in Chat Stream:** Khi LLM sinh thẻ `<bridge_hint ref_index="3" concept="..." reason="..." />` ở cuối câu trả lời, bộ phát SSE phải bóc tách thẻ này để bắn sự kiện `event: bridge_hint` riêng biệt và **xóa bỏ thẻ XML thô** khỏi văn bản hiển thị cho người dùng.
4. **Already-In-Session Reference Guard:** Nếu bài báo tham khảo `[k]` đã được mở sẵn trên thanh Tab của phiên đọc hiện tại, hệ thống không phát nút nạp trùng lặp mà trả về `is_in_session = True` (hoặc `409 REFERENCE_ALREADY_IN_SESSION` nếu gọi API trực tiếp).
5. **Single Most-Foundational Bridge Hint Per Turn:** Nếu câu trả lời chạm tới nhiều tài liệu tham khảo, chỉ trích xuất tối đa 1 thẻ `bridge_hint` cốt lõi nhất mỗi lượt trả lời để tránh làm rối giao diện học tập của học giả.

---

## Implementation Tasks

### Task 1: Socratic Bridge Hint Parser & DOI/arXiv Identifier Extractor (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/socratic_roadmap.py`
- Test: `packages/core/tests/test_socratic_roadmap.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `dataclasses`).
- Produces:
  - `BridgeHintPayload(ref_index: int, concept_name: str, reason: str)`
  - `extract_and_strip_bridge_hint(text: str) -> tuple[str, BridgeHintPayload | None]`
  - `extract_scholarly_identifiers(raw_citation: str) -> dict[str, str | None]` (trả về `{"doi": ..., "arxiv_id": ...}`).

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_socratic_roadmap.py`:
```python
from core.services.socratic_roadmap import (
    extract_and_strip_bridge_hint,
    extract_scholarly_identifiers,
)


def test_extract_and_strip_bridge_hint_tag():
    raw_output = (
        "Cơ chế này dựa trên tích vô hướng có tỷ lệ.\n"
        '<bridge_hint ref_index="3" concept="Scaled Dot-Product Attention" '
        'reason="Bài [3] trình bày chứng minh gốc về hệ số 1/sqrt(d_k)." />'
    )
    cleaned_text, hint = extract_and_strip_bridge_hint(raw_output)
    assert "<bridge_hint" not in cleaned_text
    assert hint is not None
    assert hint.ref_index == 3
    assert hint.concept_name == "Scaled Dot-Product Attention"


def test_extract_scholarly_identifiers_handles_doi_and_arxiv():
    cite = "Vaswani et al. (2017). Attention is all you need. arXiv:1706.03762, doi:10.48550/arXiv.1706.03762."
    ids = extract_scholarly_identifiers(cite)
    assert ids["arxiv_id"] == "1706.03762"
    assert ids["doi"] == "10.48550/arXiv.1706.03762"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_socratic_roadmap.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.socratic_roadmap'`

- [ ] **Step 3: Implement `packages/core/src/core/services/socratic_roadmap.py`**

Cài đặt dataclass `BridgeHintPayload`, hàm `extract_and_strip_bridge_hint()` và hàm `extract_scholarly_identifiers()` thuần Python Standard Library.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_socratic_roadmap.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/services/socratic_roadmap.py packages/core/tests/test_socratic_roadmap.py
git commit -m "feat(core): add Socratic bridge_hint tag parser and scholarly DOI/arXiv extractor"
```

---

### Task 2: References List API & 2-Tier Fast Session Ingestion Endpoint (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/v1/endpoints/documents.py`
- Modify: `apps/api/src/api/v1/endpoints/sessions.py`
- Modify: `apps/api/src/api/services/session_chat_service.py`
- Test: `apps/api/tests/test_references_and_2tier_ingest.py`

**Interfaces:**
- Consumes: `ReferenceItemModel`, `DocumentModel`, `SessionDocumentModel`, `extract_and_strip_bridge_hint`, `validate_session_tab_capacity`.
- Produces:
  - `GET /api/v1/documents/{document_id}/references` (trả về danh sách `reference_items` kèm cờ `is_in_session` khi truyền query `session_id`).
  - `POST /api/v1/sessions/{session_id}/references:ingest` (Tầng 1 tạo/liên kết `DocumentModel` vào `session_documents` trong `< 500ms`; Tầng 2 kích hoạt `BackgroundTasks` tải PDF với session DB độc lập).
  - Phát sự kiện SSE `event: bridge_hint` trong `SessionChatService` khi phát hiện thẻ gợi ý lộ trình học.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_references_and_2tier_ingest.py` kiểm tra:
1. `GET /api/v1/documents/{id}/references` trả về đúng trạng thái `is_in_session`.
2. `POST /api/v1/sessions/{id}/references:ingest` trả về `201 Created` trong `< 500ms` và trả về `409 MAX_SESSION_DOCUMENTS_REACHED` nếu phiên đã mở đủ 5 bài.
3. Khi bài tham khảo thuộc diện thu phí (`paywalled`), tài liệu được khởi tạo với `status = 'abstract_only'`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_references_and_2tier_ingest.py -v`
Expected: FAIL

- [ ] **Step 3: Implement references list, 2-tier `:ingest` endpoint, and SSE `bridge_hint` emission**

Cài đặt `GET /api/v1/documents/{document_id}/references` trong `documents.py`, `POST /api/v1/sessions/{session_id}/references:ingest` trong `sessions.py`, và tích hợp `extract_and_strip_bridge_hint` vào `session_chat_service.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_references_and_2tier_ingest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/v1/endpoints/documents.py apps/api/src/api/v1/endpoints/sessions.py apps/api/src/api/services/session_chat_service.py apps/api/tests/test_references_and_2tier_ingest.py
git commit -m "feat(api): add 3-column references endpoint, 2-tier fast ingestion, and SSE bridge_hint event"
```

---

### Task 3: Frontend 3-Column Context Table (`SmartReferenceDrawer`) & `BridgeHintCard` (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/reader/components/SmartReferenceDrawer.tsx`
- Create: `apps/web/src/features/reader/components/BridgeHintCard.tsx`
- Test: `apps/web/src/features/reader/__tests__/ContextTableAndRoadmap.test.tsx`

**Interfaces:**
- Consumes: `GET /api/v1/documents/{id}/references`, `POST /api/v1/sessions/{id}/references:ingest`, `DELETE /api/v1/sessions/{id}/documents/{doc_id}`, SSE `bridge_hint` event payload.
- Produces:
  - `SmartReferenceDrawer` hiển thị đúng 3 cột chuẩn: Cột 1 (Số thứ tự, Tiêu đề, Tác giả, Năm, DOI/arXiv, Huy hiệu PDF mở/Tóm tắt), Cột 2 (Link xuất bản gốc), Cột 3 (Nút `[➕ Thêm vào phiên]` / `[🗑️ Gỡ khỏi phiên]`).
  - `BridgeHintCard` hiển thị lộ trình học tuần tự $A \rightarrow B \rightarrow C \rightarrow D$ với nút nạp nhanh 1-Click.

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/reader/__tests__/ContextTableAndRoadmap.test.tsx` kiểm tra:
1. Render đủ 3 cột trong `SmartReferenceDrawer` và lọc nhanh theo từ khóa tác giả/tiêu đề.
2. Bấm `[➕ Thêm vào phiên]` trên `SmartReferenceDrawer` hoặc `BridgeHintCard` gọi API `:ingest` và thêm Tab mới trên thanh đọc.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- ContextTableAndRoadmap`
Expected: FAIL

- [ ] **Step 3: Implement `BridgeHintCard.tsx` and upgrade `SmartReferenceDrawer.tsx`**

Xây dựng `BridgeHintCard.tsx` và nâng cấp `SmartReferenceDrawer.tsx` bám sát thiết kế 3 cột trong `SPEC-04`.

- [ ] **Step 4: Run all 4 verification gates to confirm 100% pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/
git commit -m "feat(web): implement 3-column SmartReferenceDrawer and Socratic BridgeHintCard"
```

# Favorite Library, Hierarchical Topic Folders & 4-Entity PostgreSQL GraphRAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Kho Bài Báo Yêu Thích (`/library`), Cây Thư Mục Đề Tài phân cấp (`folders`), Động cơ bóc tách Đồ Thị Tri Thức Học Thuật 4 Thực Thể thuần PostgreSQL 16+ `pgvector` với cơ chế Hợp Nhất Đỉnh Trùng Tên (Canonical Hub Merging) và Truy Vấn Tổng Hợp Đa Bài Báo (`POST /api/v1/library/graph-query`).

**Architecture:** Tuân thủ Kiến trúc Lục giác: Bộ chuẩn hóa tên định danh `canonical_name = lower(trim(name))` và xác thực 4 loại thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) + 4 loại quan hệ (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`) nằm trong `packages/core/src/core/services/graph_extractor.py`; tầng ứng dụng trong `apps/api` thực thi Upsert `ON CONFLICT (user_id, node_type, canonical_name) DO UPDATE` trên `graph_nodes`, quản lý dọn dẹp đỉnh mồ côi khi Unstar, và thực thi truy vấn 2 bước (HNSW Vector Anchor $\rightarrow$ 1-Hop Edge Expansion); tầng giao diện `apps/web` hiển thị cây thư mục, lưới bài báo đã Star và sơ đồ mini-graph `cytoscape`.

**Tech Stack:** Python 3.12, FastAPI (`BackgroundTasks`), SQLAlchemy 2.0 Async, PostgreSQL 16+ (`pgvector` HNSW), React 19, TypeScript, Tailwind CSS, Cytoscape.js.

**Spec:** [`docs/specs/05-favorite-library-and-graphrag-spec.md`](../../specs/05-favorite-library-and-graphrag-spec.md) & [`docs/PRD/05-favorite-library-and-graphrag.md`](../../PRD/05-favorite-library-and-graphrag.md).

---

## Global Constraints

- Tuyệt đối cấm sử dụng cơ sở dữ liệu đồ thị ngoài (như Neo4j). Toàn bộ đồ thị tri thức lưu trong 2 bảng PostgreSQL `graph_nodes` và `graph_edges`.
- Chỉ chấp nhận duy nhất 4 nhãn thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và 4 kiểu cạnh (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`).
- Áp dụng **Canonical Hub Merging** trong phạm vi từng học giả: `UNIQUE (user_id, node_type, canonical_name)` với `document_id NULL REFERENCES documents(id) ON DELETE SET NULL`.
- Khi xóa một thư mục đề tài (`DELETE /api/v1/folders/{id}`), các bài báo bên trong chỉ được gán `folder_id = NULL`, tuyệt đối không bị xóa khỏi kho tài liệu của học giả.
- Khi bỏ đánh dấu yêu thích (`Unstar`), xóa các cạnh `graph_edges` của bài báo đó và chỉ xóa các đỉnh `graph_nodes` không còn bất kỳ cạnh nào liên kết tới (bảo toàn các đỉnh Hub dùng chung với bài báo khác).
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối.
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Folder Hierarchy Cycle Prevention:** Khi người dùng di chuyển thư mục $A$ vào bên trong thư mục con/cháu của chính nó ($A \rightarrow B \rightarrow A$), API `PATCH /api/v1/folders/{id}` phải phát hiện vòng lặp phân cấp và từ chối với mã lỗi `400 FOLDER_CYCLE_DETECTED`.
2. **Divergent Empirical Metric Results Across Papers:** Khi Bài báo A và Bài báo B báo cáo 2 con số khác nhau cho cùng một phương pháp trên cùng một tập dữ liệu (ví dụ: `BLEU: 28.4 (Vaswani 2017, p.8)` vs `BLEU: 27.9 (Replication 2019, p.5)`), hệ thống phải lưu thành 2 thực thể `MetricResult` riêng biệt gắn kèm `evidence_chunk_id` và `page_number` của từng bài báo nguồn thay vì ghi đè làm mất số liệu đối chứng.
3. **Shared Canonical Hub Preservation on Unstar:** Khi Bài báo 1 và Bài báo 2 cùng liên kết tới đỉnh Hub `Method: "transformer"`, việc bỏ Star Bài báo 1 chỉ xóa cạnh của Bài báo 1; đỉnh `Method: "transformer"` và cạnh của Bài báo 2 phải còn nguyên vẹn 100%.
4. **Multi-Tenant Graph Isolation:** Truy vấn HNSW Vector Anchor trên `graph_nodes` và mở rộng cạnh 1-Hop trên `graph_edges` bắt buộc luôn có điều kiện `WHERE user_id = :current_user_id` để không bao giờ trộn lẫn tri thức giữa hai học giả.
5. **Theoretical Survey Paper Graceful Extraction:** Khi bài báo được Star là bài tổng quan lý thuyết thuần túy (không có bảng số liệu thực nghiệm), bộ trích xuất chỉ tạo đỉnh `Paper` và `Method` mà không văng lỗi thiếu `Dataset` hay `MetricResult`.

---

## Implementation Tasks

### Task 1: 4-Entity Schema Validator, Canonical Name Normalizer & Folder Cycle Guard (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/graph_extractor.py`
- Modify: `packages/core/src/core/domain/entities/folder.py`
- Test: `packages/core/tests/test_graph_domain_and_folders.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `dataclasses`, `typing.Literal`, `uuid.UUID`), `pydantic.BaseModel`.
- Produces:
  - `VALID_NODE_TYPES = ("Paper", "Method", "Dataset", "MetricResult")`
  - `VALID_EDGE_TYPES = ("PROPOSES", "EVALUATED_ON", "ACHIEVES", "CITES")`
  - `normalize_canonical_name(raw_name: str) -> str`
  - `ExtractedGraphPayload` (Pydantic model kiểm tra nghiêm ngặt schema 4 thực thể & 4 quan hệ)
  - `detect_folder_cycle(folder_id: UUID, new_parent_id: UUID | None, parent_map: dict[UUID, UUID | None]) -> bool`.

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_graph_domain_and_folders.py`:
```python
import pytest
from uuid import uuid4
from pydantic import ValidationError
from core.services.graph_extractor import (
    normalize_canonical_name,
    ExtractedGraphPayload,
    detect_folder_cycle,
)


def test_normalize_canonical_name_lowercases_and_collapses_spaces():
    assert normalize_canonical_name("  Transformer   Architecture \n") == "transformer architecture"


def test_extracted_graph_payload_rejects_invalid_entity_type():
    with pytest.raises(ValidationError):
        ExtractedGraphPayload.model_validate({
            "entities": [{"type": "Author", "name": "Vaswani"}],
            "relations": [],
        })


def test_detect_folder_cycle_catches_self_and_descendant_parent():
    a, b, c = uuid4(), uuid4(), uuid4()
    parent_map = {a: None, b: a, c: b}
    assert detect_folder_cycle(a, a, parent_map) is True
    assert detect_folder_cycle(a, c, parent_map) is True
    assert detect_folder_cycle(c, a, parent_map) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_graph_domain_and_folders.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.graph_extractor'`

- [ ] **Step 3: Implement `packages/core/src/core/services/graph_extractor.py`**

Cài đặt `normalize_canonical_name`, `ExtractedGraphPayload` và `detect_folder_cycle` thuần Python Standard Library + `pydantic`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_graph_domain_and_folders.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/services/graph_extractor.py packages/core/tests/test_graph_domain_and_folders.py
git commit -m "feat(core): add 4-entity graph schema validator, canonical normalizer, and folder cycle detector"
```

---

### Task 2: Canonical Hub Upsert, Unstar Orphan Pruning & 2-Step GraphRAG Traversal Service (`apps/api`)

**Files:**
- Create: `apps/api/src/api/services/graph_rag_service.py`
- Modify: `apps/api/src/api/v1/endpoints/documents.py`
- Create: `apps/api/src/api/v1/endpoints/library.py`
- Modify: `apps/api/src/api/v1/endpoints/folders.py`
- Test: `apps/api/tests/test_graph_rag_lifecycle_and_query.py`

**Interfaces:**
- Consumes: `GraphNodeModel`, `GraphEdgeModel`, `ExtractedGraphPayload`, `normalize_canonical_name`, `detect_folder_cycle`.
- Produces:
  - `GraphRAGService.ingest_paper_graph(db: AsyncSession, user_id: UUID, document_id: UUID, payload: ExtractedGraphPayload)` (Upsert `graph_nodes` theo `(user_id, node_type, canonical_name)`, tạo `graph_edges`).
  - `GraphRAGService.prune_document_graph(db: AsyncSession, user_id: UUID, document_id: UUID)` (Xóa cạnh thuộc `document_id`, xóa đỉnh mồ côi không còn cạnh nào nối tới, giữ nguyên đỉnh Hub dùng chung).
  - `POST /api/v1/library/graph-query` (HNSW Vector Anchor top-k $\rightarrow$ 1-Hop `graph_edges` expansion $\rightarrow$ câu trả lời tổng hợp kèm `subgraph {nodes, edges}`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_graph_rag_lifecycle_and_query.py` kiểm tra:
1. Nạp 2 bài báo cùng đề cập `Method: "Transformer"` $\rightarrow$ chỉ sinh 1 dòng `GraphNodeModel` cho `"transformer"` nhưng có 2 cạnh `PROPOSES` từ 2 bài báo.
2. Bỏ Star bài báo 1 (`prune_document_graph`) $\rightarrow$ xóa cạnh của bài báo 1, giữ nguyên đỉnh Hub `"transformer"` cho bài báo 2; khi bỏ Star nốt bài báo 2 $\rightarrow$ đỉnh mồ côi được dọn sạch.
3. `POST /api/v1/library/graph-query` trả về đúng `answer` và `subgraph` 1-hop chỉ trong phạm vi `user_id` hiện tại.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_rag_lifecycle_and_query.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `graph_rag_service.py`, `library.py`, and update `documents.py` & `folders.py`**

Cài đặt đầy đủ logic Upsert Canonical Hub, dọn dẹp đỉnh mồ côi khi Unstar, kiểm tra chống vòng lặp thư mục trong `folders.py`, và mount router `library.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_rag_lifecycle_and_query.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/graph_rag_service.py apps/api/src/api/v1/endpoints/library.py apps/api/src/api/v1/endpoints/documents.py apps/api/src/api/v1/endpoints/folders.py apps/api/tests/test_graph_rag_lifecycle_and_query.py
git commit -m "feat(api): implement PostgreSQL 4-entity GraphRAG service, canonical hub merging, and orphan pruning"
```

---

### Task 3: Frontend Favorite Library Workspace, Folders Tree & Interactive Cytoscape Subgraph (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Create: `apps/web/src/features/library/components/KnowledgeSubgraphViewer.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryAndGraphRAG.test.tsx`

**Interfaces:**
- Consumes: `GET /api/v1/folders/tree`, `POST /api/v1/documents/{id}:toggle-star`, `POST /api/v1/library/graph-query`.
- Produces:
  - `LibraryWorkspaceView` hiển thị cây thư mục đề tài bên trái, lưới bài báo đã Star ở giữa và hộp hỏi đáp tổng hợp GraphRAG ở trên.
  - `KnowledgeSubgraphViewer` trực quan hóa 4 loại thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) bằng màu sắc học thuật rõ ràng kèm bảng đối chiếu số liệu thực nghiệm có trích dẫn số trang.

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/library/__tests__/LibraryAndGraphRAG.test.tsx` kiểm tra hiển thị cây thư mục, thao tác Star/Unstar và hiển thị kết quả tra cứu `subgraph` từ `/api/v1/library/graph-query`.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- LibraryAndGraphRAG`
Expected: FAIL

- [ ] **Step 3: Implement `KnowledgeSubgraphViewer.tsx` and update `LibraryWorkspaceView.tsx`**

Xây dựng component hiển thị đồ thị 4 thực thể và nâng cấp không gian Kho Yêu Thích bám sát `SPEC-05`.

- [ ] **Step 4: Run all 4 verification gates to confirm 100% pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/library/
git commit -m "feat(web): add 4-entity KnowledgeSubgraphViewer and upgrade LibraryWorkspaceView"
```

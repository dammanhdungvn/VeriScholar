# Favorite Library, Hierarchical Topic Folders & Dual-Level PostgreSQL GraphRAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa Kho Bài Báo Yêu Thích (`/library`), Cây Thư Mục Đề Tài phân cấp (`folders`), Động cơ bóc tách Đồ Thị Tri Thức Học Thuật 4 Thực Thể thuần PostgreSQL 16+ `pgvector` với cơ chế Hợp Nhất Đỉnh Hub Ngữ Nghĩa (Semantic Disambiguation Cosine $\ge 0.90$), Động cơ Thư mục học Bibliometrics (Connected Papers Prior/Derivative Works), và Truy Vấn Kép Vi Mô & Vĩ Mô (Dual-Level Local & Global GraphRAG qua `POST /api/v1/library/graph:query`).

**Architecture:** Tuân thủ nghiêm ngặt Kiến trúc Lục giác (Hexagonal Isolation):
- `packages/core/`: Lõi miền nghiệp vụ thuần khiết Python Standard Library + `pydantic`. Chứa bộ chuẩn hóa `normalize_canonical_name()`, Pydantic validator 4 thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) & 4 quan hệ (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`), bộ phát hiện vòng lặp thư mục `detect_folder_cycle()`, và công thức thư mục học.
- `apps/api/`: Mô hình SQLAlchemy (`GraphNodeModel`, `GraphEdgeModel`, `FolderCommunitySummaryModel`), DDL với chỉ mục HNSW Cosine trên cột `embedding vector(1536)`, tác vụ nền nạp tăng dần LightRAG ($< 3$s) kết hợp cosine $\ge 0.90$ khử nhập nhằng, truy vấn 2 bước SQL CTE kết hợp Lexical Graph (`document_chunks.bounding_boxes`) và Domain Graph, định tuyến truy vấn kép `mode: "local" | "global" | "hybrid"`, và dọn dẹp đỉnh mồ côi an toàn khi Unstar.
- `apps/web/`: Cây thư mục đề tài bên trái, lưới bài báo đã Star ở giữa, hộp tra cứu kép GraphRAG ở trên và sơ đồ mạng tri thức tương tác `cytoscape` (kích thước đỉnh theo Degree Centrality, nhấp đúp cạnh mở trang PDF có Bounding Box viền vàng).

**Tech Stack:** Python 3.12, FastAPI (`BackgroundTasks`), SQLAlchemy 2.0 Async, PostgreSQL 16+ (`pgvector` HNSW), React 19, TypeScript, Tailwind CSS, Cytoscape.js.

**Spec:** [`docs/specs/05-favorite-library-and-graphrag-spec.md`](../../specs/05-favorite-library-and-graphrag-spec.md) & [`docs/PRD/05-favorite-library-and-graphrag.md`](../../PRD/05-favorite-library-and-graphrag.md).

---

## Global Constraints

- Tuyệt đối cấm sử dụng cơ sở dữ liệu đồ thị ngoài (như Neo4j). Toàn bộ đồ thị tri thức lưu trong các bảng PostgreSQL `graph_nodes`, `graph_edges`, và `folder_community_summaries`.
- Chỉ chấp nhận duy nhất 4 nhãn thực thể (`Paper`, `Method`, `Dataset`, `MetricResult`) và 4 kiểu cạnh (`PROPOSES`, `EVALUATED_ON`, `ACHIEVES`, `CITES`).
- Áp dụng **Semantic Entity Disambiguation Hubs** trong phạm vi từng học giả: Nếu Cosine $\ge 0.90$, gộp vào Hub có sẵn; nếu không, tạo đỉnh mới trong `graph_nodes`.
- Khi xóa một thư mục đề tài (`DELETE /api/v1/folders/{id}`), các bài báo bên trong chỉ được gán `folder_id = NULL`, tuyệt đối không bị xóa khỏi kho tài liệu của học giả.
- Khi bỏ đánh dấu yêu thích (`Unstar`), xóa các cạnh `graph_edges` của bài báo đó và chỉ xóa các đỉnh `graph_nodes` không còn bất kỳ cạnh nào liên kết tới (bảo toàn các đỉnh Hub dùng chung với bài báo khác).
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối.
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.
- Chạy `bash scripts/deploy_to_vps.sh --fast` sau mỗi lần git commit thành công.

---

## Review Focus

1. **Folder Hierarchy Cycle Prevention:** Khi người dùng di chuyển thư mục $A$ vào bên trong thư mục con/cháu của chính nó ($A \rightarrow B \rightarrow A$), API `PATCH /api/v1/folders/{id}` phải phát hiện vòng lặp phân cấp và từ chối với mã lỗi `400 CYCLIC_FOLDER_HIERARCHY`.
2. **Contextual Metric Tuple Binding Across Papers:** Khi hai bài báo báo cáo số liệu khác nhau cho cùng một phương pháp trên cùng tập dữ liệu (ví dụ: `BLEU: 28.4` trên test set vs `BLEU: 27.9` trên val set), hệ thống phải lưu thành 2 thực thể `MetricResult` riêng biệt gắn kèm bộ 6 tham số ngữ cảnh `(dataset, task, split, metric_name, value, page_number)` và `evidence_chunk_id` thay vì ghi đè.
3. **Shared Canonical Hub Preservation on Unstar:** Khi Bài báo 1 và Bài báo 2 cùng liên kết tới đỉnh Hub `Method: "transformer"`, việc bỏ Star Bài báo 1 chỉ xóa cạnh của Bài báo 1; đỉnh `Method: "transformer"` và cạnh của Bài báo 2 phải còn nguyên vẹn 100%.
4. **Multi-Tenant Scholar Isolation in Vector CTE:** Truy vấn HNSW Vector Anchor trên `graph_nodes` và mở rộng cạnh 1-Hop trên `graph_edges` bắt buộc luôn có điều kiện `WHERE user_id = :current_user_id AND embedding IS NOT NULL` để không bao giờ trộn lẫn tri thức giữa hai học giả.
5. **Bounding Box Traceability Invariant:** Cạnh thực nghiệm trong subgraph response bắt buộc mang theo `document_id`, `evidence_chunk_id` và `page_number` để nhấp đúp trên Cytoscape kích hoạt mở đúng trang PDF và hiển thị viền vàng Bounding Box.

---

## Implementation Tasks

### Task 1: 4-Entity Schema Validator, Canonical Normalizer & Folder Cycle Guard (`packages/core`)

**Files:**
- Create: `packages/core/src/core/services/graph_extractor.py`
- Test: `packages/core/tests/test_graph_domain_and_folders.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `dataclasses`, `typing.Literal`, `uuid.UUID`), `pydantic.BaseModel`.
- Produces:
  - `VALID_NODE_TYPES = ("Paper", "Method", "Dataset", "MetricResult")`
  - `VALID_EDGE_TYPES = ("PROPOSES", "EVALUATED_ON", "ACHIEVES", "CITES")`
  - `normalize_canonical_name(raw_name: str) -> str`
  - `ExtractedGraphPayload` (Pydantic model kiểm tra nghiêm ngặt schema 4 thực thể & 4 quan hệ với bộ 6 tham số `context_tuple`)
  - `detect_folder_cycle(folder_id: UUID, new_parent_id: UUID | None, parent_map: dict[UUID, UUID | None]) -> bool`.

- [x] **Step 1: Write the failing test**

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


def test_extracted_graph_payload_validates_strict_schema():
    payload = {
        "entities": [
            {"type": "Paper", "name": "Attention Is All You Need", "page_number": 1},
            {"type": "Method", "name": "Transformer", "page_number": 3},
            {
                "type": "MetricResult",
                "name": "BLEU: 28.4",
                "page_number": 8,
                "context_tuple": {
                    "dataset": "WMT-2014 En-De",
                    "task": "Translation",
                    "split": "test",
                    "metric_name": "BLEU",
                    "value": 28.4,
                    "unit": "points",
                },
            },
        ],
        "relations": [
            {"source_name": "Attention Is All You Need", "target_name": "Transformer", "type": "PROPOSES", "page_number": 3},
            {"source_name": "Transformer", "target_name": "BLEU: 28.4", "type": "ACHIEVES", "page_number": 8},
        ],
    }
    validated = ExtractedGraphPayload.model_validate(payload)
    assert len(validated.entities) == 3
    assert len(validated.relations) == 2


def test_extracted_graph_payload_rejects_invalid_entity_or_edge_type():
    with pytest.raises(ValidationError):
        ExtractedGraphPayload.model_validate({
            "entities": [{"type": "Author", "name": "Vaswani", "page_number": 1}],
            "relations": [],
        })


def test_detect_folder_cycle_catches_self_and_descendant_parent():
    a, b, c = uuid4(), uuid4(), uuid4()
    parent_map = {a: None, b: a, c: b}
    assert detect_folder_cycle(a, a, parent_map) is True
    assert detect_folder_cycle(a, c, parent_map) is True
    assert detect_folder_cycle(c, a, parent_map) is False
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_graph_domain_and_folders.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.services.graph_extractor'`

- [x] **Step 3: Implement `packages/core/src/core/services/graph_extractor.py`**

Cài đặt `normalize_canonical_name`, `ExtractedGraphPayload`, và `detect_folder_cycle` thuần Python Standard Library + `pydantic`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_graph_domain_and_folders.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add packages/core/src/core/services/graph_extractor.py packages/core/tests/test_graph_domain_and_folders.py
git commit -m "feat(core): add 4-entity graph schema validator, canonical normalizer, and folder cycle detector"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Database Schema & SQLAlchemy Models (`graph_nodes`, `graph_edges`, `folder_community_summaries`) (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/db/models/graph.py`
- Modify: `apps/api/src/api/db/session.py`
- Test: `apps/api/tests/test_graph_models.py`

**Interfaces:**
- Consumes: SQLAlchemy 2.0 Async, `pgvector.sqlalchemy.Vector`.
- Produces:
  - `GraphNodeModel`: `id`, `user_id`, `node_type`, `canonical_name`, `metadata_json`, `embedding: Vector(1536)`.
  - `GraphEdgeModel`: `id`, `user_id`, `document_id`, `source_node_id`, `target_node_id`, `edge_type`, `metadata_json`, `evidence_chunk_id`, `page_number`.
  - `FolderCommunitySummaryModel`: `id`, `user_id`, `folder_id`, `summary_text`, `key_findings`, `embedding: Vector(1536)`.

- [x] **Step 1: Write the failing test**

Cập nhật `apps/api/tests/test_graph_models.py` kiểm tra khởi tạo `GraphNodeModel`, `GraphEdgeModel` có `page_number` và `evidence_chunk_id`, cùng `FolderCommunitySummaryModel`.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_models.py -v`
Expected: FAIL

- [x] **Step 3: Implement models in `apps/api/src/api/db/models/graph.py` & DDL in `session.py`**

Cập nhật model và DDL `ensure_database_schema()`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_models.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/db/models/graph.py apps/api/src/api/db/session.py apps/api/tests/test_graph_models.py
git commit -m "feat(api): upgrade graph SQLAlchemy models with community summaries and evidence foreign keys"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Incremental Extraction & Semantic Entity Disambiguation Service (Cosine $\ge 0.90$) (`apps/api`)

**Files:**
- Create: `apps/api/src/api/services/graph_extraction_service.py`
- Test: `apps/api/tests/test_graph_extraction_service.py`

**Interfaces:**
- Consumes: `EmbeddingService`, `GraphNodeModel`, `GraphEdgeModel`, `ExtractedGraphPayload`.
- Produces:
  - `GraphExtractionService.extract_paper_entities(document_id: UUID, text: str) -> ExtractedGraphPayload`: Trích xuất 4 thực thể qua OpenAI Structured Outputs.
  - `GraphExtractionService.ingest_paper_graph(db: AsyncSession, user_id: UUID, document_id: UUID, payload: ExtractedGraphPayload)`: Nạp tăng dần LightRAG trong $< 3$s. Đối chiếu vector cosine với các đỉnh hiện có; nếu Cosine $\ge 0.90$, gộp vào Hub có sẵn; nếu không, tạo đỉnh mới và sinh vector 1536d.
  - `GraphExtractionService.prune_document_graph(db: AsyncSession, user_id: UUID, document_id: UUID)`: Xóa các cạnh của `document_id` và quét dọn đỉnh mồ côi (bảo toàn đỉnh Hub có bài khác tham chiếu).

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_graph_extraction_service.py` kiểm thử:
1. Gắn sao bài báo A có phương pháp "Transformer" $\rightarrow$ tạo Hub.
2. Gắn sao bài báo B có phương pháp "The Transformer architecture" (Cosine $\ge 0.90$) $\rightarrow$ tái sử dụng Hub bài báo A và thêm alias.
3. Bỏ sao bài báo A $\rightarrow$ Hub vẫn còn nguyên vì bài báo B đang dùng.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_graph_extraction_service.py -v`
Expected: FAIL

- [x] **Step 3: Implement `apps/api/src/api/services/graph_extraction_service.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_graph_extraction_service.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/services/graph_extraction_service.py apps/api/tests/test_graph_extraction_service.py
git commit -m "feat(api): implement incremental LightRAG extraction with cosine 0.90 semantic disambiguation"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Dual-Level Query Engine & Connected Papers Bibliometrics Service (`apps/api`)

**Files:**
- Create: `apps/api/src/api/services/graph_rag_service.py`
- Test: `apps/api/tests/test_graph_rag_query.py`
- Test: `apps/api/tests/test_graph_bibliometrics.py`

**Interfaces:**
- Consumes: PostgreSQL CTE, `GraphNodeModel`, `GraphEdgeModel`, `FolderCommunitySummaryModel`, `DocumentChunkModel`.
- Produces:
  - `GraphRAGService.query_graph(user_id: UUID, query: str, mode: Literal["local", "global", "hybrid"], folder_id: UUID | None, top_k: int)`:
    - `local`: Thực thi 2-step CTE (`anchor_nodes` qua HNSW Cosine $\rightarrow$ 1-Hop `connected_edges` $\rightarrow$ `document_chunks.bounding_boxes AS bbox`).
    - `global`: Tra cứu trên `folder_community_summaries` kết hợp Hubs.
    - `hybrid`: Kết hợp cả hai.
  - `GraphRAGService.compute_bibliometrics(user_id: UUID, folder_id: UUID | None)`:
    - Tính toán Ghép cặp Thư mục (Bibliographic Coupling) giữa các bài báo có chung $\ge 2$ tài liệu tham khảo.
    - Xác định **Tác phẩm Cội nguồn (Prior Works)** (In-Degree cao nhất) và **Tác phẩm Phái sinh (Derivative Works)** (Out-Degree cao nhất).

- [x] **Step 1: Write the failing tests**

Tạo `apps/api/tests/test_graph_rag_query.py` và `test_graph_bibliometrics.py`.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest apps/api/tests/test_graph_rag_query.py apps/api/tests/test_graph_bibliometrics.py -v`
Expected: FAIL

- [x] **Step 3: Implement `apps/api/src/api/services/graph_rag_service.py`**

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest apps/api/tests/test_graph_rag_query.py apps/api/tests/test_graph_bibliometrics.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/services/graph_rag_service.py apps/api/tests/test_graph_rag_query.py apps/api/tests/test_graph_bibliometrics.py
git commit -m "feat(api): implement dual-level GraphRAG CTE traversal and bibliographic coupling engine"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: REST API Endpoints & Nginx Route Sync (`apps/api`)

**Files:**
- Create: `apps/api/src/api/v1/endpoints/library.py`
- Modify: `apps/api/src/api/v1/endpoints/documents.py`
- Modify: `apps/api/src/api/v1/endpoints/folders.py`
- Modify: `apps/api/src/api/main.py`
- Test: `apps/api/tests/test_library_endpoints.py`

**Interfaces:**
- Endpoints:
  - `POST /api/v1/library/graph:query` (kèm route alias `/graph-query`)
  - `GET /api/v1/folders/{id}/bibliometrics`
  - `POST /api/v1/documents/{id}:toggle-star` (kích hoạt `FastAPI BackgroundTasks` gọi `GraphExtractionService`)
  - `PATCH /api/v1/folders/{id}` (chặn vòng lặp với `400 CYCLIC_FOLDER_HIERARCHY`)

- [x] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_library_endpoints.py`.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_library_endpoints.py -v`
Expected: FAIL

- [x] **Step 3: Implement endpoints and register in `apps/api/src/api/main.py`**

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_library_endpoints.py -v`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/api/src/api/v1/endpoints/library.py apps/api/src/api/v1/endpoints/documents.py apps/api/src/api/v1/endpoints/folders.py apps/api/src/api/main.py apps/api/tests/test_library_endpoints.py
git commit -m "feat(api): expose library graph-query, bibliometrics, and star-toggle endpoints"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: Frontend Favorite Library Workspace, Folders Tree & Interactive Cytoscape Subgraph (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Create: `apps/web/src/features/library/components/KnowledgeSubgraphViewer.tsx`
- Create: `apps/web/src/features/library/components/BibliometricsPriorWorksCard.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryAndGraphRAG.test.tsx`

**Interfaces:**
- Consumes: `POST /api/v1/library/graph:query`, `GET /api/v1/folders/{id}/bibliometrics`, `POST /api/v1/documents/{id}:toggle-star`.
- Produces:
  - `LibraryWorkspaceView`: Cây thư mục đề tài, lưới bài báo đã Star, và hộp hỏi đáp thông minh 3 chế độ (`local`, `global`, `hybrid`).
  - `KnowledgeSubgraphViewer`: Sơ đồ Cytoscape có kích thước đỉnh theo Degree Centrality, nhấp đúp cạnh mở trang PDF có Bounding Box viền vàng.
  - `BibliometricsPriorWorksCard`: Thẻ hiển thị các Tác phẩm Cội nguồn kinh điển và Tác phẩm Phái sinh.

- [x] **Step 1: Write the failing test**

Tạo `apps/web/src/features/library/__tests__/LibraryAndGraphRAG.test.tsx`.

- [x] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- LibraryAndGraphRAG`
Expected: FAIL

- [x] **Step 3: Implement components in `apps/web/src/features/library/`**

- [x] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- LibraryAndGraphRAG`
Expected: PASS

- [x] **Step 5: Commit & Gate verification**

```bash
git add apps/web/src/features/library/
git commit -m "feat(web): add interactive Cytoscape knowledge graph viewer and bibliometrics cards"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 7: End-to-End Verification, 4 Mandatory Verification Gates & Rollout

- [x] **Step 1: Run Gate 1 (Python Linter & Formatter)**
  Run: `uv run ruff check . && uv run ruff format --check .`
  Expected: exit code 0

- [x] **Step 2: Run Gate 2 (Backend & Architecture Boundary Tests)**
  Run: `uv run pytest`
  Expected: exit code 0 (146+ tests passed)

- [x] **Step 3: Run Gate 3 (Frontend Unit Tests)**
  Run: `npm --prefix apps/web run test`
  Expected: exit code 0 (84+ tests passed)

- [x] **Step 4: Run Gate 4 (Production Build)**
  Run: `npm --prefix apps/web run build`
  Expected: exit code 0

- [x] **Step 5: Remote VPS Deployment Sync**
  Run: `bash scripts/deploy_to_vps.sh --fast`
  Expected: exit code 0 (cập nhật live hoặc nhận diện offline an toàn)

# Foundation Architecture, 18 PostgreSQL Models, CAS Storage & OCC Triggers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa toàn bộ 18 models SQLAlchemy 2.0 Async, lưu trữ nhị phân CAS có phân đoạn byte-range, hệ thống triggers OCC/source-detached và hàm bootstrap schema CSDL idempotent trên PostgreSQL 16+ pgvector cho VeriScholar.

**Architecture:** Áp dụng phương pháp phân tầng Topo từ gốc lên ngọn (Bottom-Up Topological Layering) tuân thủ Kiến trúc Lục giác (Hexagonal Isolation): Lõi CAS Storage độc lập trong `packages/core` $\rightarrow$ Thực thể Định danh & Tài liệu gốc $\rightarrow$ Thực thể Phiên đọc & Mạng Tri thức GraphRAG $\rightarrow$ Thực thể Soạn thảo & Bootstrap Schema Idempotent trong `apps/api`.

**Tech Stack:** Python 3.12, PostgreSQL 16+, `pgvector` 0.8.0+, SQLAlchemy 2.0 Async, `asyncpg`, `pydantic` v2, `structlog`.

**Spec:** [`docs/superpowers/specs/2026-10-25-foundation-architecture-and-db-design.md`](../specs/2026-10-25-foundation-architecture-and-db-design.md) & [`docs/specs/00-foundation-architecture-and-db.md`](../../specs/00-foundation-architecture-and-db.md).

---

## Global Constraints

- 100% mã nguồn Core Domain và Ports trong `packages/core/` chỉ dùng Python Standard Library và `pydantic`. Tuyệt đối cấm import `sqlalchemy`, `fastapi`, `pymupdf` (tuân thủ AST boundary linter).
- 100% các bảng dữ liệu nghiệp vụ bắt buộc có cột `user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE` phục vụ multi-tenant pre-filtering.
- Tuyệt đối cấm cơ chế fallback ngầm sang SQLite. Nếu không kết nối được PostgreSQL 16+ `pgvector`, hệ thống bắt buộc phải fail-fast.
- Toàn bộ liên kết trong tài liệu Markdown phải dùng đường dẫn tương đối, cấm tuyệt đối URL tuyệt đối máy chủ (`file:///...`).
- Mọi commit đều thực hiện cục bộ trên branch hiện tại, tuyệt đối không push lên remote.
- Giữ vững 4 Cổng Xác Minh Bắt Buộc (`ruff check .`, `uv run pytest`, `npm test`, `npm build`) đồng loạt đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **PostgreSQL pgvector Extension Missing:** Nếu instance PostgreSQL chưa cài hoặc chưa bật extension `vector`, hàm `ensure_database_schema()` phải thông báo lỗi rõ ràng và fail-fast thay vì chạy tiếp gây lỗi cú pháp lạ.
2. **CAS Blob Deletion Race Condition:** Khi hai yêu cầu xóa tài liệu cùng chia sẻ một file băm (`ref_count > 1`) diễn ra đồng thời, việc giảm `ref_count` phải được bảo vệ trong transaction CSDL; file nhị phân trên đĩa chỉ bị `unlink()` khi `ref_count <= 0`.
3. **Multi-Tenant Scoping Leakage:** Truy vấn vector HNSW trên `document_chunks` và `graph_nodes` phải luôn pre-filter `WHERE user_id = :user_id` để ngăn ngừa rò rỉ dữ liệu giữa các học giả khác nhau.
4. **Foreign Key Cascade Detached Trigger:** Khi một `DocumentModel` bị xóa kéo theo `research_notes.document_id` bị gán `NULL` qua `ON DELETE SET NULL`, trigger `BEFORE UPDATE ON research_notes` phải tự động bật `is_source_detached = TRUE` để bảo tồn bằng chứng nghiên cứu.
5. **OCC Concurrent Overwrite Conflict:** Khi hai client cùng gửi yêu cầu cập nhật một bản thảo (`drafts`) với cùng `version`, câu lệnh `UPDATE ... WHERE id = :id AND version = :expected_version` chỉ cho phép client thứ nhất thành công; client thứ hai phải nhận mã lỗi HTTP 412 `PRECONDITION_FAILED`.

---

## Implementation Tasks

### Task 1: CAS Physical Storage Port & Stream Range Adapter (`packages/core`)

**Files:**
- Modify: `packages/core/src/core/ports/storage.py`
- Modify: `packages/core/src/core/adapters/storage/local.py`
- Test: `packages/core/tests/test_cas_storage.py`

**Interfaces:**
- Consumes: Python Standard Library (`hashlib`, `pathlib`, `asyncio`, `collections.abc.AsyncIterator`).
- Produces: `IBlobStoragePort` protocol và `LocalStorageAdapter` class cung cấp các hàm `save_blob`, `get_blob_path`, `blob_exists`, `read_blob`, `stream_blob_range`, `delete_blob`.

- [ ] **Step 1: Viết test kiểm tra phân tán đường dẫn 2 cấp và đọc phân đoạn byte range**

Tạo/cập nhật `packages/core/tests/test_cas_storage.py`:
```python
import pytest
from pathlib import Path
from core.adapters.storage.local import LocalStorageAdapter

@pytest.mark.asyncio
async def test_cas_path_distribution_two_level(tmp_path: Path):
    adapter = LocalStorageAdapter(base_dir=tmp_path)
    sample_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    expected_rel = f"{sample_hash[:2]}/{sample_hash[2:4]}/{sample_hash}"
    assert adapter.get_blob_path(sample_hash) == expected_rel

@pytest.mark.asyncio
async def test_cas_stream_range_reading(tmp_path: Path):
    adapter = LocalStorageAdapter(base_dir=tmp_path)
    content = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    import hashlib
    content_hash = hashlib.sha256(content).hexdigest()
    
    async def async_chunks():
        yield content
    
    path, size = await adapter.save_blob(async_chunks(), content_hash)
    assert size == len(content)
    assert await adapter.blob_exists(content_hash) is True
    
    # Read range 10-19 inclusive
    range_data = b""
    async for chunk in adapter.stream_blob_range(content_hash, start_byte=10, end_byte=19):
        range_data += chunk
    assert range_data == b"ABCDEFGHIJ"
    
    # Delete and clean empty parent folders
    deleted = await adapter.delete_blob(content_hash)
    assert deleted is True
    assert await adapter.blob_exists(content_hash) is False
```

- [ ] **Step 2: Chạy test để xác nhận test chạy và phản ánh hành vi**

Run: `uv run pytest packages/core/tests/test_cas_storage.py -v`
Expected: PASS hoặc FAIL nếu thiếu phương thức `delete_blob` dọn thư mục rỗng.

- [ ] **Step 3: Hoàn thiện `LocalStorageAdapter` trong `packages/core/src/core/adapters/storage/local.py`**

Đảm bảo:
- `get_blob_path(content_hash)` trả về `<hash[:2]>/<hash[2:4]>/<hash>`.
- `stream_blob_range(content_hash, start_byte, end_byte, chunk_size)` yield đúng byte slice.
- `delete_blob(content_hash)` gọi `unlink(missing_ok=True)` và dọn dẹp các thư mục cha nếu chúng rỗng.
- Toàn bộ file I/O chạy qua `asyncio.to_thread`.

- [ ] **Step 4: Chạy lại test suite để xác nhận 100% PASS**

Run: `uv run pytest packages/core/tests/test_cas_storage.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add packages/core/src/core/ports/storage.py packages/core/src/core/adapters/storage/local.py packages/core/tests/test_cas_storage.py
git commit -m "feat(core): enhance CAS storage adapter with two-level hierarchy and range streaming"
```

---

### Task 2: Identity & Authentication Models (`users`, `scholar_profiles`, `user_api_keys`)

**Files:**
- Modify: `apps/api/src/api/db/models/user.py`
- Create: `apps/api/src/api/db/models/scholar_profile.py`
- Create: `apps/api/src/api/db/models/user_api_key.py`
- Test: `apps/api/tests/test_identity_models.py`

**Interfaces:**
- Consumes: `IdentifiableTimestampedModel` từ `apps.api.db.models.base`.
- Produces: `UserModel`, `ScholarProfileModel`, `UserApiKeyModel` (với ràng buộc `UNIQUE(user_id, provider)`).

- [ ] **Step 1: Viết failing test cho quan hệ 1:1 và ràng buộc khóa API**

Tạo `apps/api/tests/test_identity_models.py`:
```python
import pytest
from uuid import uuid4
from api.db.models.user import UserModel
from api.db.models.scholar_profile import ScholarProfileModel
from api.db.models.user_api_key import UserApiKeyModel

def test_scholar_profile_and_user_model_instantiation():
    user = UserModel(
        email="scholar@stanford.edu",
        full_name="Dr. Jane Doe",
        hashed_password="secure_hashed_pw",
        role="researcher",
    )
    profile = ScholarProfileModel(
        user_id=user.id,
        institution="Stanford University",
        department="Computer Science",
        academic_rank="Associate Professor",
        orcid_id="0000-0002-1825-0097",
        research_interests=["Deep Learning", "NLP", "AI Agents"],
    )
    assert profile.user_id == user.id
    assert "NLP" in profile.research_interests

def test_user_api_key_model_instantiation():
    user_id = uuid4()
    api_key = UserApiKeyModel(
        user_id=user_id,
        provider="openai",
        encrypted_key="enc_aes256gcm_secret",
        key_hint="sk-...a9b1",
        is_active=True,
    )
    assert api_key.provider == "openai"
    assert api_key.is_active is True
```

- [ ] **Step 2: Chạy test để xác nhận FAIL vì chưa có file model**

Run: `uv run pytest apps/api/tests/test_identity_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.db.models.scholar_profile'`

- [ ] **Step 3: Triển khai các Model định danh**

1. Tạo `apps/api/src/api/db/models/scholar_profile.py`:
   - Kế thừa `IdentifiableTimestampedModel`.
   - `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)`
   - `institution`, `department`, `academic_rank`, `orcid_id`, `google_scholar_url`, `bio`.
   - `research_interests: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)`.
2. Tạo `apps/api/src/api/db/models/user_api_key.py`:
   - Kế thừa `IdentifiableTimestampedModel`.
   - `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`
   - `provider: Mapped[str] = mapped_column(String(50), nullable=False)`
   - `encrypted_key: Mapped[str] = mapped_column(String(500), nullable=False)`
   - `key_hint: Mapped[str] = mapped_column(String(10), nullable=False)`
   - `is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)`
   - `__table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_api_keys_user_provider"), CheckConstraint("provider IN ('openai', 'anthropic', 'google', 'exa')", name="ck_user_api_keys_provider"))`
3. Cập nhật `apps/api/src/api/db/models/user.py`: Giữ các trường học thuật cũ ở trạng thái nullable để bảo toàn tương thích ngược cho auth service.

- [ ] **Step 4: Chạy lại test suite để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_identity_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 2**

```bash
git add apps/api/src/api/db/models/user.py apps/api/src/api/db/models/scholar_profile.py apps/api/src/api/db/models/user_api_key.py apps/api/tests/test_identity_models.py
git commit -m "feat(api): add ScholarProfileModel and UserApiKeyModel with provider constraints"
```

---

### Task 3: Root Document Entities & Physical CAS Blob Junction (`document_storage_blobs`, `documents`, `document_chunks`, `document_summaries`, `reference_items`)

**Files:**
- Modify: `apps/api/src/api/db/models/blob.py`
- Modify: `apps/api/src/api/db/models/document.py`
- Modify: `apps/api/src/api/db/models/chunk.py`
- Modify: `apps/api/src/api/db/models/summary.py`
- Modify: `apps/api/src/api/db/models/reference.py`
- Test: `apps/api/tests/test_document_models.py`
- Test: `apps/api/tests/test_cas_lifecycle.py`

**Interfaces:**
- Consumes: `IdentifiableTimestampedModel`, `pgvector.sqlalchemy.Vector`.
- Produces: `DocumentStorageBlobModel`, `DocumentModel`, `DocumentChunkModel` (với `user_id` và `content_tsv`), `DocumentSummaryModel` (3 luận điểm), `ReferenceItemModel` (với `user_id`).

- [ ] **Step 1: Viết test cho ràng buộc `user_id` trên child entities và CAS reference count**

Tạo `apps/api/tests/test_document_models.py`:
```python
import pytest
from uuid import uuid4
from api.db.models.chunk import DocumentChunkModel
from api.db.models.summary import DocumentSummaryModel
from api.db.models.reference import ReferenceItemModel

def test_document_child_entities_require_user_id():
    user_id = uuid4()
    doc_id = uuid4()
    
    chunk = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        text_content="Transformer self-attention mechanism...",
        bbox_json={"coords": [10.0, 20.0, 100.0, 50.0]},
    )
    assert chunk.user_id == user_id
    assert chunk.document_id == doc_id
    
    summary = DocumentSummaryModel(
        user_id=user_id,
        document_id=doc_id,
        problem_statement="Recurrent models are slow.",
        problem_citations=[],
        contributions="Proposed Multi-Head Attention.",
        contribution_citations=[],
        limitations="Quadratic memory complexity.",
        limitation_citations=[],
    )
    assert summary.user_id == user_id
    assert summary.contributions != ""
    
    ref = ReferenceItemModel(
        user_id=user_id,
        document_id=doc_id,
        ref_index=1,
        raw_text="Vaswani et al. 2017.",
        doi="10.48550/arXiv.1706.03762",
    )
    assert ref.user_id == user_id
    assert ref.ref_index == 1
```

- [ ] **Step 2: Chạy test để phát hiện các model thiếu thuộc tính `user_id`**

Run: `uv run pytest apps/api/tests/test_document_models.py -v`
Expected: FAIL (nếu model chưa có thuộc tính `user_id`).

- [ ] **Step 3: Cập nhật các Model thuộc cụm Document**

1. `apps/api/src/api/db/models/blob.py`: Đảm bảo `DocumentStorageBlobModel` có `ref_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)`.
2. `apps/api/src/api/db/models/document.py`: Đảm bảo `DocumentModel` có `user_id: Mapped[UUID]`, `blob_id: Mapped[UUID | None]` với `ForeignKey("document_storage_blobs.id", ondelete="RESTRICT")`, `status` và `access_status` có check constraints.
3. `apps/api/src/api/db/models/chunk.py`: Thêm `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`.
4. `apps/api/src/api/db/models/summary.py`: Thêm `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`.
5. `apps/api/src/api/db/models/reference.py`: Thêm `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`.

- [ ] **Step 4: Chạy lại test suite để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_document_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 3**

```bash
git add apps/api/src/api/db/models/blob.py apps/api/src/api/db/models/document.py apps/api/src/api/db/models/chunk.py apps/api/src/api/db/models/summary.py apps/api/src/api/db/models/reference.py apps/api/tests/test_document_models.py
git commit -m "feat(api): ensure user_id multi-tenant scoping and ref_count on document models"
```

---

### Task 4: Interactive Session & Academic Notes Models (`research_sessions`, `session_documents`, `session_turns`, `research_notes`, `folders`)

**Files:**
- Modify: `apps/api/src/api/db/models/session.py`
- Modify: `apps/api/src/api/db/models/note.py`
- Modify: `apps/api/src/api/db/models/folder.py`
- Test: `apps/api/tests/test_session_note_models.py`

**Interfaces:**
- Consumes: `IdentifiableTimestampedModel`, `Base`.
- Produces: `ResearchSessionModel`, `SessionDocumentModel`, `SessionTurnModel` (với `user_id` và `trace_id`), `ResearchNoteModel`, `FolderModel`.

- [ ] **Step 1: Viết test cho Session turns và Research Note frozen snapshot**

Tạo `apps/api/tests/test_session_note_models.py`:
```python
import pytest
from uuid import uuid4
from api.db.models.session import SessionTurnModel, ResearchSessionModel
from api.db.models.note import ResearchNoteModel
from api.db.models.folder import FolderModel

def test_session_turn_has_user_id_and_trace_id():
    user_id = uuid4()
    session_id = uuid4()
    turn = SessionTurnModel(
        user_id=user_id,
        session_id=session_id,
        question="What is the BLEU score?",
        answer="The BLEU score is 28.4 [[cite:chunk-1]].",
        citations=[{"chunk_id": "c1", "page": 4}],
        trace_id="tr_9c1fa8fe",
    )
    assert turn.user_id == user_id
    assert turn.trace_id == "tr_9c1fa8fe"

def test_research_note_evidence_preservation():
    user_id = uuid4()
    note = ResearchNoteModel(
        user_id=user_id,
        document_id=uuid4(),
        selected_text="Scaled dot-product formula",
        bounding_boxes=[[10, 20, 30, 40]],
        page_number=3,
        user_note="Important for chapter 2",
        tags=["attention", "math"],
        frozen_snapshot={"paper_title": "Attention Is All You Need", "year": 2017},
        version=1,
    )
    assert note.is_source_detached is False
    assert note.version == 1
    assert "math" in note.tags
```

- [ ] **Step 2: Chạy test để xác nhận FAIL nếu `SessionTurnModel` thiếu trường**

Run: `uv run pytest apps/api/tests/test_session_note_models.py -v`
Expected: FAIL nếu `SessionTurnModel` chưa có cột `user_id` hoặc `trace_id`.

- [ ] **Step 3: Cập nhật `SessionTurnModel`, `ResearchNoteModel`, `FolderModel`**

1. `apps/api/src/api/db/models/session.py`:
   - Thêm `user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)` vào `SessionTurnModel`.
   - Thêm `trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)` vào `SessionTurnModel`.
2. `apps/api/src/api/db/models/note.py`:
   - Xác nhận đã có đủ `selected_text`, `bounding_boxes`, `frozen_snapshot`, `is_source_detached`, `version`.
3. `apps/api/src/api/db/models/folder.py`:
   - Xác nhận có `color: Mapped[str]`, `description: Mapped[str | None]`, `parent_id: Mapped[UUID | None]`.

- [ ] **Step 4: Chạy lại test suite để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_session_note_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 4**

```bash
git add apps/api/src/api/db/models/session.py apps/api/src/api/db/models/note.py apps/api/src/api/db/models/folder.py apps/api/tests/test_session_note_models.py
git commit -m "feat(api): add multi-tenant user_id to session_turns and confirm note evidence models"
```

---

### Task 5: 4-Entity Academic Knowledge Graph Models (`graph_nodes`, `graph_edges`)

**Files:**
- Create: `apps/api/src/api/db/models/graph.py`
- Test: `apps/api/tests/test_graph_models.py`

**Interfaces:**
- Consumes: `IdentifiableTimestampedModel`, `Vector(1536)` từ `pgvector.sqlalchemy`.
- Produces: `GraphNodeModel` và `GraphEdgeModel` với ràng buộc `UNIQUE(user_id, node_type, canonical_name)`.

- [ ] **Step 1: Viết test cho GraphNode và GraphEdge schemas & constraints**

Tạo `apps/api/tests/test_graph_models.py`:
```python
import pytest
from uuid import uuid4
from api.db.models.graph import GraphNodeModel, GraphEdgeModel

def test_graph_node_canonical_representation():
    user_id = uuid4()
    node = GraphNodeModel(
        user_id=user_id,
        node_type="Method",
        canonical_name="transformer",
        display_name="Transformer",
        description="Attention-based sequence architecture",
    )
    assert node.user_id == user_id
    assert node.node_type == "Method"
    assert node.canonical_name == "transformer"

def test_graph_edge_representation():
    user_id = uuid4()
    source_id = uuid4()
    target_id = uuid4()
    edge = GraphEdgeModel(
        user_id=user_id,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_type="PROPOSES",
        weight=1.0,
    )
    assert edge.edge_type == "PROPOSES"
    assert edge.weight == 1.0
```

- [ ] **Step 2: Chạy test để xác nhận FAIL vì chưa có file `graph.py`**

Run: `uv run pytest apps/api/tests/test_graph_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.db.models.graph'`

- [ ] **Step 3: Triển khai `apps/api/src/api/db/models/graph.py`**

Tạo `apps/api/src/api/db/models/graph.py`:
```python
"""Database models for 4-Entity PostgreSQL GraphRAG."""

from uuid import UUID
from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class GraphNodeModel(IdentifiableTimestampedModel):
    """Canonical knowledge graph node shared across papers for a user."""
    __tablename__ = "graph_nodes"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    node_type: Mapped[str] = mapped_column(String(30), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "node_type", "canonical_name", name="uq_graph_nodes_user_type_canonical"),
        CheckConstraint("node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult')", name="ck_graph_nodes_type"),
        Index("idx_graph_nodes_user_canonical", "user_id", "canonical_name"),
    )

class GraphEdgeModel(IdentifiableTimestampedModel):
    """Typed academic relation between knowledge graph nodes."""
    __tablename__ = "graph_edges"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    source_node_id: Mapped[UUID] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id: Mapped[UUID] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String(30), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_chunk_id: Mapped[UUID | None] = mapped_column(ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')", name="ck_graph_edges_type"),
        Index("idx_graph_edges_source_target", "source_node_id", "target_node_id"),
        Index("idx_graph_edges_user_type", "user_id", "edge_type"),
    )
```

- [ ] **Step 4: Chạy lại test suite để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_graph_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 5**

```bash
git add apps/api/src/api/db/models/graph.py apps/api/tests/test_graph_models.py
git commit -m "feat(api): implement GraphNodeModel and GraphEdgeModel with canonical hub constraints"
```

---

### Task 6: Agentic Writing Workspace Models (`drafts`, `draft_assets`, `draft_messages`)

**Files:**
- Modify: `apps/api/src/api/db/models/draft.py`
- Create: `apps/api/src/api/db/models/draft_asset.py`
- Create: `apps/api/src/api/db/models/draft_message.py`
- Test: `apps/api/tests/test_draft_models.py`

**Interfaces:**
- Consumes: `IdentifiableTimestampedModel`, `Base`.
- Produces: `DraftModel` (với `bib_content`, `version`), `DraftAssetModel` (với `UNIQUE(draft_id, file_name)`), `DraftMessageModel`.

- [ ] **Step 1: Viết test cho Draft OCC version, Assets và Messages**

Tạo `apps/api/tests/test_draft_models.py`:
```python
import pytest
from uuid import uuid4
from api.db.models.draft import DraftModel
from api.db.models.draft_asset import DraftAssetModel
from api.db.models.draft_message import DraftMessageModel

def test_draft_model_fields_and_snapshot():
    user_id = uuid4()
    draft = DraftModel(
        user_id=user_id,
        title="Attention Mechanism Survey",
        content="\\documentclass{article}\n\\begin{document}\nHello\\end{document}",
        bib_content="@article{vaswani2017,\n  title={Attention Is All You Need}\n}",
        version=1,
        previous_snapshot={"content": "old", "bib_content": "old_bib", "version": 0},
    )
    assert draft.user_id == user_id
    assert draft.version == 1
    assert "@article" in draft.bib_content

def test_draft_asset_model():
    draft_id = uuid4()
    asset = DraftAssetModel(
        user_id=uuid4(),
        draft_id=draft_id,
        blob_id=uuid4(),
        file_name="figures/arch.png",
        mime_type="image/png",
        byte_size=10240,
    )
    assert asset.file_name == "figures/arch.png"
    assert asset.draft_id == draft_id
```

- [ ] **Step 2: Chạy test để xác nhận FAIL vì thiếu asset model**

Run: `uv run pytest apps/api/tests/test_draft_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.db.models.draft_asset'`

- [ ] **Step 3: Triển khai các Model Writing Workspace**

1. `apps/api/src/api/db/models/draft.py`:
   - Bổ sung `bib_content: Mapped[str] = mapped_column(Text, default="", nullable=False)`.
   - Bổ sung `source_session_id: Mapped[UUID | None] = mapped_column(ForeignKey("research_sessions.id", ondelete="SET NULL"), nullable=True)`.
   - Bổ sung `previous_snapshot: Mapped[dict | None] = mapped_column(JSONType, nullable=True)`.
   - Bổ sung `pdf_preview_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)`.
   - Bổ sung `version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)`.
2. Tạo `apps/api/src/api/db/models/draft_asset.py`:
   - `DraftAssetModel` (kế thừa `IdentifiableTimestampedModel`).
   - `user_id: Mapped[UUID]`, `draft_id: Mapped[UUID]`, `blob_id: Mapped[UUID]`.
   - `file_name: Mapped[str] = mapped_column(String(255), nullable=False)`.
   - `mime_type: Mapped[str] = mapped_column(String(100), nullable=False)`.
   - `byte_size: Mapped[int] = mapped_column(Integer, nullable=False)`.
   - `UniqueConstraint("draft_id", "file_name", name="uq_draft_assets_draft_filename")`.
3. Tạo `apps/api/src/api/db/models/draft_message.py`:
   - `DraftMessageModel` (kế thừa `IdentifiableTimestampedModel`).
   - `user_id: Mapped[UUID]`, `draft_id: Mapped[UUID]`.
   - `role: Mapped[str] = mapped_column(String(20), nullable=False)`.
   - `content: Mapped[str] = mapped_column(Text, nullable=False)`.
   - `tool_calls: Mapped[dict | None] = mapped_column(JSONType, nullable=True)`.
   - `compile_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)`.
   - `trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)`.
   - `CheckConstraint("role IN ('user', 'assistant', 'tool')", name="ck_draft_messages_role")`.

- [ ] **Step 4: Chạy lại test suite để xác nhận PASS**

Run: `uv run pytest apps/api/tests/test_draft_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 6**

```bash
git add apps/api/src/api/db/models/draft.py apps/api/src/api/db/models/draft_asset.py apps/api/src/api/db/models/draft_message.py apps/api/tests/test_draft_models.py
git commit -m "feat(api): add DraftAssetModel and DraftMessageModel with LaTeX project assets constraints"
```

---

### Task 7: Database Model Registry & Idempotent Bootstrap Engine (`init_db.py`)

**Files:**
- Modify: `apps/api/src/api/db/models/__init__.py`
- Modify: `apps/api/src/api/db/init_db.py`
- Test: `apps/api/tests/test_db_bootstrap.py`

**Interfaces:**
- Consumes: Toàn bộ 18 models từ `apps.api.db.models.*`, `sqlalchemy.ext.asyncio.AsyncConnection`.
- Produces: `ensure_database_schema(conn: AsyncConnection)` khởi tạo an toàn 18 bảng, triggers OCC & detached, chỉ mục HNSW và GIN.

- [ ] **Step 1: Viết test cho tính năng Idempotent bootstrap và Triggers**

Tạo `apps/api/tests/test_db_bootstrap.py`:
```python
import pytest
from sqlalchemy import text
from api.db.init_db import ensure_database_schema
from api.db.session import engine

@pytest.mark.asyncio
async def test_ensure_database_schema_runs_idempotently():
    """Verify that ensure_database_schema runs consecutively without raising exceptions."""
    if engine.dialect.name != "postgresql":
        pytest.skip("Bootstrap test requires PostgreSQL with pgvector")
    
    async with engine.begin() as conn:
        await ensure_database_schema(conn)
        await ensure_database_schema(conn) # 2nd run to verify idempotency
        
        # Verify 18 tables exist
        res = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = {row[0] for row in res.fetchall()}
        required_tables = {
            "users", "scholar_profiles", "user_api_keys", "document_storage_blobs",
            "documents", "document_chunks", "document_summaries", "reference_items",
            "research_sessions", "session_documents", "session_turns", "research_notes",
            "folders", "graph_nodes", "graph_edges", "drafts", "draft_assets", "draft_messages"
        }
        missing = required_tables - tables
        assert not missing, f"Missing required tables in schema: {missing}"
```

- [ ] **Step 2: Đăng ký toàn bộ 18 models vào `apps/api/src/api/db/models/__init__.py`**

Export đầy đủ:
- `UserModel`
- `ScholarProfileModel`
- `UserApiKeyModel`
- `DocumentStorageBlobModel`
- `DocumentModel`
- `DocumentChunkModel`
- `DocumentSummaryModel`
- `ReferenceItemModel`
- `ResearchSessionModel`
- `SessionDocumentModel`
- `SessionTurnModel`
- `ResearchNoteModel`
- `FolderModel`
- `GraphNodeModel`
- `GraphEdgeModel`
- `DraftModel`
- `DraftAssetModel`
- `DraftMessageModel`

- [ ] **Step 3: Cập nhật `ensure_database_schema` trong `apps/api/src/api/db/init_db.py`**

1. Tạo extension `vector`.
2. Tạo hàm `handle_occ_and_timestamp()` và gán trigger `BEFORE UPDATE` vào `drafts` và `research_notes`.
3. Tạo hàm `handle_note_source_detached()` và gán trigger `BEFORE UPDATE` vô điều kiện vào `research_notes`.
4. Gọi `await conn.run_sync(Base.metadata.create_all)`.
5. Tạo các chỉ mục nâng cao:
   - `CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);`
   - `CREATE INDEX IF NOT EXISTS idx_graph_nodes_embedding_hnsw ON graph_nodes USING hnsw (embedding vector_cosine_ops);`
   - `CREATE INDEX IF NOT EXISTS idx_document_chunks_tsv ON document_chunks USING gin (content_tsv);`

- [ ] **Step 4: Chạy test unit và boundary để xác nhận tính toàn vẹn**

Run: `uv run pytest apps/api/tests/test_architecture_boundary.py apps/api/tests/test_identity_models.py apps/api/tests/test_document_models.py apps/api/tests/test_session_note_models.py apps/api/tests/test_graph_models.py apps/api/tests/test_draft_models.py -v`
Expected: 100% PASS

- [ ] **Step 5: Commit Task 7**

```bash
git add apps/api/src/api/db/models/__init__.py apps/api/src/api/db/init_db.py apps/api/tests/test_db_bootstrap.py
git commit -m "feat(api): register all 18 models and complete idempotent database bootstrap engine"
```

---

### Task 8: End-to-End Foundation Verification & Gatekeeper Integrity

**Files:**
- Test: Toàn bộ test suite monorepo

- [ ] **Step 1: Chạy Cổng 1 (Python Linter)**
Run: `uv run ruff check .`
Expected: Exit code 0 ("All checks passed!")

- [ ] **Step 2: Chạy Cổng 2 (Backend Unit & Boundary Tests)**
Run: `uv run pytest`
Expected: 100% Passed

- [ ] **Step 3: Chạy Cổng 3 (Frontend Unit Tests)**
Run: `npm --prefix apps/web run test`
Expected: Exit code 0

- [ ] **Step 4: Chạy Cổng 4 (Frontend Production Build)**
Run: `npm --prefix apps/web run build`
Expected: Exit code 0 ("built in ...s")

- [ ] **Step 5: Commit Hoàn Thành Phân Hệ 00**

```bash
git add .
git commit -m "chore(foundation): complete all 18 database models and idempotent schema bootstrap"
```

"""Automated integration tests for Academic Reference Resolvers & Citation Graph (Module 3)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryReferenceStore:
    """In-memory database store for reference resolver and citation graph tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.references: dict[UUID, list[ReferenceItemModel]] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "status", None) is None:
                obj.status = "completed"
            self.documents[obj.id] = obj
        elif isinstance(obj, ReferenceItemModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.references.setdefault(obj.document_id, []).append(obj)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. Select reference items
        if "FROM reference_items" in stmt_str:
            mock_res = MagicMock()
            target_doc_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.references:
                    target_doc_id = v
                    break
            refs = self.references.get(target_doc_id, []) if target_doc_id else []
            mock_res.scalars.return_value.all.return_value = refs
            return mock_res

        # 2. Select document
        if "FROM documents" in stmt_str:
            mock_res = MagicMock()
            target_doc_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.documents:
                    target_doc_id = v
                    break
            doc = self.documents.get(target_doc_id) if target_doc_id else None
            mock_res.scalar_one_or_none.return_value = doc
            mock_res.scalars.return_value.all.return_value = [doc] if doc else []
            return mock_res

        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def ref_store() -> InMemoryReferenceStore:
    return InMemoryReferenceStore()


@pytest.fixture
def mock_db_session(ref_store: InMemoryReferenceStore) -> AsyncSession:
    return ref_store  # type: ignore[return-value]


@pytest.fixture
def mock_user() -> UserModel:
    user = UserModel(
        email="citation_expert@verischolar.org",
        full_name="Dr. Citation",
        is_active=True,
    )
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def client(
    mock_db_session: AsyncSession,
    mock_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> UserModel:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_resolve_references_success(client: AsyncClient) -> None:
    """Resolve an academic reference with open access PDF extraction."""
    payload = {
        "references": [
            {
                "ref_id": "ref_101",
                "doi": "10.48550/arXiv.1706.03762",
                "title": "Attention Is All You Need",
            }
        ]
    }
    response = await client.post("/api/v1/references:resolve", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert len(data["resolved"]) == 1
    ref = data["resolved"][0]
    assert ref["ref_id"] == "ref_101"
    assert ref["arxiv_id"] == "1706.03762"
    assert ref["has_open_access_pdf"] is True
    assert "https://arxiv.org/pdf/1706.03762.pdf" in ref["pdf_download_url"]
    assert data["live_resolved_count"] >= 1


@pytest.mark.asyncio
async def test_resolve_references_caching(client: AsyncClient) -> None:
    """Subsequent requests hit Global Academic Cache (< 10ms SLA)."""
    payload = {
        "references": [
            {
                "ref_id": "ref_cache_test",
                "doi": "10.48550/arXiv.1607.06450",
                "title": "Layer Normalization",
            }
        ]
    }
    # First request: live or cache
    resp1 = await client.post("/api/v1/references:resolve", json=payload)
    assert resp1.status_code == 200

    # Second request: strictly cached
    resp2 = await client.post("/api/v1/references:resolve", json=payload)
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["data"]["cached_count"] == 1


@pytest.mark.asyncio
async def test_resolve_references_empty_fails(client: AsyncClient) -> None:
    """Empty reference list fails validation with 422."""
    payload = {"references": []}
    response = await client.post("/api/v1/references:resolve", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_citation_graph_success(
    client: AsyncClient,
    ref_store: InMemoryReferenceStore,
) -> None:
    """Citation graph returns node-link schema with root and cited vertices."""
    root_doc = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="transformer.pdf",
        title="Attention Is All You Need",
        publication_year=2017,
        content_hash="hash_root",
        file_size_bytes=1000,
        is_persistent=True,
    )
    ref_store.add(root_doc)

    ref1 = ReferenceItemModel(
        document_id=root_doc.id,
        ref_index=1,
        raw_text="Ba et al. Layer Normalization.",
        parsed_title="Layer Normalization",
        parsed_year=2016,
        arxiv_id="1607.06450",
    )
    ref2 = ReferenceItemModel(
        document_id=root_doc.id,
        ref_index=2,
        raw_text="Vaswani et al. Neural Machine Translation.",
        parsed_title="Neural Machine Translation",
        parsed_year=2015,
        doi="10.1000/182",
    )
    ref_store.add(ref1)
    ref_store.add(ref2)

    # Test via /references/{document_id}/graph
    response = await client.get(f"/api/v1/references/{root_doc.id}/graph")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["root_document_id"] == str(root_doc.id)
    assert len(data["nodes"]) == 3  # Root + 2 cited
    assert len(data["edges"]) == 2  # 2 outgoing CITES edges
    assert any(n["type"] == "root" for n in data["nodes"])
    assert all(e["relation"] == "CITES" for e in data["edges"])


@pytest.mark.asyncio
async def test_citation_graph_documents_alias(
    client: AsyncClient,
    ref_store: InMemoryReferenceStore,
) -> None:
    """Endpoint is also reachable via /api/v1/documents/{id}/graph."""
    doc = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="paper.pdf",
        title="Sample Paper",
        content_hash="h_alias",
        file_size_bytes=500,
        is_persistent=True,
    )
    ref_store.add(doc)

    response = await client.get(f"/api/v1/documents/{doc.id}/graph")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["root_document_id"] == str(doc.id)


@pytest.mark.asyncio
async def test_citation_graph_cycle_breaking(
    client: AsyncClient,
    ref_store: InMemoryReferenceStore,
) -> None:
    """Cyclic citations (A cites B, B cites A) terminate cleanly without infinite loop."""
    doc_a = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="paper_a.pdf",
        title="Paper A",
        content_hash="ha",
        file_size_bytes=1000,
        is_persistent=True,
    )
    doc_b = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="paper_b.pdf",
        title="Paper B",
        content_hash="hb",
        file_size_bytes=1000,
        is_persistent=True,
    )
    ref_store.add(doc_a)
    ref_store.add(doc_b)

    # A cites B (resolved)
    ref_a = ReferenceItemModel(
        document_id=doc_a.id,
        ref_index=1,
        raw_text="Paper B",
        parsed_title="Paper B",
        resolved_document_id=doc_b.id,
    )
    # B cites A (resolved - creates cycle)
    ref_b = ReferenceItemModel(
        document_id=doc_b.id,
        ref_index=1,
        raw_text="Paper A",
        parsed_title="Paper A",
        resolved_document_id=doc_a.id,
    )
    ref_store.add(ref_a)
    ref_store.add(ref_b)

    response = await client.get(f"/api/v1/references/{doc_a.id}/graph?max_hops=2")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    # Visited set breaks the loop safely
    assert len(body["data"]["nodes"]) <= 3


@pytest.mark.asyncio
async def test_citation_graph_not_found(client: AsyncClient) -> None:
    """Querying graph for non-existent document returns 404."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/references/{fake_id}/graph")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"

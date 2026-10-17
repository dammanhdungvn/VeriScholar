"""Integration test suite for Reference Ingestion & Citation Graph (PRD §3.3).

Validates:
- POST /api/v1/sessions/{id}/references:ingest:
  - Ingesting open-access references into active session documents.
  - Automatic DocumentModel generation & ReferenceItemModel.resolved_document_id linking.
  - Strict Session Capacity Cap <= 5 papers constraint (HTTP 422 on overflow).
  - Multi-tenant isolation on session and source document.
- GET /api/v1/sessions/{id}/citation-graph:
  - Graph construction with nodes (depth 0, 1, 2) and typed edges (CITES, EXTENDS, BENCHMARKS_ON).
  - Graph Cycle Breaking & Max-Hop Constraint (k <= 2).
  - Cyclic citation loops (A -> B -> A) are safely broken without infinite loops.
  - Foundational reading path generated via topological sorting.
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.reference import CitationEdgeModel, ReferenceItemModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_academic_resolver
from api.services.auth_service import AuthService
from core.services.exa_resolver import InMemoryAcademicResolverAdapter
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def ingestion_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession], InMemoryAcademicResolverAdapter]
]:
    """Provide isolated in-memory SQLite database and client with test double resolver."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    test_resolver = InMemoryAcademicResolverAdapter()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def override_get_resolver() -> InMemoryAcademicResolverAdapter:
        return test_resolver

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_academic_resolver] = override_get_resolver

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, session_maker, test_resolver

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_academic_resolver, None)
    await engine.dispose()


async def create_test_user(
    session_maker: async_sessionmaker[AsyncSession],
    email: str = "researcher@verischolar.org",
    full_name: str = "Claude Shannon",
) -> tuple[UserModel, str]:
    """Create test user in DB and return (user, jwt_token)."""
    async with session_maker() as session:
        user = UserModel(
            id=uuid4(),
            email=email,
            full_name=full_name,
            hashed_password="mock_hashed_password",
            is_active=True,
            role="researcher",
            institution="MIT / Bell Labs",
            academic_rank="Information Theorist",
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = AuthService.create_token(
        payload={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta_seconds=3600,
    )
    return user, token


async def create_session_with_documents(
    session_maker: async_sessionmaker[AsyncSession],
    user_id: UUID,
    num_docs: int = 1,
) -> tuple[ResearchSessionModel, list[DocumentModel]]:
    """Helper creating a research session with pre-attached documents."""
    async with session_maker() as session:
        sess = ResearchSessionModel(
            id=uuid4(),
            user_id=user_id,
            title="Cross-Paper Multi-Model Session",
            viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
        )
        session.add(sess)
        await session.flush()

        docs: list[DocumentModel] = []
        for i in range(num_docs):
            doc = DocumentModel(
                id=uuid4(),
                user_id=user_id,
                filename=f"session_doc_{i + 1}.pdf",
                title=f"Session Paper #{i + 1}",
                authors=[f"Author {i + 1}"],
                publication_year=2021 + i,
                content_hash=f"hash_{uuid4().hex}",
                file_size_bytes=1024 * (i + 1),
                status="ready",
                stage="completed",
                progress=100,
            )
            session.add(doc)
            await session.flush()

            sess_doc = SessionDocumentModel(
                session_id=sess.id,
                document_id=doc.id,
                display_order=i,
            )
            session.add(sess_doc)
            docs.append(doc)

        await session.commit()
        await session.refresh(sess)
        return sess, docs


# ==============================================================================
# 1. References Ingestion Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_ingest_references_success() -> None:
    """Validate successfully ingesting open-access references into session."""
    async with ingestion_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        sess, docs = await create_session_with_documents(session_maker, user.id, num_docs=1)
        root_doc = docs[0]

        # Add reference items to root_doc
        async with session_maker() as session:
            ref1 = ReferenceItemModel(
                document_id=root_doc.id,
                ref_index=1,
                raw_text="Vaswani et al., Attention is All You Need. 2017.",
                parsed_title="Attention is All You Need",
                parsed_authors=["Vaswani, A."],
                parsed_year=2017,
                arxiv_id="1706.03762",
            )
            ref2 = ReferenceItemModel(
                document_id=root_doc.id,
                ref_index=2,
                raw_text="Devlin et al., BERT: Pre-training. 2018.",
                parsed_title="BERT: Pre-training of Deep Bidirectional Transformers",
                parsed_authors=["Devlin, J."],
                parsed_year=2018,
                arxiv_id="1810.04805",
            )
            session.add_all([ref1, ref2])
            await session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            f"/api/v1/sessions/{sess.id}/references:ingest",
            headers=headers,
            json={
                "document_id": str(root_doc.id),
                "selected_ref_indices": [1, 2],
            },
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        data = body["data"]
        assert data["session_id"] == str(sess.id)
        assert data["total_ingested"] == 2
        assert data["session_document_count"] == 3  # 1 initial + 2 ingested
        assert len(data["ingested_documents"]) == 2

        ing_1 = data["ingested_documents"][0]
        assert ing_1["ref_index"] == 1
        assert ing_1["title"] == "Attention is All You Need"
        assert ing_1["open_access_pdf_url"] == "https://arxiv.org/pdf/1706.03762.pdf"

        # Verify DB records
        async with session_maker() as session:
            # Check ReferenceItemModel updated
            ref_db = await session.scalar(
                select(ReferenceItemModel).where(
                    ReferenceItemModel.document_id == root_doc.id,
                    ReferenceItemModel.ref_index == 1,
                )
            )
            assert ref_db is not None
            assert ref_db.resolved_document_id == UUID(ing_1["document_id"])

            # Check CitationEdgeModel created
            edge = await session.scalar(
                select(CitationEdgeModel).where(
                    CitationEdgeModel.source_document_id == root_doc.id,
                    CitationEdgeModel.target_document_id == UUID(ing_1["document_id"]),
                )
            )
            assert edge is not None
            assert edge.relation == "CITES"


@pytest.mark.asyncio
async def test_ingest_references_capacity_cap_exceeded() -> None:
    """Strict Invariant: Capacity Cap <= 5 papers. Returns 422 if current + selected > 5."""
    async with ingestion_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        # Session already has 4 documents
        sess, docs = await create_session_with_documents(session_maker, user.id, num_docs=4)
        root_doc = docs[0]

        # Add 3 references
        async with session_maker() as session:
            for i in range(1, 4):
                session.add(
                    ReferenceItemModel(
                        document_id=root_doc.id,
                        ref_index=i,
                        raw_text=f"Reference Paper #{i}",
                        parsed_title=f"Paper Title #{i}",
                        arxiv_id=f"240{i}.0000{i}",
                    )
                )
            await session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        # Attempting to ingest 2 references (4 current + 2 = 6 > 5)
        resp = await client.post(
            f"/api/v1/sessions/{sess.id}/references:ingest",
            headers=headers,
            json={
                "document_id": str(root_doc.id),
                "selected_ref_indices": [1, 2],
            },
        )

        assert resp.status_code == 422, resp.text
        err = resp.json()["error"]
        assert err["code"] == "SESSION_CAPACITY_EXCEEDED"
        assert "giới hạn tối đa 5 bài báo" in err["message"]


@pytest.mark.asyncio
async def test_ingest_references_multi_tenant_isolation() -> None:
    """User B cannot ingest references into User A's session."""
    async with ingestion_test_context() as (client, session_maker, _resolver):
        user_a, _ = await create_test_user(session_maker, email="user_a@verischolar.org")
        _user_b, token_b = await create_test_user(session_maker, email="user_b@verischolar.org")
        sess_a, docs_a = await create_session_with_documents(session_maker, user_a.id, num_docs=1)

        headers_b = {"Authorization": f"Bearer {token_b}"}
        resp = await client.post(
            f"/api/v1/sessions/{sess_a.id}/references:ingest",
            headers=headers_b,
            json={
                "document_id": str(docs_a[0].id),
                "selected_ref_indices": [1],
            },
        )

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "SESSION_NOT_FOUND"


# ==============================================================================
# 2. Citation Graph & Cycle Breaking Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_citation_graph_construction_and_topo_path() -> None:
    """Validate 2-hop citation graph construction with topological reading path."""
    async with ingestion_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        sess, docs = await create_session_with_documents(session_maker, user.id, num_docs=1)
        doc_a = docs[0]  # Depth 0

        async with session_maker() as session:
            # Create Doc B (Depth 1)
            doc_b = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="doc_b.pdf",
                title="Intermediate Architecture B",
                publication_year=2021,
                content_hash="hash_b",
                file_size_bytes=1024,
                status="ready",
                stage="completed",
                progress=100,
            )
            session.add(doc_b)
            await session.flush()

            # Create Doc C (Depth 2 - Foundational Benchmark)
            doc_c = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="doc_c.pdf",
                title="ImageNet Benchmark Dataset",
                publication_year=2009,
                content_hash="hash_c",
                file_size_bytes=1024,
                status="ready",
                stage="completed",
                progress=100,
            )
            session.add(doc_c)
            await session.flush()

            # Doc A cites Doc B (relation: EXTENDS)
            session.add(
                CitationEdgeModel(
                    source_document_id=doc_a.id,
                    target_document_id=doc_b.id,
                    relation="EXTENDS",
                    confidence=0.98,
                )
            )

            # Doc B cites Doc C (relation: BENCHMARKS_ON)
            session.add(
                CitationEdgeModel(
                    source_document_id=doc_b.id,
                    target_document_id=doc_c.id,
                    relation="BENCHMARKS_ON",
                    confidence=0.95,
                )
            )
            await session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(
            f"/api/v1/sessions/{sess.id}/citation-graph",
            headers=headers,
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]

        node_map = {n["id"]: n for n in data["nodes"]}
        assert str(doc_a.id) in node_map
        assert str(doc_b.id) in node_map
        assert str(doc_c.id) in node_map

        assert node_map[str(doc_a.id)]["depth"] == 0
        assert node_map[str(doc_a.id)]["is_session_document"] is True

        assert node_map[str(doc_b.id)]["depth"] == 1
        assert node_map[str(doc_c.id)]["depth"] == 2

        # Check edges
        edge_relations = {(e["source"], e["target"]): e["relation"] for e in data["edges"]}
        assert edge_relations.get((str(doc_a.id), str(doc_b.id))) == "EXTENDS"
        assert edge_relations.get((str(doc_b.id), str(doc_c.id))) == "BENCHMARKS_ON"

        # Check Foundational Reading Path (Topological Ordering: C -> B -> A)
        reading_path = data["reading_path"]
        assert len(reading_path) >= 3
        # Foundational work C must be read before B, and B before A
        assert reading_path.index(str(doc_c.id)) < reading_path.index(str(doc_b.id))
        assert reading_path.index(str(doc_b.id)) < reading_path.index(str(doc_a.id))


@pytest.mark.asyncio
async def test_citation_graph_cycle_breaking() -> None:
    """Graph Cycle Breaking Invariant: Circular citation loops (A -> B -> A) are safely broken."""
    async with ingestion_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        sess, docs = await create_session_with_documents(session_maker, user.id, num_docs=1)
        doc_a = docs[0]

        async with session_maker() as session:
            doc_b = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="doc_b.pdf",
                title="Circular Partner Paper B",
                publication_year=2023,
                content_hash="hash_circ_b",
                file_size_bytes=1024,
                status="ready",
                stage="completed",
                progress=100,
            )
            session.add(doc_b)
            await session.flush()

            # A -> B
            session.add(
                CitationEdgeModel(
                    source_document_id=doc_a.id,
                    target_document_id=doc_b.id,
                    relation="CITES",
                    confidence=1.0,
                )
            )
            # Circular back-edge: B -> A
            session.add(
                CitationEdgeModel(
                    source_document_id=doc_b.id,
                    target_document_id=doc_a.id,
                    relation="CITES",
                    confidence=1.0,
                )
            )
            await session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(
            f"/api/v1/sessions/{sess.id}/citation-graph",
            headers=headers,
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]

        # Circular back-edge B -> A must be broken (avoiding infinite loops)
        edges = [(e["source"], e["target"]) for e in data["edges"]]
        assert (str(doc_a.id), str(doc_b.id)) in edges
        # The back-edge B -> A should have been discarded or broken
        assert (str(doc_b.id), str(doc_a.id)) not in edges

        # Reading path must still contain both documents without crashing
        assert str(doc_a.id) in data["reading_path"]
        assert str(doc_b.id) in data["reading_path"]

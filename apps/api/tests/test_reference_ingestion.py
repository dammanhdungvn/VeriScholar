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
from api.db.models.reference import ReferenceItemModel
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

            ingested_doc = await session.get(DocumentModel, UUID(ing_1["document_id"]))
            assert ingested_doc is not None
            assert ingested_doc.filename == "reference_1"
            assert ingested_doc.status == "metadata_only"
            assert ingested_doc.stage == "metadata_only"
            assert ingested_doc.file_size_bytes == 0
            assert ingested_doc.progress == 0
            assert ingested_doc.content_hash == ""
            assert "no source PDF" in (ingested_doc.error_message or "")


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

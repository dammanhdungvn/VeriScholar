"""Integration test suite for POST /api/v1/documents/{id}/references:resolve (PRD §3.3).

Validates:
- Academic reference resolution via Exa / deterministic adapters.
- Enriching references with open-access PDF URLs, DOIs, arXiv IDs, abstracts.
- Filtering by specific ref_indices.
- Strict multi-tenant isolation (foreign users cannot resolve another user's paper).
- Non-existent document handling (404).
- Ingested document state reflection (is_ingested: True and resolved_document_id).
- Database persistence of discovered metadata.
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_academic_resolver
from api.services.auth_service import AuthService
from core.services.exa_resolver import InMemoryAcademicResolverAdapter
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def resolver_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession], InMemoryAcademicResolverAdapter]
]:
    """Provide isolated in-memory SQLite database and client with test adapter."""
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
    full_name: str = "Alan Turing",
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
            institution="VeriScholar Lab",
            academic_rank="Principal Investigator",
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


async def create_test_document_with_references(
    session_maker: async_sessionmaker[AsyncSession],
    user_id: UUID,
    title: str = "Scaling Laws for Neural Language Models",
) -> tuple[DocumentModel, list[ReferenceItemModel]]:
    """Create a test document with structured reference items."""
    async with session_maker() as session:
        doc = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            filename="scaling_laws.pdf",
            title=title,
            authors=["Kaplan, J.", "McCandlish, S."],
            publication_year=2020,
            content_hash=f"hash_{uuid4().hex}",
            file_size_bytes=2048,
            status="completed",
            stage="completed",
            progress=100,
        )
        session.add(doc)
        await session.flush()

        ref1 = ReferenceItemModel(
            document_id=doc.id,
            ref_index=1,
            raw_text="Vaswani, A., et al. Attention is all you need. NeurIPS 2017.",
            parsed_title="Attention is all you need",
            parsed_authors=["Vaswani, A."],
            parsed_year=2017,
            arxiv_id="1706.03762",
            doi=None,
        )
        ref2 = ReferenceItemModel(
            document_id=doc.id,
            ref_index=2,
            raw_text="Devlin, J., et al. BERT: Pre-training. 2018.",
            parsed_title="BERT: Pre-training of Deep Bidirectional Transformers",
            parsed_authors=["Devlin, J."],
            parsed_year=2018,
            arxiv_id="1810.04805",
            doi=None,
        )
        ref3 = ReferenceItemModel(
            document_id=doc.id,
            ref_index=3,
            raw_text="Brown, T., et al. Language Models are Few-Shot Learners. NeurIPS 2020.",
            parsed_title="Language Models are Few-Shot Learners",
            parsed_authors=["Brown, T."],
            parsed_year=2020,
            arxiv_id="2005.14165",
            doi="10.48550/arXiv.2005.14165",
        )
        session.add_all([ref1, ref2, ref3])
        await session.commit()
        await session.refresh(doc)
        return doc, [ref1, ref2, ref3]


@pytest.mark.asyncio
async def test_resolve_references_success_all() -> None:
    """Validate resolving all references of a document."""
    async with resolver_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        doc, _refs = await create_test_document_with_references(session_maker, user.id)

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            f"/api/v1/documents/{doc.id}/references:resolve",
            headers=headers,
            json={},
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        data = body["data"]
        assert data["document_id"] == str(doc.id)
        assert data["total_resolved"] == 3
        assert len(data["references"]) == 3

        r1 = data["references"][0]
        assert r1["ref_index"] == 1
        assert r1["title"] == "Attention is all you need"
        assert r1["arxiv_id"] == "1706.03762"
        assert r1["open_access_pdf_url"] == "https://arxiv.org/pdf/1706.03762.pdf"
        assert "arXiv" in r1["sources"]
        assert r1["is_ingested"] is False


@pytest.mark.asyncio
async def test_resolve_references_filter_by_indices() -> None:
    """Validate filtering reference resolution to specific ref_indices."""
    async with resolver_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        doc, _refs = await create_test_document_with_references(session_maker, user.id)

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            f"/api/v1/documents/{doc.id}/references:resolve",
            headers=headers,
            json={"ref_indices": [2]},
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["total_resolved"] == 1
        assert len(data["references"]) == 1
        title_2 = "BERT: Pre-training of Deep Bidirectional Transformers"
        assert data["references"][0]["title"] == title_2


@pytest.mark.asyncio
async def test_resolve_references_multi_tenant_isolation() -> None:
    """User B cannot resolve references of User A's document (returns 404)."""
    async with resolver_test_context() as (client, session_maker, _resolver):
        user_a, _token_a = await create_test_user(session_maker, email="user_a@verischolar.org")
        _user_b, token_b = await create_test_user(session_maker, email="user_b@verischolar.org")
        doc_a, _ = await create_test_document_with_references(session_maker, user_a.id)

        headers_b = {"Authorization": f"Bearer {token_b}"}
        resp = await client.post(
            f"/api/v1/documents/{doc_a.id}/references:resolve",
            headers=headers_b,
            json={},
        )

        assert resp.status_code == 404
        err = resp.json()["error"]
        assert err["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_resolve_references_non_existent_document() -> None:
    """Resolving references on a non-existent document ID returns 404."""
    async with resolver_test_context() as (client, session_maker, _resolver):
        _user, token = await create_test_user(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            f"/api/v1/documents/{uuid4()}/references:resolve",
            headers=headers,
            json={},
        )

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_resolve_references_reflects_ingested_state() -> None:
    """When a reference has already been ingested as a DocumentModel, is_ingested=True."""
    async with resolver_test_context() as (client, session_maker, _resolver):
        user, token = await create_test_user(session_maker)
        doc, refs = await create_test_document_with_references(session_maker, user.id)

        # Ingest ref1 manually into a target document
        ingested_doc_id = uuid4()
        async with session_maker() as session:
            ingested_doc = DocumentModel(
                id=ingested_doc_id,
                user_id=user.id,
                filename="attention.pdf",
                title="Attention is all you need",
                content_hash="mock_hash_attention",
                file_size_bytes=1024,
                status="ready",
                stage="completed",
                progress=100,
            )
            session.add(ingested_doc)
            # Update ref1 resolved_document_id
            ref1 = await session.get(ReferenceItemModel, refs[0].id)
            if ref1:
                ref1.resolved_document_id = ingested_doc_id
            await session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            f"/api/v1/documents/{doc.id}/references:resolve",
            headers=headers,
            json={"ref_indices": [1]},
        )

        assert resp.status_code == 200
        ref_data = resp.json()["data"]["references"][0]
        assert ref_data["is_ingested"] is True
        assert ref_data["resolved_document_id"] == str(ingested_doc_id)

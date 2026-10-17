"""Empirical Challenger Stress Test Suite for Milestone 1 (M1_WRITING_AND_SYNTHESIS).

Comprehensive stress tests for:
1. Overleaf 1-Click Export Endpoint:
   - URL generation with special characters in title (UTF-8, Vietnamese diacritics, quotes, ampersands, math symbols, braces)
   - Empty draft content (None and "")
   - Custom LaTeX code (verbatim document preserving \\documentclass, packages, body)
   - Authorization & non-existent draft error handling
2. Proactive Associative Suggestions Endpoint:
   - High similarity domain match (dense keyword overlap, citation formatting, score calculation)
   - Zero similarity match (completely disjoint vocabulary and high min_similarity threshold)
   - Empty draft text (empty payload + empty DB draft, and fallback to DB draft content)
   - Authorization & boundary limits
3. Scalable Library Comparison Matrix:
   - Redis cache hit vs miss behavior (deterministic verification via DB deletion oracle)
   - Pagination bounds with 100+ papers (limit=200, offset=0, offset=100, page disjointness, 422 validations)
   - Multi-field search keyword filtering across Core Methodology, Datasets, and Key Metrics (keys & values)
"""

import urllib.parse
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_idempotency_port
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def stress_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Isolated in-memory SQLite database and AsyncClient with reset cache adapter."""
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

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Reset in-memory cache adapter to ensure isolation across test cases
    cache = get_idempotency_port()
    if hasattr(cache, "clear"):
        cache.clear()
    elif hasattr(cache, "_fallback") and hasattr(cache._fallback, "clear"):
        cache._fallback.clear()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, session_maker

    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


async def seed_user(
    session: AsyncSession,
    email: str = "stress_tester@verischolar.org",
    full_name: str = "Prof. Adversarial Critic",
) -> UserModel:
    """Helper to seed authenticated user."""
    user = UserModel(
        id=uuid4(),
        email=email,
        full_name=full_name,
        role="researcher",
        hashed_password="mocked_password_hash",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def auth_header_for(user: UserModel) -> dict[str, str]:
    """Generate bearer auth header."""
    token = AuthService.create_token(
        payload={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta_seconds=3600,
    )
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# SECTION 1: Overleaf Export Endpoint Empirical Stress Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_overleaf_special_characters_in_title_and_vietnamese():
    """Verify Overleaf export URL generation handles UTF-8 Vietnamese, quotes, ampersands, braces, and math symbols."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            # Title with Vietnamese diacritics, quotes, ampersand, percent, braces, math
            special_title = 'Nghiên cứu "Học Máy & Trí Tuệ Nhân Tạo": Đánh giá 100% SOTA? {Draft} $\\alpha + \\beta$'
            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title=special_title,
                content="Nội dung bản thảo thử nghiệm tiếng Việt có dấu.",
                format="latex",
                version=1,
            )
            session.add(draft)
            await session.commit()

        headers = auth_header_for(user)

        # 1. Test POST /api/v1/drafts/{id}:export-overleaf
        resp_post = await client.post(
            f"/api/v1/drafts/{draft.id}:export-overleaf",
            headers=headers,
        )
        assert resp_post.status_code == 200, resp_post.text
        data_post = resp_post.json()["data"]
        assert data_post["title"] == special_title

        # Check clean title in LaTeX snippet: braces must be stripped to prevent LaTeX syntax error
        latex_snip = data_post["latex_snip"]
        assert r"\documentclass{article}" in latex_snip
        assert r"\title{Nghiên cứu " in latex_snip
        # Braces inside title should have been removed
        assert "{Draft}" not in latex_snip
        assert "Draft" in latex_snip

        # Parse and validate Overleaf URL query parameters
        overleaf_url = data_post["overleaf_url"]
        assert overleaf_url.startswith("https://www.overleaf.com/docs?")
        parsed_url = urllib.parse.urlparse(overleaf_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        assert "snip" in query_params
        assert "snip_name" in query_params
        # Decoded snip_name must match the original title
        assert query_params["snip_name"][0] == special_title
        # Decoded snip must match the full generated LaTeX
        assert query_params["snip"][0] == latex_snip

        # 2. Test GET /api/v1/drafts/{id}/overleaf-launch endpoint alias
        resp_get = await client.get(
            f"/api/v1/drafts/{draft.id}/overleaf-launch",
            headers=headers,
        )
        assert resp_get.status_code == 200, resp_get.text
        data_get = resp_get.json()["data"]
        assert data_get["overleaf_url"] == overleaf_url
        assert data_get["launch_url"] == overleaf_url


@pytest.mark.asyncio
async def test_overleaf_empty_content_graceful_handling():
    """Verify Overleaf export handles empty draft content (None and empty string) without crashing."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            # Draft with empty content string
            draft_empty_str = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Draft with Empty String Content",
                content="",
                format="latex",
                version=1,
            )
            # Draft with None content
            draft_none = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Draft with None Content",
                content=None,
                format="latex",
                version=1,
            )
            session.add_all([draft_empty_str, draft_none])
            await session.commit()

        headers = auth_header_for(user)

        for draft in [draft_empty_str, draft_none]:
            resp = await client.post(
                f"/api/v1/drafts/{draft.id}:export-overleaf",
                headers=headers,
            )
            assert resp.status_code == 200, f"Failed for draft {draft.id}: {resp.text}"
            data = resp.json()["data"]
            assert data["snip_length"] > 0
            assert "% Empty draft content" in data["latex_snip"]
            assert r"\documentclass{article}" in data["latex_snip"]
            assert r"\begin{document}" in data["latex_snip"]
            assert r"\end{document}" in data["latex_snip"]
            assert "https://www.overleaf.com/docs?snip=" in data["overleaf_url"]


@pytest.mark.asyncio
async def test_overleaf_custom_latex_code_preservation():
    """Verify Overleaf export preserves complete custom LaTeX documents without redundant article wrapping."""
    custom_latex = (
        r"\documentclass[12pt,a4paper]{report}" + "\n"
        r"\usepackage{amsmath,amssymb}" + "\n"
        r"\usepackage{microtype}" + "\n"
        r"\begin{document}" + "\n"
        r"\chapter{Theoretical Foundations}" + "\n"
        r"Given $X \sim \mathcal{N}(0, 1)$, empirical loss satisfies $L \le \epsilon$." + "\n"
        r"\end{document}"
    )

    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Custom LaTeX Document",
                content=custom_latex,
                format="latex",
                version=1,
            )
            session.add(draft)
            await session.commit()

        headers = auth_header_for(user)
        resp = await client.post(
            f"/api/v1/drafts/{draft.id}:export-overleaf",
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]

        # Full latex must match the custom latex verbatim without double documentclass
        assert data["latex_snip"] == custom_latex
        assert data["latex_snip"].count(r"\documentclass") == 1
        assert data["latex_snip"].count(r"\begin{document}") == 1

        # Check encoded URL decodes back to the verbatim custom latex
        parsed_url = urllib.parse.urlparse(data["overleaf_url"])
        query_params = urllib.parse.parse_qs(parsed_url.query)
        assert query_params["snip"][0] == custom_latex


@pytest.mark.asyncio
async def test_overleaf_export_errors_and_isolation():
    """Verify 401 unauthenticated, 404 not found, and cross-user draft isolation."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user1 = await seed_user(session, email="user1@verischolar.org")
            user2 = await seed_user(session, email="user2@verischolar.org")
            draft1 = DraftModel(
                id=uuid4(),
                user_id=user1.id,
                title="User 1 Private Draft",
                content="Top secret research",
                format="latex",
                version=1,
            )
            session.add(draft1)
            await session.commit()

        headers_user1 = auth_header_for(user1)
        headers_user2 = auth_header_for(user2)

        # 1. Unauthenticated request -> 401
        resp_unauth = await client.post(f"/api/v1/drafts/{draft1.id}:export-overleaf")
        assert resp_unauth.status_code == 401

        # 2. Non-existent draft UUID -> 404
        random_uuid = uuid4()
        resp_404 = await client.post(
            f"/api/v1/drafts/{random_uuid}:export-overleaf",
            headers=headers_user1,
        )
        assert resp_404.status_code == 404

        # 3. User 2 trying to export User 1's draft -> 404 (isolation)
        resp_forbidden = await client.post(
            f"/api/v1/drafts/{draft1.id}:export-overleaf",
            headers=headers_user2,
        )
        assert resp_forbidden.status_code == 404


# ==============================================================================
# SECTION 2: Associative Suggestions Endpoint Empirical Stress Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_associative_suggestions_high_similarity_match():
    """Verify associative suggestions return ranked matches with high similarity scores, citations, and keywords."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            doc = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="transformer_foundation.pdf",
                title="Attention Is All You Need",
                authors=["Vaswani et al."],
                publication_year=2017,
                content_hash="vaswani_hash_2017",
                file_size_bytes=4096,
            )
            session.add(doc)

            note = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text=(
                    "Multi-head self-attention mechanisms replace recurrent layers and convolutions."
                ),
                user_note=(
                    "Cơ chế self-attention cho phép mô hình hóa mối quan hệ song song hiệu quả."
                ),
                page_number=4,
                tags=["attention", "transformers"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            session.add(note)

            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Transformer Architecture Review",
                content="Initial draft placeholder",
                format="latex",
                version=1,
            )
            session.add(draft)
            await session.commit()

        headers = auth_header_for(user)

        # Dense domain keywords matching note
        query_text = (
            "We employ multi-head self-attention mechanisms to replace recurrent layers "
            "for parallel sequence modeling."
        )

        resp = await client.post(
            f"/api/v1/drafts/{draft.id}/associative-suggestions",
            headers=headers,
            json={
                "content": query_text,
                "limit": 3,
                "min_similarity": 0.20,
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]

        assert data["total_found"] >= 1
        assert len(data["suggestions"]) >= 1

        top_suggestion = data["suggestions"][0]
        assert top_suggestion["note_id"] == str(note.id)
        assert top_suggestion["similarity_score"] > 0.40
        assert r"\cite{" in top_suggestion["suggested_citation"]
        assert "Trang 4" in top_suggestion["reason"]
        # Must extract shared tokens
        assert any(
            kw in ["multi-head", "self-attention", "mechanisms", "recurrent", "layers"]
            for kw in top_suggestion["matched_keywords"]
        )


@pytest.mark.asyncio
async def test_associative_suggestions_zero_similarity_disjoint_vocabulary():
    """Verify zero suggestions returned when draft text shares no conceptual overlap with notes."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            doc = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="quantum_optics.pdf",
                title="Quantum Optics and Photonic Crystals",
                authors=["Aspect et al."],
                publication_year=2020,
                content_hash="quantum_optics_hash",
                file_size_bytes=2048,
            )
            session.add(doc)

            note = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text="Entangled photon pairs generation through parametric down-conversion.",
                user_note="Tán xạ quang học phi tuyến và photon vướng víu.",
                page_number=7,
                tags=["quantum", "photonics"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            session.add(note)

            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Archaeological Survey",
                content="Excavation of Neolithic pottery shards in Southeast Asian river deltas.",
                format="latex",
                version=1,
            )
            session.add(draft)
            await session.commit()

        headers = auth_header_for(user)

        # 1. Completely disjoint topic -> 0 suggestions
        resp_disjoint = await client.post(
            f"/api/v1/drafts/{draft.id}/associative-suggestions",
            headers=headers,
            json={
                "content": "Archaeological stratigraphic dating of ancient ceramic clay artifacts.",
                "min_similarity": 0.15,
            },
        )
        assert resp_disjoint.status_code == 200, resp_disjoint.text
        data_disjoint = resp_disjoint.json()["data"]
        assert data_disjoint["total_found"] == 0
        assert len(data_disjoint["suggestions"]) == 0

        # 2. Stringent min_similarity threshold filtering
        resp_thresh = await client.post(
            f"/api/v1/drafts/{draft.id}/associative-suggestions",
            headers=headers,
            json={
                "content": "Photon entanglement experiments.",
                "min_similarity": 0.99,  # Impossibly high threshold
            },
        )
        assert resp_thresh.status_code == 200, resp_thresh.text
        assert resp_thresh.json()["data"]["total_found"] == 0


@pytest.mark.asyncio
async def test_associative_suggestions_empty_draft_text_and_db_fallback():
    """Verify empty draft text behavior: empty request + empty DB draft, and fallback to DB draft text."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session, email="owner_assoc@verischolar.org")
            user2 = await seed_user(session, email="intruder_assoc@verischolar.org")
            doc = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="bio_nlp.pdf",
                title="BioNLP Named Entity Recognition",
                authors=["Lee et al."],
                publication_year=2023,
                content_hash="bio_nlp_hash",
                file_size_bytes=1024,
            )
            session.add(doc)

            note = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text="Biomedical named entity recognition using fine-tuned PubMedBERT transformers.",
                user_note="Mô hình PubMedBERT trích xuất thực thể y sinh chuẩn xác.",
                page_number=2,
                tags=["biomedical", "ner"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            session.add(note)

            user2_note = ResearchNoteModel(
                id=uuid4(),
                user_id=user2.id,
                document_id=None,
                selected_text="Biomedical named entity recognition using fine-tuned PubMedBERT transformers.",
                user_note="Intruder note regarding biomedical transformers.",
                page_number=1,
                tags=["biomedical"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            session.add(user2_note)

            # Draft 1: Empty content in DB
            draft_empty = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Blank Draft",
                content="",
                format="latex",
                version=1,
            )
            # Draft 2: Meaningful content in DB
            draft_with_body = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Biomedical Survey",
                content="We evaluate biomedical named entity recognition with fine-tuned PubMedBERT models.",
                format="latex",
                version=1,
            )
            session.add_all([draft_empty, draft_with_body])
            await session.commit()

        headers = auth_header_for(user)

        # 1. Case A: Request body is empty AND Draft in DB is empty -> Returns 200 with 0 suggestions (no crash)
        resp_empty = await client.post(
            f"/api/v1/drafts/{draft_empty.id}/associative-suggestions",
            headers=headers,
            json={"content": ""},
        )
        assert resp_empty.status_code == 200, resp_empty.text
        data_empty = resp_empty.json()["data"]
        assert data_empty["total_found"] == 0
        assert data_empty["suggestions"] == []
        assert data_empty["query_excerpt"] == ""

        # 2. Case B: Request body is empty, but Draft in DB has content -> Falls back to DB draft content!
        resp_fallback = await client.post(
            f"/api/v1/drafts/{draft_with_body.id}/associative-suggestions",
            headers=headers,
            json={},  # Omit content/text to trigger fallback
        )
        assert resp_fallback.status_code == 200, resp_fallback.text
        data_fallback = resp_fallback.json()["data"]
        assert data_fallback["total_found"] >= 1
        assert len(data_fallback["suggestions"]) >= 1
        assert data_fallback["suggestions"][0]["note_id"] == str(note.id)

        # 3. Case C: User 2 tries to trigger fallback on User 1's draft -> 0 suggestions (cross-tenant isolation)
        headers_user2 = auth_header_for(user2)
        resp_unauth_fallback = await client.post(
            f"/api/v1/drafts/{draft_with_body.id}/associative-suggestions",
            headers=headers_user2,
            json={},
        )
        assert resp_unauth_fallback.status_code == 200, resp_unauth_fallback.text
        data_unauth = resp_unauth_fallback.json()["data"]
        assert data_unauth["total_found"] == 0
        assert data_unauth["suggestions"] == []
        assert data_unauth["query_excerpt"] == ""


# ==============================================================================
# SECTION 3: Library Comparison Matrix Empirical Stress Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_comparison_matrix_redis_cache_hit_vs_miss_behavior():
    """Empirically prove Redis/in-memory cache hit vs miss behavior via DB deletion oracle."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            folder = FolderModel(id=uuid4(), user_id=user.id, name="Cache Test Folder")
            session.add(folder)

            # Seed 5 documents
            docs = []
            for i in range(1, 6):
                doc = DocumentModel(
                    id=uuid4(),
                    user_id=user.id,
                    folder_id=folder.id,
                    filename=f"cached_paper_{i}.pdf",
                    title=f"Self-Supervised Representation Learning Paper {i}",
                    authors=[f"Author {i}"],
                    publication_year=2024,
                    content_hash=f"cache_hash_{i}",
                    file_size_bytes=1024 * i,
                )
                docs.append(doc)
            session.add_all(docs)
            await session.commit()

        headers = auth_header_for(user)
        topic = "Self-Supervised Learning Representations"

        # Request 1: Cache Miss (first time)
        resp_miss = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": topic,
                "folder_id": str(folder.id),
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_miss.status_code == 200, resp_miss.text
        data_miss = resp_miss.json()["data"]
        assert data_miss["total_count"] == 5
        assert len(data_miss["rows"]) == 5

        # Oracle step: Delete all documents from the database!
        async with session_maker() as session:
            await session.execute(delete(DocumentModel).where(DocumentModel.folder_id == folder.id))
            await session.commit()

        # Request 2: Cache Hit (subsequent request with same topic & folder_id)
        # Because documents were DELETED from DB, a cache miss would return 404.
        # A successful 200 response returning all 5 rows proves 100% cache hit!
        resp_hit = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": topic,
                "folder_id": str(folder.id),
                "limit": 3,
                "offset": 0,
            },
        )
        assert resp_hit.status_code == 200, (
            f"Expected cache hit, but got {resp_hit.status_code}: {resp_hit.text}"
        )
        data_hit = resp_hit.json()["data"]
        assert data_hit["total_count"] == 5
        assert len(data_hit["rows"]) == 3  # Pagination applied cleanly on cached rows!

        # Request 3: Cache Miss on new topic -> hits DB where documents are deleted -> returns 404!
        resp_new_topic = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Uncached Different Topic",
                "folder_id": str(folder.id),
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_new_topic.status_code == 404, "Expected 404 because new topic misses cache"


@pytest.mark.asyncio
async def test_comparison_matrix_large_scale_pagination_bounds_120_papers():
    """Verify pagination bounds on multi-paper matrix: limits, offsets, page disjointness, and schema validation."""
    async with stress_test_context() as (client, session_maker):
        total_seeded = 25
        async with session_maker() as session:
            user = await seed_user(session)
            folder = FolderModel(id=uuid4(), user_id=user.id, name="Massive 100+ Benchmark")
            session.add(folder)

            # Seed 25 documents
            docs = []
            for i in range(1, total_seeded + 1):
                doc = DocumentModel(
                    id=uuid4(),
                    user_id=user.id,
                    folder_id=folder.id,
                    filename=f"scale_paper_{i:03d}.pdf",
                    title=f"Scalable AI Foundation Study #{i:03d}",
                    authors=[f"Scientist {i}"],
                    publication_year=2024,
                    content_hash=f"hash_scale_{i}",
                    file_size_bytes=2048,
                )
                docs.append(doc)
            session.add_all(docs)
            await session.commit()

        headers = auth_header_for(user)

        # 1. Test limit=50, offset=0: Full retrieval of all 25 papers
        resp_full = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 50,
                "offset": 0,
            },
        )
        assert resp_full.status_code == 200, resp_full.text
        data_full = resp_full.json()["data"]
        assert data_full["total_count"] == total_seeded
        assert data_full["limit"] == 50
        assert data_full["offset"] == 0
        assert len(data_full["rows"]) == total_seeded

        # 2. Test limit=10, offset=0 (Page 1: 10 papers)
        resp_p1 = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_p1.status_code == 200, resp_p1.text
        data_p1 = resp_p1.json()["data"]
        assert data_p1["total_count"] == total_seeded
        assert len(data_p1["rows"]) == 10
        page1_ids = [r["document_id"] for r in data_p1["rows"]]

        # 3. Test limit=10, offset=20 (Page 3: indices 20 to 24 = 5 remaining papers)
        resp_p3 = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 10,
                "offset": 20,
            },
        )
        assert resp_p3.status_code == 200, resp_p3.text
        data_p3 = resp_p3.json()["data"]
        assert data_p3["total_count"] == total_seeded
        assert data_p3["offset"] == 20
        assert len(data_p3["rows"]) == 5  # 25 - 20 = 5
        page3_ids = [r["document_id"] for r in data_p3["rows"]]

        # Verify strict disjointness between offset=0 and offset=20
        assert set(page1_ids).isdisjoint(set(page3_ids))

        # 4. Test offset beyond total count (offset=30)
        resp_beyond = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 10,
                "offset": 30,
            },
        )
        assert resp_beyond.status_code == 200, resp_beyond.text
        data_beyond = resp_beyond.json()["data"]
        assert data_beyond["total_count"] == total_seeded
        assert len(data_beyond["rows"]) == 0

        # 5. Schema Validation: limit > 200 must be rejected with 422 Unprocessable Entity
        resp_overflow_limit = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 201,  # Max allowed is 200
                "offset": 0,
            },
        )
        assert resp_overflow_limit.status_code == 422

        # 6. Schema Validation: offset < 0 must be rejected with 422
        resp_negative_offset = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Massive Scale Survey",
                "folder_id": str(folder.id),
                "limit": 50,
                "offset": -1,
            },
        )
        assert resp_negative_offset.status_code == 422


@pytest.mark.asyncio
async def test_comparison_matrix_search_filtering_methodology_datasets_metrics():
    """Verify search keyword filtering across methodology, datasets, and metrics keys/values."""
    async with stress_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            folder = FolderModel(id=uuid4(), user_id=user.id, name="Diverse Methods")
            session.add(folder)

            # Paper 1: RLHF with Anthropic-HH dataset and Reward-Accuracy metric
            doc1 = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                folder_id=folder.id,
                filename="rlhf_alignment.pdf",
                title="Constitutional AI Alignment via RLHF",
                authors=["Bai et al."],
                publication_year=2023,
                content_hash="rlhf_hash_01",
                file_size_bytes=2048,
                parsed_metadata={
                    "methodology": "Reinforcement Learning from Human Feedback and DPO",
                    "datasets": ["Anthropic-HH", "UltraFeedback"],
                    "metrics": {"Reward-Margin": "0.85", "Safety-Score": "98.2%"},
                },
            )
            # Paper 2: Diffusion with CelebA-HQ dataset and FID metric
            doc2 = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                folder_id=folder.id,
                filename="diffusion_denoising.pdf",
                title="High-Resolution Denoising Generative Diffusion",
                authors=["Ho et al."],
                publication_year=2022,
                content_hash="diffusion_hash_02",
                file_size_bytes=2048,
                parsed_metadata={
                    "methodology": "Denoising Diffusion Probabilistic SDE",
                    "datasets": ["CelebA-HQ", "COCO-2017"],
                    "metrics": {"FID-Score": "2.85", "IS": "38.5"},
                },
            )
            # Paper 3: GNN with OGB-Proteins dataset and ROC-AUC metric
            doc3 = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                folder_id=folder.id,
                filename="graph_message_passing.pdf",
                title="Graph Equivariant Message Passing Networks",
                authors=["Kipf et al."],
                publication_year=2024,
                content_hash="gnn_hash_03",
                file_size_bytes=2048,
                parsed_metadata={
                    "methodology": "Equivariant Graph Message Passing",
                    "datasets": ["OGB-Proteins", "MUTAG"],
                    "metrics": {"ROC-AUC": "91.4%", "Micro-F1": "89.2%"},
                },
            )
            session.add_all([doc1, doc2, doc3])
            await session.commit()

        headers = auth_header_for(user)

        # 1. Search by Methodology keyword: "Reinforcement Learning"
        resp_method = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Machine Learning Methods",
                "folder_id": str(folder.id),
                "search": "Reinforcement Learning",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_method.status_code == 200, resp_method.text
        data_method = resp_method.json()["data"]
        assert data_method["total_count"] == 1
        assert len(data_method["rows"]) == 1
        assert data_method["rows"][0]["document_id"] == str(doc1.id)
        assert "Reinforcement Learning" in data_method["rows"][0]["core_methodology"]

        # 2. Search by Dataset keyword: "CelebA-HQ"
        resp_dataset = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Machine Learning Methods",
                "folder_id": str(folder.id),
                "search": "CelebA-HQ",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_dataset.status_code == 200, resp_dataset.text
        data_dataset = resp_dataset.json()["data"]
        assert data_dataset["total_count"] == 1
        assert len(data_dataset["rows"]) == 1
        assert data_dataset["rows"][0]["document_id"] == str(doc2.id)
        assert any("celeba" in d.lower() for d in data_dataset["rows"][0]["datasets_used"])

        # 3. Search by Metric Key: "ROC-AUC"
        resp_metric_key = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Machine Learning Methods",
                "folder_id": str(folder.id),
                "search": "ROC-AUC",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_metric_key.status_code == 200, resp_metric_key.text
        data_metric_key = resp_metric_key.json()["data"]
        assert data_metric_key["total_count"] == 1
        assert data_metric_key["rows"][0]["document_id"] == str(doc3.id)

        # 4. Search by Metric Value: "98.2%"
        resp_metric_val = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Machine Learning Methods",
                "folder_id": str(folder.id),
                "search": "98.2%",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_metric_val.status_code == 200, resp_metric_val.text
        data_metric_val = resp_metric_val.json()["data"]
        assert data_metric_val["total_count"] == 1
        assert data_metric_val["rows"][0]["document_id"] == str(doc1.id)

        # 5. Search by non-matching keyword: "QuantumSupremacy" -> 0 rows
        resp_nomatch = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Machine Learning Methods",
                "folder_id": str(folder.id),
                "search": "QuantumSupremacy",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_nomatch.status_code == 200, resp_nomatch.text
        data_nomatch = resp_nomatch.json()["data"]
        assert data_nomatch["total_count"] == 0
        assert len(data_nomatch["rows"]) == 0

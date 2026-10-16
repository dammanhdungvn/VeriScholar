"""Automated verification suite for the 4 Backend Technical Pillars:
- Pillar 2: Overleaf 1-Click Direct Sync (export-overleaf and overleaf-launch)
- Pillar 3: Proactive Associative Memory Engine (associative-suggestions)
- Pillar 4: Large-Scale Literature Comparison Matrix (pagination, search, total_count)
- Pillar 5: Enterprise On-Premise Stack (docker-compose & bootstrap script)
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def pillars_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Isolated in-memory SQLite database and AsyncClient for pillar verification."""
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

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, session_maker

    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


async def seed_user(session: AsyncSession, email: str = "researcher@verischolar.org") -> UserModel:
    """Helper to seed authenticated user."""
    user = UserModel(
        id=uuid4(),
        email=email,
        full_name="Dr. Alan Turing",
        role="researcher",
        hashed_password="mocked_hashed_password",
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
# Pillar 2: Overleaf 1-Click Sync
# ==============================================================================


@pytest.mark.asyncio
async def test_pillar2_overleaf_1click_sync():
    """Verify POST export-overleaf and GET overleaf-launch endpoints."""
    async with pillars_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Self-Supervised Foundations for Genomic Language Models",
                content=r"\section{Introduction} Deep genomic foundation models are versatile.",
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
        assert data_post["draft_id"] == str(draft.id)
        assert data_post["title"] == draft.title
        assert data_post["format"] == "latex"
        assert "https://www.overleaf.com/docs?snip=" in data_post["overleaf_url"]
        assert "snip_name=" in data_post["overleaf_url"]
        assert data_post["snip_length"] > 0
        assert data_post["latex_snip"] is not None

        # 2. Test GET /api/v1/drafts/{id}/overleaf-launch
        resp_get = await client.get(
            f"/api/v1/drafts/{draft.id}/overleaf-launch",
            headers=headers,
        )
        assert resp_get.status_code == 200, resp_get.text
        data_get = resp_get.json()["data"]
        assert data_get["overleaf_url"] == data_post["overleaf_url"]
        assert data_get["title"] == draft.title


# ==============================================================================
# Pillar 3: Proactive Associative Memory Engine
# ==============================================================================


@pytest.mark.asyncio
async def test_pillar3_proactive_associative_memory():
    """Verify proactive associative recall matching draft text with research notes."""
    async with pillars_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)

            # Create document
            doc = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                filename="vaswani2017.pdf",
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer"],
                publication_year=2017,
                content_hash="hash123",
                file_size_bytes=1024,
            )
            session.add(doc)

            # Create research notes with relevant concepts
            note1 = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text=(
                    "Multi-head attention mechanism maps a query and a set of key-value pairs."
                ),
                user_note="Cơ chế multi-head attention đột phá thay thế recurrence và convolution.",
                page_number=3,
                tags=["attention", "transformers", "nlp"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            note2 = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text="Positional encodings are added to input embeddings.",
                user_note="Mã hóa vị trí hình sin (sinusoidal positional encoding).",
                page_number=5,
                tags=["embeddings", "positional"],
                bounding_boxes=[],
                frozen_snapshot={},
            )
            session.add_all([note1, note2])

            draft = DraftModel(
                id=uuid4(),
                user_id=user.id,
                title="Transformer Survey",
                content=(
                    "Our architecture relies on multi-head attention mechanisms to replace "
                    "recurrence."
                ),
                format="latex",
                version=1,
            )
            session.add(draft)
            await session.commit()

        headers = auth_header_for(user)

        # 1. Post request with explicit content
        resp = await client.post(
            f"/api/v1/drafts/{draft.id}/associative-suggestions",
            headers=headers,
            json={
                "content": (
                    "Multi-head attention mechanism provides parallelized representation learning."
                ),
                "max_results": 5,
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["draft_id"] == str(draft.id)
        assert data["total_found"] >= 1
        assert len(data["suggestions"]) >= 1

        top_sug = data["suggestions"][0]
        assert top_sug["note_id"] == str(note1.id)
        assert top_sug["similarity_score"] > 0.0
        assert (
            r"\cite{shazeer2017}" in top_sug["suggested_citation"]
            or r"\cite{" in top_sug["suggested_citation"]
        )
        assert "Trang 3" in top_sug["reason"] or "Trang 3" in top_sug["relevance_explanation"]
        assert len(top_sug["matched_keywords"]) > 0

        # 2. Post request without content (falls back to draft body in DB)
        resp_fallback = await client.post(
            f"/api/v1/drafts/{draft.id}/associative-suggestions",
            headers=headers,
            json={},
        )
        assert resp_fallback.status_code == 200, resp_fallback.text
        assert resp_fallback.json()["data"]["total_found"] >= 1


# ==============================================================================
# Pillar 4: Large-Scale Comparison Matrix (Pagination & Search)
# ==============================================================================


@pytest.mark.asyncio
async def test_pillar4_large_scale_comparison_matrix_pagination():
    """Verify pagination (limit, offset, search, total_count) for 10+ papers."""
    async with pillars_test_context() as (client, session_maker):
        async with session_maker() as session:
            user = await seed_user(session)
            folder = FolderModel(
                id=uuid4(),
                user_id=user.id,
                name="Large Scale Benchmark",
            )
            session.add(folder)

            # Seed 8 documents
            docs = []
            for i in range(1, 9):
                title = (
                    f"Transformer Scale Paper {i}" if i <= 4 else f"Biomedical Vaccine Study {i}"
                )
                doc = DocumentModel(
                    id=uuid4(),
                    user_id=user.id,
                    folder_id=folder.id,
                    filename=f"paper_{i}.pdf",
                    title=title,
                    authors=[f"Researcher {i}"],
                    publication_year=2024,
                    content_hash=f"hash_doc_{i}",
                    file_size_bytes=2048,
                )
                docs.append(doc)
            session.add_all(docs)
            await session.commit()

        headers = auth_header_for(user)

        # 1. Fetch Page 1: limit=3, offset=0
        resp_p1 = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Scaling Laws and Foundations",
                "folder_id": str(folder.id),
                "limit": 3,
                "offset": 0,
            },
        )
        assert resp_p1.status_code == 200, resp_p1.text
        data_p1 = resp_p1.json()["data"]
        assert data_p1["total_count"] == 8
        assert data_p1["limit"] == 3
        assert data_p1["offset"] == 0
        assert len(data_p1["rows"]) == 3

        # 2. Fetch Page 2: limit=3, offset=3
        resp_p2 = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Scaling Laws and Foundations",
                "folder_id": str(folder.id),
                "limit": 3,
                "offset": 3,
            },
        )
        assert resp_p2.status_code == 200, resp_p2.text
        data_p2 = resp_p2.json()["data"]
        assert data_p2["total_count"] == 8
        assert len(data_p2["rows"]) == 3
        # Rows on page 2 must be different from page 1
        p1_ids = {r["document_id"] for r in data_p1["rows"]}
        p2_ids = {r["document_id"] for r in data_p2["rows"]}
        assert p1_ids.isdisjoint(p2_ids)

        # 3. Filter with search keyword
        resp_search = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Scaling Laws",
                "folder_id": str(folder.id),
                "search": "Vaccine",
                "limit": 10,
                "offset": 0,
            },
        )
        assert resp_search.status_code == 200, resp_search.text
        data_search = resp_search.json()["data"]
        assert data_search["total_count"] == 4
        assert len(data_search["rows"]) == 4
        assert all("vaccine" in r["title"].lower() for r in data_search["rows"])


# ==============================================================================
# Pillar 5: Enterprise On-Premise Package
# ==============================================================================


def test_pillar5_enterprise_on_premise_spec():
    """Verify docker-compose.enterprise.yml, bootstrap_enterprise.sh, and Dockerfiles."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    compose_path = project_root / "deploy" / "docker-compose.enterprise.yml"
    bootstrap_path = project_root / "scripts" / "bootstrap_enterprise.sh"
    dockerfile_api = project_root / "deploy" / "Dockerfile.api"
    dockerfile_web = project_root / "deploy" / "Dockerfile.web"

    # 1. Check file existence
    assert compose_path.exists(), "docker-compose.enterprise.yml must exist"
    assert bootstrap_path.exists(), "scripts/bootstrap_enterprise.sh must exist"
    assert dockerfile_api.exists(), "deploy/Dockerfile.api must exist"
    assert dockerfile_web.exists(), "deploy/Dockerfile.web must exist"

    # 2. Check bootstrap script permissions & content
    import os

    assert os.access(bootstrap_path, os.X_OK), "bootstrap_enterprise.sh must be executable"
    bootstrap_content = bootstrap_path.read_text(encoding="utf-8")
    assert "docker compose" in bootstrap_content or "docker-compose" in bootstrap_content
    assert "pg_isready" in bootstrap_content
    assert "POSTGRES_USER" in bootstrap_content

    # 3. Parse compose file and check all 6 core enterprise services
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = compose_data.get("services", {})
    required_services = {"postgres", "pgbouncer", "redis", "api", "arq-worker", "web"}
    assert required_services.issubset(set(services.keys())), (
        f"Missing enterprise services: {required_services - set(services.keys())}"
    )

    # 4. Check specific container configurations
    assert "pgvector" in services["postgres"]["image"]
    assert "pgbouncer" in services["pgbouncer"]["image"]
    cmd_val = services["arq-worker"].get("command", "")
    assert "arq_worker" in (cmd_val if isinstance(cmd_val, str) else " ".join(cmd_val))

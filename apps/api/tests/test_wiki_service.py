"""Unit and integration tests for WikiService persistence layer."""

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.user import UserModel
from api.services.wiki_service import WikiService
from core.models.wiki import WikiPageDraft
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def wiki_user(db_session: AsyncSession) -> UserModel:
    """Create and flush a test user for wiki testing."""
    user = UserModel(
        id=uuid4(),
        email=f"wiki_scholar_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="GS. Wiki Học Thuật",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> UserModel:
    """Create and flush another test user to verify tenant isolation."""
    user = UserModel(
        id=uuid4(),
        email=f"other_scholar_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="TS. Người Dùng Khác",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_wiki_service_upsert_and_get_page(
    db_session: AsyncSession,
    wiki_user: UserModel,
):
    """Verify upserting a new page and fetching it by slug."""
    service = WikiService(db=db_session)

    # 1. Upsert a new page
    created = await service.upsert_page(
        user_id=wiki_user.id,
        title="Scaled Dot-Product Attention",
        markdown="# Scaled Dot-Product Attention\nComputes softmax(QK^T / sqrt(d_k))V.",
        yaml_metadata={"tags": ["attention", "transformer"]},
        wikilinks=["Transformer", "Multi-Head Attention"],
        page_type="method",
    )
    assert created.id is not None
    assert created.slug == "scaled-dot-product-attention"
    assert created.title == "Scaled Dot-Product Attention"
    assert created.user_id == wiki_user.id
    assert created.page_type == "method"

    # 2. Retrieve by slug
    fetched = await service.get_page_by_slug(
        user_id=wiki_user.id, slug="scaled-dot-product-attention"
    )
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Scaled Dot-Product Attention"
    assert "softmax" in fetched.markdown_content
    assert fetched.wikilinks == ["Transformer", "Multi-Head Attention"]

    # 3. Upsert existing page (update in-place)
    updated = await service.upsert_page(
        user_id=wiki_user.id,
        title="Scaled Dot-Product Attention (Updated)",
        markdown="# Scaled Dot-Product Attention\nUpdated content with quadratic complexity.",
        yaml_metadata={"tags": ["attention", "efficiency"]},
        wikilinks=["Transformer", "FlashAttention"],
        slug="scaled-dot-product-attention",
    )
    assert updated.id == created.id
    assert updated.title == "Scaled Dot-Product Attention (Updated)"
    assert "FlashAttention" in updated.wikilinks

    # 4. Confirm updated page in database
    refetched = await service.get_page_by_slug(
        user_id=wiki_user.id, slug="scaled-dot-product-attention"
    )
    assert refetched is not None
    assert refetched.title == "Scaled Dot-Product Attention (Updated)"
    assert refetched.wikilinks == ["Transformer", "FlashAttention"]


@pytest.mark.asyncio
async def test_wiki_service_save_page_from_draft(
    db_session: AsyncSession,
    wiki_user: UserModel,
):
    """Verify compiling and persisting a WikiPageDraft domain model."""
    service = WikiService(db=db_session)

    draft = WikiPageDraft(
        title="FlashAttention Optimization",
        summary="Exact attention with IO-awareness tiling.",
        key_insights=[
            "Splits inputs into blocks to fit fast SRAM.",
            "Avoids materializing N x N attention matrix.",
        ],
        related_entities=["GPU SRAM", "Scaled Dot-Product Attention", "Tiling"],
        source_papers=["Dao et al., 2022"],
        tags=["optimization", "cuda"],
    )

    page = await service.save_page(user_id=wiki_user.id, draft=draft)

    assert page.id is not None
    assert page.slug == "flashattention-optimization"
    assert "[[GPU SRAM]]" in page.markdown_content
    assert "[[Tiling]]" in page.markdown_content
    assert "GPU SRAM" in page.wikilinks
    assert page.yaml_metadata.get("tags") == ["optimization", "cuda"]

    # Retrieve and verify
    fetched = await service.get_page_by_slug(
        user_id=wiki_user.id, slug="flashattention-optimization"
    )
    assert fetched is not None
    assert fetched.id == page.id


@pytest.mark.asyncio
async def test_wiki_service_list_pages_and_multi_tenancy(
    db_session: AsyncSession,
    wiki_user: UserModel,
    other_user: UserModel,
):
    """Verify list_pages pagination and strict tenant isolation."""
    service = WikiService(db=db_session)

    # Create 3 pages for wiki_user
    for i in range(3):
        await service.upsert_page(
            user_id=wiki_user.id,
            title=f"Concept {i}",
            markdown=f"# Concept {i}\nBody text",
            slug=f"concept-{i}",
        )

    # Create 1 page for other_user with identical slug to verify multi-tenant unique constraint
    other_page = await service.upsert_page(
        user_id=other_user.id,
        title="Concept 0 (Other)",
        markdown="# Concept 0 from other user",
        slug="concept-0",
    )
    assert other_page.id is not None

    # List pages for wiki_user
    user_pages = await service.list_pages(user_id=wiki_user.id)
    assert len(user_pages) == 3
    slugs = [p.slug for p in user_pages]
    assert "concept-0" in slugs
    assert "concept-1" in slugs
    assert "concept-2" in slugs

    # List pages for other_user
    other_pages = await service.list_pages(user_id=other_user.id)
    assert len(other_pages) == 1
    assert other_pages[0].title == "Concept 0 (Other)"

    # Pagination test
    paged = await service.list_pages(user_id=wiki_user.id, limit=2, offset=0)
    assert len(paged) == 2

    # Cross-tenant get_page_by_slug isolation
    fetched = await service.get_page_by_slug(user_id=other_user.id, slug="concept-1")
    assert fetched is None

    # Unknown slug
    unknown = await service.get_page_by_slug(user_id=wiki_user.id, slug="non-existent")
    assert unknown is None


@pytest.mark.asyncio
async def test_wiki_service_flexible_db_argument(
    db_session: AsyncSession,
    wiki_user: UserModel,
):
    """Verify WikiService methods accept db as first parameter when uninitialized."""
    stateless_service = WikiService()

    # Pass db as first argument
    page = await stateless_service.upsert_page(
        db_session,
        wiki_user.id,
        title="Stateless Test",
        markdown="# Stateless",
        slug="stateless-test",
    )
    assert page.id is not None

    fetched = await stateless_service.get_page_by_slug(db_session, wiki_user.id, "stateless-test")
    assert fetched is not None
    assert fetched.title == "Stateless Test"

    pages = await stateless_service.list_pages(db_session, wiki_user.id)
    assert any(p.slug == "stateless-test" for p in pages)


@pytest.mark.asyncio
async def test_wiki_service_delete_page(
    db_session: AsyncSession,
    wiki_user: UserModel,
):
    """Verify deleting a wiki page by slug."""
    service = WikiService(db=db_session)

    await service.upsert_page(
        user_id=wiki_user.id,
        title="To Be Deleted",
        markdown="# Deletable",
        slug="to-be-deleted",
    )
    assert await service.get_page_by_slug(user_id=wiki_user.id, slug="to-be-deleted") is not None

    deleted = await service.delete_page(user_id=wiki_user.id, slug="to-be-deleted")
    assert deleted is True

    # Should no longer exist
    assert await service.get_page_by_slug(user_id=wiki_user.id, slug="to-be-deleted") is None

    # Deleting non-existent returns False
    assert await service.delete_page(user_id=wiki_user.id, slug="to-be-deleted") is False


@pytest.mark.asyncio
async def test_wiki_service_upsert_positional_arguments_preserve_metadata_and_wikilinks(
    db_session: AsyncSession,
    wiki_user: UserModel,
):
    """Verify upsert_page preserves yaml_metadata and wikilinks when invoked with positional args."""
    service = WikiService(db=db_session)

    # 1. Positional call without db: (user_id, title, markdown, yaml_meta, wikilinks)
    yaml_meta = {"tags": ["positional", "test"], "category": "math"}
    links = ["Linear Algebra", "Vector Calculus"]
    page1 = await service.upsert_page(
        wiki_user.id,
        "Positional Page 1",
        "# Positional Page 1\nBody text.",
        yaml_meta,
        links,
    )
    assert page1.id is not None
    assert page1.title == "Positional Page 1"
    assert page1.yaml_metadata == {"tags": ["positional", "test"], "category": "math"}
    assert page1.wikilinks == ["Linear Algebra", "Vector Calculus"]

    # 2. Positional call with db: (db, user_id, title, markdown, yaml_meta, wikilinks)
    stateless = WikiService()
    yaml_meta_2 = {"level": "advanced", "author": "Vaswani"}
    links_2 = ["Attention", "FeedForward"]
    page2 = await stateless.upsert_page(
        db_session,
        wiki_user.id,
        "Positional Page 2",
        "# Positional Page 2\nBody text with [[Attention]].",
        yaml_meta_2,
        links_2,
    )
    assert page2.id is not None
    assert page2.title == "Positional Page 2"
    assert page2.yaml_metadata == {"level": "advanced", "author": "Vaswani"}
    assert page2.wikilinks == ["Attention", "FeedForward"]

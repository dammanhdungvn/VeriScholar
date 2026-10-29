"""Integration and contract tests for Academic LLM Wiki REST Endpoints and Research Gaps Synthesis.

Aligns with Spec 05 (§1.D, §4) and VeriScholar MVP architecture.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.db.models.wiki import WikiPageModel
from api.services.auth_service import AuthService
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def current_user(auth_headers: dict[str, str], db_session: AsyncSession) -> UserModel:
    """Resolve UserModel for current test auth session."""
    token = auth_headers["Authorization"].split(" ")[1]
    claims = AuthService.decode_token(token)
    user_id = claims["sub"]
    user = await db_session.get(UserModel, user_id)
    assert user is not None
    return user


@pytest.mark.asyncio
async def test_wiki_crud_and_research_gaps(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify basic lifecycle from Task 4 brief: empty listing, 404 on missing, gap synthesis."""
    # 1. List initially empty
    resp = await async_client.get("/api/v1/library/wiki", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"]["total"] == 0
    assert data["data"]["pages"] == []

    # 2. Get non-existent slug returns 404
    resp_404 = await async_client.get("/api/v1/library/wiki/unknown-concept", headers=auth_headers)
    assert resp_404.status_code == 404
    assert resp_404.json()["error"]["code"] == "WIKI_PAGE_NOT_FOUND"

    # 3. Query research gaps
    resp_gaps = await async_client.post(
        "/api/v1/library/research-gaps",
        json={"folder_id": None, "query": "Unsolved efficiency bottlenecks"},
        headers=auth_headers,
    )
    assert resp_gaps.status_code == 200
    assert "unsolved_frontiers" in resp_gaps.json()["data"]


@pytest.mark.asyncio
async def test_wiki_page_retrieval_by_slug(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
):
    """Verify retrieval of an existing compiled wiki page by slug."""
    page = WikiPageModel(
        user_id=current_user.id,
        slug="scaled-dot-product-attention",
        title="Scaled Dot-Product Attention",
        page_type="method",
        markdown_content="Toan van ve co che [[Attention]] voi ti le chia cho can bac hai cua d_k.",
        yaml_metadata={
            "formula": r"\text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V",
            "summary": "Co che chu chot trong Transformer.",
        },
        wikilinks=["Attention", "Transformer"],
    )
    db_session.add(page)
    await db_session.flush()

    resp = await async_client.get(
        "/api/v1/library/wiki/scaled-dot-product-attention",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["success"] is True
    page_data = res_json["data"]
    assert page_data["slug"] == "scaled-dot-product-attention"
    assert page_data["title"] == "Scaled Dot-Product Attention"
    assert page_data["page_type"] == "method"
    assert "Attention" in page_data["wikilinks"]
    assert page_data["markdown_content"].startswith("Toan van ve co che")


@pytest.mark.asyncio
async def test_wiki_list_filtering_and_pagination(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
):
    """Verify filtering wiki pages by page_type, folder_id, and pagination."""
    folder = FolderModel(
        user_id=current_user.id,
        name="NLP Research",
        color="#4F46E5",
    )
    db_session.add(folder)
    await db_session.flush()

    p1 = WikiPageModel(
        user_id=current_user.id,
        folder_id=folder.id,
        slug="page-method-1",
        title="Method 1",
        page_type="method",
        markdown_content="Content method 1",
        yaml_metadata={"summary": "Summary method 1"},
    )
    p2 = WikiPageModel(
        user_id=current_user.id,
        folder_id=folder.id,
        slug="page-dataset-1",
        title="Dataset 1",
        page_type="dataset",
        markdown_content="Content dataset 1",
        yaml_metadata={"summary": "Summary dataset 1"},
    )
    p3 = WikiPageModel(
        user_id=current_user.id,
        folder_id=None,
        slug="page-topic-1",
        title="Topic 1",
        page_type="topic",
        markdown_content="Content topic 1",
        yaml_metadata={"summary": "Summary topic 1"},
    )
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    # Filter by folder_id
    resp_folder = await async_client.get(
        f"/api/v1/library/wiki?folder_id={folder.id}",
        headers=auth_headers,
    )
    assert resp_folder.status_code == 200
    folder_data = resp_folder.json()["data"]
    assert folder_data["total"] == 2
    assert len(folder_data["pages"]) == 2

    # Filter by page_type
    resp_type = await async_client.get(
        "/api/v1/library/wiki?page_type=dataset",
        headers=auth_headers,
    )
    assert resp_type.status_code == 200
    type_data = resp_type.json()["data"]
    assert type_data["total"] == 1
    assert type_data["pages"][0]["slug"] == "page-dataset-1"

    # Pagination: limit=1, offset=1
    resp_paginated = await async_client.get(
        "/api/v1/library/wiki?limit=1&offset=1",
        headers=auth_headers,
    )
    assert resp_paginated.status_code == 200
    pag_data = resp_paginated.json()["data"]
    assert pag_data["total"] == 3
    assert len(pag_data["pages"]) == 1


@pytest.mark.asyncio
async def test_research_gaps_with_synthesized_papers(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
):
    """Verify research gaps synthesis incorporates paper limitations and suggests topics."""
    doc = DocumentModel(
        user_id=current_user.id,
        filename="sparse_transformer.pdf",
        title="Generating Long Sequences with Sparse Transformers",
        publication_year=2019,
        parsed_metadata={
            "abstract": "Transformers are powerful but computationally prohibitive for very long sequences.",
            "limitations": [
                "Memory footprint scales with context length",
                "Fixed sparse attention patterns cannot adapt to arbitrary input topologies",
            ],
        },
        content_hash="hash_sparse_" + uuid4().hex,
        file_size_bytes=2048,
        is_persistent=True,
        status="completed",
        stage="completed",
        progress=100,
    )
    db_session.add(doc)
    await db_session.flush()

    resp_gaps = await async_client.post(
        "/api/v1/library/research-gaps",
        json={"folder_id": None, "query": "Context length scalability"},
        headers=auth_headers,
    )
    assert resp_gaps.status_code == 200
    gaps_data = resp_gaps.json()["data"]
    assert "unsolved_frontiers" in gaps_data
    assert len(gaps_data["unsolved_frontiers"]) > 0
    assert "suggested_topics" in gaps_data
    assert len(gaps_data["suggested_topics"]) > 0
    assert gaps_data["total_papers_analyzed"] >= 1


@pytest.mark.asyncio
async def test_research_gaps_invalid_folder_returns_404(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify passing a non-existent folder_id yields 404 FOLDER_NOT_FOUND."""
    fake_folder_id = uuid4()
    resp = await async_client.post(
        "/api/v1/library/research-gaps",
        json={"folder_id": str(fake_folder_id)},
        headers=auth_headers,
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "FOLDER_NOT_FOUND"


@pytest.mark.asyncio
async def test_wiki_endpoints_unauthorized(async_client: AsyncClient):
    """Verify 401 Unauthorized when attempting to access wiki endpoints without auth."""
    resp_list = await async_client.get("/api/v1/library/wiki")
    assert resp_list.status_code == 401

    resp_get = await async_client.get("/api/v1/library/wiki/some-slug")
    assert resp_get.status_code == 401

    resp_gaps = await async_client.post("/api/v1/library/research-gaps", json={})
    assert resp_gaps.status_code == 401

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_discovery_search_empty_query_rejected(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.post(
        "/api/v1/discovery/search",
        headers=auth_headers,
        json={"query": "   "},
    )
    assert res.status_code == 400
    err = res.json()["error"]
    assert err["code"] == "SEARCH_QUERY_EMPTY"
    assert "không được để trống" in err["message"]


@pytest.mark.asyncio
async def test_discovery_search_returns_scholarly_results(
    async_client: AsyncClient, auth_headers: dict
):
    res = await async_client.post(
        "/api/v1/discovery/search",
        headers=auth_headers,
        json={"query": "Direct Preference Optimization", "limit": 5},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert isinstance(data, list)
    if len(data) > 0:
        paper = data[0]
        assert "title" in paper
        assert "authors" in paper
        assert paper["access_status"] in ["open_access_pdf", "abstract_only"]


@pytest.mark.asyncio
async def test_discovery_open_reading_creates_session_and_document(
    async_client: AsyncClient, auth_headers: dict
):
    # 1. Open reading with full PDF URL
    payload_pdf = {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer"],
        "publication_year": 2017,
        "venue": "NeurIPS 2017",
        "doi": "10.48550/arXiv.1706.03762",
        "arxiv_id": "1706.03762",
        "abstract": "The dominant sequence transduction models are based on RNNs...",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
    }
    res_pdf = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload_pdf,
    )
    assert res_pdf.status_code == 201
    data_pdf = res_pdf.json()["data"]
    assert "session_id" in data_pdf
    assert "document_id" in data_pdf
    assert data_pdf["status"] == "parsing"
    assert data_pdf["access_status"] == "open_access_pdf"

    # 2. Open reading with abstract only (no PDF URL)
    payload_abstract = {
        "title": "A general theoretical paradigm for preference learning",
        "authors": ["Emma Vance", "Liam Chen"],
        "publication_year": 2024,
        "abstract": "Preference optimization has become standard...",
        "pdf_url": None,
    }
    res_abs = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload_abstract,
    )
    assert res_abs.status_code == 201
    data_abs = res_abs.json()["data"]
    assert data_abs["status"] == "abstract_only"
    assert data_abs["access_status"] == "abstract_only"

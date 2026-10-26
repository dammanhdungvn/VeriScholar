import httpx
import pytest
from httpx import AsyncClient

SAMPLE_ARXIV_XML_WITH_IRRELEVANT_PHYSICS = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom" xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2312.10997v1</id>
    <title>Retrieval-Augmented Generation for Large Language Models: A Survey</title>
    <summary>Retrieval-Augmented Generation (RAG) significantly enhances Large Language Models...</summary>
    <published>2023-12-18T00:00:00Z</published>
    <author><name>Yunfan Gao</name></author>
    <link href="https://arxiv.org/pdf/2312.10997.pdf" rel="related" type="application/pdf" title="pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1411.4413v1</id>
    <title>Observation of the rare $B^0_s\\to\\mu^+\\mu^-$ decay from the combined analysis of CMS and LHCb data</title>
    <summary>A joint analysis is performed using data from the CMS and LHCb experiments...</summary>
    <published>2014-11-17T00:00:00Z</published>
    <author><name>CMS and LHCb Collaborations</name></author>
    <link href="https://arxiv.org/pdf/1411.4413.pdf" rel="related" type="application/pdf" title="pdf"/>
  </entry>
</feed>
"""


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
    async_client: AsyncClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
):
    original_get = httpx.AsyncClient.get

    async def mock_get(self, url, *args, **kwargs):
        if str(url).startswith("http://testserver") or not str(url).startswith("http"):
            return await original_get(self, url, *args, **kwargs)
        return httpx.Response(200, content=b"%PDF-1.4 sample content " + b"word " * 50)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

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


@pytest.mark.asyncio
async def test_scholarly_search_precision_no_particle_physics(
    async_client: AsyncClient, auth_headers: dict, monkeypatch
):
    class MockArxivResponse:
        status_code = 200
        text = SAMPLE_ARXIV_XML_WITH_IRRELEVANT_PHYSICS

    async def mock_get(*args, **kwargs):
        return MockArxivResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    res = await async_client.post(
        "/api/v1/discovery/search",
        headers=auth_headers,
        json={
            "query": "Retrieval-Augmented Generation for Large Language Models: A Survey",
            "limit": 10,
        },
    )
    assert res.status_code == 200
    papers = res.json()["data"]
    assert len(papers) > 0
    # Must contain RAG survey
    rag_papers = [p for p in papers if "Retrieval-Augmented Generation" in p["title"]]
    assert len(rag_papers) > 0
    # Must NOT contain LHCb / particle physics paper
    physics_papers = [
        p
        for p in papers
        if "LHCb" in p["title"] or "decay" in p["title"].lower() or "CMS" in p["title"]
    ]
    assert len(physics_papers) == 0
    # Must have is_peer_reviewed field
    assert "is_peer_reviewed" in papers[0]


@pytest.mark.asyncio
async def test_scholarly_search_peer_reviewed_filter(
    async_client: AsyncClient, auth_headers: dict, monkeypatch
):
    class MockArxivResponse:
        status_code = 200
        text = SAMPLE_ARXIV_XML_WITH_IRRELEVANT_PHYSICS

    async def mock_get(*args, **kwargs):
        return MockArxivResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    # 1. Search with is_peer_reviewed_only=True for preprint should exclude preprint
    res_filtered = await async_client.post(
        "/api/v1/discovery/search",
        headers=auth_headers,
        json={
            "query": "Retrieval-Augmented Generation for Large Language Models: A Survey",
            "is_peer_reviewed_only": True,
        },
    )
    assert res_filtered.status_code == 200
    papers_filtered = res_filtered.json()["data"]
    for paper in papers_filtered:
        assert paper["is_peer_reviewed"] is True

    # 2. Search for a peer-reviewed paper (NeurIPS in curated) with is_peer_reviewed_only=True
    res_neurips = await async_client.post(
        "/api/v1/discovery/search",
        headers=auth_headers,
        json={
            "query": "Attention Is All You Need",
            "is_peer_reviewed_only": True,
        },
    )
    assert res_neurips.status_code == 200
    papers_neurips = res_neurips.json()["data"]
    assert len(papers_neurips) > 0
    assert papers_neurips[0]["is_peer_reviewed"] is True
    assert "NeurIPS" in papers_neurips[0]["venue"]


def test_scholarly_search_adapter_jaccard_and_classification_units():
    from api.adapters.scholarly_search_adapter import ScholarlySearchAdapter

    # 1. Jaccard similarity tests
    q_rag = "Retrieval-Augmented Generation for Large Language Models: A Survey"
    t_rag_exact = "Retrieval-Augmented Generation for Large Language Models: A Survey"
    t_rag_variant = (
        "Towards Trustworthy Retrieval Augmented Generation for Large Language Models: A Survey"
    )
    t_physics = (
        "Observation of the rare $B^0_s\\to\\mu^+\\mu^-$ decay from the combined "
        "analysis of CMS and LHCb data"
    )

    sim_exact = ScholarlySearchAdapter.compute_title_jaccard_similarity(q_rag, t_rag_exact)
    sim_variant = ScholarlySearchAdapter.compute_title_jaccard_similarity(q_rag, t_rag_variant)
    sim_physics = ScholarlySearchAdapter.compute_title_jaccard_similarity(q_rag, t_physics)

    assert sim_exact == 1.0
    assert sim_variant >= 0.7
    assert sim_physics < 0.2
    assert ScholarlySearchAdapter._is_relevant_result(q_rag, t_rag_exact) is True
    assert ScholarlySearchAdapter._is_relevant_result(q_rag, t_physics) is False

    # 2. Peer-reviewed classification
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed("NeurIPS 2023", "10.48550/arXiv.2305.18290")
        is True
    )
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed("CVPR 2016", "10.1109/CVPR.2016.90") is True
    )
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed("arXiv", "10.48550/arXiv.2312.10997")
        is False
    )
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed(None, "10.1038/s42256-024-00800-x") is True
    )
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed("Nature Machine Intelligence", None) is True
    )
    assert (
        ScholarlySearchAdapter._classify_peer_reviewed(
            "IEEE Trans. Pattern Anal. Mach. Intell.", None
        )
        is True
    )

    # 3. arXiv query builder
    arxiv_q = ScholarlySearchAdapter._build_arxiv_query(q_rag)
    assert 'ti:"Retrieval-Augmented Generation for Large Language Models: A Survey"' in arxiv_q
    assert "ti:" in arxiv_q and "abs:" in arxiv_q

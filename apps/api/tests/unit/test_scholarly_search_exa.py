import httpx
import pytest
from api.adapters.scholarly_search_adapter import ScholarlySearchAdapter

SAMPLE_EXA_RESPONSE = {
    "results": [
        {
            "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
            "url": "https://arxiv.org/abs/2112.10752",
            "publishedDate": "2022-04-13T00:00:00.000Z",
            "author": "Robin Rombach, Andreas Blattmann, Dominik Lorenz",
            "text": (
                "By decomposing the image formation process into a sequential application "
                "of denoising autoencoders, diffusion models (DMs) achieve state-of-the-art "
                "synthesis results on image data and beyond."
            ),
            "highlights": [
                "Latent diffusion models achieve state-of-the-art synthesis.",
                "Near-lossless latent space training enables efficient high-resolution generation.",
            ],
        },
        {
            "title": "Deep Residual Learning for Image Recognition",
            "url": "https://doi.org/10.1109/CVPR.2016.90",
            "publishedDate": "2016-06-27",
            "author": ["Kaiming He", "Xiangyu Zhang"],
            "text": (
                "Deeper neural networks are more difficult to train. We present a residual "
                "learning framework to ease the training of networks that are substantially "
                "deeper than those used previously."
            ),
            "highlights": ["We present a residual learning framework."],
        },
    ]
}

SAMPLE_ARXIV_DIFFUSION_ATOM = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom" xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2006.11239v2</id>
    <title>Denoising Diffusion Probabilistic Models</title>
    <summary>We present high quality image synthesis results using diffusion probabilistic models...</summary>
    <published>2020-06-19T00:00:00Z</published>
    <author><name>Jonathan Ho</name></author>
    <author><name>Ajay Jain</name></author>
    <author><name>Pieter Abbeel</name></author>
    <link href="https://arxiv.org/pdf/2006.11239.pdf" rel="related" type="application/pdf" title="pdf"/>
  </entry>
</feed>
"""


@pytest.mark.asyncio
async def test_search_exa_success_parses_results(monkeypatch: pytest.MonkeyPatch):
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0)

    captured_request = {}

    async def mock_post(self, url, *args, **kwargs):
        captured_request["url"] = str(url)
        captured_request["headers"] = kwargs.get("headers", {})
        captured_request["json"] = kwargs.get("json", {})
        return httpx.Response(200, json=SAMPLE_EXA_RESPONSE)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    results = await adapter._search_exa(
        query="diffusion models",
        limit=5,
        api_key="test-exa-key-12345",
    )

    # 1. Verify HTTP request contract
    assert captured_request["url"] == "https://api.exa.ai/search"
    assert captured_request["headers"].get("x-api-key") == "test-exa-key-12345"
    assert captured_request["headers"].get("Content-Type") == "application/json"
    payload = captured_request["json"]
    assert payload["query"] == "diffusion models"
    assert payload["numResults"] == 5
    assert payload["type"] == "neural"
    assert payload["useAutoprompt"] is True
    assert payload["category"] == "research paper"

    # 2. Verify parsed entities
    assert len(results) == 2

    # Item 1: arXiv paper
    p1 = results[0]
    assert p1.title == "High-Resolution Image Synthesis with Latent Diffusion Models"
    assert p1.authors == ["Robin Rombach", "Andreas Blattmann", "Dominik Lorenz"]
    assert p1.publication_year == 2022
    assert p1.arxiv_id == "2112.10752"
    assert p1.pdf_url == "https://arxiv.org/pdf/2112.10752.pdf"
    assert p1.access_status == "open_access_pdf"
    assert p1.is_peer_reviewed is False
    assert "By decomposing the image formation process" in (p1.abstract or "")

    # Item 2: IEEE DOI paper
    p2 = results[1]
    assert p2.title == "Deep Residual Learning for Image Recognition"
    assert p2.authors == ["Kaiming He", "Xiangyu Zhang"]
    assert p2.publication_year == 2016
    assert p2.doi == "10.1109/CVPR.2016.90"
    assert p2.is_peer_reviewed is True
    assert p2.access_status == "abstract_only"
    assert p2.pdf_url is None
    assert "Deeper neural networks are more difficult" in (p2.abstract or "")


@pytest.mark.asyncio
async def test_search_exa_missing_api_key_returns_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("EXA_API_KEY", raising=False)
    try:
        from api.core.config import settings

        monkeypatch.setattr(settings, "EXA_API_KEY", None)
    except Exception:
        pass
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0, exa_api_key=None)

    called = False

    async def mock_post(self, url, *args, **kwargs):
        nonlocal called
        called = True
        return httpx.Response(200, json=SAMPLE_EXA_RESPONSE)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    results = await adapter._search_exa("diffusion models", limit=5)
    assert results == []
    assert not called


@pytest.mark.asyncio
async def test_search_exa_http_error_falls_back_gracefully(monkeypatch: pytest.MonkeyPatch):
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0, exa_api_key="test-key")

    # 1. Connection Timeout
    async def mock_post_timeout(self, url, *args, **kwargs):
        raise httpx.ConnectTimeout("Exa upstream timed out")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_timeout)
    results_timeout = await adapter._search_exa("diffusion models", limit=5)
    assert results_timeout == []

    # 2. HTTP 500 Server Error
    async def mock_post_500(self, url, *args, **kwargs):
        return httpx.Response(500, text="Internal Server Error")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_500)
    results_500 = await adapter._search_exa("diffusion models", limit=5)
    assert results_500 == []


@pytest.mark.asyncio
async def test_search_integrates_exa_and_arxiv(monkeypatch: pytest.MonkeyPatch):
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0, exa_api_key="test-key")

    # Mock Exa POST
    async def mock_post(self, url, *args, **kwargs):
        if "exa.ai" in str(url):
            return httpx.Response(200, json=SAMPLE_EXA_RESPONSE)
        return httpx.Response(404)

    # Mock arXiv GET
    async def mock_get(self, url, *args, **kwargs):
        if "arxiv.org" in str(url):
            return httpx.Response(200, text=SAMPLE_ARXIV_DIFFUSION_ATOM)
        return httpx.Response(404)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    results = await adapter.search("diffusion models", limit=5)

    assert len(results) >= 2
    titles = [r.title for r in results]
    assert "High-Resolution Image Synthesis with Latent Diffusion Models" in titles
    assert "Denoising Diffusion Probabilistic Models" in titles

    # Peer-reviewed papers should rank before non-peer-reviewed papers
    assert results[0].is_peer_reviewed is True
    assert results[0].title == "Deep Residual Learning for Image Recognition"

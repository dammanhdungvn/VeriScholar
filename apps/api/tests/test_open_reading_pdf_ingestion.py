"""Tests for external PDF ingestion during discovery open-reading session creation."""

import hashlib

import httpx
import pytest
from httpx import AsyncClient

SAMPLE_PDF_BYTES = b"%PDF-1.4 sample content " + b"academic paper " * 50


@pytest.mark.asyncio
async def test_open_reading_downloads_pdf_and_serves_file(
    async_client: AsyncClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
):
    """Test that open-reading with valid PDF URL downloads and registers file in CAS."""
    original_get = httpx.AsyncClient.get

    async def mock_get(self, url, *args, **kwargs):
        if str(url).startswith("http://testserver") or not str(url).startswith("http"):
            return await original_get(self, url, *args, **kwargs)
        return httpx.Response(200, content=SAMPLE_PDF_BYTES)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    payload = {
        "title": "Retrieval-Augmented Generation for Large Language Models: A Survey",
        "authors": ["Yunfan Gao", "Yun Xiong"],
        "publication_year": 2023,
        "venue": "arXiv",
        "doi": "10.48550/arXiv.2312.10997",
        "arxiv_id": "2312.10997",
        "abstract": "Retrieval-Augmented Generation (RAG) significantly enhances LLMs...",
        "pdf_url": "https://arxiv.org/pdf/2312.10997.pdf",
    }

    res = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()["data"]
    doc_id = data["document_id"]
    assert data["status"] == "parsing"
    assert data["access_status"] == "open_access_pdf"

    expected_hash = hashlib.sha256(SAMPLE_PDF_BYTES).hexdigest()

    # Verify document metadata has real content_hash and file_size_bytes
    doc_res = await async_client.get(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers,
    )
    assert doc_res.status_code == 200
    doc_data = doc_res.json()["data"]
    assert doc_data["file_size_bytes"] == len(SAMPLE_PDF_BYTES)

    # Verify GET /api/v1/documents/{document_id}/file returns HTTP 200 with identical PDF bytes
    file_res = await async_client.get(
        f"/api/v1/documents/{doc_id}/file",
        headers=auth_headers,
    )
    assert file_res.status_code == 200
    assert file_res.content == SAMPLE_PDF_BYTES
    assert file_res.headers.get("content-type") == "application/pdf"
    assert file_res.headers.get("etag") == f'"{expected_hash}"'


@pytest.mark.asyncio
async def test_open_reading_handles_download_failure_gracefully(
    async_client: AsyncClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
):
    """Test that timeout or 404 during PDF download falls back to abstract_only."""
    original_get = httpx.AsyncClient.get

    # 1. Test timeout exception
    async def mock_get_timeout(self, url, *args, **kwargs):
        if str(url).startswith("http://testserver") or not str(url).startswith("http"):
            return await original_get(self, url, *args, **kwargs)
        raise httpx.TimeoutException("Connection timed out to PDF repository")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_timeout)

    payload_timeout = {
        "title": "A Survey on Deep Learning",
        "authors": ["Test Author"],
        "publication_year": 2022,
        "pdf_url": "https://arxiv.org/pdf/timeout.pdf",
    }
    res_timeout = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload_timeout,
    )
    assert res_timeout.status_code == 201
    data_timeout = res_timeout.json()["data"]
    assert data_timeout["status"] == "abstract_only"
    assert data_timeout["access_status"] == "abstract_only"

    doc_id = data_timeout["document_id"]
    doc_res = await async_client.get(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers,
    )
    assert doc_res.status_code == 200
    assert doc_res.json()["data"]["file_size_bytes"] == 0

    # 2. Test 404 response
    async def mock_get_404(self, url, *args, **kwargs):
        if str(url).startswith("http://testserver") or not str(url).startswith("http"):
            return await original_get(self, url, *args, **kwargs)
        return httpx.Response(404, content=b"Not Found")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_404)

    payload_404 = {
        "title": "Broken Link Paper",
        "authors": ["Test Author 2"],
        "publication_year": 2023,
        "pdf_url": "https://arxiv.org/pdf/nonexistent.pdf",
    }
    res_404 = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload_404,
    )
    assert res_404.status_code == 201
    data_404 = res_404.json()["data"]
    assert data_404["status"] == "abstract_only"
    assert data_404["access_status"] == "abstract_only"

    doc_id_404 = data_404["document_id"]
    doc_res_404 = await async_client.get(
        f"/api/v1/documents/{doc_id_404}",
        headers=auth_headers,
    )
    assert doc_res_404.status_code == 200
    assert doc_res_404.json()["data"]["file_size_bytes"] == 0


@pytest.mark.asyncio
async def test_open_reading_rejects_html_magic_bytes(
    async_client: AsyncClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch
):
    """Test that responses returning HTML instead of %PDF- fall back to abstract_only."""
    original_get = httpx.AsyncClient.get
    html_content = b"<!DOCTYPE html><html><head><title>Cloudflare Challenge</title></head><body>Verify you are human</body></html>"

    async def mock_get_html(self, url, *args, **kwargs):
        if str(url).startswith("http://testserver") or not str(url).startswith("http"):
            return await original_get(self, url, *args, **kwargs)
        return httpx.Response(200, content=html_content)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_html)

    payload = {
        "title": "Paywalled Paper with Captcha",
        "authors": ["Publisher Bot"],
        "publication_year": 2024,
        "pdf_url": "https://publisher.com/article.pdf",
    }
    res = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["status"] == "abstract_only"
    assert data["access_status"] == "abstract_only"

    doc_id = data["document_id"]
    doc_res = await async_client.get(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers,
    )
    assert doc_res.status_code == 200
    assert doc_res.json()["data"]["file_size_bytes"] == 0

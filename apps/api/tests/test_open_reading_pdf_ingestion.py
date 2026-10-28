"""Tests for external PDF ingestion during discovery open-reading session creation."""

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.deps import get_document_service, get_storage
from api.schemas.discovery import OpenReadingRequest
from api.v1.endpoints.discovery import open_reading_session
from httpx import AsyncClient
from sqlalchemy import select

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


@pytest_asyncio.fixture
async def test_user(db_session):
    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Test Scholar",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_open_reading_schedules_background_parsing(db_session, test_user):
    bg_tasks = MagicMock()
    payload = OpenReadingRequest(
        title="Ragas Evaluation Paper",
        pdf_url="https://arxiv.org/pdf/2309.15217.pdf",
        authors=["Es et al."],
        publication_year=2023,
    )
    with patch(
        "api.services.document_service.DocumentService.ingest_pdf_from_url",
        new_callable=AsyncMock,
    ) as mock_ingest:
        mock_ingest.return_value = ("fake_hash_123", 102400)
        res = await open_reading_session(
            payload=payload,
            background_tasks=bg_tasks,
            current_user=test_user,
            db=db_session,
        )
        assert res.data.document_status in ["parsing", "processing"]
        assert bg_tasks.add_task.called


@pytest.mark.asyncio
async def test_parse_document_background_generates_embeddings_and_summary_metadata(
    db_session, test_user, monkeypatch: pytest.MonkeyPatch
):
    """Test that parse_document_background extracts chunks, computes embeddings, and builds summary_metadata."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_session_ctx():
        yield db_session

    monkeypatch.setattr("api.db.session.AsyncSessionLocal", lambda: mock_session_ctx())

    storage = get_storage()
    service = get_document_service(storage=storage)

    import pymupdf

    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page()
    page.insert_text(
        (72, 72),
        "Abstract: Ragas enables automated evaluation of retrieval augmented generation.\n"
        "Problem: Evaluating RAG systems requires human ground truth which is expensive and unscalable.\n"
        "Methodology: We propose reference-free evaluation metrics including Answer Relevance and Faithfulness.\n"
        "Results: Pearson correlation r > 0.82 with human annotators and 95% accuracy across benchmarks.\n"
        "Conclusion: Synthetic questions allow quantifying semantic overlap without human labels.",
    )
    valid_pdf_bytes = pdf_doc.tobytes()
    pdf_doc.close()

    content_hash = hashlib.sha256(valid_pdf_bytes).hexdigest()

    async def _stream():
        yield valid_pdf_bytes

    await storage.save_blob(_stream(), content_hash)

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        filename="ragas_eval.pdf",
        title="Ragas: Automated Evaluation of Retrieval Augmented Generation",
        authors=["Shahul Es", "Jithin James"],
        publication_year=2023,
        content_hash=content_hash,
        file_size_bytes=len(valid_pdf_bytes),
        status="parsing",
        stage="metadata_ingested",
        progress=10,
        access_status="open_access_pdf",
        parsed_metadata={"parse_options": {"chunk_size": 256, "chunk_overlap": 20}},
    )
    db_session.add(doc)
    await db_session.flush()

    with patch(
        "api.services.embedding_service.EmbeddingService.get_embeddings_batch",
        new_callable=AsyncMock,
    ) as mock_embed:
        # Mock returning 1536-dim vectors for whatever batch is requested
        mock_embed.side_effect = lambda texts, *args, **kwargs: [[0.042] * 1536 for _ in texts]

        await service.parse_document_background(doc_id, test_user.id)

    # Re-query document from DB
    res = await db_session.execute(select(DocumentModel).where(DocumentModel.id == doc_id))
    updated_doc = res.scalar_one()

    assert updated_doc.status == "completed"
    assert updated_doc.stage == "completed"
    assert updated_doc.progress == 100
    assert updated_doc.chunk_count > 0

    # Verify 4-pillar Summary Index
    assert "summary_metadata" in updated_doc.parsed_metadata
    summary_meta = updated_doc.parsed_metadata["summary_metadata"]
    assert "original_problem" in summary_meta
    assert "proposed_solution" in summary_meta
    assert "key_insights" in summary_meta
    assert "quantitative_results" in summary_meta
    assert isinstance(summary_meta["original_problem"], list)
    assert isinstance(summary_meta["proposed_solution"], list)

    # Verify chunks have embeddings
    chunks_res = await db_session.execute(
        select(DocumentChunkModel).where(DocumentChunkModel.document_id == doc_id)
    )
    chunks = list(chunks_res.scalars().all())
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.embedding is not None
        assert len(chunk.embedding) == 1536


@pytest.mark.asyncio
async def test_backfill_chunk_embeddings_script(
    db_session, test_user, monkeypatch: pytest.MonkeyPatch
):
    """Test that backfill script scans chunks missing embeddings and populates 1536d vectors idempotently."""
    import sys
    from contextlib import asynccontextmanager
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from scripts.backfill_chunk_embeddings import backfill_chunk_embeddings

    @asynccontextmanager
    async def mock_session_ctx():
        yield db_session

    monkeypatch.setattr("api.db.session.AsyncSessionLocal", lambda: mock_session_ctx())
    monkeypatch.setattr(
        "scripts.backfill_chunk_embeddings.AsyncSessionLocal", lambda: mock_session_ctx()
    )

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        filename="backfill_test.pdf",
        title="Backfill Test Paper",
        content_hash="hash_backfill_123",
        file_size_bytes=1000,
        status="completed",
        stage="completed",
        progress=100,
        access_status="open_access_pdf",
    )
    db_session.add(doc)
    await db_session.flush()

    # Create 2 chunks with embedding=None
    c1 = DocumentChunkModel(
        id=uuid4(),
        user_id=test_user.id,
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="First chunk text without embedding",
        embedding=None,
    )
    c2 = DocumentChunkModel(
        id=uuid4(),
        user_id=test_user.id,
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="Second chunk text without embedding",
        embedding=None,
    )
    db_session.add_all([c1, c2])
    await db_session.flush()

    with patch(
        "api.services.embedding_service.EmbeddingService.get_embeddings_batch",
        new_callable=AsyncMock,
    ) as mock_embed:
        mock_embed.side_effect = lambda texts, *args, **kwargs: [[0.015] * 1536 for _ in texts]

        # 1. First run: backfills the 2 chunks
        exit_code = await backfill_chunk_embeddings(batch_size=10)
        assert exit_code == 0

        # Verify DB records updated
        res = await db_session.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.document_id == doc_id)
        )
        updated_chunks = list(res.scalars().all())
        assert len(updated_chunks) == 2
        for c in updated_chunks:
            assert c.embedding is not None
            assert len(c.embedding) == 1536

        # 2. Second run: idempotent, nothing to backfill
        exit_code_2 = await backfill_chunk_embeddings(batch_size=10)
        assert exit_code_2 == 0

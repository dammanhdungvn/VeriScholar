"""Unit and integration tests for References List API, 2-Tier Fast Session Ingestion, and SSE Bridge Hint.

Complies with Hexagonal Architecture and TDD methodology.
"""

from __future__ import annotations

import time
from uuid import uuid4

import pytest
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel, SessionTurnModel
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_document_references_with_session_id_and_is_in_session(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """GET /documents/{document_id}/references with optional session_id accurately populates is_in_session."""
    # 1. Create a session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Session for Reference Testing"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    # 2. Upload source document
    pdf_bytes = b"%PDF-1.4 source document " + (b"word " * 100)
    upload_res = await async_client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("source.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code in (200, 201, 202)
    doc_id = upload_res.json()["data"]["id"]

    # Also get the user_id
    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 3. Create resolved target document
    resolved_doc = DocumentModel(
        id=uuid4(),
        user_id=user_id,
        filename="resolved_target.pdf",
        title="Attention Is All You Need",
        content_hash="hash_resolved_target_01",
        file_size_bytes=1024,
        status="ready",
        access_status="open_access_pdf",
    )
    db_session.add(resolved_doc)
    await db_session.flush()

    # Link resolved_doc to the session
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=resolved_doc.id,
        display_order=0,
    )
    db_session.add(sess_doc)

    # 4. Insert two reference items for source document:
    # Ref 1: resolved to resolved_doc (which is in session)
    # Ref 2: not resolved (not in session)
    ref1 = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=doc_id,
        ref_index=1,
        raw_text="Vaswani et al. (2017). Attention is all you need.",
        parsed_title="Attention Is All You Need",
        parsed_authors=["Vaswani et al."],
        parsed_year=2017,
        arxiv_id="1706.03762",
        doi="10.48550/arXiv.1706.03762",
        resolved_document_id=resolved_doc.id,
    )
    ref2 = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=doc_id,
        ref_index=2,
        raw_text="Devlin et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers.",
        parsed_title="BERT: Pre-training of Deep Bidirectional Transformers",
        parsed_authors=["Devlin et al."],
        parsed_year=2018,
        arxiv_id="1810.04805",
        doi="10.48550/arXiv.1810.04805",
        resolved_document_id=None,
    )
    db_session.add_all([ref1, ref2])
    await db_session.commit()

    # 5. Call GET /documents/{id}/references without session_id
    res_no_sess = await async_client.get(
        f"/api/v1/documents/{doc_id}/references",
        headers=auth_headers,
    )
    assert res_no_sess.status_code == 200
    data_no_sess = res_no_sess.json()["data"]
    assert data_no_sess["total_references"] == 2
    for r in data_no_sess["references"]:
        assert r["is_in_session"] is False

    # 6. Call GET /documents/{id}/references WITH session_id
    res_with_sess = await async_client.get(
        f"/api/v1/documents/{doc_id}/references?session_id={session_id}",
        headers=auth_headers,
    )
    assert res_with_sess.status_code == 200
    data_with_sess = res_with_sess.json()["data"]
    assert data_with_sess["total_references"] == 2

    r1 = next(r for r in data_with_sess["references"] if r["ref_index"] == 1)
    r2 = next(r for r in data_with_sess["references"] if r["ref_index"] == 2)
    assert r1["is_in_session"] is True
    assert r2["is_in_session"] is False
    assert r1["pdf_url"] == "https://arxiv.org/pdf/1706.03762.pdf"
    assert r1["access_status"] == "open_access_pdf"


@pytest.mark.asyncio
async def test_post_session_references_ingest_tier1_fast_sync(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """POST /sessions/{id}/references:ingest responds in < 500ms with HTTP 201 Created and links document."""
    # 1. Create a session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Fast Ingestion Test Session"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    # 2. Upload source document
    pdf_bytes = b"%PDF-1.4 fast ingest paper " + (b"word " * 100)
    upload_res = await async_client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("fast_source.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code in (200, 201, 202)
    doc_id = upload_res.json()["data"]["id"]

    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 3. Create reference item in DB
    ref = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=doc_id,
        ref_index=3,
        raw_text="Vaswani et al. (2017). Attention is all you need.",
        parsed_title="Attention Is All You Need",
        parsed_authors=["Vaswani et al."],
        parsed_year=2017,
        arxiv_id="1706.03762",
        doi="10.48550/arXiv.1706.03762",
    )
    db_session.add(ref)
    await db_session.commit()

    # 4. Measure execution time of Tier 1 fast ingestion
    start_t = time.perf_counter()
    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/references:ingest",
        headers=auth_headers,
        json={
            "document_id": doc_id,
            "ref_index": 3,
        },
    )
    elapsed_t = time.perf_counter() - start_t

    # Invariant: Tier 1 fast sync response must complete in < 500ms (0.5s)
    assert elapsed_t < 0.5, f"Tier 1 ingestion took {elapsed_t:.3f}s (must be < 0.5s)"
    assert res.status_code == 201
    body = res.json()
    data = body.get("data", body)
    assert data["status"] == "parsing"
    assert data["access_status"] == "open_access_pdf"
    new_doc_id = data["document_id"]

    # 5. Verify database link in session_documents
    link_stmt = select(SessionDocumentModel).where(
        SessionDocumentModel.session_id == session_id,
        SessionDocumentModel.document_id == new_doc_id,
    )
    link = (await db_session.execute(link_stmt)).scalar_one_or_none()
    assert link is not None


@pytest.mark.asyncio
async def test_session_references_ingest_capacity_limit_returns_409(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """POST /sessions/{id}/references:ingest returns HTTP 409 MAX_SESSION_DOCUMENTS_REACHED when 5 docs exist."""
    # 1. Create session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Max 5 Capacity Session"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 2. Pre-fill session with 5 documents
    for idx in range(5):
        d = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            filename=f"doc_{idx}.pdf",
            title=f"Doc {idx}",
            content_hash=f"hash_cap_{idx}",
            file_size_bytes=100,
            status="ready",
        )
        db_session.add(d)
        await db_session.flush()
        db_session.add(
            SessionDocumentModel(
                session_id=session_id,
                document_id=d.id,
                display_order=idx,
            )
        )
    await db_session.commit()

    # 3. Create a source document with a reference to ingest
    src_doc = DocumentModel(
        id=uuid4(),
        user_id=user_id,
        filename="src.pdf",
        title="Source Doc",
        content_hash="hash_src_doc",
        file_size_bytes=100,
        status="ready",
    )
    db_session.add(src_doc)
    await db_session.flush()

    ref = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=src_doc.id,
        ref_index=1,
        raw_text="Paper 6 text",
        parsed_title="Paper 6",
        arxiv_id="1909.00001",
    )
    db_session.add(ref)
    await db_session.commit()

    # 4. Ingest 6th document -> Must fail with 409 MAX_SESSION_DOCUMENTS_REACHED
    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/references:ingest",
        headers=auth_headers,
        json={"document_id": str(src_doc.id), "ref_index": 1},
    )
    assert res.status_code == 409
    err = res.json()["error"]
    assert err["code"] == "MAX_SESSION_DOCUMENTS_REACHED"


@pytest.mark.asyncio
async def test_session_references_ingest_duplicate_returns_409(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """POST /sessions/{id}/references:ingest returns HTTP 409 REFERENCE_ALREADY_IN_SESSION on duplicate."""
    # 1. Create session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Duplicate Ingestion Test"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 2. Create source doc and reference
    src_doc = DocumentModel(
        id=uuid4(),
        user_id=user_id,
        filename="src.pdf",
        title="Source Doc",
        content_hash="hash_dup_src",
        file_size_bytes=100,
        status="ready",
    )
    db_session.add(src_doc)
    await db_session.flush()

    ref = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=src_doc.id,
        ref_index=1,
        raw_text="Paper dup text",
        parsed_title="Paper Dup",
        arxiv_id="2001.00001",
    )
    db_session.add(ref)
    await db_session.commit()

    # 3. First ingest succeeds (201)
    res1 = await async_client.post(
        f"/api/v1/sessions/{session_id}/references:ingest",
        headers=auth_headers,
        json={"document_id": str(src_doc.id), "ref_index": 1},
    )
    assert res1.status_code == 201

    # 4. Second ingest of same reference returns 409 REFERENCE_ALREADY_IN_SESSION
    res2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/references:ingest",
        headers=auth_headers,
        json={"document_id": str(src_doc.id), "ref_index": 1},
    )
    assert res2.status_code == 409
    err = res2.json()["error"]
    assert err["code"] == "REFERENCE_ALREADY_IN_SESSION"


@pytest.mark.asyncio
async def test_session_references_ingest_paywall_fallback_abstract_only(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """POST /sessions/{id}/references:ingest creates status='abstract_only' when reference is paywalled."""
    # 1. Create session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Paywall Fallback Session"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 2. Source doc & paywalled reference (no arxiv_id, closed doi)
    src_doc = DocumentModel(
        id=uuid4(),
        user_id=user_id,
        filename="src.pdf",
        title="Source Doc",
        content_hash="hash_paywall_src",
        file_size_bytes=100,
        status="ready",
    )
    db_session.add(src_doc)
    await db_session.flush()

    ref = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=src_doc.id,
        ref_index=9,
        raw_text="Smith, J. (2015). Proprietary Paywalled Study. Journal of Closed Access, 10(2), 1-10.",
        parsed_title="Proprietary Paywalled Study",
        parsed_authors=["Smith, J."],
        parsed_year=2015,
        doi="10.1016/j.closed.2015.01.001",
        arxiv_id=None,
    )
    db_session.add(ref)
    await db_session.commit()

    # 3. Ingest paywalled reference -> returns 201 with status="abstract_only"
    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/references:ingest",
        headers=auth_headers,
        json={"document_id": str(src_doc.id), "ref_index": 9},
    )
    assert res.status_code == 201
    body = res.json()
    data = body.get("data", body)
    assert data["status"] == "abstract_only"
    assert data["access_status"] in ("paywalled", "abstract_only")

    # 4. Verify created document in DB
    created_doc = await db_session.get(DocumentModel, data["document_id"])
    assert created_doc is not None
    assert created_doc.status == "abstract_only"


@pytest.mark.asyncio
async def test_session_chat_stream_strips_bridge_hint_and_emits_event(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """SSE chat stream strips <bridge_hint .../> tag from tokens/turn answer and emits event: bridge_hint."""
    # 1. Create a session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Socratic Roadmap Chat Session"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["data"]["id"]

    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 2. Create document with reference [3]
    doc = DocumentModel(
        id=uuid4(),
        user_id=user_id,
        filename="diffusion_paper.pdf",
        title="Denoising Diffusion Probabilistic Models",
        content_hash="hash_diffusion_01",
        file_size_bytes=1000,
        status="ready",
    )
    db_session.add(doc)
    await db_session.flush()

    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc.id,
        display_order=0,
    )
    ref3 = ReferenceItemModel(
        id=uuid4(),
        user_id=user_id,
        document_id=doc.id,
        ref_index=3,
        raw_text="Vaswani et al. (2017). Attention is all you need.",
        parsed_title="Attention Is All You Need",
        parsed_authors=["Vaswani et al."],
        parsed_year=2017,
        arxiv_id="1706.03762",
        doi="10.48550/arXiv.1706.03762",
    )
    db_session.add_all([sess_doc, ref3])
    await db_session.commit()

    # 3. Ask question that triggers tailored roadmap or bridge hint
    chat_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
        json={
            "question": "Tôi muốn lộ trình học chi tiết để hiểu sâu thuật toán này từ con số 0.",
            "scope": "multi_paper",
        },
    )
    assert chat_res.status_code == 200
    stream_text = chat_res.text

    # Verify event: bridge_hint is emitted
    assert "event: bridge_hint" in stream_text, (
        f"Expected 'event: bridge_hint' in SSE stream, got:\n{stream_text[:500]}"
    )
    assert '"ref_index": 3' in stream_text or '"ref_index":3' in stream_text

    # Verify <bridge_hint is NOT present in any token events
    for line in stream_text.splitlines():
        if line.startswith("data: ") and "token" in line:
            assert "<bridge_hint" not in line
            assert "</bridge_hint>" not in line

    # Verify event: done is emitted
    assert "event: done" in stream_text

    # Verify database SessionTurnModel has cleanly stripped answer text
    stmt = (
        select(SessionTurnModel)
        .where(SessionTurnModel.session_id == session_id)
        .order_by(SessionTurnModel.created_at.desc())
    )
    turn = (await db_session.execute(stmt)).scalars().first()
    assert turn is not None
    assert "<bridge_hint" not in turn.answer
    assert "</bridge_hint>" not in turn.answer

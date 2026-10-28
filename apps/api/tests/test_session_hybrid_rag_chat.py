from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.services.session_chat_service import SessionChatService
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserModel:
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


@pytest_asyncio.fixture
async def setup_ragas_document(
    db_session: AsyncSession, test_user: UserModel, monkeypatch: pytest.MonkeyPatch
):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.05] * 1536),
    )

    doc_id = uuid4()
    session_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        title="Ragas Paper",
        filename="ragas.pdf",
        status="ready",
        content_hash="hash_ragas_paper_001",
        file_size_bytes=1024,
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=test_user.id,
        title="Ragas Study Session",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    c19 = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=test_user.id,
        chunk_index=19,
        page_number=3,
        content="Answer Relevance (AR) is formulated as: AR = (1/n) * sum(sim(q, q_i))",
        embedding=[0.05] * 1536,
        bounding_boxes=[[120.0, 450.0, 530.0, 535.0, 3]],
        content_tsv=func.to_tsvector(
            "simple", "Answer Relevance AR is formulated as sum sim q q_i"
        ),
    )
    db_session.add(doc)
    await db_session.flush()
    db_session.add(sess)
    await db_session.flush()
    db_session.add_all([sess_doc, c19])
    await db_session.commit()
    return session_id, doc_id


@pytest.mark.asyncio
async def test_ask_ragas_formula_ar_retrieves_page_3_with_bounding_box(
    db_session: AsyncSession, test_user: UserModel, setup_ragas_document
):
    session_id, doc_id = setup_ragas_document
    chat_service = SessionChatService(db=db_session)

    chunks, citations, abstain = await chat_service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=test_user.id,
        question="Công thức Answer Relevance (AR) trong paper là gì?",
        target_doc_ids=[doc_id],
    )
    assert not abstain
    assert any(c["page_number"] == 3 for c in citations)
    assert any(c["chunk_index"] == 19 for c in chunks)
    # Kiểm tra Bounding Box dạng mảng [x0, y0, x1, y1, page]
    bbox = citations[0]["bounding_boxes"][0]
    assert len(bbox) == 5
    assert 0 <= bbox[0] <= 1000 and 0 <= bbox[1] <= 1000


@pytest.mark.asyncio
async def test_retrieve_hybrid_chunks_rrf_scoring(
    db_session: AsyncSession,
    async_client: AsyncClient,
    auth_headers: dict,
):
    # 1. Create a session and a document via API
    res_sess = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Hybrid RAG Test"},
    )
    assert res_sess.status_code == 201
    session_id = res_sess.json()["data"]["id"]

    pdf_bytes = b"%PDF-1.4 sample attention paper " + (b"attention " * 100)
    res_doc = await async_client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("attention.pdf", pdf_bytes, "application/pdf")},
    )
    assert res_doc.status_code in (200, 201, 202)
    doc_id = res_doc.json()["data"]["id"]

    # Link document to session
    await async_client.post(
        f"/api/v1/sessions/{session_id}/documents",
        headers=auth_headers,
        json={"source_type": "document_id", "document_id": doc_id},
    )

    # 2. Get user_id from session
    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 3. Insert 2 test chunks with spatial bounding box and text content
    dummy_vec1 = [0.1] * 1536
    dummy_vec2 = [-0.1] * 1536

    chunk1 = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="The Transformer model relies entirely on self-attention mechanisms to compute representations.",
        bounding_boxes=[[50, 100, 450, 160, 1]],
        token_count=15,
        embedding=dummy_vec1,
        content_tsv=func.to_tsvector(
            "simple", "The Transformer model relies entirely on self-attention mechanisms"
        ),
    )
    chunk2 = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=1,
        page_number=2,
        content="Residual connections are applied around each of the two sub-layers followed by layer normalization.",
        bounding_boxes=[[50, 200, 450, 260, 2]],
        token_count=18,
        embedding=dummy_vec2,
        content_tsv=func.to_tsvector(
            "simple", "Residual connections are applied around each of the two sub-layers"
        ),
    )
    db_session.add_all([chunk1, chunk2])
    await db_session.commit()

    # 4. Test retrieve_hybrid_chunks method
    chat_service = SessionChatService(db=db_session)
    chunks = await chat_service.retrieve_hybrid_chunks(
        session_id=session_id,
        user_id=user_id,
        query_text="self-attention mechanism",
        query_embedding=dummy_vec1,
        limit=5,
    )

    assert len(chunks) > 0
    # Chunk 1 should rank higher due to keyword and vector match
    top_chunk = chunks[0]
    assert "self-attention" in top_chunk["content"].lower()
    assert top_chunk["page_number"] == 1
    assert "bounding_boxes" in top_chunk
    assert top_chunk["rrf_score"] > 0


@pytest.mark.asyncio
async def test_delete_session_messages_preserves_session(
    async_client: AsyncClient,
    auth_headers: dict,
):
    # 1. Create a session
    res_sess = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Session Message Reset Test"},
    )
    assert res_sess.status_code == 201
    session_id = res_sess.json()["data"]["id"]

    # 2. Delete messages (idempotent 204)
    res_del = await async_client.delete(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )
    assert res_del.status_code == 204

    # 3. Session itself must remain intact
    res_get = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )
    assert res_get.status_code == 200
    assert res_get.json()["data"]["id"] == session_id


@pytest.mark.asyncio
async def test_chat_stream_abstract_only_guardrail(
    db_session: AsyncSession,
    async_client: AsyncClient,
    auth_headers: dict,
):
    from api.db.models.document import DocumentModel

    # 1. Create a session
    res_sess = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Abstract-Only Session"},
    )
    assert res_sess.status_code == 201
    session_id = res_sess.json()["data"]["id"]

    # 2. Get user_id from session
    sess_obj = await db_session.get(ResearchSessionModel, session_id)
    assert sess_obj is not None
    user_id = sess_obj.user_id

    # 3. Create an abstract_only document
    doc = DocumentModel(
        user_id=user_id,
        filename="abstract_only_paper.pdf",
        title="Theoretical Bounds of Transformer Networks",
        content_hash="hash_theoretical_bounds",
        status="abstract_only",
        access_status="abstract_only",
        parsed_metadata={
            "abstract": "We prove the asymptotic expressiveness of self-attention layers under finite precision."
        },
        page_count=0,
        chunk_count=0,
        file_size_bytes=0,
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    # Link to session
    await async_client.post(
        f"/api/v1/sessions/{session_id}/documents",
        headers=auth_headers,
        json={"source_type": "document_id", "document_id": str(doc.id)},
    )

    # 4. Request chat stream
    res_chat = await async_client.post(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
        json={
            "question": "Mô tả đóng góp của bài báo này",
            "scope": "multi_paper",
        },
    )
    assert res_chat.status_code == 200
    content = res_chat.text
    # Should include abstract reference and no crash
    assert "event: done" in content
    assert "Theoretical" in content and "Bounds" in content

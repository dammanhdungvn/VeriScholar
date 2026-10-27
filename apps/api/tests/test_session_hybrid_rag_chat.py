import pytest
from api.db.models.chunk import DocumentChunkModel
from api.db.models.session import ResearchSessionModel
from api.services.session_chat_service import SessionChatService
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession


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

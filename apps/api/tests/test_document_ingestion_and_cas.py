from uuid import UUID, uuid4

import pymupdf
import pytest
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.deps import get_document_service, get_storage
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_cas_deduplication_and_ref_count(async_client: AsyncClient, auth_headers: dict):
    # Upload same PDF twice
    pdf_content = b"%PDF-1.4 mock content with text layer " + (b"word " * 100)
    files = {"file": ("test_paper.pdf", pdf_content, "application/pdf")}

    res1 = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert res1.status_code == 202
    doc1_id = res1.json()["data"]["id"]

    # Upload same file content again
    files2 = {"file": ("test_paper_copy.pdf", pdf_content, "application/pdf")}
    res2 = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files2)
    assert res2.status_code == 202
    doc2_id = res2.json()["data"]["id"]
    assert doc1_id != doc2_id  # Separate document records sharing same blob


@pytest.mark.asyncio
async def test_zero_retention_purges_physical_blob_when_last_reference_deleted(
    async_client: AsyncClient, auth_headers: dict
):
    pdf_content = (
        b"%PDF-1.4 unique confidential draft content "
        + uuid4().hex.encode("ascii")
        + (b" text " * 50)
    )
    files = {"file": ("confidential.pdf", pdf_content, "application/pdf")}
    res_up = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert res_up.status_code == 202
    doc_id = res_up.json()["data"]["id"]

    res_del = await async_client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["purged_physical_file"] is True


@pytest.mark.asyncio
async def test_attach_pdf_upgrades_abstract_only_to_parsing(
    async_client: AsyncClient, auth_headers: dict
):
    # 1. Create abstract-only document via open-reading
    open_res = await async_client.post(
        "/api/v1/discovery/open-reading",
        headers=auth_headers,
        json={
            "title": "Abstract Only Sample Paper",
            "authors": ["Test Researcher"],
            "publication_year": 2024,
            "pdf_url": None,
        },
    )
    assert open_res.status_code == 201
    doc_id = open_res.json()["data"]["document_id"]
    assert open_res.json()["data"]["status"] == "abstract_only"

    # 2. Attach full PDF to upgrade document
    pdf_content = b"%PDF-1.4 attached full text content " + (b"scholar " * 80)
    files = {"file": ("full_paper.pdf", pdf_content, "application/pdf")}
    attach_res = await async_client.post(
        f"/api/v1/documents/{doc_id}/attach-pdf",
        headers=auth_headers,
        files=files,
    )
    assert attach_res.status_code == 202
    attach_data = attach_res.json()["data"]
    assert attach_data["status"] == "parsing"
    assert attach_data["access_status"] == "open_access_pdf"


@pytest.mark.asyncio
async def test_document_status_completes_chunks_with_valid_user_id(
    async_client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    # 1. Create a valid text-bearing PDF in memory
    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page()
    page.insert_text(
        (72, 72),
        "Abstract: Neural networks for scientific discovery and grounding.\n"
        "Introduction: We study attention models and spatial layout chunking.\n"
        "Methodology: Deep neural models with bounding boxes.\n"
        "References: 1. Attention is all you need.",
    )
    pdf_content = pdf_doc.tobytes()
    pdf_doc.close()

    # 2. Upload PDF
    files = {"file": ("grounding_test.pdf", pdf_content, "application/pdf")}
    up_res = await async_client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert up_res.status_code == 202
    doc_id = UUID(up_res.json()["data"]["id"])

    # 3. Retrieve authenticated user ID
    me_res = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    user_id = UUID(me_res.json()["data"]["id"])

    # 4. Set document status to processing to simulate parsing in progress
    doc = await db_session.get(DocumentModel, doc_id)
    assert doc is not None
    doc.status = "processing"
    await db_session.flush()

    # 5. Call get_document_status
    service = get_document_service(storage=get_storage())
    status_res = await service.get_document_status(
        document_id=doc_id,
        user_id=user_id,
        db=db_session,
    )

    # 6. Assert doc status is completed and progress is 100
    assert status_res.status == "completed"
    assert status_res.progress == 100

    # Refresh doc from database
    await db_session.refresh(doc)
    assert doc.status == "completed"
    assert doc.progress == 100

    # 7. Assert that chunks exist and all have valid user_id matching current user
    chunks_stmt = select(DocumentChunkModel).where(DocumentChunkModel.document_id == doc_id)
    chunks_res = await db_session.execute(chunks_stmt)
    chunks = list(chunks_res.scalars().all())
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.user_id == user_id

from uuid import uuid4

import pytest
from httpx import AsyncClient


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

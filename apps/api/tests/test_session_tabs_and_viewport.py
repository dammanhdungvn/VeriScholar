import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_tab_limit_and_active_reassignment(
    async_client: AsyncClient,
    auth_headers: dict,
):
    res_sess = await async_client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"title": "Multi-Tab Test"},
    )
    assert res_sess.status_code == 201
    session_id = res_sess.json()["data"]["id"]

    doc_ids = []
    for idx in range(5):
        pdf_bytes = f"%PDF-1.4 sample paper {idx} ".encode() + (b"word " * 100)
        res_doc = await async_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": (f"paper_{idx}.pdf", pdf_bytes, "application/pdf")},
        )
        assert res_doc.status_code in (200, 201, 202)
        doc_id = res_doc.json()["data"]["id"]
        doc_ids.append(doc_id)
        res_add = await async_client.post(
            f"/api/v1/sessions/{session_id}/documents",
            headers=auth_headers,
            json={"source_type": "document_id", "document_id": doc_id},
        )
        assert res_add.status_code in (200, 201, 202)

    # Adding duplicate document must return 409 REFERENCE_ALREADY_IN_SESSION
    res_dup = await async_client.post(
        f"/api/v1/sessions/{session_id}/documents",
        headers=auth_headers,
        json={"source_type": "document_id", "document_id": doc_ids[0]},
    )
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "REFERENCE_ALREADY_IN_SESSION"

    # Adding 6th document must return 409 MAX_SESSION_DOCUMENTS_REACHED
    extra_pdf = b"%PDF-1.4 extra paper 6 " + (b"word " * 100)
    res_extra = await async_client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("paper_6.pdf", extra_pdf, "application/pdf")},
    )
    extra_id = res_extra.json()["data"]["id"]
    res_conflict = await async_client.post(
        f"/api/v1/sessions/{session_id}/documents",
        headers=auth_headers,
        json={"source_type": "document_id", "document_id": extra_id},
    )
    assert res_conflict.status_code == 409
    assert res_conflict.json()["error"]["code"] == "MAX_SESSION_DOCUMENTS_REACHED"

    # Set active_document_id to doc_ids[0]
    await async_client.patch(
        f"/api/v1/sessions/{session_id}/viewport",
        headers=auth_headers,
        json={
            "active_document_id": doc_ids[0],
            "viewport_state": {"page": 1, "zoom_ratio": 1.0, "scroll_top": 0},
        },
    )

    # Closing active tab deletes association and reassigns active_document_id
    res_close = await async_client.delete(
        f"/api/v1/sessions/{session_id}/documents/{doc_ids[0]}",
        headers=auth_headers,
    )
    assert res_close.status_code == 204

    # Verify session detail now has remaining docs and reassigned active_document_id
    res_detail = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )
    assert res_detail.status_code == 200
    detail_data = res_detail.json()["data"]
    assert doc_ids[0] not in detail_data["document_ids"]
    assert len(detail_data["document_ids"]) == 4
    assert detail_data["active_document_id"] in doc_ids[1:]

"""End-to-End Integration test for all 9 Swagger UI Module 1 (Documents) Endpoints.

Tests all operations defined in docs/vi/swagger.md:
1. POST   /api/v1/documents                      - Upload PDF
2. GET    /api/v1/documents                      - List documents (paginated)
3. GET    /api/v1/documents/{id}                 - Document detail & spatial metadata
4. GET    /api/v1/documents/{id}/file            - Binary stream (200 OK & 206 Partial Content)
5. POST   /api/v1/documents/{id}:parse           - Trigger parsing pipeline
6. GET    /api/v1/documents/{id}/status          - Polling parsing progress
7. POST   /api/v1/documents/{id}:extract-references - Extract references (20 items)
8. POST   /api/v1/documents/{id}:star            - Star / persist document in library
9. DELETE /api/v1/documents/{id}                 - Delete document (Zero-Retention)
"""

import io
from pathlib import Path

import httpx
import pytest
from api import app


@pytest.mark.anyio
async def test_swagger_module1_full_lifecycle() -> None:
    """Execute complete lifecycle covering all 9 Module 1 Swagger endpoints in sequence."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"x-user-id": "usr_swagger_e2e_tester"}

        # Read actual PDF file
        pdf_path = Path("data/papers/2504.19754v1.pdf")
        if not pdf_path.exists():
            pytest.skip("data/papers/2504.19754v1.pdf not found")
        pdf_bytes = pdf_path.read_bytes()

        # ----------------------------------------------------------------------
        # 1. [POST] /api/v1/documents (Upload PDF)
        # ----------------------------------------------------------------------
        files = {"file": ("2504.19754v1.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        r1 = await client.post("/api/v1/documents", files=files, headers=headers)
        assert r1.status_code == 201, f"POST /api/v1/documents failed: {r1.text}"
        body1 = r1.json()
        assert body1["success"] is True
        doc_id = body1["data"]["id"]
        assert body1["data"]["status"] in ("uploaded", "completed")
        assert "self_url" in body1["data"]["links"] or "self" in body1["data"]["links"]

        # ----------------------------------------------------------------------
        # 2. [GET] /api/v1/documents (List Documents Paginated)
        # ----------------------------------------------------------------------
        r2 = await client.get("/api/v1/documents?page=1&per_page=10", headers=headers)
        assert r2.status_code == 200, f"GET /api/v1/documents failed: {r2.text}"
        body2 = r2.json()
        assert body2["success"] is True
        assert body2["meta"]["page"] == 1
        assert body2["meta"]["per_page"] == 10
        assert body2["meta"]["total"] >= 1
        items = body2["data"] if isinstance(body2["data"], list) else body2["data"].get("items", [])
        assert any(item["id"] == doc_id for item in items)

        # ----------------------------------------------------------------------
        # 3. [GET] /api/v1/documents/{id} (Document Detail & Spatial Metadata)
        # ----------------------------------------------------------------------
        r3 = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert r3.status_code == 200, f"GET /api/v1/documents/{doc_id} failed: {r3.text}"
        body3 = r3.json()
        assert body3["success"] is True
        assert body3["data"]["id"] == doc_id
        assert body3["data"]["filename"] == "2504.19754v1.pdf"
        assert body3["data"]["file_size_bytes"] > 0
        assert "pages_metadata" in body3["data"]

        # ----------------------------------------------------------------------
        # 4. [GET] /api/v1/documents/{id}/file (Full & Byte Range Stream)
        # ----------------------------------------------------------------------
        # 4.1 Full Content
        r4_full = await client.get(f"/api/v1/documents/{doc_id}/file", headers=headers)
        assert r4_full.status_code == 200, f"GET /file (full) failed: {r4_full.status_code}"
        assert r4_full.headers.get("accept-ranges") == "bytes"
        assert len(r4_full.content) == len(pdf_bytes)

        # 4.2 Partial Byte-Range Content (RFC 7233)
        r4_range = await client.get(
            f"/api/v1/documents/{doc_id}/file",
            headers={**headers, "Range": "bytes=0-1023"},
        )
        assert r4_range.status_code == 206, f"GET /file (range) failed: {r4_range.status_code}"
        assert r4_range.headers.get("content-range") is not None
        assert len(r4_range.content) == 1024

        # ----------------------------------------------------------------------
        # 5. [POST] /api/v1/documents/{id}:parse (Trigger Parse Pipeline)
        # ----------------------------------------------------------------------
        r5 = await client.post(
            f"/api/v1/documents/{doc_id}:parse",
            json={"chunk_size": 512, "chunk_overlap": 50, "extract_tables": True},
            headers=headers,
        )
        assert r5.status_code in (
            200,
            202,
        ), f"POST /documents/{doc_id}:parse failed: {r5.text}"
        body5 = r5.json()
        assert body5["success"] is True
        assert body5["data"]["status"] in ("processing", "completed")

        # ----------------------------------------------------------------------
        # 6. [GET] /api/v1/documents/{id}/status (Status Polling & Progress)
        # ----------------------------------------------------------------------
        r6 = await client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
        assert r6.status_code == 200, f"GET /documents/{doc_id}/status failed: {r6.text}"
        body6 = r6.json()
        assert body6["success"] is True
        assert "stages_detail" in body6["data"]
        assert 0 <= body6["data"]["progress"] <= 100

        # ----------------------------------------------------------------------
        # 7. [POST] /api/v1/documents/{id}:extract-references (Extract References)
        # ----------------------------------------------------------------------
        r7 = await client.post(
            f"/api/v1/documents/{doc_id}:extract-references",
            json={"force_reextract": True},
            headers=headers,
        )
        assert r7.status_code == 200, (
            f"POST /documents/{doc_id}:extract-references failed: {r7.text}"
        )
        body7 = r7.json()
        assert body7["success"] is True
        assert body7["data"]["document_id"] == doc_id
        assert body7["data"]["total_extracted"] == 20
        assert len(body7["data"]["references"]) == 20

        # Verify parsed structure of extracted references
        ref1 = body7["data"]["references"][0]
        assert ref1["ref_index"] == 1
        assert ref1["parsed"]["arxiv_id"] == "2404.14219"
        assert len(ref1["parsed"]["authors"]) > 0

        # Verify no false-positive artifacts from wrapped links
        raw_texts = [r["raw_text"] for r in body7["data"]["references"]]
        assert "14673" not in raw_texts

        # ----------------------------------------------------------------------
        # 8. [POST] /api/v1/documents/{id}:star (Personal Library Persistence)
        # ----------------------------------------------------------------------
        r8 = await client.post(
            f"/api/v1/documents/{doc_id}:star",
            json={"folder_id": None},
            headers=headers,
        )
        assert r8.status_code == 200, f"POST /documents/{doc_id}:star failed: {r8.text}"
        body8 = r8.json()
        assert body8["success"] is True
        assert body8["data"]["is_persistent"] is True

        # ----------------------------------------------------------------------
        # 9. [DELETE] /api/v1/documents/{id} (Zero-Retention Deletion)
        # ----------------------------------------------------------------------
        r9 = await client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
        assert r9.status_code == 204, f"DELETE /documents/{doc_id} failed: {r9.status_code}"

        # Follow-up check: must return 404
        r9_verify = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert r9_verify.status_code == 404, f"Document {doc_id} still exists after deletion"

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

from __future__ import annotations

import io
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import httpx
import pytest
from api import app
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_storage
from core.adapters.storage.local import LocalStorageAdapter
from core.ports.storage import IBlobStoragePort
from sqlalchemy.ext.asyncio import AsyncSession


class InMemorySwaggerModule1Store:
    """In-memory SQLite/Postgres test double supporting all 9 Module 1 operations."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.blobs: dict[str, DocumentStorageBlobModel] = {}
        self.references: dict[UUID, list[ReferenceItemModel]] = {}
        self.chunks: dict[UUID, list[DocumentChunkModel]] = {}
        self.users: dict[UUID, UserModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            if obj.created_at is None:
                obj.created_at = now
            if obj.updated_at is None:
                obj.updated_at = now
            if getattr(obj, "chunk_count", None) is None:
                obj.chunk_count = 0
            if getattr(obj, "pages_metadata", None) is None:
                obj.pages_metadata = []
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentStorageBlobModel):
            self.blobs[obj.content_hash] = obj
        elif isinstance(obj, ReferenceItemModel):
            if obj.document_id not in self.references:
                self.references[obj.document_id] = []
            self.references[obj.document_id].append(obj)
        elif isinstance(obj, DocumentChunkModel):
            if obj.document_id not in self.chunks:
                self.chunks[obj.document_id] = []
            self.chunks[obj.document_id].append(obj)
        elif isinstance(obj, UserModel):
            self.users[obj.id] = obj

    def add_all(self, objs: list[object]) -> None:
        for obj in objs:
            self.add(obj)

    async def delete(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents.pop(obj.id, None)
            self.references.pop(obj.id, None)
            self.chunks.pop(obj.id, None)
        elif isinstance(obj, DocumentStorageBlobModel):
            self.blobs.pop(obj.content_hash, None)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    def begin_nested(self) -> Any:
        class _NestedContext:
            async def __aenter__(self) -> Any:
                return self

            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
                return False

        return _NestedContext()

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> MagicMock:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        mock_res = MagicMock()

        # 1. Count queries
        if "count(" in stmt_str.lower():
            cnt = len(self.documents) if "documents" in stmt_str else 0
            mock_res.scalar_one.return_value = cnt
            mock_res.scalar.return_value = cnt
            return mock_res

        # 2. Users lookup
        if "FROM users" in stmt_str:
            target_user_id = params.get("id_1") or params.get("id") or DEFAULT_DEV_USER_ID
            user = self.users.get(target_user_id)
            if user is None:
                user = UserModel(
                    id=target_user_id,
                    email="tester@verischolar.org",
                    full_name="Swagger Tester",
                    hashed_password="hash",
                    is_active=True,
                    role="researcher",
                )
                self.users[user.id] = user
            mock_res.scalar_one_or_none.return_value = user
            mock_res.scalars.return_value.all.return_value = [user]
            return mock_res

        # 3. Storage blobs lookup
        if "FROM document_storage_blobs" in stmt_str:
            target_hash = params.get("content_hash_1") or params.get("content_hash")
            blob = self.blobs.get(target_hash) if target_hash else None
            mock_res.scalar_one_or_none.return_value = blob
            return mock_res

        # 4. References delete
        if "DELETE FROM reference_items" in stmt_str:
            target_doc_id = params.get("document_id_1") or params.get("document_id")
            if target_doc_id in self.references:
                self.references[target_doc_id] = []
            return mock_res

        # 5. References select
        if "FROM reference_items" in stmt_str:
            target_doc_id = params.get("document_id_1") or params.get("document_id")
            items = self.references.get(target_doc_id, [])
            mock_res.scalars.return_value.all.return_value = list(items)
            return mock_res

        # 6. Chunks delete
        if "DELETE FROM document_chunks" in stmt_str:
            target_doc_id = params.get("document_id_1") or params.get("document_id")
            if target_doc_id in self.chunks:
                self.chunks.pop(target_doc_id, None)
            return mock_res

        # 7. Summaries delete
        if "DELETE FROM document_summaries" in stmt_str:
            return mock_res

        # 8. Document lookup & paginated list
        if "FROM documents" in stmt_str:
            target_id = params.get("id_1") or params.get("id")
            target_hash = params.get("content_hash_1") or params.get("content_hash")

            if target_id is not None:
                doc = self.documents.get(target_id)
                mock_res.scalar_one_or_none.return_value = doc
                mock_res.scalars.return_value.all.return_value = [doc] if doc else []
            elif target_hash is not None:
                doc = next(
                    (d for d in self.documents.values() if d.content_hash == target_hash),
                    None,
                )
                mock_res.scalar_one_or_none.return_value = doc
                mock_res.scalars.return_value.all.return_value = [doc] if doc else []
            else:
                docs = list(self.documents.values())
                mock_res.scalars.return_value.all.return_value = docs
                mock_res.scalar_one_or_none.return_value = docs[0] if docs else None
            return mock_res

        return mock_res


@pytest.mark.asyncio
async def test_swagger_module1_full_lifecycle(tmp_path: Path) -> None:
    """Execute complete lifecycle covering all 9 Module 1 Swagger endpoints in sequence."""
    in_memory_store = InMemorySwaggerModule1Store()
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield in_memory_store  # type: ignore[misc]

    def override_get_storage() -> IBlobStoragePort:
        return storage

    test_user = UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="swagger_tester@verischolar.org",
        full_name="Swagger Tester",
        hashed_password="hash",
        is_active=True,
        role="researcher",
    )
    in_memory_store.add(test_user)

    async def override_get_current_user() -> UserModel:
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = override_get_storage
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            headers = {"x-user-id": str(DEFAULT_DEV_USER_ID)}

            # Read actual PDF file
            pdf_path = Path("data/papers/2504.19754v1.pdf")
            if not pdf_path.exists():
                alt_name = (
                    "Reconstructing Context Evaluating Advanced Chunking "
                    "Strategies for Retrieval-Augmented Generation.pdf"
                )
                pdf_path = Path("data/papers") / alt_name
            if not pdf_path.exists():
                candidates = list(Path("data/papers").glob("*.pdf"))
                if candidates:
                    pdf_path = candidates[0]
                else:
                    pytest.skip("No sample PDF found in data/papers")
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
            items = (
                body2["data"] if isinstance(body2["data"], list) else body2["data"].get("items", [])
            )
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
    finally:
        app.dependency_overrides.clear()

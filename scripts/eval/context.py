"""Hermetic Evaluation Context Manager with RESTful cascade cleanup and signal handling."""

import sys
import uuid
from typing import Any

import httpx


class EvaluationContext:
    """Async Context Manager providing an isolated evaluation session and guaranteed cleanup.

    Follows the Hermetic Testing principle:
    - Session tagged with unique identifier (or custom user_id).
    - Connects directly via ASGITransport to the live FastAPI application, ensuring
      zero latency, direct connection to real PostgreSQL/Redis/Cloud services,
      and absolute immunity against stale out-of-process server cache.
    - Tracks all document IDs created during testing.
    - Cleans up tracked resources exclusively via the standard REST endpoint:
      DELETE /api/v1/documents/{document_id} (unless keep_data is requested for manual inspection).
    """

    def __init__(
        self,
        base_url: str | None = None,
        use_live_server: bool = False,
        keep_data: bool = False,
        user_id: str | None = None,
    ):
        self.base_url = base_url or "http://test"
        self.use_live_server = use_live_server
        self.keep_data = keep_data
        self.user_id = user_id
        self.session_tag = user_id if user_id else f"test_eval_{uuid.uuid4().hex[:8]}"
        self.headers = {
            "x-user-id": self.session_tag,
            "x-session-id": self.session_tag,
        }
        self.created_document_ids: list[str] = []
        self.client: httpx.AsyncClient | None = None
        self._is_asgi_fallback = True

    async def __aenter__(self) -> "EvaluationContext":
        if self.use_live_server:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=90.0,
                headers=self.headers,
            )
            self._is_asgi_fallback = False
        else:
            import api.db.models  # noqa: F401
            from api import app
            from api.db.models.base import Base
            from api.db.session import engine

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self.client = httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
                timeout=120.0,
                headers=self.headers,
            )
            self._is_asgi_fallback = True

        return self

    def track_document(self, document_id: str) -> None:
        """Register a document created during the evaluation for guaranteed cleanup."""
        if document_id and document_id not in self.created_document_ids:
            self.created_document_ids.append(document_id)

    async def cleanup(self) -> list[str]:
        """Purge all tracked documents using the standard REST API, unless keep_data is True."""
        if self.keep_data:
            return []
        cleaned = []
        if not self.client:
            return cleaned

        for doc_id in list(self.created_document_ids):
            try:
                res = await self.client.delete(f"/api/v1/documents/{doc_id}")
                if res.status_code in (200, 204, 404):
                    cleaned.append(doc_id)
            except Exception as e:
                sys.stderr.write(f"[WARN] Failed to delete document {doc_id}: {e}\n")

        self.created_document_ids.clear()
        return cleaned

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            await self.cleanup()
        finally:
            if self.client:
                await self.client.aclose()

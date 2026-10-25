import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from api import app
import api.db.models as db_models


@pytest.mark.asyncio
async def test_removed_endpoints_not_registered() -> None:
    fake_id = str(uuid.uuid4())
    removed_routes = [
        ("POST", f"/api/v1/drafts/{fake_id}/verify-facts"),
        ("POST", f"/api/v1/drafts/{fake_id}/share"),
        ("GET", f"/api/v1/drafts/{fake_id}/share"),
        ("POST", f"/api/v1/drafts/{fake_id}/comments"),
        ("GET", f"/api/v1/drafts/{fake_id}/comments"),
        ("POST", f"/api/v1/drafts/{fake_id}:export-overleaf"),
        ("POST", f"/api/v1/drafts/{fake_id}/overleaf"),
        ("GET", f"/api/v1/drafts/{fake_id}/overleaf-launch"),
        ("POST", f"/api/v1/drafts/{fake_id}/associative-suggestions"),
        ("POST", "/api/v1/folders/comparison-matrix"),
        ("POST", f"/api/v1/folders/{fake_id}/comparison-matrix"),
        ("GET", f"/api/v1/documents/{fake_id}/export-pdf"),
        ("POST", f"/api/v1/sessions/{fake_id}:export-bundle"),
        ("GET", f"/api/v1/sessions/{fake_id}/citation-graph"),
        ("POST", "/api/v1/notes:synthesize"),
        ("GET", "/events"),
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for method, path in removed_routes:
            resp = await client.request(method, path)
            assert resp.status_code in (404, 405), f"Expected 404/405 for {method} {path}, got {resp.status_code}"


def test_removed_db_models_absent() -> None:
    assert not hasattr(db_models, "DraftCommentModel")
    assert not hasattr(db_models, "NoteSynthesisModel")
    assert not hasattr(db_models, "CitationEdgeModel")

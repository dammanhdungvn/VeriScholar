"""SEV-1 Security Incident Test Suite: Session Authentication & Multi-Tenant Isolation.

Verifies:
- Case 1: Unauthenticated client (no token) -> Blocked with HTTP 401 UNAUTHORIZED on all endpoints.
- Case 1b: External X-User-Id spoofing attempt without token is rejected with 401 in live mode.
- Case 2: Tenant Isolation / BOLA / IDOR defense: User A accessing User B's session receives 404 NOT FOUND.
- Case 3: Legitimate Owner: User B accessing own session receives HTTP 200 OK.
"""

import os
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.session import get_db
from api.deps import get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def session_security_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Provide isolated in-memory SQLite database and AsyncClient."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client, session_maker
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_case_1_unauthenticated_requests_blocked_with_401() -> None:
    """Case 1: Client without Authorization Bearer Token receives 401 Unauthorized across all endpoints."""
    async with session_security_test_context() as (client, _):
        random_id = uuid4()

        # 1. GET /sessions
        res_list = await client.get("/api/v1/sessions")
        assert res_list.status_code == 401
        assert res_list.json()["error"]["code"] == "UNAUTHORIZED"

        # 2. POST /sessions
        res_create = await client.post("/api/v1/sessions", json={"title": "Unauthorized Session"})
        assert res_create.status_code == 401
        assert res_create.json()["error"]["code"] == "UNAUTHORIZED"

        # 3. GET /sessions/{id}
        res_detail = await client.get(f"/api/v1/sessions/{random_id}")
        assert res_detail.status_code == 401
        assert res_detail.json()["error"]["code"] == "UNAUTHORIZED"

        # 4. PATCH /sessions/{id}
        res_patch = await client.patch(
            f"/api/v1/sessions/{random_id}",
            json={"title": "Hacked Title"},
            headers={"If-Match": '"v1"'},
        )
        assert res_patch.status_code == 401
        assert res_patch.json()["error"]["code"] == "UNAUTHORIZED"

        # 5. PATCH /sessions/{id}/viewport
        res_viewport = await client.patch(
            f"/api/v1/sessions/{random_id}/viewport",
            json={"viewport_state": {"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}},
            headers={"If-Match": '"v1"'},
        )
        assert res_viewport.status_code == 401
        assert res_viewport.json()["error"]["code"] == "UNAUTHORIZED"

        # 6. DELETE /sessions/{id}
        res_delete = await client.delete(f"/api/v1/sessions/{random_id}")
        assert res_delete.status_code == 401
        assert res_delete.json()["error"]["code"] == "UNAUTHORIZED"

        # 7. POST /sessions/{id}/documents
        res_add_doc = await client.post(
            f"/api/v1/sessions/{random_id}/documents",
            json={"source_type": "url", "url": "https://arxiv.org/abs/1706.03762"},
        )
        assert res_add_doc.status_code == 401
        assert res_add_doc.json()["error"]["code"] == "UNAUTHORIZED"

        # 8. GET /sessions/{id}/messages
        res_messages = await client.get(f"/api/v1/sessions/{random_id}/messages")
        assert res_messages.status_code == 401
        assert res_messages.json()["error"]["code"] == "UNAUTHORIZED"

        # 9. DELETE /sessions/{id}/messages
        res_clear_msg = await client.delete(f"/api/v1/sessions/{random_id}/messages")
        assert res_clear_msg.status_code == 401
        assert res_clear_msg.json()["error"]["code"] == "UNAUTHORIZED"

        # 10. GET /sessions/{id}/citation-graph
        res_graph = await client.get(f"/api/v1/sessions/{random_id}/citation-graph")
        assert res_graph.status_code == 401
        assert res_graph.json()["error"]["code"] == "UNAUTHORIZED"

        # 11. POST /sessions/{id}/references:ingest
        res_ingest = await client.post(
            f"/api/v1/sessions/{random_id}/references:ingest",
            json={"document_id": str(uuid4()), "selected_ref_indices": [0]},
        )
        assert res_ingest.status_code == 401
        assert res_ingest.json()["error"]["code"] == "UNAUTHORIZED"

        # 12. POST /sessions/{id}:export-bundle
        res_bundle = await client.post(f"/api/v1/sessions/{random_id}:export-bundle")
        assert res_bundle.status_code == 401
        assert res_bundle.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_case_1b_x_user_id_blocked_outside_test_harness() -> None:
    """Case 1b: Verify that X-User-Id header without token is rejected when not in test harness."""
    original_val = os.environ.pop("PYTEST_CURRENT_TEST", None)
    try:
        async with session_security_test_context() as (client, _):
            res = await client.get(
                f"/api/v1/sessions/{uuid4()}",
                headers={"X-User-Id": "00000000-0000-0000-0000-000000000001"},
            )
            assert res.status_code == 401, "X-User-Id must be rejected outside test harness"
            assert res.json()["error"]["code"] == "UNAUTHORIZED"
    finally:
        if original_val is not None:
            os.environ["PYTEST_CURRENT_TEST"] = original_val


@pytest.mark.asyncio
async def test_case_2_and_3_tenant_isolation_and_legitimate_owner_access() -> None:
    """Verify Case 2 (User A accessing User B receives 404) and Case 3 (User B owner receives 200)."""
    async with session_security_test_context() as (client, session_maker):
        # 1. Register User A (Alice)
        reg_a = await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Alice Scholar",
                "email": "alice@security.org",
                "password": "PasswordAlice123!",
            },
        )
        assert reg_a.status_code == 201
        token_a = reg_a.json()["data"]["tokens"]["access_token"]
        user_a_id = UUID(reg_a.json()["data"]["user"]["id"])

        # 2. Register User B (Bob)
        reg_b = await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Bob Researcher",
                "email": "bob@security.org",
                "password": "PasswordBob123!",
            },
        )
        assert reg_b.status_code == 201
        token_b = reg_b.json()["data"]["tokens"]["access_token"]
        user_b_id = UUID(reg_b.json()["data"]["user"]["id"])
        assert user_a_id != user_b_id

        # 3. Create a session and document owned by Bob (User B)
        session_b_id = uuid4()
        doc_b_id = uuid4()

        async with session_maker() as db_session:
            doc_b = DocumentModel(
                id=doc_b_id,
                user_id=user_b_id,
                filename="bob_secret_paper.pdf",
                title="Bob Confidential Research",
                content_hash="b" * 64,
                file_size_bytes=2048,
                status="completed",
                is_persistent=True,
            )
            db_session.add(doc_b)

            session_b = ResearchSessionModel(
                id=session_b_id,
                user_id=user_b_id,
                title="Bob Private Session",
                active_document_id=doc_b_id,
                viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
                active_tab="chat",
                is_archived=False,
                version=1,
            )
            db_session.add(session_b)

            link = SessionDocumentModel(
                session_id=session_b_id,
                document_id=doc_b_id,
                display_order=0,
            )
            db_session.add(link)
            await db_session.commit()

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # ----------------------------------------------------------------------
        # CASE 2: User A attempts to access User B's session -> MUST BE 404 NOT FOUND
        # ----------------------------------------------------------------------
        # Detail
        res_a_get = await client.get(f"/api/v1/sessions/{session_b_id}", headers=headers_a)
        assert res_a_get.status_code == 404
        assert res_a_get.json()["error"]["code"] == "SESSION_NOT_FOUND"

        # Update metadata
        res_a_patch = await client.patch(
            f"/api/v1/sessions/{session_b_id}",
            headers={**headers_a, "If-Match": '"v1"'},
            json={"title": "Hacked Title"},
        )
        assert res_a_patch.status_code == 404

        # Update viewport
        res_a_viewport = await client.patch(
            f"/api/v1/sessions/{session_b_id}/viewport",
            headers={**headers_a, "If-Match": '"v1"'},
            json={"viewport_state": {"page": 2, "zoom_ratio": 1.5, "scroll_top": 100.0}},
        )
        assert res_a_viewport.status_code == 404

        # Messages history
        res_a_messages = await client.get(
            f"/api/v1/sessions/{session_b_id}/messages", headers=headers_a
        )
        assert res_a_messages.status_code == 404

        # Citation graph
        res_a_graph = await client.get(
            f"/api/v1/sessions/{session_b_id}/citation-graph", headers=headers_a
        )
        assert res_a_graph.status_code == 404

        # Delete session
        res_a_delete = await client.delete(f"/api/v1/sessions/{session_b_id}", headers=headers_a)
        assert res_a_delete.status_code == 404

        # Clear messages
        res_a_clear_msg = await client.delete(
            f"/api/v1/sessions/{session_b_id}/messages", headers=headers_a
        )
        assert res_a_clear_msg.status_code == 404

        # User A session list must NOT contain Bob's session
        res_a_list = await client.get("/api/v1/sessions", headers=headers_a)
        assert res_a_list.status_code == 200
        a_session_ids = [s["id"] for s in res_a_list.json()["data"]]
        assert str(session_b_id) not in a_session_ids

        # ----------------------------------------------------------------------
        # CASE 3: User B (Legitimate Owner) accesses own session -> 200 OK
        # ----------------------------------------------------------------------
        # Detail
        res_b_get = await client.get(f"/api/v1/sessions/{session_b_id}", headers=headers_b)
        assert res_b_get.status_code == 200
        b_data = res_b_get.json()["data"]
        assert b_data["id"] == str(session_b_id)
        assert b_data["title"] == "Bob Private Session"
        assert len(b_data["documents"]) == 1
        assert b_data["documents"][0]["id"] == str(doc_b_id)

        # User B session list includes session_b
        res_b_list = await client.get("/api/v1/sessions", headers=headers_b)
        assert res_b_list.status_code == 200
        b_session_ids = [s["id"] for s in res_b_list.json()["data"]]
        assert str(session_b_id) in b_session_ids

        # Update metadata
        res_b_patch = await client.patch(
            f"/api/v1/sessions/{session_b_id}",
            headers={**headers_b, "If-Match": '"v1"'},
            json={"title": "Bob Renamed Session"},
        )
        assert res_b_patch.status_code == 200
        assert res_b_patch.json()["data"]["title"] == "Bob Renamed Session"

        # Update viewport
        res_b_viewport = await client.patch(
            f"/api/v1/sessions/{session_b_id}/viewport",
            headers={**headers_b, "If-Match": '"v2"'},
            json={"viewport_state": {"page": 3, "zoom_ratio": 1.25, "scroll_top": 50.0}},
        )
        assert res_b_viewport.status_code == 200
        assert res_b_viewport.json()["data"]["viewport_state"]["page"] == 3

        # Messages list
        res_b_messages = await client.get(
            f"/api/v1/sessions/{session_b_id}/messages", headers=headers_b
        )
        assert res_b_messages.status_code == 200
        assert res_b_messages.json()["data"] == []

        # Citation graph
        res_b_graph = await client.get(
            f"/api/v1/sessions/{session_b_id}/citation-graph", headers=headers_b
        )
        assert res_b_graph.status_code == 200

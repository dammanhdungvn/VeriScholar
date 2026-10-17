"""Integration test suite for Draft Peer Review Comments & Annotations (PRD §3.2).

Validates:
- Full CRUD for peer review comments and line annotations.
- Threaded replies hierarchy (parent_id linking and nested replies response).
- RBAC permissions across Owner, Editor, Commenter, and Viewer roles.
- Commenter constraint: Can comment and resolve, but strictly forbidden from editing draft source.
- Viewer constraint: Can read comments, but strictly forbidden from creating or resolving comments.
- Multi-tenant isolation: Unshared users cannot access, create, or mutate comments.
- Cascade deletion: Deleting a draft cascades and deletes all associated comments.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.draft import DraftCommentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def comments_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Provide isolated in-memory SQLite database and AsyncClient for comments testing."""
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, session_maker

    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


async def create_test_user(
    session_maker: async_sessionmaker[AsyncSession],
    email: str = "researcher@verischolar.org",
    full_name: str = "Alan Turing",
) -> tuple[UserModel, str]:
    """Helper to create an active test user in DB and return (user, jwt_token)."""
    async with session_maker() as session:
        user = UserModel(
            id=uuid4(),
            email=email,
            full_name=full_name,
            hashed_password="mock_hashed_password",
            is_active=True,
            is_verified=True,
            role="researcher",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = AuthService.create_token(
        payload={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta_seconds=3600,
    )
    return user, token


@pytest.mark.asyncio
async def test_create_and_list_draft_comments() -> None:
    """Verify creating top-level line annotations and listing them."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner@verischolar.org")
        headers = {"Authorization": f"Bearer {owner_token}"}

        # 1. Create a draft
        create_res = await client.post(
            "/api/v1/drafts",
            json={
                "title": "Quantum Error Correction",
                "content": "\\section{Intro}\nSurface codes have a high fault tolerance threshold.",
                "format": "latex",
            },
            headers=headers,
        )
        assert create_res.status_code == 201
        draft_id = create_res.json()["data"]["id"]

        # 2. Post a line annotation comment
        comment_payload = {
            "start_offset": 16,
            "end_offset": 29,
            "selected_text": "Surface codes",
            "comment_text": "Should explicitly specify the 1% threshold reference.",
        }
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json=comment_payload,
            headers=headers,
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["draft_id"] == draft_id
        assert data["author_id"] == str(owner.id)
        assert data["start_offset"] == 16
        assert data["end_offset"] == 29
        assert data["selected_text"] == "Surface codes"
        assert data["comment_text"] == "Should explicitly specify the 1% threshold reference."
        assert data["is_resolved"] is False
        assert data["parent_id"] is None
        assert data["replies"] == []
        comment_id = data["id"]

        # 3. List comments
        list_res = await client.get(f"/api/v1/drafts/{draft_id}/comments", headers=headers)
        assert list_res.status_code == 200
        list_data = list_res.json()["data"]
        assert list_data["total"] == 1
        assert len(list_data["items"]) == 1
        assert list_data["items"][0]["id"] == comment_id


@pytest.mark.asyncio
async def test_threaded_replies_hierarchy() -> None:
    """Verify threaded replies correctly attach to parent comment in tree representation."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "author@verischolar.org")
        editor, editor_token = await create_test_user(session_maker, "editor@verischolar.org")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        editor_headers = {"Authorization": f"Bearer {editor_token}"}

        # 1. Create draft and invite editor
        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Threaded Paper", "content": "Body text", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        share_res = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": editor.email, "permission": "editor"},
            headers=owner_headers,
        )
        assert share_res.status_code == 200

        # 2. Owner posts root comment
        root_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={
                "start_offset": 0,
                "end_offset": 4,
                "selected_text": "Body",
                "comment_text": "Can we expand this section?",
            },
            headers=owner_headers,
        )
        assert root_res.status_code == 201
        root_comment_id = root_res.json()["data"]["id"]

        # 3. Editor posts reply referencing root comment ID
        reply_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={
                "comment_text": "I will draft the expanded subsection today.",
                "parent_id": root_comment_id,
            },
            headers=editor_headers,
        )
        assert reply_res.status_code == 201
        reply_data = reply_res.json()["data"]
        assert reply_data["parent_id"] == root_comment_id
        assert reply_data["author_id"] == str(editor.id)

        # 4. List comments and verify tree structure
        list_res = await client.get(f"/api/v1/drafts/{draft_id}/comments", headers=owner_headers)
        assert list_res.status_code == 200
        list_data = list_res.json()["data"]
        assert list_data["total"] == 2
        assert len(list_data["items"]) == 1
        root_item = list_data["items"][0]
        assert root_item["id"] == root_comment_id
        assert len(root_item["replies"]) == 1
        assert root_item["replies"][0]["id"] == reply_data["id"]
        assert root_item["replies"][0]["comment_text"] == (
            "I will draft the expanded subsection today."
        )


@pytest.mark.asyncio
async def test_update_comment_text_and_permissions() -> None:
    """Verify only original author can edit comment text, while others are rejected."""
    async with comments_test_context() as (client, session_maker):
        author, author_token = await create_test_user(session_maker, "commenter1@verischolar.org")
        collab, collab_token = await create_test_user(session_maker, "collab@verischolar.org")
        author_headers = {"Authorization": f"Bearer {author_token}"}
        collab_headers = {"Authorization": f"Bearer {collab_token}"}

        # Create draft and share
        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Draft", "content": "Text", "format": "latex"},
            headers=author_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": collab.email, "permission": "editor"},
            headers=author_headers,
        )

        # Author creates comment
        post_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Initial typo"},
            headers=author_headers,
        )
        comment_id = post_res.json()["data"]["id"]

        # Collaborator attempts to change author's comment text -> 403 Forbidden
        patch_collab_res = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
            json={"comment_text": "Malicious edit"},
            headers=collab_headers,
        )
        assert patch_collab_res.status_code == 403

        # Author updates their own text -> 200 OK
        patch_author_res = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
            json={"comment_text": "Corrected comment text"},
            headers=author_headers,
        )
        assert patch_author_res.status_code == 200
        assert patch_author_res.json()["data"]["comment_text"] == "Corrected comment text"


@pytest.mark.asyncio
async def test_resolve_and_reopen_comment() -> None:
    """Verify collaborators can resolve or reopen comments."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "lead@verischolar.org")
        reviewer, reviewer_token = await create_test_user(session_maker, "reviewer@verischolar.org")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Resolution Draft", "content": "Sample content", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # Share with commenter role
        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": reviewer.email, "permission": "commenter"},
            headers=owner_headers,
        )

        # Reviewer posts comment
        post_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Please fix equation (4)"},
            headers=reviewer_headers,
        )
        comment_id = post_res.json()["data"]["id"]

        # Owner resolves comment
        resolve_res = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
            json={"is_resolved": True},
            headers=owner_headers,
        )
        assert resolve_res.status_code == 200
        assert resolve_res.json()["data"]["is_resolved"] is True

        # Reviewer reopens comment
        reopen_res = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
            json={"is_resolved": False},
            headers=reviewer_headers,
        )
        assert reopen_res.status_code == 200
        assert reopen_res.json()["data"]["is_resolved"] is False


@pytest.mark.asyncio
async def test_delete_comment_author_and_draft_owner() -> None:
    """Verify comment author or draft owner can delete comment, while unauthorized cannot."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner2@verischolar.org")
        editor, editor_token = await create_test_user(session_maker, "editor2@verischolar.org")
        other_editor, other_token = await create_test_user(session_maker, "other@verischolar.org")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        editor_headers = {"Authorization": f"Bearer {editor_token}"}
        other_headers = {"Authorization": f"Bearer {other_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Delete Draft", "content": "Content", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": editor.email, "permission": "editor"},
            headers=owner_headers,
        )
        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": other_editor.email, "permission": "editor"},
            headers=owner_headers,
        )

        # Editor posts comment 1
        c1_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Comment to be deleted by other editor"},
            headers=editor_headers,
        )
        c1_id = c1_res.json()["data"]["id"]

        # Other editor attempts to delete comment 1 -> 403 Forbidden
        del_forbidden = await client.delete(
            f"/api/v1/drafts/{draft_id}/comments/{c1_id}",
            headers=other_headers,
        )
        assert del_forbidden.status_code == 403

        # Draft owner deletes comment 1 -> 204 No Content
        del_owner_res = await client.delete(
            f"/api/v1/drafts/{draft_id}/comments/{c1_id}",
            headers=owner_headers,
        )
        assert del_owner_res.status_code == 204

        # Editor posts comment 2 and deletes it themselves
        c2_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Comment to be deleted by self"},
            headers=editor_headers,
        )
        c2_id = c2_res.json()["data"]["id"]
        del_self_res = await client.delete(
            f"/api/v1/drafts/{draft_id}/comments/{c2_id}",
            headers=editor_headers,
        )
        assert del_self_res.status_code == 204


@pytest.mark.asyncio
async def test_commenter_rbac_cannot_edit_draft_source() -> None:
    """Verify DraftRole.COMMENTER can comment and resolve, but is strictly blocked from editing."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner_rbac@verischolar.org")
        commenter, commenter_token = await create_test_user(
            session_maker, "commenter_rbac@verischolar.org"
        )
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        commenter_headers = {"Authorization": f"Bearer {commenter_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "RBAC Protected", "content": "Original Content", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # Share with commenter role
        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": commenter.email, "permission": "commenter"},
            headers=owner_headers,
        )

        # 1. Commenter CAN post comment (201)
        post_c = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Peer review remark"},
            headers=commenter_headers,
        )
        assert post_c.status_code == 201

        # 2. Commenter CAN list comments (200)
        list_c = await client.get(f"/api/v1/drafts/{draft_id}/comments", headers=commenter_headers)
        assert list_c.status_code == 200

        # 3. Commenter CAN resolve comment (200)
        c_id = post_c.json()["data"]["id"]
        res_c = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{c_id}",
            json={"is_resolved": True},
            headers=commenter_headers,
        )
        assert res_c.status_code == 200

        # 4. Invariant: Commenter CANNOT edit draft source text (403 Forbidden)
        edit_draft = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"content": "Unauthorized tampering", "version": 1},
            headers=commenter_headers,
        )
        assert edit_draft.status_code == 403
        err_msg = edit_draft.json().get("error", {}).get("message") or edit_draft.json().get(
            "detail", {}
        ).get("message", "")
        assert "strictly forbidden from editing draft source" in err_msg


@pytest.mark.asyncio
async def test_viewer_rbac_cannot_create_or_resolve_comments() -> None:
    """Verify DraftRole.VIEWER can read comments, but is blocked from creating or resolving."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner_v@verischolar.org")
        viewer, viewer_token = await create_test_user(session_maker, "viewer_v@verischolar.org")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Viewer Protected", "content": "Body", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # Share with viewer role
        await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": viewer.email, "permission": "viewer"},
            headers=owner_headers,
        )

        # Owner creates comment
        c_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Discussion point"},
            headers=owner_headers,
        )
        c_id = c_res.json()["data"]["id"]

        # 1. Viewer CAN list comments (200)
        list_res = await client.get(f"/api/v1/drafts/{draft_id}/comments", headers=viewer_headers)
        assert list_res.status_code == 200
        assert list_res.json()["data"]["total"] == 1

        # 2. Viewer CANNOT create comments (403)
        post_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Viewer commentary"},
            headers=viewer_headers,
        )
        assert post_res.status_code == 403

        # 3. Viewer CANNOT resolve comments (403)
        patch_res = await client.patch(
            f"/api/v1/drafts/{draft_id}/comments/{c_id}",
            json={"is_resolved": True},
            headers=viewer_headers,
        )
        assert patch_res.status_code == 403


@pytest.mark.asyncio
async def test_comments_multi_tenant_isolation() -> None:
    """Verify unauthorized strangers receive 404 on comment endpoints for unshared drafts."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner_iso@verischolar.org")
        stranger, stranger_token = await create_test_user(
            session_maker, "stranger_iso@verischolar.org"
        )
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        stranger_headers = {"Authorization": f"Bearer {stranger_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Private Draft", "content": "Secret IP", "format": "latex"},
            headers=owner_headers,
        )
        draft_id = create_res.json()["data"]["id"]

        c_res = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Confidential note"},
            headers=owner_headers,
        )
        comment_id = c_res.json()["data"]["id"]

        # Stranger attempts list -> 404
        assert (
            await client.get(f"/api/v1/drafts/{draft_id}/comments", headers=stranger_headers)
        ).status_code == 404

        # Stranger attempts create -> 404
        assert (
            await client.post(
                f"/api/v1/drafts/{draft_id}/comments",
                json={"comment_text": "Probe"},
                headers=stranger_headers,
            )
        ).status_code == 404

        # Stranger attempts update -> 404
        assert (
            await client.patch(
                f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
                json={"comment_text": "Tamper"},
                headers=stranger_headers,
            )
        ).status_code == 404

        # Stranger attempts delete -> 404
        assert (
            await client.delete(
                f"/api/v1/drafts/{draft_id}/comments/{comment_id}",
                headers=stranger_headers,
            )
        ).status_code == 404


@pytest.mark.asyncio
async def test_draft_deletion_cascades_comments() -> None:
    """Verify deleting a draft cascades and cleans up all associated comments from database."""
    async with comments_test_context() as (client, session_maker):
        owner, owner_token = await create_test_user(session_maker, "owner_cascade@verischolar.org")
        headers = {"Authorization": f"Bearer {owner_token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "To Delete", "content": "Temp", "format": "latex"},
            headers=headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # Add root comment and reply
        r1 = await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Root comment"},
            headers=headers,
        )
        c_id = r1.json()["data"]["id"]
        await client.post(
            f"/api/v1/drafts/{draft_id}/comments",
            json={"comment_text": "Reply", "parent_id": c_id},
            headers=headers,
        )

        # Delete draft
        del_res = await client.delete(f"/api/v1/drafts/{draft_id}", headers=headers)
        assert del_res.status_code == 204

        # Verify DB is clean
        async with session_maker() as session:
            stmt = select(DraftCommentModel).where(DraftCommentModel.draft_id == UUID(draft_id))
            comments = (await session.execute(stmt)).scalars().all()
            assert len(comments) == 0

"""Integration and contract tests for Draft Endpoints:
1. POST /api/v1/drafts with source_session_id (Academic Skeleton Generator)
2. POST /api/v1/drafts/{id}/chat:stream (Unbuffered SSE, previous_snapshot, draft_messages)
3. POST /api/v1/drafts/{id}:undo (Restore snapshot or 409 NO_UNDO_SNAPSHOT_AVAILABLE)
4. POST /api/v1/drafts/{id}/compile:clear-cache (Clear cache and recompile)
5. POST /api/v1/drafts/{id}/synctex:forward & :inverse (Bidirectional SyncTeX navigation)
6. POST /api/v1/drafts/{id}:export-bundle (Camera-Ready zip bundle)
"""

from __future__ import annotations

import io
import zipfile
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.draft_message import DraftMessageModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.services.auth_service import AuthService
from api.services.draft_service import DraftService
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def current_user(auth_headers: dict[str, str], db_session: AsyncSession) -> UserModel:
    token = auth_headers["Authorization"].split(" ")[1]
    claims = AuthService.decode_token(token)
    user_id = claims["sub"]
    user = await db_session.get(UserModel, user_id)
    assert user is not None
    return user


@pytest.mark.asyncio
async def test_create_draft_from_source_session_generates_skeleton(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 1: POST /api/v1/drafts with source_session_id generates main_tex & references.bib."""
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=current_user.id,
        title="Attention Is All You Need",
        filename="attention.pdf",
        authors=["Vaswani, Ashish", "Shazeer, Noam"],
        publication_year=2017,
        status="ready",
        content_hash="hash_attention_001",
        file_size_bytes=2048,
    )
    db_session.add(doc)

    session_id = uuid4()
    session = ResearchSessionModel(
        id=session_id,
        user_id=current_user.id,
        title="Transformer Foundations",
    )
    db_session.add(session)

    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add(sess_doc)
    await db_session.commit()

    res = await async_client.post(
        "/api/v1/drafts",
        headers=auth_headers,
        json={
            "title": "Nghiên cứu Kiến trúc Transformer Mới",
            "source_session_id": str(session_id),
            "template": "academic_skeleton",
        },
    )
    assert res.status_code == 201, res.text
    payload = res.json()["data"]

    assert payload["title"] == "Nghiên cứu Kiến trúc Transformer Mới"
    assert "\\documentclass" in payload["content"]
    assert "\\section{Introduction}" in payload["content"]
    assert "\\section{Related Work}" in payload["content"]
    assert "@article{" in payload["bib_content"]
    assert "Vaswani" in payload["bib_content"]
    assert payload["source_session_id"] == str(session_id)


@pytest.mark.asyncio
async def test_draft_chat_stream_snapshots_emits_sse_and_records_messages(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 2: POST /api/v1/drafts/{id}/chat:stream captures snapshot, streams SSE, records messages."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Bản thảo ban đầu",
        content="\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
        bib_content="@article{test2024, title={Test Paper}, author={Author, A.}, year={2024}}",
        version=1,
    )
    db_session.add(draft)
    await db_session.commit()

    mock_events = [
        {"event": "thinking", "type": "thinking", "data": {"message": "Đang suy nghĩ..."}},
        {
            "event": "tool_start",
            "type": "tool_start",
            "data": {"name": "edit_latex_files", "args": {}},
        },
        {
            "event": "content_update",
            "type": "content_update",
            "data": {
                "target_file": "main.tex",
                "content": "\\documentclass{article}\n\\begin{document}\nUpdated Content\n\\end{document}",
            },
        },
        {
            "event": "compile_attempt",
            "type": "compile_attempt",
            "data": {"attempt": 1, "success": True, "diagnostics": []},
        },
        {
            "event": "done",
            "type": "done",
            "data": {
                "pdf_path": "/tmp/drafts/test.pdf",
                "main_tex": "\\documentclass{article}\n\\begin{document}\nUpdated Content\n\\end{document}",
                "bib_content": draft.bib_content,
                "final_answer": "Đã sửa xong và biên dịch thành công.",
            },
        },
    ]

    async def _mock_run(*args, **kwargs):
        for ev in mock_events:
            yield ev

    with patch("api.agents.latex_agent.LatexCoauthorAgent.run", side_effect=_mock_run):
        async with async_client.stream(
            "POST",
            f"/api/v1/drafts/{draft.id}/chat:stream",
            headers=auth_headers,
            json={"prompt": "Hãy bổ sung nội dung bài báo."},
        ) as stream_response:
            assert stream_response.status_code == 200
            assert "text/event-stream" in stream_response.headers.get("content-type", "")

            raw_stream_body = ""
            async for chunk in stream_response.aiter_text():
                raw_stream_body += chunk

    assert "event: thinking" in raw_stream_body
    assert "event: tool_start" in raw_stream_body
    assert "event: compile_attempt" in raw_stream_body
    assert "event: done" in raw_stream_body

    # Verify database updates
    refreshed_draft = await db_session.get(DraftModel, draft.id)
    assert refreshed_draft is not None
    assert refreshed_draft.previous_snapshot is not None
    undo_data = refreshed_draft.previous_snapshot.get("undo") or refreshed_draft.previous_snapshot
    assert "saved_at" in undo_data
    assert "Hello World" in undo_data["content"]
    assert refreshed_draft.version == 2
    assert "Updated Content" in refreshed_draft.content

    # Verify draft_messages recorded
    msg_stmt = (
        select(DraftMessageModel)
        .where(DraftMessageModel.draft_id == draft.id)
        .order_by(DraftMessageModel.created_at.asc())
    )
    messages = list((await db_session.execute(msg_stmt)).scalars().all())
    assert len(messages) >= 2
    assert messages[0].role == "user"
    assert "bổ sung nội dung" in messages[0].content
    assert messages[-1].role == "assistant"


@pytest.mark.asyncio
async def test_undo_restores_snapshot_and_clears_it(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 3: POST /api/v1/drafts/{id}:undo restores snapshot or returns 409 NO_UNDO_SNAPSHOT_AVAILABLE."""
    # Subtest A: No snapshot -> 409 NO_UNDO_SNAPSHOT_AVAILABLE
    draft_no_snap = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Draft No Snapshot",
        content="Current Content",
        bib_content="Current Bib",
        previous_snapshot=None,
        version=1,
    )
    db_session.add(draft_no_snap)
    await db_session.commit()

    res_err = await async_client.post(
        f"/api/v1/drafts/{draft_no_snap.id}:undo",
        headers=auth_headers,
    )
    assert res_err.status_code == 409, res_err.text
    err_body = res_err.json()
    err_code = (
        err_body.get("error", {}).get("code")
        or err_body.get("detail", {}).get("code")
        or err_body.get("code")
    )
    assert err_code == "NO_UNDO_SNAPSHOT_AVAILABLE"
    err_detail = err_body.get("detail") or err_body.get("error") or {}
    assert (
        err_detail.get("message") == "Không có bản sao lưu trước đó để thực hiện thao tác hoàn tác."
    )
    assert err_detail.get("action") == "Nút hoàn tác chỉ khả dụng sau khi AI đã can thiệp."

    # Subtest B: Has snapshot -> restored, cache evicted, and snapshot cleared
    snap_data = {
        "content": "\\documentclass{article}\n\\begin{document}\nOriginal pristine text\n\\end{document}",
        "bib_content": "@article{pristine, title={Pristine Bib}, year={2023}}",
        "version": 1,
        "saved_at": "2026-10-25T10:30:00Z",
    }
    draft_with_snap = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Draft With Snapshot",
        content="\\documentclass{article}\n\\begin{document}\nAccidentally ruined text\n\\end{document}",
        bib_content="@article{ruined, title={Ruined Bib}, year={2024}}",
        previous_snapshot=snap_data,
        version=2,
    )
    db_session.add(draft_with_snap)
    await db_session.commit()

    # Pre-populate cache to verify cache invalidation on undo
    DraftService._draft_pdf_cache[draft_with_snap.id] = b"cached_ruined_pdf"

    res_ok = await async_client.post(
        f"/api/v1/drafts/{draft_with_snap.id}:undo",
        headers=auth_headers,
    )
    assert res_ok.status_code == 200, res_ok.text
    payload = res_ok.json()["data"]

    assert payload["content"] == snap_data["content"]
    assert payload["bib_content"] == snap_data["bib_content"]
    assert payload["version"] > 2

    # Verify db state
    refreshed = await db_session.get(DraftModel, draft_with_snap.id)
    assert refreshed is not None
    assert refreshed.content == snap_data["content"]
    assert refreshed.bib_content == snap_data["bib_content"]
    assert refreshed.previous_snapshot is not None
    assert refreshed.previous_snapshot.get("redo") is not None
    assert "Accidentally ruined text" in refreshed.previous_snapshot["redo"]["content"]

    # Subtest C: Symmetrical 2-way Undo -> Calling undo again executes Redo!
    res_redo = await async_client.post(
        f"/api/v1/drafts/{draft_with_snap.id}:undo",
        headers=auth_headers,
    )
    assert res_redo.status_code == 200, res_redo.text
    payload_redo = res_redo.json()["data"]
    assert "Accidentally ruined text" in payload_redo["content"]
    assert payload_redo["previous_snapshot"]["undo"] is not None

    # Verify cache was cleared
    assert DraftService._draft_pdf_cache.get(draft_with_snap.id) is None


@pytest.mark.asyncio
async def test_compile_clear_cache_clears_and_recompiles(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 4: POST /api/v1/drafts/{id}/compile:clear-cache removes cache and recompiles cleanly."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Draft For Clear Cache",
        content="\\documentclass{article}\n\\begin{document}\nCompile Test\n\\end{document}",
        bib_content="",
        version=1,
    )
    db_session.add(draft)
    await db_session.commit()

    mock_compile_result = {
        "success": True,
        "is_cached": False,
        "pdf_path": "/tmp/drafts/test.pdf",
        "synctex_path": "/tmp/drafts/test.synctex.gz",
        "logs": "Output written on output.pdf (1 page)...",
        "diagnostics": [],
        "engine": "pdflatex",
        "duration_seconds": 0.42,
    }

    with patch(
        "api.services.clsi_latex_compiler.CLSILatexCompiler.compile",
        new=AsyncMock(return_value=mock_compile_result),
    ) as mock_comp:
        res = await async_client.post(
            f"/api/v1/drafts/{draft.id}/compile:clear-cache",
            headers=auth_headers,
        )
        assert res.status_code == 200, res.text
        payload = res.json()["data"]

        assert payload["draft_id"] == str(draft.id)
        assert payload["cache_cleared"] is True
        assert payload["success"] is True
        assert "Output written" in payload["logs"]
        assert f"/api/v1/drafts/{draft.id}/preview.pdf" in payload["pdf_preview_url"]

        # Assert clear_cache=True was passed to compiler
        assert mock_comp.await_count == 1
        _, kwargs = mock_comp.call_args
        assert kwargs.get("clear_cache") is True


@pytest.mark.asyncio
async def test_synctex_forward_and_inverse_endpoints(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 5: POST /api/v1/drafts/{id}/synctex:forward & synctex:inverse bidirectional navigation."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Draft For SyncTeX",
        content="\\documentclass{article}\n\\begin{document}\nLine 42\n\\end{document}",
        bib_content="",
        version=1,
    )
    db_session.add(draft)
    await db_session.commit()

    mock_fwd = {
        "page": 2,
        "h": 145.2,
        "v": 320.5,
        "width": 420.0,
        "height": 18.0,
    }
    mock_inv = {
        "file": "main.tex",
        "line": 42,
        "column": 5,
    }

    with (
        patch(
            "api.services.clsi_latex_compiler.CLSILatexCompiler.synctex_forward",
            new=AsyncMock(return_value=mock_fwd),
        ),
        patch(
            "api.services.clsi_latex_compiler.CLSILatexCompiler.synctex_inverse",
            new=AsyncMock(return_value=mock_inv),
        ),
    ):
        # Forward
        res_fwd = await async_client.post(
            f"/api/v1/drafts/{draft.id}/synctex:forward",
            headers=auth_headers,
            json={"file": "main.tex", "line": 42, "column": 1},
        )
        assert res_fwd.status_code == 200, res_fwd.text
        data_fwd = res_fwd.json()["data"]
        assert data_fwd["page"] == 2
        assert data_fwd["h"] == 145.2
        assert data_fwd["v"] == 320.5
        assert data_fwd["width"] == 420.0
        assert data_fwd["height"] == 18.0

        # Inverse
        res_inv = await async_client.post(
            f"/api/v1/drafts/{draft.id}/synctex:inverse",
            headers=auth_headers,
            json={"page": 2, "x": 160.0, "y": 325.0},
        )
        assert res_inv.status_code == 200, res_inv.text
        data_inv = res_inv.json()["data"]
        assert data_inv["file"] == "main.tex"
        assert data_inv["line"] == 42
        assert data_inv["column"] == 5


@pytest.mark.asyncio
async def test_export_bundle_produces_camera_ready_zip(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test 6: POST /api/v1/drafts/{id}:export-bundle yields complete submission zip package."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Academic Camera Ready Paper",
        content="\\documentclass{article}\n\\begin{document}\nFull Paper\n\\end{document}",
        bib_content="@article{smith2024, title={Foundational Research}, author={Smith, J.}, year={2024}}",
        version=1,
    )
    db_session.add(draft)
    await db_session.commit()

    # Pre-populate compiled PDF preview cache to decouple export bundle test from external compiler binaries
    DraftService._draft_pdf_cache[draft.id] = (
        b"%PDF-1.4 valid compiled pdf bytes for academic bundle test"
    )

    res = await async_client.post(
        f"/api/v1/drafts/{draft.id}:export-bundle",
        headers=auth_headers,
    )
    assert res.status_code == 200, res.text
    assert res.headers.get("content-type") == "application/zip"

    with zipfile.ZipFile(io.BytesIO(res.content), "r") as zf:
        namelist = zf.namelist()
        assert "main.tex" in namelist
        assert "references.bib" in namelist
        assert "README.txt" in namelist
        assert any(name.startswith("figures/") for name in namelist)

        main_tex_content = zf.read("main.tex").decode("utf-8")
        assert "Full Paper" in main_tex_content

        bib_content = zf.read("references.bib").decode("utf-8")
        assert "smith2024" in bib_content

        readme_content = zf.read("README.txt").decode("utf-8")
        warning_msg = (
            "Bản thảo chưa được biên dịch thành công lần cuối, vui lòng chạy tectonic "
            "hoặc pdflatex theo hướng dẫn bên dưới để kiểm tra lỗi cú pháp."
        )
        # Because this valid draft compiled successfully, warning must NOT be present
        assert warning_msg not in readme_content

    # Subtest: Draft with broken syntax uses fallback preview and includes the warning in README.txt
    broken_draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Broken Syntax Paper",
        content="\\documentclass{article}\n\\begin{document}\n\\badmacro{{{}}\n",
        bib_content="",
        version=1,
    )
    db_session.add(broken_draft)
    await db_session.commit()

    res_broken = await async_client.post(
        f"/api/v1/drafts/{broken_draft.id}:export-bundle",
        headers=auth_headers,
    )
    assert res_broken.status_code == 200
    with zipfile.ZipFile(io.BytesIO(res_broken.content), "r") as zf:
        readme_broken = zf.read("README.txt").decode("utf-8")
        assert warning_msg in readme_broken


@pytest.mark.asyncio
async def test_chat_stream_empty_prompt_and_occ_conflict(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Edge cases: empty prompt yields 400 EMPTY_PROMPT_CONTENT; version mismatch yields 412 CONCURRENCY_CONFLICT."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Edge Case Draft",
        content="\\documentclass{article}",
        version=3,
    )
    db_session.add(draft)
    await db_session.commit()

    # Empty prompt -> 400
    res_empty = await async_client.post(
        f"/api/v1/drafts/{draft.id}/chat:stream",
        headers=auth_headers,
        json={"prompt": "   "},
    )
    assert res_empty.status_code == 400, res_empty.text
    assert res_empty.json()["error"]["code"] == "EMPTY_PROMPT_CONTENT"

    # OCC Conflict -> 412
    res_occ = await async_client.post(
        f"/api/v1/drafts/{draft.id}/chat:stream",
        headers=auth_headers,
        json={"prompt": "Valid prompt", "version": 1},
    )
    assert res_occ.status_code == 412, res_occ.text
    assert res_occ.json()["error"]["code"] == "CONCURRENCY_CONFLICT"


@pytest.mark.asyncio
async def test_create_draft_invalid_session_yields_404(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Non-existent source_session_id yields 404 SOURCE_SESSION_NOT_FOUND."""
    fake_session_id = uuid4()
    res = await async_client.post(
        "/api/v1/drafts",
        headers=auth_headers,
        json={
            "title": "Invalid Session Draft",
            "source_session_id": str(fake_session_id),
        },
    )
    assert res.status_code == 404, res.text
    assert res.json()["error"]["code"] == "SOURCE_SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_draft_with_bib_content(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    """Test updating draft with bib_content: verifies 200 OK, incremented ETag, DB persistence, and cache eviction."""
    draft = DraftModel(
        id=uuid4(),
        user_id=current_user.id,
        title="Initial Draft Title",
        content="\\documentclass{article}\n\\begin{document}\nInitial\n\\end{document}",
        bib_content="@article{initial, title={Initial Paper}, year={2020}}",
        version=1,
    )
    db_session.add(draft)
    await db_session.commit()

    # Pre-populate cache to verify cache invalidation on manual update
    DraftService._draft_pdf_cache[draft.id] = b"old_cached_pdf"

    new_bib = "@article{updated2026, title={Updated Reference}, year={2026}}"
    update_payload = {
        "bib_content": new_bib,
        "version": 1,
    }

    res = await async_client.put(
        f"/api/v1/drafts/{draft.id}",
        json=update_payload,
        headers=auth_headers,
    )
    assert res.status_code == 200, res.text
    assert res.headers.get("ETag") == '"2"'
    data = res.json()["data"]
    assert data["bib_content"] == new_bib
    assert data["version"] == 2

    # Verify database persistence
    refreshed = await db_session.get(DraftModel, draft.id)
    assert refreshed is not None
    assert refreshed.bib_content == new_bib
    assert refreshed.version == 2

    # Verify PDF cache was invalidated
    assert DraftService._draft_pdf_cache.get(draft.id) is None

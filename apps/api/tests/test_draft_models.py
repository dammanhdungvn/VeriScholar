"""Unit tests for Agentic Writing Workspace models (Task 6)."""

from uuid import uuid4

from api.db.models.draft import DraftModel
from api.db.models.draft_asset import DraftAssetModel
from api.db.models.draft_message import DraftMessageModel
from sqlalchemy import CheckConstraint, UniqueConstraint


def test_draft_model_fields_and_snapshot():
    """Verify DraftModel fields including bib_content, snapshot, source session and version."""
    user_id = uuid4()
    session_id = uuid4()
    draft = DraftModel(
        user_id=user_id,
        title="Attention Mechanism Survey",
        content="\\documentclass{article}\n\\begin{document}\nHello\\end{document}",
        bib_content="@article{vaswani2017,\n  title={Attention Is All You Need}\n}",
        format="latex",
        template="blank",
        version=1,
        source_session_id=session_id,
        previous_snapshot={"content": "old", "bib_content": "old_bib", "version": 0},
        pdf_preview_storage_path="/storage/previews/draft-1.pdf",
    )
    assert draft.user_id == user_id
    assert draft.version == 1
    assert "@article" in draft.bib_content
    assert draft.source_session_id == session_id
    assert draft.previous_snapshot == {"content": "old", "bib_content": "old_bib", "version": 0}
    assert draft.pdf_preview_storage_path == "/storage/previews/draft-1.pdf"
    assert DraftModel.__tablename__ == "drafts"


def test_draft_asset_model():
    """Verify DraftAssetModel representation, attributes and constraints."""
    user_id = uuid4()
    draft_id = uuid4()
    blob_id = uuid4()
    asset = DraftAssetModel(
        user_id=user_id,
        draft_id=draft_id,
        blob_id=blob_id,
        file_name="figures/arch.png",
        mime_type="image/png",
        byte_size=10240,
    )
    assert asset.user_id == user_id
    assert asset.draft_id == draft_id
    assert asset.blob_id == blob_id
    assert asset.file_name == "figures/arch.png"
    assert asset.mime_type == "image/png"
    assert asset.byte_size == 10240
    assert DraftAssetModel.__tablename__ == "draft_assets"

    # Check unique constraint on (draft_id, file_name)
    table = DraftAssetModel.__table__
    unique_constraints = {c.name: c for c in table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_draft_assets_draft_filename" in unique_constraints
    uq = unique_constraints["uq_draft_assets_draft_filename"]
    uq_cols = {col.name for col in uq.columns}
    assert uq_cols == {"draft_id", "file_name"}


def test_draft_message_model():
    """Verify DraftMessageModel representation, attributes and check constraint."""
    user_id = uuid4()
    draft_id = uuid4()
    msg = DraftMessageModel(
        user_id=user_id,
        draft_id=draft_id,
        role="assistant",
        content="Here is the revised LaTeX section.",
        tool_calls=[{"name": "edit_latex_files", "args": {"file": "main.tex"}}],
        compile_attempts=1,
        trace_id="tr_writer_1234",
    )
    assert msg.user_id == user_id
    assert msg.draft_id == draft_id
    assert msg.role == "assistant"
    assert msg.content == "Here is the revised LaTeX section."
    assert msg.tool_calls == [{"name": "edit_latex_files", "args": {"file": "main.tex"}}]
    assert msg.compile_attempts == 1
    assert msg.trace_id == "tr_writer_1234"
    assert DraftMessageModel.__tablename__ == "draft_messages"

    # Check check constraint ck_draft_messages_role
    table = DraftMessageModel.__table__
    check_constraints = {c.name: c for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_draft_messages_role" in check_constraints
    assert "role IN ('user', 'assistant', 'tool')" in str(
        check_constraints["ck_draft_messages_role"].sqltext
    )

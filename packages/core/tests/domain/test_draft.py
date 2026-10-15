"""Unit tests for Draft domain entity in packages/core."""

from uuid import uuid4

import pytest
from core.domain.entities.draft import Draft
from core.domain.exceptions import ConcurrencyConflictError


def test_draft_initialization() -> None:
    """Test draft default initialization and invariants."""
    user_id = uuid4()
    draft = Draft(user_id=user_id, title="Neural Machine Translation Review", format="latex")

    assert draft.title == "Neural Machine Translation Review"
    assert draft.format == "latex"
    assert draft.content == ""
    assert draft.version == 1
    assert draft.user_id == user_id


def test_draft_update_content_success() -> None:
    """Test successful content update increments version and timestamps."""
    draft = Draft(title="Initial Title", content="Initial LaTeX", format="latex")
    assert draft.version == 1

    draft.update_content(
        title="Updated Title",
        content="\\section{Introduction}\nUpdated content here.",
        format="latex",
        expected_version=1,
    )

    assert draft.title == "Updated Title"
    assert draft.content == "\\section{Introduction}\nUpdated content here."
    assert draft.version == 2


def test_draft_occ_conflict_error() -> None:
    """Test OCC conflict error when expected version does not match."""
    draft = Draft(title="Initial", content="Hello", version=2)

    with pytest.raises(ConcurrencyConflictError) as exc_info:
        draft.update_content(
            title="Conflict Attempt",
            content="New content",
            format="latex",
            expected_version=1,  # Stale version
        )

    assert "Draft version conflict: expected 1, current 2" in str(exc_info.value)
    assert draft.title == "Initial"
    assert draft.version == 2


def test_draft_asset_entity() -> None:
    """Test DraftAsset domain entity creation and invariants."""
    from core.domain.entities.draft import DraftAsset

    draft_id = uuid4()
    asset = DraftAsset(
        draft_id=draft_id,
        asset_type="bibtex",
        filename="references.bib",
        file_size_bytes=1024,
        storage_url=f"/api/v1/drafts/{draft_id}/assets/references.bib",
        caption="BibTeX bibliography",
        latex_label="bib:refs",
    )
    assert asset.draft_id == draft_id
    assert asset.asset_type == "bibtex"
    assert asset.filename == "references.bib"
    assert asset.file_size_bytes == 1024


def test_draft_share_and_collaborator_entities() -> None:
    """Test DraftCollaborator and DraftShareSettings domain entities."""
    from core.domain.entities.draft import DraftCollaborator, DraftShareSettings

    draft_id = uuid4()
    collab = DraftCollaborator(email="researcher@verischolar.org", permission="editor")
    share = DraftShareSettings(
        draft_id=draft_id,
        share_token="tok123",
        share_url=f"/shared/drafts/{draft_id}?token=tok123",
        permission="editor",
        allow_public_link=True,
        collaborators=[collab],
    )
    assert share.draft_id == draft_id
    assert share.allow_public_link is True
    assert len(share.collaborators) == 1
    assert share.collaborators[0].email == "researcher@verischolar.org"


def test_draft_assist_result_entity() -> None:
    """Test DraftAssistResult domain entity."""
    from core.domain.entities.draft import DraftAssistResult

    draft_id = uuid4()
    assist = DraftAssistResult(
        draft_id=draft_id,
        action="polish",
        generated_text="Polished academic sentence.",
        suggested_citations=["vaswani2017attention"],
    )
    assert assist.draft_id == draft_id
    assert assist.action == "polish"
    assert len(assist.suggested_citations) == 1

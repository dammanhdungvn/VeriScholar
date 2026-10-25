from uuid import uuid4

from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)


def test_session_turn_has_user_id_and_trace_id():
    assert "user_id" in SessionTurnModel.__table__.columns
    assert "trace_id" in SessionTurnModel.__table__.columns

    user_id = uuid4()
    session_id = uuid4()
    turn = SessionTurnModel(
        user_id=user_id,
        session_id=session_id,
        question="What is the BLEU score?",
        answer="The BLEU score is 28.4 [[cite:chunk-1]].",
        citations=[{"chunk_id": "c1", "page": 4}],
        trace_id="tr_9c1fa8fe",
    )
    assert turn.user_id == user_id
    assert turn.session_id == session_id
    assert turn.trace_id == "tr_9c1fa8fe"
    assert turn.prompt_tokens == 0
    assert turn.completion_tokens == 0
    assert turn.latency_ms == 0
    assert turn.finish_reason == "stop"


def test_research_session_and_document_models():
    user_id = uuid4()
    session = ResearchSessionModel(
        user_id=user_id,
        title="Transformer Study",
    )
    assert session.user_id == user_id
    assert session.title == "Transformer Study"
    assert session.active_tab == "chat"
    assert session.is_archived is False
    assert session.version == 1

    doc_id = uuid4()
    sess_doc = SessionDocumentModel(
        session_id=session.id,
        document_id=doc_id,
    )
    assert sess_doc.session_id == session.id
    assert sess_doc.document_id == doc_id
    assert sess_doc.display_order == 0


def test_research_note_evidence_preservation():
    user_id = uuid4()
    note = ResearchNoteModel(
        user_id=user_id,
        document_id=uuid4(),
        selected_text="Scaled dot-product formula",
        bounding_boxes=[[10, 20, 30, 40]],
        page_number=3,
        user_note="Important for chapter 2",
        tags=["attention", "math"],
        frozen_snapshot={"paper_title": "Attention Is All You Need", "year": 2017},
        version=1,
    )
    assert note.user_id == user_id
    assert note.is_source_detached is False
    assert note.version == 1
    assert "math" in note.tags
    assert note.frozen_snapshot["year"] == 2017
    assert note.content == "Important for chapter 2"


def test_folder_model_hierarchy():
    user_id = uuid4()
    parent_folder = FolderModel(
        user_id=user_id,
        name="AI Research",
    )
    assert parent_folder.user_id == user_id
    assert parent_folder.name == "AI Research"
    assert parent_folder.parent_id is None
    assert parent_folder.color != ""

    subfolder = FolderModel(
        user_id=user_id,
        name="Attention Mechanisms",
        parent_id=parent_folder.id,
    )
    assert subfolder.parent_id == parent_folder.id

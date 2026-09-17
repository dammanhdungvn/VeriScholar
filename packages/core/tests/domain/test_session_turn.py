"""Unit tests for SessionTurn domain entity."""

from uuid import uuid4

from core.domain.entities.session_turn import SessionTurn
from core.domain.value_objects.enums import SessionTurnFinishReason


def test_session_turn_valid_instantiation() -> None:
    session_id = uuid4()
    document_id = uuid4()

    turn = SessionTurn(
        session_id=session_id,
        question="What architecture does the Transformer use?",
        answer="The Transformer uses an encoder-decoder architecture [^c_1].",
        citations=[
            {
                "citation_id": "cit_1",
                "document_id": document_id,
                "document_title": "Attention Is All You Need",
                "page_number": 2,
                "bounding_boxes": [[0.1, 0.2, 0.8, 0.4, 2.0]],
            }
        ],
        finish_reason=SessionTurnFinishReason.STOP,
        prompt_tokens=150,
        completion_tokens=45,
    )

    assert turn.session_id == session_id
    assert turn.prompt_tokens == 150
    assert turn.completion_tokens == 45
    assert turn.total_tokens == 195
    assert turn.finish_reason == SessionTurnFinishReason.STOP


def test_session_turn_abstention() -> None:
    turn = SessionTurn(
        session_id=uuid4(),
        question="What is the author's personal phone number?",
        answer="The provided document does not contain this information.",
        finish_reason=SessionTurnFinishReason.ABSTENTION,
        prompt_tokens=80,
        completion_tokens=15,
    )

    assert turn.finish_reason == SessionTurnFinishReason.ABSTENTION
    assert turn.total_tokens == 95

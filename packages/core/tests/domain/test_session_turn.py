"""Unit tests for SessionTurn domain entity."""

from uuid import uuid4

from core.domain.entities.session_turn import SessionTurn
from core.domain.value_objects.enums import SessionTurnFinishReason


def test_session_turn_valid_instantiation() -> None:
    session_id = uuid4()
    turn = SessionTurn(
        session_id=session_id,
        turn_index=0,
        user_query="What architecture does the Transformer use?",
        assistant_response="The Transformer uses an encoder-decoder architecture [^c_1].",
        citations=[{"chunk_id": str(uuid4()), "page": 2, "bbox": [0.1, 0.2, 0.8, 0.4, 2]}],
        finish_reason=SessionTurnFinishReason.STOP,
        prompt_tokens=150,
        completion_tokens=45,
    )

    assert turn.session_id == session_id
    assert turn.turn_index == 0
    assert turn.prompt_tokens == 150
    assert turn.completion_tokens == 45
    assert turn.total_tokens == 195
    assert turn.is_abstention is False


def test_session_turn_abstention() -> None:
    session_id = uuid4()
    turn = SessionTurn(
        session_id=session_id,
        turn_index=1,
        user_query="What is the author's personal phone number?",
        assistant_response="The provided document does not contain this information.",
        finish_reason=SessionTurnFinishReason.ABSTENTION,
        prompt_tokens=80,
        completion_tokens=15,
    )

    assert turn.is_abstention is True
    assert turn.total_tokens == 95

import pytest
from api.schemas.session import SessionChatMessageRequest


def test_session_chat_request_schema_supports_reasoning_effort():
    # Default is high (or medium)
    req_default = SessionChatMessageRequest(question="Phân tích mô hình")
    assert req_default.reasoning_effort in ("high", "medium")

    # Custom low
    req_custom = SessionChatMessageRequest(content="Phân tích", reasoning_effort="low")
    assert req_custom.reasoning_effort == "low"

    # Custom off
    req_off = SessionChatMessageRequest(message="Phân tích", reasoning_effort="off")
    assert req_off.reasoning_effort == "off"


def test_session_chat_request_rejects_invalid_effort():
    with pytest.raises(Exception):
        SessionChatMessageRequest(question="Test", reasoning_effort="invalid_level")

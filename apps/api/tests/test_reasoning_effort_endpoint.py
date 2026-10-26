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

    # Luna 5.6 aliases: light & extra_high
    req_light = SessionChatMessageRequest(question="Tóm tắt", reasoning_effort="light")
    assert req_light.reasoning_effort == "light"

    req_extra = SessionChatMessageRequest(question="Đào sâu", reasoning_effort="extra_high")
    assert req_extra.reasoning_effort == "extra_high"


def test_session_chat_request_rejects_invalid_effort():
    with pytest.raises(Exception):
        SessionChatMessageRequest(question="Test", reasoning_effort="invalid_level")

from uuid import uuid4

import pytest
from core.services.citation_parser import (
    MAX_SESSION_DOCUMENTS,
    DocumentAlreadyInSessionError,
    SessionTabLimitExceededError,
    extract_citation_markers,
    validate_session_tab_capacity,
)


def test_validate_session_tab_capacity_enforces_max_5():
    existing = [uuid4() for _ in range(MAX_SESSION_DOCUMENTS)]
    with pytest.raises(SessionTabLimitExceededError) as exc_info:
        validate_session_tab_capacity(existing, uuid4())
    assert exc_info.value.code == "MAX_SESSION_DOCUMENTS_REACHED"


def test_validate_session_tab_capacity_detects_duplicate():
    doc_id = uuid4()
    with pytest.raises(DocumentAlreadyInSessionError) as exc_info:
        validate_session_tab_capacity([doc_id], doc_id)
    assert exc_info.value.code == "REFERENCE_ALREADY_IN_SESSION"


def test_extract_citation_markers_preserves_order_and_uniqueness():
    sample = "Kết quả BLEU đạt 28.4 [[cite:2]] vượt qua baseline [[cite:1]] và [[cite:2]]."
    assert extract_citation_markers(sample) == [2, 1]

"""Pure domain citation parser and multi-tab capacity invariants.

Adheres strictly to Hexagonal Isolation: pure Python standard library only.
"""

from __future__ import annotations

import re
from uuid import UUID

from core.domain.exceptions import DomainError

MAX_SESSION_DOCUMENTS: int = 5


class SessionTabLimitExceededError(DomainError):
    """Raised when session exceeds 5 documents capacity limit."""

    code: str = "MAX_SESSION_DOCUMENTS_REACHED"

    def __init__(
        self,
        message: str = (
            "Phiên đọc chỉ hỗ trợ tối đa 5 bài báo cùng lúc để bảo đảm độ chính xác cao nhất."
        ),
    ) -> None:
        super().__init__(message)
        self.code = "MAX_SESSION_DOCUMENTS_REACHED"


class DocumentAlreadyInSessionError(DomainError):
    """Raised when document already exists in the session tabs."""

    code: str = "REFERENCE_ALREADY_IN_SESSION"

    def __init__(
        self,
        message: str = "Tài liệu này đã tồn tại trong phiên nghiên cứu hiện tại.",
    ) -> None:
        super().__init__(message)
        self.code = "REFERENCE_ALREADY_IN_SESSION"


def validate_session_tab_capacity(current_doc_ids: list[UUID], new_doc_id: UUID) -> None:
    """Validate tab limit and duplicate document invariants for deep reading session.

    Raises:
        DocumentAlreadyInSessionError: If new_doc_id is already in current_doc_ids.
        SessionTabLimitExceededError: If current_doc_ids length is >= MAX_SESSION_DOCUMENTS.
    """
    if new_doc_id in current_doc_ids:
        raise DocumentAlreadyInSessionError()

    if len(current_doc_ids) >= MAX_SESSION_DOCUMENTS:
        raise SessionTabLimitExceededError()


def extract_citation_markers(markdown_text: str) -> list[int]:
    """Extract citation index numbers from markdown text matching [[cite:N]].

    Maintains order of first appearance and eliminates duplicates.
    """
    seen: set[int] = set()
    result: list[int] = []
    for match in re.finditer(r"\[\[cite:(\d+)\]\]", markdown_text):
        idx = int(match.group(1))
        if idx not in seen:
            seen.add(idx)
            result.append(idx)
    return result

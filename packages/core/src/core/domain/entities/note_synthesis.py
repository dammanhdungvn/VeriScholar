"""Domain entities and value objects for AI Note Syntheses (Knowledge Digest)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class SynthesisMode(str, Enum):
    CONCEPT_LESSON = "concept_lesson"
    LITERATURE_REVIEW = "literature_review"
    RESEARCH_GAP = "research_gap"
    ACTIVE_RECALL_QUIZ = "active_recall_quiz"


@dataclass(frozen=True)
class InteractiveBadge:
    """Visual citation badge linking synthesized prose to exact source passage."""

    badge_id: str
    note_id: str
    document_id: str | None
    citation_label: str
    page_number: int
    bounding_boxes: list[list[float | int]] = field(default_factory=list)
    quote_text: str = ""
    is_source_detached: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "badge_id": self.badge_id,
            "note_id": self.note_id,
            "document_id": self.document_id,
            "citation_label": self.citation_label,
            "page_number": self.page_number,
            "bounding_boxes": self.bounding_boxes,
            "quote_text": self.quote_text,
            "is_source_detached": self.is_source_detached,
        }


@dataclass
class NoteSynthesis:
    """Aggregate Root representing a synthesized knowledge digest derived from notes."""

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    title: str = ""
    mode: str = SynthesisMode.CONCEPT_LESSON.value
    language: str = "vi"
    markdown_content: str = ""
    interactive_badges: list[dict[str, Any]] = field(default_factory=list)
    source_note_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

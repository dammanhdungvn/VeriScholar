"""SessionTurn Domain Entity and Citation Item Value Object.

Represents an atomic Q&A turn in a multi-paper research session.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from core.domain.value_objects.enums import SessionTurnFinishReason


class CitationItem(BaseModel):
    """Value object representing an academic citation ground with spatial bounding boxes."""

    model_config = ConfigDict(frozen=True)

    citation_id: str = Field(description="Unique citation tag identifier e.g. cit_1")
    document_id: UUID = Field(description="Referenced document UUID")
    document_title: str = Field(description="Document title for attribution")
    page_number: int = Field(ge=1, description="Target page number")
    bounding_boxes: list[list[float]] = Field(
        default_factory=list,
        description="Spatial coordinates [[x1, y1, x2, y2, page]] for canvas highlighting",
    )
    score: float = Field(default=1.0, description="Reranker / similarity relevance score")


class SessionTurn(BaseModel):
    """Domain Entity representing an atomic inquiry turn in a session."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Turn unique identifier")
    session_id: UUID = Field(description="Associated research session UUID")
    question: str = Field(min_length=1, description="User prompt or question")
    answer: str = Field(description="Grounded AI response")
    citations: list[CitationItem] = Field(
        default_factory=list, description="Grounding citation references"
    )
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    finish_reason: SessionTurnFinishReason | str = Field(
        default=SessionTurnFinishReason.STOP, description="Generation completion reason"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

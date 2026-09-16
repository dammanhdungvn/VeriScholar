"""Document Summary domain entity representing the 3-point grounded summary."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from core.domain.value_objects.bounding_box import BoundingBox


class SummaryPoint(BaseModel):
    """A grounded summary point containing synthesis text and original visual citations."""

    text: str = Field(min_length=1, description="Synthesized point statement")
    bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Normalized bounding boxes covering evidence on the document page",
    )


class DocumentSummary(BaseModel):
    """Singleton 3-point grounded summary for an academic paper."""

    id: UUID | None = Field(default=None, description="Summary UUID")
    document_id: UUID = Field(..., description="Associated document UUID")
    problem_statement: SummaryPoint = Field(
        ..., description="Core research problem addressed by the paper"
    )
    contributions: SummaryPoint = Field(..., description="Key contributions and novel proposals")
    limitations: SummaryPoint = Field(
        ..., description="Remaining limitations, assumptions, or research gaps"
    )
    total_tokens: int = Field(
        default=0, ge=0, description="Total tokens consumed during generation"
    )
    latency_ms: int = Field(default=0, ge=0, description="Generation latency in milliseconds")
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)

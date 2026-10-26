"""Database model for 3-point grounded document summary."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

JSONType = JSON().with_variant(JSONB, "postgresql")


class DocumentSummaryModel(IdentifiableTimestampedModel):
    """Represents a 3-point grounded summary (1-1 with DocumentModel)."""

    __tablename__ = "document_summaries"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    problem_citations: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    contributions: Mapped[str] = mapped_column(Text, nullable=False)
    contribution_citations: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    limitations: Mapped[str] = mapped_column(Text, nullable=False)
    limitation_citations: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

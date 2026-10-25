"""Database models for Research Notes."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

TagsArrayType = JSON().with_variant(PG_ARRAY(Text), "postgresql")


class ResearchNoteModel(IdentifiableTimestampedModel):
    """Personal academic note with citation, bounding boxes and frozen evidence snapshot.

    Aligns with VeriScholar Database Specification (research_notes).
    Enforces optimistic concurrency control (OCC) and source detachment preservation.
    """

    __tablename__ = "research_notes"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    chunk_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    bounding_boxes: Mapped[list[list[float | int]]] = mapped_column(
        JSONType, default=list, nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    user_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(TagsArrayType, default=list, nullable=False)
    frozen_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    is_source_detached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    document = relationship("DocumentModel", foreign_keys=[document_id], lazy="selectin")
    chunk = relationship("DocumentChunkModel", foreign_keys=[chunk_id], lazy="selectin")

    @property
    def content(self) -> str:
        """Convenience alias for user_note or selected_text."""
        return self.user_note or self.selected_text or ""

    __table_args__ = (
        CheckConstraint("page_number >= 1", name="ck_research_notes_page_number_positive"),
        Index("idx_research_notes_user_doc", "user_id", "document_id"),
        Index("idx_research_notes_created", "created_at"),
        Index("idx_research_notes_user_created", "user_id", "created_at"),
    )

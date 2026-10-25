"""Database model for extracted scholarly references."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column


class ReferenceItemModel(IdentifiableTimestampedModel):
    """Represents a structured academic reference extracted from a document.

    Aligns with VeriScholar Database Specification Section 3.6 (reference_items).
    """

    __tablename__ = "reference_items"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ref_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_authors: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    parsed_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    arxiv_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    resolved_document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("document_id", "ref_index", name="uq_reference_items_document_ref_index"),
    )

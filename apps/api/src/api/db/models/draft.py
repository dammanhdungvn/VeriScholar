"""Database model for Research Writing Drafts."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DraftModel(IdentifiableTimestampedModel):
    """Academic research writing draft supporting LaTeX or Markdown.

    Enforces multi-tenant user isolation and optimistic concurrency control (OCC).
    """

    __tablename__ = "drafts"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Draft")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="latex")
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationship to user
    user = relationship("UserModel", foreign_keys=[user_id], lazy="selectin")

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_drafts_version_positive"),
        CheckConstraint("format IN ('latex', 'markdown')", name="ck_drafts_format_valid"),
        Index("idx_drafts_user_created", "user_id", "created_at"),
    )

"""Database model for Research Writing Drafts."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
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
    source_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("research_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Draft")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    bib_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="latex")
    template: Mapped[str | None] = mapped_column(String(50), nullable=True, default="blank")
    pdf_preview_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    previous_snapshot: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationship to user
    user = relationship("UserModel", foreign_keys=[user_id], lazy="selectin")

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_drafts_version_positive"),
        CheckConstraint("format IN ('latex', 'markdown')", name="ck_drafts_format_valid"),
        Index("idx_drafts_user_created", "user_id", "created_at"),
    )

    def __init__(self, **kwargs: Any) -> None:
        if "title" not in kwargs:
            self.title = "Untitled Draft"
        if "content" not in kwargs:
            self.content = ""
        if "bib_content" not in kwargs:
            self.bib_content = ""
        if "format" not in kwargs:
            self.format = "latex"
        if "template" not in kwargs:
            self.template = "blank"
        if "version" not in kwargs:
            self.version = 1
        for k, v in kwargs.items():
            setattr(self, k, v)

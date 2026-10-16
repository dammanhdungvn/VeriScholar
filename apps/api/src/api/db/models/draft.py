"""Database model for Research Writing Drafts."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import (
    Boolean,
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
    template: Mapped[str | None] = mapped_column(String(50), nullable=True, default="blank")
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationship to user
    user = relationship("UserModel", foreign_keys=[user_id], lazy="selectin")
    comments = relationship(
        "DraftCommentModel",
        foreign_keys="DraftCommentModel.draft_id",
        back_populates="draft",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_drafts_version_positive"),
        CheckConstraint("format IN ('latex', 'markdown')", name="ck_drafts_format_valid"),
        Index("idx_drafts_user_created", "user_id", "created_at"),
    )


class DraftCommentModel(IdentifiableTimestampedModel):
    """Peer review comment and line annotation attached to a draft.

    Supports threaded replies and resolution status tracking according to PRD §3.2.
    """

    __tablename__ = "draft_comments"

    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    selected_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    comment_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("draft_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    draft = relationship(
        "DraftModel", foreign_keys=[draft_id], lazy="selectin", back_populates="comments"
    )
    author = relationship("UserModel", foreign_keys=[author_id], lazy="selectin")
    parent = relationship(
        "DraftCommentModel",
        remote_side="DraftCommentModel.id",
        foreign_keys=[parent_id],
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_draft_comments_draft_created", "draft_id", "created_at"),
        Index("idx_draft_comments_parent", "parent_id"),
    )

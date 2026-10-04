"""Database models for Module 2: Drafting Workspace, Comments, and SAFE Fact-Checking."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from api.db.models.base import Base, IdentifiableTimestampedModel
from api.db.models.document import JSONType
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DraftModel(IdentifiableTimestampedModel):
    """Academic draft document model with OCC versioning."""

    __tablename__ = "drafts"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[str] = mapped_column(String(20), default="latex", nullable=False)
    template: Mapped[str] = mapped_column(String(50), default="ieee_conference", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_compiled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_compile_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pdf_preview_storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    comments = relationship(
        "DraftCommentModel", back_populates="draft", cascade="all, delete-orphan"
    )
    verifications = relationship(
        "DraftVerificationModel",
        back_populates="draft",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_drafts_user_updated", "user_id", "updated_at"),
        CheckConstraint("format IN ('latex', 'markdown')", name="ck_drafts_format"),
        CheckConstraint(
            "last_compile_status IS NULL OR "
            "last_compile_status IN ('success', 'failed', 'timeout')",
            name="ck_drafts_compile_status",
        ),
    )


class DraftCommentModel(IdentifiableTimestampedModel):
    """Line/sentence-level peer review comment for academic drafts."""

    __tablename__ = "draft_comments"

    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)

    draft = relationship("DraftModel", back_populates="comments")

    __table_args__ = (
        Index("idx_draft_comments_draft_line", "draft_id", "line_number"),
        CheckConstraint("line_number >= 1", name="ck_draft_comments_line_number"),
        CheckConstraint("status IN ('open', 'resolved')", name="ck_draft_comments_status"),
    )


class DraftVerificationModel(Base):
    """SAFE Fact-Checking verification audit log."""

    __tablename__ = "draft_verifications"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    claims_result: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONType, default=list, nullable=False
    )
    total_claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    supported_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contradicted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_enough_info_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    draft = relationship("DraftModel", back_populates="verifications")

    __table_args__ = (Index("idx_draft_verifications_draft", "draft_id", "created_at"),)

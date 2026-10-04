"""Database model for Public Resource Sharing & Instant Revocation."""

from datetime import datetime
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column


class ShareModel(IdentifiableTimestampedModel):
    """Represents a public share link for notes, documents, or drafts."""

    __tablename__ = "shares"

    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    permission: Mapped[str] = mapped_column(String(20), default="read_only", nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_shares_resource_user", "user_id", "resource_type", "resource_id"),)

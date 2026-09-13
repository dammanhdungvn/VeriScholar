"""Research Session database models."""

from datetime import UTC, datetime
from uuid import UUID

from api.db.models.base import Base, IdentifiableTimestampedModel
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ResearchSessionModel(IdentifiableTimestampedModel):
    """Represents a research inquiry and dual-chat session."""

    __tablename__ = "research_sessions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class SessionDocumentModel(Base):
    """Many-to-many association table linking documents to research sessions (max 5)."""

    __tablename__ = "session_documents"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

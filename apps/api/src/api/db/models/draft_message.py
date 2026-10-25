"""Database model for Agentic Writing Assistant Conversation Turns."""

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
from sqlalchemy.orm import Mapped, mapped_column


class DraftMessageModel(IdentifiableTimestampedModel):
    """Stores conversation turns, tool calls, and compilation attempts for Writing Agent."""

    __tablename__ = "draft_messages"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[dict | list | None] = mapped_column(JSONType, nullable=True)
    compile_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'tool')",
            name="ck_draft_messages_role",
        ),
        Index("idx_draft_messages_user_draft_time", "user_id", "draft_id", "created_at"),
    )

    def __init__(self, **kwargs: Any) -> None:
        if "compile_attempts" not in kwargs:
            self.compile_attempts = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

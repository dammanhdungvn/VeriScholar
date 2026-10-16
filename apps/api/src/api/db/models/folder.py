"""Library Folder database model (Module 4 & Module 1 integration)."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class FolderModel(IdentifiableTimestampedModel):
    """Hierarchical research project folders for library categorization."""

    __tablename__ = "folders"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True
    )
    color: Mapped[str] = mapped_column(String(30), default="#6366f1", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_folders_user_parent", "user_id", "parent_id"),
        UniqueConstraint("user_id", "parent_id", "name", name="uq_folders_user_parent_name"),
    )

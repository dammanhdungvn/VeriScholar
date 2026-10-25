"""Database model for Draft LaTeX Assets (figures and diagrams)."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column


class DraftAssetModel(IdentifiableTimestampedModel):
    """Assets and images stored in figures/ directory for scholarly LaTeX drafts."""

    __tablename__ = "draft_assets"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    blob_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_storage_blobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("draft_id", "file_name", name="uq_draft_assets_draft_filename"),
        CheckConstraint(
            "mime_type IN ('image/png', 'image/jpeg', 'image/webp', 'application/pdf')",
            name="ck_draft_assets_mime_type",
        ),
        Index("idx_draft_assets_user_draft", "user_id", "draft_id"),
    )

    def __init__(self, **kwargs: Any) -> None:
        if "filename" in kwargs and "file_name" not in kwargs:
            kwargs["file_name"] = kwargs.pop("filename")
        if "file_size_bytes" in kwargs and "byte_size" not in kwargs:
            kwargs["byte_size"] = kwargs.pop("file_size_bytes")
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def filename(self) -> str:
        return self.file_name

    @filename.setter
    def filename(self, value: str) -> None:
        self.file_name = value

    @property
    def file_size_bytes(self) -> int:
        return self.byte_size

    @file_size_bytes.setter
    def file_size_bytes(self, value: int) -> None:
        self.byte_size = value

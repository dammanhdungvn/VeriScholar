"""Multi-tenant Document database model."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

# Compatibility JSON type that defaults to JSONB on PostgreSQL, JSON on others
JSONType = JSON().with_variant(JSONB, "postgresql")


class DocumentModel(IdentifiableTimestampedModel):
    """Represents a scholarly document entity owned by a user."""

    __tablename__ = "documents"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    blob_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_storage_blobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    folder_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_metadata: Mapped[list[dict]] = mapped_column(JSONType, default=list, nullable=False)
    parsed_metadata: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="uploaded", nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_persistent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access_status: Mapped[str] = mapped_column(
        String(30), default="open_access_pdf", nullable=False
    )

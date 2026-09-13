"""Content-Addressable Storage (CAS) Blob database model."""

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class DocumentStorageBlobModel(IdentifiableTimestampedModel):
    """Represents a deduplicated physical binary file blob."""

    __tablename__ = "document_storage_blobs"

    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ref_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="processing", nullable=False)

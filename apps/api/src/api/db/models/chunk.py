"""Database model for extracted document text chunks with spatial bounding boxes."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, synonym


class DocumentChunkModel(IdentifiableTimestampedModel):
    """Represents a semantically coherent text chunk of an academic paper.

    Aligns with VeriScholar Database Specification Section 3.4 (document_chunks).
    Includes exact spatial bounding boxes for visual PDF grounding and token metrics.
    """

    __tablename__ = "document_chunks"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    bounding_boxes: Mapped[list[list[float | int]]] = mapped_column(
        JSONType, default=list, nullable=False
    )
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    content_tsv: Mapped[Any | None] = mapped_column(TSVECTOR, nullable=True)

    text_content = synonym("content")
    bbox_json = synonym("bounding_boxes")

    def __init__(self, **kwargs: Any) -> None:
        if "text_content" in kwargs and "content" not in kwargs:
            kwargs["content"] = kwargs.pop("text_content")
        if "bbox_json" in kwargs and "bounding_boxes" not in kwargs:
            kwargs["bounding_boxes"] = kwargs.pop("bbox_json")
        super().__init__(**kwargs)

    __table_args__ = (
        UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunks_document_chunk_idx"
        ),
        Index("ix_document_chunks_doc_page", "document_id", "page_number"),
    )

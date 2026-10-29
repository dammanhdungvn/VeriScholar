"""Database model for Compiled Academic LLM Wiki (wiki_pages)."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, synonym


class WikiPageModel(IdentifiableTimestampedModel):
    """Represents a compiled academic markdown wiki page with YAML metadata,

    [[wikilinks]], and vector embedding for cross-paper exploration.
    Aligns with Spec 05 (§1.D, §3) and Spec 00.
    """

    __tablename__ = "wiki_pages"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    folder_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    page_type: Mapped[str] = mapped_column(String(50), default="topic", nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    yaml_metadata: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    wikilinks: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    content_markdown = synonym("markdown_content")
    metadata_json = synonym("yaml_metadata")

    def __init__(self, **kwargs: Any) -> None:
        if "content_markdown" in kwargs and "markdown_content" not in kwargs:
            kwargs["markdown_content"] = kwargs.pop("content_markdown")
        if "metadata_json" in kwargs and "yaml_metadata" not in kwargs:
            kwargs["yaml_metadata"] = kwargs.pop("metadata_json")
        if "page_type" not in kwargs:
            kwargs["page_type"] = "topic"
        if "yaml_metadata" not in kwargs:
            kwargs["yaml_metadata"] = {}
        if "wikilinks" not in kwargs:
            kwargs["wikilinks"] = []
        super().__init__(**kwargs)

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_wiki_pages_user_slug"),
        Index("idx_wiki_pages_user_folder", "user_id", "folder_id"),
    )

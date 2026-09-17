"""Domain entities and value objects for Research Notes."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from core.domain.exceptions import ConcurrencyConflictError, InvalidNoteDataError


@dataclass(frozen=True)
class FrozenSnapshot:
    """Immutable evidence snapshot preserving original citation context.

    Ensures research thinking and exact quotations are preserved even if
    the source document PDF is permanently deleted from the workspace.
    """

    document_id: str | None
    document_title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    source_filename: str = ""
    page_number: int = 1
    chunk_id: str | None = None
    chunk_section: str | None = None
    selected_text: str = ""
    bounding_boxes: list[list[float | int]] = field(default_factory=list)
    captured_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "document_title": self.document_title,
            "authors": self.authors,
            "year": self.year,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "source_filename": self.source_filename,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "chunk_section": self.chunk_section,
            "selected_text": self.selected_text,
            "bounding_boxes": self.bounding_boxes,
            "captured_at": self.captured_at,
        }


@dataclass
class ResearchNote:
    """Aggregate Root representing a personal academic research note.

    Binds user notes, highlighted quotes, spatial coordinates, and evidence snapshot.
    Enforces optimistic concurrency control (OCC).
    """

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    document_id: UUID | None = None
    chunk_id: UUID | None = None
    selected_text: str = ""
    bounding_boxes: list[list[float | int]] = field(default_factory=list)
    page_number: int = 1
    user_note: str | None = None
    tags: list[str] = field(default_factory=list)
    frozen_snapshot: dict[str, Any] = field(default_factory=dict)
    is_source_detached: bool = False
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.selected_text or not self.selected_text.strip():
            raise InvalidNoteDataError("Selected text cannot be empty.")
        if self.page_number < 1:
            raise InvalidNoteDataError("Page number must be at least 1.")

    def update_content(
        self,
        user_note: str | None,
        tags: list[str] | None,
        expected_version: int,
    ) -> None:
        """Update personal memo and tags with optimistic concurrency check."""
        if self.version != expected_version:
            raise ConcurrencyConflictError(
                f"Resource version conflict: expected {expected_version}, current {self.version}"
            )
        if user_note is not None:
            self.user_note = user_note
        if tags is not None:
            # Deduplicate tags while preserving order
            seen: set[str] = set()
            cleaned_tags: list[str] = []
            for t in tags:
                clean_t = t.strip()
                if clean_t and clean_t not in seen:
                    seen.add(clean_t)
                    cleaned_tags.append(clean_t)
            self.tags = cleaned_tags

        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    def mark_detached(self) -> None:
        """Mark note as detached when source document is removed."""
        self.is_source_detached = True
        self.document_id = None
        self.chunk_id = None
        self.updated_at = datetime.now(timezone.utc)

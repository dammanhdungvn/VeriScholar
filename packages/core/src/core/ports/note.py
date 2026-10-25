"""Port interfaces for Research Notes."""

from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities.note import ResearchNote


class INoteRepositoryPort(ABC):
    """Port for persisting and querying research notes."""

    @abstractmethod
    async def create_note(self, note: ResearchNote) -> ResearchNote:
        """Persist a new research note."""

    @abstractmethod
    async def get_note_by_id(self, note_id: UUID, user_id: UUID) -> ResearchNote | None:
        """Retrieve a research note by ID and user ownership."""

    @abstractmethod
    async def list_notes(
        self,
        user_id: UUID,
        document_id: UUID | None = None,
        tag: str | None = None,
        folder_id: UUID | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[ResearchNote], int]:
        """List notes matching optional filters with pagination."""

    @abstractmethod
    async def update_note(
        self,
        note_id: UUID,
        user_id: UUID,
        user_note: str | None,
        tags: list[str] | None,
        expected_version: int,
    ) -> ResearchNote:
        """Update a note with optimistic concurrency control."""

    @abstractmethod
    async def delete_note(self, note_id: UUID, user_id: UUID) -> bool:
        """Delete a research note."""

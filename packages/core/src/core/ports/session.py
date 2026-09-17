"""Research Session Repository Port Protocols.

Defines port interfaces for persisting and managing multi-paper research sessions,
document sets, and chat turns in compliance with Hexagonal Architecture.
"""

from typing import Protocol
from uuid import UUID

from core.domain.entities.session import ResearchSession
from core.domain.entities.session_turn import SessionTurn


class ISessionRepositoryPort(Protocol):
    """Abstract repository port for managing research sessions."""

    async def create_session(
        self,
        user_id: UUID,
        title: str,
        initial_document_ids: list[UUID],
    ) -> ResearchSession:
        """Create a new research session and associate initial documents within an ACID boundary."""
        ...

    async def get_by_id(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> ResearchSession | None:
        """Retrieve a session by its ID ensuring multi-tenant ownership."""
        ...

    async def list_sessions(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        include_archived: bool = False,
        query: str | None = None,
    ) -> tuple[list[ResearchSession], int]:
        """List sessions for a user with pagination, filter, and optional search."""
        ...

    async def update_metadata_occ(
        self,
        session_id: UUID,
        user_id: UUID,
        title: str,
        expected_version: int,
    ) -> ResearchSession:
        """Update session title verifying optimistic concurrency control version."""
        ...

    async def update_viewport_occ(
        self,
        session_id: UUID,
        user_id: UUID,
        viewport_state: dict,
        active_tab: str,
        active_document_id: UUID | None,
        expected_version: int,
    ) -> ResearchSession:
        """Update session viewport state and active tab with OCC check."""
        ...

    async def delete_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a research session and its associations."""
        ...

    async def add_document(
        self,
        session_id: UUID,
        document_id: UUID,
    ) -> None:
        """Associate a document to the session."""
        ...


class ISessionChatRepositoryPort(Protocol):
    """Abstract repository port for session chat conversation turns."""

    async def save_turn(
        self,
        turn: SessionTurn,
    ) -> SessionTurn:
        """Persist a conversation turn."""
        ...

    async def list_turns(
        self,
        session_id: UUID,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[SessionTurn], int]:
        """List conversation turns for a session in chronological order."""
        ...

    async def clear_turns(
        self,
        session_id: UUID,
    ) -> int:
        """Delete all conversation turns for a session (idempotent)."""
        ...

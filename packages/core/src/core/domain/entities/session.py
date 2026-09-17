"""ResearchSession Domain Entity.

Represents a multi-paper research session (1 - 5 papers) facilitating dual-pane
reading, cross-document context namespacing, and persistent viewport tracking.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from core.domain.exceptions import (
    ArchivedSessionForbiddenError,
    DocumentAlreadyInSessionError,
    InvariantViolationError,
    SessionCapacityExceededError,
)
from core.domain.value_objects.enums import SessionActiveTab
from core.domain.value_objects.viewport_state import ViewportState

MAX_SESSION_DOCUMENTS = 5


class ResearchSession(BaseModel):
    """Domain Entity representing a multi-document deep reading research session."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Unique session identifier")
    user_id: UUID = Field(description="Owner user identifier")
    title: str = Field(min_length=1, max_length=255, description="Session title")
    active_document_id: UUID | None = Field(
        default=None, description="Currently active document in canvas viewer"
    )
    document_ids: list[UUID] = Field(
        default_factory=list,
        description="List of associated document identifiers (max 5)",
    )
    viewport_state: ViewportState = Field(
        default_factory=ViewportState,
        description="Active scroll, zoom, and page viewport state",
    )
    active_tab: SessionActiveTab = Field(
        default=SessionActiveTab.CHAT,
        description="Active sidebar/interaction tab",
    )
    is_archived: bool = Field(
        default=False,
        description="Whether session is archived after 30-day TTL expiration",
    )
    archived_at: datetime | None = Field(
        default=None,
        description="Timestamp when session was transitioned to archived state",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="OCC version counter for optimistic concurrency control",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Enforce clean non-whitespace title."""
        cleaned = v.strip()
        if not cleaned:
            raise InvariantViolationError("Session title cannot be empty or whitespace only")
        if len(cleaned) > 255:
            raise InvariantViolationError("Session title cannot exceed 255 characters")
        return cleaned

    @model_validator(mode="after")
    def validate_capacity_and_active_doc(self) -> "ResearchSession":
        """Enforce capacity constraint and active document consistency."""
        if len(self.document_ids) > MAX_SESSION_DOCUMENTS:
            raise SessionCapacityExceededError(
                f"Session capacity exceeded: Maximum {MAX_SESSION_DOCUMENTS} documents allowed, "
                f"got {len(self.document_ids)}"
            )

        if self.document_ids and self.active_document_id is None:
            object.__setattr__(self, "active_document_id", self.document_ids[0])

        if self.active_document_id and self.document_ids:
            if self.active_document_id not in self.document_ids:
                raise InvariantViolationError(
                    f"Active document {self.active_document_id} must be in session document_ids"
                )

        return self

    def add_document(self, document_id: UUID) -> None:
        """Add a document to the session adhering to capacity constraints."""
        if self.is_archived:
            raise ArchivedSessionForbiddenError("Cannot add document to an archived session")
        if document_id in self.document_ids:
            raise DocumentAlreadyInSessionError(f"Document {document_id} already in session")
        if len(self.document_ids) >= MAX_SESSION_DOCUMENTS:
            raise SessionCapacityExceededError(
                f"Session capacity exceeded: Maximum {MAX_SESSION_DOCUMENTS} documents allowed"
            )
        self.document_ids.append(document_id)
        if self.active_document_id is None:
            self.active_document_id = document_id
        self.updated_at = datetime.now(UTC)

    def remove_document(self, document_id: UUID) -> None:
        """Remove a document from the session and re-assign active document if necessary."""
        if self.is_archived:
            raise ArchivedSessionForbiddenError("Cannot remove document from an archived session")
        if document_id not in self.document_ids:
            return
        self.document_ids.remove(document_id)
        if self.active_document_id == document_id:
            self.active_document_id = self.document_ids[0] if self.document_ids else None
        self.updated_at = datetime.now(UTC)

    def update_title(self, title: str) -> None:
        """Update session title."""
        if self.is_archived:
            raise ArchivedSessionForbiddenError("Cannot modify an archived session")
        self.title = self.validate_title(title)
        self.updated_at = datetime.now(UTC)

    def update_viewport(
        self,
        viewport_state: ViewportState,
        active_tab: SessionActiveTab,
        active_document_id: UUID | None = None,
    ) -> None:
        """Update session viewport state, active tab, and currently selected active document."""
        if self.is_archived:
            raise ArchivedSessionForbiddenError("Cannot update viewport on an archived session")
        if active_document_id is not None:
            if self.document_ids and active_document_id not in self.document_ids:
                raise InvariantViolationError(
                    f"Active document {active_document_id} must be in session document_ids"
                )
            self.active_document_id = active_document_id
        self.viewport_state = viewport_state
        self.active_tab = active_tab
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        """Transition session to archived state."""
        self.is_archived = True
        self.archived_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def restore(self) -> None:
        """Restore archived session to active state."""
        self.is_archived = False
        self.archived_at = None
        self.updated_at = datetime.now(UTC)

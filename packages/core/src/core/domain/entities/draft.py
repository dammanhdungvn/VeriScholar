"""Domain entity for Research Writing Drafts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from core.domain.exceptions import ConcurrencyConflictError


@dataclass
class Draft:
    """Aggregate Root representing an academic research writing draft.

    Supports LaTeX or Markdown format with strict Optimistic Concurrency Control (OCC).
    """

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    title: str = "Untitled Draft"
    content: str = ""
    format: str = "latex"  # "latex" | "markdown"
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            self.title = "Untitled Draft"
        if self.format not in ("latex", "markdown"):
            self.format = "latex"

    def update_content(
        self,
        title: str | None,
        content: str | None,
        format: str | None,
        expected_version: int,
    ) -> None:
        """Update draft title and content with optimistic concurrency verification.

        Raises:
            ConcurrencyConflictError: When expected_version does not match current version.
        """
        if self.version != expected_version:
            raise ConcurrencyConflictError(
                f"Draft version conflict: expected {expected_version}, current {self.version}"
            )

        if title is not None:
            clean_title = title.strip()
            if clean_title:
                self.title = clean_title

        if content is not None:
            self.content = content

        if format is not None and format in ("latex", "markdown"):
            self.format = format

        self.version += 1
        self.updated_at = datetime.now(timezone.utc)


class DraftRole(str, Enum):
    """Hierarchical collaborative roles on research writing drafts."""

    OWNER = "owner"
    EDITOR = "editor"
    COMMENTER = "commenter"
    VIEWER = "viewer"

    @classmethod
    def from_str(cls, val: str) -> DraftRole:
        norm = val.lower().strip()
        if norm in ("owner",):
            return cls.OWNER
        elif norm in ("editor", "edit"):
            return cls.EDITOR
        elif norm in ("commenter", "comment"):
            return cls.COMMENTER
        elif norm in ("viewer", "view"):
            return cls.VIEWER
        return cls.VIEWER


@dataclass
class DraftAsset:
    """Domain representation of a research draft asset (figures, tables, bibtex)."""

    id: UUID = field(default_factory=uuid4)
    draft_id: UUID = field(default_factory=uuid4)
    asset_type: str = "image"  # image, bibtex, table, dataset, supplementary
    filename: str = ""
    file_size_bytes: int = 0
    storage_url: str = ""
    caption: str | None = None
    latex_label: str | None = None
    is_private: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DraftCollaborator:
    """Collaborator entity granted shared permissions on a research draft."""

    email: str
    permission: str = "editor"  # viewer, commenter, editor
    user_id: UUID | None = None
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def role(self) -> DraftRole:
        return DraftRole.from_str(self.permission)


@dataclass
class DraftShareSettings:
    """Aggregate sharing and access control settings for a research draft."""

    draft_id: UUID
    share_token: str
    share_url: str
    permission: str = "editor"
    allow_public_link: bool = False
    collaborators: list[DraftCollaborator] = field(default_factory=list)

    def resolve_role(
        self,
        draft_owner_id: UUID,
        user_id: UUID,
        user_email: str | None = None,
    ) -> DraftRole | None:
        """Resolve effective collaborative role for a user on this draft."""
        if draft_owner_id == user_id:
            return DraftRole.OWNER

        for c in self.collaborators:
            if (c.user_id and c.user_id == user_id) or (
                user_email and c.email.lower() == user_email.lower()
            ):
                return c.role

        if self.allow_public_link:
            return DraftRole.from_str(self.permission)

        return None


@dataclass
class DraftAssistResult:
    """Domain result from an AI writing assistant request."""

    draft_id: UUID
    action: str
    generated_text: str
    suggested_citations: list[str] = field(default_factory=list)
    diff_preview: str | None = None


def can_edit_draft_source(role: DraftRole) -> bool:
    """Only owner and editor can edit draft markup source."""
    return role in (DraftRole.OWNER, DraftRole.EDITOR)


def can_compile_draft(role: DraftRole) -> bool:
    """Only owner and editor can invoke LaTeX compilation."""
    return role in (DraftRole.OWNER, DraftRole.EDITOR)


def can_call_costly_ai(role: DraftRole) -> bool:
    """Only owner and editor can trigger cost-incurring LLM assist or fact verification."""
    return role in (DraftRole.OWNER, DraftRole.EDITOR)


def can_manage_draft_assets(role: DraftRole) -> bool:
    """Only owner and editor can upload or delete assets."""
    return role in (DraftRole.OWNER, DraftRole.EDITOR)


def can_manage_draft_share(role: DraftRole) -> bool:
    """Only the draft owner can configure share permissions."""
    return role == DraftRole.OWNER

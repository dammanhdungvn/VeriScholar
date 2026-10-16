"""Pure domain exceptions for VeriScholar.

These exceptions represent domain invariant violations and business rule failures.
They have zero dependencies on external frameworks or infrastructure layers.
"""


class DomainError(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity cannot be found."""


class InvariantViolationError(DomainError):
    """Raised when a core domain invariant is violated."""


class InvalidBoundingBoxError(InvariantViolationError):
    """Raised when bounding box coordinates violate spatial invariants."""


class InvalidPageMetadataError(InvariantViolationError):
    """Raised when page dimensions or rotation violate geometrical constraints."""


class FileSizeLimitExceededError(InvariantViolationError):
    """Raised when a file exceeds the maximum allowed size (e.g. 50MB)."""


class InvalidContentHashError(InvariantViolationError):
    """Raised when a content hash does not conform to SHA-256 hex format."""


class InvalidDocumentStateTransitionError(DomainError):
    """Raised when a document status transition violates the document lifecycle."""


class SessionCapacityExceededError(InvariantViolationError):
    """Raised when a research session exceeds maximum capacity (max 5 documents)."""


class SessionNotFoundError(EntityNotFoundError):
    """Raised when a research session cannot be found or is not accessible."""


class DocumentAlreadyInSessionError(InvariantViolationError):
    """Raised when attempting to add a document that already exists in the session."""


class ConcurrencyConflictError(DomainError):
    """Raised when an OCC version precondition (If-Match / ETag) fails."""


class PreconditionRequiredError(DomainError):
    """Raised when a required precondition header (such as If-Match) is missing."""


class ArchivedSessionForbiddenError(DomainError):
    """Raised when attempting modification actions on an archived session."""


class InvalidUrlSourceError(InvariantViolationError):
    """Raised when a provided URL for document ingestion is malformed or invalid."""


class NoteNotFoundError(EntityNotFoundError):
    """Raised when a research note cannot be found or is not accessible."""


class InvalidNoteDataError(InvariantViolationError):
    """Raised when note data violates domain validation rules."""


class NoteSynthesisError(DomainError):
    """Raised when AI synthesis fails or input notes are invalid."""


class DomainValidationError(InvariantViolationError):
    """Raised when a document fails domain academic validation gates."""

    def __init__(self, code: str, message: str, field: str = "file") -> None:
        super().__init__(message)
        self.code = code
        self.field = field


class SandboxInfrastructureUnavailableError(DomainError):
    """Raised when hardened sandbox infrastructure cannot be established or verified."""

    def __init__(self, message: str, reasons: list[str] | None = None) -> None:
        super().__init__(message)
        self.reasons = reasons or []


class ZipSlipSecurityError(DomainError):
    """Raised when an uploaded archive contains directory traversal, symlinks, or absolute paths."""


class MaliciousAssetContentError(DomainError):
    """Raised when an asset contains dangerous macro commands or invalid binary data."""


class AssetQuotaExceededError(DomainError):
    """Raised when asset archive exceeds maximum file count, ratio, or total size limits."""


class DraftRoleForbiddenError(DomainError):
    """Raised when an authenticated collaborator attempts an action forbidden for their role."""

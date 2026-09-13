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

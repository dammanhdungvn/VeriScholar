"""Domain enumerations for Module 1 (Deep Read) and core lifecycle states."""

from enum import StrEnum


class DocumentStatus(StrEnum):
    """Lifecycle status of a document entity."""

    UPLOADED = "uploaded"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentStage(StrEnum):
    """Specific processing stage within the ingestion pipeline."""

    QUEUED = "queued"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"


class BlobStatus(StrEnum):
    """Storage blob state in Content-Addressed Storage (CAS)."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionTurnFinishReason(StrEnum):
    """Reason why an assistant turn generation completed."""

    STOP = "stop"
    LENGTH = "length"
    ABSTENTION = "abstention"
    ERROR = "error"

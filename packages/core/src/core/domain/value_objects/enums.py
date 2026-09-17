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
    VALIDATION = "validation"
    LAYOUT_DETECTION = "layout_detection"
    RUNNING_OCR = "running_ocr"
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


class SessionActiveTab(StrEnum):
    """Active UI tab within the dual-pane research workspace."""

    CHAT = "chat"
    NOTES = "notes"
    SUMMARY = "summary"
    GRAPH = "graph"
    DRAFT = "draft"

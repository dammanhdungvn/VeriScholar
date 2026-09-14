"""Domain Entities for VeriScholar Core."""

from core.domain.entities.blob import DocumentStorageBlob
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.document import Document
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    extract_references_from_text,
    parse_reference_item,
)
from core.domain.entities.session_turn import SessionTurn

__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentStorageBlob",
    "ExtractedReference",
    "ParsedReferenceInfo",
    "SessionTurn",
    "extract_references_from_text",
    "parse_reference_item",
]

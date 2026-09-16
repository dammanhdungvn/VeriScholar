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
from core.domain.entities.structure import DocumentSection, DocumentStructure
from core.domain.entities.summary import DocumentSummary, SummaryPoint

__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentSection",
    "DocumentStorageBlob",
    "DocumentStructure",
    "DocumentSummary",
    "ExtractedReference",
    "ParsedReferenceInfo",
    "SessionTurn",
    "SummaryPoint",
    "extract_references_from_text",
    "parse_reference_item",
]

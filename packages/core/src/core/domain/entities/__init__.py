"""Domain Entities for VeriScholar Core."""

from core.domain.entities.blob import DocumentStorageBlob
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.document import Document
from core.domain.entities.note import FrozenSnapshot, ResearchNote
from core.domain.entities.note_synthesis import (
    InteractiveBadge,
    NoteSynthesis,
    SynthesisMode,
)
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    extract_references_from_text,
    parse_reference_item,
)
from core.domain.entities.session import ResearchSession
from core.domain.entities.session_turn import CitationItem, SessionTurn
from core.domain.entities.structure import DocumentSection, DocumentStructure
from core.domain.entities.summary import DocumentSummary, SummaryPoint

__all__ = [
    "CitationItem",
    "Document",
    "DocumentChunk",
    "DocumentSection",
    "DocumentStorageBlob",
    "DocumentStructure",
    "DocumentSummary",
    "ExtractedReference",
    "FrozenSnapshot",
    "InteractiveBadge",
    "NoteSynthesis",
    "ParsedReferenceInfo",
    "ResearchNote",
    "ResearchSession",
    "SessionTurn",
    "SummaryPoint",
    "SynthesisMode",
    "extract_references_from_text",
    "parse_reference_item",
]

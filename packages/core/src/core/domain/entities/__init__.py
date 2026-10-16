"""Domain Entities for VeriScholar Core."""

from core.domain.entities.blob import DocumentStorageBlob
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.document import Document
from core.domain.entities.draft import Draft
from core.domain.entities.latex import LatexCompilationResult, LatexSyntaxError
from core.domain.entities.note import FrozenSnapshot, ResearchNote
from core.domain.entities.note_synthesis import (
    InteractiveBadge,
    NoteSynthesis,
    SynthesisMode,
)
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    ResolvedAcademicReference,
    extract_references_from_text,
    parse_reference_item,
)
from core.domain.entities.safe_claim import (
    AtomicClaim,
    FactVerificationReport,
    FactVerificationStatus,
)
from core.domain.entities.session import ResearchSession
from core.domain.entities.session_turn import CitationItem, SessionTurn
from core.domain.entities.structure import DocumentSection, DocumentStructure
from core.domain.entities.summary import DocumentSummary, SummaryPoint

__all__ = [
    "AtomicClaim",
    "CitationItem",
    "Document",
    "DocumentChunk",
    "DocumentSection",
    "DocumentStorageBlob",
    "DocumentStructure",
    "DocumentSummary",
    "Draft",
    "ExtractedReference",
    "FactVerificationReport",
    "FactVerificationStatus",
    "FrozenSnapshot",
    "InteractiveBadge",
    "LatexCompilationResult",
    "LatexSyntaxError",
    "NoteSynthesis",
    "ParsedReferenceInfo",
    "ResearchNote",
    "ResearchSession",
    "ResolvedAcademicReference",
    "SessionTurn",
    "SummaryPoint",
    "SynthesisMode",
    "extract_references_from_text",
    "parse_reference_item",
]

"""Domain Entities for VeriScholar Core."""

from core.domain.entities.blob import DocumentStorageBlob
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.document import Document
from core.domain.entities.draft import Draft
from core.domain.entities.folder import (
    ComparisonMatrixResult,
    ComparisonMatrixRow,
    FolderEntity,
    SufficiencyEvaluation,
)
from core.domain.entities.latex import LatexCompilationResult, LatexSyntaxError
from core.domain.entities.note import FrozenSnapshot, ResearchNote
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    ResolvedAcademicReference,
    extract_references_from_text,
    parse_reference_item,
)
from core.domain.entities.session import ResearchSession
from core.domain.entities.session_turn import CitationItem, SessionTurn
from core.domain.entities.structure import DocumentSection, DocumentStructure
from core.domain.entities.summary import DocumentSummary, SummaryPoint

__all__ = [
    "CitationItem",
    "ComparisonMatrixResult",
    "ComparisonMatrixRow",
    "Document",
    "DocumentChunk",
    "DocumentSection",
    "DocumentStorageBlob",
    "DocumentStructure",
    "DocumentSummary",
    "Draft",
    "ExtractedReference",
    "FolderEntity",
    "FrozenSnapshot",
    "LatexCompilationResult",
    "LatexSyntaxError",
    "ParsedReferenceInfo",
    "ResearchNote",
    "ResearchSession",
    "ResolvedAcademicReference",
    "SessionTurn",
    "SufficiencyEvaluation",
    "SummaryPoint",
    "extract_references_from_text",
    "parse_reference_item",
]

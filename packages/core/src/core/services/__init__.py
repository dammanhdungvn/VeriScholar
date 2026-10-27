"""Core domain services package."""

from core.services.academic_cache import GlobalAcademicCache
from core.services.document_validator import AcademicPaperValidator
from core.services.exa_resolver import (
    ExaAcademicResolverAdapter,
    InMemoryAcademicResolverAdapter,
)
from core.services.graph_extractor import (
    VALID_EDGE_TYPES,
    VALID_NODE_TYPES,
    ExtractedEntity,
    ExtractedGraphPayload,
    ExtractedRelation,
    MetricContextTuple,
    detect_folder_cycle,
    normalize_canonical_name,
)
from core.services.guardrails import (
    AIGuardrailsService,
    InputGuardrailResult,
    OutputGuardrailResult,
)
from core.services.socratic_roadmap import (
    BridgeHintPayload,
    extract_and_strip_bridge_hint,
    extract_scholarly_identifiers,
)

__all__ = [
    "AcademicPaperValidator",
    "AIGuardrailsService",
    "BridgeHintPayload",
    "ExaAcademicResolverAdapter",
    "ExtractedEntity",
    "ExtractedGraphPayload",
    "ExtractedRelation",
    "GlobalAcademicCache",
    "InMemoryAcademicResolverAdapter",
    "InputGuardrailResult",
    "MetricContextTuple",
    "OutputGuardrailResult",
    "VALID_EDGE_TYPES",
    "VALID_NODE_TYPES",
    "detect_folder_cycle",
    "extract_and_strip_bridge_hint",
    "extract_scholarly_identifiers",
    "normalize_canonical_name",
]

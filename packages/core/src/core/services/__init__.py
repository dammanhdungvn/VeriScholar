"""Core domain services package."""

from core.services.academic_cache import GlobalAcademicCache
from core.services.document_validator import AcademicPaperValidator
from core.services.exa_resolver import (
    ExaAcademicResolverAdapter,
    InMemoryAcademicResolverAdapter,
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
    "GlobalAcademicCache",
    "InMemoryAcademicResolverAdapter",
    "InputGuardrailResult",
    "OutputGuardrailResult",
    "extract_and_strip_bridge_hint",
    "extract_scholarly_identifiers",
]

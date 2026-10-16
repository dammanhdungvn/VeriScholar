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

__all__ = [
    "AcademicPaperValidator",
    "AIGuardrailsService",
    "ExaAcademicResolverAdapter",
    "GlobalAcademicCache",
    "InMemoryAcademicResolverAdapter",
    "InputGuardrailResult",
    "OutputGuardrailResult",
]

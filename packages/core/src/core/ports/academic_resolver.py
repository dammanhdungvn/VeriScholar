"""Academic Search Resolver Port.

Aligns with VeriScholar PRD §3.3 (Academic Reference Ingestion & Multi-Paper Synthesis).
"""

from abc import ABC, abstractmethod

from core.domain.entities.reference import ExtractedReference, ResolvedAcademicReference


class IAcademicSearchResolverPort(ABC):
    """Port defining the contract for academic reference search and resolution."""

    @abstractmethod
    async def resolve_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference:
        """Resolve a single extracted reference to rich academic metadata."""
        pass

    @abstractmethod
    async def resolve_batch(
        self, references: list[ExtractedReference]
    ) -> list[ResolvedAcademicReference]:
        """Resolve a batch of extracted references."""
        pass

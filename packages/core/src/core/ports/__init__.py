"""Ports defining abstract contracts for inbound and outbound adapters."""

from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.ports.chunk import IChunkExtractorPort
from core.ports.idempotency import IIdempotencyPort
from core.ports.note import INoteRepositoryPort
from core.ports.session import ISessionRepositoryPort
from core.ports.storage import IBlobStoragePort
from core.ports.structure import IStructureExtractorPort
from core.ports.summary import IDocumentSummarizerPort

__all__ = [
    "IAcademicSearchResolverPort",
    "IBlobStoragePort",
    "IChunkExtractorPort",
    "IDocumentSummarizerPort",
    "IIdempotencyPort",
    "INoteRepositoryPort",
    "ISessionRepositoryPort",
    "IStructureExtractorPort",
]

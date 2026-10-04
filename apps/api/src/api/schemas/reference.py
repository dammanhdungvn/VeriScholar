"""Pydantic schemas for References Resolving & Citation Graph (Module 3)."""

from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class ReferenceResolveItemRequest(BaseModel):
    """Single reference resolution query item."""

    ref_id: str = Field(description="Client-side reference tracking identifier (e.g. 'ref_1')")
    doi: str | None = Field(default=None, description="Digital Object Identifier (DOI)")
    arxiv_id: str | None = Field(default=None, description="arXiv identifier (e.g. '1706.03762')")
    title: str | None = Field(default=None, description="Extracted reference paper title")


class ReferenceResolveRequest(BaseModel):
    """Batch reference resolution request payload."""

    references: list[ReferenceResolveItemRequest] = Field(
        min_length=1,
        max_length=50,
        description="List of academic references to batch resolve (1-50 items)",
    )


class ResolvedReferenceData(BaseModel):
    """Enriched scholarly reference metadata from Global Academic Cache."""

    ref_id: str = Field(description="Client-side tracking identifier")
    doi: str | None = Field(default=None, description="Normalized DOI")
    arxiv_id: str | None = Field(default=None, description="Normalized arXiv ID")
    title: str = Field(description="Standardized academic paper title")
    authors: list[str] = Field(default_factory=list, description="Author names")
    year: int | None = Field(default=None, description="Publication year")
    venue: str | None = Field(default=None, description="Publication venue or journal")
    citation_count: int = Field(default=0, ge=0, description="Global citation count")
    has_open_access_pdf: bool = Field(default=False, description="Open access PDF availability")
    pdf_download_url: str | None = Field(default=None, description="Direct Open Access PDF URL")


class ReferenceResolveResponseData(BaseModel):
    """Response payload containing resolved references and cache metrics."""

    resolved: list[ResolvedReferenceData] = Field(description="List of resolved reference items")
    cached_count: int = Field(default=0, ge=0, description="Items served from cache")
    live_resolved_count: int = Field(default=0, ge=0, description="Items resolved live via APIs")


class ReferenceResolveEnvelope(SingleResponseEnvelope[ReferenceResolveResponseData]):
    """Standard Envelope for batch reference resolution."""


class GraphNode(BaseModel):
    """Citation graph node representation."""

    id: str = Field(description="Unique node identifier (document UUID or normalized reference ID)")
    title: str = Field(description="Display title of the academic paper")
    year: int | None = Field(default=None, description="Publication year")
    type: str = Field(description="Node role in graph ('root', 'cited', 'citing')")


class GraphEdge(BaseModel):
    """Citation graph directional relation edge."""

    source: str = Field(description="Originating paper node ID")
    target: str = Field(description="Target paper node ID")
    relation: str = Field(
        default="CITES",
        description="Bibliographic relationship ('CITES', 'EXTENDS', 'BENCHMARKS_ON')",
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Edge confidence score")


class CitationGraphResponseData(BaseModel):
    """Citation knowledge graph node-link schema with cycle breaking."""

    root_document_id: UUID = Field(description="UUID of the root document being explored")
    nodes: list[GraphNode] = Field(description="Graph vertex list")
    edges: list[GraphEdge] = Field(description="Graph directed edge list")


class CitationGraphEnvelope(SingleResponseEnvelope[CitationGraphResponseData]):
    """Standard Envelope for citation knowledge graph query."""

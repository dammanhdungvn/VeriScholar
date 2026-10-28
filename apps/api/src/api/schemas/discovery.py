"""Pydantic schemas for scholarly literature discovery and zero-to-reading ingestion."""

from uuid import UUID

from pydantic import BaseModel, Field


class DiscoverySearchRequest(BaseModel):
    """Payload for searching academic literature across external sources."""

    query: str = Field(min_length=1, max_length=500, description="Academic search query or DOI")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of search results")
    is_peer_reviewed_only: bool = Field(
        default=False,
        description="Filter to only return peer-reviewed publications",
    )


class OpenReadingRequest(BaseModel):
    """Payload for initiating a 1-click Zero-to-Reading session from discovery."""

    title: str = Field(min_length=1, max_length=500, description="Paper title")
    authors: list[str] = Field(default_factory=list, description="Author list")
    publication_year: int | None = Field(default=None, description="Year published")
    venue: str | None = Field(default=None, max_length=255, description="Publication venue")
    doi: str | None = Field(default=None, max_length=255, description="DOI identifier")
    arxiv_id: str | None = Field(default=None, max_length=100, description="arXiv identifier")
    abstract: str | None = Field(default=None, description="Paper abstract text")
    pdf_url: str | None = Field(
        default=None, max_length=1000, description="Direct URL to open-access PDF"
    )


class OpenReadingResponse(BaseModel):
    """Response payload containing created session and document identifiers."""

    session_id: UUID = Field(description="Created research session identifier")
    document_id: UUID = Field(description="Created document identifier")
    status: str = Field(description="Document processing status ('parsing' or 'abstract_only')")
    access_status: str = Field(description="Access status ('open_access_pdf' or 'abstract_only')")

    @property
    def document_status(self) -> str:
        """Alias for status to maintain schema compatibility with test harness."""
        return self.status

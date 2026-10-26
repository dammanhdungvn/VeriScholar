"""Pure domain port and search result entities for external academic literature discovery.

Adheres strictly to Hexagonal Architecture: zero external I/O or framework dependencies.
"""

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class ScholarlyPaperSearchResult(BaseModel):
    """Normalized search result item across external academic repositories."""

    title: str = Field(description="Title of the academic publication")
    authors: list[str] = Field(default_factory=list, description="Author list")
    publication_year: int | None = Field(default=None, description="Year of publication")
    venue: str | None = Field(default=None, description="Publication venue or journal")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    arxiv_id: str | None = Field(default=None, description="arXiv identifier")
    abstract: str | None = Field(default=None, description="Paper abstract text")
    access_status: Literal["open_access_pdf", "abstract_only"] = Field(
        default="abstract_only",
        description="Whether full open-access PDF is available or abstract only",
    )
    pdf_url: str | None = Field(
        default=None, description="Direct URL to open-access PDF if available"
    )


class IScholarlySearchPort(ABC):
    """Abstract port defining external academic literature search contract."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[ScholarlyPaperSearchResult]:
        """Search academic literature across scholarly sources with unified deduplication."""
        pass

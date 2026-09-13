"""Standard API response envelope models."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    """Envelope metadata accompanying all successful responses."""

    request_id: str = Field(
        default_factory=lambda: f"req_{uuid4().hex[:12]}",
        description="Unique request tracing ID",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Server timestamp in UTC",
    )


class SingleResponseEnvelope(BaseModel, Generic[DataT]):
    """Standard Single Resource Envelope (RFC-compliant wrapper)."""

    success: bool = Field(default=True, description="Indicates request success")
    data: DataT = Field(description="Primary response payload")
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response tracking metadata",
    )


class PaginationMeta(BaseModel):
    """Pagination tracking metadata conforming to RFC 8288 standard."""

    total: int = Field(description="Total number of items matching query")
    page: int = Field(description="Current page index (1-based)")
    per_page: int = Field(description="Number of items returned per page")
    total_pages: int = Field(description="Total number of available pages")
    request_id: str = Field(
        default_factory=lambda: f"req_{uuid4().hex[:12]}",
        description="Unique request tracing ID",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Server timestamp in UTC",
    )


class PaginationLinks(BaseModel):
    """HATEOAS pagination links conforming to RFC 8288."""

    first: str = Field(description="Link to the first page")
    prev: str | None = Field(
        default=None,
        description="Link to previous page (null if on first page)",
    )
    self: str = Field(description="Link to current page")
    next: str | None = Field(
        default=None,
        description="Link to next page (null if on last page)",
    )
    last: str = Field(description="Link to the last page")


class PaginatedResponseEnvelope(BaseModel, Generic[DataT]):
    """Standard RFC 8288 Paginated Collection Envelope."""

    success: bool = Field(default=True, description="Indicates request success")
    data: list[DataT] = Field(description="List of items for current page")
    meta: PaginationMeta = Field(description="Pagination metadata")
    links: PaginationLinks = Field(description="RFC 8288 navigation links")

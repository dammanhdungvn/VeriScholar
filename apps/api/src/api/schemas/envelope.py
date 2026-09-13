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

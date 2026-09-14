"""Idempotency Port defining abstract contracts for 24-Hour idempotency window."""

from abc import ABC, abstractmethod
from typing import Any


class IIdempotencyPort(ABC):
    """Abstract Port for caching and retrieving idempotent responses (RFC / API Specs)."""

    @abstractmethod
    async def get_response(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached response data by idempotency key if present and within TTL."""
        ...

    @abstractmethod
    async def store_response(
        self,
        key: str,
        response_data: dict[str, Any],
        status_code: int = 202,
        ttl_seconds: int = 86400,
    ) -> None:
        """Store response data associated with idempotency key with TTL window (default 24h)."""
        ...

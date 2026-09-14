"""Cache and Idempotency Adapters adhering to 24-Hour retention window."""

import copy
import json
import logging
import time
from typing import Any

from core.ports.idempotency import IIdempotencyPort

logger = logging.getLogger(__name__)


class InMemoryIdempotencyAdapter(IIdempotencyPort):
    """Deterministic in-memory idempotency cache for development, testing and fallback."""

    def __init__(self) -> None:
        # Key -> (expires_at_timestamp, payload_dict, status_code)
        self._cache: dict[str, tuple[float, dict[str, Any], int]] = {}

    async def get_response(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached response data by key if present and not expired."""
        if key not in self._cache:
            return None

        expires_at, data, _ = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            return None

        return copy.deepcopy(data)

    async def store_response(
        self,
        key: str,
        response_data: dict[str, Any],
        status_code: int = 202,
        ttl_seconds: int = 86400,
    ) -> None:
        """Store response data associated with key with expiration TTL in seconds."""
        expires_at = time.time() + ttl_seconds
        self._cache[key] = (expires_at, copy.deepcopy(response_data), status_code)

    def clear(self) -> None:
        """Clear all entries (useful in testing suites)."""
        self._cache.clear()


class RedisIdempotencyAdapter(IIdempotencyPort):
    """Production Redis adapter with 24-Hour TTL and transparent in-memory fallback."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        fallback: IIdempotencyPort | None = None,
    ) -> None:
        self.redis_url = redis_url
        self._fallback = fallback or InMemoryIdempotencyAdapter()
        self._client: Any = None
        self._redis_available: bool = True

    async def _get_client(self) -> Any:
        if self._client is None and self._redis_available:
            try:
                import redis.asyncio as aioredis

                self._client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.0,
                )
            except Exception as e:
                logger.warning(
                    "Redis not available, falling back to in-memory idempotency: %s",
                    e,
                )
                self._redis_available = False
        return self._client

    async def get_response(self, key: str) -> dict[str, Any] | None:
        """Retrieve from Redis or fallback to in-memory cache."""
        client = await self._get_client()
        if client and self._redis_available:
            try:
                val = await client.get(key)
                if val is not None:
                    return json.loads(val)  # type: ignore[no-any-return]
                return None
            except Exception as e:
                logger.warning("Redis get error for key %s: %s; using fallback", key, e)

        return await self._fallback.get_response(key)

    async def store_response(
        self,
        key: str,
        response_data: dict[str, Any],
        status_code: int = 202,
        ttl_seconds: int = 86400,
    ) -> None:
        """Store into Redis with TTL or fallback to in-memory cache."""
        client = await self._get_client()
        stored_in_redis = False

        if client and self._redis_available:
            try:
                json_str = json.dumps(response_data)
                await client.set(key, json_str, ex=ttl_seconds)
                stored_in_redis = True
            except Exception as e:
                logger.warning("Redis set error for key %s: %s; using fallback", key, e)

        # Always also store in fallback to ensure local memory consistency
        if not stored_in_redis or self._fallback:
            await self._fallback.store_response(
                key=key,
                response_data=response_data,
                status_code=status_code,
                ttl_seconds=ttl_seconds,
            )

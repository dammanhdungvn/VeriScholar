"""Unit tests for InMemoryIdempotencyAdapter and RedisIdempotencyAdapter."""

import pytest
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter, RedisIdempotencyAdapter


@pytest.mark.asyncio
async def test_in_memory_idempotency_store_and_get() -> None:
    adapter = InMemoryIdempotencyAdapter()
    key = "user1:doc1:parse:abc-123"
    data = {"success": True, "data": {"id": "123", "status": "processing"}}

    assert await adapter.get_response(key) is None

    await adapter.store_response(key, data, status_code=202, ttl_seconds=3600)
    cached = await adapter.get_response(key)
    assert isinstance(cached, dict)
    assert cached["data"]["id"] == "123"

    # Verify deepcopy
    cached["data"]["id"] = "mutated"
    cached_again = await adapter.get_response(key)
    assert isinstance(cached_again, dict)
    assert cached_again["data"]["id"] == "123"


@pytest.mark.asyncio
async def test_in_memory_idempotency_expired_ttl() -> None:
    adapter = InMemoryIdempotencyAdapter()
    key = "user1:doc1:parse:expired"
    data = {"status": "ok"}

    # Store with TTL = 0 (immediately expired)
    await adapter.store_response(key, data, ttl_seconds=-1)
    assert await adapter.get_response(key) is None


@pytest.mark.asyncio
async def test_redis_idempotency_adapter_fallback_when_no_redis() -> None:
    adapter = RedisIdempotencyAdapter(redis_url="redis://localhost:9999/0")
    key = "user1:doc1:parse:fallback-key"
    data = {"id": "fallback-id", "status": "processing"}

    await adapter.store_response(key, data, status_code=202, ttl_seconds=60)
    result = await adapter.get_response(key)
    assert result is not None

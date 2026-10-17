"""Empirical Challenge Suite: Redis Unavailability & Idempotency Fallback Testing.

Tests:
1. RedisIdempotencyAdapter graceful degradation when Redis connection fails on connect.
2. RedisIdempotencyAdapter fallback to InMemoryIdempotencyAdapter when get_response raises ConnectionError.
3. RedisIdempotencyAdapter fallback to InMemoryIdempotencyAdapter when store_response raises ConnectionError.
4. LibrarySynthesisService matrix generation and query caching across simulated Redis failure.
5. Empirical reproduction of AI Tracing NameError defect when Langfuse client is active.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.services.ai_tracing_service import AITracingService
from api.services.library_synthesis_service import LibrarySynthesisService
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter, RedisIdempotencyAdapter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def in_memory_db_session() -> AsyncIterator[AsyncSession]:
    """Provide isolated in-memory SQLite database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_redis_adapter_fallback_on_unreachable_host():
    """Verify RedisIdempotencyAdapter degrades gracefully when pointing to dead port."""
    # Point to a dead local port where Redis is guaranteed not running
    fallback = InMemoryIdempotencyAdapter()
    adapter = RedisIdempotencyAdapter(
        redis_url="redis://127.0.0.1:65530/0",
        fallback=fallback,
    )

    test_key = "test:idempotency:offline_redis"
    test_data = {"status": "success", "cached_at": 123456789}

    # Storing must not throw an exception, and must succeed via in-memory fallback
    await adapter.store_response(test_key, test_data, ttl_seconds=60)

    # Retrieval must return the stored payload from fallback
    retrieved = await adapter.get_response(test_key)
    assert retrieved is not None
    assert retrieved == test_data

    # Verify fallback cache holds the item
    fallback_val = await fallback.get_response(test_key)
    assert fallback_val == test_data


@pytest.mark.asyncio
async def test_redis_adapter_fallback_when_get_raises_connection_error():
    """Verify RedisIdempotencyAdapter transparently falls back when get_response raises ConnectionError."""
    fallback = InMemoryIdempotencyAdapter()
    adapter = RedisIdempotencyAdapter(
        redis_url="redis://localhost:6379/0",
        fallback=fallback,
    )

    # Pre-populate fallback
    test_key = "test:key:get_failure"
    expected_data = {"result": "fallback_hit"}
    await fallback.store_response(test_key, expected_data)

    # Mock Redis client where get() raises ConnectionError
    mock_client = AsyncMock()
    mock_client.get.side_effect = ConnectionError("Connection refused by Redis server")
    adapter._client = mock_client
    adapter._redis_available = True

    # Call get_response - should catch ConnectionError, log warning, and return from fallback
    result = await adapter.get_response(test_key)
    assert result == expected_data
    mock_client.get.assert_awaited_once_with(test_key)


@pytest.mark.asyncio
async def test_redis_adapter_fallback_when_set_raises_connection_error():
    """Verify RedisIdempotencyAdapter stores in fallback when set_response raises ConnectionError."""
    fallback = InMemoryIdempotencyAdapter()
    adapter = RedisIdempotencyAdapter(
        redis_url="redis://localhost:6379/0",
        fallback=fallback,
    )

    # Mock Redis client where set() raises TimeoutError
    mock_client = AsyncMock()
    mock_client.set.side_effect = TimeoutError("Redis socket read timeout")
    adapter._client = mock_client
    adapter._redis_available = True

    test_key = "test:key:set_failure"
    payload = {"data": "must_not_be_lost"}

    # Store into adapter - should catch TimeoutError and write to fallback
    await adapter.store_response(test_key, payload, ttl_seconds=120)

    # Verify fallback holds the payload
    in_mem_res = await fallback.get_response(test_key)
    assert in_mem_res == payload


@pytest.mark.asyncio
async def test_library_synthesis_service_caching_with_dead_redis():
    """Verify LibrarySynthesisService matrix generation and caching with offline Redis."""
    async with in_memory_db_session() as session:
        user_id = uuid4()
        user = UserModel(
            id=user_id,
            email="researcher_dead_redis@verischolar.org",
            full_name="Dr. Offline Redis",
            role="researcher",
            hashed_password="mock",
            is_active=True,
        )
        session.add(user)

        folder_id = uuid4()
        folder = FolderModel(id=folder_id, user_id=user_id, name="Offline Folder")
        session.add(folder)

        doc1 = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            folder_id=folder_id,
            filename="paper1.pdf",
            title="Attention Mechanisms in Large Contexts",
            authors=["Researcher A"],
            publication_year=2024,
            content_hash="hash_p1",
            file_size_bytes=1024,
        )
        doc2 = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            folder_id=folder_id,
            filename="paper2.pdf",
            title="Vaccine Distribution Observational Study",
            authors=["Researcher B"],
            publication_year=2023,
            content_hash="hash_p2",
            file_size_bytes=2048,
        )
        session.add_all([doc1, doc2])
        await session.commit()

        # Offline Redis adapter pointing to closed port
        offline_adapter = RedisIdempotencyAdapter(
            redis_url="redis://127.0.0.1:65531/0",
            fallback=InMemoryIdempotencyAdapter(),
        )

        service = LibrarySynthesisService(
            db=session,
            ai_tracing=None,  # Null context to isolate caching logic
            cache=offline_adapter,
        )

        # 1. First call: executes extraction and caches into fallback without crashing
        res1 = await service.generate_comparison_matrix(
            user_id=user_id,
            topic="Attention and Vaccines",
            folder_id=folder_id,
            limit=10,
            offset=0,
        )
        assert res1.total_count == 2
        assert len(res1.rows) == 2

        # 2. Second call: hits cache via fallback adapter
        res2 = await service.generate_comparison_matrix(
            user_id=user_id,
            topic="Attention and Vaccines",
            folder_id=folder_id,
            limit=10,
            offset=0,
        )
        assert res2.total_count == 2
        assert [r.title for r in res2.rows] == [r.title for r in res1.rows]


@pytest.mark.asyncio
async def test_ai_tracing_version_parameter_and_span_creation():
    """Verify AITracingService.trace() accepts version and creates span without NameError."""
    ai_tracing = AITracingService()
    mock_langfuse_client = MagicMock()
    ai_tracing.client = mock_langfuse_client

    # Calling trace() with and without explicit version must succeed cleanly
    span1 = ai_tracing.trace(name="test_trace_default", user_id=uuid4())
    assert span1 is not None

    span2 = ai_tracing.trace(name="test_trace_explicit", user_id=uuid4(), version="1.0.0-rc1")
    assert span2 is not None

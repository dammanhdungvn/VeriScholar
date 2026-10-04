"""Unit and isolation tests for CostControlService and token limit enforcement."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.db.models.user import UserModel
from api.services.cost_control_service import CostControlService
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_check_token_quota_within_limit() -> None:
    """Pass token quota check when tokens used is below quota."""
    service = CostControlService()
    user = UserModel(
        id=uuid4(),
        email="test@scholar.org",
        full_name="Scholar",
        hashed_password="pw",
        role="researcher",
        token_quota=50000,
        tokens_used=10000,
    )
    mock_db = AsyncMock()
    # Should not raise exception
    await service.check_token_quota(mock_db, user, estimated_tokens=5000)


@pytest.mark.asyncio
async def test_check_token_quota_exceeded() -> None:
    """Raise HTTP 429 QUOTA_EXCEEDED when token usage breaches limit."""
    service = CostControlService()
    user = UserModel(
        id=uuid4(),
        email="test@scholar.org",
        full_name="Scholar",
        hashed_password="pw",
        role="researcher",
        token_quota=20000,
        tokens_used=19500,
    )
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await service.check_token_quota(mock_db, user, estimated_tokens=1000)

    assert exc_info.value.status_code == 429
    assert exc_info.value.detail["code"] == "QUOTA_EXCEEDED"


@pytest.mark.asyncio
async def test_record_usage_and_calculate_status() -> None:
    """Record consumption and verify real-time status calculations."""
    service = CostControlService()
    user = UserModel(
        id=uuid4(),
        email="test@scholar.org",
        full_name="Scholar",
        hashed_password="pw",
        role="researcher",
        token_quota=100000,
        tokens_used=50000,
        storage_quota_bytes=1000000,
        storage_used_bytes=500000,
    )
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    record = await service.record_usage(
        db=mock_db,
        user=user,
        activity_type="chat_completion",
        tokens_prompt=2000,
        tokens_completion=500,
        model_name="gpt-5.6-luna",
        cost_cents=0.05,
        bytes_transferred=1024,
    )

    assert record.total_tokens == 2500
    assert user.tokens_used == 52500
    assert user.storage_used_bytes == 501024
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()

    status_data = service.get_quota_status(user)
    assert status_data.tokens_remaining == 47500
    assert status_data.percent_tokens_used == 52.5
    assert status_data.is_quota_exceeded is False

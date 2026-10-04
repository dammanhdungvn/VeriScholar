"""Service for Token Quota Management and Cost Control (BỔ SUNG 1)."""

from typing import Any
from uuid import UUID

from api.db.models.usage_record import UsageRecordModel
from api.db.models.user import UserModel
from api.schemas.auth import TokenQuotaStatusResponse
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class CostControlService:
    """Manages token rate limiting, token quotas, and API cost accounting."""

    async def check_token_quota(
        self,
        db: AsyncSession,
        user: UserModel,
        estimated_tokens: int = 1000,
    ) -> None:
        """Verify user has sufficient token quota balance before launching costly LLM operations."""
        del db  # Reserved for database-level locks if needed
        if user.tokens_used + estimated_tokens > user.token_quota:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "QUOTA_EXCEEDED",
                    "message": (
                        f"Hạn mức token của bạn đã đạt giới hạn ({user.tokens_used:,} / "
                        f"{user.token_quota:,} tokens). "
                        "Vui lòng nâng cấp hạn mức để tiếp tục sử dụng."
                    ),
                    "field": "token_quota",
                    "action": "Liên hệ quản trị viên hoặc nâng cấp hạn mức tài khoản.",
                },
            )

    async def record_usage(
        self,
        db: AsyncSession,
        user: UserModel,
        activity_type: str,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        model_name: str = "default",
        cost_cents: float = 0.0,
        bytes_transferred: int = 0,
        organization_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecordModel:
        """Record token consumption and update user's cumulative usage counters."""
        total_tokens = tokens_prompt + tokens_completion
        user.tokens_used += total_tokens
        if bytes_transferred > 0:
            user.storage_used_bytes += bytes_transferred

        record = UsageRecordModel(
            user_id=user.id,
            organization_id=organization_id,
            activity_type=activity_type,
            model_name=model_name,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            total_tokens=total_tokens,
            cost_cents=cost_cents,
            bytes_transferred=bytes_transferred,
            metadata_json=metadata or {},
        )
        db.add(record)
        await db.commit()
        return record

    def get_quota_status(self, user: UserModel) -> TokenQuotaStatusResponse:
        """Calculate and return real-time token and storage balance metrics."""
        remaining_tokens = max(0, user.token_quota - user.tokens_used)
        pct_tokens = (
            round((user.tokens_used / user.token_quota) * 100.0, 2)
            if user.token_quota > 0
            else 100.0
        )
        remaining_storage = max(0, user.storage_quota_bytes - user.storage_used_bytes)
        pct_storage = (
            round((user.storage_used_bytes / user.storage_quota_bytes) * 100.0, 2)
            if user.storage_quota_bytes > 0
            else 100.0
        )

        return TokenQuotaStatusResponse(
            token_quota=user.token_quota,
            tokens_used=user.tokens_used,
            tokens_remaining=remaining_tokens,
            percent_tokens_used=min(100.0, pct_tokens),
            storage_quota_bytes=user.storage_quota_bytes,
            storage_used_bytes=user.storage_used_bytes,
            storage_remaining_bytes=remaining_storage,
            percent_storage_used=min(100.0, pct_storage),
            is_quota_exceeded=(user.tokens_used >= user.token_quota),
        )

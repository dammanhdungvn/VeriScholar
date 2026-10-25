"""Database model for user-provided BYOK and integration API keys."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class UserApiKeyModel(IdentifiableTimestampedModel):
    """Encrypted personal API key storage with per-provider constraints."""

    __tablename__ = "user_api_keys"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    encrypted_key: Mapped[str] = mapped_column(String(500), nullable=False)
    key_hint: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_api_keys_user_provider"),
        CheckConstraint(
            "provider IN ('openai', 'anthropic', 'google', 'exa')",
            name="ck_user_api_keys_provider",
        ),
    )

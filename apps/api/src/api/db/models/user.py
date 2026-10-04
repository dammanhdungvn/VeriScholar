"""User database model."""

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(IdentifiableTimestampedModel):
    """Represents an application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="researcher", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    token_quota: Mapped[int] = mapped_column(nullable=False, default=200000)
    tokens_used: Mapped[int] = mapped_column(nullable=False, default=0)
    storage_quota_bytes: Mapped[int] = mapped_column(nullable=False, default=1073741824)  # 1 GB
    storage_used_bytes: Mapped[int] = mapped_column(nullable=False, default=0)

"""User database model."""

from api.db.models.base import IdentifiableTimestampedModel
from sqlalchemy import Boolean, CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(IdentifiableTimestampedModel):
    """Represents an application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="researcher", nullable=False)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    academic_rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    orcid_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    research_interests: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_scholar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    theme_preference: Mapped[str] = mapped_column(String(20), default="system", nullable=False)
    byok_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("theme_preference IN ('light', 'dark', 'system')", name="ck_users_theme"),
    )

    @property
    def has_byok(self) -> bool:
        """Return True if the user has an encrypted BYOK key stored."""
        return bool(self.byok_api_key_encrypted)

    @property
    def byok_masked(self) -> str | None:
        """Decrypt BYOK key in memory and return only its masked form."""
        if not self.byok_api_key_encrypted:
            return None
        from api.core.config import settings
        from api.core.crypto import CryptoError, decrypt_byok_key
        from core.services.email_validator import mask_api_key

        try:
            raw_key = decrypt_byok_key(self.byok_api_key_encrypted, settings.BYOK_ENCRYPTION_KEY)
            return mask_api_key(raw_key)
        except CryptoError:
            return None

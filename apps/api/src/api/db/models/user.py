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

"""Database model for Scholar Academic Profile (1-1 with UserModel)."""

from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ScholarProfileModel(IdentifiableTimestampedModel):
    """Represents extended scholarly profile metadata for researchers."""

    __tablename__ = "scholar_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    academic_rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    orcid_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    google_scholar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_interests: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)

"""Organization and Lab collaboration database models."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from api.db.models.base import Base, IdentifiableTimestampedModel
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class OrganizationModel(IdentifiableTimestampedModel):
    """Represents a collaborative research lab or organization."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_quota_bytes: Mapped[int] = mapped_column(
        BigInteger, default=10737418240, nullable=False
    )  # 10 GB default
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    token_quota: Mapped[int] = mapped_column(
        Integer, default=1000000, nullable=False
    )  # 1,000,000 tokens
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class OrganizationMemberModel(Base):
    """Represents membership and role within a research lab/organization."""

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_members_org_user"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(50), default="member", nullable=False
    )  # 'owner', 'admin', 'member', 'guest'
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

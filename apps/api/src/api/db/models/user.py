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

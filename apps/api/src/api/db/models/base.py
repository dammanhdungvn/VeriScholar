"""SQLAlchemy Declarative Base for VeriScholar API."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Abstract declarative base for all database models."""

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        mapper = getattr(self, "__mapper__", None)
        if mapper is not None:
            for col in mapper.columns:
                if (
                    col.key not in kwargs
                    and getattr(self, col.key, None) is None
                    and col.default is not None
                ):
                    arg = col.default.arg
                    if callable(arg):
                        try:
                            setattr(self, col.key, arg())
                        except TypeError:
                            pass
                    else:
                        setattr(self, col.key, arg)


class IdentifiableTimestampedModel(Base):
    """Abstract model mixin providing standard UUID primary key and timestamps."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

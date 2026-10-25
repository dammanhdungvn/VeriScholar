"""Domain entity representing an academic scholar user."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.domain.value_objects.enums import AcademicRank, ThemePreference


class UserEntity(BaseModel):
    """Pure domain entity representing a VeriScholar user."""

    id: UUID
    email: str
    full_name: str
    theme_preference: ThemePreference = ThemePreference.SYSTEM
    academic_rank: AcademicRank | str | None = None
    orcid_id: str | None = None
    institution: str | None = None
    department: str | None = None
    is_active: bool = True
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)

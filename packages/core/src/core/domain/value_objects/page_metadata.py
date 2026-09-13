"""PageMetadata and PageDimensions Value Objects.

Encapsulates page geometric dimensions, rotation, and viewport rendering contracts
for PDF.js Canvas synchronization.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.exceptions import InvalidPageMetadataError

ALLOWED_ROTATION_DEGREES = {0, 90, 180, 270}


class PageDimensions(BaseModel):
    """Immutable page dimensions in typographical points (72 points = 1 inch)."""

    model_config = ConfigDict(frozen=True)

    width_pt: float = Field(gt=0.0, description="Page width in typographical points")
    height_pt: float = Field(gt=0.0, description="Page height in typographical points")

    @property
    def aspect_ratio(self) -> float:
        """Ratio of width to height."""
        return self.width_pt / self.height_pt


class PageMetadata(BaseModel):
    """Geometric and orientation metadata for a single PDF page."""

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(ge=1, description="1-indexed document page number")
    width_pt: float = Field(gt=0.0, description="Page width in points")
    height_pt: float = Field(gt=0.0, description="Page height in points")
    rotation_deg: int = Field(default=0, description="Page orientation rotation in degrees")

    @field_validator("rotation_deg")
    @classmethod
    def validate_rotation(cls, v: int) -> int:
        """Enforce standard orthogonal PDF rotation degrees (0, 90, 180, 270)."""
        normalized = v % 360
        if normalized not in ALLOWED_ROTATION_DEGREES:
            allowed = sorted(ALLOWED_ROTATION_DEGREES)
            raise InvalidPageMetadataError(
                f"Invalid page rotation {v} degrees. Must be one of {allowed}"
            )
        return normalized

    @property
    def dimensions(self) -> PageDimensions:
        """Extract dimension pair value object."""
        return PageDimensions(width_pt=self.width_pt, height_pt=self.height_pt)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to database JSONB format."""
        return {
            "page_number": self.page_number,
            "dimensions": [round(self.width_pt, 2), round(self.height_pt, 2)],
            "rotation_deg": self.rotation_deg,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PageMetadata":
        """Deserialize from database JSONB dictionary."""
        try:
            page_num = data["page_number"]
            dims = data["dimensions"]
            rot = data.get("rotation_deg", 0)
            return cls(
                page_number=page_num,
                width_pt=float(dims[0]),
                height_pt=float(dims[1]),
                rotation_deg=int(rot),
            )
        except (KeyError, IndexError, TypeError, ValueError) as err:
            raise InvalidPageMetadataError(f"Malformed page metadata dictionary: {err}") from err

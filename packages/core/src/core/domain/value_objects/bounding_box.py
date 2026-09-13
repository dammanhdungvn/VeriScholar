"""BoundingBox Value Object.

Represents a normalized bounding rectangle on a PDF document page:
[x0, y0, x1, y1, page] where x0, y0, x1, y1 in [0.0, 1.0] and page >= 1.
Origin (0.0, 0.0) is the Top-Left of the page.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.domain.exceptions import InvalidBoundingBoxError


class BoundingBox(BaseModel):
    """Immutable normalized bounding box value object on a specific document page."""

    model_config = ConfigDict(frozen=True)

    x0: float = Field(ge=0.0, le=1.0, description="Normalized left coordinate (0.0 to 1.0)")
    y0: float = Field(ge=0.0, le=1.0, description="Normalized top coordinate (0.0 to 1.0)")
    x1: float = Field(ge=0.0, le=1.0, description="Normalized right coordinate (0.0 to 1.0)")
    y1: float = Field(ge=0.0, le=1.0, description="Normalized bottom coordinate (0.0 to 1.0)")
    page: int = Field(ge=1, description="1-indexed document page number")

    @model_validator(mode="after")
    def validate_spatial_ordering(self) -> "BoundingBox":
        """Enforce strict geometric coordinate invariant: x0 < x1 and y0 < y1."""
        if self.x0 >= self.x1:
            raise InvalidBoundingBoxError(
                f"Invalid x coordinates: x0 ({self.x0}) must be strictly less than x1 ({self.x1})"
            )
        if self.y0 >= self.y1:
            raise InvalidBoundingBoxError(
                f"Invalid y coordinates: y0 ({self.y0}) must be strictly less than y1 ({self.y1})"
            )
        return self

    @property
    def width(self) -> float:
        """Normalized width of the bounding box."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Normalized height of the bounding box."""
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        """Normalized geometric area."""
        return self.width * self.height

    def to_list(self) -> list[Any]:
        """Convert to standard 5-element array [x0, y0, x1, y1, page]."""
        return [
            round(self.x0, 6),
            round(self.y0, 6),
            round(self.x1, 6),
            round(self.y1, 6),
            self.page,
        ]

    @classmethod
    def from_list(cls, values: list[Any] | tuple[Any, ...]) -> "BoundingBox":
        """Instantiate BoundingBox from raw [x0, y0, x1, y1, page] array."""
        if len(values) != 5:
            raise InvalidBoundingBoxError(
                f"Array must contain exactly 5 elements [x0, y0, x1, y1, page], got {len(values)}"
            )
        try:
            return cls(
                x0=float(values[0]),
                y0=float(values[1]),
                x1=float(values[2]),
                y1=float(values[3]),
                page=int(values[4]),
            )
        except (ValueError, TypeError) as err:
            raise InvalidBoundingBoxError(f"Invalid bounding box element types: {err}") from err

    def intersects(self, other: "BoundingBox") -> bool:
        """Determine if this box intersects with another box on the same page."""
        if self.page != other.page:
            return False
        return not (
            self.x1 <= other.x0 or self.x0 >= other.x1 or self.y1 <= other.y0 or self.y0 >= other.y1
        )

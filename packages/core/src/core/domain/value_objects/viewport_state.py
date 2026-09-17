"""ViewportState Value Object.

Represents the active viewport scroll, page, and zoom coordinates within
the multi-tab PDF.js canvas viewer.
"""

from pydantic import BaseModel, ConfigDict, Field


class ViewportState(BaseModel):
    """Immutable viewport state representation for canvas and reading position."""

    model_config = ConfigDict(frozen=True)

    page: int = Field(default=1, ge=1, description="1-indexed active PDF page")
    zoom_ratio: float = Field(default=1.0, gt=0.0, le=5.0, description="Visual zoom scale factor")
    scroll_top: float = Field(
        default=0.0, ge=0.0, description="Vertical scroll offset position in pixels"
    )

    def to_dict(self) -> dict[str, float | int]:
        """Convert to dictionary representation for database persistence."""
        return {
            "page": self.page,
            "zoom_ratio": self.zoom_ratio,
            "scroll_top": self.scroll_top,
        }

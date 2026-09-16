"""PDF Annotation Value Objects.

Defines domain value objects for ISO 32000-1 / ISO 32000-2 text markup annotations.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from core.domain.value_objects.bounding_box import BoundingBox


class AnnotationCategory(str, Enum):
    """Category of scholarly visual grounding annotation."""

    PROBLEM_STATEMENT = "problem_statement"
    CONTRIBUTION = "contribution"
    LIMITATION = "limitation"
    USER_NOTE = "user_note"


class PdfAnnotation(BaseModel):
    """Immutable domain value object representing a native PDF highlight annotation."""

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(ge=1, description="1-indexed target page number")
    bounding_box: BoundingBox = Field(description="Normalized bounding box of highlight")
    title: str = Field(description="Annotation title / author metadata (e.g. VeriScholar AI)")
    content: str = Field(description="Rich explanation or comment content for popup note")
    category: AnnotationCategory = Field(description="Scholarly finding category")
    color_rgb: tuple[float, float, float] = Field(
        default=(0.15, 0.75, 0.45),
        description="RGB stroke color normalized between 0.0 and 1.0",
    )
    opacity: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Highlight opacity so underlying text remains crisp",
    )

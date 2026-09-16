"""Document Structure domain entity representing TOC, Headings, and Sections."""

from uuid import UUID

from pydantic import BaseModel, Field

from core.domain.value_objects.bounding_box import BoundingBox


class DocumentSection(BaseModel):
    """Section or heading entry in the document's structure."""

    title: str = Field(min_length=1, description="Heading or section title text")
    page_number: int = Field(ge=1, description="1-indexed page number where heading is located")
    bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Normalized bounding boxes covering the heading title on the page",
    )


class DocumentStructure(BaseModel):
    """Structured table of contents, abstract, and sections of an academic paper."""

    document_id: UUID | None = Field(default=None, description="Associated document UUID")
    title: str | None = Field(default=None, description="Extracted paper title")
    abstract: str | None = Field(default=None, description="Extracted paper abstract text")
    abstract_bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Normalized bounding boxes covering the abstract text block",
    )
    sections: list[DocumentSection] = Field(
        default_factory=list,
        description="Hierarchical or sequential list of document sections/headings",
    )

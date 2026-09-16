"""Unit tests for PdfAnnotation value object and AnnotationCategory enum."""

import pytest
from core.domain.exceptions import InvalidBoundingBoxError
from core.domain.value_objects.bounding_box import BoundingBox
from core.domain.value_objects.pdf_annotation import AnnotationCategory, PdfAnnotation


def test_pdf_annotation_valid_instantiation() -> None:
    box = BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.3, page=1)
    annot = PdfAnnotation(
        page_number=1,
        bounding_box=box,
        title="VeriScholar AI [Contributions]",
        content="Grounding synthesis text",
        category=AnnotationCategory.CONTRIBUTION,
        color_rgb=(0.15, 0.75, 0.45),
        opacity=0.4,
    )
    assert annot.page_number == 1
    assert annot.bounding_box == box
    assert annot.category == AnnotationCategory.CONTRIBUTION
    assert annot.color_rgb == (0.15, 0.75, 0.45)
    assert annot.opacity == 0.4


def test_pdf_annotation_is_immutable() -> None:
    box = BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.3, page=1)
    annot = PdfAnnotation(
        page_number=1,
        bounding_box=box,
        title="VeriScholar AI",
        content="Content",
        category=AnnotationCategory.PROBLEM_STATEMENT,
    )
    with pytest.raises(Exception):
        annot.title = "Modified Title"  # type: ignore[misc]


def test_pdf_annotation_rejects_invalid_page() -> None:
    box = BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.3, page=1)
    with pytest.raises(Exception):
        PdfAnnotation(
            page_number=0,  # Invalid: page >= 1
            bounding_box=box,
            title="VeriScholar AI",
            content="Content",
            category=AnnotationCategory.LIMITATION,
        )


def test_pdf_annotation_rejects_invalid_bounding_box() -> None:
    with pytest.raises(InvalidBoundingBoxError):
        BoundingBox(x0=0.8, y0=0.2, x1=0.1, y1=0.3, page=1)

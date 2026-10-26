import pytest
from core.domain.exceptions import DomainValidationError
from core.services.pdf_validator import (
    MAX_PDF_FILE_SIZE_BYTES,
    MAX_PDF_PAGE_COUNT,
    normalize_bbox_coordinates,
    validate_pdf_metadata_invariants,
)


def test_pdf_validator_enforces_size_and_page_limits():
    # File too large
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(MAX_PDF_FILE_SIZE_BYTES + 1, 10, 100, False)
    assert exc.value.code == "PDF_FILE_TOO_LARGE"

    # Pages exceeded
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, MAX_PDF_PAGE_COUNT + 1, 100, False)
    assert exc.value.code == "PDF_PAGE_LIMIT_EXCEEDED"


def test_pdf_validator_detects_scanned_pdf_without_text():
    # Only 10 chars on page 1 -> scanned image
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, 10, 10, False)
    assert exc.value.code == "PDF_NO_TEXT_LAYER"


def test_pdf_validator_detects_password_protection():
    with pytest.raises(DomainValidationError) as exc:
        validate_pdf_metadata_invariants(1000, 10, 100, True)
    assert exc.value.code == "PDF_PASSWORD_PROTECTED"


def test_normalize_bbox_coordinates_scales_to_thousand():
    # Raw box in center of 600x800 page
    norm = normalize_bbox_coordinates(150.0, 200.0, 450.0, 600.0, 600.0, 800.0)
    assert norm == (250, 250, 750, 750)

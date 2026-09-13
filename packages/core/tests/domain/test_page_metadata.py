"""Unit tests for PageMetadata and PageDimensions value objects."""

import pytest
from core.domain.exceptions import InvalidPageMetadataError
from core.domain.value_objects.page_metadata import PageMetadata


def test_page_metadata_valid_instantiation() -> None:
    page = PageMetadata(page_number=1, width_pt=595.28, height_pt=841.89, rotation_deg=0)
    assert page.page_number == 1
    assert page.width_pt == 595.28
    assert page.height_pt == 841.89
    assert page.rotation_deg == 0
    assert round(page.dimensions.aspect_ratio, 2) == 0.71


@pytest.mark.parametrize("valid_rot", [0, 90, 180, 270, 360])
def test_page_metadata_valid_rotations(valid_rot: int) -> None:
    page = PageMetadata(page_number=1, width_pt=612.0, height_pt=792.0, rotation_deg=valid_rot)
    assert page.rotation_deg in {0, 90, 180, 270}


def test_page_metadata_rejects_invalid_rotation() -> None:
    with pytest.raises(InvalidPageMetadataError, match="Invalid page rotation"):
        PageMetadata(page_number=1, width_pt=612.0, height_pt=792.0, rotation_deg=45)


def test_page_metadata_serialization_roundtrip() -> None:
    original = PageMetadata(page_number=3, width_pt=612.456, height_pt=792.789, rotation_deg=90)
    data_dict = original.to_dict()
    assert data_dict == {
        "page_number": 3,
        "dimensions": [612.46, 792.79],
        "rotation_deg": 90,
    }

    restored = PageMetadata.from_dict(data_dict)
    assert restored.page_number == original.page_number
    assert round(restored.width_pt, 2) == round(original.width_pt, 2)
    assert round(restored.height_pt, 2) == round(original.height_pt, 2)
    assert restored.rotation_deg == original.rotation_deg


def test_page_metadata_from_dict_malformed() -> None:
    with pytest.raises(InvalidPageMetadataError):
        PageMetadata.from_dict({"page_number": 1, "dimensions": [612.0]})

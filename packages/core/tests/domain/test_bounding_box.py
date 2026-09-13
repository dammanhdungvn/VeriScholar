"""Unit tests for BoundingBox value object."""

import pytest
from core.domain.exceptions import InvalidBoundingBoxError
from core.domain.value_objects.bounding_box import BoundingBox


def test_bounding_box_valid_instantiation() -> None:
    box = BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.9, page=1)
    assert box.x0 == 0.1
    assert box.y0 == 0.2
    assert box.x1 == 0.8
    assert box.y1 == 0.9
    assert box.page == 1
    assert round(box.width, 2) == 0.7
    assert round(box.height, 2) == 0.7
    assert round(box.area, 4) == 0.49


def test_bounding_box_rejects_inverted_x() -> None:
    with pytest.raises(InvalidBoundingBoxError, match="Invalid x coordinates"):
        BoundingBox(x0=0.8, y0=0.2, x1=0.1, y1=0.9, page=1)


def test_bounding_box_rejects_equal_x() -> None:
    with pytest.raises(InvalidBoundingBoxError, match="Invalid x coordinates"):
        BoundingBox(x0=0.5, y0=0.2, x1=0.5, y1=0.9, page=1)


def test_bounding_box_rejects_inverted_y() -> None:
    with pytest.raises(InvalidBoundingBoxError, match="Invalid y coordinates"):
        BoundingBox(x0=0.1, y0=0.9, x1=0.8, y1=0.2, page=1)


def test_bounding_box_rejects_out_of_bounds() -> None:
    with pytest.raises(Exception):  # Pydantic validation error for ge/le
        BoundingBox(x0=-0.1, y0=0.2, x1=0.8, y1=0.9, page=1)

    with pytest.raises(Exception):
        BoundingBox(x0=0.1, y0=0.2, x1=1.5, y1=0.9, page=1)


def test_bounding_box_rejects_invalid_page() -> None:
    with pytest.raises(Exception):
        BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.9, page=0)


def test_bounding_box_serialization_roundtrip() -> None:
    original = BoundingBox(x0=0.123456, y0=0.234567, x1=0.890123, y1=0.901234, page=5)
    raw_list = original.to_list()
    assert raw_list == [0.123456, 0.234567, 0.890123, 0.901234, 5]

    restored = BoundingBox.from_list(raw_list)
    assert restored == original


def test_bounding_box_from_list_invalid_length() -> None:
    with pytest.raises(InvalidBoundingBoxError, match="must contain exactly 5 elements"):
        BoundingBox.from_list([0.1, 0.2, 0.8, 0.9])


def test_bounding_box_from_list_invalid_types() -> None:
    with pytest.raises(InvalidBoundingBoxError, match="Invalid bounding box element types"):
        BoundingBox.from_list(["invalid_float", 0.2, 0.8, 0.9, 1])


def test_bounding_box_intersects() -> None:
    box1 = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=1)
    box2 = BoundingBox(x0=0.3, y0=0.3, x1=0.7, y1=0.7, page=1)
    box3 = BoundingBox(x0=0.6, y0=0.6, x1=0.9, y1=0.9, page=1)
    box4_diff_page = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=2)

    assert box1.intersects(box2) is True
    assert box2.intersects(box1) is True
    assert box1.intersects(box3) is False
    assert box1.intersects(box4_diff_page) is False

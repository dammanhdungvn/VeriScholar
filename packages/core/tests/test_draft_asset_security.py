"""Unit tests for DraftAssetSecurityValidator supporting PNG, JPEG, JPG, and WebP assets."""

import pytest
from core.domain.exceptions import MaliciousAssetContentError
from core.services.draft_asset_security import DraftAssetSecurityValidator


def test_validator_accepts_valid_png():
    validator = DraftAssetSecurityValidator()
    valid_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    ext = validator.validate_single_asset("figure.png", valid_png)
    assert ext == ".png"


def test_validator_accepts_valid_jpeg_and_jpg():
    validator = DraftAssetSecurityValidator()
    valid_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 20

    ext_jpeg = validator.validate_single_asset("img-0.jpeg", valid_jpeg)
    assert ext_jpeg == ".jpeg"

    ext_jpg = validator.validate_single_asset("img-1.jpg", valid_jpeg)
    assert ext_jpg == ".jpg"


def test_validator_accepts_valid_webp():
    validator = DraftAssetSecurityValidator()
    valid_webp = b"RIFF" + b"\x00\x00\x00\x10" + b"WEBP" + b"\x00" * 10
    ext = validator.validate_single_asset("chart.webp", valid_webp)
    assert ext == ".webp"


def test_validator_rejects_corrupted_jpeg():
    validator = DraftAssetSecurityValidator()
    invalid_jpeg = b"NOT_A_JPEG_HEADER"
    with pytest.raises(MaliciousAssetContentError, match="valid JPEG image header"):
        validator.validate_single_asset("fake.jpeg", invalid_jpeg)


def test_validator_rejects_unsupported_extensions():
    validator = DraftAssetSecurityValidator()
    with pytest.raises(MaliciousAssetContentError, match="not permitted"):
        validator.validate_single_asset("malicious.sh", b"#!/bin/bash\n")

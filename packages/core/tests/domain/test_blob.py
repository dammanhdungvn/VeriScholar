"""Unit tests for DocumentStorageBlob domain entity."""

import pytest
from core.domain.entities.blob import DocumentStorageBlob
from core.domain.exceptions import (
    FileSizeLimitExceededError,
    InvalidContentHashError,
    InvariantViolationError,
)
from core.domain.value_objects.enums import BlobStatus

VALID_HASH = "a" * 64


def test_blob_valid_instantiation() -> None:
    blob = DocumentStorageBlob(
        content_hash=VALID_HASH,
        storage_path="storage/blobs/aa/aaaa.pdf",
        file_size_bytes=1024 * 1024,
    )
    assert blob.content_hash == VALID_HASH
    assert blob.file_size_bytes == 1048576
    assert blob.ref_count == 1
    assert blob.status == BlobStatus.PROCESSING
    assert blob.is_orphan is False


def test_blob_rejects_invalid_hash_format() -> None:
    with pytest.raises(InvalidContentHashError, match="Must be a 64-char lowercase SHA-256"):
        DocumentStorageBlob(
            content_hash="invalid_hash_too_short",
            storage_path="storage/blobs/test.pdf",
            file_size_bytes=1000,
        )

    with pytest.raises(InvalidContentHashError, match="Must be a 64-char lowercase SHA-256"):
        DocumentStorageBlob(
            content_hash="z" * 64,  # 'z' is not a valid hex character
            storage_path="storage/blobs/test.pdf",
            file_size_bytes=1000,
        )


def test_blob_rejects_exceeding_max_file_size() -> None:
    exceeding_size = 52_428_801  # 50MB + 1 byte
    with pytest.raises(FileSizeLimitExceededError, match="exceeds maximum limit of"):
        DocumentStorageBlob(
            content_hash=VALID_HASH,
            storage_path="storage/blobs/test.pdf",
            file_size_bytes=exceeding_size,
        )


def test_blob_reference_counting_lifecycle() -> None:
    blob = DocumentStorageBlob(
        content_hash=VALID_HASH,
        storage_path="storage/blobs/test.pdf",
        file_size_bytes=5000,
        ref_count=1,
    )

    blob.increment_reference()
    assert blob.ref_count == 2
    assert blob.is_orphan is False

    blob.decrement_reference()
    assert blob.ref_count == 1
    assert blob.is_orphan is False

    blob.decrement_reference()
    assert blob.ref_count == 0
    assert blob.is_orphan is True

    # Attempting to decrement below 0 must raise InvariantViolationError
    with pytest.raises(InvariantViolationError, match="Cannot decrement ref_count below 0"):
        blob.decrement_reference()


def test_blob_status_transitions() -> None:
    blob = DocumentStorageBlob(
        content_hash=VALID_HASH,
        storage_path="storage/blobs/test.pdf",
        file_size_bytes=5000,
    )

    blob.mark_completed()
    assert blob.status == BlobStatus.COMPLETED

    blob.mark_failed()
    assert blob.status == BlobStatus.FAILED

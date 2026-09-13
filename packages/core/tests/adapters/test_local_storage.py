"""Unit tests for LocalStorageAdapter."""

import hashlib
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from core.adapters.storage.local import LocalStorageAdapter
from core.domain.exceptions import InvariantViolationError


async def _make_stream(data: bytes, chunk_size: int = 1024) -> AsyncIterator[bytes]:
    """Helper to convert bytes into an async iterator."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


@pytest.mark.asyncio
async def test_local_storage_save_and_exists(tmp_path: Path) -> None:
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")
    content = b"%PDF-1.4 test document content"
    expected_hash = hashlib.sha256(content).hexdigest()

    assert await storage.blob_exists(expected_hash) is False

    rel_path, byte_size = await storage.save_blob(
        stream=_make_stream(content),
        content_hash=expected_hash,
    )

    assert byte_size == len(content)
    assert expected_hash in rel_path
    assert await storage.blob_exists(expected_hash) is True

    # Check file physically exists
    abs_path = Path(storage.get_blob_path(expected_hash))
    assert abs_path.is_file()
    assert abs_path.read_bytes() == content


@pytest.mark.asyncio
async def test_local_storage_deduplication(tmp_path: Path) -> None:
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")
    content = b"%PDF-1.4 repeated upload"
    expected_hash = hashlib.sha256(content).hexdigest()

    # First save
    rel_path_1, size_1 = await storage.save_blob(_make_stream(content), expected_hash)
    # Second save should reuse existing blob
    rel_path_2, size_2 = await storage.save_blob(_make_stream(content), expected_hash)

    assert rel_path_1 == rel_path_2
    assert size_1 == size_2 == len(content)


@pytest.mark.asyncio
async def test_local_storage_rejects_mismatched_hash(tmp_path: Path) -> None:
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")
    content = b"%PDF-1.4 valid content"
    bad_hash = "f" * 64

    with pytest.raises(InvariantViolationError, match="Integrity check failed"):
        await storage.save_blob(_make_stream(content), bad_hash)

    assert await storage.blob_exists(bad_hash) is False


@pytest.mark.asyncio
async def test_local_storage_delete_blob(tmp_path: Path) -> None:
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")
    content = b"%PDF-1.4 content to delete"
    expected_hash = hashlib.sha256(content).hexdigest()

    await storage.save_blob(_make_stream(content), expected_hash)
    assert await storage.blob_exists(expected_hash) is True

    deleted = await storage.delete_blob(expected_hash)
    assert deleted is True
    assert await storage.blob_exists(expected_hash) is False

    # Deleting already deleted blob returns False
    assert await storage.delete_blob(expected_hash) is False


@pytest.mark.asyncio
async def test_local_storage_stream_blob_range(tmp_path: Path) -> None:
    storage = LocalStorageAdapter(base_directory=tmp_path / "blobs")
    content = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    expected_hash = hashlib.sha256(content).hexdigest()

    await storage.save_blob(_make_stream(content), expected_hash)

    # 1. Full stream without end_byte
    full_chunks = []
    async for chunk in storage.stream_blob_range(expected_hash, start_byte=0, chunk_size=10):
        full_chunks.append(chunk)
    assert b"".join(full_chunks) == content

    # 2. Slice stream with start_byte and end_byte
    slice_chunks = []
    async for chunk in storage.stream_blob_range(
        expected_hash, start_byte=10, end_byte=19, chunk_size=4
    ):
        slice_chunks.append(chunk)
    assert b"".join(slice_chunks) == content[10:20]

    # 3. Stream with invalid range returns empty
    empty_chunks = []
    async for chunk in storage.stream_blob_range(expected_hash, start_byte=100, end_byte=120):
        empty_chunks.append(chunk)
    assert b"".join(empty_chunks) == b""

    # 4. Stream non-existent blob raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        async for _ in storage.stream_blob_range("0" * 64):
            pass

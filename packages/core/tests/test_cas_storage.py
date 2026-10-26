"""Unit tests for Content-Addressable Storage (CAS) local filesystem adapter."""

import hashlib
from pathlib import Path

import pytest
from core.adapters.storage.local import LocalStorageAdapter


@pytest.mark.asyncio
async def test_cas_path_distribution_two_level(tmp_path: Path):
    adapter = LocalStorageAdapter(base_dir=tmp_path)
    sample_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    expected_rel = f"{sample_hash[:2]}/{sample_hash[2:4]}/{sample_hash}"
    assert adapter.get_blob_path(sample_hash) == expected_rel


@pytest.mark.asyncio
async def test_cas_stream_range_reading(tmp_path: Path):
    adapter = LocalStorageAdapter(base_dir=tmp_path)
    content = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    content_hash = hashlib.sha256(content).hexdigest()

    async def async_chunks():
        yield content

    path, size = await adapter.save_blob(async_chunks(), content_hash)
    assert size == len(content)
    assert await adapter.blob_exists(content_hash) is True

    # Read range 10-19 inclusive (10 bytes: 'A' through 'J')
    range_data = b""
    async for chunk in adapter.stream_blob_range(content_hash, start_byte=10, end_byte=19):
        range_data += chunk
    assert range_data == b"ABCDEFGHIJ"

    # Delete and clean empty parent folders
    deleted = await adapter.delete_blob(content_hash)
    assert deleted is True
    assert await adapter.blob_exists(content_hash) is False

    # Check parent dirs are cleaned up
    prefix_dir = tmp_path / content_hash[:2]
    assert not prefix_dir.exists()


@pytest.mark.asyncio
async def test_cas_delete_nonexistent_blob(tmp_path: Path):
    adapter = LocalStorageAdapter(base_dir=tmp_path)
    assert await adapter.delete_blob("nonexistenthash123456") is False

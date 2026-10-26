"""Local filesystem Content-Addressable Storage (CAS) adapter.

Organizes blobs in a 2-tier fan-out directory structure:
storage/blobs/ab/cd/abcdef123456...
Guarantees atomic file writes via temporary files and rename operations.
"""

import asyncio
import hashlib
import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path

from core.domain.exceptions import InvariantViolationError
from core.ports.storage import IBlobStoragePort

logger = logging.getLogger(__name__)

DEFAULT_STORAGE_CHUNK_SIZE_BYTES: int = 64 * 1024  # 64 KB buffer chunk


class LocalStorageAdapter(IBlobStoragePort):
    """Filesystem-backed Content-Addressable Storage adapter."""

    def __init__(
        self,
        base_directory: Path | str = "storage/blobs",
        base_dir: Path | str | None = None,
    ) -> None:
        effective_base = base_dir if base_dir is not None else base_directory
        self.base_dir = Path(effective_base).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, content_hash: str) -> Path:
        """Derive 2-tier partitioned filesystem path from content hash."""
        clean_hash = content_hash.lower().strip()
        prefix1 = clean_hash[:2]
        prefix2 = clean_hash[2:4]
        # Check if legacy .pdf file exists on disk, otherwise use raw hash
        pdf_path = self.base_dir / prefix1 / prefix2 / f"{clean_hash}.pdf"
        if pdf_path.is_file():
            return pdf_path
        return self.base_dir / prefix1 / prefix2 / clean_hash

    def get_blob_path(self, content_hash: str) -> str:
        """Return canonical 2-tier partitioned storage relative path for given content hash."""
        clean_hash = content_hash.lower().strip()
        return f"{clean_hash[:2]}/{clean_hash[2:4]}/{clean_hash}"

    async def blob_exists(self, content_hash: str) -> bool:
        """Check whether physical blob file exists on disk."""
        target_path = self._resolve_path(content_hash)
        return await asyncio.to_thread(target_path.is_file)

    async def save_blob(
        self,
        stream: AsyncIterator[bytes],
        content_hash: str,
    ) -> tuple[str, int]:
        """Stream bytes from upload to disk atomically, verifying hash integrity.

        Args:
            stream: Asynchronous byte iterator.
            content_hash: Expected SHA-256 hash.

        Returns:
            Tuple of (relative_storage_path, total_bytes).
        """
        clean_hash = content_hash.lower().strip()
        final_path = self._resolve_path(clean_hash)

        # Check if already present on disk (CAS deduplication)
        if await self.blob_exists(clean_hash):
            file_size = await asyncio.to_thread(final_path.stat)
            return self.get_blob_path(clean_hash), file_size.st_size

        # Prepare parent directories
        await asyncio.to_thread(final_path.parent.mkdir, parents=True, exist_ok=True)

        temp_path = final_path.with_suffix(".tmp")
        hasher = hashlib.sha256()
        total_bytes = 0

        # Atomic write loop
        try:
            with open(temp_path, "wb") as f:
                async for chunk in stream:
                    if not chunk:
                        continue
                    total_bytes += len(chunk)
                    hasher.update(chunk)
                    f.write(chunk)

            calculated_hash = hasher.hexdigest()
            if calculated_hash != clean_hash:
                raise InvariantViolationError(
                    f"Integrity check failed: hash '{calculated_hash}' != '{clean_hash}'"
                )

            # Atomic replace
            await asyncio.to_thread(os.replace, temp_path, final_path)
        except Exception:
            if temp_path.exists():
                await asyncio.to_thread(temp_path.unlink, missing_ok=True)
            raise

        return self.get_blob_path(clean_hash), total_bytes

    async def delete_blob(self, content_hash: str) -> bool:
        """Safely delete blob file when ref_count reaches 0 and clean empty parent folders."""
        target_path = self._resolve_path(content_hash)
        if not await asyncio.to_thread(target_path.is_file):
            return False

        await asyncio.to_thread(target_path.unlink, missing_ok=True)

        def _cleanup_empty_parents(path: Path) -> None:
            clean_hash = content_hash.lower().strip()
            try:
                p2 = path.parent
                if p2.exists() and p2 != self.base_dir and not any(p2.iterdir()):
                    p2.rmdir()
                p1 = self.base_dir / clean_hash[:2]
                if p1.exists() and p1 != self.base_dir and not any(p1.iterdir()):
                    p1.rmdir()
            except OSError as err:
                logger.debug("Storage cleanup: directory not empty or permission denied: %s", err)

        await asyncio.to_thread(_cleanup_empty_parents, target_path)
        return True

    async def read_blob(self, content_hash: str) -> bytes:
        """Read entire physical blob binary into memory."""
        target_path = self._resolve_path(content_hash)
        if not await asyncio.to_thread(target_path.is_file):
            raise FileNotFoundError(f"Blob file not found for hash: {content_hash}")
        return await asyncio.to_thread(target_path.read_bytes)

    async def stream_blob_range(
        self,
        content_hash: str,
        start_byte: int = 0,
        end_byte: int | None = None,
        chunk_size: int = DEFAULT_STORAGE_CHUNK_SIZE_BYTES,
    ) -> AsyncIterator[bytes]:
        """Stream binary slice from local disk without whole-file memory buffering.

        Supports HTTP 206 Partial Content range streaming for Web Canvas / PDF.js.
        """
        target_path = self._resolve_path(content_hash)
        if not await asyncio.to_thread(target_path.is_file):
            raise FileNotFoundError(f"Blob file not found for hash: {content_hash}")

        file_size = await asyncio.to_thread(os.path.getsize, target_path)
        actual_end = file_size - 1 if end_byte is None else min(end_byte, file_size - 1)

        if start_byte < 0 or start_byte > actual_end or start_byte >= file_size:
            return

        def _read_chunk(file_handle, bytes_to_read: int) -> bytes:
            return file_handle.read(bytes_to_read)

        def _open_and_seek(file_path: Path, offset: int):
            f = open(file_path, "rb")
            if offset > 0:
                f.seek(offset)
            return f

        f = await asyncio.to_thread(_open_and_seek, target_path, start_byte)
        try:
            bytes_remaining = (actual_end - start_byte) + 1
            while bytes_remaining > 0:
                read_size = min(chunk_size, bytes_remaining)
                chunk = await asyncio.to_thread(_read_chunk, f, read_size)
                if not chunk:
                    break
                bytes_remaining -= len(chunk)
                yield chunk
        finally:
            await asyncio.to_thread(f.close)

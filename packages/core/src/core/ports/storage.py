"""Storage Port Protocol for Content-Addressable Storage (CAS).

Defines the contract for binary blob persistence, retrieval, and life-cycle management
in compliance with Hexagonal Architecture.
"""

from collections.abc import AsyncIterator
from typing import Protocol


class IBlobStoragePort(Protocol):
    """Abstract port for physical file storage operations."""

    async def save_blob(
        self,
        stream: AsyncIterator[bytes],
        content_hash: str,
    ) -> tuple[str, int]:
        """Stream bytes to storage under content_hash.

        Args:
            stream: Asynchronous byte iterator yielding chunks.
            content_hash: SHA-256 hexadecimal hash identifying the payload.

        Returns:
            Tuple of (storage_path, total_byte_size).
        """
        ...

    async def blob_exists(self, content_hash: str) -> bool:
        """Check if physical blob already exists in storage."""
        ...

    def get_blob_path(self, content_hash: str) -> str:
        """Get canonical storage path for given content hash."""
        ...

    async def delete_blob(self, content_hash: str) -> bool:
        """Permanently purge physical blob from storage."""
        ...

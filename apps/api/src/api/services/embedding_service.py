"""OpenAI Batch Embedding Service for Scholarly Document Chunks and Queries.

Generates 1536-dimensional dense vector embeddings using OpenAI's
text-embedding-3-small model with batching and error handling.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog
from api.core.config import settings
from pydantic import SecretStr

logger = structlog.get_logger("api.services.embedding")


class EmbeddingService:
    """Service for computing dense text embeddings via OpenAI API."""

    def __init__(
        self,
        api_key: str | SecretStr | None = None,
        base_url: str | None = None,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
    ) -> None:
        self.model = model
        self.dimensions = dimensions

        # Resolve API key
        resolved_key: str | None = None
        if api_key is not None:
            if isinstance(api_key, SecretStr):
                resolved_key = api_key.get_secret_value()
            else:
                resolved_key = str(api_key).strip()
        elif settings.OPENAI_API_KEY is not None:
            resolved_key = settings.OPENAI_API_KEY.get_secret_value()

        if not resolved_key or not resolved_key.strip():
            raise ValueError("OpenAI API key is required for EmbeddingService")

        self.api_key = resolved_key.strip()
        self.base_url = (
            base_url or settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
        ).rstrip("/")

    async def get_embedding(self, text: str) -> list[float]:
        """Compute 1536-dimensional embedding vector for a single text."""
        sanitized = text.strip() if text and text.strip() else " "
        embeddings = await self._call_openai_embedding([sanitized])
        if not embeddings:
            raise RuntimeError("OpenAI returned empty embedding response")
        return embeddings[0]

    async def get_embeddings_batch(
        self, texts: list[str], batch_size: int = 128
    ) -> list[list[float]]:
        """Compute embeddings for a list of texts in batches of size <= batch_size."""
        if not texts:
            return []

        if batch_size <= 0:
            batch_size = 128

        results: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            sanitized_chunk = [t.strip() if t and t.strip() else " " for t in chunk]
            batch_embeddings = await self._call_openai_embedding(sanitized_chunk)
            results.extend(batch_embeddings[: len(chunk)])

        return results

    async def _call_openai_embedding(self, texts: list[str]) -> list[list[float]]:
        """Call the OpenAI embeddings endpoint for a batch of texts."""
        if not texts:
            return []

        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
        }

        logger.debug(
            "calling_openai_embeddings",
            model=self.model,
            count=len(texts),
            dimensions=self.dimensions,
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as err:
                logger.error("openai_embedding_failed", error=str(err), url=url)
                raise

        items = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
        return [item["embedding"] for item in items]

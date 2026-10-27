#!/usr/bin/env python3
"""Backfill script for document chunk vector embeddings.

Scans all document_chunks where embedding IS NULL, computes 1536-dimensional
dense vector embeddings via EmbeddingService (text-embedding-3-small) in batches
up to 128 chunks, and updates PostgreSQL idempotently.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure monorepo package and api paths are on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
API_SRC = REPO_ROOT / "apps" / "api" / "src"
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"

for p in (API_SRC, CORE_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from api.db.models.chunk import DocumentChunkModel
from api.db.session import AsyncSessionLocal
from api.services.embedding_service import EmbeddingService
from sqlalchemy import func, select

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backfill_chunk_embeddings")


async def backfill_chunk_embeddings(batch_size: int = 128) -> int:
    """Find all document_chunks with NULL embeddings and backfill them in batches."""
    logger.info("Initializing EmbeddingService for backfill...")
    try:
        embedding_service = EmbeddingService()
    except Exception as e:
        logger.error("Failed to initialize EmbeddingService: %s", e)
        logger.error("Ensure OPENAI_API_KEY is configured in your environment or .env")
        return 1

    async with AsyncSessionLocal() as session:
        # 1. Count total chunks missing embeddings
        count_stmt = (
            select(func.count())
            .select_from(DocumentChunkModel)
            .where(DocumentChunkModel.embedding.is_(None))
        )
        res = await session.execute(count_stmt)
        total_missing = res.scalar() or 0

        logger.info("Total document chunks needing embeddings: %d", total_missing)
        if total_missing == 0:
            logger.info("All document chunks already have embeddings. Nothing to backfill.")
            return 0

        processed = 0

        while True:
            # Fetch next batch of chunks missing embeddings
            stmt = (
                select(DocumentChunkModel)
                .where(DocumentChunkModel.embedding.is_(None))
                .order_by(DocumentChunkModel.created_at.asc(), DocumentChunkModel.id.asc())
                .limit(batch_size)
            )
            chunks_res = await session.execute(stmt)
            batch = list(chunks_res.scalars().all())

            if not batch:
                break

            texts = [c.content for c in batch]
            logger.info(
                "Computing embeddings for batch of %d chunks (overall progress: %d/%d)...",
                len(batch),
                processed,
                total_missing,
            )

            try:
                embeddings = await embedding_service.get_embeddings_batch(
                    texts, batch_size=batch_size
                )
                if len(embeddings) != len(batch):
                    logger.error(
                        "Mismatch in returned embeddings count: got %d, expected %d",
                        len(embeddings),
                        len(batch),
                    )
                    break

                for chunk, emb in zip(batch, embeddings):
                    chunk.embedding = emb

                await session.commit()
                processed += len(batch)
                logger.info("Committed batch: %d/%d chunks backfilled.", processed, total_missing)

            except Exception as e:
                logger.exception("Error processing batch at offset %d: %s", processed, e)
                await session.rollback()
                return 1

        logger.info("Embedding backfill complete! Total processed: %d chunks.", processed)
        return 0


def main() -> None:
    exit_code = asyncio.run(backfill_chunk_embeddings())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

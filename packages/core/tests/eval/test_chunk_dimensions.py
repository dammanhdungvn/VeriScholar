"""Unit tests for multi-model embedding dimensions on DocumentChunk."""

from uuid import uuid4

import pytest
from core.domain.entities.chunk import (
    BGE_M3_EMBEDDING_DIM,
    OPENAI_EMBEDDING_DIM,
    VALID_EMBEDDING_DIMS,
    DocumentChunk,
)
from core.domain.exceptions import InvariantViolationError


def test_chunk_supports_both_1024_and_1536_dimensions() -> None:
    doc_id = uuid4()

    assert BGE_M3_EMBEDDING_DIM == 1024
    assert OPENAI_EMBEDDING_DIM == 1536
    assert 1024 in VALID_EMBEDDING_DIMS
    assert 1536 in VALID_EMBEDDING_DIMS

    # 1. 1024 dimensions (BGE-M3)
    chunk_1024 = DocumentChunk(
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="BGE-M3 Chunk Content",
        token_count=10,
        embedding=[0.01] * 1024,
    )
    assert chunk_1024.embedding is not None
    assert len(chunk_1024.embedding) == 1024

    # 2. 1536 dimensions (OpenAI text-embedding-3-small)
    chunk_1536 = DocumentChunk(
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="OpenAI Chunk Content",
        token_count=10,
        embedding=[0.02] * 1536,
    )
    assert chunk_1536.embedding is not None
    assert len(chunk_1536.embedding) == 1536

    # 3. attach_embedding with 1536 dims
    empty_chunk = DocumentChunk(
        document_id=doc_id,
        chunk_index=2,
        page_number=1,
        content="Empty Embedding Chunk",
        token_count=5,
    )
    assert empty_chunk.embedding is None
    empty_chunk.attach_embedding([0.05] * 1536)
    assert len(empty_chunk.embedding) == 1536


def test_chunk_rejects_disallowed_dimensions() -> None:
    doc_id = uuid4()
    for bad_dim in [128, 512, 768, 2048]:
        with pytest.raises(InvariantViolationError, match="dimension mismatch"):
            DocumentChunk(
                document_id=doc_id,
                chunk_index=0,
                page_number=1,
                content="Bad Dim Chunk",
                token_count=5,
                embedding=[0.1] * bad_dim,
            )

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=1,
            content="Valid chunk",
            token_count=5,
        )
        with pytest.raises(InvariantViolationError, match="Must be 1024 or 1536"):
            chunk.attach_embedding([0.1] * bad_dim)

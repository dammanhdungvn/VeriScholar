"""Unit tests for DocumentChunk domain entity."""

from uuid import uuid4

import pytest
from core.domain.entities.chunk import BGE_M3_EMBEDDING_DIM, DocumentChunk
from core.domain.exceptions import InvariantViolationError
from core.domain.value_objects.bounding_box import BoundingBox


def test_chunk_valid_instantiation() -> None:
    doc_id = uuid4()
    box = BoundingBox(x0=0.1, y0=0.1, x1=0.8, y1=0.4, page=1)

    chunk = DocumentChunk(
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="Transformer networks rely entirely on an attention mechanism.",
        bounding_boxes=[box],
        token_count=10,
    )

    assert chunk.document_id == doc_id
    assert chunk.chunk_index == 0
    assert chunk.page_number == 1
    assert chunk.token_count == 10
    assert len(chunk.bounding_boxes) == 1
    assert chunk.embedding is None
    assert chunk.bounding_boxes_raw == [[0.1, 0.1, 0.8, 0.4, 1]]


def test_chunk_embedding_dimension_invariant() -> None:
    doc_id = uuid4()
    valid_embedding = [0.01] * BGE_M3_EMBEDDING_DIM
    invalid_embedding = [0.01] * 512

    chunk = DocumentChunk(
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="Test content",
        token_count=5,
    )

    # Valid 1024-dim attachment succeeds
    chunk.attach_embedding(valid_embedding)
    assert chunk.embedding is not None
    assert len(chunk.embedding) == 1024

    # Invalid dimension attachment raises InvariantViolationError
    with pytest.raises(InvariantViolationError, match="Must be 1024"):
        chunk.attach_embedding(invalid_embedding)


def test_chunk_direct_instantiation_rejects_bad_embedding() -> None:
    with pytest.raises(InvariantViolationError, match="dimension mismatch"):
        DocumentChunk(
            document_id=uuid4(),
            chunk_index=0,
            page_number=1,
            content="Content",
            token_count=5,
            embedding=[0.5] * 128,  # Not 1024
        )


def test_chunk_add_bounding_box() -> None:
    chunk = DocumentChunk(
        document_id=uuid4(),
        chunk_index=1,
        page_number=2,
        content="Second page continuation",
        token_count=8,
    )
    assert len(chunk.bounding_boxes) == 0

    chunk.add_bounding_box(BoundingBox(x0=0.1, y0=0.1, x1=0.9, y1=0.3, page=2))
    chunk.add_bounding_box(BoundingBox(x0=0.1, y0=0.35, x1=0.9, y1=0.55, page=2))
    assert len(chunk.bounding_boxes) == 2

"""Unit tests for Document domain entity."""

from uuid import uuid4

import pytest
from core.domain.entities.document import Document
from core.domain.exceptions import (
    FileSizeLimitExceededError,
    InvalidContentHashError,
    InvalidDocumentStateTransitionError,
)
from core.domain.value_objects.enums import DocumentStage, DocumentStatus
from core.domain.value_objects.page_metadata import PageMetadata

VALID_HASH = "b" * 64


def test_document_valid_instantiation() -> None:
    user_id = uuid4()
    doc = Document(
        user_id=user_id,
        filename="attention_is_all_you_need.pdf",
        content_hash=VALID_HASH,
        file_size_bytes=2_048_000,
    )

    assert doc.user_id == user_id
    assert doc.filename == "attention_is_all_you_need.pdf"
    assert doc.status == DocumentStatus.UPLOADED
    assert doc.stage == DocumentStage.QUEUED
    assert doc.progress == 0
    assert doc.is_persistent is False
    assert doc.chunk_count == 0


def test_document_rejects_invalid_hash() -> None:
    with pytest.raises(InvalidContentHashError):
        Document(
            user_id=uuid4(),
            filename="paper.pdf",
            content_hash="short_hash",
            file_size_bytes=1000,
        )


def test_document_rejects_oversized_file() -> None:
    with pytest.raises(FileSizeLimitExceededError):
        Document(
            user_id=uuid4(),
            filename="large.pdf",
            content_hash=VALID_HASH,
            file_size_bytes=60_000_000,
        )


def test_document_lifecycle_progression() -> None:
    doc = Document(
        user_id=uuid4(),
        filename="nature_paper.pdf",
        content_hash=VALID_HASH,
        file_size_bytes=1_500_000,
    )

    doc.start_processing()
    assert doc.status == DocumentStatus.PROCESSING
    assert doc.stage == DocumentStage.PARSING
    assert doc.progress == 10

    doc.advance_stage(DocumentStage.CHUNKING, 40)
    assert doc.stage == DocumentStage.CHUNKING
    assert doc.progress == 40

    doc.advance_stage(DocumentStage.EMBEDDING, 75)
    assert doc.stage == DocumentStage.EMBEDDING
    assert doc.progress == 75

    pages = [
        PageMetadata(page_number=1, width_pt=595.0, height_pt=842.0),
        PageMetadata(page_number=2, width_pt=595.0, height_pt=842.0),
    ]

    doc.mark_completed(
        page_count=2,
        chunk_count=18,
        pages_metadata=pages,
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
    )

    assert doc.status == DocumentStatus.COMPLETED
    assert doc.stage == DocumentStage.COMPLETED
    assert doc.progress == 100
    assert doc.page_count == 2
    assert doc.chunk_count == 18
    assert doc.title == "Attention Is All You Need"
    assert doc.authors == ["Vaswani et al."]


def test_document_rejects_reprocessing_completed() -> None:
    doc = Document(
        user_id=uuid4(),
        filename="test.pdf",
        content_hash=VALID_HASH,
        file_size_bytes=1000,
    )
    doc.start_processing()
    doc.mark_completed(page_count=1, chunk_count=1, pages_metadata=[])

    with pytest.raises(InvalidDocumentStateTransitionError, match="already COMPLETED"):
        doc.start_processing()


def test_document_failure_transition() -> None:
    doc = Document(
        user_id=uuid4(),
        filename="corrupted.pdf",
        content_hash=VALID_HASH,
        file_size_bytes=1000,
    )
    doc.start_processing()
    doc.mark_failed("PDF header corrupted or password protected")

    assert doc.status == DocumentStatus.FAILED
    assert doc.stage == DocumentStage.FAILED
    assert "password protected" in str(doc.error_message)


def test_document_persistence_toggle() -> None:
    doc = Document(
        user_id=uuid4(),
        filename="test.pdf",
        content_hash=VALID_HASH,
        file_size_bytes=1000,
    )
    assert doc.is_persistent is False
    doc.set_persistence(True)
    assert doc.is_persistent is True
    doc.set_persistence(False)
    assert doc.is_persistent is False

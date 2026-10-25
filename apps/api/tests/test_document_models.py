from uuid import uuid4

from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.summary import DocumentSummaryModel


def test_document_storage_blob_model_defaults():
    blob = DocumentStorageBlobModel(
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_path="e3/b0/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_size_bytes=1024,
    )
    assert blob.ref_count == 1
    assert blob.status == "processing"
    assert blob.file_size_bytes == 1024


def test_document_model_defaults_and_fields():
    assert "is_starred" in DocumentModel.__table__.columns
    assert "access_status" in DocumentModel.__table__.columns
    user_id = uuid4()
    doc = DocumentModel(
        user_id=user_id,
        filename="attention.pdf",
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_size_bytes=2048,
    )
    assert doc.user_id == user_id
    assert doc.is_starred is False
    assert doc.access_status == "open_access_pdf"
    assert doc.chunk_count == 0
    assert doc.status == "uploaded"
    assert doc.is_persistent is False


def test_document_chunk_model_dual_support_and_defaults():
    assert "user_id" in DocumentChunkModel.__table__.columns
    assert "content_tsv" in DocumentChunkModel.__table__.columns
    user_id = uuid4()
    doc_id = uuid4()

    # Initialized with text_content & bbox_json
    chunk1 = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        text_content="Transformer self-attention mechanism...",
        bbox_json=[[10.0, 20.0, 100.0, 50.0]],
    )
    assert chunk1.user_id == user_id
    assert chunk1.document_id == doc_id
    assert chunk1.text_content == "Transformer self-attention mechanism..."
    assert chunk1.content == "Transformer self-attention mechanism..."
    assert chunk1.bbox_json == [[10.0, 20.0, 100.0, 50.0]]
    assert chunk1.bounding_boxes == [[10.0, 20.0, 100.0, 50.0]]
    assert chunk1.token_count == 0

    # Test property setters
    chunk1.text_content = "Updated content"
    assert chunk1.content == "Updated content"
    chunk1.content = "Re-updated"
    assert chunk1.text_content == "Re-updated"

    chunk1.bbox_json = [[1.0, 2.0, 3.0, 4.0]]
    assert chunk1.bounding_boxes == [[1.0, 2.0, 3.0, 4.0]]
    chunk1.bounding_boxes = [[5.0, 6.0, 7.0, 8.0]]
    assert chunk1.bbox_json == [[5.0, 6.0, 7.0, 8.0]]

    # Initialized with content & bounding_boxes
    chunk2 = DocumentChunkModel(
        user_id=user_id,
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="Multi-head attention allows...",
        bounding_boxes=[[12.0, 25.0, 105.0, 55.0]],
        token_count=42,
    )
    assert chunk2.user_id == user_id
    assert chunk2.content == "Multi-head attention allows..."
    assert chunk2.text_content == "Multi-head attention allows..."
    assert chunk2.bounding_boxes == [[12.0, 25.0, 105.0, 55.0]]
    assert chunk2.bbox_json == [[12.0, 25.0, 105.0, 55.0]]
    assert chunk2.token_count == 42

    # Check content_tsv column exists on model
    assert hasattr(DocumentChunkModel, "content_tsv")


def test_document_summary_model_user_id_and_fields():
    assert "user_id" in DocumentSummaryModel.__table__.columns
    user_id = uuid4()
    doc_id = uuid4()

    summary = DocumentSummaryModel(
        user_id=user_id,
        document_id=doc_id,
        problem_statement="Recurrent models are slow.",
        problem_citations=[],
        contributions="Proposed Multi-Head Attention.",
        contribution_citations=[],
        limitations="Quadratic memory complexity.",
        limitation_citations=[],
    )
    assert summary.user_id == user_id
    assert summary.document_id == doc_id
    assert summary.contributions == "Proposed Multi-Head Attention."
    assert summary.total_tokens == 0
    assert summary.latency_ms == 0


def test_reference_item_model_user_id_and_fields():
    assert "user_id" in ReferenceItemModel.__table__.columns
    user_id = uuid4()
    doc_id = uuid4()

    ref = ReferenceItemModel(
        user_id=user_id,
        document_id=doc_id,
        ref_index=1,
        raw_text="Vaswani et al. 2017.",
        doi="10.48550/arXiv.1706.03762",
    )
    assert ref.user_id == user_id
    assert ref.document_id == doc_id
    assert ref.ref_index == 1
    assert ref.doi == "10.48550/arXiv.1706.03762"

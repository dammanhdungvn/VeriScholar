"""Unit tests for SAFE Fact-Checking Core Domain Engine (Module 2)."""

from uuid import uuid4

import pytest
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import FactVerificationStatus
from core.domain.value_objects.bounding_box import BoundingBox
from core.services.safe_fact_checker import SafeFactChecker


@pytest.fixture
def sample_literature_chunks() -> list[DocumentChunk]:
    """Create sample literature chunks with normalized bounding boxes."""
    doc_id = uuid4()
    box1 = BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.3, page=1)
    box2 = BoundingBox(x0=0.15, y0=0.4, x1=0.85, y1=0.55, page=2)

    chunk1 = DocumentChunk(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content=(
            "The proposed Transformer architecture achieves 28.4 BLEU on English-to-German "
            "translation, establishing state of the art and outperforming all previous ensembles."
        ),
        bounding_boxes=[box1],
        token_count=30,
    )

    chunk2 = DocumentChunk(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=1,
        page_number=2,
        content=(
            "We evaluate our model on the WMT 2014 English-to-French translation task, "
            "where it scores 41.8 BLEU after training for 3.5 days on 8 GPUs."
        ),
        bounding_boxes=[box2],
        token_count=35,
    )

    return [chunk1, chunk2]


def test_decompose_claims() -> None:
    """Verify decomposition of complex sentences into atomic claims."""
    checker = SafeFactChecker()
    text = (
        "The Transformer model achieves 28.4 BLEU on English-to-German translation, "
        "and it scores 41.8 BLEU on English-to-French. Furthermore, training required 8 GPUs."
    )
    claims = checker.decompose_claims(text)
    assert len(claims) >= 3
    assert any("28.4 BLEU" in c for c in claims)
    assert any("41.8 BLEU" in c for c in claims)
    assert any("8 GPUs" in c for c in claims)


@pytest.mark.asyncio
async def test_verify_supported_claim(sample_literature_chunks: list[DocumentChunk]) -> None:
    """Verify that a factually accurate claim receives SUPPORTED verdict with bounding boxes."""
    checker = SafeFactChecker()
    text = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    report = await checker.verify_text(text, sample_literature_chunks)

    assert report.total_claims >= 1
    assert report.supported_claims == 1
    assert report.contradicted_claims == 0
    assert report.unverified_claims == 0
    assert report.supported_ratio == 1.0

    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.SUPPORTED
    assert claim.confidence_score >= 0.6
    assert claim.evidence_page == 1
    assert len(claim.evidence_bounding_boxes) == 1
    assert claim.evidence_bounding_boxes[0].page == 1


@pytest.mark.asyncio
async def test_verify_contradicted_claim(sample_literature_chunks: list[DocumentChunk]) -> None:
    """Verify that a claim with contradictory statement is labeled CONTRADICTED."""
    checker = SafeFactChecker()
    # Baseline assertion: asserts "underperforms" while chunk says "outperforming"
    text = "The Transformer architecture underperforms previous ensemble baselines on translation."
    report = await checker.verify_text(text, sample_literature_chunks)

    assert len(report.claims) == 1
    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.CONTRADICTED
    assert "underperform" in claim.reasoning or "mâu thuẫn" in claim.reasoning.lower()


@pytest.mark.asyncio
async def test_verify_not_enough_info_claim(sample_literature_chunks: list[DocumentChunk]) -> None:
    """Verify that an unsubstantiated claim receives NOT_ENOUGH_INFO."""
    checker = SafeFactChecker()
    text = "Quantum computing demonstrates exponential speedup for integer factorization."
    report = await checker.verify_text(text, sample_literature_chunks)

    assert len(report.claims) == 1
    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.NOT_ENOUGH_INFO
    assert claim.evidence_text is None
    assert report.supported_claims == 0
    assert report.unverified_claims == 1
    assert report.supported_ratio == 0.0

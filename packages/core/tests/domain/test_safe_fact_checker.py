"""Unit tests for SAFE Fact-Checking Core Domain Engine (Module 2)."""

from uuid import uuid4

import pytest
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import (
    FactVerificationStatus,
    SafeNliEvidence,
    SafeNliVerdict,
)
from core.domain.value_objects.bounding_box import BoundingBox
from core.ports.safe_verifier import ISafeNliPort
from core.services.safe_fact_checker import SafeFactChecker
from core.services.safe_nli_adapter import SafeNliEngineAdapter


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


# ------------------------------------------------------------------------------
# Neural NLI Adapter Integration Tests (PRD §3.2 & Option A Contract)
# ------------------------------------------------------------------------------
_neural_available = SafeNliEngineAdapter().is_neural_active
requires_neural_model = pytest.mark.skipif(
    not _neural_available,
    reason="Offline ONNX model weights not present on disk (models/nli/...)",
)


@requires_neural_model
@pytest.mark.asyncio
async def test_verify_text_with_neural_adapter_supported(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify neural SafeNliEngineAdapter produces SUPPORTED verdict with evidence anchors."""
    adapter = SafeNliEngineAdapter()
    checker = SafeFactChecker(nli_adapter=adapter)
    text = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    doc_id = sample_literature_chunks[0].document_id
    doc_metadata = {doc_id: "Attention Is All You Need"}

    report = await checker.verify_text(
        text=text,
        retrieval_context=sample_literature_chunks,
        doc_metadata=doc_metadata,
    )

    assert report.total_claims == 1
    assert report.supported_claims == 1
    assert report.contradicted_claims == 0
    assert report.unverified_claims == 0
    assert report.supported_ratio == 1.0

    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.SUPPORTED
    assert claim.confidence_score >= 0.8
    assert claim.evidence_document_id == doc_id
    assert claim.evidence_document_title == "Attention Is All You Need"
    assert claim.evidence_page == 1
    assert len(claim.evidence_bounding_boxes) == 1
    assert claim.evidence_bounding_boxes[0].page == 1
    assert len(claim.reasoning.split(". ")) <= 2


@requires_neural_model
@pytest.mark.asyncio
async def test_verify_text_with_neural_adapter_contradicted_numerical(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify neural adapter detects numerical mismatch and tags CONTRADICTED."""
    adapter = SafeNliEngineAdapter()
    checker = SafeFactChecker(nli_adapter=adapter)
    text = "The Transformer architecture achieves 35.2 BLEU on English-to-German translation."
    doc_id = sample_literature_chunks[0].document_id
    doc_metadata = {doc_id: "Attention Is All You Need"}

    report = await checker.verify_text(
        text=text,
        retrieval_context=sample_literature_chunks,
        doc_metadata=doc_metadata,
    )

    assert report.total_claims == 1
    assert report.contradicted_claims == 1
    assert report.supported_claims == 0
    assert report.supported_ratio == 0.0

    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.CONTRADICTED
    assert claim.evidence_page == 1
    assert len(claim.evidence_bounding_boxes) == 1
    assert "Số liệu trong khẳng định" in claim.reasoning or "không khớp" in claim.reasoning


@requires_neural_model
@pytest.mark.asyncio
async def test_verify_text_with_neural_adapter_contradicted_lexical(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify neural adapter detects antonym/contradiction and tags CONTRADICTED."""
    adapter = SafeNliEngineAdapter()
    checker = SafeFactChecker(nli_adapter=adapter)
    text = "The Transformer architecture underperforms all previous single models."

    report = await checker.verify_text(
        text=text,
        retrieval_context=sample_literature_chunks,
    )

    assert report.total_claims == 1
    assert report.contradicted_claims == 1
    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.CONTRADICTED
    assert claim.evidence_page == 1


@requires_neural_model
@pytest.mark.asyncio
async def test_verify_text_with_neural_adapter_not_enough_info(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify neural adapter handles out-of-domain query with NOT_ENOUGH_INFO."""
    adapter = SafeNliEngineAdapter()
    checker = SafeFactChecker(nli_adapter=adapter)
    text = "Quantum computing demonstrates exponential speedup for integer factorization."

    report = await checker.verify_text(
        text=text,
        retrieval_context=sample_literature_chunks,
    )

    assert report.total_claims == 1
    assert report.unverified_claims == 1
    assert report.supported_claims == 0
    claim = report.claims[0]
    assert claim.status == FactVerificationStatus.NOT_ENOUGH_INFO
    assert claim.evidence_text is None
    assert claim.evidence_bounding_boxes == []


@pytest.mark.asyncio
async def test_verify_text_hexagonal_di_mock_port(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify SafeFactChecker works with any custom implementation of ISafeNliPort."""

    class CustomFakeNliAdapter(ISafeNliPort):
        async def classify(
            self,
            claim: str,
            retrieval_context: list[DocumentChunk],
        ) -> SafeNliVerdict:
            return SafeNliVerdict(
                label="supported",
                evidence=SafeNliEvidence(
                    chunk_id=retrieval_context[0].id,
                    page=1,
                    bounding_boxes=retrieval_context[0].bounding_boxes,
                    text="Mock verified evidence.",
                ),
                explanation="Fake adapter verified claim successfully.",
            )

    checker = SafeFactChecker(nli_adapter=CustomFakeNliAdapter())
    report = await checker.verify_text("Arbitrary factual assertion.", sample_literature_chunks)

    assert report.supported_claims == 1
    assert report.claims[0].status == FactVerificationStatus.SUPPORTED
    assert report.claims[0].evidence_text == "Mock verified evidence."
    assert report.claims[0].reasoning == "Fake adapter verified claim successfully."


@pytest.mark.asyncio
async def test_verify_text_with_adapter_exception_fallback_to_heuristic(
    sample_literature_chunks: list[DocumentChunk],
) -> None:
    """Verify SafeFactChecker falls back gracefully to heuristic when adapter raises exception."""

    class CrashingNliAdapter(ISafeNliPort):
        async def classify(
            self,
            claim: str,
            retrieval_context: list[DocumentChunk],
        ) -> SafeNliVerdict:
            raise RuntimeError("Simulated unhandled ONNX runtime crash")

    checker = SafeFactChecker(nli_adapter=CrashingNliAdapter())
    text = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    doc_id = sample_literature_chunks[0].document_id
    doc_metadata = {doc_id: "Attention Is All You Need"}

    report = await checker.verify_text(
        text=text,
        retrieval_context=sample_literature_chunks,
        doc_metadata=doc_metadata,
    )

    # Heuristic fallback successfully catches the exception and verifies claim
    assert report.total_claims == 1
    assert report.supported_claims == 1
    assert report.claims[0].status == FactVerificationStatus.SUPPORTED
    assert report.claims[0].evidence_document_id == doc_id


def test_clean_latex_for_fact_checking_strips_preamble_and_environments() -> None:
    """Verify that decompose_claims sanitizes LaTeX preambles, macros, math, and comments."""
    checker = SafeFactChecker()
    latex_code = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=blue}
\geometry{a4paper, margin=1in}
\title{Self-Attention Networks}
\author{Research Author}

\begin{document}
\maketitle

% This is an internal draft comment
\section{Experimental Results}
The Transformer architecture achieves 28.4 BLEU on English-to-German translation.
In our experiments, the proposed model outperforms previous ensemble baselines by 2.1 BLEU.
Furthermore, training required 8 GPUs for 3.5 days.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{architecture.png}
\caption{System Architecture Diagram}
\end{figure}

\begin{equation}
E = mc^2 + \int_0^1 f(x) dx
\end{equation}

\bibliographystyle{plain}
\bibliography{sample}
\end{document}
"""
    claims = checker.decompose_claims(latex_code)

    # Must extract only genuine prose sentences, not LaTeX commands
    assert len(claims) >= 3
    assert any("28.4 BLEU" in c for c in claims)
    assert any("outperforms previous ensemble" in c for c in claims)
    assert any("8 GPUs" in c for c in claims)

    # Must NOT contain LaTeX preamble, environments, or comments
    for c in claims:
        assert r"\documentclass" not in c
        assert r"\usepackage" not in c
        assert r"\hypersetup" not in c
        assert r"\geometry" not in c
        assert r"\begin" not in c
        assert r"\end" not in c
        assert r"\includegraphics" not in c
        assert "E = mc^2" not in c
        assert "draft comment" not in c

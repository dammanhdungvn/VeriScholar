"""Unit tests for dedicated SAFE NLI Adapter & Option A PRD Contract."""

from uuid import uuid4

import pytest
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import SafeNliEvidence, SafeNliVerdict
from core.domain.value_objects.bounding_box import BoundingBox
from core.services.safe_nli_adapter import SafeNliEngineAdapter
from pydantic import ValidationError


@pytest.fixture
def sample_chunk() -> DocumentChunk:
    doc_id = uuid4()
    return DocumentChunk(
        id=uuid4(),
        document_id=doc_id,
        page_number=4,
        chunk_index=0,
        token_count=35,
        content=(
            "The proposed Transformer architecture achieves 28.4 BLEU on English-to-German "
            "translation, outperforming all previous single and ensemble models. "
            "Training took 3.5 days on 8 P100 GPUs."
        ),
        bounding_boxes=[BoundingBox(x0=0.1, y0=0.2, x1=0.8, y1=0.35, page=4)],
    )


@pytest.mark.asyncio
async def test_nli_verdict_supported(sample_chunk: DocumentChunk) -> None:
    """Verify supported claim returns label='supported' and concise explanation."""
    adapter = SafeNliEngineAdapter(min_support_threshold=0.35)
    claim = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."

    verdict = await adapter.classify(claim, [sample_chunk])

    assert verdict.label == "supported"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 4
    assert len(verdict.evidence.bounding_boxes) == 1
    assert verdict.evidence.bounding_boxes[0].page == 4
    assert "28.4 BLEU" in verdict.evidence.text

    # Contract checks
    assert verdict.explanation != ""
    assert len(verdict.explanation.split(". ")) <= 2


@pytest.mark.asyncio
async def test_nli_verdict_contradicted_numerical(sample_chunk: DocumentChunk) -> None:
    """Verify numerical mismatch results in label='contradicted'."""
    adapter = SafeNliEngineAdapter(min_support_threshold=0.35)
    # Claim asserts 35.2 BLEU while chunk states 28.4 BLEU
    claim = "The Transformer architecture achieves 35.2 BLEU on English-to-German translation."

    verdict = await adapter.classify(claim, [sample_chunk])

    assert verdict.label == "contradicted"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 4
    assert "Số liệu trong khẳng định" in verdict.explanation


@pytest.mark.asyncio
async def test_nli_verdict_contradicted_lexical(sample_chunk: DocumentChunk) -> None:
    """Verify antonym/contradiction pair results in label='contradicted'."""
    adapter = SafeNliEngineAdapter(min_support_threshold=0.30)
    # Claim asserts underperformed while chunk states outperformed
    claim = "The Transformer architecture underperforms all previous single models."

    verdict = await adapter.classify(claim, [sample_chunk])

    assert verdict.label == "contradicted"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 4
    assert "trái ngược" in verdict.explanation


@pytest.mark.asyncio
async def test_nli_verdict_not_enough_info(sample_chunk: DocumentChunk) -> None:
    """Verify unrelated claim returns label='not_enough_info' with None evidence."""
    adapter = SafeNliEngineAdapter(min_support_threshold=0.45)
    claim = "Quantum computing algorithms factor large prime numbers in polynomial time."

    verdict = await adapter.classify(claim, [sample_chunk])

    assert verdict.label == "not_enough_info"
    assert verdict.evidence is None
    assert "Không tìm thấy" in verdict.explanation


def test_option_a_contract_forbids_chain_of_thought() -> None:
    """Verify Option A contract strictly forbids chain-of-thought or reasoning trace fields."""
    # Valid verdict creation
    verdict = SafeNliVerdict(
        label="supported",
        evidence=SafeNliEvidence(
            chunk_id=uuid4(),
            page=1,
            bounding_boxes=[BoundingBox(x0=0.1, y0=0.1, x1=0.9, y1=0.9, page=1)],
            text="Verified passage",
        ),
        explanation="First sentence explanation. Second sentence evidence citation.",
    )

    data = verdict.model_dump()
    assert set(data.keys()) == {"label", "evidence", "explanation"}
    assert "chain_of_thought" not in data
    assert "thought" not in data
    assert "reasoning_steps" not in data

    # Attempting to inject chain-of-thought MUST raise ValidationError due to extra='forbid'
    with pytest.raises(ValidationError):
        SafeNliVerdict(
            label="supported",
            explanation="Valid explanation.",
            chain_of_thought="Step 1: Analyzed text. Step 2: Inferred truth.",  # type: ignore[call-arg]
        )


def test_option_a_contract_truncates_long_explanation() -> None:
    """Verify explanation exceeding 2 sentences is constrained to at most 2 sentences."""
    long_text = (
        "Sentence one here. Sentence two here. Sentence three should be dropped. "
        "Sentence four dropped."
    )
    verdict = SafeNliVerdict(
        label="supported",
        evidence=None,
        explanation=long_text,
    )
    # Must only keep first two sentences
    assert verdict.explanation == "Sentence one here. Sentence two here."


def test_nli_pair_ordering_and_model_selection() -> None:
    """Verify premise=evidence, hypothesis=claim and default model name."""
    adapter = SafeNliEngineAdapter()
    assert adapter.model_name == "cross-encoder/nli-deberta-v3-small"

    pair = adapter.format_nli_pair(
        evidence_text="Passage from academic literature",
        claim="Claim under verification",
    )
    assert pair["premise"] == "Passage from academic literature"
    assert pair["hypothesis"] == "Claim under verification"


@pytest.mark.asyncio
async def test_evidence_without_coordinates_preserves_none_without_fabrication() -> None:
    """Verify evidence lacking bbox leaves bounding_boxes empty without fabricating coords."""
    chunk_without_coords = DocumentChunk(
        id=uuid4(),
        document_id=uuid4(),
        chunk_index=0,
        page_number=1,
        bounding_boxes=[],  # No bounding boxes
        content="Transformer model achieves strong BLEU scores on machine translation.",
        token_count=15,
    )

    adapter = SafeNliEngineAdapter(min_support_threshold=0.3)
    verdict = await adapter.classify(
        "Transformer model achieves strong BLEU scores on machine translation.",
        [chunk_without_coords],
    )

    assert verdict.label == "supported"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 1
    assert verdict.evidence.bounding_boxes == []

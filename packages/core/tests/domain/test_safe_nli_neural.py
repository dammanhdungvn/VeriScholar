"""Integration & benchmark tests for dedicated offline ONNX SAFE NLI neural engine."""

import time
from uuid import uuid4

import pytest
from core.domain.entities.chunk import DocumentChunk
from core.domain.value_objects.bounding_box import BoundingBox
from core.eval.adapters.scifact import SciFactAdapter
from core.services.safe_nli_adapter import SafeNliEngineAdapter

_neural_available = SafeNliEngineAdapter().is_neural_active
requires_neural_model = pytest.mark.skipif(
    not _neural_available,
    reason="Offline ONNX model weights not present on disk (models/nli/...)",
)


@pytest.fixture
def transformer_chunk() -> DocumentChunk:
    return DocumentChunk(
        id=uuid4(),
        document_id=uuid4(),
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


@requires_neural_model
def test_neural_model_initialization() -> None:
    """Verify that SafeNliEngineAdapter successfully activates ONNX session."""
    adapter = SafeNliEngineAdapter()
    assert adapter.is_neural_active is True
    assert adapter.model_name == "cross-encoder/nli-deberta-v3-small"


@requires_neural_model
def test_neural_model_direct_batch_prediction() -> None:
    """Verify direct batch probability outputs across 3 logical NLI classes."""
    adapter = SafeNliEngineAdapter()
    assert adapter.is_neural_active is True

    pairs = [
        # 1. Entailment
        (
            (
                "The proposed Transformer architecture achieves 28.4 BLEU on "
                "English-to-German translation."
            ),
            "The Transformer architecture achieves 28.4 BLEU on English-to-German translation.",
        ),
        # 2. Contradiction
        (
            (
                "The proposed Transformer architecture achieves 28.4 BLEU on English-to-German "
                "translation, outperforming all previous single and ensemble models."
            ),
            "The Transformer architecture underperforms all previous single models.",
        ),
        # 3. Neutral
        (
            (
                "The proposed Transformer architecture achieves 28.4 BLEU on English-to-German "
                "translation, outperforming all previous single and ensemble models."
            ),
            (
                "The researchers plan to evaluate the architecture on additional language pairs "
                "in future work."
            ),
        ),
    ]

    predictions = adapter._predict_neural_batch(pairs)
    assert len(predictions) == 3

    p_contra_1, p_entail_1, p_neutral_1 = predictions[0]
    assert p_entail_1 > 0.90, f"Expected entailment > 0.90, got {p_entail_1}"

    p_contra_2, p_entail_2, p_neutral_2 = predictions[1]
    assert p_contra_2 > 0.90, f"Expected contradiction > 0.90, got {p_contra_2}"

    p_contra_3, p_entail_3, p_neutral_3 = predictions[2]
    assert p_neutral_3 > 0.80, f"Expected neutral > 0.80, got {p_neutral_3}"


@requires_neural_model
@pytest.mark.asyncio
async def test_neural_model_classify_verdicts(transformer_chunk: DocumentChunk) -> None:
    """Verify end-to-end classify() generates compliant Option A verdicts via ONNX."""
    adapter = SafeNliEngineAdapter()
    assert adapter.is_neural_active is True

    # 1. Supported
    claim_supp = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    verdict_supp = await adapter.classify(claim_supp, [transformer_chunk])
    assert verdict_supp.label == "supported"
    assert verdict_supp.evidence is not None
    assert verdict_supp.evidence.page == 4
    assert len(verdict_supp.evidence.bounding_boxes) == 1
    assert "28.4 BLEU" in verdict_supp.evidence.text
    assert len(verdict_supp.explanation.split(". ")) <= 2

    # 2. Numerical Contradiction
    claim_num = "The Transformer architecture achieves 35.2 BLEU on English-to-German translation."
    verdict_num = await adapter.classify(claim_num, [transformer_chunk])
    assert verdict_num.label == "contradicted"
    assert verdict_num.evidence is not None
    assert verdict_num.evidence.page == 4
    assert "Số liệu trong khẳng định" in verdict_num.explanation

    # 3. Lexical Contradiction
    claim_lex = "The Transformer architecture underperforms all previous single models."
    verdict_lex = await adapter.classify(claim_lex, [transformer_chunk])
    assert verdict_lex.label == "contradicted"
    assert verdict_lex.evidence is not None
    assert verdict_lex.evidence.page == 4

    # 4. Not Enough Info
    claim_neut = "Quantum computing algorithms factor large prime numbers in polynomial time."
    verdict_neut = await adapter.classify(claim_neut, [transformer_chunk])
    assert verdict_neut.label == "not_enough_info"
    assert verdict_neut.evidence is None


@pytest.mark.asyncio
async def test_neural_model_fallback_when_disabled(transformer_chunk: DocumentChunk) -> None:
    """Verify that use_neural=False seamlessly falls back to deterministic rule engine."""
    adapter = SafeNliEngineAdapter(use_neural=False)
    assert adapter.is_neural_active is False

    claim = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    verdict = await adapter.classify(claim, [transformer_chunk])
    assert verdict.label == "supported"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 4


@pytest.mark.asyncio
async def test_neural_model_fallback_on_invalid_path(transformer_chunk: DocumentChunk) -> None:
    """Verify that missing model files trigger graceful fallback rather than crash."""
    adapter = SafeNliEngineAdapter(model_dir="/tmp/non_existent_model_dir_xyz")
    assert adapter.is_neural_active is False

    claim = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    verdict = await adapter.classify(claim, [transformer_chunk])
    assert verdict.label == "supported"
    assert verdict.evidence is not None


@requires_neural_model
@pytest.mark.asyncio
async def test_neural_inference_latency_sla(transformer_chunk: DocumentChunk) -> None:
    """Verify that inference latency strictly adheres to sub-100ms SLA on CPU."""
    adapter = SafeNliEngineAdapter()
    assert adapter.is_neural_active is True

    claim = "The Transformer architecture achieves 28.4 BLEU on English-to-German translation."
    latencies: list[float] = []

    # Run 15 iterations
    for _ in range(15):
        t0 = time.perf_counter()
        verdict = await adapter.classify(claim, [transformer_chunk])
        dur_ms = (time.perf_counter() - t0) * 1000
        latencies.append(dur_ms)
        assert verdict.label == "supported"

    mean_latency = sum(latencies) / len(latencies)
    assert mean_latency < 50.0, f"Mean latency {mean_latency:.2f}ms exceeds 50ms SLA"


@requires_neural_model
@pytest.mark.asyncio
async def test_scifact_sample_evaluation_pipeline() -> None:
    """Verify end-to-end evaluation with SciFact benchmark adapter."""
    adapter = SafeNliEngineAdapter()
    assert adapter.is_neural_active is True

    scifact = SciFactAdapter(
        corpus={
            "100": {
                "title": "Attention Is All You Need",
                "abstract": [
                    (
                        "The dominant sequence transduction models are based on complex "
                        "recurrent or convolutional neural networks."
                    ),
                    "We propose the Transformer, a model architecture eschewing recurrence.",
                    (
                        "The Transformer achieves 28.4 BLEU on the WMT 2014 "
                        "English-to-German translation task."
                    ),
                ],
            }
        }
    )

    raw_claim = {
        "id": 1,
        "claim": "The Transformer achieves 28.4 BLEU on English-to-German translation.",
        "cited_doc_ids": [100],
        "evidence": {
            "100": [{"sentences": [2], "label": "SUPPORT"}],
        },
    }

    samples = scifact.parse_data([raw_claim])
    assert len(samples) == 1
    sample = samples[0]

    # Convert corpus abstract into DocumentChunk
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=uuid4(),
        page_number=1,
        chunk_index=0,
        token_count=45,
        content=" ".join(scifact.corpus["100"]["abstract"]),
        bounding_boxes=[BoundingBox(x0=0.1, y0=0.1, x1=0.9, y1=0.3, page=1)],
    )

    verdict = await adapter.classify(sample.query, [chunk])
    assert verdict.label == "supported"
    assert verdict.evidence is not None
    assert verdict.evidence.page == 1

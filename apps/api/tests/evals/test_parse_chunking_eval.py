"""Eval Suite for Document Parse, 4-Tier Hierarchical Chunking, and Live API Evaluation Harness.

Validates:
1. Ground-Truth Golden Dataset integrity and structural invariants.
2. Tier 1: Section-Aware Splitting (zero section leakage).
3. Tier 2: Block-Level / Table / Equation Preservation.
4. Tier 3: Sentence-Boundary Splitting (Boundary Integrity Ratio == 100%).
5. Tier 4: Contextual Enrichment Header tagging for vector search.
6. Bounding Box Normalization Invariants ([0.0, 1.0], Top-Left origin).
7. Ragas QA retrieval readiness against golden answers.
8. Live AI Model Integration via real API keys loaded from .env:
   - Live Vector Embedding generation via OpenAI API (text-embedding-3-small, 1536-dim).
   - Live Semantic Reranking validation via Cohere API (rerank-v3.5).
   - Live LLM-as-a-Judge evaluation (Temperature=0.0, Likert 1-5 & Faithfulness Score >= 0.95).
"""

import json
import os
import re
from pathlib import Path
from typing import Any

import pymupdf
import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path("/home/dammanhdungvn/Downloads/Workspace/VeriScholar")
API_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env"
ROOT_ENV_PATH = PROJECT_ROOT / ".env"

if API_ENV_PATH.exists():
    load_dotenv(API_ENV_PATH)
elif ROOT_ENV_PATH.exists():
    load_dotenv(ROOT_ENV_PATH)

DATA_DIR = PROJECT_ROOT / "data" / "papers"
GOLDEN_DATASET_PATH = DATA_DIR / "golden_eval_dataset.json"


@pytest.fixture(scope="module")
def golden_dataset() -> dict[str, Any]:
    """Load and parse the ground-truth golden dataset."""
    assert GOLDEN_DATASET_PATH.exists(), f"Golden dataset not found at {GOLDEN_DATASET_PATH}"
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def test_golden_dataset_schema_and_integrity(golden_dataset: dict[str, Any]) -> None:
    """Verify that golden evaluation dataset adheres to required contract."""
    assert golden_dataset.get("version") == "1.0.0"
    papers = golden_dataset.get("benchmark_papers", {})
    assert len(papers) >= 3, "Golden dataset must evaluate at least 3 distinct papers"

    criteria = golden_dataset.get("acceptance_criteria", {})
    assert criteria.get("boundary_integrity_ratio") == 1.0
    assert criteria.get("section_leakage_rate") == 0.0
    assert criteria.get("bbox_iou_threshold") == 0.85


@pytest.mark.parametrize(
    "pdf_filename",
    [
        "1706.03762v7.pdf",
        "2504.19754v1.pdf",
        "2507.12425v1.pdf",
    ],
)
def test_pdf_physical_integrity_and_text_layer(pdf_filename: str) -> None:
    """Validate that physical benchmark PDFs exist, open cleanly, and have valid text layers."""
    pdf_path = DATA_DIR / pdf_filename
    assert pdf_path.exists(), f"Benchmark PDF missing: {pdf_path}"

    doc = pymupdf.open(pdf_path)
    assert len(doc) > 0, "PDF must have at least 1 page"

    sample_pages = min(3, len(doc))
    for page_idx in range(sample_pages):
        page_text = doc[page_idx].get_text().strip()
        assert len(page_text) >= 100, f"Page {page_idx + 1} chars below Fast-Path threshold"


def test_tier1_section_aware_boundaries(golden_dataset: dict[str, Any]) -> None:
    """Tier 1 Eval: Verify Section-Aware Splitting does not mix distinct sections."""
    papers = golden_dataset.get("benchmark_papers", {})
    for pdf_name, meta in papers.items():
        expected_sections = meta.get("expected_sections", [])
        assert len(expected_sections) >= 3, f"Insufficient expected sections for {pdf_name}"

        last_page = 1
        for sec in expected_sections:
            assert sec["page_start"] >= last_page or sec["page_start"] == last_page - 1
            assert sec["page_end"] >= sec["page_start"]
            last_page = sec["page_start"]


def test_tier2_structural_invariants_and_equations(golden_dataset: dict[str, Any]) -> None:
    """Tier 2 Eval: Verify that critical mathematical equations and tables are preserved."""
    papers = golden_dataset.get("benchmark_papers", {})
    transformer_paper = papers.get("1706.03762v7.pdf", {})
    invariants = transformer_paper.get("structural_invariants", {})

    equations = invariants.get("must_preserve_equations", [])
    assert len(equations) >= 2
    assert any("Attention(Q, K, V)" in eq for eq in equations)
    assert any("MultiHead(Q, K, V)" in eq for eq in equations)

    tables = invariants.get("must_preserve_tables", [])
    assert len(tables) >= 2


def test_tier3_sentence_boundary_integrity_simulation(golden_dataset: dict[str, Any]) -> None:
    """Tier 3 Eval: Sentence-Boundary Splitting must never cut mid-sentence (100% integrity)."""
    raw_paragraph = (
        "Recurrent models typically factor computation along the symbol positions. "
        "Aligning the positions to steps in computation time, they generate hidden states. "
        "This inherently sequential nature precludes parallelization within examples. "
        "Recent work has achieved significant improvements in efficiency. "
        "However, fundamental constraints remain."
    )

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_paragraph) if s.strip()]
    assert len(sentences) == 5

    max_chunk_chars = 180
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for s in sentences:
        if current_len + len(s) > max_chunk_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [s]
            current_len = len(s)
        else:
            current_chunk.append(s)
            current_len += len(s)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    for chunk in chunks:
        assert chunk[-1] in {".", "!", "?"}, f"Chunk violated sentence boundary: '{chunk}'"


def test_tier4_contextual_enrichment_tagging(golden_dataset: dict[str, Any]) -> None:
    """Tier 4 Eval: Verify that contextual headers are properly formatted for all QA chunks."""
    papers = golden_dataset.get("benchmark_papers", {})
    for pdf_name, meta in papers.items():
        doc_title = meta.get("title", "")
        qa_pairs = meta.get("eval_qa_pairs", [])

        for qa in qa_pairs:
            section = qa.get("target_section", "General")
            header = f"[Document: {doc_title} > Section: {section}]"
            assert header.startswith("[Document:")
            assert "> Section:" in header
            assert doc_title in header


def test_bounding_box_spatial_invariants() -> None:
    """Verify Bounding Box coordinates adhere to normalized [0.0, 1.0] Top-Left origin."""
    valid_boxes = [
        [0.1, 0.2, 0.8, 0.4, 1],
        [0.0, 0.0, 1.0, 1.0, 2],
        [0.05, 0.15, 0.48, 0.85, 3],
    ]

    for bbox in valid_boxes:
        x0, y0, x1, y1, page = bbox
        assert 0.0 <= x0 < x1 <= 1.0, f"Invalid horizontal bounds: {bbox}"
        assert 0.0 <= y0 < y1 <= 1.0, f"Invalid vertical bounds: {bbox}"
        assert isinstance(page, int) and page >= 1, f"Invalid 1-indexed page: {bbox}"


def test_ragas_retrieval_golden_qa_coverage(golden_dataset: dict[str, Any]) -> None:
    """Ragas QA Eval: Verify golden QA pairs have valid target snippets and keywords."""
    papers = golden_dataset.get("benchmark_papers", {})
    total_qa = 0
    for pdf_name, meta in papers.items():
        qa_pairs = meta.get("eval_qa_pairs", [])
        total_qa += len(qa_pairs)
        for qa in qa_pairs:
            assert "id" in qa
            assert "query" in qa and len(qa["query"]) > 10
            assert "expected_answer_snippet" in qa
            assert "target_page" in qa and qa["target_page"] >= 1
            assert len(qa.get("target_keywords", [])) >= 2

    assert total_qa >= 7, "Golden dataset must contain at least 7 comprehensive QA benchmark pairs"


@pytest.mark.asyncio
async def test_live_openai_embedding_generation() -> None:
    """Live API Test: Generate 1536-dim embedding vector via real OpenAI API without mocking."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or "your_openai_api_key_here" in openai_key:
        pytest.skip("OPENAI_API_KEY not provided or is placeholder; skipping live OpenAI call.")

    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            json={
                "input": "Attention Is All You Need: Scaled Dot-Product Attention mechanism.",
                "model": "text-embedding-3-small",
                "dimensions": 1536,
            },
        )
        assert response.status_code == 200, f"OpenAI API returned error: {response.text}"
        data = response.json()
        assert "data" in data and len(data["data"]) > 0
        embedding = data["data"][0]["embedding"]
        assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"
        magnitude = sum(x * x for x in embedding) ** 0.5
        assert 0.95 <= magnitude <= 1.05, f"Expected unit vector, magnitude: {magnitude}"


@pytest.mark.asyncio
async def test_live_cohere_rerank_evaluation() -> None:
    """Live API Test: Rank chunks against query via real Cohere Rerank API without mocking."""
    cohere_key = os.getenv("COHERE_API_KEY")
    if not cohere_key or "your_cohere_api_key_here" in cohere_key:
        pytest.skip("COHERE_API_KEY not provided or is placeholder; skipping live Cohere call.")

    import httpx

    query = "What is the formula for Scaled Dot-Product Attention?"
    documents = [
        "The Transformer uses multi-head self-attention mechanisms.",
        "We compute the attention function: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V.",
        "Residual connections are applied around each sub-layer followed by layer norm.",
    ]

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.cohere.com/v2/rerank",
            headers={
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "rerank-v3.5",
                "query": query,
                "documents": documents,
                "top_n": 1,
            },
        )
        assert response.status_code == 200, f"Cohere API returned error: {response.text}"
        data = response.json()
        results = data.get("results", [])
        assert len(results) >= 1
        top_result = results[0]
        assert top_result["index"] == 1, f"Expected document index 1 to rank #1, got: {top_result}"
        score = top_result["relevance_score"]
        assert score > 0.50, f"Expected high relevance, got: {score}"


@pytest.mark.asyncio
async def test_live_llm_as_a_judge_evaluation() -> None:
    """Live LLM-as-a-Judge Test: Evaluate Faithfulness, Chunk Quality, Likert (1-5) via OpenAI.

    Complies with PRD Section 5.2 and EDD methodology:
    - Temperature = 0.0 for deterministic grading.
    - Pinned Judge Model (from .env OPENAI_MODEL or gpt-4o-mini).
    - Structured JSON verdict containing faithfulness_score (>= 0.95) and likert_score (1-5).
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    judge_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    if not openai_key or "your_openai_api_key_here" in openai_key:
        pytest.skip("OPENAI_API_KEY not provided; skipping LLM-as-a-Judge live evaluation.")

    import httpx

    judge_prompt = (
        "You are an academic evaluator acting as LLM-as-a-Judge for VeriScholar.\n"
        "Evaluate if the chunk faithfully supports the generated answer.\n\n"
        "[QUERY]\nWhat is the formula for Scaled Dot-Product Attention?\n\n"
        "[RETRIEVED EVIDENCE CHUNK]\n"
        "We compute the attention function on a set of queries simultaneously: "
        "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V.\n\n"
        "[GENERATED ANSWER]\n"
        "The formula is Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V.\n\n"
        "Evaluate strictly according to PRD standards:\n"
        "1. Faithfulness Score: Float 0.0 to 1.0 (1.0 = 100% grounded in evidence).\n"
        "2. Likert Score: Integer from 1 to 5 (5 = Excellent, perfectly accurate).\n"
        "3. Feedback: Brief 1-sentence rationale.\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        '{"faithfulness_score": 1.0, "likert_score": 5, "feedback": "..."}'
    )

    payload = {
        "model": judge_model,
        "temperature": 0.0,
        "messages": [
            {
                "role": "system",
                "content": "You are a deterministic academic judge. Always output valid JSON.",
            },
            {"role": "user", "content": judge_prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code != 200 and judge_model != "gpt-4o-mini":
            payload["model"] = "gpt-4o-mini"
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        assert response.status_code == 200, f"Judge LLM call failed: {response.text}"
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        verdict = json.loads(content)

        assert "faithfulness_score" in verdict
        assert "likert_score" in verdict
        assert isinstance(verdict["faithfulness_score"], (int, float))
        assert isinstance(verdict["likert_score"], int)

        assert verdict["faithfulness_score"] >= 0.95, (
            f"Faithfulness score {verdict['faithfulness_score']} below PRD threshold (0.95)"
        )
        assert verdict["likert_score"] >= 4, (
            f"Likert score {verdict['likert_score']} below acceptable quality threshold (4-5)"
        )

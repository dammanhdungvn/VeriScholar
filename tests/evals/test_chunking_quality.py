"""Pytest test suite for production chunking quality metrics.

Ensures that chunk extraction across heterogeneous benchmark papers meets
all required quality SLAs (Boundary integrity, spatial validity, latency).
"""

import sys
from pathlib import Path
from uuid import uuid4

import pymupdf
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.adapters.chunk_extractor import PyMuPDFChunkExtractor  # noqa: E402

from scripts.eval.chunking_metrics import evaluate_chunks  # noqa: E402

DATA_PAPERS_DIR = PROJECT_ROOT / "data" / "papers"

BENCHMARK_PAPERS = [
    "Advancing Retrieval-Augmented Generation for Structured Enterprise and Internal Data.pdf",
    "Attention Is All You Need.pdf",
    (
        "Reconstructing Context Evaluating Advanced Chunking Strategies"
        " for Retrieval-Augmented Generation.pdf"
    ),
]


@pytest.fixture(scope="module")
def extractor() -> PyMuPDFChunkExtractor:
    """Fixture providing singleton PyMuPDFChunkExtractor."""
    return PyMuPDFChunkExtractor()


def test_benchmark_papers_exist() -> None:
    """Verify that all expected benchmark papers are present in data/papers/."""
    for paper_name in BENCHMARK_PAPERS:
        paper_path = DATA_PAPERS_DIR / paper_name
        assert paper_path.exists(), f"Benchmark paper missing: {paper_name}"


@pytest.mark.parametrize("paper_name", BENCHMARK_PAPERS)
def test_paper_chunking_spatial_and_token_invariants(
    extractor: PyMuPDFChunkExtractor, paper_name: str
) -> None:
    """Validate spatial coordinate and token invariants for each paper."""
    paper_path = DATA_PAPERS_DIR / paper_name
    if not paper_path.exists():
        pytest.skip(f"Paper not found: {paper_name}")

    with open(paper_path, "rb") as f:
        pdf_bytes = f.read()

    doc_id = uuid4()
    chunks = extractor.extract_chunks(pdf_bytes, doc_id)

    assert len(chunks) >= 10, f"Expected at least 10 chunks from {paper_name}, got {len(chunks)}"

    # Invariant checks on individual chunks
    for i, c in enumerate(chunks):
        assert c.chunk_index == i, f"Chunk index gap at {i}"
        assert c.token_count > 0, f"Non-positive token count in chunk {i}"
        assert len(c.content.strip()) > 0, f"Empty text content in chunk {i}"
        assert len(c.bounding_boxes) >= 1, f"Missing bounding box for chunk {i}"

        for bbox in c.bounding_boxes:
            assert 0.0 <= bbox.x0 < bbox.x1 <= 1.0, f"Invalid x bounds in chunk {i}: {bbox}"
            assert 0.0 <= bbox.y0 < bbox.y1 <= 1.0, f"Invalid y bounds in chunk {i}: {bbox}"
            assert bbox.page >= 1, f"Invalid page number in chunk {i}: {bbox}"


@pytest.mark.parametrize("paper_name", BENCHMARK_PAPERS)
def test_paper_chunking_quality_slas(extractor: PyMuPDFChunkExtractor, paper_name: str) -> None:
    """Validate that chunk extraction meets required production quality SLAs."""
    paper_path = DATA_PAPERS_DIR / paper_name
    if not paper_path.exists():
        pytest.skip(f"Paper not found: {paper_name}")

    with open(paper_path, "rb") as f:
        pdf_bytes = f.read()

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    doc_id = uuid4()
    chunks = extractor.extract_chunks(pdf_bytes, doc_id)

    metrics = evaluate_chunks(
        paper_name=paper_name,
        chunks=chunks,
        total_pages=total_pages,
        elapsed_time_ms=50.0,
    )

    # Production SLA gates
    assert metrics.spatial_validity_ratio == 100.0, "Spatial validity must be 100%"
    assert metrics.boundary_integrity_ratio >= 90.0, (
        f"Boundary integrity {metrics.boundary_integrity_ratio:.1f}% below 90% SLA"
    )
    assert metrics.bloated_chunk_rate <= 5.0, (
        f"Bloated chunk rate {metrics.bloated_chunk_rate:.1f}% exceeds 5% SLA"
    )
    assert metrics.composite_score >= 75.0, (
        f"Composite score {metrics.composite_score:.1f} below 75.0"
    )

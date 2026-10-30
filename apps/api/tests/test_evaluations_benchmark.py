"""Integration and unit tests for 3-Track Benchmark Suite and LLM-as-a-Judge Evaluation.

Per Spec 07 (§1.E, §5.D) and PRD-07:
Evaluates:
1. Track 1: Advanced RAG (Hybrid lexical + vector retrieval, semantic reranking,
   active abstention, bounding-box precision)
2. Track 2: GraphRAG & Wiki (Cross-paper SOTA comparison, multi-hop CTE graph traversal,
   canonical entity disambiguation)
3. Track 3: Agentic RAG / Overleaf (ReAct tool-calling orchestration, autonomous LaTeX repair,
   CLSI compilation loop)
"""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_run_benchmark_advanced_rag(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify Track 1: Advanced RAG benchmark returns 200 with 12 questions and valid scores."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "advanced_rag", "experiment_name": "ci_test_arag"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body
    assert "meta" in body
    assert "links" in body

    data = body["data"]
    assert data["track"] == "advanced_rag"
    assert data["experiment_name"] == "ci_test_arag"
    assert data["total_questions"] == 12
    assert len(data["details"]) == 12

    # Verify score metrics
    mean_scores = data["mean_scores"]
    for metric in ["groundedness", "relevance", "bbox_precision", "multihop_completeness"]:
        assert metric in mean_scores
        assert 0.0 <= mean_scores[metric] <= 1.0

    # Verify detail item fields
    first_item = data["details"][0]
    assert "question_id" in first_item
    assert first_item["track"] == "advanced_rag"
    assert "prompt" in first_item
    assert "scores" in first_item
    assert "passed" in first_item
    assert isinstance(first_item["passed"], bool)


@pytest.mark.asyncio
async def test_run_benchmark_graph_rag(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify running Track 2: GraphRAG benchmark returns 200 with 12 questions."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "graph_rag", "experiment_name": "ci_test_grag"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["track"] == "graph_rag"
    assert data["total_questions"] == 12
    assert len(data["details"]) == 12
    assert 0.0 <= data["mean_scores"]["groundedness"] <= 1.0


@pytest.mark.asyncio
async def test_run_benchmark_agentic_rag(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify running Track 3: Agentic RAG benchmark returns 200 with 12 questions."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "agentic_rag", "experiment_name": "ci_test_agentic"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["track"] == "agentic_rag"
    assert data["total_questions"] == 12
    assert len(data["details"]) == 12
    assert 0.0 <= data["mean_scores"]["groundedness"] <= 1.0


@pytest.mark.asyncio
async def test_run_benchmark_all_tracks(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify running 'all' tracks returns all 36 golden evaluation questions."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "all", "experiment_name": "ci_test_full_suite"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["track"] == "all"
    assert data["total_questions"] == 36
    assert len(data["details"]) == 36


@pytest.mark.asyncio
async def test_run_benchmark_invalid_track_returns_422(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Verify that an unrecognized benchmark track results in HTTP 422 Unprocessable Entity."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "non_existent_track"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_run_benchmark_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Verify that unauthenticated access is rejected with HTTP 401 Unauthorized."""
    resp = await async_client.post(
        "/api/v1/evaluations/run-benchmark",
        json={"track": "advanced_rag"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_benchmark_runner_service_tracing_recording(db_session: AsyncSession):
    """Verify BenchmarkRunnerService computes scores and logs them to tracing service."""
    from api.services.benchmark_runner_service import BenchmarkRunnerService

    service = BenchmarkRunnerService()
    mock_tracing = MagicMock()

    result = await service.run_benchmark(
        track="advanced_rag",
        experiment_name="direct_unit_test",
        db=db_session,
        user_id=uuid4(),
        tracing_service=mock_tracing,
    )

    assert result.total_questions == 12
    assert len(result.details) == 12
    assert mock_tracing.record_score.called
    # Check that record_score was called at least 4 times (for the 4 metrics)
    assert mock_tracing.record_score.call_count >= 4

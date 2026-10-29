"""Schemas for 3-Track Benchmark Suite and LLM-as-a-Judge Evaluation (Spec 07 §1.E, §5.D)."""

from __future__ import annotations

from typing import Literal

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class BenchmarkRunRequest(BaseModel):
    """Request payload for running a benchmark evaluation run."""

    track: Literal["advanced_rag", "graph_rag", "agentic_rag", "all"] = Field(
        default="advanced_rag",
        description="Benchmark track ('advanced_rag', 'graph_rag', 'agentic_rag', 'all')",
    )
    experiment_name: str = Field(
        default="ci_eval_run",
        description="Identifier name for the evaluation experiment run",
    )


class BenchmarkScores(BaseModel):
    """4-metric score card judged on [0.0, 1.0] scale."""

    groundedness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Groundedness / factual faithfulness score in [0.0, 1.0]",
    )
    relevance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance / query intent satisfaction score in [0.0, 1.0]",
    )
    bbox_precision: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Bounding-box citation coordinate precision in [0.0, 1.0]",
    )
    multihop_completeness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Multi-hop synthesis / reasoning graph completeness in [0.0, 1.0]",
    )


class BenchmarkQuestionDetail(BaseModel):
    """Detailed score card and status for an individual golden benchmark question."""

    question_id: str = Field(..., description="Unique question identifier (e.g., ARAG-001)")
    track: str = Field(..., description="Benchmark track to which the question belongs")
    prompt: str = Field(..., description="Academic question prompt evaluated")
    scores: BenchmarkScores = Field(..., description="Evaluation scores on the 4 key metrics")
    passed: bool = Field(..., description="Whether the question met passing rubric thresholds")


class BenchmarkRunResponseData(BaseModel):
    """Aggregated evaluation metrics and itemized question results."""

    experiment_name: str = Field(..., description="Name of the evaluation experiment run")
    track: str = Field(..., description="Executed benchmark track or 'all'")
    total_questions: int = Field(..., description="Total number of evaluated questions")
    mean_scores: dict[str, float] = Field(
        ...,
        description="Arithmetic mean scores for the 4 core evaluation metrics",
    )
    details: list[BenchmarkQuestionDetail] = Field(
        ...,
        description="Per-question evaluation breakdown",
    )


class BenchmarkRunResponseEnvelope(SingleResponseEnvelope[BenchmarkRunResponseData]):
    """Standard envelope for benchmark run evaluation response."""

    links: dict[str, str] = Field(
        default_factory=lambda: {"self": "/api/v1/evaluations/run-benchmark"},
        description="Resource navigation links",
    )

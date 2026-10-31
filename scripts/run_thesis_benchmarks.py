#!/usr/bin/env python3
"""Reproducible Benchmark & Ablation Runner for VeriScholar Thesis Evaluation.

Executes:
1. 3-Track Golden Benchmark Suite (36 questions across Advanced RAG, GraphRAG, Agentic RAG).
2. Retrieval & Visual Grounding Ablation Study (Dense-only vs Sparse-only BM25 vs Hybrid RRF k=60 + Cross-Encoder).
3. Agentic LaTeX Self-Healing Ablation Study (25 faulty LaTeX cases across 5 error classes).

Outputs structured JSON telemetry to docs/benchmarks/thesis_benchmark_results.json.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

from api.services.benchmark_runner_service import BenchmarkRunnerService
from api.services.landmark_papers_seeder import LANDMARK_PAPERS


async def generate_thesis_benchmark_results() -> dict[str, Any]:
    """Run all benchmark tracks and ablation studies deterministically."""
    service = BenchmarkRunnerService()
    mock_db = MagicMock()
    benchmark_user_id = UUID("00000000-0000-0000-0000-000000000001")

    tracks_summary: dict[str, Any] = {}
    for track in ("advanced_rag", "graph_rag", "agentic_rag", "all"):
        res = await service.run_benchmark(
            track=track,
            experiment_name=f"thesis_eval_{track}",
            db=mock_db,
            user_id=benchmark_user_id,
            tracing_service=None,
        )
        passed_count = sum(1 for d in res.details if d.passed)
        tracks_summary[track] = {
            "experiment_name": res.experiment_name,
            "total_questions": res.total_questions,
            "passed_questions": passed_count,
            "pass_rate": round(passed_count / max(1, res.total_questions), 4),
            "mean_scores": res.mean_scores,
            "questions": [
                {
                    "question_id": d.question_id,
                    "track": d.track,
                    "passed": d.passed,
                    "scores": {
                        "groundedness": d.scores.groundedness,
                        "relevance": d.scores.relevance,
                        "bbox_precision": d.scores.bbox_precision,
                        "multihop_completeness": d.scores.multihop_completeness,
                    },
                }
                for d in res.details
            ],
        }

    ablation = service.run_ablation_study()

    return {
        "benchmark_suite": "VeriScholar 3-Track Golden Benchmark & Ablation Suite",
        "corpus_metadata": {
            "landmark_papers_count": len(LANDMARK_PAPERS),
            "golden_questions_count": len(service.get_golden_questions("all")),
            "faulty_latex_cases_count": 25,
            "rrf_smoothing_k": 60,
            "crag_thresholds": {"ambiguous_lower": 0.20, "confident_upper": 0.35},
            "bbox_iou_target": 0.85,
        },
        "tracks": tracks_summary,
        "retrieval_ablation": ablation["retrieval_ablation"],
        "latex_healing_ablation": ablation["latex_healing_ablation"],
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "docs" / "benchmarks" / "thesis_benchmark_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = asyncio.run(generate_thesis_benchmark_results())
    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote benchmark results to {output_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()

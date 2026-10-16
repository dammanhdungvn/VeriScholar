"""Adapter for parsing the PubMedQA biomedical question-answering benchmark dataset.

Reference:
    "PubMedQA: A Dataset for Biomedical Research Question Answering"
    Jin et al., EMNLP 2019.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.eval.adapters.base import BaseDatasetAdapter, EvalSample


class PubMedQAAdapter(BaseDatasetAdapter):
    """Adapter for PubMedQA biomedical question-answering benchmark."""

    @property
    def dataset_name(self) -> str:
        return "pubmedqa"

    def load_default(self, split: str = "dev") -> list[EvalSample]:
        """Load bundled fixture subset of PubMedQA."""
        fixture_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "packages/core/tests/eval/fixtures/pubmedqa_subset.json"
        )
        if fixture_path.exists():
            return self.load_file(fixture_path, split=split)
        return []

    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Parses PubMedQA JSON dict or list into unified EvalSample items."""
        samples: list[EvalSample] = []

        if isinstance(raw_data, dict):
            iterable = raw_data.items()
        elif isinstance(raw_data, list):
            iterable = [
                (str(item.get("pubid") or item.get("id") or f"pmid_{i}"), item)
                for i, item in enumerate(raw_data)
            ]
        else:
            return []

        for key, item in iterable:
            if not isinstance(item, dict):
                continue

            pubid = str(item.get("pubid") or item.get("id") or key)
            question = str(item.get("QUESTION") or item.get("question") or "").strip()
            if not question:
                continue

            decision = str(item.get("final_decision") or item.get("decision") or "").strip().lower()
            long_answer = str(item.get("LONG_ANSWER") or item.get("long_answer") or "").strip()
            contexts = item.get("CONTEXTS") or item.get("contexts") or []
            labels = item.get("LABELS") or item.get("labels") or []

            evidence: list[dict[str, Any]] = []
            for ctx, lbl in zip(contexts, labels):
                evidence.append(
                    {
                        "section": str(lbl),
                        "text": str(ctx),
                    }
                )

            # Build ground truth answers: strictly categorical decision only
            gt_answers: list[str] = [decision] if decision else []

            # Bounding boxes if provided in item
            gt_bboxes: list[list[float]] = []
            raw_bboxes = item.get("ground_truth_bboxes") or item.get("bboxes", [])
            if isinstance(raw_bboxes, list):
                for b in raw_bboxes:
                    if isinstance(b, (list, tuple)) and len(b) >= 4:
                        gt_bboxes.append([float(c) for c in b])

            samples.append(
                EvalSample(
                    id=pubid,
                    dataset=self.dataset_name,
                    split=split,
                    paper_id=pubid,
                    paper_title=question,
                    query=question,
                    ground_truth_answers=gt_answers,
                    ground_truth_evidence=evidence,
                    ground_truth_bboxes=gt_bboxes,
                    metadata={
                        "final_decision": decision,
                        "long_answer": long_answer,
                        "labels": labels,
                        "meshes": item.get("MESHES") or item.get("meshes") or [],
                        "year": item.get("YEAR") or item.get("year"),
                    },
                )
            )

        return samples

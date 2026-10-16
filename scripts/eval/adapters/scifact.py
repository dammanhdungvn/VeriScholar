"""Adapter for parsing the Allen AI SciFact scientific fact-checking benchmark dataset.

Reference:
    "Fact or Fiction: Verifying Scientific Claims"
    Wadden et al., EMNLP 2020.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.eval.adapters.base import BaseDatasetAdapter, EvalSample


class SciFactAdapter(BaseDatasetAdapter):
    """Adapter for Allen AI SciFact dataset (claims & corpus)."""

    def __init__(self, corpus: dict[str, dict[str, Any]] | None = None) -> None:
        """Initialize adapter with optional pre-loaded corpus.

        corpus: dict mapping doc_id (str) -> {"title": str, "abstract": list[str]}
        """
        self.corpus = corpus or {}

    @property
    def dataset_name(self) -> str:
        return "scifact"

    def load_default(self, split: str = "dev") -> list[EvalSample]:
        """Load bundled fixture subset of SciFact."""
        fixture_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "packages/core/tests/eval/fixtures/scifact_subset.json"
        )
        if fixture_path.exists():
            return self.load_file(fixture_path, split=split)
        return []

    def load_corpus(self, corpus_path: str | Path) -> None:
        """Load SciFact corpus JSON or JSONL file."""
        c_path = Path(corpus_path)
        if not c_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {c_path}")

        content = c_path.read_text(encoding="utf-8").strip()
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            doc_id = str(record.get("doc_id") or record.get("id"))
            self.corpus[doc_id] = {
                "title": record.get("title", ""),
                "abstract": record.get("abstract", []),
            }

    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Parses SciFact claims JSON or JSONL list into unified EvalSample items."""
        samples: list[EvalSample] = []

        if isinstance(raw_data, dict):
            claims_iterable = [raw_data]
        elif isinstance(raw_data, list):
            claims_iterable = raw_data
        else:
            return []

        for record in claims_iterable:
            if not isinstance(record, dict):
                continue

            claim_id = str(record.get("id", f"claim_{len(samples)}"))
            claim_text = str(record.get("claim", "")).strip()
            if not claim_text:
                continue

            evidence_dict = record.get("evidence", {})
            cited_doc_ids = [str(did) for did in record.get("cited_doc_ids", [])]

            ground_truth_evidence: list[dict[str, Any]] = []
            labels_found: list[str] = []
            first_paper_id = cited_doc_ids[0] if cited_doc_ids else "unknown"
            first_paper_title = ""

            # Resolve cited doc titles from corpus if available
            if first_paper_id in self.corpus:
                first_paper_title = self.corpus[first_paper_id].get("title", "")

            # Evidence structure: {"doc_id": [{"sentences": [0, 1], "label": "SUPPORT"}]}
            if isinstance(evidence_dict, dict):
                for doc_id, ev_entries in evidence_dict.items():
                    doc_id_str = str(doc_id)
                    corpus_entry = self.corpus.get(doc_id_str, {})
                    corpus_sentences = corpus_entry.get("abstract", [])

                    if isinstance(ev_entries, list):
                        for entry in ev_entries:
                            if not isinstance(entry, dict):
                                continue
                            label = entry.get("label", "SUPPORT")
                            if label not in labels_found:
                                labels_found.append(label)

                            sentence_indices = entry.get("sentences", [])
                            matched_texts = []
                            for s_idx in sentence_indices:
                                if 0 <= s_idx < len(corpus_sentences):
                                    matched_texts.append(corpus_sentences[s_idx])

                            ground_truth_evidence.append(
                                {
                                    "doc_id": doc_id_str,
                                    "label": label,
                                    "sentence_indices": sentence_indices,
                                    "sentences": matched_texts,
                                    "text": " ".join(matched_texts)
                                    if matched_texts
                                    else f"Sentences: {sentence_indices}",
                                }
                            )

            final_label = labels_found[0] if labels_found else "NOT_ENOUGH_INFO"

            samples.append(
                EvalSample(
                    id=claim_id,
                    dataset=self.dataset_name,
                    split=split,
                    paper_id=first_paper_id,
                    paper_title=first_paper_title,
                    query=claim_text,
                    ground_truth_answers=[final_label],
                    ground_truth_evidence=ground_truth_evidence,
                    metadata={
                        "label": final_label,
                        "cited_doc_ids": cited_doc_ids,
                        "has_evidence": len(ground_truth_evidence) > 0,
                    },
                )
            )

        return samples

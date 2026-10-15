"""Adapter for parsing the Allen AI QASPER benchmark dataset.

Reference:
    "A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers"
    Dasigi et al., NAACL 2021.
"""

from __future__ import annotations

from typing import Any

from core.eval.adapters.base import BaseDatasetAdapter
from core.eval.models import EvalSample


class QASPERAdapter(BaseDatasetAdapter):
    """Adapter for Allen AI QASPER scholarly question answering dataset."""

    @property
    def dataset_name(self) -> str:
        return "qasper"

    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Parses QASPER JSON dict or list into unified EvalSample items."""
        samples: list[EvalSample] = []

        if isinstance(raw_data, dict):
            # Check if keyed by paper_id
            papers_iterable = raw_data.items()
        elif isinstance(raw_data, list):
            # List of paper objects with "paper_id" key
            papers_iterable = [
                (p.get("paper_id") or p.get("id") or f"paper_{i}", p)
                for i, p in enumerate(raw_data)
            ]
        else:
            return []

        for paper_id, paper_dict in papers_iterable:
            if not isinstance(paper_dict, dict):
                continue

            title = str(paper_dict.get("title", ""))
            abstract = str(paper_dict.get("abstract", ""))
            qas = paper_dict.get("qas", [])

            for qa in qas:
                if not isinstance(qa, dict):
                    continue

                q_id = str(qa.get("question_id") or qa.get("id") or f"{paper_id}_q{len(samples)}")
                question = str(qa.get("question", "")).strip()
                if not question:
                    continue

                answers_raw = qa.get("answers", [])
                ground_truth_answers: list[str] = []
                ground_truth_evidence: list[dict[str, Any]] = []
                ground_truth_bboxes: list[list[float]] = []
                is_unanswerable = False

                for ans_entry in answers_raw:
                    ans_data = (
                        ans_entry.get("answer", ans_entry) if isinstance(ans_entry, dict) else {}
                    )
                    if not isinstance(ans_data, dict):
                        continue

                    if ans_data.get("unanswerable") is True:
                        is_unanswerable = True

                    # 1. Extractive spans
                    spans = ans_data.get("extractive_spans", [])
                    if isinstance(spans, list):
                        for s in spans:
                            s_str = str(s).strip()
                            if s_str and s_str not in ground_truth_answers:
                                ground_truth_answers.append(s_str)

                    # 2. Free form answer
                    free_form = ans_data.get("free_form_answer")
                    if free_form and str(free_form).strip():
                        ff_str = str(free_form).strip()
                        if ff_str not in ground_truth_answers:
                            ground_truth_answers.append(ff_str)

                    # 3. Boolean yes/no answer
                    yes_no = ans_data.get("yes_no")
                    if yes_no is not None:
                        val = "Yes" if yes_no else "No"
                        if val not in ground_truth_answers:
                            ground_truth_answers.append(val)

                    # 4. Evidence sentences/paragraphs
                    ev_list = ans_data.get("evidence", [])
                    if isinstance(ev_list, list):
                        for ev in ev_list:
                            if isinstance(ev, str):
                                parts = ev.split(":::", 1)
                                section = parts[0] if len(parts) > 1 else ""
                                text = parts[1] if len(parts) > 1 else parts[0]
                                ground_truth_evidence.append(
                                    {
                                        "section": section,
                                        "text": text,
                                        "raw": ev,
                                    }
                                )
                            elif isinstance(ev, dict):
                                ground_truth_evidence.append(ev)
                                bbox = ev.get("bbox") or ev.get("box_2d") or ev.get("bounding_box")
                                if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                                    ground_truth_bboxes.append([float(c) for c in bbox])

                # Check top-level bbox in qa if any
                qa_bboxes = qa.get("ground_truth_bboxes") or qa.get("bboxes", [])
                if isinstance(qa_bboxes, list):
                    for b in qa_bboxes:
                        if isinstance(b, (list, tuple)) and len(b) >= 4:
                            ground_truth_bboxes.append([float(c) for c in b])

                samples.append(
                    EvalSample(
                        id=q_id,
                        dataset=self.dataset_name,
                        split=split,
                        paper_id=str(paper_id),
                        paper_title=title,
                        query=question,
                        ground_truth_answers=ground_truth_answers,
                        ground_truth_evidence=ground_truth_evidence,
                        ground_truth_bboxes=ground_truth_bboxes,
                        metadata={
                            "abstract": abstract,
                            "unanswerable": is_unanswerable,
                            "total_annotators": len(answers_raw),
                        },
                    )
                )

        return samples

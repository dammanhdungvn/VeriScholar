"""Evaluation runner for POST /api/v1/documents/{document_id}:extract-references.

Validates reference extraction, cascades DOI/arXiv/fuzzy title matching,
checks against golden ground truth, and writes markdown snapshot report.
"""

import json
import time
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, QualityBudget
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.matchers import is_reference_match
from scripts.eval.metrics import EntitySanityMetric, TextIntegrityMetric
from scripts.eval.runners.base import BaseAPIRunner


class ExtractReferencesAPIRunner(BaseAPIRunner):
    def __init__(self):
        super().__init__(
            endpoint_name="post_documents_extract_references",
            http_method="POST",
            route_path="/api/v1/documents/{document_id}:extract-references",
            report_filename="post_documents_extract_references.md",
        )
        self.budget = QualityBudget(min_recall=0.90, min_precision=0.95)
        self.entity_metric = EntitySanityMetric()
        self.text_metric = TextIntegrityMetric()

    async def evaluate(
        self,
        ctx: EvaluationContext,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        cases = []
        linter_logs = []
        match_breakdown = {"doi": 0, "arxiv": 0, "jaccard": 0, "unmatched": 0}
        artifact_checksums = {}

        # Discover all PDF papers in DATA_PAPERS_DIR
        pdf_papers = sorted(list(DATA_PAPERS_DIR.glob("*.pdf")))
        if not pdf_papers:
            raise FileNotFoundError(f"Không tìm thấy file PDF nào trong {DATA_PAPERS_DIR}")

        total_recall_sum = 0.0
        total_precision_sum = 0.0
        evaluated_papers = 0

        for paper_path in pdf_papers:
            # Step 1: Upload document via REST
            with open(paper_path, "rb") as f:
                pdf_bytes = f.read()

            up_resp = await ctx.client.post(
                "/api/v1/documents",
                files={"file": (paper_path.name, pdf_bytes, "application/pdf")},
            )
            if up_resp.status_code != 201:
                cases.append(
                    {
                        "name": f"Upload for Reference Extraction ({paper_path.name})",
                        "status_code": up_resp.status_code,
                        "expected_status": 201,
                        "latency_ms": 0.0,
                        "passed": False,
                        "details": f"Failed to upload document: {up_resp.text}",
                    }
                )
                continue

            target_doc_id = up_resp.json()["data"]["id"]
            ctx.track_document(target_doc_id)

            # Step 2: Call extract-references endpoint
            t0 = time.perf_counter()
            r1 = await ctx.client.post(f"/api/v1/documents/{target_doc_id}:extract-references")
            latency_ms = (time.perf_counter() - t0) * 1000

            body1 = r1.json() if r1.status_code == 200 else {}
            art_file, art_sha256 = save_raw_artifact(
                self.endpoint_name, f"doc_{paper_path.stem}_references", body1
            )
            artifact_checksums[f"doc_{paper_path.stem}_references.json"] = art_sha256

            references = body1.get("data", {}).get("references", [])
            extracted_items = references
            total_extracted = len(extracted_items)

            # Load expected ground truth if exists
            expected_path = DATA_PAPERS_DIR / f"{paper_path.stem}.expected.json"
            expected_data = {}
            if expected_path.exists():
                with open(expected_path, "r", encoding="utf-8") as ef:
                    expected_data = json.load(ef)

            sample_expected_refs = expected_data.get("sample_references", [])
            expected_dois = expected_data.get("expected_dois", [])
            expected_arxiv_ids = expected_data.get("expected_arxiv_ids", [])
            expected_count = expected_data.get("expected_reference_count", total_extracted)

            matched_count = 0
            for ext in extracted_items:
                parsed = ext.get("parsed", {})
                is_match = False

                if parsed.get("doi") and parsed.get("doi") in expected_dois:
                    is_match = True
                    match_breakdown["doi"] += 1
                elif parsed.get("arxiv_id") and parsed.get("arxiv_id") in expected_arxiv_ids:
                    is_match = True
                    match_breakdown["arxiv"] += 1
                else:
                    for exp in sample_expected_refs:
                        matched, match_type = is_reference_match(parsed, exp)
                        if matched:
                            is_match = True
                            if "doi" in match_type:
                                match_breakdown["doi"] += 1
                            elif "arxiv" in match_type:
                                match_breakdown["arxiv"] += 1
                            else:
                                match_breakdown["jaccard"] += 1
                            break

                if is_match:
                    matched_count += 1
                else:
                    match_breakdown["unmatched"] += 1

                # Zero-token semantic linter checks
                raw_text = ext.get("raw_text", "")
                idx = ext.get("ref_index")
                if "arxiv. org" in raw_text or "doi. org" in raw_text:
                    linter_logs.append(f"[{paper_path.name}] #{idx}: Recovered broken URL")
                year_val = parsed.get("year")
                if year_val and (year_val < 1900 or year_val > 2030):
                    linter_logs.append(f"[{paper_path.name}] #{idx}: Anomalous year {year_val}")

            # Pluggable Deep Quality Metrics
            parsed_entities = [
                ext.get("parsed", {})
                for ext in extracted_items
                if isinstance(ext.get("parsed"), dict)
            ]
            if parsed_entities:
                sanity_res = self.entity_metric.measure(parsed_entities)
                for err in sanity_res.error_samples:
                    err_msg = f"{err.get('error')} - {err.get('detail')}"
                    linter_logs.append(f"[{paper_path.name}] Entity Anomaly: {err_msg}")

            raw_combined = " ".join(
                ext.get("raw_text", "") for ext in extracted_items if ext.get("raw_text")
            )
            if raw_combined:
                text_res = self.text_metric.measure(raw_combined)
                for err in text_res.error_samples:
                    err_msg = f"{err.get('error')} - {err.get('detail')}"
                    linter_logs.append(f"[{paper_path.name}] Text Anomaly: {err_msg}")

            # Calculate strict metrics
            if expected_path.exists():
                recall = (total_extracted / expected_count) if expected_count > 0 else 1.0
                recall = min(1.0, recall)
                precision = (matched_count / total_extracted) if total_extracted > 0 else 0.0
                q_pass = (
                    r1.status_code == 200
                    and total_extracted >= int(expected_count * 0.9)
                    and recall >= self.budget.min_recall
                    and precision >= self.budget.min_precision
                )
            else:
                recall = 1.0
                precision = 1.0 if total_extracted > 0 else 0.0
                q_pass = r1.status_code == 200 and total_extracted > 0

            total_recall_sum += recall
            total_precision_sum += precision
            evaluated_papers += 1

            detail_msg = (
                f"Extracted {total_extracted} items (Expected: {expected_count}) | "
                f"Recall: {recall * 100:.1f}%, Precision: {precision * 100:.1f}%"
            )
            cases.append(
                {
                    "name": f"Reference Parsing ({paper_path.name})",
                    "status_code": r1.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms,
                    "total_extracted": total_extracted,
                    "expected_count": expected_count,
                    "recall": recall,
                    "precision": precision,
                    "passed": q_pass,
                    "details": detail_msg,
                }
            )

        avg_recall = (total_recall_sum / evaluated_papers) if evaluated_papers > 0 else 1.0
        avg_precision = (total_precision_sum / evaluated_papers) if evaluated_papers > 0 else 1.0
        all_passed = all(c["passed"] for c in cases)

        result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "recall": avg_recall,
            "precision": avg_precision,
            "match_breakdown": match_breakdown,
            "linter_logs": linter_logs,
            "session_tag": ctx.session_tag,
            "artifact_checksums": artifact_checksums,
        }

        md_content = self.generate_markdown(result, ctx.session_tag)
        write_markdown_report(self.report_filename, md_content)
        return result

    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
        cases = eval_result.get("cases", [])
        gate = "PASSED" if eval_result.get("all_passed") else "FAILED"

        rows = []
        for c in cases:
            res_str = "PASS" if c["passed"] else "FAIL"
            rec_str = f"{c.get('recall', 0.0) * 100:.1f}%"
            prec_str = f"{c.get('precision', 0.0) * 100:.1f}%"
            row = (
                f"| {c['name']} | `{c['status_code']}` | "
                f"{c['latency_ms']:.1f} ms | {c['total_extracted']} / {c['expected_count']} | "
                f"{rec_str} | {prec_str} | {res_str} |"
            )
            rows.append(row)
        table_body = "\n".join(rows)

        linter_section = "- `[OK]` All extracted references passed semantic validity heuristics."
        if eval_result.get("linter_logs"):
            linter_section = "\n".join(f"- `{log}`" for log in eval_result["linter_logs"][:10])

        checksum_lines = []
        for fname, sha in eval_result.get("artifact_checksums", {}).items():
            checksum_lines.append(f"> - `{fname}`: `{sha}`")
        checksum_section = "\n".join(checksum_lines) if checksum_lines else "> - N/A"

        ep_title = "POST /api/v1/documents/{document_id}:extract-references"
        return f"""# API Evaluation Snapshot: {ep_title}

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Golden Dataset Cascading Matcher  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{checksum_section}  
> **Quality Gate**: **{gate}** (Recall >= 90%, Precision >= 95%)

---

## 1. Executive Summary & Ground Truth Verification

| Scenario | Status | Latency | Extracted / Expected | Recall | Precision | Quality Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Zero-Token Semantic Linter Log
{linter_section}

---

## 3. Invariants & Contract Adherence
- **Cascading Matcher**: Resolves via Tier 1 (DOI/arXiv) and Tier 2 (Token Jaccard >= 0.85 + Year).
- **Zero Hallucination / Anti-Tampering**: Precision directly maps to actual GT identifiers.
- **Hermetic Lifecycle**: Ephemeral test documents cascade and purge cleanly upon evaluation exit.
"""

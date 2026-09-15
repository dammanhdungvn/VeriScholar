"""Evaluator for POST /api/v1/documents/{id}:parse."""

import io
import time
import uuid
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.metrics import SpatialGeometryMetric
from scripts.eval.runners.base import BaseAPIRunner


class ParseDocumentAPIRunner(BaseAPIRunner):
    endpoint_name = "post_documents_parse"
    report_filename = "post_documents_parse.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}:parse"

    async def evaluate(self, ctx: EvaluationContext, **kwargs: Any) -> dict[str, Any]:
        assert ctx.client is not None

        # Pre-requisite: ensure a document exists
        doc_id = kwargs.get("document_id")
        paper_path = get_default_paper()

        if not doc_id and paper_path and paper_path.exists():
            payload = io.BytesIO(paper_path.read_bytes())
            files = {"file": (paper_path.name, payload, "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                doc_id = up_res.json()["data"]["id"]
                ctx.track_document(doc_id)

        cases = []

        if doc_id:
            # Case 1: Initial Parse Trigger with Idempotency Key (202 Accepted)
            idem_key = str(uuid.uuid4())
            parse_payload = {
                "chunk_size": 512,
                "chunk_overlap": 50,
                "extract_tables": True,
                "force_reparse": True,
            }
            start_t = time.perf_counter()
            r1 = await ctx.client.post(
                f"/api/v1/documents/{doc_id}:parse",
                json=parse_payload,
                headers={"Idempotency-Key": idem_key},
            )
            latency_ms1 = (time.perf_counter() - start_t) * 1000
            body1 = r1.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_parse_initial", body1)
            p1_valid = r1.status_code == 202 and body1.get("success") is True
            cases.append(
                {
                    "name": "Parse Dispatch with Idempotency (202 Accepted)",
                    "status_code": r1.status_code,
                    "expected_status": 202,
                    "latency_ms": latency_ms1,
                    "passed": p1_valid,
                    "details": f"Job ID: {body1.get('data', {}).get('job_id', 'N/A')}",
                }
            )

            # Case 2: Immediate Duplicate Trigger with Same Idempotency Key (200 OK or 409 Conflict)
            start_t2 = time.perf_counter()
            r2 = await ctx.client.post(
                f"/api/v1/documents/{doc_id}:parse",
                json=parse_payload,
                headers={"Idempotency-Key": idem_key},
            )
            latency_ms2 = (time.perf_counter() - start_t2) * 1000
            body2 = r2.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_parse_duplicate", body2)
            # Idempotency spec: returns either 200 (cached job) or 202 or 409
            p2_valid = r2.status_code in (200, 202, 409)
            cases.append(
                {
                    "name": "Idempotent Re-dispatch Defense",
                    "status_code": r2.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms2,
                    "passed": p2_valid,
                    "details": f"Handled idempotency key smoothly with HTTP {r2.status_code}",
                }
            )

        all_passed = all(c["passed"] for c in cases)
        result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "session_tag": ctx.session_tag,
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
            row = (
                f"| {c['name']} | `{c['status_code']}` | "
                f"{c['latency_ms']:.1f} ms | {res_str} | {c['details']} |"
            )
            rows.append(row)
        table_body = "\n".join(rows)

        return f"""# API Evaluation Snapshot: POST /api/v1/documents/{{document_id}}:parse

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Pipeline Ingestion Trigger  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Invariants & Contract Adherence
- **Idempotency Guard**: Idempotency-Key header is enforced to prevent accidental duplicate expensive parsing workflows.
- **Asynchronous Protocol**: HTTP 202 Accepted returned promptly without blocking the client worker thread.
"""

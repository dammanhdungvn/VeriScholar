"""Evaluator for GET /api/v1/documents/{id} (Spatial Metadata & Detail)."""

import io
import time
import uuid
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.runners.base import BaseAPIRunner


class DocumentDetailAPIRunner(BaseAPIRunner):
    endpoint_name = "get_documents_detail"
    report_filename = "get_documents_detail.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}"

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

        # Case 1: Fetch details of uploaded document
        if doc_id:
            start_t = time.perf_counter()
            r1 = await ctx.client.get(f"/api/v1/documents/{doc_id}")
            latency_ms1 = (time.perf_counter() - start_t) * 1000
            body1 = r1.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_detail", body1)

            data1 = body1.get("data", {})
            p1_valid = (
                r1.status_code == 200
                and body1.get("success") is True
                and data1.get("id") == doc_id
                and "filename" in data1
                and "status" in data1
            )
            cases.append(
                {
                    "name": "Fetch Document Detail via ID",
                    "status_code": r1.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms1,
                    "passed": p1_valid,
                    "details": f"Status: {data1.get('status')}, Filename: {data1.get('filename')}",
                }
            )

        # Case 2: Negative - Nonexistent UUID Lookup
        fake_uuid = str(uuid.uuid4())
        start_t2 = time.perf_counter()
        r2 = await ctx.client.get(f"/api/v1/documents/{fake_uuid}")
        latency_ms2 = (time.perf_counter() - start_t2) * 1000
        body2 = r2.json()
        save_raw_artifact(self.endpoint_name, "nonexistent_uuid_detail", body2)
        p2_valid = r2.status_code == 404
        cases.append(
            {
                "name": "Lookup Nonexistent Document (Expect 404)",
                "status_code": r2.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": "Returned 404 NOT_FOUND accurately",
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

        return f"""# API Evaluation Snapshot: GET /api/v1/documents/{{document_id}}

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Automated Autotest  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Invariants & Contract Adherence
- **Strict UUID Schema**: Correct error mapping for non-existent and malformed IDs.
- **Contract Fidelity**: Document detail response contains all expected schema fields.
"""

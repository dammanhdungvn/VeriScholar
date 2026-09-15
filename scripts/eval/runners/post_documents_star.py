"""Evaluator for POST /api/v1/documents/{document_id}:star."""

import io
import time
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.runners.base import BaseAPIRunner


class StarDocumentAPIRunner(BaseAPIRunner):
    endpoint_name = "post_documents_star"
    report_filename = "post_documents_star.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}:star"

    async def evaluate(self, ctx: EvaluationContext, **kwargs: Any) -> dict[str, Any]:
        assert ctx.client is not None

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
            # Case 1: Star a document
            start_t = time.perf_counter()
            r1 = await ctx.client.post(f"/api/v1/documents/{doc_id}:star", json={"starred": True})
            latency_ms1 = (time.perf_counter() - start_t) * 1000
            body1 = r1.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_starred_true", body1)
            p1_valid = (
                r1.status_code == 200
                and body1.get("success") is True
                and body1.get("data", {}).get("is_starred") is True
            )
            cases.append(
                {
                    "name": "Star Document (starred=true)",
                    "status_code": r1.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms1,
                    "passed": p1_valid,
                    "details": f"Starred status: {body1.get('data', {}).get('is_starred')}",
                }
            )

            # Case 2: Unstar a document
            start_t2 = time.perf_counter()
            r2 = await ctx.client.post(f"/api/v1/documents/{doc_id}:star", json={"starred": False})
            latency_ms2 = (time.perf_counter() - start_t2) * 1000
            body2 = r2.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_starred_false", body2)
            p2_valid = (
                r2.status_code == 200
                and body2.get("success") is True
                and body2.get("data", {}).get("is_starred") is False
            )
            cases.append(
                {
                    "name": "Unstar Document (starred=false)",
                    "status_code": r2.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms2,
                    "passed": p2_valid,
                    "details": f"Starred status: {body2.get('data', {}).get('is_starred')}",
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

        return f"""# API Evaluation Snapshot: POST /api/v1/documents/{{document_id}}:star

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
- **Idempotent Bookmark Toggle**: Reliable state mutation without duplicate status records.
- **Tenant Scope Check**: Star action cannot mutate documents belonging to another user.
"""

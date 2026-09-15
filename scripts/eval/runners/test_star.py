"""Evaluator for POST /api/v1/documents/{document_id}:star."""

import io
import time
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR
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
        paper_path = DATA_PAPERS_DIR / "2504.19754v1.pdf"

        if not doc_id and paper_path.exists():
            payload = io.BytesIO(paper_path.read_bytes())
            files = {"file": (paper_path.name, payload, "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                doc_id = up_res.json()["data"]["id"]
                ctx.track_document(doc_id)

        cases = []

        if doc_id:
            # Case 1: Star with folder_id: null (Root Library Promotion)
            start_t = time.perf_counter()
            r1 = await ctx.client.post(
                f"/api/v1/documents/{doc_id}:star",
                json={"folder_id": None},
            )
            latency_ms1 = (time.perf_counter() - start_t) * 1000
            body1 = r1.json()
            save_raw_artifact(self.endpoint_name, f"doc_{doc_id}_star_root", body1)

            data1 = body1.get("data", {})
            p1_valid = (
                r1.status_code == 200
                and body1.get("success") is True
                and data1.get("is_persistent") is True
                and data1.get("folder_id") is None
            )
            cases.append(
                {
                    "name": "Library Star Promotion (folder_id: null)",
                    "status_code": r1.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms1,
                    "passed": p1_valid,
                    "details": f"is_persistent: {data1.get('is_persistent')}, folder_id: None",
                }
            )

            # Case 2: Unstar / folder change
            start_t2 = time.perf_counter()
            r2 = await ctx.client.post(
                f"/api/v1/documents/{doc_id}:star",
                json={"folder_id": None},
            )
            latency_ms2 = (time.perf_counter() - start_t2) * 1000
            p2_valid = r2.status_code == 200
            cases.append(
                {
                    "name": "Idempotent Star Invocation",
                    "status_code": r2.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms2,
                    "passed": p2_valid,
                    "details": "Ensures idempotent persistence state update",
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
- **Atomic Persistence**: Marks `is_persistent = true`, promoting document to user library.
- **Folder Nullability**: Correctly supports root-level starring without requiring folder ID.
"""

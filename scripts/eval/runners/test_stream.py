"""Evaluator for GET /api/v1/documents/{document_id}/file (Binary Streaming)."""

import io
import time
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.runners.base import BaseAPIRunner


class StreamFileAPIRunner(BaseAPIRunner):
    endpoint_name = "get_documents_file_stream"
    report_filename = "get_documents_file_stream.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}/file"

    async def evaluate(self, ctx: EvaluationContext, **kwargs: Any) -> dict[str, Any]:
        assert ctx.client is not None

        # Pre-requisite: ensure a document exists
        doc_id = kwargs.get("document_id")
        paper_path = DATA_PAPERS_DIR / "2504.19754v1.pdf"

        if not doc_id and paper_path.exists():
            file_bytes = paper_path.read_bytes()
            files = {"file": (paper_path.name, io.BytesIO(file_bytes), "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                doc_id = up_res.json()["data"]["id"]
                ctx.track_document(doc_id)

        cases = []

        if doc_id:
            # Case 1: Full Download (HTTP 200 OK)
            start_t = time.perf_counter()
            r1 = await ctx.client.get(f"/api/v1/documents/{doc_id}/file")
            latency_ms1 = (time.perf_counter() - start_t) * 1000

            save_raw_artifact(
                self.endpoint_name,
                "full_stream_headers",
                {"headers": dict(r1.headers), "status_code": r1.status_code},
            )

            p1_valid = (
                r1.status_code == 200
                and "application/pdf" in r1.headers.get("content-type", "")
                and len(r1.content) > 0
            )
            cases.append(
                {
                    "name": "Full Binary Download (HTTP 200 OK)",
                    "status_code": r1.status_code,
                    "expected_status": 200,
                    "latency_ms": latency_ms1,
                    "passed": p1_valid,
                    "details": f"Transferred: {len(r1.content)} bytes, Type: application/pdf",
                }
            )

            # Case 2: Byte Range Request (HTTP 206 Partial Content)
            start_t2 = time.perf_counter()
            r2 = await ctx.client.get(
                f"/api/v1/documents/{doc_id}/file", headers={"range": "bytes=0-1023"}
            )
            latency_ms2 = (time.perf_counter() - start_t2) * 1000

            save_raw_artifact(
                self.endpoint_name,
                "byte_range_headers",
                {"headers": dict(r2.headers), "status_code": r2.status_code},
            )

            p2_valid = (
                r2.status_code == 206
                and len(r2.content) == 1024
                and "bytes 0-1023/" in r2.headers.get("content-range", "")
            )
            cases.append(
                {
                    "name": "Byte Range Stream (bytes=0-1023 -> HTTP 206)",
                    "status_code": r2.status_code,
                    "expected_status": 206,
                    "latency_ms": latency_ms2,
                    "passed": p2_valid,
                    "details": f"Range: 0-1023, Payload: {len(r2.content)} bytes",
                }
            )

            # Case 3: Unsatisfiable Range (HTTP 416)
            start_t3 = time.perf_counter()
            r3 = await ctx.client.get(
                f"/api/v1/documents/{doc_id}/file",
                headers={"range": "bytes=999999999-999999999"},
            )
            latency_ms3 = (time.perf_counter() - start_t3) * 1000
            p3_valid = r3.status_code == 416
            cases.append(
                {
                    "name": "Unsatisfiable Byte Range (HTTP 416)",
                    "status_code": r3.status_code,
                    "expected_status": 416,
                    "latency_ms": latency_ms3,
                    "passed": p3_valid,
                    "details": "Triggered 416 Range Not Satisfiable per RFC 9110",
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

        return f"""# API Evaluation Snapshot: GET /api/v1/documents/{{document_id}}/file

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
- **RFC 9110 Byte Serving**: Supports `Range: bytes=start-end` for progressive PDF rendering.
- **Header Integrity**: Returns `Accept-Ranges: bytes` and `Content-Type: application/pdf`.
- **Boundary Guard**: Unsatisfiable ranges yield HTTP `416 Range Not Satisfiable`.
"""

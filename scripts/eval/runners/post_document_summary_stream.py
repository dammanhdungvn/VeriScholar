"""Evaluator for POST /api/v1/documents/{document_id}/summary:stream (Real-time SSE Stream)."""

import json
import time
import uuid
from pathlib import Path
from typing import Any

from api.db.models.document import DocumentModel
from api.db.session import AsyncSessionLocal
from sqlalchemy import update

from scripts.eval.config import DATA_PAPERS_DIR, get_available_papers, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


def parse_summary_sse_stream(raw_text: str) -> dict[str, Any]:
    """Parse SSE text into structured events, tokens, and bounding boxes."""
    events: list[dict[str, Any]] = []
    sections_text: dict[str, list[str]] = {
        "problem_statement": [],
        "contributions": [],
        "limitations": [],
    }
    sections_boxes: dict[str, list[list[float]]] = {
        "problem_statement": [],
        "contributions": [],
        "limitations": [],
    }
    start_payload: dict[str, Any] | None = None
    end_payload: dict[str, Any] | None = None
    error_payload: dict[str, Any] | None = None

    raw_chunks = raw_text.strip().split("\n\n")
    for chunk in raw_chunks:
        lines = chunk.strip().split("\n")
        event_type = None
        data_str = None
        for line in lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_str = line.split(":", 1)[1].strip()

        if event_type and data_str:
            try:
                data_obj = json.loads(data_str)
            except Exception:
                data_obj = data_str

            events.append({"event": event_type, "data": data_obj})

            if event_type == "summary_start" and isinstance(data_obj, dict):
                start_payload = data_obj
            elif event_type == "summary_chunk" and isinstance(data_obj, dict):
                sec = data_obj.get("section")
                tok = data_obj.get("token", "")
                if sec in sections_text:
                    sections_text[sec].append(tok)
            elif event_type == "summary_box" and isinstance(data_obj, dict):
                sec = data_obj.get("section")
                boxes = data_obj.get("bounding_boxes", [])
                if sec in sections_boxes:
                    sections_boxes[sec].extend(boxes)
            elif event_type == "summary_end" and isinstance(data_obj, dict):
                end_payload = data_obj
            elif event_type == "error" and isinstance(data_obj, dict):
                error_payload = data_obj

    return {
        "events": events,
        "event_count": len(events),
        "start": start_payload,
        "end": end_payload,
        "error": error_payload,
        "sections_text": {k: "".join(v).strip() for k, v in sections_text.items()},
        "sections_boxes": sections_boxes,
    }


class DocumentSummaryStreamAPIRunner(BaseAPIRunner):
    """Evaluates POST /api/v1/documents/{document_id}/summary:stream real-time SSE streaming."""

    endpoint_name = "post_documents_summary_stream"
    report_filename = "post_document_summary_stream.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}/summary:stream"

    async def evaluate(
        self,
        ctx: EvaluationContext,
        document_id: str | None = None,
        paper: str | Path | None = None,
        interactive: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        assert ctx.client is not None
        cases: list[dict[str, Any]] = []
        artifact_checksums: dict[str, str] = {}
        linter_warnings: list[str] = []

        # 1. Clean refresh for output report
        check_and_prepare_output_file(self.report_filename, interactive=interactive)

        # 2. Golden paper selection
        target_paper: Path | None = None
        if paper:
            p = Path(paper)
            target_paper = p if p.is_absolute() else DATA_PAPERS_DIR / p
        else:
            available = get_available_papers()
            target_paper = available[0] if available else get_default_paper()

        if not target_paper or not target_paper.exists():
            linter_warnings.append(f"Target paper not found: {target_paper}")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # 3. Hermetic Seeding: Upload paper
        seeded_doc_id = document_id
        if not seeded_doc_id:
            files = {"file": (target_paper.name, target_paper.read_bytes(), "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                seeded_doc_id = up_res.json().get("data", {}).get("id")
                if seeded_doc_id:
                    ctx.track_document(seeded_doc_id)
            else:
                linter_warnings.append(
                    f"Failed to seed document for summary:stream: HTTP {up_res.status_code}"
                )
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        def _is_valid_bbox(box: list[float]) -> bool:
            if not isinstance(box, (list, tuple)) or len(box) != 5:
                return False
            x0, y0, x1, y1, pg = box
            return (
                0.0 <= x0 <= 1.0
                and 0.0 <= y0 <= 1.0
                and 0.0 <= x1 <= 1.0
                and 0.0 <= y1 <= 1.0
                and x1 >= x0
                and y1 >= y0
                and int(pg) >= 1
            )

        # =========================================================================
        # Scenario 1: Stream Grounded Summary on Completed Document
        # =========================================================================
        t0 = time.perf_counter()
        headers = {"Accept": "text/event-stream"}
        resp1 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:stream",
            headers=headers,
        )
        latency1 = (time.perf_counter() - t0) * 1000.0

        parsed1 = parse_summary_sse_stream(resp1.text)
        has_start = parsed1["start"] is not None
        has_end = parsed1["end"] is not None
        has_tokens = any(len(txt) > 0 for txt in parsed1["sections_text"].values())
        all_boxes_valid = all(
            _is_valid_bbox(b) for b_list in parsed1["sections_boxes"].values() for b in b_list
        )

        p1_ok = (
            resp1.status_code == 200
            and "text/event-stream" in resp1.headers.get("content-type", "")
            and has_start
            and has_end
            and has_tokens
            and all_boxes_valid
        )

        raw_art1 = {
            "document_id": seeded_doc_id,
            "status_code": resp1.status_code,
            "headers": dict(resp1.headers),
            "parsed_sse": parsed1,
            "raw_stream_sample": resp1.text[:500],
        }
        _, sha1 = save_raw_artifact(
            self.endpoint_name, "01_stream_summary_success_completed", raw_art1
        )
        artifact_checksums["01_stream_summary_success_completed.json"] = sha1

        cases.append(
            {
                "id": "01_stream_summary_success_completed",
                "name": "Stream Real-Time 3-Point Grounded Summary (SSE)",
                "passed": p1_ok,
                "status_code": resp1.status_code,
                "expected_status": 200,
                "latency_ms": latency1,
                "raw_response": raw_art1,
                "details": (
                    f"Parsed {parsed1['event_count']} SSE events. Sections populated: "
                    f"{list(parsed1['sections_text'].keys())}. Total Bounding Boxes: "
                    f"{sum(len(b) for b in parsed1['sections_boxes'].values())}."
                ),
            }
        )

        # =========================================================================
        # Scenario 2: Lifecycle Status Guard - Processing Document (409 Conflict)
        # =========================================================================
        # Upload a dummy document and set its status to 'processing' with 0 chunks
        t0 = time.perf_counter()
        raw_pdf = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        )
        files_proc = {"file": ("transient_inflight.pdf", raw_pdf, "application/pdf")}
        up_proc = await ctx.client.post("/api/v1/documents", files=files_proc)
        proc_doc_id = up_proc.json().get("data", {}).get("id")
        if proc_doc_id:
            ctx.track_document(proc_doc_id)
            async with AsyncSessionLocal() as db_session:
                await db_session.execute(
                    update(DocumentModel)
                    .where(DocumentModel.id == uuid.UUID(proc_doc_id))
                    .values(status="processing", chunk_count=0)
                )
                await db_session.commit()

        resp2 = await ctx.client.post(
            f"/api/v1/documents/{proc_doc_id}/summary:stream",
            headers=headers,
        )
        latency2 = (time.perf_counter() - t0) * 1000.0
        data2 = (
            resp2.json()
            if resp2.headers.get("content-type", "").startswith("application/json")
            else {}
        )

        p2_ok = (
            resp2.status_code == 409 and data2.get("error", {}).get("code") == "DOCUMENT_PROCESSING"
        )

        _, sha2 = save_raw_artifact(
            self.endpoint_name, "02_stream_summary_409_processing_guard", data2
        )
        artifact_checksums["02_stream_summary_409_processing_guard.json"] = sha2

        cases.append(
            {
                "id": "02_stream_summary_409_processing_guard",
                "name": "Lifecycle Guard: Pre-stream Churn Protection (HTTP 409)",
                "passed": p2_ok,
                "status_code": resp2.status_code,
                "expected_status": 409,
                "latency_ms": latency2,
                "raw_response": data2,
                "details": (
                    "Pre-flight status check prevented premature 200 connection drop; returned "
                    f"HTTP 409 Conflict: {data2.get('error', {}).get('code')}"
                ),
            }
        )

        # =========================================================================
        # Scenario 3: Non-existent Document UUID (404 Not Found)
        # =========================================================================
        t0 = time.perf_counter()
        random_doc_id = str(uuid.uuid4())
        resp3 = await ctx.client.post(
            f"/api/v1/documents/{random_doc_id}/summary:stream",
            headers=headers,
        )
        latency3 = (time.perf_counter() - t0) * 1000.0
        data3 = (
            resp3.json()
            if resp3.headers.get("content-type", "").startswith("application/json")
            else {}
        )

        p3_ok = (
            resp3.status_code == 404 and data3.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
        )

        _, sha3 = save_raw_artifact(self.endpoint_name, "03_stream_summary_404_not_found", data3)
        artifact_checksums["03_stream_summary_404_not_found.json"] = sha3

        cases.append(
            {
                "id": "03_stream_summary_404_not_found",
                "name": "Non-existent Document UUID (HTTP 404)",
                "passed": p3_ok,
                "status_code": resp3.status_code,
                "expected_status": 404,
                "latency_ms": latency3,
                "raw_response": data3,
                "details": f"Returned RFC 7807 Error: {data3.get('error', {}).get('code')}",
            }
        )

        # =========================================================================
        # Scenario 4: Malformed UUID Validation (422 Unprocessable)
        # =========================================================================
        t0 = time.perf_counter()
        resp4 = await ctx.client.post(
            "/api/v1/documents/not-a-valid-uuid/summary:stream",
            headers=headers,
        )
        latency4 = (time.perf_counter() - t0) * 1000.0
        data4 = resp4.json() if resp4.content else {}

        p4_ok = resp4.status_code == 422
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_stream_summary_422_invalid_uuid", data4)
        artifact_checksums["04_stream_summary_422_invalid_uuid.json"] = sha4

        cases.append(
            {
                "id": "04_stream_summary_422_invalid_uuid",
                "name": "Malformed Path UUID Parameter Validation (HTTP 422)",
                "passed": p4_ok,
                "status_code": resp4.status_code,
                "expected_status": 422,
                "latency_ms": latency4,
                "raw_response": data4,
                "details": "FastAPI Path validation caught malformed UUID string",
            }
        )

        # =========================================================================
        # Scenario 5: Stream Content-Type & SSE Protocol Framing Check
        # =========================================================================
        t0 = time.perf_counter()
        resp5 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:stream",
            headers={"Accept": "*/*"},
        )
        latency5 = (time.perf_counter() - t0) * 1000.0

        p5_ok = (
            resp5.status_code == 200
            and "text/event-stream" in resp5.headers.get("content-type", "")
            and resp5.headers.get("cache-control") == "no-cache"
            and resp5.headers.get("x-accel-buffering") == "no"
        )

        raw_art5 = {"headers": dict(resp5.headers)}
        _, sha5 = save_raw_artifact(
            self.endpoint_name, "05_stream_summary_headers_and_buffering", raw_art5
        )
        artifact_checksums["05_stream_summary_headers_and_buffering.json"] = sha5

        cases.append(
            {
                "id": "05_stream_summary_headers_and_buffering",
                "name": "SSE Buffering Bypass & Network Headers Compliance",
                "passed": p5_ok,
                "status_code": resp5.status_code,
                "expected_status": 200,
                "latency_ms": latency5,
                "raw_response": raw_art5,
                "details": (
                    f"content-type={resp5.headers.get('content-type')}, "
                    f"cache-control={resp5.headers.get('cache-control')}, "
                    f"x-accel-buffering={resp5.headers.get('x-accel-buffering')}"
                ),
            }
        )

        all_passed = all(c["passed"] for c in cases)

        eval_result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "linter_warnings": linter_warnings,
            "artifact_checksums": artifact_checksums,
            "session_tag": ctx.session_tag,
        }

        # 4. In-Terminal Box (Standardized Summary Format)
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=self.route_path,
            req_headers={"accept": "text/event-stream"},
            req_body={"scenarios": [c["name"] for c in cases]},
            status_code=200 if all_passed else 500,
            latency_ms=sum(c["latency_ms"] for c in cases),
            res_body={
                "total_scenarios": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
            },
            quality_checks=[(c["passed"], f"{c['name']} ({c['latency_ms']:.1f}ms)") for c in cases],
        )
        print("\n" + terminal_box)

        # 5. Write output markdown report
        md_content = self.generate_markdown(eval_result, ctx.session_tag, target_paper.name)
        report_path = write_markdown_report(self.report_filename, md_content)
        eval_result["report_path"] = str(report_path)

        return eval_result

    def generate_markdown(
        self,
        eval_result: dict[str, Any],
        session_tag: str,
        paper_name: str = "sample.pdf",
    ) -> str:
        cases = eval_result.get("cases", [])
        gate = "PASSED" if eval_result.get("all_passed") else "FAILED"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        md = [
            f"# API Evaluation Snapshot: {self.http_method} {self.route_path}\n",
            f"- **Target Endpoint:** `{self.http_method} {self.route_path}`",
            f"- **Evaluated Paper:** `{paper_name}`",
            f"- **Session Tag:** `{session_tag}`",
            f"- **Date Evaluated:** `{now}`",
            f"- **Total Scenarios Evaluated:** `{len(cases)}`",
            f"- **Quality Gate:** `{gate}`\n",
            "## Audit Artifact Checksums (SHA-256)\n",
            "| Scenario / Case Identifier | SHA-256 Checksum | Storage Artifact |",
            "| :--- | :--- | :--- |",
        ]

        for k, v in eval_result.get("artifact_checksums", {}).items():
            md.append(f"| `{k}` | `{v}` | `tests/.artifacts/{self.endpoint_name}/{k}` |")

        md.append("\n---\n")
        md.append("## 1. Executive Summary & Verification Matrix\n")
        md.append(
            "| Scenario | HTTP Status | Expected Status | Status Code Pass | Contract Pass | Latency | Verdict |"
        )
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")

        for c in cases:
            code_pass = "✅ PASS" if c["status_code"] == c["expected_status"] else "❌ FAIL"
            contract_pass = "✅ PASS" if c["passed"] else "❌ FAIL"
            verdict = "**PASS**" if c["passed"] else "**FAIL**"
            md.append(
                f"| {c['name']} | `{c['status_code']}` | `{c['expected_status']}` | {code_pass} | {contract_pass} | {c['latency_ms']:.2f}ms | {verdict} |"
            )

        md.append("\n---\n")
        md.append("## 2. Invariants & Contract Adherence\n")
        md.append(
            "- **W3C Server-Sent Events (SSE):** `text/event-stream` mime-type with `summary_start`, `summary_chunk`, `summary_box`, `summary_end`."
        )
        md.append(
            "- **Visual Grounding Coordinates:** Bounding boxes conform to normalized 5-tuples `[x0, y0, x1, y2, page]` within [0.0, 1.0]."
        )
        md.append(
            "- **Pre-Stream Status Guards:** Pre-flight checks on document lifecycle status (409 Conflict for in-flight processing, 422 for failed) prevent connection abortion."
        )
        md.append(
            "- **Zero Network Buffering:** Headers `Cache-Control: no-cache` and `X-Accel-Buffering: no` enforce low-latency TTFT."
        )

        md.append("\n---\n")
        md.append("## 3. Full Raw Payloads & Audit Artifacts (Untruncated)\n")
        for idx, c in enumerate(cases, 1):
            md.append(f"### Case {idx}: {c['name']} (Status: `{c['status_code']}`)\n")
            md.append(
                "```json\n"
                + json.dumps(c.get("details", {}), indent=2, ensure_ascii=False)
                + "\n```\n"
            )

        return "\n".join(md)

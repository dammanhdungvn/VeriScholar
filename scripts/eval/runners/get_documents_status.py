"""Evaluator for GET /api/v1/documents/{document_id}/status (Polling & Stage Breakdown)."""

import json
import time
import uuid
from pathlib import Path
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, get_available_papers, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


class DocumentStatusAPIRunner(BaseAPIRunner):
    """Evaluates document ingestion progress polling, 5-stage pipeline breakdown, and negative guards."""

    endpoint_name = "get_documents_status"
    report_filename = "get_documents_status.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}/status"

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

        # 1. Clean refresh for output markdown report in temp/output/test/
        check_and_prepare_output_file(self.report_filename, interactive=interactive)

        # 2. Paper selection
        target_paper: Path | None = None
        if paper:
            p = Path(paper)
            target_paper = p if p.is_absolute() else DATA_PAPERS_DIR / p
        else:
            available = get_available_papers()
            target_paper = available[0] if available else get_default_paper()

        if not target_paper or not target_paper.exists():
            linter_warnings.append(f"Target paper file not found: {target_paper}")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # 3. Hermetic Seeding: Upload target paper to obtain a valid document_id
        seeded_doc_id = document_id
        if not seeded_doc_id:
            files = {"file": (target_paper.name, target_paper.read_bytes(), "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                seeded_doc_id = up_res.json().get("data", {}).get("id")
                if seeded_doc_id:
                    ctx.track_document(seeded_doc_id)
            else:
                linter_warnings.append(f"Failed to seed document for status test: HTTP {up_res.status_code}")
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        # Scenario 1: Fresh Upload Status & 5-Stage Breakdown (Expect HTTP 200 OK)
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}/status")
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        data1 = body1.get("data", {})
        meta1 = body1.get("meta", {})
        stages1 = data1.get("stages_detail", {})

        expected_stages = ["validation", "layout_detection", "ocr", "chunking", "embedding"]
        stages_all_present = all(st in stages1 for st in expected_stages)
        stages_all_pending = all(stages1.get(st) == "pending" for st in expected_stages)

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("id") == seeded_doc_id
            and data1.get("status") == "uploaded"
            and data1.get("stage") == "queued"
            and data1.get("progress") == 0
            and stages_all_present
            and stages_all_pending
            and data1.get("error_message") is None
            and "request_id" in meta1
            and "timestamp" in meta1
        )

        _, sha1 = save_raw_artifact(self.endpoint_name, "fresh_upload_status", body1)
        artifact_checksums["fresh_upload_status.json"] = sha1

        cases.append(
            {
                "name": "Fresh Upload Status & 5-Stage Breakdown (HTTP 200 OK)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": (
                    f"Status: {data1.get('status')} | Stage: {data1.get('stage')} | "
                    f"Progress: {data1.get('progress')}% | 5/5 Sub-stages pending"
                ),
                "raw_response": body1,
            }
        )

        # Scenario 2: Progress & Error Message Field Integrity (HTTP 200 OK)
        progress_val = data1.get("progress", -1)
        progress_bounded = isinstance(progress_val, int) and 0 <= progress_val <= 100
        error_msg_valid = data1.get("error_message") is None or isinstance(data1.get("error_message"), str)
        content_type_valid = "application/json" in r1.headers.get("content-type", "")
        latency_budget_valid = latency_ms1 < 50.0  # Quality Budget: < 50ms for DB index read

        p2_valid = progress_bounded and error_msg_valid and content_type_valid and latency_budget_valid
        cases.append(
            {
                "name": "Progress Bound & Envelope Invariant Audit",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p2_valid,
                "details": (
                    f"Progress in [0, 100]: {progress_bounded} | Error field valid: {error_msg_valid} | "
                    f"Latency < 50ms: {latency_ms1:.1f}ms"
                ),
                "raw_response": {
                    "progress": progress_val,
                    "error_message": data1.get("error_message"),
                    "content_type": r1.headers.get("content-type"),
                    "latency_ms": latency_ms1,
                },
            }
        )

        # Scenario 3: Nonexistent Document Guard (Expect HTTP 404 Not Found)
        fake_uuid = str(uuid.uuid4())
        t2 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/documents/{fake_uuid}/status")
        latency_ms3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code in (403, 404) else {}

        p3_valid = (
            r3.status_code == 404
            and body3.get("success") is False
            and body3.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
            and body3.get("error", {}).get("field") == "id"
        )
        _, sha3 = save_raw_artifact(self.endpoint_name, "nonexistent_uuid_404", body3)
        artifact_checksums["nonexistent_uuid_404.json"] = sha3

        cases.append(
            {
                "name": "Nonexistent Document Lookup (Expect HTTP 404)",
                "status_code": r3.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"Unregistered UUID blocked with 404 ({body3.get('error', {}).get('code')})",
                "raw_response": body3,
            }
        )

        # Scenario 4: Malformed UUID Path Guard (Expect HTTP 422 Unprocessable Entity)
        malformed_id = "invalid-uuid-format-status"
        t3 = time.perf_counter()
        r4 = await ctx.client.get(f"/api/v1/documents/{malformed_id}/status")
        latency_ms4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code == 422 else {}

        p4_valid = r4.status_code == 422
        _, sha4 = save_raw_artifact(self.endpoint_name, "malformed_uuid_422", body4)
        artifact_checksums["malformed_uuid_422.json"] = sha4

        cases.append(
            {
                "name": "Malformed UUID Parameter Guard (Expect HTTP 422)",
                "status_code": r4.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": "Malformed UUID string intercepted by FastAPI validation router",
                "raw_response": body4,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the primary status query)
        checks = [
            (r1.status_code == 200, f"Status Code & Envelope: {r1.status_code} OK (Kỳ vọng: 200)"),
            (
                data1.get("status") == "uploaded" and data1.get("stage") == "queued",
                f"State & Stage Matrix : {data1.get('status')} | {data1.get('stage')} | {data1.get('progress')}%",
            ),
            (stages_all_present and stages_all_pending, "5-Stage Breakdown    : 5/5 sub-stages verified (pending)"),
            (progress_bounded, "Progress Bounded     : PASS (0 <= progress <= 100)"),
            (p3_valid, "Nonexistent Guard    : PASS (UUID không tồn tại trả về 404)"),
            (p4_valid, "Malformed Guard      : PASS (Chuỗi sai UUID bị chặn 422)"),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}/status",
            req_headers={"x-user-id": ctx.session_tag, "accept": "application/json"},
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=body1,
            quality_checks=checks,
        )
        print("\n" + terminal_box)

        all_passed = all(c["passed"] for c in cases)
        eval_result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "artifact_checksums": artifact_checksums,
            "linter_warnings": linter_warnings,
            "session_tag": ctx.session_tag,
        }

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
        checksums = eval_result.get("artifact_checksums", {})
        warnings = eval_result.get("linter_warnings", [])

        rows = []
        raw_sections = []
        for idx, c in enumerate(cases, 1):
            res_str = "PASS" if c["passed"] else "FAIL"
            row = (
                f"| {c['name']} | `{c['status_code']}` | "
                f"{c['latency_ms']:.1f} ms | {res_str} | {c['details']} |"
            )
            rows.append(row)

            if c.get("raw_response"):
                raw_json_str = json.dumps(c["raw_response"], indent=2, ensure_ascii=False)
                raw_sections.append(
                    f"### Case {idx}: {c['name']} (Status: `{c['status_code']}`)\n"
                    f"```json\n{raw_json_str}\n```\n"
                )

        table_body = "\n".join(rows)
        raw_payloads_body = "\n".join(raw_sections)

        checksum_lines = []
        for fname, sha in checksums.items():
            checksum_lines.append(f"> - `{fname}`: `{sha}`")
        checksum_block = "\n".join(checksum_lines) if checksum_lines else "> - None"

        warning_block = ""
        if warnings:
            w_lines = [f"- `[WARN]` {w}" for w in warnings]
            warning_block = f"\n## 4. Linter Warnings\n" + "\n".join(w_lines) + "\n"

        target_rel_path = f"temp/output/test/{self.report_filename}"

        return f"""# API Evaluation Snapshot: GET /api/v1/documents/{{document_id}}/status

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Pipeline Status Polling & Stage Breakdown  
> **Target Paper**: `{paper_name}`  
> **Target Output**: `{target_rel_path}`  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{checksum_block}  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Invariants & Contract Adherence
- **5-Stage Pipeline Hierarchy**:
  - The status payload contains granular stage tracking across 5 distinct sub-stages:
    - `validation`: Document sanity, MIME, format checks.
    - `layout_detection`: Layout recognition and page segmentation.
    - `ocr`: Text, tables, and mathematical formula extraction.
    - `chunking`: Semantic chunking and spatial Bounding Box grounding.
    - `embedding`: Dense vector embedding generation and HNSW indexing.
- **Progress Bounding Invariant**: Progress percentage is strictly bounded within integer range `[0, 100]`.
- **Negative Boundary Validation**:
  - Unregistered UUIDs return `HTTP 404 Not Found` with code `DOCUMENT_NOT_FOUND`.
  - Non-UUID strings return `HTTP 422 Unprocessable Entity`.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads & Audit Artifacts (Untruncated)

{raw_payloads_body}
{warning_block}"""

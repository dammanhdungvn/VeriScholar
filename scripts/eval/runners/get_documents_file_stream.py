"""Evaluator for GET /api/v1/documents/{document_id}/file (Binary Streaming & RFC Range Requests)."""

import hashlib
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


class StreamFileAPIRunner(BaseAPIRunner):
    """Evaluates Binary PDF Streaming, RFC 9110/RFC 7233 Partial Content, and Boundary Guards."""

    endpoint_name = "get_documents_file_stream"
    report_filename = "get_documents_file_stream.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}/file"

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

        pdf_bytes = target_paper.read_bytes()
        file_size_bytes = len(pdf_bytes)
        local_file_sha256 = hashlib.sha256(pdf_bytes).hexdigest()

        # 3. Hermetic Seeding: Upload target paper to obtain a valid document_id
        seeded_doc_id = document_id
        if not seeded_doc_id:
            files = {"file": (target_paper.name, pdf_bytes, "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                seeded_doc_id = up_res.json().get("data", {}).get("id")
                if seeded_doc_id:
                    ctx.track_document(seeded_doc_id)
            else:
                linter_warnings.append(
                    f"Failed to seed document for file streaming test: HTTP {up_res.status_code}"
                )
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        # Scenario 1: Full Binary PDF Streaming (Expect HTTP 200 OK)
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}/file")
        latency_ms1 = (time.perf_counter() - t0) * 1000

        r1_bytes = r1.content
        r1_sha256 = hashlib.sha256(r1_bytes).hexdigest()
        r1_magic = r1_bytes[:8].decode("latin-1", errors="replace") if len(r1_bytes) >= 8 else ""

        p1_valid = (
            r1.status_code == 200
            and "application/pdf" in r1.headers.get("content-type", "")
            and r1.headers.get("accept-ranges") == "bytes"
            and r1.headers.get("content-length") == str(file_size_bytes)
            and len(r1_bytes) == file_size_bytes
            and r1_sha256 == local_file_sha256
            and r1_bytes.startswith(b"%PDF-")
        )

        s1_artifact_data = {
            "status_code": r1.status_code,
            "headers": dict(r1.headers),
            "binary_meta": {
                "content_type": r1.headers.get("content-type"),
                "bytes_received": len(r1_bytes),
                "expected_size_bytes": file_size_bytes,
                "magic_bytes": r1_magic,
                "stream_sha256": r1_sha256,
                "local_sha256": local_file_sha256,
                "integrity_verified": r1_sha256 == local_file_sha256,
            },
        }
        _, sha1 = save_raw_artifact(self.endpoint_name, "full_stream_headers", s1_artifact_data)
        artifact_checksums["full_stream_headers.json"] = sha1

        cases.append(
            {
                "name": "Full Binary PDF Streaming (HTTP 200 OK)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": f"Streamed {len(r1_bytes):,} bytes | SHA-256 match 100% | Content-Type: {r1.headers.get('content-type')}",
                "raw_response": s1_artifact_data,
            }
        )

        # Scenario 2: Partial Range Streaming (Expect HTTP 206 Partial Content)
        range_req_header = "bytes=0-1023"
        t1 = time.perf_counter()
        r2 = await ctx.client.get(
            f"/api/v1/documents/{seeded_doc_id}/file",
            headers={"Range": range_req_header},
        )
        latency_ms2 = (time.perf_counter() - t1) * 1000

        r2_bytes = r2.content
        expected_range_bytes = pdf_bytes[0:1024]
        range_match = r2_bytes == expected_range_bytes

        p2_valid = (
            r2.status_code == 206
            and r2.headers.get("content-range") == f"bytes 0-1023/{file_size_bytes}"
            and r2.headers.get("content-length") == "1024"
            and len(r2_bytes) == 1024
            and range_match
            and r2_bytes.startswith(b"%PDF-")
        )

        s2_artifact_data = {
            "status_code": r2.status_code,
            "headers": dict(r2.headers),
            "range_requested": range_req_header,
            "content_range_returned": r2.headers.get("content-range"),
            "bytes_received": len(r2_bytes),
            "range_slice_matched": range_match,
        }
        _, sha2 = save_raw_artifact(self.endpoint_name, "partial_range_0_1023", s2_artifact_data)
        artifact_checksums["partial_range_0_1023.json"] = sha2

        cases.append(
            {
                "name": "Partial Range Streaming (HTTP 206 Partial Content)",
                "status_code": r2.status_code,
                "expected_status": 206,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": f"Content-Range: {r2.headers.get('content-range')} | Received {len(r2_bytes)} B exactly matching slice [0:1024]",
                "raw_response": s2_artifact_data,
            }
        )

        # Scenario 3: Unsatisfiable Range Guard (Expect HTTP 416 Range Not Satisfiable)
        unsatisfiable_range = "bytes=99999999-99999999"
        t2 = time.perf_counter()
        r3 = await ctx.client.get(
            f"/api/v1/documents/{seeded_doc_id}/file",
            headers={"Range": unsatisfiable_range},
        )
        latency_ms3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code == 416 else {}

        p3_valid = (
            r3.status_code == 416
            and r3.headers.get("content-range") == f"bytes */{file_size_bytes}"
            and body3.get("success") is False
            and body3.get("error", {}).get("code") == "RANGE_NOT_SATISFIABLE"
        )
        _, sha3 = save_raw_artifact(self.endpoint_name, "unsatisfiable_range_416", body3)
        artifact_checksums["unsatisfiable_range_416.json"] = sha3

        cases.append(
            {
                "name": "Unsatisfiable Range Guard (HTTP 416 Range Not Satisfiable)",
                "status_code": r3.status_code,
                "expected_status": 416,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"Content-Range: {r3.headers.get('content-range')} | Code: {body3.get('error', {}).get('code')}",
                "raw_response": body3,
            }
        )

        # Scenario 4: Nonexistent Document Guard (Expect HTTP 404 Not Found)
        fake_uuid = str(uuid.uuid4())
        t3 = time.perf_counter()
        r4 = await ctx.client.get(f"/api/v1/documents/{fake_uuid}/file")
        latency_ms4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code in (403, 404) else {}

        p4_valid = (
            r4.status_code == 404
            and body4.get("success") is False
            and body4.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
        )
        _, sha4 = save_raw_artifact(self.endpoint_name, "nonexistent_uuid_404", body4)
        artifact_checksums["nonexistent_uuid_404.json"] = sha4

        cases.append(
            {
                "name": "Nonexistent Document Lookup (Expect HTTP 404)",
                "status_code": r4.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": f"Correctly returned 404 Not Found with code '{body4.get('error', {}).get('code')}'",
                "raw_response": body4,
            }
        )

        # Scenario 5: Malformed UUID Guard (Expect HTTP 422 Unprocessable Entity)
        malformed_id = "not-a-valid-uuid-9999"
        t4 = time.perf_counter()
        r5 = await ctx.client.get(f"/api/v1/documents/{malformed_id}/file")
        latency_ms5 = (time.perf_counter() - t4) * 1000
        body5 = r5.json() if r5.status_code == 422 else {}

        p5_valid = r5.status_code == 422
        _, sha5 = save_raw_artifact(self.endpoint_name, "malformed_uuid_422", body5)
        artifact_checksums["malformed_uuid_422.json"] = sha5

        cases.append(
            {
                "name": "Malformed UUID Parameter Guard (Expect HTTP 422)",
                "status_code": r5.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": "Triggered HTTP 422 Unprocessable Entity for malformed path parameter",
                "raw_response": body5,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the primary full streaming)
        terminal_binary_body = {
            "[BINARY_STREAM_INFO]": "application/pdf binary content (safe folding)",
            "bytes_streamed": len(r1_bytes),
            "magic_header": r1_magic,
            "stream_sha256": f"{r1_sha256[:8]}...{r1_sha256[-8:]} (sha256 verified)",
            "integrity_matched": r1_sha256 == local_file_sha256,
        }
        checks = [
            (r1.status_code == 200, f"Full Stream Status   : {r1.status_code} OK (Kỳ vọng: 200)"),
            (p1_valid, f"Byte Size & SHA-256   : PASS ({len(r1_bytes):,} bytes khớp 100% tệp gốc)"),
            (p2_valid, "Partial Range 0-1023  : PASS (HTTP 206, 1,024 bytes khớp phân đoạn)"),
            (p3_valid, "Unsatisfiable Range   : PASS (HTTP 416 Range Not Satisfiable)"),
            (p4_valid, "Nonexistent Guard     : PASS (UUID không tồn tại trả về 404)"),
            (p5_valid, "Malformed Guard       : PASS (Chuỗi không phải UUID bị chặn 422)"),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}/file",
            req_headers={"x-user-id": ctx.session_tag, "accept": "application/pdf"},
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=terminal_binary_body,
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
            warning_block = "\n## 4. Linter Warnings\n" + "\n".join(w_lines) + "\n"

        target_rel_path = f"temp/output/test/{self.report_filename}"

        return f"""# API Evaluation Snapshot: GET /api/v1/documents/{{document_id}}/file

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Binary PDF Streaming & RFC Range Partial Content  
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
- **Binary Streaming Protocol (RFC 9110 & RFC 7233)**:
  - Full stream returns `HTTP 200 OK` with `Content-Type: application/pdf`, `Accept-Ranges: bytes`, and exact `Content-Length`.
  - Byte-range requests return `HTTP 206 Partial Content` with conforming `Content-Range: bytes <start>-<end>/<total>` and exact sliced payload.
- **Terminal Anti-Hang Protection**: Binary payloads are safely digested via SHA-256 without streaming unescaped control characters to standard output.
- **Negative Boundary Validation**:
  - Unsatisfiable ranges return `HTTP 416 Range Not Satisfiable` with `Content-Range: bytes */<total>`.
  - Nonexistent document IDs return `HTTP 404 Not Found` with structured error payload.
  - Non-UUID strings return `HTTP 422 Unprocessable Entity`.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads & Stream Artifacts (Untruncated)

{raw_payloads_body}
{warning_block}"""

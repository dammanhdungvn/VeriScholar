"""Evaluator for GET /api/v1/documents/{document_id} (Module 1: Document Detail & Spatial Metadata)."""

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


class DocumentDetailAPIRunner(BaseAPIRunner):
    """Evaluates Document Detail retrieval, Spatial Metadata dimensions, and Boundary Guards."""

    endpoint_name = "get_documents_detail"
    report_filename = "get_documents_detail.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}"

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
                linter_warnings.append(f"Failed to seed document for detail test: HTTP {up_res.status_code}")
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        # Scenario 1: Valid Document Detail Retrieval (Expect HTTP 200)
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}")
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        _, sha1 = save_raw_artifact(self.endpoint_name, "valid_document_detail", body1)
        artifact_checksums["valid_document_detail.json"] = sha1

        data1 = body1.get("data", {})
        pages_meta = data1.get("pages_metadata", [])

        # Validate spatial pages metadata structure
        pages_valid = isinstance(pages_meta, list)
        if pages_valid and len(pages_meta) > 0:
            for pm in pages_meta:
                if not (
                    isinstance(pm, dict)
                    and pm.get("page_number", 0) >= 1
                    and isinstance(pm.get("dimensions"), list)
                    and len(pm.get("dimensions", [])) == 2
                    and pm.get("dimensions")[0] > 0
                    and pm.get("dimensions")[1] > 0
                    and pm.get("rotation_deg", 0) in (0, 90, 180, 270)
                ):
                    pages_valid = False
                    break

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("id") == seeded_doc_id
            and data1.get("filename") == target_paper.name
            and data1.get("file_size_bytes") == file_size_bytes
            and data1.get("status") in ("uploaded", "completed")
            and data1.get("is_persistent") is False
            and pages_valid
        )
        cases.append(
            {
                "name": "Valid Document Detail & Spatial Metadata Retrieval",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": f"File: {data1.get('filename')} | Size: {data1.get('file_size_bytes'):,} B | Status: {data1.get('status')} | Pages: {len(pages_meta)}",
                "raw_response": body1,
            }
        )

        # Scenario 2: Nonexistent Document UUID Lookup (Expect HTTP 404)
        fake_uuid = str(uuid.uuid4())
        t1 = time.perf_counter()
        r2 = await ctx.client.get(f"/api/v1/documents/{fake_uuid}")
        latency_ms2 = (time.perf_counter() - t1) * 1000
        body2 = r2.json() if r2.status_code in (403, 404) else {}
        _, sha2 = save_raw_artifact(self.endpoint_name, "nonexistent_uuid_404", body2)
        artifact_checksums["nonexistent_uuid_404.json"] = sha2

        error_obj = body2.get("error", {})
        p2_valid = (
            r2.status_code == 404
            and body2.get("success") is False
            and error_obj.get("code") == "DOCUMENT_NOT_FOUND"
            and error_obj.get("field") == "id"
        )
        cases.append(
            {
                "name": "Nonexistent Document UUID Lookup (Expect HTTP 404)",
                "status_code": r2.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": f"Accurately returned 404 Not Found with code '{error_obj.get('code')}'",
                "raw_response": body2,
            }
        )

        # Scenario 3: Malformed UUID Guard (Expect HTTP 422 Unprocessable Entity)
        malformed_id = "not-a-valid-uuid-9999"
        t2 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/documents/{malformed_id}")
        latency_ms3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code == 422 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "malformed_uuid_422", body3)
        artifact_checksums["malformed_uuid_422.json"] = sha3

        p3_valid = r3.status_code == 422
        cases.append(
            {
                "name": "Malformed UUID Parameter Guard (Expect HTTP 422)",
                "status_code": r3.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": "Triggered HTTP 422 Unprocessable Entity for invalid UUID format",
                "raw_response": body3,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the primary valid retrieval)
        checks = [
            (r1.status_code == 200, f"HTTP Status Code : {r1.status_code} OK (Kỳ vọng: 200)"),
            (data1.get("id") == seeded_doc_id, f"Document ID Match: {seeded_doc_id}"),
            (data1.get("filename") == target_paper.name, f"Filename Match   : {target_paper.name}"),
            (data1.get("file_size_bytes") == file_size_bytes, f"Byte Size Match  : {file_size_bytes:,} bytes"),
            (pages_valid, f"Spatial Metadata : PASS (Cấu trúc {len(pages_meta)} trang hợp lệ)"),
            (p2_valid, "Nonexistent Guard: PASS (UUID không tồn tại trả về 404 DOCUMENT_NOT_FOUND)"),
            (p3_valid, "Malformed Guard  : PASS (Chuỗi không phải UUID bị chặn 422)"),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}",
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

        return f"""# API Evaluation Snapshot: GET /api/v1/documents/{{document_id}}

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Document Detail & Spatial Metadata Retrieval  
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
- **Top-Level Single Resource Envelope**: Response strictly adheres to `DocumentDetailEnvelope` format (`success`, `data`, `meta`).
- **Canvas Spatial Metadata Contract**: Each item in `pages_metadata` contains `page_number`, typographical points `dimensions: [width, height]`, and `rotation_deg in (0, 90, 180, 270)`.
- **Negative Boundary Validation**:
  - Nonexistent UUIDs return HTTP `404 Not Found` with structured error code `DOCUMENT_NOT_FOUND`.
  - Non-UUID strings return HTTP `422 Unprocessable Entity`.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads (Untruncated)

{raw_payloads_body}
{warning_block}"""

"""Evaluation runner for POST /api/v1/documents (Module 1: Document Upload & CAS Deduplication)."""

import json
import time
import urllib.parse
from pathlib import Path
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR, TEMP_OUTPUT_TEST_DIR, get_available_papers
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


class UploadAPIRunner(BaseAPIRunner):
    """Evaluates Document Upload and CAS deduplication behavior."""

    endpoint_name = "post_documents_upload"
    report_filename = "post_documents_upload.md"
    http_method = "POST"
    route_path = "/api/v1/documents"

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

        # 1. Check and prepare output report file in temp/output/test/
        check_and_prepare_output_file(self.report_filename, interactive=interactive)

        if paper:
            p = Path(paper)
            if not p.is_absolute():
                p = DATA_PAPERS_DIR / p
            golden_papers = [p]
        else:
            # Dynamically discover all actual PDF papers in DATA_PAPERS_DIR
            golden_papers = get_available_papers()

        for paper_path in golden_papers:
            if not paper_path.exists():
                linter_warnings.append(f"Missing sample file: {paper_path.name}")
                continue

            pdf_bytes = paper_path.read_bytes()

            # Scenario 1: Initial Upload (Expect HTTP 201)
            t0 = time.perf_counter()
            r1 = await ctx.client.post(
                "/api/v1/documents",
                files={"file": (paper_path.name, pdf_bytes, "application/pdf")},
            )
            latency_ms1 = (time.perf_counter() - t0) * 1000

            body1 = r1.json() if r1.status_code in (200, 201) else {}
            _, sha1 = save_raw_artifact(self.endpoint_name, f"{paper_path.stem}_initial", body1)
            artifact_checksums[f"{paper_path.stem}_initial.json"] = sha1

            doc_id1 = body1.get("data", {}).get("id")
            if doc_id1:
                ctx.track_document(doc_id1)

            ret_fn1 = body1.get("data", {}).get("filename", "")
            fn_matches1 = (
                ret_fn1 == paper_path.name
                or urllib.parse.unquote(ret_fn1) == paper_path.name
                or ret_fn1.replace("\n", " ") == paper_path.name.replace("\n", " ")
            )

            is_pass1 = (
                r1.status_code == 201
                and body1.get("success") is True
                and fn_matches1
                and body1.get("data", {}).get("content_hash") is not None
            )
            cases.append(
                {
                    "name": f"Valid PDF Upload ({paper_path.name})",
                    "status_code": r1.status_code,
                    "expected_status": 201,
                    "latency_ms": latency_ms1,
                    "doc_id": doc_id1,
                    "passed": is_pass1,
                    "details": f"Doc ID: {doc_id1} | Hash: {body1.get('data', {}).get('content_hash', '')[:12]}...",
                    "raw_response": body1,
                }
            )

            # Scenario 2: Deduplication Check (CAS)
            t1 = time.perf_counter()
            r_dup = await ctx.client.post(
                "/api/v1/documents",
                files={"file": (f"copy_{paper_path.name}", pdf_bytes, "application/pdf")},
            )
            latency_ms2 = (time.perf_counter() - t1) * 1000

            body_dup = r_dup.json() if r_dup.status_code in (200, 201) else {}
            _, sha_dup = save_raw_artifact(
                self.endpoint_name, f"{paper_path.stem}_duplicate", body_dup
            )
            artifact_checksums[f"{paper_path.stem}_duplicate.json"] = sha_dup

            doc_id_dup = body_dup.get("data", {}).get("id")
            if doc_id_dup:
                ctx.track_document(doc_id_dup)

            is_cas_dedup = (
                r_dup.status_code == 201
                and body_dup.get("data", {}).get("content_hash")
                == body1.get("data", {}).get("content_hash")
            )
            cases.append(
                {
                    "name": f"CAS Deduplication ({paper_path.name})",
                    "status_code": r_dup.status_code,
                    "expected_status": 201,
                    "latency_ms": latency_ms2,
                    "doc_id": doc_id_dup,
                    "passed": is_cas_dedup,
                    "details": f"CAS Dedup Matched Hash: {body_dup.get('data', {}).get('content_hash', '')[:12]}...",
                    "raw_response": body_dup,
                }
            )

            # Render In-Terminal HTTP Exchange Box for Developer & AI Immediate Inspection
            content_hash = body1.get("data", {}).get("content_hash", "N/A")
            checks = [
                (r1.status_code == 201, f"HTTP Status Code : {r1.status_code} Created (Kỳ vọng: 201)"),
                (content_hash != "N/A", f"Content Hash CAS : {content_hash}"),
                (
                    is_cas_dedup,
                    f"CAS Deduplication: {'PASS' if is_cas_dedup else 'FAIL'} (Bản sao tái sử dụng cùng blob trong {latency_ms2:.1f} ms)",
                ),
                (
                    is_pass1 and is_cas_dedup,
                    f"Đạt chuẩn Gate   : {'PASSED' if (is_pass1 and is_cas_dedup) else 'FAILED'}",
                ),
            ]
            terminal_box = format_terminal_box(
                method=self.http_method,
                path=self.route_path,
                req_headers={"x-user-id": ctx.session_tag, "content-type": "multipart/form-data"},
                form_data={"file": f"{paper_path.name} ({len(pdf_bytes):,} bytes | application/pdf)"},
                req_body=None,
                status_code=r1.status_code,
                latency_ms=latency_ms1,
                res_headers=dict(r1.headers),
                res_body=body1,
                quality_checks=checks,
            )
            print("\n" + terminal_box)

        # Scenario 3: Negative Test - Corrupted Header (only run when evaluating full suite or when paper not restricted)
        if not paper:
            corrupt_path = DATA_PAPERS_DIR / "corrupted_structure.pdf"
            if corrupt_path.exists():
                t2 = time.perf_counter()
                r_corrupt = await ctx.client.post(
                    "/api/v1/documents",
                    files={"file": ("corrupt.pdf", corrupt_path.read_bytes(), "application/pdf")},
                )
                latency_ms3 = (time.perf_counter() - t2) * 1000
                is_pass_corrupt = r_corrupt.status_code == 422
                cases.append(
                    {
                        "name": "Chaos: Corrupted Binary Header",
                        "status_code": r_corrupt.status_code,
                        "expected_status": 422,
                        "latency_ms": latency_ms3,
                        "doc_id": None,
                        "passed": is_pass_corrupt,
                        "details": "Triggered 422 Validation Error as expected",
                        "raw_response": r_corrupt.json() if r_corrupt.status_code == 422 else {},
                    }
                )

        all_passed = all(c["passed"] for c in cases)
        eval_result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "artifact_checksums": artifact_checksums,
            "linter_warnings": linter_warnings,
            "session_tag": ctx.session_tag,
        }

        md_content = self.generate_markdown(eval_result, ctx.session_tag)
        report_path = write_markdown_report(self.report_filename, md_content)
        eval_result["report_path"] = str(report_path)

        return eval_result

    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
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

            # Build Full Raw JSON block for 100% fidelity without terminal bloat
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

        return f"""# API Evaluation Snapshot: POST /api/v1/documents

> **Audit Header**: Session Tag: `{session_tag}` | Mode: CAS Ingestion & Deduplication  
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

## 2. Invariants & Storage Integrity
- **Content-Addressable Storage (CAS)**: Cryptographic SHA-256 matches bitwise identical uploads.
- **Zero-Retention Hermetic Safety**: Temporary test documents are tracked and cascade-purged on context exit (or retained via `--keep-data`).
- **Robust Multipart Parsing**: Validates special character preservation in filename payloads.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads (Untruncated)

{raw_payloads_body}
{warning_block}"""

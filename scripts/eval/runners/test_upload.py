"""Evaluation runner for POST /api/v1/documents.

Validates PDF document upload across all golden papers, Content-Addressable Storage (CAS)
SHA-256 deduplication, magic bytes validation barrier, and writes markdown snapshot report.
"""

import io
import time
from typing import Any

from scripts.eval.config import DATA_PAPERS_DIR
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import save_raw_artifact, write_markdown_report
from scripts.eval.runners.base import BaseAPIRunner


class UploadAPIRunner(BaseAPIRunner):
    def __init__(self):
        super().__init__(
            endpoint_name="post_documents_upload",
            http_method="POST",
            route_path="/api/v1/documents",
            report_filename="post_documents_upload.md",
        )

    async def evaluate(
        self,
        ctx: EvaluationContext,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        cases = []
        artifact_checksums = {}

        # Discover all PDF papers in DATA_PAPERS_DIR
        pdf_papers = sorted(list(DATA_PAPERS_DIR.glob("*.pdf")))
        if not pdf_papers:
            raise FileNotFoundError(f"Không tìm thấy file PDF nào trong {DATA_PAPERS_DIR}")

        # Iterate over each golden paper
        for paper_path in pdf_papers:
            with open(paper_path, "rb") as f:
                pdf_bytes = f.read()

            # Scenario 1: Upload valid PDF
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

            is_pass1 = (
                r1.status_code == 201
                and body1.get("success") is True
                and body1.get("data", {}).get("filename") == paper_path.name
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

            doc_id2 = body_dup.get("data", {}).get("id")
            if doc_id2:
                ctx.track_document(doc_id2)

            is_dup_ok = (
                r_dup.status_code == 201
                and body_dup.get("success") is True
                and body_dup.get("data", {}).get("content_hash")
                == body1.get("data", {}).get("content_hash")
            )
            cases.append(
                {
                    "name": f"CAS Deduplication Check ({paper_path.name})",
                    "status_code": r_dup.status_code,
                    "expected_status": 201,
                    "latency_ms": latency_ms2,
                    "passed": is_dup_ok,
                }
            )

        # Scenario 3: Corrupted PDF Header Rejection
        fake_corrupted = io.BytesIO(b"NOT_A_PDF_MAGIC_BYTES_1234567890")
        t2 = time.perf_counter()
        r_err = await ctx.client.post(
            "/api/v1/documents",
            files={"file": ("corrupted.pdf", fake_corrupted, "application/pdf")},
        )
        latency_ms3 = (time.perf_counter() - t2) * 1000

        body_err = r_err.json()
        _, sha_err = save_raw_artifact(self.endpoint_name, "corrupted_structure", body_err)
        artifact_checksums["corrupted_structure.json"] = sha_err

        is_err_ok = r_err.status_code in (400, 422) and body_err.get("success") is False
        cases.append(
            {
                "name": "Corrupted PDF Header Rejection",
                "status_code": r_err.status_code,
                "expected_status": 400,
                "latency_ms": latency_ms3,
                "success": body_err.get("success", False),
                "error_code": body_err.get("error", {}).get("code"),
                "passed": is_err_ok,
            }
        )

        all_passed = all(c["passed"] for c in cases)
        result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "session_tag": ctx.session_tag,
            "artifact_checksums": artifact_checksums,
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
            rows.append(
                f"| {c['name']} | `{c['status_code']}` (exp: `{c['expected_status']}`) | "
                f"{c['latency_ms']:.1f} ms | {res_str} |"
            )
        table_body = "\n".join(rows)

        checksum_lines = []
        for fname, sha in eval_result.get("artifact_checksums", {}).items():
            checksum_lines.append(f"> - `{fname}`: `{sha}`")
        checksum_section = "\n".join(checksum_lines) if checksum_lines else "> - N/A"

        return f"""# API Evaluation Snapshot: POST /api/v1/documents

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Automated Autotest  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{checksum_section}  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Test Scenario | HTTP Status | Latency | Status |
| :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Invariants & Architecture Checks
- **CAS Deduplication**: Re-uploading identical binary computes exact SHA-256.
- **Validation Ingress Barrier**: Corrupted PDF binary is rejected with HTTP 400.
- **Zero-Storage Retention**: Ephemeral test tenant cleaned up on evaluation exit.
- **Payload Integrity**: Checksums cryptographically bound to raw json artifacts.
"""

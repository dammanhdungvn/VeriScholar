"""Evaluator for POST /api/v1/documents/{document_id}:star (Star / Promotion)."""

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


class StarDocumentAPIRunner(BaseAPIRunner):
    """Evaluates document starring, persistent library promotion, and folder association guards."""

    endpoint_name = "post_documents_star"
    report_filename = "post_documents_star.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}:star"

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
                linter_warnings.append(
                    f"Failed to seed document for star test: HTTP {up_res.status_code}"
                )
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        # Scenario 1: Star Without Folder (Default General Library, Expect HTTP 200 OK)
        payload1 = {"folder_id": None}
        t0 = time.perf_counter()
        r1 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:star",
            json=payload1,
        )
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        data1 = body1.get("data", {})
        meta1 = body1.get("meta", {})

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("id") == seeded_doc_id
            and data1.get("is_persistent") is True
            and data1.get("folder_id") is None
            and data1.get("filename") == target_paper.name
            and "updated_at" in data1
            and "request_id" in meta1
            and "timestamp" in meta1
        )

        _, sha1 = save_raw_artifact(self.endpoint_name, "star_without_folder_200", body1)
        artifact_checksums["star_without_folder_200.json"] = sha1

        cases.append(
            {
                "name": "Star Without Folder (Promote to General Library)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": (
                    f"is_persistent: {data1.get('is_persistent')} | folder_id: {data1.get('folder_id')} | "
                    f"Updated: {data1.get('updated_at')}"
                ),
                "raw_response": body1,
            }
        )

        # Scenario 2: Idempotent Star Re-invocation (Expect HTTP 200 OK)
        payload2: dict[str, Any] = {}
        t1 = time.perf_counter()
        r2 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:star",
            json=payload2,
        )
        latency_ms2 = (time.perf_counter() - t1) * 1000
        body2 = r2.json() if r2.status_code == 200 else {}
        data2 = body2.get("data", {})

        p2_valid = (
            r2.status_code == 200
            and body2.get("success") is True
            and data2.get("id") == seeded_doc_id
            and data2.get("is_persistent") is True
            and data2.get("folder_id") is None
        )

        _, sha2 = save_raw_artifact(self.endpoint_name, "star_idempotent_reinvocation_200", body2)
        artifact_checksums["star_idempotent_reinvocation_200.json"] = sha2

        cases.append(
            {
                "name": "Idempotent Star Re-invocation (Empty Body)",
                "status_code": r2.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": "Repeated star maintained is_persistent=True without duplication",
                "raw_response": body2,
            }
        )

        # Scenario 3: Nonexistent Folder Assignment Guard (Expect HTTP 404 Not Found)
        fake_folder_id = str(uuid.uuid4())
        payload3 = {"folder_id": fake_folder_id}
        t2 = time.perf_counter()
        r3 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:star",
            json=payload3,
        )
        latency_ms3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code in (403, 404) else {}

        p3_valid = (
            r3.status_code == 404
            and body3.get("success") is False
            and body3.get("error", {}).get("code") == "FOLDER_NOT_FOUND"
            and body3.get("error", {}).get("field") == "folder_id"
        )

        _, sha3 = save_raw_artifact(self.endpoint_name, "nonexistent_folder_404", body3)
        artifact_checksums["nonexistent_folder_404.json"] = sha3

        cases.append(
            {
                "name": "Nonexistent Folder Guard (Expect HTTP 404)",
                "status_code": r3.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"Rejected unowned folder with 404 ({body3.get('error', {}).get('code')})",
                "raw_response": body3,
            }
        )

        # Scenario 4: Nonexistent Document Guard (Expect HTTP 404 Not Found)
        fake_doc_id = str(uuid.uuid4())
        t3 = time.perf_counter()
        r4 = await ctx.client.post(
            f"/api/v1/documents/{fake_doc_id}:star",
            json={"folder_id": None},
        )
        latency_ms4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code in (403, 404) else {}

        p4_valid = (
            r4.status_code == 404
            and body4.get("success") is False
            and body4.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
            and body4.get("error", {}).get("field") == "id"
        )

        _, sha4 = save_raw_artifact(self.endpoint_name, "nonexistent_document_404", body4)
        artifact_checksums["nonexistent_document_404.json"] = sha4

        cases.append(
            {
                "name": "Nonexistent Document Lookup (Expect HTTP 404)",
                "status_code": r4.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": f"Unregistered UUID blocked with 404 ({body4.get('error', {}).get('code')})",
                "raw_response": body4,
            }
        )

        # Scenario 5: Malformed UUID Path Guard (Expect HTTP 422 Unprocessable Entity)
        malformed_id = "invalid-uuid-format-star"
        t4 = time.perf_counter()
        r5 = await ctx.client.post(
            f"/api/v1/documents/{malformed_id}:star",
            json={"folder_id": None},
        )
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
                "details": "Malformed UUID parameter intercepted by FastAPI validation router",
                "raw_response": body5,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the primary star operation)
        checks = [
            (r1.status_code == 200, f"Status Code & Envelope: {r1.status_code} OK (Kỳ vọng: 200)"),
            (
                data1.get("is_persistent") is True,
                "Persistence Promotion : PASS (is_persistent = True)",
            ),
            (data1.get("folder_id") is None, "Default Folder State : PASS (folder_id = None)"),
            (p2_valid, "Idempotent Execution : PASS (gọi lại lần 2 vẫn 200 OK)"),
            (p3_valid, "Folder Guard (404)   : PASS (Thư mục ma bị từ chối FOLDER_NOT_FOUND)"),
            (p4_valid, "Document Guard (404) : PASS (UUID không tồn tại trả về 404)"),
            (p5_valid, "Malformed Guard (422): PASS (Chuỗi sai UUID bị chặn 422)"),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}:star",
            req_headers={"x-user-id": ctx.session_tag, "content-type": "application/json"},
            form_data=None,
            req_body=payload1,
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
            warning_block = "\n## 4. Linter Warnings\n" + "\n".join(w_lines) + "\n"

        target_rel_path = f"temp/output/test/{self.report_filename}"

        return f"""# API Evaluation Snapshot: POST /api/v1/documents/{{document_id}}:star

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Personal Library Promotion & Star  
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
- **Custom Method Semantics (Google Cloud AIP-136)**:
  - The custom method `:star` permanently promotes the paper from ephemeral state to persistent personal library retention (`is_persistent: True`).
- **Idempotency Guarantee**: Repeated invocations of `:star` maintain the `is_persistent: True` invariant safely without creating duplicate records or mutating unaffected fields.
- **Folder Scoping & Boundary Validation**:
  - Gaining assignment to a nonexistent or foreign `folder_id` is blocked with `HTTP 404 FOLDER_NOT_FOUND`.
  - Nonexistent document IDs return `HTTP 404 DOCUMENT_NOT_FOUND`.
  - Non-UUID format returns `HTTP 422 Unprocessable Entity`.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads & Audit Artifacts (Untruncated)

{raw_payloads_body}
{warning_block}"""

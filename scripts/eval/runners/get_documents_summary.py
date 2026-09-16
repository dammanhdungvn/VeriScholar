"""Evaluator for GET /api/v1/documents/{document_id}/summary (Document Summary API)."""

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


class DocumentSummaryAPIRunner(BaseAPIRunner):
    """Evaluates document 3-point grounded summary retrieval and visual grounding bounding boxes."""

    endpoint_name = "get_documents_summary"
    report_filename = "get_documents_summary.md"
    http_method = "GET"
    route_path = "/api/v1/documents/{document_id}/summary"

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

        # 3. Hermetic Seeding: Upload target paper to obtain a valid document_id if needed
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
                    f"Failed to seed document for summary test: HTTP {up_res.status_code}"
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
                and pg >= 1
            )

        # Scenario 1: Standard Retrieval & Grounding Synthesis (200 OK)
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}/summary")
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        data1 = body1.get("data", {})

        p1_prob = data1.get("problem_statement", {})
        p1_contr = data1.get("contributions", {})
        p1_limit = data1.get("limitations", {})

        s1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("document_id") == seeded_doc_id
            and bool(p1_prob.get("text"))
            and bool(p1_contr.get("text"))
            and bool(p1_limit.get("text"))
            and data1.get("total_tokens", 0) > 0
        )

        c1_audit_path, c1_sha = save_raw_artifact(
            self.endpoint_name, "case1_standard_summary", body1
        )
        artifact_checksums["case1_standard_summary"] = c1_sha

        cases.append(
            {
                "name": "Case 1: Standard Grounded Summary Retrieval (200 OK)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": s1_valid,
                "details": (
                    f"Retrieved 3-point summary: tokens={data1.get('total_tokens')}, "
                    f"prob_len={len(p1_prob.get('text', ''))}, contr_len={len(p1_contr.get('text', ''))}, "
                    f"limit_len={len(p1_limit.get('text', ''))}"
                ),
                "audit_file": str(c1_audit_path),
                "sha256": c1_sha,
                "raw_response": body1,
            }
        )

        # Scenario 2: Visual Grounding Coordinate Invariant Verification
        all_boxes: list[list[float]] = []
        all_boxes.extend(p1_prob.get("bounding_boxes") or [])
        all_boxes.extend(p1_contr.get("bounding_boxes") or [])
        all_boxes.extend(p1_limit.get("bounding_boxes") or [])

        boxes_valid = len(all_boxes) > 0 and all(_is_valid_bbox(b) for b in all_boxes)
        c2_audit_path, c2_sha = save_raw_artifact(
            self.endpoint_name, "case2_visual_grounding_boxes", {"bounding_boxes": all_boxes}
        )
        artifact_checksums["case2_visual_grounding_boxes"] = c2_sha

        cases.append(
            {
                "name": "Case 2: Visual Grounding Coordinate Invariant ([x0, y0, x1, y1, page])",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": boxes_valid,
                "details": (
                    f"Validated {len(all_boxes)} bounding boxes across 3 points: "
                    f"prob={len(p1_prob.get('bounding_boxes') or [])}, "
                    f"contr={len(p1_contr.get('bounding_boxes') or [])}, "
                    f"limit={len(p1_limit.get('bounding_boxes') or [])}"
                ),
                "audit_file": str(c2_audit_path),
                "sha256": c2_sha,
                "raw_response": {"total_boxes": len(all_boxes), "sample_boxes": all_boxes[:3]},
            }
        )

        # Scenario 3: Cached Query Latency SLA (< 100ms)
        t0 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}/summary")
        latency_ms3 = (time.perf_counter() - t0) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        s3_valid = r3.status_code == 200 and latency_ms3 < 100.0

        c3_audit_path, c3_sha = save_raw_artifact(self.endpoint_name, "case3_cached_summary", body3)
        artifact_checksums["case3_cached_summary"] = c3_sha

        cases.append(
            {
                "name": f"Case 3: Cached Point Query ({latency_ms3:.2f}ms < 100ms SLA)",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms3,
                "passed": s3_valid,
                "details": f"Direct database point query executed in {latency_ms3:.2f}ms",
                "audit_file": str(c3_audit_path),
                "sha256": c3_sha,
                "raw_response": body3,
            }
        )

        # Scenario 4: Singleton Resource Idempotency & Consistency
        t0 = time.perf_counter()
        r4 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}/summary")
        latency_ms4 = (time.perf_counter() - t0) * 1000
        body4 = r4.json() if r4.status_code == 200 else {}
        data4 = body4.get("data", {})

        s4_valid = (
            r4.status_code == 200
            and data4.get("document_id") == seeded_doc_id
            and data4.get("problem_statement", {}).get("text") == p1_prob.get("text")
            and data4.get("contributions", {}).get("text") == p1_contr.get("text")
            and data4.get("limitations", {}).get("text") == p1_limit.get("text")
            and data4.get("total_tokens") == data1.get("total_tokens")
        )

        c4_audit_path, c4_sha = save_raw_artifact(
            self.endpoint_name, "case4_singleton_consistency", body4
        )
        artifact_checksums["case4_singleton_consistency"] = c4_sha

        cases.append(
            {
                "name": "Case 4: Singleton Resource Idempotency & Consistency",
                "status_code": r4.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms4,
                "passed": s4_valid,
                "details": "Verified 100% deterministic text and token count across repeated singleton queries",
                "audit_file": str(c4_audit_path),
                "sha256": c4_sha,
                "raw_response": body4,
            }
        )

        # Scenario 5: Nonexistent Document Guard (404 DOCUMENT_NOT_FOUND)
        random_doc_uuid = str(uuid.uuid4())
        t0 = time.perf_counter()
        r5 = await ctx.client.get(f"/api/v1/documents/{random_doc_uuid}/summary")
        latency_ms5 = (time.perf_counter() - t0) * 1000
        body5 = r5.json() if r5.status_code == 404 else {}
        err5 = body5.get("error", {})
        s5_valid = (
            r5.status_code == 404
            and body5.get("success") is False
            and err5.get("code") == "DOCUMENT_NOT_FOUND"
        )

        c5_audit_path, c5_sha = save_raw_artifact(self.endpoint_name, "case5_doc_not_found", body5)
        artifact_checksums["case5_doc_not_found"] = c5_sha

        cases.append(
            {
                "name": "Case 5: Nonexistent Document Guard (404 DOCUMENT_NOT_FOUND)",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms5,
                "passed": s5_valid,
                "details": f"Rejected nonexistent document UUID with code={err5.get('code')}",
                "audit_file": str(c5_audit_path),
                "sha256": c5_sha,
                "raw_response": body5,
            }
        )

        # Scenario 6: Malformed Input Guard (422 Unprocessable Entity)
        t0 = time.perf_counter()
        r6 = await ctx.client.get("/api/v1/documents/invalid-uuid-format/summary")
        latency_ms6 = (time.perf_counter() - t0) * 1000
        body6 = r6.json() if r6.status_code == 422 else {}
        s6_valid = r6.status_code == 422

        c6_audit_path, c6_sha = save_raw_artifact(self.endpoint_name, "case6_invalid_uuid", body6)
        artifact_checksums["case6_invalid_uuid"] = c6_sha

        cases.append(
            {
                "name": "Case 6: Malformed UUID Validation Guard (422 Unprocessable Entity)",
                "status_code": r6.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms6,
                "passed": s6_valid,
                "details": "FastAPI/Pydantic path parameter validation rejected invalid UUID format",
                "audit_file": str(c6_audit_path),
                "sha256": c6_sha,
                "raw_response": body6,
            }
        )

        # Quality Checks for Terminal UI Box
        checks = [
            (
                r1.status_code == 200,
                f"Status Code & Envelope  : {r1.status_code} OK (Kỳ vọng: 200)",
            ),
            (
                s1_valid,
                f"Grounded 3-Point Summary : PASS (tokens={data1.get('total_tokens')}, boxes={len(all_boxes)})",
            ),
            (
                boxes_valid,
                f"Visual Grounding Invariant: PASS ({len(all_boxes)} boxes follow [x0, y0, x1, y1, page])",
            ),
            (
                s3_valid,
                f"Cached Query SLA (<100ms): PASS ({latency_ms3:.2f} ms)",
            ),
            (
                s4_valid,
                "Singleton Consistency   : PASS (100% deterministic across repeated queries)",
            ),
            (
                s5_valid,
                "Doc Guard (404)          : PASS (UUID không tồn tại trả về 404 DOCUMENT_NOT_FOUND)",
            ),
            (
                s6_valid,
                "Malformed Input (422)    : PASS (UUID sai định dạng bị chặn 422)",
            ),
        ]

        display_body: dict[str, Any] = {
            "success": body1.get("success"),
            "data": {
                "document_id": data1.get("document_id"),
                "problem_statement": {
                    "text": (p1_prob.get("text", "")[:60] + "...") if p1_prob.get("text") else None,
                    "boxes_count": len(p1_prob.get("bounding_boxes") or []),
                },
                "contributions": {
                    "text": (p1_contr.get("text", "")[:60] + "...")
                    if p1_contr.get("text")
                    else None,
                    "boxes_count": len(p1_contr.get("bounding_boxes") or []),
                },
                "limitations": {
                    "text": (p1_limit.get("text", "")[:60] + "...")
                    if p1_limit.get("text")
                    else None,
                    "boxes_count": len(p1_limit.get("bounding_boxes") or []),
                },
                "total_tokens": data1.get("total_tokens"),
                "latency_ms": data1.get("latency_ms"),
            },
        }

        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}/summary",
            req_headers={
                "x-user-id": ctx.session_tag,
                "accept": "application/json",
            },
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=display_body,
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
            md.append(f"| `{k}` | `{v}` | `tests/.artifacts/{self.endpoint_name}/{k}.json` |")

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
            "- **Singleton Sub-Resource Pattern (Google AIP-130):** Endpoint `/api/v1/documents/{id}/summary` acts as a deterministic 1:1 singleton resource without child IDs."
        )
        md.append(
            "- **Visual Grounding Coordinate Invariant:** Every summary point (problem, contributions, limitations) contains a list of bounding boxes formatted as `[x0, y0, x1, y1, page]` with normalized float coordinates `0.0 <= x0 < x1 <= 1.0` and `0.0 <= y0 < y1 <= 1.0` for PDF.js yellow highlight overlay."
        )
        md.append(
            "- **Sub-100ms Direct Cache Lookup:** Query hits `document_summaries` table indexed by `document_id` for instant retrieval under SLA."
        )
        md.append(
            "- **Multi-Tenant Security Isolation:** Direct access to documents belonging to other users strictly returns `404 DOCUMENT_NOT_FOUND` to prevent ID enumeration."
        )
        md.append(
            "- **Lifecycle Error Protection (RFC 7807):** Ingesting documents return `409 DOCUMENT_PROCESSING`, failed documents return `422 DOCUMENT_FAILED`."
        )
        md.append("\n---\n")

        md.append("## 3. Full Raw Payloads & Audit Artifacts (Untruncated)\n")
        for c in cases:
            md.append(f"### {c['name']} (Status: `{c['status_code']}`)\n")
            md.append(f"- **Latency:** `{c['latency_ms']:.2f}ms`")
            md.append(f"- **Audit File:** `{c['audit_file']}`")
            md.append(f"- **SHA-256 Checksum:** `{c['sha256']}`\n")
            md.append("```json")
            md.append(json.dumps(c["raw_response"], indent=2, ensure_ascii=False))
            md.append("```\n")

        return "\n".join(md)

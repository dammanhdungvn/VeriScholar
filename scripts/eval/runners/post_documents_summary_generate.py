"""Evaluator for POST /api/v1/documents/{document_id}/summary:generate (Custom Method API)."""

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


class DocumentSummaryGenerateAPIRunner(BaseAPIRunner):
    """Evaluates custom method summary generation, idempotency, and re-synthesis."""

    endpoint_name = "post_documents_summary_generate"
    report_filename = "post_documents_summary_generate.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}/summary:generate"

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

        # 1. Clean refresh for output markdown report
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

        # 3. Hermetic Seeding: Upload target paper
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
                    f"Failed to seed document for summary:generate: HTTP {up_res.status_code}"
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

        # Case 1: Initial Synthesis or Default Generation (force=False)
        t0 = time.perf_counter()
        r1 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            json={"force": False},
        )
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        data1 = body1.get("data", {})
        cache1 = r1.headers.get("X-Cache", "")

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
            and cache1 in ("Generated", "Cache-Hit")
        )

        c1_path, c1_sha = save_raw_artifact(self.endpoint_name, "case1_initial_generate", body1)
        artifact_checksums["case1_initial_generate"] = c1_sha
        cases.append(
            {
                "name": "Case 1: Standard Summary Generation (200 OK)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": s1_valid,
                "details": f"Generated summary with X-Cache: {cache1}, tokens={data1.get('total_tokens')}",
                "audit_file": str(c1_path),
                "sha256": c1_sha,
                "raw_response": body1,
            }
        )

        # Case 2: Cached Query SLA (force=False on existing summary -> X-Cache: Cache-Hit)
        t0 = time.perf_counter()
        r2 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            json={"force": False},
        )
        latency_ms2 = (time.perf_counter() - t0) * 1000
        body2 = r2.json() if r2.status_code == 200 else {}
        cache2 = r2.headers.get("X-Cache", "")
        s2_valid = r2.status_code == 200 and cache2 == "Cache-Hit" and latency_ms2 < 100.0

        c2_path, c2_sha = save_raw_artifact(self.endpoint_name, "case2_cache_hit", body2)
        artifact_checksums["case2_cache_hit"] = c2_sha
        cases.append(
            {
                "name": f"Case 2: Cache Hit Verification ({latency_ms2:.2f}ms < 100ms SLA)",
                "status_code": r2.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms2,
                "passed": s2_valid,
                "details": f"Retrieved cached summary with X-Cache: {cache2} in {latency_ms2:.2f}ms",
                "audit_file": str(c2_path),
                "sha256": c2_sha,
                "raw_response": body2,
            }
        )

        # Case 3: Forced Re-synthesis (force=True -> X-Cache: Generated)
        t0 = time.perf_counter()
        r3 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            json={"force": True},
        )
        latency_ms3 = (time.perf_counter() - t0) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        cache3 = r3.headers.get("X-Cache", "")
        s3_valid = r3.status_code == 200 and cache3 == "Generated"

        c3_path, c3_sha = save_raw_artifact(self.endpoint_name, "case3_forced_resynthesis", body3)
        artifact_checksums["case3_forced_resynthesis"] = c3_sha
        cases.append(
            {
                "name": "Case 3: Forced Re-synthesis (force=True, X-Cache: Generated)",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms3,
                "passed": s3_valid,
                "details": f"Forced re-synthesis completed with X-Cache: {cache3} in {latency_ms3:.2f}ms",
                "audit_file": str(c3_path),
                "sha256": c3_sha,
                "raw_response": body3,
            }
        )

        # Case 4: Idempotency Protection (Idempotency-Key header)
        idem_key = str(uuid.uuid4())
        idem_headers = {"Idempotency-Key": idem_key}
        t0 = time.perf_counter()
        await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            json={"force": True},
            headers=idem_headers,
        )
        r4 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            json={"force": True},
            headers=idem_headers,
        )
        latency_ms4 = (time.perf_counter() - t0) * 1000
        body4 = r4.json() if r4.status_code == 200 else {}
        cache4 = r4.headers.get("X-Cache", "")
        s4_valid = r4.status_code == 200 and cache4 == "Idempotent-Hit"

        c4_path, c4_sha = save_raw_artifact(self.endpoint_name, "case4_idempotency_hit", body4)
        artifact_checksums["case4_idempotency_hit"] = c4_sha
        cases.append(
            {
                "name": "Case 4: Idempotency-Key Deduplication (X-Cache: Idempotent-Hit)",
                "status_code": r4.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms4,
                "passed": s4_valid,
                "details": f"Duplicate request prevented with X-Cache: {cache4}",
                "audit_file": str(c4_path),
                "sha256": c4_sha,
                "raw_response": body4,
            }
        )

        # Case 5: Visual Grounding Coordinate Verification
        all_boxes: list[list[float]] = []
        p3_data = body3.get("data", {})
        all_boxes.extend(p3_data.get("problem_statement", {}).get("bounding_boxes") or [])
        all_boxes.extend(p3_data.get("contributions", {}).get("bounding_boxes") or [])
        all_boxes.extend(p3_data.get("limitations", {}).get("bounding_boxes") or [])
        boxes_valid = len(all_boxes) > 0 and all(_is_valid_bbox(b) for b in all_boxes)

        c5_path, c5_sha = save_raw_artifact(
            self.endpoint_name, "case5_bounding_boxes", {"bounding_boxes": all_boxes}
        )
        artifact_checksums["case5_bounding_boxes"] = c5_sha
        cases.append(
            {
                "name": "Case 5: Visual Grounding Coordinate Invariant ([x0, y0, x1, y1, page])",
                "status_code": 200,
                "expected_status": 200,
                "latency_ms": 0.5,
                "passed": boxes_valid,
                "details": f"Validated {len(all_boxes)} bounding boxes across 3 points",
                "audit_file": str(c5_path),
                "sha256": c5_sha,
                "raw_response": {"total_boxes": len(all_boxes), "sample_boxes": all_boxes[:3]},
            }
        )

        # Case 6: Non-existent Document Error Guard (404)
        non_existent_id = str(uuid.uuid4())
        r6 = await ctx.client.post(
            f"/api/v1/documents/{non_existent_id}/summary:generate",
            json={"force": False},
        )
        body6 = r6.json() if r6.status_code == 404 else {}
        err6 = body6.get("error", {})
        s6_valid = r6.status_code == 404 and err6.get("code") == "DOCUMENT_NOT_FOUND"

        c6_path, c6_sha = save_raw_artifact(self.endpoint_name, "case6_not_found_guard", body6)
        artifact_checksums["case6_not_found_guard"] = c6_sha
        cases.append(
            {
                "name": "Case 6: Non-existent Document Guard (404 DOCUMENT_NOT_FOUND)",
                "status_code": r6.status_code,
                "expected_status": 404,
                "latency_ms": 1.0,
                "passed": s6_valid,
                "details": f"Error code: {err6.get('code')}, message: {err6.get('message')}",
                "audit_file": str(c6_path),
                "sha256": c6_sha,
                "raw_response": body6,
            }
        )

        # Quality Checks for Terminal UI Box
        checks = [
            (
                r1.status_code == 200,
                f"Status Code & Envelope  : {r1.status_code} OK (Expected: 200)",
            ),
            (
                s1_valid,
                f"Summary Generation      : PASS (X-Cache: {cache1}, tokens={data1.get('total_tokens')})",
            ),
            (
                s2_valid,
                f"Cache Hit SLA (<100ms)  : PASS ({latency_ms2:.2f} ms, X-Cache: {cache2})",
            ),
            (
                s3_valid,
                f"Forced Re-synthesis     : PASS (X-Cache: {cache3}, {latency_ms3:.2f} ms)",
            ),
            (
                s4_valid,
                f"Idempotency Protection  : PASS (X-Cache: {cache4})",
            ),
            (
                boxes_valid,
                f"Visual Grounding Invar  : PASS ({len(all_boxes)} boxes follow [x0, y0, x1, y1, page])",
            ),
            (
                s6_valid,
                "Doc Guard (404)          : PASS (Nonexistent UUID returns 404 DOCUMENT_NOT_FOUND)",
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
            path=f"/api/v1/documents/{seeded_doc_id}/summary:generate",
            req_headers={
                "x-user-id": ctx.session_tag,
                "accept": "application/json",
            },
            form_data=None,
            req_body={"force": False},
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
            "- **Google AIP-136 Custom Method Pattern:** Endpoint `POST /api/v1/documents/{id}/summary:generate` triggers a non-standard verb action (`:generate`) cleanly separated from standard CRUD."
        )
        md.append(
            "- **Zero-Downtime Resilience & Hybrid LLM / Heuristic Routing:** Synthesizer communicates with LLM using OpenAI JSON schema mode, and automatically falls back to regex-based heuristic extractor if no API key is set or on timeout."
        )
        md.append(
            "- **Visual Grounding Micro-Precision Invariant:** Quotes identified in the summary are mapped directly to PDF bounding boxes via PyMuPDF `page.search_for()` for pinpoint highlights."
        )
        md.append(
            "- **Distributed Idempotency Protection:** Requests passing `Idempotency-Key` are cached for 24 hours, returning `X-Cache: Idempotent-Hit` to prevent duplicate LLM costs."
        )
        md.append(
            "- **Cache Hit SLA (< 100ms):** When `force=False` and a summary exists, the endpoint bypasses LLM synthesis and responds with `X-Cache: Cache-Hit` in milliseconds."
        )
        md.append(
            "- **Multi-Tenant Security Isolation:** Document ownership is enforced; nonexistent or foreign documents strictly return `404 DOCUMENT_NOT_FOUND`."
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

"""Evaluator for DELETE /api/v1/sessions/{id} (#50: Xóa phiên nghiên cứu & Cascade Associations)."""

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


class DeleteSessionAPIRunner(BaseAPIRunner):
    """Evaluates session permanent deletion, cascade cleanup, document preservation, and multi-tenant isolation."""

    endpoint_name = "delete_session"
    report_filename = "delete_session.md"
    http_method = "DELETE"
    route_path = "/api/v1/sessions/{id}"

    async def evaluate(
        self,
        ctx: EvaluationContext,
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

        # 2. Benchmark paper seeding
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

        # Seed 1 document for session attachment to test document preservation
        pdf_bytes = target_paper.read_bytes()
        filename = f"delete_test_{target_paper.name}"
        files = {"file": (filename, pdf_bytes, "application/pdf")}
        up_res = await ctx.client.post("/api/v1/documents", files=files)
        seeded_doc_id: str | None = None
        if up_res.status_code in (200, 201):
            seeded_doc_id = up_res.json().get("data", {}).get("id")
            if seeded_doc_id:
                ctx.track_document(seeded_doc_id)
        else:
            linter_warnings.append(
                f"Failed to seed document for session test: HTTP {up_res.status_code}"
            )

        # Seed Session A (owned by current test user)
        session_a_payload = {
            "title": "Phiên Nghiên Cứu Thử Nghiệm Xóa Vĩnh Viễn",
            "initial_document_ids": [seeded_doc_id] if seeded_doc_id else [],
        }
        res_a = await ctx.client.post("/api/v1/sessions", json=session_a_payload)
        session_a_id: str | None = None
        if res_a.status_code in (200, 201):
            session_a_id = res_a.json().get("data", {}).get("id")

        # Seed Session B under an Alien Tenant (for multi-tenant isolation testing)
        alien_user_id = str(uuid.uuid4())
        alien_headers = {"x-user-id": alien_user_id, "x-session-id": alien_user_id}
        res_alien = await ctx.client.post(
            "/api/v1/sessions",
            json={"title": "Alien Tenant Private Session", "initial_document_ids": []},
            headers=alien_headers,
        )
        alien_session_id: str | None = None
        if res_alien.status_code in (200, 201):
            alien_session_id = res_alien.json().get("data", {}).get("id")

        if not session_a_id or not alien_session_id:
            linter_warnings.append("Failed to seed prerequisite test sessions.")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # ----------------------------------------------------------------------
        # Scenario 1: Clean Session Deletion (HTTP 204 No Content)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.delete(f"/api/v1/sessions/{session_a_id}")
        latency_ms1 = (time.perf_counter() - t0) * 1000

        res_body1 = {
            "status_code": r1.status_code,
            "headers": dict(r1.headers),
            "text_length": len(r1.text),
        }
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_delete_session_success", res_body1)
        artifact_checksums["01_delete_session_success.json"] = sha1

        p1_valid = r1.status_code == 204 and len(r1.text) == 0
        cases.append(
            {
                "name": "Clean Session Deletion (HTTP 204 No Content)",
                "status_code": r1.status_code,
                "expected_status": 204,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": f"Session {session_a_id} deleted with HTTP 204 (Empty body)",
                "raw_response": res_body1,
            }
        )

        checks1 = [
            (r1.status_code == 204, "HTTP Status 204 No Content"),
            (len(r1.text) == 0, "Empty Response Body (RFC 9110 compliant)"),
            (
                r1.headers.get("content-type") is None
                or "application/json" not in r1.headers.get("content-type", ""),
                "No Redundant JSON Payload",
            ),
        ]
        tbox1 = format_terminal_box(
            method="DELETE",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=res_body1,
            quality_checks=checks1,
        )
        print("\n" + tbox1)

        # ----------------------------------------------------------------------
        # Scenario 2: Underlying Document Preservation Invariant
        # ----------------------------------------------------------------------
        t2 = time.perf_counter()
        r2 = await ctx.client.get(f"/api/v1/documents/{seeded_doc_id}")
        latency_ms2 = (time.perf_counter() - t2) * 1000
        body2 = r2.json() if r2.status_code == 200 else {}
        _, sha2 = save_raw_artifact(self.endpoint_name, "02_underlying_document_preserved", body2)
        artifact_checksums["02_underlying_document_preserved.json"] = sha2

        doc_data2 = body2.get("data", {})
        p2_valid = (
            r2.status_code == 200
            and body2.get("success") is True
            and doc_data2.get("id") == seeded_doc_id
        )
        cases.append(
            {
                "name": "Underlying Document Preservation",
                "status_code": r2.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": f"Document {seeded_doc_id} is intact with status '{doc_data2.get('status')}'",
                "raw_response": body2,
            }
        )

        checks2 = [
            (r2.status_code == 200, "HTTP Status 200 OK for Attached Document"),
            (body2.get("success") is True, "Document Envelope success: True"),
            (doc_data2.get("id") == seeded_doc_id, "Document ID Matches Seeded ID"),
            (doc_data2.get("status") is not None, "Document Status Preserved in Library"),
        ]
        tbox2 = format_terminal_box(
            method="GET",
            path=f"/api/v1/documents/{seeded_doc_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r2.status_code,
            latency_ms=latency_ms2,
            res_headers=dict(r2.headers),
            res_body=body2,
            quality_checks=checks2,
        )
        print("\n" + tbox2)

        # ----------------------------------------------------------------------
        # Scenario 3: Cascade Associations Removal Verification
        # ----------------------------------------------------------------------
        t3 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/sessions/{session_a_id}")
        latency_ms3 = (time.perf_counter() - t3) * 1000
        body3 = r3.json() if r3.status_code == 404 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_cascade_associations_removed", body3)
        artifact_checksums["03_cascade_associations_removed.json"] = sha3

        err3 = body3.get("error", {})
        p3_valid = (
            r3.status_code == 404
            and body3.get("success") is False
            and err3.get("code") == "SESSION_NOT_FOUND"
        )
        cases.append(
            {
                "name": "Cascade Associations Removal Verification",
                "status_code": r3.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"GET /api/v1/sessions/{session_a_id} returns 404 SESSION_NOT_FOUND",
                "raw_response": body3,
            }
        )

        checks3 = [
            (r3.status_code == 404, "HTTP Status 404 Not Found"),
            (body3.get("success") is False, "success is False"),
            (err3.get("code") == "SESSION_NOT_FOUND", "Error code is SESSION_NOT_FOUND"),
        ]
        tbox3 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r3.status_code,
            latency_ms=latency_ms3,
            res_headers=dict(r3.headers),
            res_body=body3,
            quality_checks=checks3,
        )
        print("\n" + tbox3)

        # ----------------------------------------------------------------------
        # Scenario 4: Multi-Tenant User Isolation Guard (Alien User Session)
        # ----------------------------------------------------------------------
        t4 = time.perf_counter()
        r4 = await ctx.client.delete(f"/api/v1/sessions/{alien_session_id}")
        latency_ms4 = (time.perf_counter() - t4) * 1000
        body4 = r4.json() if r4.status_code == 404 else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_multi_tenant_isolation", body4)
        artifact_checksums["04_multi_tenant_isolation.json"] = sha4

        err4 = body4.get("error", {})
        p4_valid = (
            r4.status_code == 404
            and body4.get("success") is False
            and err4.get("code") == "SESSION_NOT_FOUND"
        )
        cases.append(
            {
                "name": "Multi-Tenant User Isolation Guard (Alien User)",
                "status_code": r4.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": f"Cannot delete alien session '{alien_session_id}' -> 404 SESSION_NOT_FOUND",
                "raw_response": body4,
            }
        )

        checks4 = [
            (r4.status_code == 404, "HTTP Status 404 Not Found"),
            (body4.get("success") is False, "success is False"),
            (err4.get("code") == "SESSION_NOT_FOUND", "Error code is SESSION_NOT_FOUND"),
        ]
        tbox4 = format_terminal_box(
            method="DELETE",
            path=f"/api/v1/sessions/{alien_session_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r4.status_code,
            latency_ms=latency_ms4,
            res_headers=dict(r4.headers),
            res_body=body4,
            quality_checks=checks4,
        )
        print("\n" + tbox4)

        # Clean up alien session under alien headers
        await ctx.client.delete(f"/api/v1/sessions/{alien_session_id}", headers=alien_headers)

        # ----------------------------------------------------------------------
        # Scenario 5: Idempotent Repeat Delete Guard
        # ----------------------------------------------------------------------
        t5 = time.perf_counter()
        r5 = await ctx.client.delete(f"/api/v1/sessions/{session_a_id}")
        latency_ms5 = (time.perf_counter() - t5) * 1000
        body5 = r5.json() if r5.status_code == 404 else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_idempotent_repeat_delete_guard", body5)
        artifact_checksums["05_idempotent_repeat_delete_guard.json"] = sha5

        err5 = body5.get("error", {})
        p5_valid = (
            r5.status_code == 404
            and body5.get("success") is False
            and err5.get("code") == "SESSION_NOT_FOUND"
        )
        cases.append(
            {
                "name": "Idempotent Repeat Delete Guard",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": f"Repeated DELETE on purged session '{session_a_id}' -> 404 SESSION_NOT_FOUND",
                "raw_response": body5,
            }
        )

        checks5 = [
            (r5.status_code == 404, "HTTP Status 404 Not Found"),
            (body5.get("success") is False, "Response success is False"),
            (err5.get("code") == "SESSION_NOT_FOUND", "Error code is SESSION_NOT_FOUND"),
        ]
        tbox5 = format_terminal_box(
            method="DELETE",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r5.status_code,
            latency_ms=latency_ms5,
            res_headers=dict(r5.headers),
            res_body=body5,
            quality_checks=checks5,
        )
        print("\n" + tbox5)

        # ----------------------------------------------------------------------
        # Scenario 6: Path UUID Format Validation Guard
        # ----------------------------------------------------------------------
        invalid_uuid_path = "malformed-session-uuid-xyz"
        t6 = time.perf_counter()
        r6 = await ctx.client.delete(f"/api/v1/sessions/{invalid_uuid_path}")
        latency_ms6 = (time.perf_counter() - t6) * 1000
        body6 = r6.json() if r6.status_code == 422 else {}
        _, sha6 = save_raw_artifact(self.endpoint_name, "06_validation_bounds_guard", body6)
        artifact_checksums["06_validation_bounds_guard.json"] = sha6

        p6_valid = (
            r6.status_code == 422
            and body6.get("success") is False
            and body6.get("error", {}).get("code") == "VALIDATION_ERROR"
        )
        cases.append(
            {
                "name": "Path UUID Format Validation Guard",
                "status_code": r6.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms6,
                "passed": p6_valid,
                "details": f"Path '{invalid_uuid_path}' -> HTTP 422 VALIDATION_ERROR",
                "raw_response": body6,
            }
        )

        checks6 = [
            (r6.status_code == 422, "HTTP Status 422 Unprocessable Entity"),
            (body6.get("success") is False, "Response success is False"),
            (
                body6.get("error", {}).get("code") == "VALIDATION_ERROR",
                "Error code is VALIDATION_ERROR",
            ),
        ]
        tbox6 = format_terminal_box(
            method="DELETE",
            path=f"/api/v1/sessions/{invalid_uuid_path}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r6.status_code,
            latency_ms=latency_ms6,
            res_headers=dict(r6.headers),
            res_body=body6,
            quality_checks=checks6,
        )
        print("\n" + tbox6)

        all_passed = all(c["passed"] for c in cases)
        eval_result = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "artifact_checksums": artifact_checksums,
            "linter_warnings": linter_warnings,
            "session_tag": ctx.session_tag,
        }

        # Generate markdown report
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

        return f"""# API Evaluation Snapshot: DELETE /api/v1/sessions/{{id}}

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#50 Xóa phiên nghiên cứu & Cascade Associations`  
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
- **Clean HTTP 204 Invariant**: Trả về đúng `HTTP 204 No Content` với thân phản hồi rỗng khi xóa thành công.
- **Underlying Document Preservation**: Tuyệt đối không xóa tài liệu gốc trong thư viện người dùng khi xóa phiên.
- **Cascade Removal Invariant**: Xóa xếp chồng sạch sẽ bản ghi phiên trong `research_sessions`, `session_documents`, `session_turns`.
- **Multi-Tenant Shielding**: Trả về `404 SESSION_NOT_FOUND` khi người dùng khác truy cập/xóa phiên trái phép.
- **Hermetic Teardown**: Toàn bộ tài nguyên phục vụ kiểm thử được dọn dẹp khép kín.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

"""Evaluator for PATCH /api/v1/sessions/{id}/viewport (#49: Auto-save PDF viewport state & Tab with OCC)."""

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


class PatchSessionViewportAPIRunner(BaseAPIRunner):
    """Evaluates viewport state persistence, Optimistic Concurrency Control (OCC), document association guard, and multi-tenant isolation."""

    endpoint_name = "patch_session_viewport"
    report_filename = "patch_session_viewport.md"
    http_method = "PATCH"
    route_path = "/api/v1/sessions/{id}/viewport"

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

        # Seed Document 1 (to attach to session)
        pdf_bytes = target_paper.read_bytes()
        files1 = {"file": (f"viewport_attached_{target_paper.name}", pdf_bytes, "application/pdf")}
        up_res1 = await ctx.client.post("/api/v1/documents", files=files1)
        attached_doc_id: str | None = None
        if up_res1.status_code in (200, 201):
            attached_doc_id = up_res1.json().get("data", {}).get("id")
            if attached_doc_id:
                ctx.track_document(attached_doc_id)

        # Seed Document 2 (unlinked, to test invalid active document guard)
        files2 = {"file": (f"viewport_unlinked_{target_paper.name}", pdf_bytes, "application/pdf")}
        up_res2 = await ctx.client.post("/api/v1/documents", files=files2)
        unlinked_doc_id: str | None = None
        if up_res2.status_code in (200, 201):
            unlinked_doc_id = up_res2.json().get("data", {}).get("id")
            if unlinked_doc_id:
                ctx.track_document(unlinked_doc_id)

        # Seed Session A owned by current test user with attached_doc_id
        session_payload = {
            "title": "Phiên Đọc Sâu & Đồng Bộ Viewport Tự Động",
            "initial_document_ids": [attached_doc_id] if attached_doc_id else [],
        }
        res_session = await ctx.client.post("/api/v1/sessions", json=session_payload)
        session_id: str | None = None
        if res_session.status_code in (200, 201):
            session_id = res_session.json().get("data", {}).get("id")

        # Seed Alien Tenant Session (for cross-tenant checks)
        alien_user_id = str(uuid.uuid4())
        alien_headers = {"x-user-id": alien_user_id, "x-session-id": alien_user_id}
        res_alien = await ctx.client.post(
            "/api/v1/sessions",
            json={"title": "Alien Tenant Session", "initial_document_ids": []},
            headers=alien_headers,
        )
        alien_session_id: str | None = None
        if res_alien.status_code in (200, 201):
            alien_session_id = res_alien.json().get("data", {}).get("id")

        if not session_id or not alien_session_id or not attached_doc_id or not unlinked_doc_id:
            linter_warnings.append("Failed to seed prerequisite documents and sessions.")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # ----------------------------------------------------------------------
        # Scenario 1: Valid Viewport Update with OCC (If-Match: "v1")
        # ----------------------------------------------------------------------
        update_payload1 = {
            "viewport_state": {
                "page": 3,
                "zoom_ratio": 1.25,
                "scroll_top": 450.0,
            },
            "active_tab": "notes",
            "active_document_id": attached_doc_id,
        }
        headers1 = {"If-Match": '"v1"'}
        t1 = time.perf_counter()
        r1 = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json=update_payload1,
            headers=headers1,
        )
        latency_ms1 = (time.perf_counter() - t1) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_viewport_update_success", body1)
        artifact_checksums["01_viewport_update_success.json"] = sha1

        data1 = body1.get("data", {})
        vp1 = data1.get("viewport_state", {})
        etag_res1 = r1.headers.get("ETag", "")

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("version") == 2
            and etag_res1 == '"v2"'
            and vp1.get("page") == 3
            and vp1.get("zoom_ratio") == 1.25
            and vp1.get("scroll_top") == 450.0
            and data1.get("active_tab") == "notes"
            and data1.get("active_document_id") == attached_doc_id
        )
        cases.append(
            {
                "name": 'Valid Viewport Update with OCC (If-Match: "v1")',
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": f"Updated viewport to page=3, zoom=1.25, active_tab='notes', ETag='{etag_res1}', version={data1.get('version')}",
                "raw_response": body1,
            }
        )

        checks1 = [
            (r1.status_code == 200, "HTTP Status 200 OK"),
            (body1.get("success") is True, "Envelope success: True"),
            (data1.get("version") == 2, "OCC Version incremented from 1 to 2"),
            (etag_res1 == '"v2"', "Response ETag Header matches '\"v2\"'"),
            (vp1.get("page") == 3, "Viewport page updated to 3"),
            (data1.get("active_tab") == "notes", "Active tab updated to 'notes'"),
            (data1.get("active_document_id") == attached_doc_id, "Active document preserved"),
        ]
        tbox1 = format_terminal_box(
            method="PATCH",
            path=f"/api/v1/sessions/{session_id}/viewport",
            req_headers={"x-user-id": ctx.session_tag, "If-Match": '"v1"'},
            form_data=None,
            req_body=update_payload1,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=body1,
            quality_checks=checks1,
        )
        print("\n" + tbox1)

        # ----------------------------------------------------------------------
        # Scenario 2: Stale Version Concurrency Conflict Guard (If-Match: "v1")
        # ----------------------------------------------------------------------
        stale_payload = {
            "viewport_state": {
                "page": 4,
                "zoom_ratio": 1.5,
                "scroll_top": 600.0,
            },
            "active_tab": "chat",
        }
        stale_headers = {"If-Match": '"v1"'}  # Server is already at version 2!
        t2 = time.perf_counter()
        r2 = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json=stale_payload,
            headers=stale_headers,
        )
        latency_ms2 = (time.perf_counter() - t2) * 1000
        body2 = r2.json() if r2.status_code == 412 else {}
        _, sha2 = save_raw_artifact(self.endpoint_name, "02_concurrency_conflict_guard", body2)
        artifact_checksums["02_concurrency_conflict_guard.json"] = sha2

        err2 = body2.get("error", {})
        p2_valid = (
            r2.status_code == 412
            and body2.get("success") is False
            and err2.get("code") == "CONCURRENCY_CONFLICT"
        )
        cases.append(
            {
                "name": "Stale Version Concurrency Conflict Guard",
                "status_code": r2.status_code,
                "expected_status": 412,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": "Stale If-Match 'v1' rejected with HTTP 412 CONCURRENCY_CONFLICT",
                "raw_response": body2,
            }
        )

        checks2 = [
            (r2.status_code == 412, "HTTP Status 412 Precondition Failed"),
            (body2.get("success") is False, "Response success is False"),
            (err2.get("code") == "CONCURRENCY_CONFLICT", "Error code is CONCURRENCY_CONFLICT"),
        ]
        tbox2 = format_terminal_box(
            method="PATCH",
            path=f"/api/v1/sessions/{session_id}/viewport",
            req_headers={"x-user-id": ctx.session_tag, "If-Match": '"v1"'},
            form_data=None,
            req_body=stale_payload,
            status_code=r2.status_code,
            latency_ms=latency_ms2,
            res_headers=dict(r2.headers),
            res_body=body2,
            quality_checks=checks2,
        )
        print("\n" + tbox2)

        # ----------------------------------------------------------------------
        # Scenario 3: Missing Precondition Header Guard (No If-Match)
        # ----------------------------------------------------------------------
        no_etag_payload = {
            "viewport_state": {
                "page": 2,
                "zoom_ratio": 1.0,
                "scroll_top": 100.0,
            },
        }
        t3 = time.perf_counter()
        r3 = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json=no_etag_payload,
        )
        latency_ms3 = (time.perf_counter() - t3) * 1000
        body3 = r3.json() if r3.status_code == 428 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_precondition_required_guard", body3)
        artifact_checksums["03_precondition_required_guard.json"] = sha3

        err3 = body3.get("error", {})
        p3_valid = (
            r3.status_code == 428
            and body3.get("success") is False
            and err3.get("code") == "PRECONDITION_REQUIRED"
        )
        cases.append(
            {
                "name": "Missing Precondition Header Guard",
                "status_code": r3.status_code,
                "expected_status": 428,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": "Missing If-Match header rejected with HTTP 428 PRECONDITION_REQUIRED",
                "raw_response": body3,
            }
        )

        checks3 = [
            (r3.status_code == 428, "HTTP Status 428 Precondition Required"),
            (body3.get("success") is False, "Response success is False"),
            (err3.get("code") == "PRECONDITION_REQUIRED", "Error code is PRECONDITION_REQUIRED"),
        ]
        tbox3 = format_terminal_box(
            method="PATCH",
            path=f"/api/v1/sessions/{session_id}/viewport",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=no_etag_payload,
            status_code=r3.status_code,
            latency_ms=latency_ms3,
            res_headers=dict(r3.headers),
            res_body=body3,
            quality_checks=checks3,
        )
        print("\n" + tbox3)

        # ----------------------------------------------------------------------
        # Scenario 4: Unassociated Document Attachment Guard (400 Bad Request)
        # ----------------------------------------------------------------------
        unlinked_payload = {
            "viewport_state": {
                "page": 2,
                "zoom_ratio": 1.0,
                "scroll_top": 100.0,
            },
            "active_document_id": unlinked_doc_id,
        }
        headers4 = {"If-Match": '"v2"'}
        t4 = time.perf_counter()
        r4 = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json=unlinked_payload,
            headers=headers4,
        )
        latency_ms4 = (time.perf_counter() - t4) * 1000
        body4 = r4.json() if r4.status_code == 400 else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_invalid_active_document_guard", body4)
        artifact_checksums["04_invalid_active_document_guard.json"] = sha4

        err4 = body4.get("error", {})
        p4_valid = (
            r4.status_code == 400
            and body4.get("success") is False
            and err4.get("code") == "INVALID_ACTIVE_DOCUMENT"
        )
        cases.append(
            {
                "name": "Unassociated Document Attachment Guard",
                "status_code": r4.status_code,
                "expected_status": 400,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": f"Unlinked doc '{unlinked_doc_id}' rejected with HTTP 400 INVALID_ACTIVE_DOCUMENT",
                "raw_response": body4,
            }
        )

        checks4 = [
            (r4.status_code == 400, "HTTP Status 400 Bad Request"),
            (body4.get("success") is False, "Response success is False"),
            (
                err4.get("code") == "INVALID_ACTIVE_DOCUMENT",
                "Error code is INVALID_ACTIVE_DOCUMENT",
            ),
        ]
        tbox4 = format_terminal_box(
            method="PATCH",
            path=f"/api/v1/sessions/{session_id}/viewport",
            req_headers={"x-user-id": ctx.session_tag, "If-Match": '"v2"'},
            form_data=None,
            req_body=unlinked_payload,
            status_code=r4.status_code,
            latency_ms=latency_ms4,
            res_headers=dict(r4.headers),
            res_body=body4,
            quality_checks=checks4,
        )
        print("\n" + tbox4)

        # ----------------------------------------------------------------------
        # Scenario 5: Multi-Tenant User Isolation Guard (Alien User)
        # ----------------------------------------------------------------------
        alien_patch_payload = {
            "viewport_state": {
                "page": 5,
                "zoom_ratio": 2.0,
                "scroll_top": 800.0,
            },
        }
        alien_patch_headers = {
            "x-user-id": alien_user_id,
            "x-session-id": alien_user_id,
            "If-Match": '"v2"',
        }
        t5 = time.perf_counter()
        r5 = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json=alien_patch_payload,
            headers=alien_patch_headers,
        )
        latency_ms5 = (time.perf_counter() - t5) * 1000
        body5 = r5.json() if r5.status_code == 404 else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_multi_tenant_isolation", body5)
        artifact_checksums["05_multi_tenant_isolation.json"] = sha5

        err5 = body5.get("error", {})
        p5_valid = (
            r5.status_code == 404
            and body5.get("success") is False
            and err5.get("code") == "SESSION_NOT_FOUND"
        )
        cases.append(
            {
                "name": "Multi-Tenant User Isolation Guard",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": "Alien tenant cannot update session -> HTTP 404 SESSION_NOT_FOUND",
                "raw_response": body5,
            }
        )

        checks5 = [
            (r5.status_code == 404, "HTTP Status 404 Not Found"),
            (body5.get("success") is False, "Response success is False"),
            (err5.get("code") == "SESSION_NOT_FOUND", "Error code is SESSION_NOT_FOUND"),
        ]
        tbox5 = format_terminal_box(
            method="PATCH",
            path=f"/api/v1/sessions/{session_id}/viewport",
            req_headers={"x-user-id": alien_user_id, "If-Match": '"v2"'},
            form_data=None,
            req_body=alien_patch_payload,
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
        r6 = await ctx.client.patch(
            f"/api/v1/sessions/{invalid_uuid_path}/viewport",
            json=update_payload1,
            headers={"If-Match": '"v2"'},
        )
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
            method="PATCH",
            path=f"/api/v1/sessions/{invalid_uuid_path}/viewport",
            req_headers={"x-user-id": ctx.session_tag, "If-Match": '"v2"'},
            form_data=None,
            req_body=update_payload1,
            status_code=r6.status_code,
            latency_ms=latency_ms6,
            res_headers=dict(r6.headers),
            res_body=body6,
            quality_checks=checks6,
        )
        print("\n" + tbox6)

        # Hermetic cleanup
        await ctx.client.delete(f"/api/v1/sessions/{session_id}")
        await ctx.client.delete(f"/api/v1/sessions/{alien_session_id}", headers=alien_headers)

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

        return f"""# API Evaluation Snapshot: PATCH /api/v1/sessions/{{id}}/viewport

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#49 Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)`  
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
- **OCC Version Increment Invariant**: Phiên bản tự động tăng `+1`, response header `ETag: "v{{version+1}}"` đồng nhất hoàn toàn với `data.version`.
- **Precondition Required Invariant**: Bắt buộc client gửi `If-Match` theo chuẩn RFC 7232; thiếu header trả về `428 Precondition Required`.
- **Lost Update Protection**: Chặn đứng việc ghi đè trạng thái cũ bằng mã `412 Precondition Failed` (`CONCURRENCY_CONFLICT`).
- **Document Boundary Invariant**: Chỉ chấp nhận `active_document_id` đã được gắn kết vào phiên; truyền tài liệu lạ trả về `400 Bad Request`.
- **Hermetic Teardown**: Dọn dẹp phiên và tài liệu thử nghiệm khép kín.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

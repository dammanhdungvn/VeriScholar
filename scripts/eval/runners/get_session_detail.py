"""Evaluator for GET /api/v1/sessions/{id} (#47: Khôi phục nguyên vẹn phiên - Snapshots, Tabs, Viewport)."""

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


class GetSessionDetailAPIRunner(BaseAPIRunner):
    """Evaluates session restoration, viewport state, OCC ETag conformance, and multi-tenant shielding."""

    endpoint_name = "get_session_detail"
    report_filename = "get_session_detail.md"
    http_method = "GET"
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

        # Seed 1 document for session attachment
        pdf_bytes = target_paper.read_bytes()
        filename = f"seed_{target_paper.name}"
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

        # Seed Session A (with attached document)
        session_a_payload = {
            "title": "Nghiên cứu Kiến trúc Transformer và Attention Mechanism",
            "initial_document_ids": [seeded_doc_id] if seeded_doc_id else [],
        }
        res_a = await ctx.client.post("/api/v1/sessions", json=session_a_payload)
        session_a_id: str | None = None
        if res_a.status_code in (200, 201):
            session_a_id = res_a.json().get("data", {}).get("id")
            if session_a_id:
                ctx.track_session(session_a_id)

        # Seed Session B (empty session without documents)
        session_b_payload = {
            "title": "Khởi tạo Phiên Trống Chưa Nạp Tài Liệu",
            "initial_document_ids": [],
        }
        res_b = await ctx.client.post("/api/v1/sessions", json=session_b_payload)
        session_b_id: str | None = None
        if res_b.status_code in (200, 201):
            session_b_id = res_b.json().get("data", {}).get("id")
            if session_b_id:
                ctx.track_session(session_b_id)

        if not session_a_id or not session_b_id:
            linter_warnings.append("Failed to seed prerequisite test sessions.")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # ----------------------------------------------------------------------
        # Scenario 1: Full Session Restoration (Snapshots, Tabs, Viewport)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/sessions/{session_a_id}")
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_full_session_restoration", body1)
        artifact_checksums["01_full_session_restoration.json"] = sha1

        data1 = body1.get("data", {})
        doc_ids1 = data1.get("document_ids", [])
        viewport1 = data1.get("viewport_state", {})
        documents1 = data1.get("documents", [])

        viewport_valid = (
            isinstance(viewport1, dict)
            and viewport1.get("page", 0) >= 1
            and viewport1.get("zoom_ratio", 0) > 0
            and viewport1.get("scroll_top", -1) >= 0
        )
        has_required_keys = {
            "id",
            "title",
            "document_ids",
            "active_document_id",
            "viewport_state",
            "active_tab",
            "is_archived",
            "version",
            "message_count",
            "documents",
            "created_at",
            "updated_at",
        }.issubset(data1.keys())

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and data1.get("id") == session_a_id
            and data1.get("title") == session_a_payload["title"]
            and viewport_valid
            and data1.get("active_tab") in ("chat", "notes", "summary", "graph", "draft")
            and data1.get("is_archived") is False
            and data1.get("version", 0) >= 1
            and has_required_keys
            and (seeded_doc_id in doc_ids1 if seeded_doc_id else True)
            and len(documents1) >= (1 if seeded_doc_id else 0)
        )
        cases.append(
            {
                "name": "Full Session Restoration (Snapshots, Tabs, Viewport)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": (
                    f"Session ID: {session_a_id} | Version: {data1.get('version')} | "
                    f"Documents: {len(documents1)} | Viewport valid: {viewport_valid} | Tab: {data1.get('active_tab')}"
                ),
                "raw_response": body1,
            }
        )

        checks1 = [
            (r1.status_code == 200, "HTTP Status 200 OK"),
            (body1.get("success") is True, "Response Envelope success: True"),
            (data1.get("id") == session_a_id, "Session ID Matches Requested Resource"),
            (viewport_valid, "Viewport State Restored (page, zoom_ratio, scroll_top)"),
            (has_required_keys, "Complete SessionResponseData Schema Conformity"),
            (len(documents1) >= (1 if seeded_doc_id else 0), "Attached Documents Restored"),
        ]
        tbox1 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=body1,
            quality_checks=checks1,
        )
        print("\n" + tbox1)

        # ----------------------------------------------------------------------
        # Scenario 2: ETag Header Conformance & OCC Version Lock
        # ----------------------------------------------------------------------
        etag_header = r1.headers.get("etag") or r1.headers.get("ETag")
        expected_version = data1.get("version", 1)
        expected_etag = f'"v{expected_version}"'

        etag_valid = etag_header is not None and etag_header.strip() == expected_etag
        etag_payload = {
            "etag_header": etag_header,
            "expected_etag": expected_etag,
            "session_version": expected_version,
            "rfc_9110_compliant": etag_valid,
        }
        _, sha2 = save_raw_artifact(self.endpoint_name, "02_etag_header_conformance", etag_payload)
        artifact_checksums["02_etag_header_conformance.json"] = sha2

        p2_valid = etag_valid and r1.status_code == 200
        cases.append(
            {
                "name": "ETag Header Conformance & OCC Version Lock",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p2_valid,
                "details": f"ETag Header: {etag_header} (Coincides with version {expected_version})",
                "raw_response": etag_payload,
            }
        )

        checks2 = [
            (etag_header is not None, "ETag Header Present in HTTP 200 Response"),
            (etag_valid, f"ETag Matches Expected RFC 9110 Format ({expected_etag})"),
            (expected_version >= 1, "Initial Session Version >= 1"),
        ]
        tbox2 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=etag_payload,
            quality_checks=checks2,
        )
        print("\n" + tbox2)

        # ----------------------------------------------------------------------
        # Scenario 3: Empty Session Restoration (No documents attached)
        # ----------------------------------------------------------------------
        t3 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/sessions/{session_b_id}")
        latency_ms3 = (time.perf_counter() - t3) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_empty_session_restoration", body3)
        artifact_checksums["03_empty_session_restoration.json"] = sha3

        data3 = body3.get("data", {})
        doc_ids3 = data3.get("document_ids", [])
        documents3 = data3.get("documents", [])
        active_doc3 = data3.get("active_document_id")
        msg_count3 = data3.get("message_count", 0)

        p3_valid = (
            r3.status_code == 200
            and body3.get("success") is True
            and data3.get("id") == session_b_id
            and len(doc_ids3) == 0
            and len(documents3) == 0
            and active_doc3 is None
            and msg_count3 == 0
        )
        cases.append(
            {
                "name": "Empty Session Restoration (No documents attached)",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": (
                    f"Session ID: {session_b_id} | Documents: {len(documents3)} | "
                    f"Active Document: {active_doc3} | Message Count: {msg_count3}"
                ),
                "raw_response": body3,
            }
        )

        checks3 = [
            (r3.status_code == 200, "HTTP Status 200 OK"),
            (len(doc_ids3) == 0, "document_ids is Empty List"),
            (len(documents3) == 0, "documents collection is Empty List"),
            (active_doc3 is None, "active_document_id is None"),
            (msg_count3 == 0, "message_count is 0"),
        ]
        tbox3 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{session_b_id}",
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
        # Scenario 4: Multi-Tenant User Isolation Guard (Alien User)
        # ----------------------------------------------------------------------
        alien_tenant_id = str(uuid.uuid4())
        alien_headers = {"x-user-id": alien_tenant_id, "x-session-id": alien_tenant_id}

        t4 = time.perf_counter()
        r4 = await ctx.client.get(f"/api/v1/sessions/{session_a_id}", headers=alien_headers)
        latency_ms4 = (time.perf_counter() - t4) * 1000
        body4 = r4.json() if r4.status_code == 404 else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_multi_tenant_isolation", body4)
        artifact_checksums["04_multi_tenant_isolation.json"] = sha4

        err4 = body4.get("error", {})
        is_shielded = (
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
                "passed": is_shielded,
                "details": f"Alien User '{alien_tenant_id}' received HTTP 404 SESSION_NOT_FOUND",
                "raw_response": body4,
            }
        )

        checks4 = [
            (r4.status_code == 404, "HTTP Status 404 Not Found"),
            (body4.get("success") is False, "success is False"),
            (err4.get("code") == "SESSION_NOT_FOUND", "Error code is SESSION_NOT_FOUND"),
        ]
        tbox4 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{session_a_id}",
            req_headers=alien_headers,
            form_data=None,
            req_body=None,
            status_code=r4.status_code,
            latency_ms=latency_ms4,
            res_headers=dict(r4.headers),
            res_body=body4,
            quality_checks=checks4,
        )
        print("\n" + tbox4)

        # ----------------------------------------------------------------------
        # Scenario 5: Non-Existent Session UUID Guard
        # ----------------------------------------------------------------------
        random_non_existent_uuid = str(uuid.uuid4())
        t5 = time.perf_counter()
        r5 = await ctx.client.get(f"/api/v1/sessions/{random_non_existent_uuid}")
        latency_ms5 = (time.perf_counter() - t5) * 1000
        body5 = r5.json() if r5.status_code == 404 else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_not_found_guard", body5)
        artifact_checksums["05_not_found_guard.json"] = sha5

        err5 = body5.get("error", {})
        p5_valid = (
            r5.status_code == 404
            and body5.get("success") is False
            and err5.get("code") == "SESSION_NOT_FOUND"
        )
        cases.append(
            {
                "name": "Non-existent Session UUID Guard",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": f"Non-existent UUID '{random_non_existent_uuid}' -> HTTP 404 SESSION_NOT_FOUND",
                "raw_response": body5,
            }
        )

        checks5 = [
            (r5.status_code == 404, "HTTP Status 404 Not Found"),
            (body5.get("success") is False, "Response success is False"),
            (err5.get("code") == "SESSION_NOT_FOUND", "Standardized error code: SESSION_NOT_FOUND"),
        ]
        tbox5 = format_terminal_box(
            method="GET",
            path=f"/api/v1/sessions/{random_non_existent_uuid}",
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
        invalid_uuid_path = "malformed-session-uuid-123"
        t6 = time.perf_counter()
        r6 = await ctx.client.get(f"/api/v1/sessions/{invalid_uuid_path}")
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
            method="GET",
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

        return f"""# API Evaluation Snapshot: GET /api/v1/sessions/{{id}}

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#47 Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)`  
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
- **OCC ETag Conformance Invariant**: HTTP 200 responses return `ETag: "v{{version}}"` matching the resource version for subsequent optimistic locking operations (`If-Match`).
- **Complete State Invariant**: Restores full workspace parameters (`viewport_state` with `page`, `zoom_ratio`, `scroll_top`), `active_tab`, and attached `documents`.
- **Multi-Tenant Shielding**: Unauthorized access attempts by other tenants receive `404 Not Found` with `SESSION_NOT_FOUND`, preventing resource enumeration.
- **Path UUID Validation**: Invalid UUID formats are rejected at routing boundary with HTTP 422 RFC 7807 problem details.
- **Hermetic REST Lifecycle**: Test sessions and documents are tracked and purged cleanly via standard REST endpoints upon teardown.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

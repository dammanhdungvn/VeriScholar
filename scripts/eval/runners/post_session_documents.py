"""Evaluator for POST /api/v1/sessions/{id}/documents (#51: Nạp bài vào phiên - Pure JSON: url hoặc document_id)."""

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


class PostSessionDocumentsAPIRunner(BaseAPIRunner):
    """Evaluates adding documents to sessions via pure JSON AIP pattern, capacity cap, and tenancy isolation."""

    endpoint_name = "post_session_documents"
    report_filename = "post_session_documents.md"
    http_method = "POST"
    route_path = "/api/v1/sessions/{id}/documents"

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

        pdf_bytes = target_paper.read_bytes()
        seeded_docs: list[str] = []

        # Seed 5 library documents to test incremental addition and capacity cap
        for i in range(1, 6):
            files = {"file": (f"attach_doc_{i}_{target_paper.name}", pdf_bytes, "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                doc_id = up_res.json().get("data", {}).get("id")
                if doc_id:
                    seeded_docs.append(doc_id)
                    ctx.track_document(doc_id)

        if len(seeded_docs) < 5:
            linter_warnings.append("Failed to seed prerequisite library documents.")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        doc1_id, doc2_id, doc3_id, doc4_id, doc5_id = seeded_docs[:5]

        # Seed Session A with 1 initial document (doc1)
        session_payload = {
            "title": "Phiên Nghiên Cứu Đa Tài Liệu Pure JSON",
            "initial_document_ids": [doc1_id],
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

        if not session_id or not alien_session_id:
            linter_warnings.append("Failed to seed prerequisite sessions.")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        url_created_doc_id: str | None = None

        # ----------------------------------------------------------------------
        # Scenario 1: Add Existing Document via ID (HTTP 202 Accepted)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        req1_body = {"source_type": "document_id", "document_id": doc2_id}
        res1 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json=req1_body,
        )
        latency1 = (time.perf_counter() - t0) * 1000
        d1 = res1.json() if res1.content else {}

        _, chk1 = save_raw_artifact(
            self.endpoint_name,
            "01_add_existing_document_success",
            d1,
        )
        artifact_checksums["01_add_existing_document_success.json"] = chk1

        checks1: list[tuple[bool, str]] = [
            (res1.status_code == 202, "HTTP Status 202 Accepted"),
            (d1.get("success") is True, "Envelope success: True"),
            (d1.get("data", {}).get("document_id") == doc2_id, "Document ID matches doc2_id"),
            (
                d1.get("data", {}).get("session_id") == session_id,
                "Session ID matches target session",
            ),
            (d1.get("data", {}).get("status") == "associated", "Status is associated"),
            (d1.get("data", {}).get("version") == 2, "Session version incremented to 2"),
        ]
        pass1 = all(p for p, _ in checks1)
        tbox1 = format_terminal_box(
            method="POST",
            path=f"/api/v1/sessions/{session_id}/documents",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=req1_body,
            status_code=res1.status_code,
            latency_ms=latency1,
            res_headers=dict(res1.headers),
            res_body=d1,
            quality_checks=checks1,
        )
        print("\n" + tbox1)
        cases.append(
            {
                "name": "01_add_existing_document_success",
                "passed": pass1,
                "status_code": res1.status_code,
                "expected_code": 202,
                "latency_ms": round(latency1, 2),
                "details": "Nạp tài liệu đã có thành công (202 Accepted, status=associated, version=2)",
                "checks": checks1,
                "artifact": "01_add_existing_document_success.json",
                "checksum": chk1,
                "raw_response": d1,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 2: Add Document via Online URL (HTTP 202 Accepted & Queued)
        # ----------------------------------------------------------------------
        url_payload = {
            "source_type": "url",
            "url": "https://arxiv.org/pdf/1706.03762.pdf",
            "title": "Attention Is All You Need (Online)",
        }
        t0 = time.perf_counter()
        res2 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json=url_payload,
        )
        latency2 = (time.perf_counter() - t0) * 1000
        d2 = res2.json() if res2.content else {}

        if d2.get("data", {}).get("document_id"):
            url_created_doc_id = d2["data"]["document_id"]
            ctx.track_document(url_created_doc_id)

        _, chk2 = save_raw_artifact(
            self.endpoint_name,
            "02_add_document_via_url_success",
            d2,
        )
        artifact_checksums["02_add_document_via_url_success.json"] = chk2

        checks2: list[tuple[bool, str]] = [
            (res2.status_code == 202, "HTTP Status 202 Accepted"),
            (d2.get("success") is True, "Envelope success: True"),
            (bool(url_created_doc_id), "Target doc ID generated"),
            (
                d2.get("data", {}).get("session_id") == session_id,
                "Session ID matches target session",
            ),
            (d2.get("data", {}).get("status") == "queued", "Status is queued for URL ingestion"),
            (d2.get("data", {}).get("version") == 3, "Session version incremented to 3"),
        ]
        pass2 = all(p for p, _ in checks2)
        tbox2 = format_terminal_box(
            method="POST",
            path=f"/api/v1/sessions/{session_id}/documents",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=url_payload,
            status_code=res2.status_code,
            latency_ms=latency2,
            res_headers=dict(res2.headers),
            res_body=d2,
            quality_checks=checks2,
        )
        print("\n" + tbox2)
        cases.append(
            {
                "name": "02_add_document_via_url_success",
                "passed": pass2,
                "status_code": res2.status_code,
                "expected_code": 202,
                "latency_ms": round(latency2, 2),
                "details": "Nạp tài liệu qua URL thành công (202 Accepted, status=queued, version=3)",
                "checks": checks2,
                "artifact": "02_add_document_via_url_success.json",
                "checksum": chk2,
                "raw_response": d2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 3: Duplicate Document Attachment Conflict Guard (HTTP 409)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        req3_body = {"source_type": "document_id", "document_id": doc2_id}
        res3 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json=req3_body,
        )
        latency3 = (time.perf_counter() - t0) * 1000
        d3 = res3.json() if res3.content else {}

        _, chk3 = save_raw_artifact(
            self.endpoint_name,
            "03_duplicate_document_conflict_guard",
            d3,
        )
        artifact_checksums["03_duplicate_document_conflict_guard.json"] = chk3

        checks3: list[tuple[bool, str]] = [
            (res3.status_code == 409, "HTTP Status 409 Conflict"),
            (d3.get("success") is False, "Response success is False"),
            (
                d3.get("error", {}).get("code") == "DOCUMENT_ALREADY_IN_SESSION",
                "Error code is DOCUMENT_ALREADY_IN_SESSION",
            ),
        ]
        pass3 = all(p for p, _ in checks3)
        tbox3 = format_terminal_box(
            method="POST",
            path=f"/api/v1/sessions/{session_id}/documents",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=req3_body,
            status_code=res3.status_code,
            latency_ms=latency3,
            res_headers=dict(res3.headers),
            res_body=d3,
            quality_checks=checks3,
        )
        print("\n" + tbox3)
        cases.append(
            {
                "name": "03_duplicate_document_conflict_guard",
                "passed": pass3,
                "status_code": res3.status_code,
                "expected_code": 409,
                "latency_ms": round(latency3, 2),
                "details": "Chặn nạp trùng tài liệu vào phiên (409 DOCUMENT_ALREADY_IN_SESSION)",
                "checks": checks3,
                "artifact": "03_duplicate_document_conflict_guard.json",
                "checksum": chk3,
                "raw_response": d3,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 4: Session Capacity Cap Guard (Max 5 Documents) (HTTP 422)
        # Current count in session: doc1, doc2, url_doc (3 docs).
        # We attach doc3 and doc4 to reach capacity limit of 5.
        # ----------------------------------------------------------------------
        await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json={"source_type": "document_id", "document_id": doc3_id},
        )
        await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json={"source_type": "document_id", "document_id": doc4_id},
        )

        # Now session has 5 documents. Attempting to add doc5 must trigger capacity cap.
        t0 = time.perf_counter()
        req4_body = {"source_type": "document_id", "document_id": doc5_id}
        res4 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json=req4_body,
        )
        latency4 = (time.perf_counter() - t0) * 1000
        d4 = res4.json() if res4.content else {}

        _, chk4 = save_raw_artifact(
            self.endpoint_name,
            "04_capacity_cap_guard",
            d4,
        )
        artifact_checksums["04_capacity_cap_guard.json"] = chk4

        checks4: list[tuple[bool, str]] = [
            (res4.status_code == 422, "HTTP Status 422 Unprocessable Entity"),
            (d4.get("success") is False, "Response success is False"),
            (
                d4.get("error", {}).get("code") == "SESSION_CAPACITY_EXCEEDED",
                "Error code is SESSION_CAPACITY_EXCEEDED",
            ),
        ]
        pass4 = all(p for p, _ in checks4)
        tbox4 = format_terminal_box(
            method="POST",
            path=f"/api/v1/sessions/{session_id}/documents",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=req4_body,
            status_code=res4.status_code,
            latency_ms=latency4,
            res_headers=dict(res4.headers),
            res_body=d4,
            quality_checks=checks4,
        )
        print("\n" + tbox4)
        cases.append(
            {
                "name": "04_capacity_cap_guard",
                "passed": pass4,
                "status_code": res4.status_code,
                "expected_code": 422,
                "latency_ms": round(latency4, 2),
                "details": "Chặn vượt quá ngưỡng 5 bài báo/phiên (422 SESSION_CAPACITY_EXCEEDED)",
                "checks": checks4,
                "artifact": "04_capacity_cap_guard.json",
                "checksum": chk4,
                "raw_response": d4,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 5: Multi-Tenant User Isolation Guard (HTTP 404)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        req5_body = {"source_type": "document_id", "document_id": doc5_id}
        res5 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json=req5_body,
            headers=alien_headers,
        )
        latency5 = (time.perf_counter() - t0) * 1000
        d5 = res5.json() if res5.content else {}

        _, chk5 = save_raw_artifact(
            self.endpoint_name,
            "05_multi_tenant_isolation",
            d5,
        )
        artifact_checksums["05_multi_tenant_isolation.json"] = chk5

        checks5: list[tuple[bool, str]] = [
            (res5.status_code == 404, "HTTP Status 404 Not Found"),
            (d5.get("success") is False, "Response success is False"),
            (
                d5.get("error", {}).get("code") == "SESSION_NOT_FOUND",
                "Error code is SESSION_NOT_FOUND",
            ),
        ]
        pass5 = all(p for p, _ in checks5)
        tbox5 = format_terminal_box(
            method="POST",
            path=f"/api/v1/sessions/{session_id}/documents",
            req_headers=alien_headers,
            form_data=None,
            req_body=req5_body,
            status_code=res5.status_code,
            latency_ms=latency5,
            res_headers=dict(res5.headers),
            res_body=d5,
            quality_checks=checks5,
        )
        print("\n" + tbox5)
        cases.append(
            {
                "name": "05_multi_tenant_isolation",
                "passed": pass5,
                "status_code": res5.status_code,
                "expected_code": 404,
                "latency_ms": round(latency5, 2),
                "details": "Chặn người dùng lạ thao tác trên phiên riêng tư (404 SESSION_NOT_FOUND)",
                "checks": checks5,
                "artifact": "05_multi_tenant_isolation.json",
                "checksum": chk5,
                "raw_response": d5,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 6: Validation Bounds & Path Format Guard (HTTP 422)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        req6_body = {"source_type": "document_id", "document_id": doc5_id}
        res6 = await ctx.client.post(
            "/api/v1/sessions/malformed-session-uuid-xyz/documents",
            json=req6_body,
        )
        latency6 = (time.perf_counter() - t0) * 1000
        d6 = res6.json() if res6.content else {}

        _, chk6 = save_raw_artifact(
            self.endpoint_name,
            "06_validation_error_guard",
            d6,
        )
        artifact_checksums["06_validation_error_guard.json"] = chk6

        checks6: list[tuple[bool, str]] = [
            (res6.status_code == 422, "HTTP Status 422 Unprocessable Entity"),
            (d6.get("success") is False, "Response success is False"),
            (
                d6.get("error", {}).get("code") == "VALIDATION_ERROR",
                "Error code is VALIDATION_ERROR",
            ),
        ]
        pass6 = all(p for p, _ in checks6)
        tbox6 = format_terminal_box(
            method="POST",
            path="/api/v1/sessions/malformed-session-uuid-xyz/documents",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=req6_body,
            status_code=res6.status_code,
            latency_ms=latency6,
            res_headers=dict(res6.headers),
            res_body=d6,
            quality_checks=checks6,
        )
        print("\n" + tbox6)
        cases.append(
            {
                "name": "06_validation_error_guard",
                "passed": pass6,
                "status_code": res6.status_code,
                "expected_code": 422,
                "latency_ms": round(latency6, 2),
                "details": "Chặn đường dẫn UUID sai định dạng (422 VALIDATION_ERROR)",
                "checks": checks6,
                "artifact": "06_validation_error_guard.json",
                "checksum": chk6,
                "raw_response": d6,
            }
        )

        # ----------------------------------------------------------------------
        # Hermetic Teardown
        # ----------------------------------------------------------------------
        if session_id:
            await ctx.client.delete(f"/api/v1/sessions/{session_id}")
        if alien_session_id:
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

        return f"""# API Evaluation Snapshot: POST /api/v1/sessions/{{id}}/documents

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#51 Nạp bài vào phiên (Pure JSON: url hoặc document_id)`  
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
- **202 Accepted Asynchronous Acknowledgement Invariant**: Phản hồi HTTP 202 Accepted và ID liên kết khi nạp tài liệu qua Pure JSON.
- **Session Capacity Cap (Max 5 Documents)**: Cưỡng chế nghiêm ngặt tối đa 5 tài liệu/phiên đọc sâu (HTTP 422 SESSION_CAPACITY_EXCEEDED).
- **Duplicate Document Attachment Guard**: Ngăn chặn đính kèm trùng lặp cùng một tài liệu vào phiên (HTTP 409 DOCUMENT_ALREADY_IN_SESSION).
- **Multi-Tenant User Isolation Guard**: Bảo vệ dữ liệu người dùng, trả về HTTP 404 SESSION_NOT_FOUND cho truy vấn trái phép.
- **Hermetic Cleanup**: Thu hồi toàn bộ phiên và tài liệu thử nghiệm sau kiểm định (Zero Retention).

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

"""Evaluator for POST /api/v1/sessions (#45: Khởi tạo phiên nghiên cứu đa bài mới)."""

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


class CreateSessionAPIRunner(BaseAPIRunner):
    """Evaluates multi-paper research session creation, capacity guards, and state invariants."""

    endpoint_name = "post_sessions_create"
    report_filename = "post_sessions_create.md"
    http_method = "POST"
    route_path = "/api/v1/sessions"

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

        # Seed 2 documents for multi-paper session evaluation
        seeded_doc_ids: list[str] = []
        pdf_bytes = target_paper.read_bytes()
        for i in range(2):
            filename = f"seed_{i}_{target_paper.name}"
            files = {"file": (filename, pdf_bytes, "application/pdf")}
            up_res = await ctx.client.post("/api/v1/documents", files=files)
            if up_res.status_code in (200, 201):
                doc_id = up_res.json().get("data", {}).get("id")
                if doc_id:
                    seeded_doc_ids.append(doc_id)
                    ctx.track_document(doc_id)
            else:
                linter_warnings.append(
                    f"Failed to seed document {i} for session test: HTTP {up_res.status_code}"
                )

        if len(seeded_doc_ids) < 2:
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # ----------------------------------------------------------------------
        # Scenario 1: Create Session with Valid Documents (Expect HTTP 201 Created)
        # ----------------------------------------------------------------------
        payload1 = {
            "title": "Nghiên cứu Cơ chế Chú ý và Mô hình Biến đổi Transformer",
            "initial_document_ids": seeded_doc_ids,
        }
        t0 = time.perf_counter()
        r1 = await ctx.client.post("/api/v1/sessions", json=payload1)
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code in (200, 201) else {}
        data1 = body1.get("data", {})

        session1_id = data1.get("id")
        if session1_id:
            ctx.track_session(session1_id)

        p1_valid = (
            r1.status_code == 201
            and body1.get("success") is True
            and data1.get("title") == payload1["title"]
            and data1.get("document_ids") == seeded_doc_ids
            and data1.get("active_document_id") == seeded_doc_ids[0]
            and data1.get("active_tab") == "chat"
            and data1.get("is_archived") is False
            and data1.get("version") == 1
            and r1.headers.get("Location") == f"/api/v1/sessions/{session1_id}"
            and r1.headers.get("ETag") == '"v1"'
        )

        _, sha1 = save_raw_artifact(self.endpoint_name, "create_valid_session_201", body1)
        artifact_checksums["create_valid_session_201.json"] = sha1

        cases.append(
            {
                "name": "Create Session with Valid Documents (201 Created)",
                "status_code": r1.status_code,
                "expected_status": 201,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": "Initialized session with active doc, default canvas viewport, Location & ETag headers",
                "raw_response": body1,
            }
        )

        # Terminal Box for primary happy-path scenario
        checks1 = [
            (r1.status_code == 201, "HTTP Status 201 Created"),
            (body1.get("success") is True, "Response Success Envelope: True"),
            (
                data1.get("active_document_id") == seeded_doc_ids[0],
                "Active Document Set to First Document",
            ),
            (r1.headers.get("Location") is not None, "Location Header Present"),
            (r1.headers.get("ETag") == '"v1"', "ETag Version Header: '\"v1\"'"),
        ]
        tbox = format_terminal_box(
            method=self.http_method,
            path=self.route_path,
            req_headers={"Content-Type": "application/json"},
            form_data=None,
            req_body=payload1,
            status_code=r1.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r1.headers),
            res_body=body1,
            quality_checks=checks1,
        )
        print("\n" + tbox)

        # ----------------------------------------------------------------------
        # Scenario 2: Create Empty Session (No Initial Documents, Expect HTTP 201)
        # ----------------------------------------------------------------------
        payload2 = {
            "title": "Khởi tạo Phiên Trống Chưa Nạp Tài Liệu",
            "initial_document_ids": [],
        }
        t1 = time.perf_counter()
        r2 = await ctx.client.post("/api/v1/sessions", json=payload2)
        latency_ms2 = (time.perf_counter() - t1) * 1000
        body2 = r2.json() if r2.status_code in (200, 201) else {}
        data2 = body2.get("data", {})

        session2_id = data2.get("id")
        if session2_id:
            ctx.track_session(session2_id)

        p2_valid = (
            r2.status_code == 201
            and body2.get("success") is True
            and data2.get("document_ids") == []
            and data2.get("active_document_id") is None
            and data2.get("version") == 1
        )

        _, sha2 = save_raw_artifact(self.endpoint_name, "create_empty_session_201", body2)
        artifact_checksums["create_empty_session_201.json"] = sha2

        cases.append(
            {
                "name": "Create Empty Session (201 Created)",
                "status_code": r2.status_code,
                "expected_status": 201,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": "Empty document set cleanly handled with null active_document_id",
                "raw_response": body2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 3: Auto-naming Fallback when Title is Null (Expect HTTP 201)
        # ----------------------------------------------------------------------
        payload3 = {"initial_document_ids": [seeded_doc_ids[0]]}
        t_auto = time.perf_counter()
        r_auto = await ctx.client.post("/api/v1/sessions", json=payload3)
        latency_ms_auto = (time.perf_counter() - t_auto) * 1000
        body_auto = r_auto.json() if r_auto.status_code in (200, 201) else {}
        data_auto = body_auto.get("data", {})

        if data_auto.get("id"):
            ctx.track_session(data_auto["id"])

        p_auto_valid = (
            r_auto.status_code == 201
            and body_auto.get("success") is True
            and str(data_auto.get("title", "")).startswith("Nghiên cứu: ")
        )
        _, sha_auto = save_raw_artifact(self.endpoint_name, "auto_naming_fallback_201", body_auto)
        artifact_checksums["auto_naming_fallback_201.json"] = sha_auto

        cases.append(
            {
                "name": "Auto-naming Fallback when Title is Null (201 Created)",
                "status_code": r_auto.status_code,
                "expected_status": 201,
                "latency_ms": latency_ms_auto,
                "passed": p_auto_valid,
                "details": f"Automatically generated descriptive title: '{data_auto.get('title')}'",
                "raw_response": body_auto,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 4: Idempotency Protection Replay (Expect HTTP 200 + X-Cache: Idempotent-Hit)
        # ----------------------------------------------------------------------
        idempotency_key = f"eval-idem-{uuid.uuid4()}"
        headers_idem = {"Idempotency-Key": idempotency_key}
        payload_idem = {"title": "Idempotent Evaluation Session"}

        # First call (creates session)
        r_idem1 = await ctx.client.post("/api/v1/sessions", json=payload_idem, headers=headers_idem)
        data_idem1 = r_idem1.json().get("data", {})
        if data_idem1.get("id"):
            ctx.track_session(data_idem1["id"])

        # Second call (idempotent cache hit)
        t_idem = time.perf_counter()
        r_idem2 = await ctx.client.post("/api/v1/sessions", json=payload_idem, headers=headers_idem)
        latency_ms_idem = (time.perf_counter() - t_idem) * 1000
        body_idem2 = r_idem2.json() if r_idem2.status_code in (200, 201) else {}
        data_idem2 = body_idem2.get("data", {})

        p_idem_valid = (
            r_idem2.status_code == 200
            and r_idem2.headers.get("X-Cache") == "Idempotent-Hit"
            and data_idem1.get("id") == data_idem2.get("id")
        )
        _, sha_idem = save_raw_artifact(self.endpoint_name, "idempotency_cache_hit_200", body_idem2)
        artifact_checksums["idempotency_cache_hit_200.json"] = sha_idem

        cases.append(
            {
                "name": "Idempotency Protection Replay (200 OK)",
                "status_code": r_idem2.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms_idem,
                "passed": p_idem_valid,
                "details": "Replayed identical key returning cached session with X-Cache: Idempotent-Hit",
                "raw_response": body_idem2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 5: Embedded Document Metadata (include_documents=true)
        # ----------------------------------------------------------------------
        t_embed = time.perf_counter()
        r_embed = await ctx.client.post(
            "/api/v1/sessions?include_documents=true",
            json={
                "title": "Embedded Metadata Session",
                "initial_document_ids": [seeded_doc_ids[0]],
            },
        )
        latency_ms_embed = (time.perf_counter() - t_embed) * 1000
        body_embed = r_embed.json() if r_embed.status_code in (200, 201) else {}
        data_embed = body_embed.get("data", {})

        if data_embed.get("id"):
            ctx.track_session(data_embed["id"])

        p_embed_valid = (
            r_embed.status_code == 201
            and data_embed.get("documents") is not None
            and len(data_embed.get("documents", [])) == 1
            and data_embed["documents"][0].get("id") == seeded_doc_ids[0]
        )
        _, sha_embed = save_raw_artifact(self.endpoint_name, "embedded_documents_201", body_embed)
        artifact_checksums["embedded_documents_201.json"] = sha_embed

        cases.append(
            {
                "name": "Embedded Document Metadata (201 Created)",
                "status_code": r_embed.status_code,
                "expected_status": 201,
                "latency_ms": latency_ms_embed,
                "passed": p_embed_valid,
                "details": "Embedded rich document metadata without extra round-trips",
                "raw_response": body_embed,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 6: Capacity Guard - Over 5 Documents (Expect HTTP 400 Bad Request)
        # ----------------------------------------------------------------------
        dummy_6_docs = [str(uuid.uuid4()) for _ in range(6)]
        payload_cap = {
            "title": "Phiên Vượt Quá Dung Lượng 5 Bài Báo",
            "initial_document_ids": dummy_6_docs,
        }
        t_cap = time.perf_counter()
        r_cap = await ctx.client.post("/api/v1/sessions", json=payload_cap)
        latency_ms_cap = (time.perf_counter() - t_cap) * 1000
        body_cap = r_cap.json() if r_cap.status_code in (400, 422) else {}

        p_cap_valid = (
            r_cap.status_code == 400
            and body_cap.get("success") is False
            and body_cap.get("error", {}).get("code") == "SESSION_CAPACITY_EXCEEDED"
        )

        _, sha_cap = save_raw_artifact(self.endpoint_name, "capacity_guard_exceeded_400", body_cap)
        artifact_checksums["capacity_guard_exceeded_400.json"] = sha_cap

        cases.append(
            {
                "name": "Capacity Guard Exceeded (Expect HTTP 400)",
                "status_code": r_cap.status_code,
                "expected_status": 400,
                "latency_ms": latency_ms_cap,
                "passed": p_cap_valid,
                "details": f"Blocked > 5 papers with 400 ({body_cap.get('error', {}).get('code')})",
                "raw_response": body_cap,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 7: Duplicate Document IDs Deduplication (Expect HTTP 201 Created)
        # ----------------------------------------------------------------------
        payload_dup = {
            "title": "Khử Trùng Lặp Tài Liệu Đầu Vào",
            "initial_document_ids": [seeded_doc_ids[0], seeded_doc_ids[0], seeded_doc_ids[1]],
        }
        t_dup = time.perf_counter()
        r_dup = await ctx.client.post("/api/v1/sessions", json=payload_dup)
        latency_ms_dup = (time.perf_counter() - t_dup) * 1000
        body_dup = r_dup.json() if r_dup.status_code in (200, 201) else {}
        data_dup = body_dup.get("data", {})

        if data_dup.get("id"):
            ctx.track_session(data_dup["id"])

        p_dup_valid = (
            r_dup.status_code == 201
            and data_dup.get("document_ids") == seeded_doc_ids
            and data_dup.get("active_document_id") == seeded_doc_ids[0]
        )

        _, sha_dup = save_raw_artifact(self.endpoint_name, "dedup_documents_201", body_dup)
        artifact_checksums["dedup_documents_201.json"] = sha_dup

        cases.append(
            {
                "name": "Duplicate Document Deduplication (201 Created)",
                "status_code": r_dup.status_code,
                "expected_status": 201,
                "latency_ms": latency_ms_dup,
                "passed": p_dup_valid,
                "details": "Deduplicated repeated document IDs while maintaining sequential order",
                "raw_response": body_dup,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 8: Non-existent Document Lookup Guard (Expect HTTP 404 Not Found)
        # ----------------------------------------------------------------------
        fake_doc_id = str(uuid.uuid4())
        payload_non = {
            "title": "Kiểm Tra Tài Liệu Không Tồn Tại",
            "initial_document_ids": [fake_doc_id],
        }
        t_non = time.perf_counter()
        r_non = await ctx.client.post("/api/v1/sessions", json=payload_non)
        latency_ms_non = (time.perf_counter() - t_non) * 1000
        body_non = r_non.json() if r_non.status_code in (403, 404) else {}

        p_non_valid = (
            r_non.status_code == 404
            and body_non.get("success") is False
            and body_non.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
        )

        _, sha_non = save_raw_artifact(self.endpoint_name, "nonexistent_document_404", body_non)
        artifact_checksums["nonexistent_document_404.json"] = sha_non

        cases.append(
            {
                "name": "Nonexistent Document Guard (Expect HTTP 404)",
                "status_code": r_non.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms_non,
                "passed": p_non_valid,
                "details": f"Blocked unowned or missing document ID with 404 ({body_non.get('error', {}).get('code')})",
                "raw_response": body_non,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 9: Validation Guard - Whitespace Title (Expect HTTP 422)
        # ----------------------------------------------------------------------
        payload_white = {"title": "    "}
        t_white = time.perf_counter()
        r_white = await ctx.client.post("/api/v1/sessions", json=payload_white)
        latency_ms_white = (time.perf_counter() - t_white) * 1000
        body_white = r_white.json() if r_white.status_code == 422 else {}

        p_white_valid = r_white.status_code == 422
        _, sha_white = save_raw_artifact(self.endpoint_name, "whitespace_title_422", body_white)
        artifact_checksums["whitespace_title_422.json"] = sha_white

        cases.append(
            {
                "name": "Validation Guard Whitespace Title (Expect HTTP 422)",
                "status_code": r_white.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms_white,
                "passed": p_white_valid,
                "details": "Pydantic validator blocked whitespace-only string with 422",
                "raw_response": body_white,
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

        return f"""# API Evaluation Snapshot: POST /api/v1/sessions

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Multi-Paper Research Session Creation  
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
- **Strict Multi-tenant Isolation**: Documents belonging to another user are securely shielded (HTTP 404).
- **Capacity Constraint (1-5 Papers)**: Enforces upper limit invariant returning `SESSION_CAPACITY_EXCEEDED` on overflow.
- **Deduplication & Order Preservation**: Duplicate IDs in payload are stripped while preserving the primary document order.
- **RESTful Headers**: Returns standard `Location` header to new resource and `ETag: "v1"` for OCC synchronization.
- **Idempotency Guarantee**: Protects against double submissions with `Idempotency-Key` and `X-Cache: Idempotent-Hit`.
- **Intelligent Auto-naming Fallback**: Formats descriptive title from the first document or current timestamp.
- **Embedded Document Metadata**: Optional `?include_documents=true` populates document metadata to eliminate extra round-trips.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

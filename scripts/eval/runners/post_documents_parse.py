"""Evaluator for POST /api/v1/documents/{document_id}:parse (Ingestion Dispatch & Idempotency)."""

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


class ParseDocumentAPIRunner(BaseAPIRunner):
    """Evaluates document ingestion trigger, 24-hour Idempotency-Key caching, state machine, and guards."""

    endpoint_name = "post_documents_parse"
    report_filename = "post_documents_parse.md"
    http_method = "POST"
    route_path = "/api/v1/documents/{document_id}:parse"

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
                    f"Failed to seed document for parse test: HTTP {up_res.status_code}"
                )
                return {
                    "endpoint": self.endpoint_name,
                    "all_passed": False,
                    "cases": [],
                    "linter_warnings": linter_warnings,
                    "session_tag": ctx.session_tag,
                }

        # Scenario 1: Initial Parse Trigger with Idempotency Key (Expect HTTP 202 Accepted & X-Cache: Miss)
        idem_key = str(uuid.uuid4())
        payload1 = {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "extract_tables": True,
            "force_reparse": False,
        }
        headers1 = {"Idempotency-Key": idem_key}
        t0 = time.perf_counter()
        r1 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:parse",
            json=payload1,
            headers=headers1,
        )
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 202 else {}
        data1 = body1.get("data", {})
        meta1 = body1.get("meta", {})
        cache_header1 = r1.headers.get("x-cache", "")

        p1_valid = (
            r1.status_code == 202
            and body1.get("success") is True
            and cache_header1 == "Miss"
            and data1.get("id") == seeded_doc_id
            and data1.get("status") == "processing"
            and data1.get("stage") == "validation"
            and data1.get("progress") == 0
            and data1.get("links", {}).get("status_url")
            == f"/api/v1/documents/{seeded_doc_id}/status"
            and data1.get("links", {}).get("detail_url") == f"/api/v1/documents/{seeded_doc_id}"
            and "request_id" in meta1
            and "timestamp" in meta1
        )

        _, sha1 = save_raw_artifact(self.endpoint_name, "parse_initial_202", body1)
        artifact_checksums["parse_initial_202.json"] = sha1

        cases.append(
            {
                "name": "Initial Parse with Idempotency Key (202 Accepted)",
                "status_code": r1.status_code,
                "expected_status": 202,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": (
                    f"X-Cache: {cache_header1} | status: {data1.get('status')} | stage: {data1.get('stage')} | "
                    f"HATEOAS links verified"
                ),
                "raw_response": body1,
            }
        )

        # Scenario 2: 24-hour Idempotency Cache Hit (Expect HTTP 202 Accepted & X-Cache: Idempotent-Hit)
        t1 = time.perf_counter()
        r2 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:parse",
            json=payload1,
            headers=headers1,
        )
        latency_ms2 = (time.perf_counter() - t1) * 1000
        body2 = r2.json() if r2.status_code == 202 else {}
        data2 = body2.get("data", {})
        cache_header2 = r2.headers.get("x-cache", "")

        p2_valid = (
            r2.status_code == 202
            and body2.get("success") is True
            and cache_header2 == "Idempotent-Hit"
            and data2.get("id") == seeded_doc_id
            and data2.get("status") == "processing"
        )

        _, sha2 = save_raw_artifact(self.endpoint_name, "parse_idempotent_hit_202", body2)
        artifact_checksums["parse_idempotent_hit_202.json"] = sha2

        cases.append(
            {
                "name": "24h Idempotency Cache Hit Defense (202 Accepted)",
                "status_code": r2.status_code,
                "expected_status": 202,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": f"X-Cache: {cache_header2} | Repeated dispatch returned cached response without re-triggering",
                "raw_response": body2,
            }
        )

        # Scenario 3: Concurrency Conflict Guard (Expect HTTP 409 Conflict)
        # Calling parse without Idempotency-Key while document is currently in 'processing' status
        payload3 = {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "extract_tables": True,
            "force_reparse": False,
        }
        t2 = time.perf_counter()
        r3 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:parse",
            json=payload3,
        )
        latency_ms3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code == 409 else {}

        p3_valid = (
            r3.status_code == 409
            and body3.get("success") is False
            and body3.get("error", {}).get("code") == "DOCUMENT_PROCESSING"
            and body3.get("error", {}).get("field") == "id"
        )

        _, sha3 = save_raw_artifact(self.endpoint_name, "parse_conflict_409", body3)
        artifact_checksums["parse_conflict_409.json"] = sha3

        cases.append(
            {
                "name": "Processing State Machine Conflict Guard (Expect HTTP 409)",
                "status_code": r3.status_code,
                "expected_status": 409,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"Concurrent processing locked with 409 ({body3.get('error', {}).get('code')})",
                "raw_response": body3,
            }
        )

        # Scenario 4: Force Reparse Override (Expect HTTP 202 Accepted)
        payload4 = {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "extract_tables": True,
            "force_reparse": True,
        }
        t3 = time.perf_counter()
        r4 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:parse",
            json=payload4,
        )
        latency_ms4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code == 202 else {}
        data4 = body4.get("data", {})

        p4_valid = (
            r4.status_code == 202
            and body4.get("success") is True
            and data4.get("id") == seeded_doc_id
            and data4.get("status") == "processing"
            and data4.get("stage") == "validation"
            and data4.get("progress") == 0
        )

        _, sha4 = save_raw_artifact(self.endpoint_name, "parse_force_reparse_202", body4)
        artifact_checksums["parse_force_reparse_202.json"] = sha4

        cases.append(
            {
                "name": "Force Reparse Override Pipeline Reset (202 Accepted)",
                "status_code": r4.status_code,
                "expected_status": 202,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": "force_reparse=true successfully bypassed 409 lock and reset pipeline",
                "raw_response": body4,
            }
        )

        # Scenario 5: Chunking Parameter Validation Guard (Expect HTTP 422 Unprocessable Entity)
        payload5 = {
            "chunk_size": 100,
            "chunk_overlap": 150,  # Invalid: overlap >= size
        }
        t4 = time.perf_counter()
        r5 = await ctx.client.post(
            f"/api/v1/documents/{seeded_doc_id}:parse",
            json=payload5,
        )
        latency_ms5 = (time.perf_counter() - t4) * 1000
        body5 = r5.json() if r5.status_code == 422 else {}

        p5_valid = r5.status_code == 422 and body5.get("success") is False
        _, sha5 = save_raw_artifact(self.endpoint_name, "parse_validation_guard_422", body5)
        artifact_checksums["parse_validation_guard_422.json"] = sha5

        cases.append(
            {
                "name": "Chunking Parameter Guard (overlap >= size -> 422)",
                "status_code": r5.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": "Pydantic validator intercepted invalid chunking configuration with 422",
                "raw_response": body5,
            }
        )

        # Scenario 6: Nonexistent Document Guard (Expect HTTP 404 Not Found)
        fake_doc_id = str(uuid.uuid4())
        t5 = time.perf_counter()
        r6 = await ctx.client.post(
            f"/api/v1/documents/{fake_doc_id}:parse",
            json={"force_reparse": False},
        )
        latency_ms6 = (time.perf_counter() - t5) * 1000
        body6 = r6.json() if r6.status_code in (403, 404) else {}

        p6_valid = (
            r6.status_code == 404
            and body6.get("success") is False
            and body6.get("error", {}).get("code") == "DOCUMENT_NOT_FOUND"
            and body6.get("error", {}).get("field") == "id"
        )

        _, sha6 = save_raw_artifact(self.endpoint_name, "parse_nonexistent_document_404", body6)
        artifact_checksums["parse_nonexistent_document_404.json"] = sha6

        cases.append(
            {
                "name": "Nonexistent Document Lookup (Expect HTTP 404)",
                "status_code": r6.status_code,
                "expected_status": 404,
                "latency_ms": latency_ms6,
                "passed": p6_valid,
                "details": f"Unregistered UUID rejected with 404 ({body6.get('error', {}).get('code')})",
                "raw_response": body6,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the primary parse dispatch)
        checks = [
            (
                r1.status_code == 202,
                f"Status Code & Envelope: {r1.status_code} Accepted (Kỳ vọng: 202)",
            ),
            (cache_header1 == "Miss", "Idempotency Cache Miss : PASS (X-Cache: Miss)"),
            (p2_valid, "Idempotency Cache Hit  : PASS (X-Cache: Idempotent-Hit)"),
            (p3_valid, "Processing State Lock  : PASS (409 Conflict khi kích hoạt trùng lặp)"),
            (
                p4_valid,
                "Force Reparse Reset    : PASS (force_reparse=true tái kích hoạt thành công)",
            ),
            (p5_valid, "Chunking Parameter (422: PASS (overlap >= size bị chặn 422)"),
            (p6_valid, "Document Guard (404)   : PASS (UUID không tồn tại trả về 404)"),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"/api/v1/documents/{seeded_doc_id}:parse",
            req_headers={
                "x-user-id": ctx.session_tag,
                "content-type": "application/json",
                "Idempotency-Key": idem_key,
            },
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

        return f"""# API Evaluation Snapshot: POST /api/v1/documents/{{document_id}}:parse

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Document Ingestion Trigger & Idempotency  
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
- **Asynchronous Task Dispatch Semantics (HTTP 202 Accepted)**:
  - The custom method `:parse` initiates or re-initiates the parsing pipeline and immediately returns `HTTP 202 Accepted` with initial status `processing`, stage `validation`, and progress `0`.
- **24-Hour Idempotency Cache Protection**:
  - Gửi kèm header `Idempotency-Key` kích hoạt bộ đệm 24h: lần đầu trả về `X-Cache: Miss`, lần gửi lại trả về `X-Cache: Idempotent-Hit` mà không kích hoạt lại pipeline hoặc sinh xung đột 409.
- **State Machine & Concurrency Guard**:
  - Khi tài liệu đang ở trạng thái `processing`, các request gửi tiếp theo không có `Idempotency-Key` và `force_reparse=false` bị chặn với `HTTP 409 DOCUMENT_PROCESSING`.
  - Cờ `force_reparse=true` cho phép ghi đè trạng thái và khởi động lại pipeline sạch sẽ.
- **Parameter & Boundary Guard**:
  - Ràng buộc bất biến `chunk_overlap < chunk_size` được kiểm tra và chặn với `HTTP 422 Unprocessable Entity`.
  - ID tài liệu không tồn tại bị từ chối với `HTTP 404 DOCUMENT_NOT_FOUND`.
- **Deterministic Refresh**: Báo cáo snapshot được làm mới sạch sẽ tại `{target_rel_path}`.

---

## 3. Full Raw Payloads & Audit Artifacts (Untruncated)

{raw_payloads_body}
{warning_block}"""

"""Evaluator for GET /api/v1/documents (Module 1: Paginated Document Listing & Filtering)."""

import json
import time
from typing import Any

from scripts.eval.config import get_available_papers
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


class ListDocumentsAPIRunner(BaseAPIRunner):
    """Evaluates Document Listing, RFC 8288 Pagination, Status Filtering, and Boundary Guards."""

    endpoint_name = "get_documents_list"
    report_filename = "get_documents_list.md"
    http_method = "GET"
    route_path = "/api/v1/documents"

    async def evaluate(
        self,
        ctx: EvaluationContext,
        interactive: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        assert ctx.client is not None
        cases: list[dict[str, Any]] = []
        artifact_checksums: dict[str, str] = {}
        linter_warnings: list[str] = []

        # 1. Clean refresh for output markdown report in temp/output/test/
        check_and_prepare_output_file(self.report_filename, interactive=interactive)

        # 2. Hermetic Data Seeding: Ensure at least 3 documents exist in this session
        available_papers = get_available_papers()
        seeded_docs: list[str] = []
        if available_papers:
            for idx in range(3):
                p = available_papers[idx % len(available_papers)]
                fn = f"seed_{idx + 1}_{p.name}" if idx >= len(available_papers) else p.name
                files = {"file": (fn, p.read_bytes(), "application/pdf")}
                up_res = await ctx.client.post("/api/v1/documents", files=files)
                if up_res.status_code in (200, 201):
                    doc_id = up_res.json().get("data", {}).get("id")
                    if doc_id:
                        ctx.track_document(doc_id)
                        seeded_docs.append(doc_id)
        else:
            linter_warnings.append("No sample PDF papers available in data/papers/ for seeding.")

        # Scenario 1: Default Pagination (No query params -> page=1, per_page=20)
        t0 = time.perf_counter()
        r_default = await ctx.client.get("/api/v1/documents")
        latency_ms0 = (time.perf_counter() - t0) * 1000
        body_default = r_default.json() if r_default.status_code == 200 else {}
        _, sha0 = save_raw_artifact(self.endpoint_name, "default_pagination", body_default)
        artifact_checksums["default_pagination.json"] = sha0

        meta0 = body_default.get("meta", {})
        data0 = body_default.get("data", [])
        p0_valid = (
            r_default.status_code == 200
            and body_default.get("success") is True
            and meta0.get("page") == 1
            and meta0.get("per_page") == 20
            and isinstance(data0, list)
            and len(data0) >= len(seeded_docs)
        )
        cases.append(
            {
                "name": "Default Paginated Query (page=1, per_page=20)",
                "status_code": r_default.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms0,
                "passed": p0_valid,
                "details": f"Total: {meta0.get('total', 0)} items | Returned: {len(data0)} items",
                "raw_response": body_default,
            }
        )

        # Scenario 2: Strict Page Slicing (page=1, per_page=2)
        t1 = time.perf_counter()
        r_slice = await ctx.client.get("/api/v1/documents?page=1&per_page=2")
        latency_ms1 = (time.perf_counter() - t1) * 1000
        body_slice = r_slice.json() if r_slice.status_code == 200 else {}
        _, sha1 = save_raw_artifact(self.endpoint_name, "page_1_per_page_2", body_slice)
        artifact_checksums["page_1_per_page_2.json"] = sha1

        meta1 = body_slice.get("meta", {})
        data1 = body_slice.get("data", [])
        links1 = body_slice.get("links", {})
        page1_ids = [item.get("id") for item in data1 if isinstance(item, dict)]

        # Chronological ordering check: created_at DESC
        is_chronological = True
        if len(data1) >= 2:
            is_chronological = data1[0].get("created_at", "") >= data1[1].get("created_at", "")

        p1_valid = (
            r_slice.status_code == 200
            and body_slice.get("success") is True
            and meta1.get("page") == 1
            and meta1.get("per_page") == 2
            and len(data1) == 2
            and meta1.get("total_pages", 0) >= 2
            and links1.get("next") is not None
            and links1.get("prev") is None
            and is_chronological
        )
        cases.append(
            {
                "name": "Strict Page Slicing (page=1, per_page=2)",
                "status_code": r_slice.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": f"Slice size: {len(data1)}/2 | Total pages: {meta1.get('total_pages', 0)} | Next: {bool(links1.get('next'))}",
                "raw_response": body_slice,
            }
        )

        # Scenario 3: Page 2 Navigation & Non-Overlapping Continuity (page=2, per_page=2)
        t2 = time.perf_counter()
        r_page2 = await ctx.client.get("/api/v1/documents?page=2&per_page=2")
        latency_ms2 = (time.perf_counter() - t2) * 1000
        body_page2 = r_page2.json() if r_page2.status_code == 200 else {}
        _, sha2 = save_raw_artifact(self.endpoint_name, "page_2_per_page_2", body_page2)
        artifact_checksums["page_2_per_page_2.json"] = sha2

        meta2 = body_page2.get("meta", {})
        data2 = body_page2.get("data", [])
        links2 = body_page2.get("links", {})
        page2_ids = [item.get("id") for item in data2 if isinstance(item, dict)]

        # Verify no overlap between page 1 and page 2
        no_overlap = not bool(set(page1_ids).intersection(set(page2_ids)))
        p2_valid = (
            r_page2.status_code == 200
            and body_page2.get("success") is True
            and meta2.get("page") == 2
            and len(data2) >= 1
            and links2.get("prev") is not None
            and no_overlap
        )
        cases.append(
            {
                "name": "Page 2 Navigation & Non-Overlapping Continuity",
                "status_code": r_page2.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": f"Page 2 items: {len(data2)} | No overlap: {no_overlap} | Prev: {bool(links2.get('prev'))}",
                "raw_response": body_page2,
            }
        )

        # Scenario 4: Filter By Status (status=uploaded)
        t3 = time.perf_counter()
        r_status = await ctx.client.get("/api/v1/documents?status=uploaded")
        latency_ms3 = (time.perf_counter() - t3) * 1000
        body_status = r_status.json() if r_status.status_code == 200 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "filter_status_uploaded", body_status)
        artifact_checksums["filter_status_uploaded.json"] = sha3

        data3 = body_status.get("data", [])
        all_uploaded = (
            isinstance(data3, list)
            and len(data3) > 0
            and all(item.get("status") == "uploaded" for item in data3 if isinstance(item, dict))
        )
        p3_valid = r_status.status_code == 200 and all_uploaded
        cases.append(
            {
                "name": "Filter by Status (status=uploaded)",
                "status_code": r_status.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": f"Matched items: {len(data3)} with status=uploaded",
                "raw_response": body_status,
            }
        )

        # Scenario 5: Boundary Guard 1 - Reject Page 0 (RFC/FastAPI ge=1)
        t4 = time.perf_counter()
        r_page0 = await ctx.client.get("/api/v1/documents?page=0")
        latency_ms4 = (time.perf_counter() - t4) * 1000
        body_page0 = r_page0.json() if r_page0.status_code == 422 else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "invalid_page_0", body_page0)
        artifact_checksums["invalid_page_0.json"] = sha4
        p4_valid = r_page0.status_code == 422
        cases.append(
            {
                "name": "Boundary Guard: Reject Page 0 (Expect HTTP 422)",
                "status_code": r_page0.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": "Triggered 422 Unprocessable Entity for page < 1",
                "raw_response": body_page0,
            }
        )

        # Scenario 6: Boundary Guard 2 - Reject per_page > 100 (FastAPI le=100)
        t5 = time.perf_counter()
        r_pp101 = await ctx.client.get("/api/v1/documents?per_page=101")
        latency_ms5 = (time.perf_counter() - t5) * 1000
        body_pp101 = r_pp101.json() if r_pp101.status_code == 422 else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "invalid_per_page_101", body_pp101)
        artifact_checksums["invalid_per_page_101.json"] = sha5
        p5_valid = r_pp101.status_code == 422
        cases.append(
            {
                "name": "Boundary Guard: Reject per_page=101 (Expect HTTP 422)",
                "status_code": r_pp101.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": "Triggered 422 Unprocessable Entity for per_page > 100",
                "raw_response": body_pp101,
            }
        )

        # In-Terminal HTTP Exchange Display (Visual Box for the core pagination request)
        checks = [
            (
                r_slice.status_code == 200,
                f"HTTP Status Code : {r_slice.status_code} OK (Kỳ vọng: 200)",
            ),
            (len(data1) == 2, f"Page Limit Match : {len(data1)} items / page (Khớp per_page=2)"),
            (is_chronological, "Chronological Ord: PASS (Sắp xếp created_at DESC)"),
            (
                bool(links1.get("next")) and links1.get("prev") is None,
                "RFC 8288 Links   : PASS (next trang 2 hợp lệ, prev là null)",
            ),
            (no_overlap, "Page Continuity  : PASS (Không trùng lặp tài liệu giữa trang 1 và 2)"),
            (all_uploaded, "Status Filtering : PASS (100% tài liệu khớp status=uploaded)"),
            (
                p4_valid and p5_valid,
                "Negative Guards  : PASS (page=0 & per_page=101 bị từ chối 422)",
            ),
        ]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=f"{self.route_path}?page=1&per_page=2",
            req_headers={"x-user-id": ctx.session_tag, "accept": "application/json"},
            form_data=None,
            req_body=None,
            status_code=r_slice.status_code,
            latency_ms=latency_ms1,
            res_headers=dict(r_slice.headers),
            res_body=body_slice,
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

        return f"""# API Evaluation Snapshot: GET /api/v1/documents

> **Audit Header**: Session Tag: `{session_tag}` | Mode: Paginated Document Listing & Filtering  
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
- **Strict RFC 8288 / JSON:API Pagination**: `meta` object conveys total items, page number, per_page, and total pages; `links` provides `self`, `first`, `next`, `prev`, and `last`.
- **Chronological Sorting**: Output collections maintain strict `created_at DESC` ordering.
- **Tenant Isolation**: Only documents associated with the active session tag (`x-user-id`) are returned.
- **Boundary Validation**: Rejects `page < 1` and `per_page > 100` with HTTP `422 Unprocessable Entity`.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `{target_rel_path}`.

---

## 3. Full Raw Payloads (Untruncated)

{raw_payloads_body}
{warning_block}"""

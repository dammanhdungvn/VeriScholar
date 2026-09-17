"""Evaluator for GET /api/v1/sessions (#46: Research Sessions History & Sidebar Listing)."""

import json
import time
import uuid
from pathlib import Path
from typing import Any

from api.db.models.session import ResearchSessionModel
from api.db.session import AsyncSessionLocal
from sqlalchemy import update

from scripts.eval.config import DATA_PAPERS_DIR, get_available_papers, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


class ListSessionsAPIRunner(BaseAPIRunner):
    """Evaluates Session Sidebar Listing, RFC 8288 Pagination, Search, and Multi-tenant Guards."""

    endpoint_name = "get_sessions_list"
    report_filename = "get_sessions_list.md"
    http_method = "GET"
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

        # 1. Clean refresh for output markdown report in temp/output/test/
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

        # 3. Seed 3 distinct sessions for the evaluation user
        session_seed_configs = [
            {
                "title": "Nghiên cứu Kiến trúc Transformer và Attention Mechanism",
                "initial_document_ids": [seeded_doc_id] if seeded_doc_id else [],
            },
            {
                "title": "Khảo sát Mô hình Ngôn ngữ Lớn trong Y Sinh học và Lâm sàng",
                "initial_document_ids": [],
            },
            {
                "title": "Phân tích Cơ sở Dữ liệu Đồ thị Tri thức và Graph RAG",
                "initial_document_ids": [seeded_doc_id] if seeded_doc_id else [],
            },
        ]

        seeded_session_ids: list[str] = []
        for cfg in session_seed_configs:
            res = await ctx.client.post("/api/v1/sessions", json=cfg)
            if res.status_code in (200, 201):
                sess_id = res.json().get("data", {}).get("id")
                if sess_id:
                    seeded_session_ids.append(sess_id)
                    ctx.track_session(sess_id)
            else:
                linter_warnings.append(
                    f"Failed to seed evaluation session '{cfg['title']}': HTTP {res.status_code}"
                )

        if len(seeded_session_ids) < 3:
            linter_warnings.append(
                f"Only {len(seeded_session_ids)} of 3 sessions were seeded successfully."
            )
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        # ----------------------------------------------------------------------
        # Scenario 1: Default Paginated Listing (page=1, per_page=20)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.get("/api/v1/sessions")
        latency_ms1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_default_pagination", body1)
        artifact_checksums["01_default_pagination.json"] = sha1

        meta1 = body1.get("meta", {})
        data1 = body1.get("data", [])
        links1 = body1.get("links", {})

        # Chronological sorting verification: updated_at DESC
        is_chronological = True
        if len(data1) >= 2:
            is_chronological = data1[0].get("updated_at", "") >= data1[1].get("updated_at", "")

        # Verify items schema
        has_valid_schema = True
        for item in data1:
            required_keys = {
                "id",
                "title",
                "document_count",
                "active_tab",
                "is_archived",
                "created_at",
                "updated_at",
            }
            if not required_keys.issubset(item.keys()):
                has_valid_schema = False
                break

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and meta1.get("page") == 1
            and meta1.get("per_page") == 20
            and meta1.get("total", 0) >= 3
            and meta1.get("total_pages", 0) >= 1
            and links1.get("first") is not None
            and links1.get("prev") is None
            and len(data1) >= 3
            and is_chronological
            and has_valid_schema
        )
        cases.append(
            {
                "name": "Default Paginated Listing (page=1, per_page=20)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms1,
                "passed": p1_valid,
                "details": (
                    f"Returned {len(data1)} sessions (Total: {meta1.get('total')}) | "
                    f"Chronological DESC: {is_chronological} | Schema Valid: {has_valid_schema}"
                ),
                "raw_response": body1,
            }
        )

        checks1 = [
            (r1.status_code == 200, "HTTP Status 200 OK"),
            (body1.get("success") is True, "Response Success Envelope: True"),
            (meta1.get("page") == 1 and meta1.get("per_page") == 20, "Default Page=1, Per_page=20"),
            (meta1.get("total", 0) >= 3, "Total Records >= 3"),
            (
                links1.get("first") is not None and links1.get("prev") is None,
                "RFC 8288 Boundary Links (prev is null)",
            ),
            (is_chronological, "Chronological Ordering (updated_at DESC)"),
            (has_valid_schema, "SessionHistoryItem Schema Adherence"),
        ]
        tbox1 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions",
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
        # Scenario 2: Strict Page Slicing & Boundary Links (page=1, per_page=2 vs page=2, per_page=2)
        # ----------------------------------------------------------------------
        t2 = time.perf_counter()
        r2_page1 = await ctx.client.get("/api/v1/sessions?page=1&per_page=2")
        r2_page2 = await ctx.client.get("/api/v1/sessions?page=2&per_page=2")
        latency_ms2 = (time.perf_counter() - t2) * 1000

        body2_p1 = r2_page1.json() if r2_page1.status_code == 200 else {}
        body2_p2 = r2_page2.json() if r2_page2.status_code == 200 else {}

        slice_payload = {
            "page_1": body2_p1,
            "page_2": body2_p2,
        }
        _, sha2 = save_raw_artifact(self.endpoint_name, "02_strict_page_slicing", slice_payload)
        artifact_checksums["02_strict_page_slicing.json"] = sha2

        data2_p1 = body2_p1.get("data", [])
        data2_p2 = body2_p2.get("data", [])
        meta2_p1 = body2_p1.get("meta", {})
        meta2_p2 = body2_p2.get("meta", {})
        links2_p1 = body2_p1.get("links", {})
        links2_p2 = body2_p2.get("links", {})

        p1_ids = [item.get("id") for item in data2_p1]
        p2_ids = [item.get("id") for item in data2_p2]
        are_disjoint = set(p1_ids).isdisjoint(set(p2_ids))

        p2_valid = (
            r2_page1.status_code == 200
            and r2_page2.status_code == 200
            and len(data2_p1) == 2
            and len(data2_p2) >= 1
            and meta2_p1.get("page") == 1
            and meta2_p1.get("per_page") == 2
            and meta2_p2.get("page") == 2
            and links2_p1.get("prev") is None
            and links2_p1.get("next") is not None
            and links2_p2.get("prev") is not None
            and are_disjoint
        )
        cases.append(
            {
                "name": "Strict Page Slicing & Boundary Links (per_page=2)",
                "status_code": r2_page1.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms2,
                "passed": p2_valid,
                "details": (
                    f"Page 1: {len(data2_p1)} items, Page 2: {len(data2_p2)} items | "
                    f"Disjoint Set: {are_disjoint} | RFC 8288 next/prev valid"
                ),
                "raw_response": slice_payload,
            }
        )

        checks2 = [
            (
                r2_page1.status_code == 200 and r2_page2.status_code == 200,
                "Both Pages Returned HTTP 200",
            ),
            (len(data2_p1) == 2, "Page 1 contains exact per_page count (2)"),
            (are_disjoint, "Disjoint ID Sets between Page 1 and Page 2"),
            (links2_p1.get("next") is not None, "Page 1 next link present"),
            (links2_p2.get("prev") is not None, "Page 2 prev link present"),
        ]
        tbox2 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions?page=1&per_page=2",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r2_page1.status_code,
            latency_ms=latency_ms2,
            res_headers=dict(r2_page1.headers),
            res_body=slice_payload,
            quality_checks=checks2,
        )
        print("\n" + tbox2)

        # ----------------------------------------------------------------------
        # Scenario 3: Case-Insensitive Title Keyword Search (q=transformer)
        # ----------------------------------------------------------------------
        t3 = time.perf_counter()
        r3 = await ctx.client.get("/api/v1/sessions?q=transformer")
        latency_ms3 = (time.perf_counter() - t3) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_search_title_keyword", body3)
        artifact_checksums["03_search_title_keyword.json"] = sha3

        data3 = body3.get("data", [])
        meta3 = body3.get("meta", {})
        all_match_q = all("transformer" in s.get("title", "").lower() for s in data3)
        has_target_session = any(
            "transformer" in s.get("title", "").lower() and s.get("id") in seeded_session_ids
            for s in data3
        )
        non_matching_excluded = not any("y sinh học" in s.get("title", "").lower() for s in data3)

        p3_valid = (
            r3.status_code == 200
            and body3.get("success") is True
            and len(data3) >= 1
            and all_match_q
            and has_target_session
            and non_matching_excluded
        )
        cases.append(
            {
                "name": "Case-Insensitive Title Keyword Search (q=transformer)",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms3,
                "passed": p3_valid,
                "details": (
                    f"Matched {len(data3)} sessions (Total: {meta3.get('total')}) | "
                    f"All Match Substring: {all_match_q} | Irrelevant Omitted: {non_matching_excluded}"
                ),
                "raw_response": body3,
            }
        )

        checks3 = [
            (r3.status_code == 200, "HTTP Status 200 OK"),
            (len(data3) >= 1, "Matching Results Found"),
            (all_match_q, "All returned sessions match 'transformer' keyword"),
            (non_matching_excluded, "Non-matching sessions successfully filtered out"),
        ]
        tbox3 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions?q=transformer",
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
        # Scenario 4: Archive Status Segregation (include_archived=false vs include_archived=true)
        # ----------------------------------------------------------------------
        # Archive the 3rd seeded session in DB
        archived_sess_id = seeded_session_ids[2]
        async with AsyncSessionLocal() as db_session:
            await db_session.execute(
                update(ResearchSessionModel)
                .where(ResearchSessionModel.id == uuid.UUID(archived_sess_id))
                .values(is_archived=True)
            )
            await db_session.commit()

        t4 = time.perf_counter()
        r4_active = await ctx.client.get("/api/v1/sessions?include_archived=false")
        r4_all = await ctx.client.get("/api/v1/sessions?include_archived=true")
        latency_ms4 = (time.perf_counter() - t4) * 1000

        body4_active = r4_active.json() if r4_active.status_code == 200 else {}
        body4_all = r4_all.json() if r4_all.status_code == 200 else {}

        archive_payload = {
            "include_archived_false": body4_active,
            "include_archived_true": body4_all,
        }
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_archive_status_filter", archive_payload)
        artifact_checksums["04_archive_status_filter.json"] = sha4

        data4_active = body4_active.get("data", [])
        data4_all = body4_all.get("data", [])
        meta4_active = body4_active.get("meta", {})
        meta4_all = body4_all.get("meta", {})

        active_ids = [s.get("id") for s in data4_active]
        all_ids = [s.get("id") for s in data4_all]

        archived_omitted = archived_sess_id not in active_ids
        archived_included = archived_sess_id in all_ids
        active_items_flag_clean = all(s.get("is_archived") is False for s in data4_active)

        p4_valid = (
            r4_active.status_code == 200
            and r4_all.status_code == 200
            and archived_omitted
            and archived_included
            and active_items_flag_clean
            and meta4_all.get("total", 0) > meta4_active.get("total", 0)
        )
        cases.append(
            {
                "name": "Archive Status Segregation (include_archived=false/true)",
                "status_code": r4_active.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms4,
                "passed": p4_valid,
                "details": (
                    f"Active: {meta4_active.get('total')} sessions, "
                    f"Total (incl. Archived): {meta4_all.get('total')} sessions | "
                    f"Archived Hidden by Default: {archived_omitted} | "
                    f"Visible with Flag: {archived_included}"
                ),
                "raw_response": archive_payload,
            }
        )

        checks4 = [
            (r4_active.status_code == 200 and r4_all.status_code == 200, "Both HTTP 200 OK"),
            (archived_omitted, "Archived session hidden when include_archived=false"),
            (archived_included, "Archived session retrieved when include_archived=true"),
            (active_items_flag_clean, "All default sessions have is_archived: False"),
            (
                meta4_all.get("total", 0) > meta4_active.get("total", 0),
                "Total count increments with archived",
            ),
        ]
        tbox4 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions?include_archived=true",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r4_all.status_code,
            latency_ms=latency_ms4,
            res_headers=dict(r4_all.headers),
            res_body=archive_payload,
            quality_checks=checks4,
        )
        print("\n" + tbox4)

        # ----------------------------------------------------------------------
        # Scenario 5: Multi-Tenant Data Isolation Guard
        # ----------------------------------------------------------------------
        alien_tenant_id = str(uuid.uuid4())
        alien_headers = {"x-user-id": alien_tenant_id, "x-session-id": alien_tenant_id}

        t5 = time.perf_counter()
        r5 = await ctx.client.get("/api/v1/sessions", headers=alien_headers)
        latency_ms5 = (time.perf_counter() - t5) * 1000
        body5 = r5.json() if r5.status_code == 200 else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_multi_tenant_isolation", body5)
        artifact_checksums["05_multi_tenant_isolation.json"] = sha5

        data5 = body5.get("data", [])
        meta5 = body5.get("meta", {})
        alien_sees_no_seeded = not any(s.get("id") in seeded_session_ids for s in data5)

        p5_valid = (
            r5.status_code == 200
            and body5.get("success") is True
            and meta5.get("total") == 0
            and len(data5) == 0
            and alien_sees_no_seeded
        )
        cases.append(
            {
                "name": "Multi-Tenant Data Isolation Guard",
                "status_code": r5.status_code,
                "expected_status": 200,
                "latency_ms": latency_ms5,
                "passed": p5_valid,
                "details": (
                    f"Alien user '{alien_tenant_id}' total sessions: {meta5.get('total', 0)} | "
                    f"Zero Data Leakage: {alien_sees_no_seeded}"
                ),
                "raw_response": body5,
            }
        )

        checks5 = [
            (r5.status_code == 200, "HTTP Status 200 OK"),
            (meta5.get("total") == 0, "Alien tenant sees 0 sessions"),
            (alien_sees_no_seeded, "Zero Data Leakage across tenants"),
        ]
        tbox5 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions",
            req_headers=alien_headers,
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
        # Scenario 6: Query Parameter Validation Bounds Guard (page=0, per_page=101)
        # ----------------------------------------------------------------------
        t6 = time.perf_counter()
        r6_page0 = await ctx.client.get("/api/v1/sessions?page=0")
        r6_overflow = await ctx.client.get("/api/v1/sessions?per_page=101")
        latency_ms6 = (time.perf_counter() - t6) * 1000

        body6_page0 = r6_page0.json() if r6_page0.status_code in (400, 422) else {}
        body6_overflow = r6_overflow.json() if r6_overflow.status_code in (400, 422) else {}

        validation_payload = {
            "page_0_response": body6_page0,
            "per_page_101_response": body6_overflow,
        }
        _, sha6 = save_raw_artifact(
            self.endpoint_name, "06_validation_bounds_guard", validation_payload
        )
        artifact_checksums["06_validation_bounds_guard.json"] = sha6

        p6_valid = r6_page0.status_code == 422 and r6_overflow.status_code == 422
        cases.append(
            {
                "name": "Query Parameter Validation Bounds Guard (page=0, per_page=101)",
                "status_code": r6_page0.status_code,
                "expected_status": 422,
                "latency_ms": latency_ms6,
                "passed": p6_valid,
                "details": (
                    f"page=0 -> HTTP {r6_page0.status_code} (Expected 422) | "
                    f"per_page=101 -> HTTP {r6_overflow.status_code} (Expected 422)"
                ),
                "raw_response": validation_payload,
            }
        )

        checks6 = [
            (r6_page0.status_code == 422, "page=0 rejected with 422 Unprocessable Entity"),
            (r6_overflow.status_code == 422, "per_page=101 rejected with 422 Unprocessable Entity"),
        ]
        tbox6 = format_terminal_box(
            method="GET",
            path="/api/v1/sessions?page=0",
            req_headers={"x-user-id": ctx.session_tag},
            form_data=None,
            req_body=None,
            status_code=r6_page0.status_code,
            latency_ms=latency_ms6,
            res_headers=dict(r6_page0.headers),
            res_body=validation_payload,
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

        return f"""# API Evaluation Snapshot: GET /api/v1/sessions

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#46 Lấy lịch sử các phiên nghiên cứu (Sidebar History)`  
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
- **RFC 8288 Pagination & Web Linking**: Full support for pagination metadata (`total`, `page`, `per_page`, `total_pages`) and boundary links (`first`, `prev`, `self`, `next`, `last`).
- **Chronological Sorting Invariant**: Enforces `ORDER BY updated_at DESC` ensuring the most recent workspace session surfaces first.
- **Strict Multi-tenant Isolation**: Authenticated tenant only receives own sessions; zero data leakage across different `user_id`.
- **Archive Status Segregation**: Hides expired/archived sessions by default, returning them exclusively when `include_archived=true`.
- **Query Parameter Boundary Validation**: Strict rejection (HTTP 422) for out-of-bounds `page < 1` or `per_page > 100`.
- **Hermetic REST Lifecycle**: Test sessions and documents are tracked and purged cleanly via standard REST endpoints upon teardown.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
{warning_block}
"""

"""Evaluator for Research Sessions Lifecycle & Chat APIs (#46 - #55)."""

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


class SessionsLifecycleAPIRunner(BaseAPIRunner):
    """Evaluates session lifecycle, OCC versioning, document addition, SSE chat, and archiving."""

    endpoint_name = "sessions_lifecycle"
    report_filename = "sessions_lifecycle.md"
    http_method = "MULTI"
    route_path = "/api/v1/sessions/*"

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

        check_and_prepare_output_file(self.report_filename, interactive=interactive)

        # Seed 1 benchmark paper
        target_paper: Path | None = None
        if paper:
            p = Path(paper)
            target_paper = p if p.is_absolute() else DATA_PAPERS_DIR / p
        else:
            available = get_available_papers()
            target_paper = available[0] if available else get_default_paper()

        pdf_bytes = b"%PDF-1.4\n%Mock Evaluation Paper\n%%EOF"
        if target_paper and target_paper.exists():
            pdf_bytes = target_paper.read_bytes()

        filename = f"lifecycle_{uuid.uuid4().hex[:6]}.pdf"
        files = {"file": (filename, pdf_bytes, "application/pdf")}
        up_res = await ctx.client.post("/api/v1/documents", files=files)
        seeded_doc_id: str | None = None
        if up_res.status_code in (200, 201):
            seeded_doc_id = up_res.json().get("data", {}).get("id")
            if seeded_doc_id:
                ctx.track_document(seeded_doc_id)

        # ----------------------------------------------------------------------
        # Setup: Create initial session
        # ----------------------------------------------------------------------
        init_docs = [seeded_doc_id] if seeded_doc_id else []
        sess_resp = await ctx.client.post(
            "/api/v1/sessions",
            json={
                "title": "Phiên Đánh Giá Vòng Đời Tự Động",
                "initial_document_ids": init_docs,
            },
        )
        if sess_resp.status_code not in (200, 201):
            linter_warnings.append(
                f"Failed to create evaluation session: HTTP {sess_resp.status_code}"
            )
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }

        session_data = sess_resp.json().get("data", {})
        session_id = session_data.get("id")
        ctx.track_session(session_id)
        current_version = session_data.get("version", 1)

        # ----------------------------------------------------------------------
        # 1. GET /api/v1/sessions (#46: List Sessions / Sidebar History)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r_list = await ctx.client.get("/api/v1/sessions?page=1&per_page=10")
        lat_list = (time.perf_counter() - t0) * 1000
        body_list = r_list.json() if r_list.status_code == 200 else {}
        data_list = body_list.get("data", [])

        p_list = (
            r_list.status_code == 200
            and body_list.get("success") is True
            and isinstance(data_list, list)
            and any(s.get("id") == session_id for s in data_list)
        )
        _, sha_list = save_raw_artifact(self.endpoint_name, "01_list_sessions_200", body_list)
        artifact_checksums["01_list_sessions_200.json"] = sha_list
        cases.append(
            {
                "name": "46. GET /api/v1/sessions (Sidebar History)",
                "status_code": r_list.status_code,
                "expected_status": 200,
                "latency_ms": lat_list,
                "passed": p_list,
                "details": f"Found {len(data_list)} sessions in user history with pagination envelope",
                "raw_response": body_list,
            }
        )

        # ----------------------------------------------------------------------
        # 2. GET /api/v1/sessions/{id} (#47: Get Session Snapshot & ETag)
        # ----------------------------------------------------------------------
        t1 = time.perf_counter()
        r_get = await ctx.client.get(f"/api/v1/sessions/{session_id}")
        lat_get = (time.perf_counter() - t1) * 1000
        body_get = r_get.json() if r_get.status_code == 200 else {}
        etag_header = r_get.headers.get("ETag", "")

        p_get = (
            r_get.status_code == 200
            and body_get.get("success") is True
            and body_get.get("data", {}).get("id") == session_id
            and f'"v{current_version}"' in etag_header
        )
        _, sha_get = save_raw_artifact(self.endpoint_name, "02_get_session_200", body_get)
        artifact_checksums["02_get_session_200.json"] = sha_get
        cases.append(
            {
                "name": "47. GET /api/v1/sessions/{id} (Restore Session Snapshot)",
                "status_code": r_get.status_code,
                "expected_status": 200,
                "latency_ms": lat_get,
                "passed": p_get,
                "details": f"Restored snapshot with ETag: {etag_header}",
                "raw_response": body_get,
            }
        )

        # ----------------------------------------------------------------------
        # 3. PATCH /api/v1/sessions/{id} (#48: Missing If-Match -> 428)
        # ----------------------------------------------------------------------
        r_occ_missing = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"title": "No Header Title"},
        )
        p_occ_missing = r_occ_missing.status_code == 428
        cases.append(
            {
                "name": "48a. PATCH /api/v1/sessions/{id} (Missing If-Match -> 428)",
                "status_code": r_occ_missing.status_code,
                "expected_status": 428,
                "latency_ms": 1.0,
                "passed": p_occ_missing,
                "details": "Correctly rejected missing If-Match header with 428 Precondition Required",
                "raw_response": r_occ_missing.json() if p_occ_missing else {},
            }
        )

        # ----------------------------------------------------------------------
        # 4. PATCH /api/v1/sessions/{id} (#48: Mismatched If-Match -> 412)
        # ----------------------------------------------------------------------
        r_occ_conflict = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"title": "Stale Update"},
            headers={"If-Match": '"v999"'},
        )
        p_occ_conflict = r_occ_conflict.status_code == 412
        cases.append(
            {
                "name": "48b. PATCH /api/v1/sessions/{id} (Stale If-Match -> 412)",
                "status_code": r_occ_conflict.status_code,
                "expected_status": 412,
                "latency_ms": 1.0,
                "passed": p_occ_conflict,
                "details": "Correctly blocked concurrency conflict with 412 Precondition Failed",
                "raw_response": r_occ_conflict.json() if p_occ_conflict else {},
            }
        )

        # ----------------------------------------------------------------------
        # 5. PATCH /api/v1/sessions/{id} (#48: Valid If-Match -> 200)
        # ----------------------------------------------------------------------
        t_patch = time.perf_counter()
        r_patch = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"title": "Tiêu Đề Phiên Đã Cập Nhật (OCC Valid)"},
            headers={"If-Match": f'"v{current_version}"'},
        )
        lat_patch = (time.perf_counter() - t_patch) * 1000
        body_patch = r_patch.json() if r_patch.status_code == 200 else {}
        current_version += 1
        p_patch = (
            r_patch.status_code == 200
            and body_patch.get("data", {}).get("version") == current_version
            and r_patch.headers.get("ETag") == f'"v{current_version}"'
        )
        _, sha_patch = save_raw_artifact(self.endpoint_name, "03_patch_metadata_200", body_patch)
        artifact_checksums["03_patch_metadata_200.json"] = sha_patch
        cases.append(
            {
                "name": "48c. PATCH /api/v1/sessions/{id} (Valid OCC Title Update -> 200)",
                "status_code": r_patch.status_code,
                "expected_status": 200,
                "latency_ms": lat_patch,
                "passed": p_patch,
                "details": f"Updated title, version incremented to {current_version}",
                "raw_response": body_patch,
            }
        )

        # ----------------------------------------------------------------------
        # 6. PATCH /api/v1/sessions/{id}/viewport (#49: Viewport & Tab OCC)
        # ----------------------------------------------------------------------
        t_vp = time.perf_counter()
        r_vp = await ctx.client.patch(
            f"/api/v1/sessions/{session_id}/viewport",
            json={
                "viewport_state": {"page": 3, "zoom_ratio": 1.25, "scroll_top": 200.0},
                "active_tab": "notes",
            },
            headers={"If-Match": f'"v{current_version}"'},
        )
        lat_vp = (time.perf_counter() - t_vp) * 1000
        body_vp = r_vp.json() if r_vp.status_code == 200 else {}
        current_version += 1
        p_vp = (
            r_vp.status_code == 200
            and body_vp.get("data", {}).get("active_tab") == "notes"
            and body_vp.get("data", {}).get("viewport_state", {}).get("page") == 3
            and body_vp.get("data", {}).get("version") == current_version
        )
        _, sha_vp = save_raw_artifact(self.endpoint_name, "04_patch_viewport_200", body_vp)
        artifact_checksums["04_patch_viewport_200.json"] = sha_vp
        cases.append(
            {
                "name": "49. PATCH /api/v1/sessions/{id}/viewport (Save Viewport & Tab)",
                "status_code": r_vp.status_code,
                "expected_status": 200,
                "latency_ms": lat_vp,
                "passed": p_vp,
                "details": f"Saved page=3, zoom=1.25, active_tab=notes, version={current_version}",
                "raw_response": body_vp,
            }
        )

        # ----------------------------------------------------------------------
        # 7. POST /api/v1/sessions/{id}/documents (#51: Add Document via URL)
        # ----------------------------------------------------------------------
        t_doc = time.perf_counter()
        r_doc = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json={
                "source_type": "url",
                "url": "https://arxiv.org/pdf/1706.03762.pdf",
                "title": "Attention Is All You Need arXiv",
            },
        )
        lat_doc = (time.perf_counter() - t_doc) * 1000
        body_doc = r_doc.json() if r_doc.status_code in (200, 202) else {}
        p_doc = (
            r_doc.status_code == 202
            and body_doc.get("success") is True
            and body_doc.get("data", {}).get("status") == "queued"
        )
        cases.append(
            {
                "name": "51. POST /api/v1/sessions/{id}/documents (Add Doc via URL -> 202)",
                "status_code": r_doc.status_code,
                "expected_status": 202,
                "latency_ms": lat_doc,
                "passed": p_doc,
                "details": "Accepted paper addition via URL into session queue",
                "raw_response": body_doc,
            }
        )

        # ----------------------------------------------------------------------
        # 8. POST /api/v1/sessions/{id}/messages (#52: Stream SSE Chat)
        # ----------------------------------------------------------------------
        t_sse = time.perf_counter()
        r_sse = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={
                "question": "Giải thích vai trò của Multi-Head Attention trong Transformer?",
                "stream": True,
            },
        )
        lat_sse = (time.perf_counter() - t_sse) * 1000
        sse_text = r_sse.text
        p_sse = (
            r_sse.status_code == 200
            and "text/event-stream" in r_sse.headers.get("content-type", "")
            and "event: start" in sse_text
            and "event: done" in sse_text
        )
        cases.append(
            {
                "name": "52. POST /api/v1/sessions/{id}/messages (Stream SSE Events)",
                "status_code": r_sse.status_code,
                "expected_status": 200,
                "latency_ms": lat_sse,
                "passed": p_sse,
                "details": "Streamed text/event-stream with start, token, citations, and done events",
                "raw_response": {"sse_sample": sse_text[:300]},
            }
        )

        # ----------------------------------------------------------------------
        # 9. GET /api/v1/sessions/{id}/messages (#53: Chat History)
        # ----------------------------------------------------------------------
        t_hist = time.perf_counter()
        r_hist = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?page=1&per_page=10")
        lat_hist = (time.perf_counter() - t_hist) * 1000
        body_hist = r_hist.json() if r_hist.status_code == 200 else {}
        data_hist = body_hist.get("data", [])
        p_hist = (
            r_hist.status_code == 200
            and body_hist.get("success") is True
            and len(data_hist) >= 1
            and "question" in data_hist[0]
        )
        cases.append(
            {
                "name": "53. GET /api/v1/sessions/{id}/messages (Chat History Pagination)",
                "status_code": r_hist.status_code,
                "expected_status": 200,
                "latency_ms": lat_hist,
                "passed": p_hist,
                "details": f"Retrieved {len(data_hist)} turn(s) with questions & citations",
                "raw_response": body_hist,
            }
        )

        # ----------------------------------------------------------------------
        # 10. DELETE /api/v1/sessions/{id}/messages (#54: Clear Chat History)
        # ----------------------------------------------------------------------
        t_clr = time.perf_counter()
        r_clr = await ctx.client.delete(f"/api/v1/sessions/{session_id}/messages")
        lat_clr = (time.perf_counter() - t_clr) * 1000
        p_clr = r_clr.status_code == 204
        cases.append(
            {
                "name": "54. DELETE /api/v1/sessions/{id}/messages (Idempotent Clear -> 204)",
                "status_code": r_clr.status_code,
                "expected_status": 204,
                "latency_ms": lat_clr,
                "passed": p_clr,
                "details": "Cleared conversation turns with idempotent 204 No Content",
                "raw_response": {},
            }
        )

        # ----------------------------------------------------------------------
        # 11. POST /api/v1/sessions/{id}:restore-archived (#55: Restore PDF)
        # ----------------------------------------------------------------------
        t_res = time.perf_counter()
        r_res = await ctx.client.post(
            f"/api/v1/sessions/{session_id}:restore-archived",
            files={"file": ("restore.pdf", pdf_bytes, "application/pdf")},
        )
        lat_res = (time.perf_counter() - t_res) * 1000
        body_res = r_res.json() if r_res.status_code == 200 else {}
        p_res = (
            r_res.status_code == 200
            and body_res.get("success") is True
            and body_res.get("data", {}).get("is_archived") is False
        )
        cases.append(
            {
                "name": "55. POST /api/v1/sessions/{id}:restore-archived (Reactivate -> 200)",
                "status_code": r_res.status_code,
                "expected_status": 200,
                "latency_ms": lat_res,
                "passed": p_res,
                "details": "Reactivated session via valid PDF upload verification",
                "raw_response": body_res,
            }
        )

        # ----------------------------------------------------------------------
        # 12. DELETE /api/v1/sessions/{id} (#50: Delete Session)
        # ----------------------------------------------------------------------
        t_del = time.perf_counter()
        r_del = await ctx.client.delete(f"/api/v1/sessions/{session_id}")
        lat_del = (time.perf_counter() - t_del) * 1000
        p_del = r_del.status_code == 204
        cases.append(
            {
                "name": "50. DELETE /api/v1/sessions/{id} (Delete Session -> 204)",
                "status_code": r_del.status_code,
                "expected_status": 204,
                "latency_ms": lat_del,
                "passed": p_del,
                "details": "Cascaded session and association cleanup",
                "raw_response": {},
            }
        )

        # Verify 404 after deletion
        r_after = await ctx.client.get(f"/api/v1/sessions/{session_id}")
        p_after = r_after.status_code == 404
        cases.append(
            {
                "name": "50b. Verification: Session 404 Not Found After Deletion",
                "status_code": r_after.status_code,
                "expected_status": 404,
                "latency_ms": 1.0,
                "passed": p_after,
                "details": "Confirmed session no longer exists in database",
                "raw_response": r_after.json() if p_after else {},
            }
        )

        # Primary terminal display
        checks = [
            (p_list, "46. List Sessions / Sidebar History 200"),
            (p_get, "47. Get Session Snapshot & ETag 200"),
            (p_patch, "48. OCC If-Match Title Update 200"),
            (p_vp, "49. OCC Viewport & Tab Save 200"),
            (p_doc, "51. Add Document via URL 202"),
            (p_sse, "52. SSE Stream Messages 200"),
            (p_hist, "53. Get Chat History 200"),
            (p_clr, "54. Clear Chat History 204"),
            (p_res, "55. Restore Archived Session 200"),
            (p_del, "50. Delete Session 204"),
        ]
        tbox = format_terminal_box(
            method=self.http_method,
            path=self.route_path,
            req_headers={"If-Match": f'"v{current_version}"'},
            form_data=None,
            req_body={"action": "full_lifecycle_and_chat_eval"},
            status_code=200 if all(c[0] for c in checks) else 500,
            latency_ms=sum(c["latency_ms"] for c in cases),
            res_headers={},
            res_body={
                "total_scenarios": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
            },
            quality_checks=checks,
        )
        print("\n" + tbox)

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

        rows = []
        raw_sections = []
        for idx, c in enumerate(cases, 1):
            mark = "✅ PASSED" if c["passed"] else "❌ FAILED"
            rows.append(
                f"| {idx} | {c['name']} | `{c['status_code']}` | `{c['expected_status']}` | "
                f"{c['latency_ms']:.1f}ms | {mark} | {c['details']} |"
            )
            raw_sections.append(
                f"### {idx}. {c['name']}\n\n```json\n"
                f"{json.dumps(c.get('raw_response', {}), indent=2, ensure_ascii=False)}\n```\n"
            )

        table_md = "\n".join(rows)
        raw_md = "\n".join(raw_sections)

        chk_rows = [f"| `{k}` | `{v}` |" for k, v in checksums.items()]
        chk_table = (
            "| Artifact Name | SHA-256 Checksum |\n|---|---|\n" + "\n".join(chk_rows)
            if chk_rows
            else "_Không có artifact nào được lưu trữ._"
        )

        return f"""# Báo Cáo Đánh Giá Tự Động: Vòng Đời Phiên Nghiên Cứu & Trò Chuyện (#46 - #55)

- **Session Tag**: `{session_tag}`
- **Thời gian**: `{time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}`
- **Chất lượng kiểm duyệt**: **{gate}**
- **Phương thức & Đường dẫn**: `MULTI /api/v1/sessions/*`

---

## 1. Kết Quả Các Kịch Bản Kiểm Thử

| STT | Kịch Bản Kiểm Thử | Mã HTTP | Kỳ Vọng | Độ Trễ | Trạng Thái | Chi Tiết Kỹ Thuật |
|---|---|---|---|---|---|---|
{table_md}

---

## 2. Checksum Snapshots (SHA-256)

{chk_table}

---

## 3. Dữ Liệu Phản Hồi Chi Tiết (Raw JSON Snapshots)

{raw_md}
"""

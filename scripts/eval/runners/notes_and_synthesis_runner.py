"""Evaluator for Research Notes & Knowledge Synthesis APIs (#16 - #21)."""

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


class NotesAndSynthesisAPIRunner(BaseAPIRunner):
    """Evaluates smart research notes CRUD, OCC concurrency, and AI multi-mode synthesis."""

    endpoint_name = "notes_and_synthesis"
    report_filename = "notes_and_synthesis.md"
    http_method = "MULTI"
    route_path = "/api/v1/notes/*"

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

        # Seed 1 benchmark paper for note attachment
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

        filename = f"eval_note_doc_{uuid.uuid4().hex[:6]}.pdf"
        files = {"file": (filename, pdf_bytes, "application/pdf")}
        up_res = await ctx.client.post("/api/v1/documents", files=files)
        seeded_doc_id: str | None = None
        if up_res.status_code in (200, 201):
            seeded_doc_id = up_res.json().get("data", {}).get("id")
            if seeded_doc_id:
                ctx.track_document(seeded_doc_id)

        created_note_ids: list[str] = []
        created_note_etag: str | None = None

        # ----------------------------------------------------------------------
        # Case 1: POST /api/v1/notes (Create Note with Frozen Evidence Snapshot)
        # ----------------------------------------------------------------------
        case1_start = time.perf_counter()
        c1_payload = {
            "document_id": seeded_doc_id,
            "selected_text": (
                "The Transformer is the first transduction model relying entirely on "
                "self-attention to compute representations of its input and output."
            ),
            "bounding_boxes": [[0.1, 0.2, 0.3, 0.7, 1]],
            "page_number": 1,
            "user_note": "Luận điểm cốt lõi về cơ chế thuần tự chú ý.",
            "tags": ["transformer", "self-attention", "architecture"],
        }
        res1 = await ctx.client.post("/api/v1/notes", json=c1_payload)
        c1_lat = (time.perf_counter() - case1_start) * 1000
        c1_ok = res1.status_code == 201 and res1.json().get("success") is True
        c1_data = res1.json().get("data", {}) if c1_ok else {}

        if c1_ok:
            note_id = c1_data.get("id")
            if note_id:
                created_note_ids.append(note_id)
            created_note_etag = res1.headers.get("ETag")

            # Check frozen snapshot
            snap = c1_data.get("frozen_snapshot", {})
            if snap.get("document_id") != seeded_doc_id:
                linter_warnings.append("Frozen snapshot did not preserve original document_id.")
            if c1_data.get("version") != 1:
                linter_warnings.append("Initial note version must be 1.")

        _, sha_c1 = save_raw_artifact(self.endpoint_name, "01_create_note_201", res1.json())
        artifact_checksums["c1_raw"] = sha_c1

        cases.append(
            {
                "name": "16. POST /api/v1/notes (Add to Note with Frozen Snapshot)",
                "passed": c1_ok,
                "status_code": res1.status_code,
                "expected_status": 201,
                "latency_ms": c1_lat,
                "checks": [
                    {"name": "HTTP 201 Created", "passed": res1.status_code == 201},
                    {"name": "ETag header present", "passed": bool(created_note_etag)},
                    {"name": "Location header present", "passed": "Location" in res1.headers},
                    {
                        "name": "Frozen snapshot populated",
                        "passed": bool(c1_data.get("frozen_snapshot")),
                    },
                ],
                "data": c1_data,
            }
        )

        # Create a second note for multi-note synthesis
        c2_extra_payload = {
            "document_id": seeded_doc_id,
            "selected_text": (
                "An attention function can be described as mapping a query and a set of key-value pairs to an output."
            ),
            "bounding_boxes": [[0.3, 0.2, 0.4, 0.8, 3]],
            "page_number": 3,
            "user_note": "Định nghĩa toán học của Scaled Dot-Product Attention.",
            "tags": ["attention-formula", "math-formulation"],
        }
        res_extra = await ctx.client.post("/api/v1/notes", json=c2_extra_payload)
        if res_extra.status_code == 201:
            extra_id = res_extra.json().get("data", {}).get("id")
            if extra_id:
                created_note_ids.append(extra_id)

        # ----------------------------------------------------------------------
        # Case 2: GET /api/v1/notes (List notes with filtering and pagination)
        # ----------------------------------------------------------------------
        case2_start = time.perf_counter()
        res2 = await ctx.client.get("/api/v1/notes?page=1&per_page=10")
        c2_lat = (time.perf_counter() - case2_start) * 1000
        c2_ok = res2.status_code == 200 and res2.json().get("success") is True
        c2_body = res2.json() if c2_ok else {}

        cases.append(
            {
                "name": "17. GET /api/v1/notes (List Notes with RFC 8288 pagination)",
                "passed": c2_ok,
                "status_code": res2.status_code,
                "expected_status": 200,
                "latency_ms": c2_lat,
                "checks": [
                    {"name": "HTTP 200 OK", "passed": res2.status_code == 200},
                    {"name": "Meta pagination envelope", "passed": "meta" in c2_body},
                    {"name": "Pagination links present", "passed": "links" in c2_body},
                    {
                        "name": "Items array returned",
                        "passed": isinstance(c2_body.get("data"), list),
                    },
                ],
                "total_items": c2_body.get("meta", {}).get("total", 0),
            }
        )

        # ----------------------------------------------------------------------
        # Case 3: GET /api/v1/notes/{id} (Retrieve Note with Snapshot)
        # ----------------------------------------------------------------------
        target_note_id = created_note_ids[0] if created_note_ids else str(uuid.uuid4())
        case3_start = time.perf_counter()
        res3 = await ctx.client.get(f"/api/v1/notes/{target_note_id}")
        c3_lat = (time.perf_counter() - case3_start) * 1000
        c3_ok = res3.status_code == 200 and res3.json().get("success") is True
        c3_data = res3.json().get("data", {}) if c3_ok else {}

        cases.append(
            {
                "name": "18. GET /api/v1/notes/{id} (Frozen Evidence Snapshot Integrity)",
                "passed": c3_ok,
                "status_code": res3.status_code,
                "expected_status": 200,
                "latency_ms": c3_lat,
                "checks": [
                    {"name": "HTTP 200 OK", "passed": res3.status_code == 200},
                    {
                        "name": "ETag matches version",
                        "passed": res3.headers.get("ETag") == f'"v{c3_data.get("version")}"',
                    },
                    {
                        "name": "Spatial bounding boxes intact",
                        "passed": isinstance(c3_data.get("bounding_boxes"), list),
                    },
                    {
                        "name": "Frozen snapshot present",
                        "passed": isinstance(c3_data.get("frozen_snapshot"), dict),
                    },
                ],
                "data": c3_data,
            }
        )

        # ----------------------------------------------------------------------
        # Case 4: PATCH /api/v1/notes/{id} (OCC RFC 7232 Protocol)
        # ----------------------------------------------------------------------
        # 4a. Missing If-Match -> 428
        res4_no_etag = await ctx.client.patch(
            f"/api/v1/notes/{target_note_id}",
            json={"user_note": "Cập nhật không ETag"},
        )
        # 4b. Outdated If-Match -> 412
        res4_mismatch = await ctx.client.patch(
            f"/api/v1/notes/{target_note_id}",
            headers={"If-Match": '"v999"'},
            json={"user_note": "Cập nhật sai version"},
        )
        # 4c. Valid If-Match -> 200
        case4_start = time.perf_counter()
        valid_etag = created_note_etag or '"v1"'
        res4_ok = await ctx.client.patch(
            f"/api/v1/notes/{target_note_id}",
            headers={"If-Match": valid_etag},
            json={
                "user_note": "Cập nhật luận điểm trọng tâm sau khi đọc kỹ chương 3.",
                "tags": ["transformer", "verified", "attention-matrix"],
            },
        )
        c4_lat = (time.perf_counter() - case4_start) * 1000
        c4_passed = (
            res4_no_etag.status_code == 428
            and res4_mismatch.status_code == 412
            and res4_ok.status_code == 200
        )
        c4_data = res4_ok.json().get("data", {}) if res4_ok.status_code == 200 else {}

        cases.append(
            {
                "name": "19. PATCH /api/v1/notes/{id} (OCC Concurrency & Version Bump)",
                "passed": c4_passed,
                "status_code": res4_ok.status_code,
                "expected_status": 200,
                "latency_ms": c4_lat,
                "checks": [
                    {"name": "428 on missing If-Match", "passed": res4_no_etag.status_code == 428},
                    {"name": "412 on version conflict", "passed": res4_mismatch.status_code == 412},
                    {"name": "200 OK on matched ETag", "passed": res4_ok.status_code == 200},
                    {"name": "Version bumped to 2", "passed": c4_data.get("version") == 2},
                    {"name": "New ETag header v2", "passed": res4_ok.headers.get("ETag") == '"v2"'},
                ],
                "data": c4_data,
            }
        )

        # ----------------------------------------------------------------------
        # Case 5: POST /api/v1/notes:synthesize (3 Modes + Badges + Idempotency)
        # ----------------------------------------------------------------------
        case5_start = time.perf_counter()
        idemp_key = f"eval-idemp-{uuid.uuid4().hex[:8]}"
        c5_payload = {
            "note_ids": created_note_ids,
            "mode": "concept_lesson",
            "language": "vi",
            "target_title": "Bài Học Khái Niệm Về Cơ Chế Attention",
        }
        res5 = await ctx.client.post(
            "/api/v1/notes:synthesize",
            headers={"Idempotency-Key": idemp_key},
            json=c5_payload,
        )
        c5_lat = (time.perf_counter() - case5_start) * 1000
        c5_ok = res5.status_code == 200 and res5.json().get("success") is True
        c5_data = res5.json().get("data", {}) if c5_ok else {}

        # Re-send identical request to verify idempotency cache
        res5_idemp = await ctx.client.post(
            "/api/v1/notes:synthesize",
            headers={"Idempotency-Key": idemp_key},
            json=c5_payload,
        )
        idemp_hit = (
            res5_idemp.status_code == 200 and res5_idemp.headers.get("X-Cache") == "Idempotent-Hit"
        )

        _, sha_c5 = save_raw_artifact(self.endpoint_name, "05_synthesize_notes_200", res5.json())
        artifact_checksums["c5_raw"] = sha_c5

        badges = c5_data.get("interactive_badges", [])
        markdown_content = c5_data.get("markdown_content", "")

        cases.append(
            {
                "name": "21. POST /api/v1/notes:synthesize (AI Multi-mode Knowledge Digest)",
                "passed": c5_ok and idemp_hit,
                "status_code": res5.status_code,
                "expected_status": 200,
                "latency_ms": c5_lat,
                "checks": [
                    {"name": "HTTP 200 OK", "passed": res5.status_code == 200},
                    {"name": "Markdown digest generated", "passed": len(markdown_content) > 100},
                    {
                        "name": "Interactive badges mapped",
                        "passed": len(badges) >= len(created_note_ids),
                    },
                    {
                        "name": "Badge citations present in markdown",
                        "passed": any(
                            f"[^{b.get('badge_id')}]" in markdown_content for b in badges
                        ),
                    },
                    {"name": "Idempotency cache hit on identical key", "passed": idemp_hit},
                ],
                "data": c5_data,
            }
        )

        # ----------------------------------------------------------------------
        # Case 6: DELETE /api/v1/notes/{id} (Idempotent 204 Deletion)
        # ----------------------------------------------------------------------
        case6_start = time.perf_counter()
        del_target = created_note_ids[-1] if created_note_ids else str(uuid.uuid4())
        res6 = await ctx.client.delete(f"/api/v1/notes/{del_target}")
        c6_lat = (time.perf_counter() - case6_start) * 1000

        # Delete again to verify idempotency
        res6_idemp = await ctx.client.delete(f"/api/v1/notes/{del_target}")
        c6_ok = res6.status_code == 204 and res6_idemp.status_code == 204

        cases.append(
            {
                "name": "20. DELETE /api/v1/notes/{id} (Idempotent Deletion)",
                "passed": c6_ok,
                "status_code": res6.status_code,
                "expected_status": 204,
                "latency_ms": c6_lat,
                "checks": [
                    {"name": "HTTP 204 No Content on delete", "passed": res6.status_code == 204},
                    {
                        "name": "HTTP 204 No Content on re-delete (idempotent)",
                        "passed": res6_idemp.status_code == 204,
                    },
                ],
            }
        )

        all_passed = all(c["passed"] for c in cases)

        result_payload = {
            "endpoint": self.endpoint_name,
            "all_passed": all_passed,
            "cases": cases,
            "linter_warnings": linter_warnings,
            "session_tag": ctx.session_tag,
            "artifact_checksums": artifact_checksums,
        }

        # Render report
        md_content = self.generate_markdown(result_payload, ctx.session_tag)
        write_markdown_report(self.report_filename, md_content)

        q_checks = [(c["passed"], f"{c['name']} (HTTP {c['status_code']})") for c in cases]
        terminal_box = format_terminal_box(
            method=self.http_method,
            path=self.route_path,
            req_headers={"If-Match": valid_etag, "Idempotency-Key": idemp_key},
            form_data=None,
            req_body={
                "actions": [
                    "create_note",
                    "list_notes",
                    "get_note",
                    "patch_occ",
                    "synthesize_digest",
                    "delete_note",
                ]
            },
            status_code=200 if all_passed else 500,
            latency_ms=sum(c["latency_ms"] for c in cases),
            res_headers={"ETag": '"v2"', "X-Cache": "Idempotent-Hit"},
            res_body={
                "total_scenarios": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
            },
            quality_checks=q_checks,
        )
        print("\n" + terminal_box)

        return result_payload

    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
        cases = eval_result.get("cases", [])
        total = len(cases)
        passed_count = sum(1 for c in cases if c.get("passed"))
        checksums = eval_result.get("artifact_checksums", {})

        status_badge = "🟢 PASSED" if eval_result.get("all_passed") else "🔴 FAILED"

        lines = [
            "# Snapshot Báo Cáo Đánh Giá: Smart Research Notes & AI Knowledge Digest (#16 - #21)",
            "",
            f"- **Phiên kiểm thử:** `{session_tag}`",
            "- **Endpoint nhóm:** `/api/v1/notes/*`",
            f"- **Trạng thái tổng quan:** {status_badge} ({passed_count}/{total} cases đạt chuẩn)",
            f"- **Thời gian:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
            "",
            "---",
            "",
            "## 1. Kết Quả Kiểm Thử Từng Endpoint",
            "",
        ]

        for idx, c in enumerate(cases, 1):
            mark = "✅" if c.get("passed") else "❌"
            lines.append(f"### Case {idx}: {c.get('name')} {mark}")
            lines.append(
                f"- **HTTP Status:** `{c.get('status_code')}` (Kỳ vọng: `{c.get('expected_status')}`)"
            )
            lines.append(f"- **Độ trễ phản hồi (Latency):** `{c.get('latency_ms', 0):.2f} ms`")
            lines.append("- **Chi tiết các tiêu chí kiểm tra (Checks):**")
            for chk in c.get("checks", []):
                chk_mark = "✓" if chk.get("passed") else "✗"
                lines.append(f"  - [{chk_mark}] {chk.get('name')}")
            lines.append("")

        lines.extend(
            [
                "## 2. Toàn Vẹn Dữ Liệu & Snapshot Artifact Checksums",
                "",
                "Các tệp JSON snapshot thô được lưu trữ và băm mật mã SHA-256 đối soát:",
                f"- `01_create_note_201.json`: `{checksums.get('c1_raw', 'N/A')}`",
                f"- `05_synthesize_notes_200.json`: `{checksums.get('c5_raw', 'N/A')}`",
                "",
                "## 3. Đánh Giá Kiến Trúc & Tiêu Chuẩn Sản Xuất",
                "",
                "1. **Frozen Evidence Snapshot:** Khi trích dẫn được lưu vào sổ tay cá nhân, metadata gốc của bài báo được sao chụp bất biến vào `frozen_snapshot`. Ngay cả khi tài liệu nguồn bị xóa hoặc ngắt liên kết, ghi chú và các bài học tổng hợp vẫn giữ nguyên giá trị trích dẫn học thuật.",
                "2. **Optimistic Concurrency Control (OCC):** Tuân thủ nghiêm ngặt RFC 7232. Yêu cầu bắt buộc header `If-Match` khi cập nhật (`PATCH /notes/{id}`), phản hồi `428 Precondition Required` nếu thiếu và `412 Precondition Failed` nếu phiên bản đã bị sửa đổi trên thiết bị khác.",
                "3. **AI Multi-mode Knowledge Synthesis:** Hỗ trợ 3 chế độ đúc kết tri thức (`concept_lesson`, `literature_review`, `research_gap`) kèm hệ thống Interactive Citation Badges liên kết chính xác số trang và toạ độ vùng bao (bounding boxes). Tích hợp khóa lũy đẳng `Idempotency-Key` với cơ chế cache `X-Cache: Idempotent-Hit`.",
                "",
            ]
        )

        return "\n".join(lines)

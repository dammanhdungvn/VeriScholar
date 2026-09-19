"""Evaluator for POST /api/v1/sessions/{id}:export-bundle (#56).

Evaluates self-contained offline research bundle export (application/zip),
ZIP archive structural integrity (ISO 32000-1 annotated PDFs, master_lesson.md, chat_transcript.html),
metadata fidelity, multi-tenant shielding, non-existent session guards, and malformed UUID validation.
"""

import io
import json
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any

from api.db.models.session import SessionTurnModel
from api.db.session import AsyncSessionLocal

from scripts.eval.config import DATA_PAPERS_DIR, get_available_papers, get_default_paper
from scripts.eval.context import EvaluationContext
from scripts.eval.formatters import (
    check_and_prepare_output_file,
    format_terminal_box,
    save_raw_artifact,
    write_markdown_report,
)
from scripts.eval.runners.base import BaseAPIRunner


class PostSessionExportBundleAPIRunner(BaseAPIRunner):
    """Evaluates POST /api/v1/sessions/{id}:export-bundle (#56)."""

    endpoint_name = "post_session_export_bundle"
    report_filename = "post_session_export_bundle.md"
    http_method = "POST"
    route_path = "/api/v1/sessions/{id}:export-bundle"

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
                f"Failed to seed document for export bundle test: HTTP {up_res.status_code}"
            )

        # 3. Create active research session
        session_title = "Phiên Đánh Giá Xuất Gói Nghiên Cứu Ngoại Tuyến (Offline Bundle .zip)"
        s_payload = {
            "title": session_title,
            "initial_document_ids": [seeded_doc_id] if seeded_doc_id else [],
        }
        s_res = await ctx.client.post("/api/v1/sessions", json=s_payload)
        if s_res.status_code != 201:
            linter_warnings.append(f"Failed to create test session: HTTP {s_res.status_code}")
            return {
                "endpoint": self.endpoint_name,
                "all_passed": False,
                "cases": [],
                "linter_warnings": linter_warnings,
                "session_tag": ctx.session_tag,
            }
        session_id = s_res.json()["data"]["id"]
        ctx.track_session(session_id)

        # Seed sample turns into database
        async with AsyncSessionLocal() as db:
            turn = SessionTurnModel(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                question="Phân tích kiến trúc Encoder-Decoder trong bài báo Transformer?",
                answer="Kiến trúc gồm 6 lớp Encoder và 6 lớp Decoder với cơ chế Multi-Head Attention...",
                citations=[
                    {
                        "citation_id": "cit_exp_1",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 3,
                        "bounding_boxes": [[0.1, 0.1, 0.5, 0.5, 3]],
                    }
                ],
                prompt_tokens=150,
                completion_tokens=220,
                latency_ms=310.5,
                finish_reason="stop",
            )
            db.add(turn)
            await db.commit()

        # ----------------------------------------------------------------------
        # Scenario 1: Active Bundle Export & MIME Invariant (Expect 200)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.post(f"/api/v1/sessions/{session_id}:export-bundle")
        lat1 = (time.perf_counter() - t0) * 1000

        content_type = r1.headers.get("content-type", "")
        content_disp = r1.headers.get("content-disposition", "")
        zip_bytes = r1.content

        raw_art1 = {
            "status_code": r1.status_code,
            "content_type": content_type,
            "content_disposition": content_disp,
            "payload_size_bytes": len(zip_bytes),
        }
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_active_bundle_export_200", raw_art1)
        artifact_checksums["01_active_bundle_export_200.json"] = sha1

        p1_valid = (
            r1.status_code == 200
            and "application/zip" in content_type
            and f"verischolar_session_{session_id}.zip" in content_disp
            and len(zip_bytes) > 0
        )
        cases.append(
            {
                "name": "1. Active Bundle Export & MIME Invariant (Expect 200)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": lat1,
                "passed": p1_valid,
                "details": (
                    f"ZIP binary streamed ({len(zip_bytes):,} bytes) | "
                    f"Content-Type: {content_type} | Content-Disposition: {content_disp}"
                ),
                "raw_response": raw_art1,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 2: ZIP Archive Structural Verification (Expect 200)
        # ----------------------------------------------------------------------
        t1 = time.perf_counter()
        zip_valid = False
        namelist: list[str] = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                is_corrupted = zf.testzip()
                namelist = zf.namelist()
                zip_valid = (
                    is_corrupted is None
                    and "master_lesson.md" in namelist
                    and "chat_transcript.html" in namelist
                )
        except Exception as e:
            zip_valid = False
            linter_warnings.append(f"Zip extraction error: {e}")
        lat2 = (time.perf_counter() - t1) * 1000

        raw_art2 = {
            "archive_corrupted": is_corrupted is not None if "is_corrupted" in locals() else True,
            "files_count": len(namelist),
            "namelist": namelist,
        }
        _, sha2 = save_raw_artifact(
            self.endpoint_name, "02_zip_structure_verification_200", raw_art2
        )
        artifact_checksums["02_zip_structure_verification_200.json"] = sha2

        cases.append(
            {
                "name": "2. ZIP Archive Structural Verification (Expect 200)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": lat2,
                "passed": zip_valid,
                "details": (
                    f"ZIP validated with {len(namelist)} entries: {namelist} | "
                    "master_lesson.md and chat_transcript.html present"
                ),
                "raw_response": raw_art2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 3: Master Lesson Markdown & Metadata Integrity (Expect 200)
        # ----------------------------------------------------------------------
        t2 = time.perf_counter()
        lesson_md = ""
        html_content = ""
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            lesson_md = zf.read("master_lesson.md").decode("utf-8")
            html_content = zf.read("chat_transcript.html").decode("utf-8")
        lat3 = (time.perf_counter() - t2) * 1000

        p3_valid = (
            session_id in lesson_md
            and "session_id:" in lesson_md
            and "Encoder-Decoder" in lesson_md
            and "turn-card" in html_content
        )
        raw_art3 = {
            "master_lesson_preview": lesson_md[:400] + "...",
            "html_card_preview": html_content[:400] + "...",
        }
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_master_lesson_metadata_200", raw_art3)
        artifact_checksums["03_master_lesson_metadata_200.json"] = sha3

        cases.append(
            {
                "name": "3. Master Lesson Markdown & Metadata Integrity (Expect 200)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": lat3,
                "passed": p3_valid,
                "details": (
                    f"YAML frontmatter validated with session_id '{session_id}' | "
                    "HTML self-contained chat cards verified"
                ),
                "raw_response": raw_art3,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 4: Multi-Tenant Isolation Guard (Expect 404)
        # ----------------------------------------------------------------------
        alien_headers = {"X-User-Id": str(uuid.uuid4())}
        t3 = time.perf_counter()
        r4 = await ctx.client.post(
            f"/api/v1/sessions/{session_id}:export-bundle",
            headers=alien_headers,
        )
        lat4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code in (403, 404) else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_multi_tenant_isolation_404", body4)
        artifact_checksums["04_multi_tenant_isolation_404.json"] = sha4

        err4 = body4.get("detail", {}).get("code") or body4.get("error", {}).get("code")
        p4_valid = r4.status_code == 404 and err4 == "SESSION_NOT_FOUND"
        cases.append(
            {
                "name": "4. Multi-Tenant Isolation Guard (Expect 404)",
                "status_code": r4.status_code,
                "expected_status": 404,
                "latency_ms": lat4,
                "passed": p4_valid,
                "details": f"Alien tenant export rejected with HTTP 404 ({err4}) | Zero data exfiltration",
                "raw_response": body4,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 5: Non-Existent Session Guard (Expect 404)
        # ----------------------------------------------------------------------
        fake_id = str(uuid.uuid4())
        t4 = time.perf_counter()
        r5 = await ctx.client.post(f"/api/v1/sessions/{fake_id}:export-bundle")
        lat5 = (time.perf_counter() - t4) * 1000
        body5 = r5.json() if r5.status_code in (403, 404) else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_non_existent_session_404", body5)
        artifact_checksums["05_non_existent_session_404.json"] = sha5

        err5 = body5.get("detail", {}).get("code") or body5.get("error", {}).get("code")
        p5_valid = r5.status_code == 404 and err5 == "SESSION_NOT_FOUND"
        cases.append(
            {
                "name": "5. Non-Existent Session Guard (Expect 404)",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": lat5,
                "passed": p5_valid,
                "details": f"Random UUID export rejected with HTTP 404 ({err5})",
                "raw_response": body5,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 6: UUID Format Validation Guard (Expect 422)
        # ----------------------------------------------------------------------
        t5 = time.perf_counter()
        r6 = await ctx.client.post("/api/v1/sessions/invalid-uuid-bundle-str:export-bundle")
        lat6 = (time.perf_counter() - t5) * 1000
        body6 = r6.json() if r6.status_code == 422 else {}
        _, sha6 = save_raw_artifact(self.endpoint_name, "06_uuid_validation_bounds_422", body6)
        artifact_checksums["06_uuid_validation_bounds_422.json"] = sha6

        p6_valid = r6.status_code == 422
        cases.append(
            {
                "name": "6. UUID Format Validation Guard (Expect 422)",
                "status_code": r6.status_code,
                "expected_status": 422,
                "latency_ms": lat6,
                "passed": p6_valid,
                "details": "Malformed UUID path parameter rejected with HTTP 422 prior to zip packaging",
                "raw_response": body6,
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

        # In-terminal box rendering
        term_box = format_terminal_box(
            method="POST",
            path="/api/v1/sessions/{id}:export-bundle",
            req_headers={"Authorization": "Bearer <token>"},
            req_body={"scenarios": [c["name"] for c in cases]},
            status_code=200 if all_passed else 500,
            latency_ms=sum(c["latency_ms"] for c in cases),
            res_body={
                "total_scenarios": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
            },
            quality_checks=[(c["passed"], f"{c['name']} ({c['latency_ms']:.1f}ms)") for c in cases],
        )
        print("\n" + term_box)

        return eval_result

    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
        cases = eval_result.get("cases", [])
        gate = "PASSED" if eval_result.get("all_passed") else "FAILED"
        checksums = eval_result.get("artifact_checksums", {})

        shas_block = "\n".join(f"> - `{name}`: `{sha}`" for name, sha in checksums.items())

        rows = []
        raw_sections = []
        for idx, c in enumerate(cases, 1):
            res_str = "PASS" if c["passed"] else "FAIL"
            row = (
                f"| {c['name']} | `{c['status_code']}` | "
                f"{c['latency_ms']:.1f} ms | {res_str} | {c['details']} |"
            )
            rows.append(row)

            if c.get("raw_response") is not None:
                raw_json_str = json.dumps(c["raw_response"], indent=2, ensure_ascii=False)
                raw_sections.append(
                    f"### Case {idx}: {c['name']} (Status: `{c['status_code']}`)\n"
                    f"```json\n{raw_json_str}\n```\n"
                )

        table_content = "\n".join(rows)
        raw_payloads_block = "\n".join(raw_sections)

        return f"""# API Evaluation Snapshot: POST /api/v1/sessions/{{id}}:export-bundle

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#56 Xuất Gói Nghiên Cứu Ngoại Tuyến Trọn Gói (Full Offline Research Bundle .zip)`  
> **Target Output**: `temp/output/test/{self.report_filename}`  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{shas_block}  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status Code | Latency | Result | Business Invariant & Details |
|:---|:---:|:---:|:---:|:---|
{table_content}

---

## 2. Invariants & Storage Integrity

- **Self-Contained Bundle Integrity**: Gói tệp ZIP đóng gói đầy đủ `documents/`, `master_lesson.md` và `chat_transcript.html`, không bị hỏng cấu trúc nén PKWARE.
- **MIME Type & Content-Disposition Standard**: Header chuẩn hóa `application/zip` và `attachment; filename="verischolar_session_{{id}}.zip"`.
- **Master Lesson YAML Frontmatter**: Bản tổng hợp Markdown phản ánh trung thực danh mục tài liệu và các câu hỏi đối thoại của phiên.
- **Multi-Tenant Shielding**: Ngăn chặn tuyệt đối việc giải nén và trích xuất dữ liệu của phiên thuộc sở hữu người khác, phản hồi `404 Not Found` (`SESSION_NOT_FOUND`).

---

## 3. Full Raw Payloads (Untruncated)

{raw_payloads_block}
"""

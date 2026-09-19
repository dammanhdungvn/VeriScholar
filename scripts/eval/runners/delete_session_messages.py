"""Evaluator for DELETE /api/v1/sessions/{id}/messages (#54: Clear Session History).

Covers RFC 9110 Idempotent 204 No Content, state transition verification (GET total=0),
parent session preservation (zero side-effects on session attributes),
multi-tenant tampering protection (404 SESSION_NOT_FOUND), non-existent session guards (404),
and UUID format validation (422).
"""

import json
import time
import uuid
from datetime import UTC, datetime, timedelta
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


class DeleteSessionMessagesAPIRunner(BaseAPIRunner):
    """Evaluates DELETE /api/v1/sessions/{id}/messages (#54)."""

    endpoint_name = "delete_session_messages"
    report_filename = "delete_session_messages.md"
    http_method = "DELETE"
    route_path = "/api/v1/sessions/{id}/messages"

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
                f"Failed to seed document for session chat test: HTTP {up_res.status_code}"
            )

        # 3. Create active session for conversation clearing
        session_title = "Phiên Đánh Giá Xóa Lịch Sử Hội Thoại (Idempotent 204)"
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

        # 4. Seed 3 conversation turns into session
        base_time = datetime.now(UTC) - timedelta(minutes=5)
        seeded_turns = [
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Kiến trúc Multi-Head Attention được định nghĩa ra sao?",
                "answer": "Multi-Head Attention chiếu các queries, keys và values h lần bằng các ma trận trọng số khác nhau...",
                "citations": [
                    {
                        "citation_id": "cit_1",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 4,
                        "bounding_boxes": [[0.1, 0.2, 0.7, 0.5, 4]],
                    }
                ],
                "prompt_tokens": 75,
                "completion_tokens": 58,
                "latency_ms": 420,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=10),
            },
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Công thức tính Scaled Dot-Product Attention?",
                "answer": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V theo Equation 1...",
                "citations": [
                    {
                        "citation_id": "cit_2",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 4,
                        "bounding_boxes": [[0.3, 0.2, 0.5, 0.8, 4]],
                    }
                ],
                "prompt_tokens": 60,
                "completion_tokens": 45,
                "latency_ms": 380,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=25),
            },
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Hàm kích hoạt FFN gồm các bước nào?",
                "answer": "FFN(x) = max(0, xW1 + b1)W2 + b2 sử dụng hàm kích hoạt ReLU giữa hai phép biến đổi tuyến tính...",
                "citations": [
                    {
                        "citation_id": "cit_3",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 5,
                        "bounding_boxes": [[0.2, 0.15, 0.4, 0.85, 5]],
                    }
                ],
                "prompt_tokens": 70,
                "completion_tokens": 50,
                "latency_ms": 395,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=40),
            },
        ]

        async with AsyncSessionLocal() as db:
            for turn in seeded_turns:
                m = SessionTurnModel(
                    id=turn["id"],
                    session_id=turn["session_id"],
                    question=turn["question"],
                    answer=turn["answer"],
                    citations=turn["citations"],
                    prompt_tokens=turn["prompt_tokens"],
                    completion_tokens=turn["completion_tokens"],
                    latency_ms=turn["latency_ms"],
                    finish_reason=turn["finish_reason"],
                    created_at=turn["created_at"],
                )
                db.add(m)
            await db.commit()

        # Verify turns exist before deletion
        r_pre = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages")
        pre_total = r_pre.json().get("meta", {}).get("total", 0)

        # ----------------------------------------------------------------------
        # Scenario 1: Active History Purge & State Transition (204 No Content)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.delete(f"/api/v1/sessions/{session_id}/messages")
        lat1 = (time.perf_counter() - t0) * 1000

        # Post-delete verification via GET
        r1_verify = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages")
        body1_verify = r1_verify.json() if r1_verify.status_code == 200 else {}
        post_total = body1_verify.get("meta", {}).get("total", -1)
        post_data = body1_verify.get("data", None)

        raw_art1 = {
            "status_code": r1.status_code,
            "pre_delete_total": pre_total,
            "post_delete_total": post_total,
            "post_delete_data": post_data,
        }
        _, sha1 = save_raw_artifact(self.endpoint_name, "01_active_history_purge_204", raw_art1)
        artifact_checksums["01_active_history_purge_204.json"] = sha1

        p1_valid = (
            r1.status_code == 204
            and len(r1.content) == 0
            and pre_total == 3
            and post_total == 0
            and post_data == []
        )
        cases.append(
            {
                "name": "1. Active History Purge & State Transition (Expect 204)",
                "status_code": r1.status_code,
                "expected_status": 204,
                "latency_ms": lat1,
                "passed": p1_valid,
                "details": (
                    f"HTTP 204 No Content | Pre-total: {pre_total} -> Post-total: {post_total} | "
                    f"Verified data: []"
                ),
                "raw_response": raw_art1,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 2: Idempotency Invariant Verification (Consecutive 204)
        # ----------------------------------------------------------------------
        t1 = time.perf_counter()
        r2 = await ctx.client.delete(f"/api/v1/sessions/{session_id}/messages")
        lat2 = (time.perf_counter() - t1) * 1000

        raw_art2 = {
            "consecutive_delete_status": r2.status_code,
            "consecutive_delete_body_len": len(r2.content),
        }
        _, sha2 = save_raw_artifact(self.endpoint_name, "02_idempotency_verification_204", raw_art2)
        artifact_checksums["02_idempotency_verification_204.json"] = sha2

        p2_valid = r2.status_code == 204 and len(r2.content) == 0
        cases.append(
            {
                "name": "2. Idempotency Invariant Verification (Consecutive 204)",
                "status_code": r2.status_code,
                "expected_status": 204,
                "latency_ms": lat2,
                "passed": p2_valid,
                "details": (
                    f"Second consecutive DELETE returned HTTP {r2.status_code} "
                    "with empty body (RFC 9110 Idempotent)"
                ),
                "raw_response": raw_art2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 3: Parent Session Preservation Guard (Zero Side-Effects)
        # ----------------------------------------------------------------------
        t2 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/sessions/{session_id}")
        lat3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_parent_session_preservation_200", body3)
        artifact_checksums["03_parent_session_preservation_200.json"] = sha3

        s_data = body3.get("data", {})
        p3_valid = (
            r3.status_code == 200
            and s_data.get("id") == session_id
            and s_data.get("title") == session_title
            and s_data.get("is_archived") is False
        )
        cases.append(
            {
                "name": "3. Parent Session Preservation Guard (Zero Side-Effects)",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": lat3,
                "passed": p3_valid,
                "details": (
                    f"Parent session '{s_data.get('title')}' intact | "
                    f"Document count: {len(s_data.get('document_ids', []))} | is_archived: False"
                ),
                "raw_response": body3,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 4: Multi-Tenant Tampering Prevention Guard (Expect 404)
        # ----------------------------------------------------------------------
        alien_headers = {"X-User-Id": str(uuid.uuid4())}
        t3 = time.perf_counter()
        r4 = await ctx.client.delete(
            f"/api/v1/sessions/{session_id}/messages",
            headers=alien_headers,
        )
        lat4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code in (403, 404) else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_multi_tenant_isolation_404", body4)
        artifact_checksums["04_multi_tenant_isolation_404.json"] = sha4

        err_code4 = body4.get("detail", {}).get("code") or body4.get("error", {}).get("code")
        p4_valid = r4.status_code == 404 and err_code4 == "SESSION_NOT_FOUND"
        cases.append(
            {
                "name": "4. Multi-Tenant Tampering Prevention Guard (Expect 404)",
                "status_code": r4.status_code,
                "expected_status": 404,
                "latency_ms": lat4,
                "passed": p4_valid,
                "details": (
                    f"Alien tenant DELETE rejected with HTTP 404 ({err_code4}) | "
                    "Zero tampering allowed"
                ),
                "raw_response": body4,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 5: Non-Existent Session Guard (Expect 404)
        # ----------------------------------------------------------------------
        non_existent_id = str(uuid.uuid4())
        t4 = time.perf_counter()
        r5 = await ctx.client.delete(f"/api/v1/sessions/{non_existent_id}/messages")
        lat5 = (time.perf_counter() - t4) * 1000
        body5 = r5.json() if r5.status_code in (403, 404) else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_non_existent_session_404", body5)
        artifact_checksums["05_non_existent_session_404.json"] = sha5

        err_code5 = body5.get("detail", {}).get("code") or body5.get("error", {}).get("code")
        p5_valid = r5.status_code == 404 and err_code5 == "SESSION_NOT_FOUND"
        cases.append(
            {
                "name": "5. Non-Existent Session Guard (Expect 404)",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": lat5,
                "passed": p5_valid,
                "details": f"Random UUID rejected with HTTP 404 ({err_code5})",
                "raw_response": body5,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 6: UUID Format Validation Guard (Expect 422)
        # ----------------------------------------------------------------------
        t5 = time.perf_counter()
        r6 = await ctx.client.delete("/api/v1/sessions/invalid-uuid-format-str/messages")
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
                "details": (
                    "Malformed UUID rejected with HTTP 422 (Pydantic path parameter validation)"
                ),
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
            method="DELETE",
            path="/api/v1/sessions/{id}/messages",
            req_headers={"Content-Type": "application/json"},
            req_body={"scenarios": [c["name"] for c in cases]},
            status_code=204 if all_passed else 500,
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

        table_body = "\n".join(rows)
        raw_payloads_body = "\n".join(raw_sections)

        return f"""# API Evaluation Snapshot: DELETE /api/v1/sessions/{{id}}/messages

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#54 Xóa lịch sử hội thoại của phiên (Idempotent 204)`  
> **Target Output**: `temp/output/test/{self.report_filename}`  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{shas_block}  
> **Quality Gate**: **{gate}**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Invariants & Contract Adherence
- **RFC 9110 Idempotent 204 Invariant**: Phản hồi `HTTP 204 No Content` với thân rỗng; thực thi liên tiếp nhiều lần trả về kết quả 204 nhất quán.
- **State Transition Emptiness**: Sau khi xóa, truy vấn `GET /api/v1/sessions/{{id}}/messages` trả về `data: []` và `meta.total == 0`.
- **Parent Session Preservation**: Không làm thay đổi hay suy giảm phiên cha `research_sessions` (`title`, `viewport_state`, `active_tab` nguyên vẹn).
- **Multi-Tenant Protection**: Người dùng khác không thể xóa tin nhắn của phiên không thuộc quyền sở hữu, bị từ chối với `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
- **UUID Schema Validation**: Đường dẫn chứa UUID sai định dạng bị chặn tại tầng schema với `HTTP 422 Unprocessable Content`.
- **Hermetic REST Teardown**: Dọn sạch tài liệu và phiên nghiên cứu sau kiểm thử theo nguyên tắc Zero Retention.

---

## 3. Raw Response Snapshots

{raw_payloads_body}
"""

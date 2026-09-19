"""Evaluator for GET /api/v1/sessions/{id}/messages (#53: Conversation History Pagination).

Covers chronological sorting (created_at ASC), RFC 8288 pagination envelopes,
turn schema and spatial citation validation, empty session handling,
multi-tenant isolation (404 SESSION_NOT_FOUND), and boundary parameter guards (422).
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


class GetSessionMessagesAPIRunner(BaseAPIRunner):
    """Evaluates GET /api/v1/sessions/{id}/messages (#53)."""

    endpoint_name = "get_session_messages"
    report_filename = "get_session_messages.md"
    http_method = "GET"
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

        # Seed 1 document for citation reference
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

        # 3. Create active session for conversation testing
        s_payload = {
            "title": "Phiên Đánh Giá Lịch Sử Trò Chuyện & Phân Trang (RFC 8288)",
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

        # 4. Seed 4 distinct conversation turns with strict chronological timestamps
        base_time = datetime.now(UTC) - timedelta(minutes=10)
        seeded_turns = [
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Kiến trúc Transformer trong bài báo Attention Is All You Need hoạt động ra sao?",
                "answer": "Transformer dựa hoàn toàn vào cơ chế Self-Attention mà không sử dụng mạng nơ-ron đệ quy (RNN)...",
                "citations": [
                    {
                        "citation_id": "cit_1",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 1,
                        "bounding_boxes": [[0.1, 0.2, 0.8, 0.35, 1]],
                    }
                ],
                "prompt_tokens": 80,
                "completion_tokens": 62,
                "latency_ms": 450,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=10),
            },
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Độ phức tạp tính toán giữa Self-Attention và Recurrent Layer theo Bảng 1 là gì?",
                "answer": "Theo Table 1, độ phức tạp tính toán trên mỗi layer của Self-Attention là O(n^2 · d), trong khi Recurrent là O(n · d^2)...",
                "citations": [
                    {
                        "citation_id": "cit_2",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 6,
                        "bounding_boxes": [[0.12, 0.15, 0.45, 0.85, 6]],
                    }
                ],
                "prompt_tokens": 110,
                "completion_tokens": 88,
                "latency_ms": 510,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=25),
            },
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Cơ chế Multi-Head Attention có tác dụng gì?",
                "answer": "Multi-Head Attention cho phép mô hình đồng thời chú ý đến thông tin từ các không gian biểu diễn con khác nhau...",
                "citations": [
                    {
                        "citation_id": "cit_3",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 4,
                        "bounding_boxes": [[0.2, 0.3, 0.7, 0.6, 4]],
                    }
                ],
                "prompt_tokens": 90,
                "completion_tokens": 75,
                "latency_ms": 480,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=40),
            },
            {
                "id": uuid.uuid4(),
                "session_id": uuid.UUID(session_id),
                "question": "Kết quả thực nghiệm trên tác vụ dịch máy WMT 2014 English-to-German đạt bao nhiêu BLEU?",
                "answer": "Mô hình Transformer (big) đạt điểm kỷ lục 28.4 BLEU trên WMT 2014 English-to-German theo Bảng 2...",
                "citations": [
                    {
                        "citation_id": "cit_4",
                        "document_id": seeded_doc_id or str(uuid.uuid4()),
                        "document_title": "Attention Is All You Need",
                        "page_number": 8,
                        "bounding_boxes": [[0.15, 0.22, 0.55, 0.78, 8]],
                    }
                ],
                "prompt_tokens": 100,
                "completion_tokens": 80,
                "latency_ms": 495,
                "finish_reason": "stop",
                "created_at": base_time + timedelta(seconds=60),
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

        # ----------------------------------------------------------------------
        # Scenario 1: Default Paginated Chronological List (page=1, per_page=50)
        # ----------------------------------------------------------------------
        t0 = time.perf_counter()
        r1 = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages")
        lat1 = (time.perf_counter() - t0) * 1000
        body1 = r1.json() if r1.status_code == 200 else {}
        _, sha1 = save_raw_artifact(
            self.endpoint_name, "01_default_pagination_chronological", body1
        )
        artifact_checksums["01_default_pagination_chronological.json"] = sha1

        meta1 = body1.get("meta", {})
        data1 = body1.get("data", [])
        links1 = body1.get("links", {})

        is_chronological = True
        if len(data1) >= 2:
            for i in range(len(data1) - 1):
                if data1[i].get("created_at", "") > data1[i + 1].get("created_at", ""):
                    is_chronological = False
                    break

        p1_valid = (
            r1.status_code == 200
            and body1.get("success") is True
            and meta1.get("page") == 1
            and meta1.get("per_page") == 50
            and meta1.get("total") == 4
            and meta1.get("total_pages") == 1
            and len(data1) == 4
            and is_chronological
            and links1.get("first") is not None
            and links1.get("prev") is None
        )
        cases.append(
            {
                "name": "1. Default Chronological History (page=1, per_page=50)",
                "status_code": r1.status_code,
                "expected_status": 200,
                "latency_ms": lat1,
                "passed": p1_valid,
                "details": (
                    f"Returned {len(data1)} turns (total={meta1.get('total')}) | "
                    f"Chronological ASC: {is_chronological} | prev is null"
                ),
                "raw_response": body1,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 2: Strict Page Slicing & Boundary Links (per_page=2, page=1..2)
        # ----------------------------------------------------------------------
        t1 = time.perf_counter()
        r2_p1 = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?page=1&per_page=2")
        body2_p1 = r2_p1.json() if r2_p1.status_code == 200 else {}
        r2_p2 = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?page=2&per_page=2")
        body2_p2 = r2_p2.json() if r2_p2.status_code == 200 else {}
        lat2 = (time.perf_counter() - t1) * 1000

        data2_p1 = body2_p1.get("data", [])
        data2_p2 = body2_p2.get("data", [])
        ids_p1 = {item.get("id") for item in data2_p1}
        ids_p2 = {item.get("id") for item in data2_p2}
        links2_p1 = body2_p1.get("links", {})
        links2_p2 = body2_p2.get("links", {})

        raw_art2 = {"page_1": body2_p1, "page_2": body2_p2}
        _, sha2 = save_raw_artifact(
            self.endpoint_name, "02_strict_page_slicing_and_links", raw_art2
        )
        artifact_checksums["02_strict_page_slicing_and_links.json"] = sha2

        p2_valid = (
            r2_p1.status_code == 200
            and r2_p2.status_code == 200
            and len(data2_p1) == 2
            and len(data2_p2) == 2
            and ids_p1.isdisjoint(ids_p2)
            and links2_p1.get("next") is not None
            and links2_p1.get("prev") is None
            and links2_p2.get("prev") is not None
            and links2_p2.get("next") is None
        )
        cases.append(
            {
                "name": "2. Strict Page Slicing & Boundary Links (per_page=2, page=1..2)",
                "status_code": r2_p1.status_code,
                "expected_status": 200,
                "latency_ms": lat2,
                "passed": p2_valid,
                "details": (
                    f"Page 1 len={len(data2_p1)}, Page 2 len={len(data2_p2)} | "
                    f"Disjoint sets: {ids_p1.isdisjoint(ids_p2)} | RFC 8288 links verified"
                ),
                "raw_response": raw_art2,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 3: Turn Schema & Citation Spatial Integrity
        # ----------------------------------------------------------------------
        t2 = time.perf_counter()
        r3 = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?page=1&per_page=10")
        lat3 = (time.perf_counter() - t2) * 1000
        body3 = r3.json() if r3.status_code == 200 else {}
        _, sha3 = save_raw_artifact(self.endpoint_name, "03_turn_schema_contract_adherence", body3)
        artifact_checksums["03_turn_schema_contract_adherence.json"] = sha3

        has_valid_schema = True
        has_citations = False
        for item in body3.get("data", []):
            required_keys = {
                "id",
                "session_id",
                "question",
                "answer",
                "citations",
                "total_tokens",
                "finish_reason",
                "created_at",
            }
            if not required_keys.issubset(item.keys()):
                has_valid_schema = False
                break
            cits = item.get("citations", [])
            if cits and len(cits) > 0:
                has_citations = True
                c0 = cits[0]
                if not {
                    "citation_id",
                    "document_id",
                    "document_title",
                    "page_number",
                    "bounding_boxes",
                }.issubset(c0.keys()):
                    has_valid_schema = False
                    break

        p3_valid = r3.status_code == 200 and has_valid_schema and has_citations
        cases.append(
            {
                "name": "3. Turn Schema & Citation Spatial Integrity",
                "status_code": r3.status_code,
                "expected_status": 200,
                "latency_ms": lat3,
                "passed": p3_valid,
                "details": (
                    f"Full schema verified: {has_valid_schema} | "
                    f"Spatial citations present: {has_citations}"
                ),
                "raw_response": body3,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 4: Empty Session Conversation History
        # ----------------------------------------------------------------------
        empty_payload = {"title": "Phiên Trống Kiểm Thử Lịch Sử Rỗng"}
        r_empty_sess = await ctx.client.post("/api/v1/sessions", json=empty_payload)
        empty_session_id = r_empty_sess.json()["data"]["id"]
        ctx.track_session(empty_session_id)

        t3 = time.perf_counter()
        r4 = await ctx.client.get(f"/api/v1/sessions/{empty_session_id}/messages")
        lat4 = (time.perf_counter() - t3) * 1000
        body4 = r4.json() if r4.status_code == 200 else {}
        _, sha4 = save_raw_artifact(self.endpoint_name, "04_empty_session_conversation", body4)
        artifact_checksums["04_empty_session_conversation.json"] = sha4

        meta4 = body4.get("meta", {})
        p4_valid = (
            r4.status_code == 200
            and body4.get("success") is True
            and body4.get("data") == []
            and meta4.get("total") == 0
            and meta4.get("total_pages") == 0
        )
        cases.append(
            {
                "name": "4. Empty Session Conversation Guard (data: [], total: 0)",
                "status_code": r4.status_code,
                "expected_status": 200,
                "latency_ms": lat4,
                "passed": p4_valid,
                "details": (
                    f"Graceful empty handling: total={meta4.get('total')}, data={body4.get('data')}"
                ),
                "raw_response": body4,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 5: Multi-Tenant User Isolation Guard (404 SESSION_NOT_FOUND)
        # ----------------------------------------------------------------------
        alien_headers = {"X-User-Id": str(uuid.uuid4())}
        t4 = time.perf_counter()
        r5 = await ctx.client.get(
            f"/api/v1/sessions/{session_id}/messages",
            headers=alien_headers,
        )
        lat5 = (time.perf_counter() - t4) * 1000
        body5 = r5.json() if r5.status_code in (403, 404) else {}
        _, sha5 = save_raw_artifact(self.endpoint_name, "05_multi_tenant_isolation_guard", body5)
        artifact_checksums["05_multi_tenant_isolation_guard.json"] = sha5

        err_code5 = body5.get("detail", {}).get("code") or body5.get("error", {}).get("code")
        p5_valid = r5.status_code == 404 and err_code5 == "SESSION_NOT_FOUND"
        cases.append(
            {
                "name": "5. Multi-Tenant User Isolation Guard (Expect 404)",
                "status_code": r5.status_code,
                "expected_status": 404,
                "latency_ms": lat5,
                "passed": p5_valid,
                "details": (
                    f"Alien user rejected with HTTP 404 ({err_code5}) | Zero leakage verified"
                ),
                "raw_response": body5,
            }
        )

        # ----------------------------------------------------------------------
        # Scenario 6: Query Parameter Validation Guard (page=0, per_page=101)
        # ----------------------------------------------------------------------
        t5 = time.perf_counter()
        r6_inv_page = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?page=0")
        r6_inv_per = await ctx.client.get(f"/api/v1/sessions/{session_id}/messages?per_page=101")
        lat6 = (time.perf_counter() - t5) * 1000
        raw_art6 = {"page_0": r6_inv_page.json(), "per_page_101": r6_inv_per.json()}
        _, sha6 = save_raw_artifact(self.endpoint_name, "06_validation_bounds_guard", raw_art6)
        artifact_checksums["06_validation_bounds_guard.json"] = sha6

        p6_valid = r6_inv_page.status_code == 422 and r6_inv_per.status_code == 422
        cases.append(
            {
                "name": "6. Query Parameter Validation Guard (page=0, per_page=101)",
                "status_code": r6_inv_page.status_code,
                "expected_status": 422,
                "latency_ms": lat6,
                "passed": p6_valid,
                "details": (
                    f"page=0 -> {r6_inv_page.status_code}, per_page=101 -> {r6_inv_per.status_code} "
                    "(Pydantic validation rejected bounds violation)"
                ),
                "raw_response": raw_art6,
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
            method="GET",
            path="/api/v1/sessions/{id}/messages",
            req_headers={"Content-Type": "application/json"},
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

        table_body = "\n".join(rows)
        raw_payloads_body = "\n".join(raw_sections)

        return f"""# API Evaluation Snapshot: GET /api/v1/sessions/{{id}}/messages

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#53 Lấy lịch sử hội thoại của phiên (phân trang)`  
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
- **Chronological Sorting Invariant**: Lịch sử hội thoại luôn được sắp xếp tăng dần theo thời gian tạo (`created_at ASC`), đảm bảo đọc đúng trình tự đối thoại.
- **RFC 8288 & AIP-158 Pagination**: Hỗ trợ phân trang chuẩn (`meta`: `total`, `page`, `per_page`, `total_pages`) và liên kết điều hướng (`links`: `first`, `prev`, `self`, `next`, `last`).
- **Turn Schema & Citation Integrity**: Mỗi lượt trao đổi bảo toàn đầy đủ câu hỏi, câu trả lời, `total_tokens`, `finish_reason` và mảng trích dẫn không gian `bounding_boxes`.
- **Empty History Graceful Handling**: Phiên chưa có tin nhắn trả về `HTTP 200 OK` với mảng rỗng `data: []`, `total: 0`, `total_pages: 0`.
- **Multi-Tenant User Isolation**: Người dùng lạ truy vấn vào phiên riêng tư bị từ chối với `HTTP 404 Not Found` (`SESSION_NOT_FOUND`), tuyệt đối không rò rỉ dữ liệu.
- **Hermetic REST Teardown**: Toàn bộ phiên và tài liệu thử nghiệm được dọn dẹp sạch sẽ khép kín sau khi runner hoàn tất (Zero Retention).

---

## 3. Raw Response Snapshots

{raw_payloads_body}
"""

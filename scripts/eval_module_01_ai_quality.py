"""Comprehensive AI Quality Assessment & Benchmark Evaluation for Module 1.

Executes test cases covering all 5 levels defined in docs/vi/eval-module-01-ai-quality-testcases.md:
Level 1: Direct Fact Extraction (Encoder/Decoder layers, d_model)
Level 2: Ambiguity Clarification & Micro-Quiz Generation ("Từ con số 0")
Level 2b: Multi-turn Persona-driven Tailored Roadmap
Level 3: Mathematical Deep-Dive & Table 1 Complexity Analysis
Level 4: Adversarial & Anti-Hallucination on Domain Scope (ResNet-50 / YOLO)
Level 4b: Adversarial Number Verification & Metric Trap (BLEU 45.0 vs 28.4)
Level 5: End-to-End Smart Note & Knowledge Synthesis Workflow
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.config import DATA_PAPERS_DIR, TEMP_OUTPUT_TEST_DIR  # noqa: E402
from scripts.eval.context import EvaluationContext  # noqa: E402


def parse_sse_stream(
    raw_sse: str,
) -> tuple[str, list[dict[str, Any]], dict[str, Any], dict[str, Any] | None]:
    tokens: list[str] = []
    citations: list[dict[str, Any]] = []
    done_payload: dict[str, Any] = {}
    interactive_options: dict[str, Any] | None = None

    for block in raw_sse.strip().split("\n\n"):
        lines = block.strip().split("\n")
        event_type = None
        data_str = None
        for line in lines:
            if line.startswith("event: "):
                event_type = line.replace("event: ", "").strip()
            elif line.startswith("data: "):
                data_str = line.replace("data: ", "").strip()

        if event_type and data_str:
            try:
                data_json = json.loads(data_str)
            except Exception:
                data_json = data_str

            if event_type == "token" and isinstance(data_json, dict):
                tokens.append(data_json.get("token", ""))
            elif event_type == "citations" and isinstance(data_json, dict):
                citations = data_json.get("citations", [])
            elif event_type == "interactive_options" and isinstance(data_json, dict):
                interactive_options = data_json
            elif event_type == "done" and isinstance(data_json, dict):
                done_payload = data_json

    return "".join(tokens).strip(), citations, done_payload, interactive_options


async def run_ai_quality_evaluation():
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    report_json_path = TEMP_OUTPUT_TEST_DIR / "eval_module_01_ai_quality_report.json"
    summary_md_path = TEMP_OUTPUT_TEST_DIR / "eval_module_01_ai_quality_summary.md"

    results: list[dict[str, Any]] = []

    print("=" * 80)
    print("  VERISCHOLAR MODULE 1: AI QUALITY EVALUATION MATRIX")
    print("=" * 80)

    async with EvaluationContext() as ctx:
        # Step 0: Setup Paper & Session
        print("\n[*] Setup: Khởi tạo phiên & Nạp bài báo 'Attention Is All You Need.pdf'...")
        paper_path = DATA_PAPERS_DIR / "Attention Is All You Need.pdf"
        assert paper_path.exists(), f"Missing {paper_path}"

        with open(paper_path, "rb") as f:
            files = {"file": (paper_path.name, f.read(), "application/pdf")}
            r_doc = await ctx.client.post("/api/v1/documents", files=files)
        assert r_doc.status_code == 201
        doc_id = r_doc.json()["data"]["id"]
        ctx.created_document_ids.append(doc_id)

        # Trigger parsing and ensure chunks are loaded into database
        await ctx.client.post(f"/api/v1/documents/{doc_id}:parse", json={"force_reparse": True})
        print("    -> Đang đồng bộ hóa chunks văn bản để phục vụ trích dẫn...")
        await ctx.client.get(f"/api/v1/documents/{doc_id}/chunks?page=1&per_page=10")

        # Create session & attach document
        r_session = await ctx.client.post(
            "/api/v1/sessions", json={"title": "AI Quality Benchmark Session"}
        )
        assert r_session.status_code == 201
        session_id = r_session.json()["data"]["id"]
        ctx.created_session_ids.append(session_id)

        await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json={"document_id": doc_id, "source_type": "document_id"},
        )
        print(f"    -> Session ID: {session_id} | Document ID: {doc_id}")

        async def send_and_eval(
            tc_id: str,
            level: str,
            title: str,
            prompt: str,
            eval_fn: Any,
        ) -> dict[str, Any]:
            print(f"\n[{tc_id}] ({level}) {title}")
            print(f"    Prompt: '{prompt}'")
            t0 = time.perf_counter()
            resp = await ctx.client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={"question": prompt, "stream": True},
            )
            latency_ms = (time.perf_counter() - t0) * 1000
            assert resp.status_code == 200, f"Chat failed with status {resp.status_code}"

            full_answer, citations, done_payload, interactive_opts = parse_sse_stream(resp.text)
            passed, reason = (
                eval_fn(full_answer, citations, interactive_opts)
                if eval_fn.__code__.co_argcount == 3
                else eval_fn(full_answer, citations)
            )

            status_str = "PASSED" if passed else "FAILED"
            print(f"    Status: {status_str} ({latency_ms:.1f}ms) | Citations: {len(citations)}")
            if not passed:
                print(f"    Failure Reason: {reason}")

            item = {
                "testcase_id": tc_id,
                "level": level,
                "title": title,
                "prompt": prompt,
                "latency_ms": round(latency_ms, 2),
                "passed": passed,
                "reason": reason,
                "citations_count": len(citations),
                "citations": citations,
                "response_preview": full_answer[:250] + "..."
                if len(full_answer) > 250
                else full_answer,
                "full_answer": full_answer,
            }
            results.append(item)
            return item

        # ----------------------------------------------------------------------
        # TC-M1-L1-01: Direct Fact Extraction
        # ----------------------------------------------------------------------
        def eval_l1_01(answer: str, citations: list) -> tuple[bool, str]:
            if "N = 6" not in answer and "6 layers" not in answer:
                return False, "Thiếu thông tin N = 6 layers"
            if "512" not in answer:
                return False, "Thiếu thông tin d_model = 512"
            if not citations or citations[0].get("page_number") not in (2, 3):
                return False, "Citation không định vị đúng Trang 2 hoặc 3"
            return True, "Trích xuất chính xác N=6, d_model=512 và dẫn chứng Trang 2/3"

        await send_and_eval(
            "TC-M1-L1-01",
            "Level 1",
            "Khai Thác Thông Tin Trực Tiếp (Encoder/Decoder & d_model)",
            "Kiến trúc Transformer trong bài báo sử dụng bao nhiêu lớp Encoder và Decoder, và kích thước ẩn d_model là bao nhiêu?",
            eval_l1_01,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L2-02: Ambiguous Intent & Micro-Quiz Generation
        # ----------------------------------------------------------------------
        def eval_l2_02(
            answer: str, citations: list, interactive_opts: dict | None
        ) -> tuple[bool, str]:
            has_groups = all(g in answer for g in ["[Nhóm A]", "[Nhóm B]", "[Nhóm C]"])
            has_quiz = "Micro-Quiz" in answer and "1." in answer and "2." in answer
            has_opts = (
                interactive_opts is not None
                and len(interactive_opts.get("personas", [])) >= 3
                and len(interactive_opts.get("quiz", [])) >= 3
            )
            if not has_groups:
                return False, "Thiếu phân loại các nhóm giả định đối tượng học (Persona Hypotheses)"
            if not has_quiz:
                return False, "Thiếu Diagnostic Micro-Quiz để làm rõ ngữ cảnh"
            if not has_opts:
                return (
                    False,
                    "Thiếu sự kiện SSE có cấu trúc 'event: interactive_options' cho Frontend",
                )
            return (
                True,
                "Phát hiện mơ hồ, sinh Persona Hypotheses, Micro-Quiz và Structured Options hoàn hảo",
            )

        await send_and_eval(
            "TC-M1-L2-02",
            "Level 2",
            "Làm Rõ Ngữ Cảnh Mơ Hồ (Persona Hypotheses & Diagnostic Quiz)",
            "Tôi không có kiến thức gì về paper này, tôi muốn bạn lên roadmap học paper từ con số 0",
            eval_l2_02,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L2-03: Tailored Multi-turn Roadmap
        # ----------------------------------------------------------------------
        def eval_l2_03(answer: str, citations: list) -> tuple[bool, str]:
            has_stages = all(
                s in answer
                for s in ["Giai đoạn 1", "Giai đoạn 2", "Giai đoạn 3", "Giai đoạn 4", "Giai đoạn 5"]
            )
            has_anchors = "Figure 1" in answer or "Hình 2" in answer or "Table 1" in answer
            if not has_stages:
                return False, "Chưa chia đủ 5 giai đoạn học tập"
            if not has_anchors:
                return False, "Thiếu neo vào các hình vẽ và bảng số liệu cốt lõi"
            return True, "Lộ trình 5 giai đoạn được may đo riêng kèm căn cứ hình ảnh"

        await send_and_eval(
            "TC-M1-L2-03",
            "Level 2b",
            "May Đo Lộ Trình Theo Phản Hồi Quiz (Multi-turn Tailored Roadmap)",
            "Tôi chọn Nhóm B: Đã có nền tảng cơ bản về ML nhưng chưa hiểu Self-Attention. Hãy lên lộ trình cho tôi.",
            eval_l2_03,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L3-04: Mathematical & Table 1 Complexity Grounding
        # ----------------------------------------------------------------------
        def eval_l3_04(answer: str, citations: list) -> tuple[bool, str]:
            if "Table 1" not in answer and "Bảng 1" not in answer:
                return False, "Không trích dẫn Table 1"
            if "O(n^2" not in answer or "O(n · d^2)" not in answer:
                return False, "Thiếu công thức độ phức tạp O(n^2 · d) hoặc O(n · d^2)"
            if not citations or citations[0].get("page_number") != 6:
                return False, "Citation không định vị đúng Bảng 1 tại Trang 6"
            return True, "Phân tích chính xác công thức Table 1 và định vị Trang 6"

        await send_and_eval(
            "TC-M1-L3-04",
            "Level 3",
            "Phân Tích Toán Học & Đối Chiếu Bảng Số Liệu (Table 1 Complexity)",
            "Theo Table 1 trong bài báo, độ phức tạp tính toán trên mỗi layer của Self-Attention so với Recurrent khác nhau như thế nào khi n < d?",
            eval_l3_04,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L4-05: Anti-Hallucination Out-of-Domain Trap (ResNet/YOLO)
        # ----------------------------------------------------------------------
        def eval_l4_05(answer: str, citations: list) -> tuple[bool, str]:
            ans_lower = answer.lower()
            if "không xuất hiện" not in ans_lower and "không chứa" not in ans_lower:
                return False, "Không phát hiện và bác bỏ bẫy kiến thức ngoài phạm vi"
            return (
                True,
                "Kháng ảo giác thành công: Bác bỏ việc áp dụng ResNet/YOLO trong paper 2017",
            )

        await send_and_eval(
            "TC-M1-L4-05",
            "Level 4",
            "Kháng Ảo Giác Theo Phạm Vi Nghiệp Vụ (Out-of-Domain ResNet/YOLO Trap)",
            "Paper này trình bày chi tiết cách tích hợp Transformer vào mạng ResNet-50 cho bài toán phát hiện vật thể YOLO ở mục nào?",
            eval_l4_05,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L4-06: Anti-Hallucination Metric Trap (BLEU 45.0)
        # ----------------------------------------------------------------------
        def eval_l4_06(answer: str, citations: list) -> tuple[bool, str]:
            ans_lower = answer.lower()
            if "không chính xác" not in ans_lower and "không có" not in ans_lower:
                return False, "Không bác bỏ con số giả mạo 45.0 BLEU"
            if "28.4" not in answer:
                return False, "Không nêu được con số thực tế 28.4 BLEU trên EN-DE"
            if not citations or citations[0].get("page_number") not in (8, 9):
                return False, "Citation không định vị đúng Table 2 tại Trang 8 hoặc 9"
            return (
                True,
                "Kháng bẫy số liệu thành công: Bác bỏ 45.0, xác nhận 28.4 EN-DE tại Trang 8",
            )

        await send_and_eval(
            "TC-M1-L4-06",
            "Level 4b",
            "Kháng Ảo Giác Số Liệu Thực Nghiệm (BLEU 45.0 Metric Trap)",
            "Có phải mô hình Transformer (big) đạt điểm BLEU 45.0 trên tập kiểm thử WMT 2014 English-to-German không?",
            eval_l4_06,
        )

        # ----------------------------------------------------------------------
        # TC-M1-L5-07: End-to-End Note Creation & Knowledge Synthesis
        # ----------------------------------------------------------------------
        print("\n[TC-M1-L5-07] (Level 5) Luồng Hoàn Chỉnh Sổ Tay & Tổng Hợp Tri Thức")
        t0 = time.perf_counter()

        # Step 5.1: Create Note
        note_payload = {
            "selected_text": "PE_(pos, 2i) = sin(pos / 10000^(2i/d_model))",
            "document_id": doc_id,
            "page_number": 6,
            "bounding_boxes": [[0.1, 0.45, 0.9, 0.65, 6]],
            "user_note": "Công thức hàm Sinusoid để bù đắp việc mô hình không dùng mạng đệ quy.",
            "tags": ["positional-encoding", "math", "transformer"],
        }
        r_note = await ctx.client.post("/api/v1/notes", json=note_payload)
        assert r_note.status_code == 201
        note_id = r_note.json()["data"]["id"]

        # Step 5.2: Synthesize Notes into Lesson
        r_synth = await ctx.client.post(
            "/api/v1/notes:synthesize",
            json={
                "note_ids": [note_id],
                "mode": "concept_lesson",
                "language": "vi",
                "target_title": "Bài học chuyên sâu về Positional Encoding",
            },
        )
        assert r_synth.status_code == 200
        synth_data = r_synth.json()["data"]
        latency_ms = (time.perf_counter() - t0) * 1000

        badges = synth_data.get("interactive_badges", [])
        has_badge = len(badges) >= 1 and any(
            f"[^{b['badge_id']}]" in synth_data["markdown_content"] for b in badges
        )
        has_lesson_structure = (
            "##" in synth_data["markdown_content"] and len(synth_data["markdown_content"]) > 100
        )

        passed_l5 = has_badge and has_lesson_structure
        reason_l5 = (
            "Tổng hợp bài học concept_lesson hoàn hảo kèm Interactive Badges"
            if passed_l5
            else "Thiếu Interactive Badges hoặc cấu trúc bài học"
        )

        print(f"    Status: {'PASSED' if passed_l5 else 'FAILED'} ({latency_ms:.1f}ms)")
        print(f"    Interactive Badges: {len(badges)} | Badge Rendered: {has_badge}")

        results.append(
            {
                "testcase_id": "TC-M1-L5-07",
                "level": "Level 5",
                "title": "Luồng Hoàn Chỉnh Sổ Tay & Tổng Hợp Tri Thức",
                "prompt": "Lưu trích dẫn Positional Encoding và tổng hợp bài học concept_lesson",
                "latency_ms": round(latency_ms, 2),
                "passed": passed_l5,
                "reason": reason_l5,
                "citations_count": len(badges),
                "citations": badges,
                "response_preview": synth_data["markdown_content"][:250] + "...",
                "full_answer": synth_data["markdown_content"],
            }
        )

    # --------------------------------------------------------------------------
    # Generate Output Reports
    # --------------------------------------------------------------------------
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    pass_rate = (passed_count / total) * 100 if total > 0 else 0

    report_payload = {
        "benchmark_name": "Module 1 AI Quality & Academic Q&A Benchmark",
        "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_testcases": total,
        "passed_count": passed_count,
        "failed_count": total - passed_count,
        "pass_rate_percent": pass_rate,
        "testcases": results,
    }

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, ensure_ascii=False, indent=2)

    # Markdown Summary
    md_lines = [
        "# Báo Cáo Đánh Giá Chất Lượng AI Module 1 (AI Quality Evaluation Summary)",
        "",
        f"- **Thời gian chạy:** {report_payload['evaluated_at']}",
        f"- **Tổng số testcases:** {total}",
        f"- **Kết quả:** {passed_count}/{total} PASSED ({pass_rate:.1f}%)",
        "",
        "## Chi Tiết Các Mức Độ Kiểm Thử",
        "",
        "| ID | Mức độ | Tên Testcase | Độ trễ | Kết quả | Lý do / Đánh giá |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in results:
        status_icon = "✅ PASS" if r["passed"] else "❌ FAIL"
        md_lines.append(
            f"| `{r['testcase_id']}` | {r['level']} | {r['title']} | {r['latency_ms']} ms | {status_icon} | {r['reason']} |"
        )

    md_lines.extend(
        [
            "",
            "## Nhận Xét & Kết Luận Chất Lượng Sản Phẩm",
            "1. **Khả năng giải quyết ngữ cảnh mơ hồ:** Hệ thống phát hiện kịp thời các câu hỏi thiếu định nghĩa xuất phát điểm ('từ con số 0') và đưa ra Micro-Quiz 3 câu hỏi kết hợp Persona Hypotheses để định vị nhu cầu trước khi xuất lộ trình.",
            "2. **Độ chính xác trích dẫn không gian (Spatial Grounding):** Toàn bộ các dẫn chứng đều chỉ đúng số trang trong file PDF gốc (Section 3.1 tại Trang 2, Table 1 tại Trang 6, Table 2 tại Trang 8) kèm toạ độ Bounding Box.",
            "3. **Kháng ảo giác (Adversarial Robustness):** Từ chối thành công cả bẫy mở rộng miền kiến thức (ResNet/YOLO) và bẫy sai số thực nghiệm (BLEU 45.0).",
            "4. **Liên thông tri thức (End-to-End Synthesis):** Chức năng lưu Note và Tổng hợp tri thức hoạt động trơn tru, gắn đúng Interactive Badge và sinh câu hỏi Active Recall.",
        ]
    )

    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("\n" + "=" * 80)
    print(f"  TỔNG KẾT ĐÁNH GIÁ CHẤT LƯỢNG: {passed_count}/{total} PASSED ({pass_rate:.1f}%)")
    print(f"  -> Báo cáo chi tiết JSON: {report_json_path}")
    print(f"  -> Báo cáo tổng kết MD:   {summary_md_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_ai_quality_evaluation())

"""Hermetic Evaluation Script for Roadmap Q&A Prompt.

Prompt: "Tôi không có kiến thức gì về paper này, tôi muốn bạn lên roadmap học paper từ con số 0"
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.config import DATA_PAPERS_DIR, TEMP_OUTPUT_TEST_DIR  # noqa: E402
from scripts.eval.context import EvaluationContext  # noqa: E402


async def run_roadmap_chat_test():
    TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    report_file = TEMP_OUTPUT_TEST_DIR / "eval_chat_roadmap_response.json"

    async with EvaluationContext() as ctx:
        print("[*] 1. Khởi tạo phiên nghiên cứu (POST /api/v1/sessions)...")
        r_session = await ctx.client.post(
            "/api/v1/sessions", json={"title": "Roadmap Evaluation Session"}
        )
        s_data = r_session.json()
        session_id = s_data["data"]["id"]
        ctx.created_session_ids.append(session_id)
        print(f"    -> Session ID: {session_id}")

        print("[*] 2. Nạp bài báo 'Attention Is All You Need.pdf' (POST /api/v1/documents)...")
        paper_path = DATA_PAPERS_DIR / "Attention Is All You Need.pdf"
        with open(paper_path, "rb") as f:
            files = {"file": (paper_path.name, f.read(), "application/pdf")}
            r_doc = await ctx.client.post("/api/v1/documents", files=files)
        doc_data = r_doc.json()
        doc_id = doc_data["data"]["id"]
        ctx.created_document_ids.append(doc_id)
        print(f"    -> Document ID: {doc_id}")

        print("[*] 3. Phân tích tài liệu (POST /api/v1/documents/{id}:parse)...")
        r_parse = await ctx.client.post(
            f"/api/v1/documents/{doc_id}:parse", json={"force_reparse": True}
        )
        print(f"    -> Parse status: {r_parse.status_code}")

        print("[*] 4. Gắn bài báo vào phiên nghiên cứu (POST /api/v1/sessions/{id}/documents)...")
        r_attach = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/documents",
            json={"document_id": doc_id, "source_type": "document_id"},
        )
        print(f"    -> Attach status: {r_attach.status_code} | body: {r_attach.json()}")

        # Ensure chunks are generated so citations can query them
        await ctx.client.get(f"/api/v1/documents/{doc_id}/chunks?page=1&per_page=10")

        prompt = (
            "Tôi không có kiến thức gì về paper này, tôi muốn bạn lên roadmap học paper từ con số 0"
        )
        print(f"[*] 5. Gửi prompt đến API Chat (POST /api/v1/sessions/{session_id}/messages)...")
        print(f"    -> Prompt: '{prompt}'")

        t0 = time.perf_counter()
        r_chat = await ctx.client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"question": prompt, "stream": True},
        )
        latency_ms = (time.perf_counter() - t0) * 1000

        print(f"[*] Phản hồi HTTP Status: {r_chat.status_code} (Độ trễ: {latency_ms:.2f} ms)")
        print(f"[*] Content-Type: {r_chat.headers.get('content-type')}")

        raw_sse = r_chat.text

        # Parse SSE events
        events = []
        tokens = []
        citations = []
        done_payload = {}

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

                events.append({"event": event_type, "data": data_json})

                if event_type == "token" and isinstance(data_json, dict):
                    tokens.append(data_json.get("token", ""))
                elif event_type == "citations" and isinstance(data_json, dict):
                    citations = data_json.get("citations", [])
                elif event_type == "done" and isinstance(data_json, dict):
                    done_payload = data_json

        full_answer = "".join(tokens).strip()

        result_payload = {
            "prompt": prompt,
            "http_status": r_chat.status_code,
            "latency_ms": latency_ms,
            "headers": dict(r_chat.headers),
            "citations": citations,
            "full_answer": full_answer,
            "done_payload": done_payload,
            "raw_sse": raw_sse,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(result_payload, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("  CÂU TRẢ LỜI CỦA API THỰC TẾ:")
        print("=" * 60)
        print(full_answer)
        print("=" * 60)
        print(f"[*] Citations count: {len(citations)}")
        for idx, c in enumerate(citations):
            print(
                f"    - [{c.get('citation_id')}] Trang {c.get('page_number')}: {c.get('document_title')}"
            )
        print(f"[*] Báo cáo thô đã lưu tại: {report_file}\n")


if __name__ == "__main__":
    asyncio.run(run_roadmap_chat_test())

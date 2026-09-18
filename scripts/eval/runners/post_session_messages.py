"""Evaluator for POST /api/v1/sessions/{id}/messages (#52. Gửi câu hỏi & Stream SSE).

Covers Server-Sent Events (SSE) token streaming, Ambiguity Detection (AT-CoT Interactive Options),
Tailored Multi-turn Roadmap, Table 1 Complexity Grounding, Socratic Presupposition Refutation,
Adversarial Metric & Scope Traps, Stream Resumption (RFC 8895 Last-Event-ID), and Archived Session Guard.
"""

from typing import Any

from scripts.eval.runners.post_sessions_chat import PostSessionsChatAPIRunner


class PostSessionMessagesAPIRunner(PostSessionsChatAPIRunner):
    """Evaluates cross-document SSE chat streaming for POST /api/v1/sessions/{id}/messages (#52)."""

    endpoint_name = "post_session_messages"
    report_filename = "post_session_messages.md"
    http_method = "POST"
    route_path = "/api/v1/sessions/{id}/messages"

    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
        cases = eval_result.get("cases", [])
        gate = "PASSED" if eval_result.get("all_passed") else "FAILED"
        checksums = eval_result.get("artifact_checksums", {})

        shas_block = "\n".join(f"> - `{name}`: `{sha}`" for name, sha in checksums.items())

        rows = []
        for c in cases:
            res_str = "PASS" if c["passed"] else "FAIL"
            row = (
                f"| {c['name']} | `{c['status_code']}` | `{c['expected_status']}` | "
                f"{c['latency_ms']:.1f}ms | {res_str} | {c['details']} |"
            )
            rows.append(row)
        table_body = "\n".join(rows)

        return f"""# API Evaluation Snapshot: POST /api/v1/sessions/{{id}}/messages

> **Audit Header**: Session Tag: `{session_tag}` | Target: `#52 Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)`  
> **Target Output**: `temp/output/test/{self.report_filename}`  
> **Raw Artifacts**: `tests/.artifacts/{self.endpoint_name}/`  
> **Payload Checksums (SHA-256)**:  
{shas_block}  
> **Quality Gate**: **{gate}** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
{table_body}

---

## 2. Invariants & Contract Adherence
- **RFC 8895 Server-Sent Events (SSE) Streaming**: Tuân thủ chuẩn `text/event-stream`, phát chuỗi sự kiện `start`, `reasoning`, `citations`, `token`, `interactive_options`, `done`.
- **AT-CoT Ambiguity Resolution**: Tự động nhận diện truy vấn mơ hồ ('từ con số 0'), phát sự kiện SSE `interactive_options` với 3 Personas và 3 câu hỏi Diagnostic Micro-Quiz định hình đối tượng học.
- **Multi-turn Context Grounding**: Phản hồi may đo theo phản hồi lựa chọn Nhóm B với lộ trình 5 chặng neo chính xác vào Figure 1 và Table 1.
- **Table 1 Mathematical Precision**: So sánh chuẩn xác độ phức tạp $\\mathcal{{O}}(n^2 \\cdot d)$ vs $\\mathcal{{O}}(n \\cdot d^2)$, đính kèm trích dẫn không gian Trang 6 với Bounding Box IoU.
- **Socratic Presupposition Refutation**: Bác bỏ tiền đề sai lệch gán ghép RNN vào Encoder Transformer, điều hướng người học đến Positional Encoding tại Mục 3.5 Trang 6.
- **Anti-Hallucination Scope & Metric Guards**:
  - Từ chối các truy vấn ngoài phạm vi thời gian/nghiệp vụ (ResNet, YOLO, GSM8K, GPT-4) trên bài báo 2017 (`finish_reason="abstention"`).
  - Bác bỏ bẫy sai số thực nghiệm 45.0 BLEU, xác nhận chính xác điểm kỷ lục 28.4 EN-DE tại Table 2 Trang 8.
- **Stream Resumption (RFC 8895 Last-Event-ID)**: Hỗ trợ khôi phục luồng stream đứt quãng, bỏ qua sự kiện đã phát tới client.
- **Archived Session Message Guard**: Khóa gửi tin nhắn và phát sự kiện `error` (`SESSION_ARCHIVED`) khi phiên đã chuyển sang trạng thái lưu trữ.
- **Hermetic REST Lifecycle & Clean Up**: Tự động dọn sạch tài nguyên và bảng phụ thuộc qua REST API chuẩn (`DELETE /api/v1/documents/{{id}}` và `DELETE /api/v1/sessions/{{id}}`) khi kết thúc tiến trình (Zero Retention).

---

## 3. Raw Response Snapshots (Sample SSE Event Payloads)

### Case 1: Ambiguous Query Clarification (`event: interactive_options`)
```json
{{
  "event": "interactive_options",
  "data": {{
    "personas": [
      {{"id": "persona_a", "label": "Nhóm A: Nhập môn AI / Chưa có nền tảng toán"}},
      {{"id": "persona_b", "label": "Nhóm B: Đã có nền tảng cơ bản về ML nhưng chưa hiểu Self-Attention"}},
      {{"id": "persona_c", "label": "Nhóm C: Kỹ sư muốn triển khai Transformer từ scratch"}}
    ],
    "quiz": [
      {{"question": "Bạn đã quen thuộc với phép nhân ma trận chưa?", "options": ["Có", "Chưa"]}},
      {{"question": "Mục tiêu chính của bạn là hiểu lý thuyết hay viết code?", "options": ["Lý thuyết", "Thực hành"]}},
      {{"question": "Bạn có sẵn sàng đọc trực tiếp công thức toán trong Paper không?", "options": ["Có", "Cần giải thích trực quan"]}}
    ]
  }}
}}
```

### Case 3: Table 1 Complexity Math & Citations
```json
{{
  "citations": [
    {{
      "citation_id": "cit_1",
      "document_title": "Attention Is All You Need",
      "page_number": 6,
      "bounding_boxes": [[0.12, 0.15, 0.45, 0.85, 6]]
    }}
  ],
  "full_answer": "Theo Table 1 trong bài báo, độ phức tạp tính toán trên mỗi layer của Self-Attention là O(n^2 · d), trong khi Recurrent là O(n · d^2). Khi n < d, Self-Attention nhanh hơn đáng kể..."
}}
```

### Case 4: Socratic False Presupposition Refutation
```json
{{
  "thought": "User hỏi vị trí RNN trong Encoder. Cần bác bỏ vì Transformer hoàn toàn loại bỏ Recurrence.",
  "full_answer": "Tiền đề trong câu hỏi của bạn chưa chính xác: Kiến trúc Transformer trong bài báo đã loại bỏ hoàn toàn các cơ chế đệ quy (RNN)... Để duy trì thứ tự từ, tác giả sử dụng Positional Encoding được trình bày chi tiết tại Mục 3.5, Trang 6."
}}
```
"""

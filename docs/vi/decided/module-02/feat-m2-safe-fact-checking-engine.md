# Module 2: Kiến trúc Quy trình 4 Bước SAFE Fact-Checking Engine

## 1. Tổng quan & Mục tiêu Kỹ thuật
Quy trình kiểm chứng sự thật học thuật tuân thủ nghiêm ngặt phương pháp chuẩn **SAFE (Search-Augmented Factuality Evaluator)** của Google DeepMind, kết hợp làm giàu ngữ cảnh tiền đề (Premise Context Augmentation) và bảo toàn tọa độ trích dẫn trực quan `BoundingBox` `[x0, y0, x1, y1, page]`.

---

## 2. Chuỗi Quy trình 4 Bước (Pipeline Architecture)

```
Văn bản / Bản thảo
       │
       ▼
[Bước 1: Phân rã Sự thật (Fact Decomposition)]
  Tách các câu phức thành các mệnh đề nguyên tử độc lập (Atomic Claims)
       │
       ▼
[Bước 2: Chuẩn hóa Ngữ cảnh & Thực thể (Entity Normalization)]
  Phân giải đại từ ("họ", "mô hình này") thành danh từ thực thể xác định
       │
       ▼
[Bước 3: Truy xuất Bất đối xứng Có Mục tiêu (Targeted Retrieval)]
  Sinh query hướng mục tiêu và xếp hạng chunk bằng Asymmetric Coverage Matching
       │
       ▼
[Bước 4: NLI Scoring & Làm Giàu Tiền Đề (Textual Entailment)]
  Ghép ngữ cảnh phân mục vào Premise, phân loại 3 nhãn:
  🟢 Supported | 🔴 Contradicted | 🟡 Not Enough Info
```

### Bước 1: Fact Decomposition (Phân rã sự thật)
- Phân tích câu phức thành các phát biểu sự thật nguyên tử (Atomic Claims).
- Ví dụ câu: *"Mô hình Attention đạt 28.4 BLEU trên WMT 2014 và giảm thời gian huấn luyện xuống 3.5 ngày"* được tách thành 2 mệnh đề nguyên tử:
  1. `Mô hình Attention đạt 28.4 BLEU trên WMT 2014`
  2. `Mô hình Attention giảm thời gian huấn luyện xuống 3.5 ngày`

### Bước 2: Entity & Context Normalization
- Bóc tách thực thể viết hoa, danh từ riêng hoặc thuật ngữ khoa học (`Transformer`, `BLEU`, `ImageNet`, `ResNet`).
- Thay thế các tham chiếu mơ hồ bằng thực thể trung tâm được phát hiện trong toàn bài.

### Bước 3: Asymmetric Retrieval Coverage Ranking
- Đối chiếu mệnh đề ngắn (7 - 12 tokens) với các khối văn bản tài liệu khoa học (50 - 150 tokens).
- Điểm tương đồng được tính theo công thức bao phủ bất đối xứng:
  $$\text{Score} = 0.75 \times \text{Recall}_{\text{claim\_coverage}} + 0.25 \times \text{Precision} + \text{EntityBonus}$$
- Điều này ngăn chặn việc suy giảm điểm khi đối chiếu câu ngắn với đoạn dài có chứa bằng chứng đầy đủ.

### Bước 4: Natural Language Inference (NLI) & Bounding Box Preservation
- Khi xác định mối quan hệ ngữ nghĩa giữa mệnh đề và bằng chứng:
  - Nếu bằng chứng bao hàm và xác thực số liệu/luận điểm: Nhãn `supported`, độ tin cậy từ 0.75 đến 0.98.
  - Nếu bằng chứng phủ định hoặc chứa cặp từ mâu thuẫn đối nghịch (như *"outperform"* vs *"underperform"*, *"increase"* vs *"decrease"*): Nhãn `contradicted`, phát tín hiệu cảnh báo AI suy diễn sai.
  - Nếu không tìm thấy bằng chứng thỏa mãn ngưỡng độ tương đồng: Nhãn `not_enough_info`.
- **Bất biến Tọa độ Bounding Box:** Toàn bộ bằng chứng được trích xuất đều lưu giữ nguyên vẹn mảng tọa độ chuẩn hóa `[x0, y0, x1, y1, page]`, `page >= 1`, gốc tọa độ Top-Left `(0, 0)` theo quy chuẩn hệ thống.

---

## 3. API Contract & Schema

- **Route:** `POST /api/v1/drafts/{id}/verify-facts`
- **Request Body:**
  ```json
  {
    "text": "The Transformer architecture achieves 28.4 BLEU on English-to-German translation.",
    "document_ids": ["c348f980-0a2b-4fa8-b220-db9d18fa5b02"]
  }
  ```
- **Response Structure (`VerifyFactsResponse`):**
  ```json
  {
    "success": true,
    "data": {
      "draft_id": "9a0f443b-6e93-4e89-a5c6-628d0097f48e",
      "verified_text": "The Transformer architecture achieves 28.4 BLEU on English-to-German translation.",
      "claims": [
        {
          "id": "claim_54e19b38ae",
          "claim_text": "The Transformer architecture achieves 28.4 BLEU on English-to-German translation.",
          "normalized_entities": ["Transformer", "BLEU"],
          "status": "supported",
          "confidence_score": 0.95,
          "evidence_text": "On the WMT 2014 English-to-German translation task, the big transformer model achieves 28.4 BLEU.",
          "evidence_document_id": "c348f980-0a2b-4fa8-b220-db9d18fa5b02",
          "evidence_document_title": "Attention Is All You Need",
          "evidence_page": 1,
          "evidence_bounding_boxes": [[0.1, 0.2, 0.8, 0.3, 1]],
          "reasoning": "Direct empirical entailment verified against document chunk."
        }
      ],
      "total_claims": 1,
      "supported_claims": 1,
      "contradicted_claims": 0,
      "unverified_claims": 0,
      "supported_ratio": 1.0,
      "latency_ms": 145,
      "verified_at": "2026-10-15T06:30:00Z"
    }
  }
  ```

---

## 4. Kiểm thử Đơn vị & In-Memory Isolation
- `packages/core/tests/domain/test_safe_fact_checker.py`:
  - `test_fact_decomposition`: Kiểm tra phân rã câu phức thành mệnh đề nguyên tử.
  - `test_entity_normalization`: Kiểm tra bóc tách thực thể viết hoa.
  - `test_fact_verification_supported`: Kiểm tra nhãn supported và bảo toàn bounding box.
  - `test_fact_verification_contradicted`: Kiểm tra nhận diện mâu thuẫn số liệu.

# Thiết Kế Hệ Thống Đánh Giá Chất Lượng API Qua Báo Cáo Tự Động (API Snapshot & Evaluation Harness)

## 1. Bối Cảnh & Vấn Đề (Problem Statement)

Trong các hệ thống xử lý tài liệu khoa học phức tạp như **VeriScholar** (kết hợp bóc tách PDF nhị phân, thị giác máy tính, phân mảnh ngữ nghĩa, bóc tách thực thể học thuật, visual grounding và truy xuất vector RAG):
- **Khoảng cách giữa "Unit Test Xanh" và "Dữ Liệu Phân Phối Thực Tế":** Unit test với Mock data thường luôn pass vì dữ liệu giả định quá lý tưởng (chuỗi văn bản ngắn, cú pháp chuẩn). Tuy nhiên, khi đối mặt với tài liệu PDF thực tế ngoài đời (bản in arXiv 2 cột, bảng biểu phức tạp, công thức Toán, ngắt dòng URL, header/footer dính vào nội dung), pipeline thực tế rất dễ phát sinh lỗi nghiêm trọng.
- **Chi phí kiểm thử thủ công cao:** Việc kỹ sư phải sử dụng Postman kiểm thử từng API rồi sao chép thủ công hàng trăm dòng JSON vào màn hình trao đổi để đánh giá chất lượng vừa tốn thời gian, vừa dễ bỏ sót lỗi.
- **Nhu cầu về một mặt phẳng quan sát chung (Shared Observability Plane):** Cần một cơ chế tự động hóa cho phép chạy API với các bài báo học thuật chuẩn (Golden Papers Dataset), đối chiếu với dữ liệu chuẩn (Ground Truth), lưu giữ cả Input và Output theo cấu trúc tinh gọn vào tệp báo cáo Markdown (`.md`) song song với tệp chỉ số máy đọc (`eval_metrics.json`). Cơ chế này giúp cả kỹ sư, AI Agent và đường ống CI/CD có chung một lăng kính quan sát, đánh giá chất lượng và phát hiện lỗi hồi quy tức thì ngay trên Git repo.

---

## 2. Điểm Mạnh Cốt Lõi Của Thiết Kế (Core Architectural Strengths)

1. **AI & Human-Readable Shared Artifacts:**  
   Báo cáo Markdown đặt trực tiếp trong repository giúp kỹ sư và AI Agent đọc - hiểu cấu trúc dữ liệu ngang hàng mà không cần phải truy cập cơ sở dữ liệu hay log server phức tạp.
2. **Bộ Kiểm Tra Ngữ Nghĩa Không Tốn Token (Zero-Token Semantic Linter Heuristics):**  
   Phát hiện sớm các lỗi trích xuất cấu trúc (như regex bắt nhầm ngày tháng vào tiêu đề, rỗng tác giả, URL ngắt quãng, DOI trùng lặp tiền tố) bằng logic Heuristic với chi phí tính toán bằng 0, không cần tiêu tốn token gọi mô hình LLM-as-a-judge cho các trường dữ liệu có quy chuẩn.
3. **Thước Đo Không Gian Cho Visual Grounding RAG (Spatial IoU Gate):**  
   Đánh giá độ chính xác của tọa độ hộp giới hạn (Bounding Box) trên canvas PDF.js, đảm bảo tính năng highlight bằng chứng học thuật hiển thị chuẩn xác từng pixel.
4. **Theo Dõi Hồi Quy Trực Quan Bằng Git Diff (Visual Regression via Git Diff):**  
   Mọi cải tiến hay suy giảm chất lượng trích xuất đều được phản ánh trực tiếp dưới dạng các dòng diff xanh/đỏ rõ ràng trong mỗi Pull Request, giúp việc Code Review diễn ra minh bạch và nhanh chóng.

---

## 3. Hệ Thống Rào Chặn & Giải Pháp Kỹ Thuật Đạt Chuẩn Production (Freeze Spec)

Đối chiếu với các nguyên lý trong *Software Engineering at Google*, *Continuous Delivery*, *Designing Data-Intensive Applications*, *Building Microservices* và *AI Engineering*, kiến trúc thiết lập 8 rào chặn bảo vệ hệ thống:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TÁM NGUYÊN TẮC BẢO VỆ HỆ THỐNG                           │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ 1. Cascading Matcher     │ Khớp 2 tầng: DOI/arXiv ID -> Token Jaccard >=0.85│
│    (Token Jaccard)       │ + Năm để tính Precision & Recall thực tế.        │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 2. Spatial IoU Gate      │ Đo Intersection over Union của Bounding Box:     │
│    (Visual Grounding)    │ Yêu cầu IoU >= 0.70 để chống lệch tọa độ canvas. │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 3. Hermetic REST Cleanup │ Dọn dẹp hợp thức qua DELETE /api/v1/documents/{id│
│    (No Backdoor Endpoint)│ Tuyệt đối không tạo backdoor API gây lỗ hổng.    │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 4. Deterministic Polling │ Tự động bắt mã 202 Accepted, Polling trạng thái  │
│    Barrier (Async Sync)  │ đến khi status == "completed" mới kiểm toán.     │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 5. Signal Safe Cleanup   │ Hủy task chính qua asyncio.CancelledError để     │
│    (Event Loop Safety)   │ coroutine __aexit__ luôn dọn sạch khi bị ngắt.   │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 6. Full VCR Replay       │ Replay Cassette cho Azure OCR, OpenAI Embeddings,│
│    (Zero-Cost CI Gate)   │ Crossref; Chỉ --live-cloud mới gọi mạng thực tế. │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 7. Snapshot Blessing     │ Cờ --bless tự động cập nhật .expected.json khi   │
│    (Workflow Ergonomics) │ thuật toán cải tiến vượt trội dữ liệu cũ.        │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 8. Dual-Output & Budget  │ .md tinh gọn (< 50 KB) cho người & AI review;    │
│    (CI Quality Gate)     │ eval_metrics.json (exit code 1 nếu Recall < 0.90)│
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

### 3.1. Thuật Toán Khớp Xếp Tầng (Cascading Matcher: Token Jaccard)

- **Nguy cơ tiềm ẩn:** Nếu dùng `difflib.SequenceMatcher` ở cấp độ ký tự, thuật toán dễ bị đánh lừa bởi tiêu đề phụ (ví dụ: *"Attention Is All You Need"* so với *"Attention Is All You Need: A Deep Dive"* đạt similarity > 0.85 gây bắt nhầm), hoặc bị trượt do đảo vị trí từ.
- **Giải pháp chuẩn hóa:** Sử dụng **Token-based Jaccard Similarity** kết hợp rào chắn tiền tố/hậu tố:
  - **Công thức tính toán:**
    - `Recall = |Extracted ∩ Expected| / |Expected|`
    - `Precision = |Extracted ∩ Expected| / |Extracted|`
  - **Logic so khớp 2 tầng:**
    ```python
    import re
    from typing import Any


    def token_jaccard_similarity(title_a: str, title_b: str) -> float:
      tokens_a = set(re.findall(r'\w+', title_a.lower()))
      tokens_b = set(re.findall(r'\w+', title_b.lower()))
      if not tokens_a or not tokens_b:
        return 0.0
      return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))


    def is_reference_match(
        extracted: dict[str, Any], expected: dict[str, Any]
    ) -> bool:
      # Tầng 1: Khớp định danh duy nhất (DOI / arXiv ID)
      if extracted.get('doi') and expected.get('doi'):
        return (
            extracted['doi'].strip().lower() == expected['doi'].strip().lower()
        )
      if extracted.get('arxiv_id') and expected.get('arxiv_id'):
        return (
            extracted['arxiv_id'].strip().lower()
            == expected['arxiv_id'].strip().lower()
        )

      # Tầng 2: Khớp tiêu đề mờ theo Token Jaccard
      title_ext = extracted.get('title', '')
      title_exp = expected.get('title', '')
      similarity = token_jaccard_similarity(title_ext, title_exp)

      if similarity >= 0.85:
        # Kiểm tra từ định danh phiên bản/phần (part 1, part 2, v1, v2) nếu có
        for tag in ['part 1', 'part 2', 'part i', 'part ii', 'v1', 'v2']:
          if (tag in title_ext.lower()) != (tag in title_exp.lower()):
            return False
        if extracted.get('year') and expected.get('year'):
          return extracted['year'] == expected['year']
        return True

      return False
```

---

### 3.2. Thước Đo Không Gian Cho Visual Grounding RAG (Spatial IoU Gate)

- **Nguy cơ tiềm ẩn:** VeriScholar render khung viền highlight trên Canvas PDF.js dựa trên tọa độ `[x0, y0, x1, y1, page]`. Nếu parser trích xuất đúng 100% chữ nhưng bị lỗi ma trận affine (như `rotation_deg = 90` làm đổi trục X và Y, hoặc sai tỷ lệ trang), khung highlight sẽ bị vẽ lệch ra khoảng trắng hoặc sang cột đối diện.
- **Giải pháp chuẩn hóa:**
  - Bổ sung thước đo **Intersection over Union (IoU)** cho Bounding Box trong tập Ground Truth đối với các bài kiểm thử Layout/Chunks:
    - `IoU(B_pred, B_gt) = Area(B_pred ∩ B_gt) / Area(B_pred ∪ B_gt)`
  - Ngưỡng nghiệm thu tối thiểu: **`Spatial_IoU >= 0.70`** (hoặc độ bao phủ ký tự Containment >= 0.85).

---

### 3.3. Dọn Dẹp An Toàn Qua Chuẩn REST API (Loại Bỏ Anti-Pattern Testing Backdoor)

- **Nguy cơ tiềm ẩn:** Tạo các endpoint backdoor như `/api/v1/testing/...` trên router FastAPI vi phạm nghiêm trọng hợp đồng API 59 endpoints đã đóng băng, đồng thời tiềm ẩn rủi ro bảo mật IDOR nếu lọt lên production.
- **Giải pháp chuẩn hóa:**
  - Harness tương tác 100% qua chuẩn REST hiện hữu của hệ thống.
  - Trong `EvaluationContext`:
    1. Khi tải bài báo lên, lưu lại danh sách `created_document_ids`.
    2. Khi dọn dẹp trong `__aexit__`, gọi tuần tự `DELETE /api/v1/documents/{doc_id}`.
    3. Endpoint này kích hoạt luồng cascade Domain chuẩn: xóa chunks, vectors, và giảm `ref_count` trong `document_storage_blobs` tuyệt đối an toàn.

---

### 3.4. VCR Replay Barrier Toàn Diện (Bảo Vệ Hạn Ngạch & Tính Tất Định CI)

- **Nguy cơ tiềm ẩn:** Gói Azure for Students (F0) chỉ có 500 trang/tháng; đồng thời việc gửi request liên tục đến OpenAI Embedding (`text-embedding-3-small`) trên mỗi lượt CI sẽ gây tốn chi phí token và dễ bị chặn tần suất mạng (`429 Too Many Requests`).
- **Giải pháp chuẩn hóa:**
  - Thiết lập thư mục `tests/fixtures/cassettes/` lưu trữ phản hồi đã cache của các dịch vụ bên ngoài (Azure OCR, OpenAI Embeddings, Crossref).
  - **Mặc định (CI Gate & Local Dev):** Sử dụng mock cassette, tiêu tốn **0 token và 0 request đám mây**.
  - **Chế độ kiểm toán trực tiếp (`--live-cloud`):** Chỉ kích hoạt khi có lệnh kiểm toán phát hành chính thức.

---

### 3.5. Cơ Chế Cập Nhật Baseline Tự Động (Snapshot Blessing Pattern)

- **Nguy cơ tiềm ẩn:** Khi kỹ sư cải tiến thuật toán bóc tách giúp tìm thấy nhiều tài liệu tham khảo chính xác hơn dữ liệu cũ, toàn bộ test suite sẽ báo fail do lệch với `.expected.json`. Nếu phải cập nhật thủ công hàng trăm trường JSON bằng tay thì chi phí bảo trì sẽ rất lớn.
- **Giải pháp chuẩn hóa:**
  - Bổ sung cờ **`--bless`** (tương tự như Jest / Pytest-Snapshot):
    ```bash
    uv run python scripts/eval_api.py --api extract-references --bless
    ```
  - Khi kỹ sư đã xem xét báo cáo Markdown và xác nhận kết quả mới là chính xác, lệnh trên sẽ tự động đồng bộ output mới vào tệp `.expected.json`.

---

### 3.6. Rào Chặn Đồng Bộ Trạng Thái Cho Endpoint Bất Đồng Bộ `202 Accepted` (Deterministic Polling Barrier)

- Gửi lệnh `POST :parse` và nhận mã `202 Accepted`.
- Tự động chuyển sang vòng lặp polling `GET /documents/{id}/status` với Exponential Backoff (chu kỳ 500ms đến 2s, timeout cứng 30 giây).
- Chỉ khi `status == "completed"`, runner mới gọi `GET /documents/{id}` để nạp payload thực tế vào bộ linter ngữ nghĩa.

---

### 3.7. Rào Chặn Tín Hiệu Ngắt An Toàn (Signal-Safe Cancellation)

- Thay vì dùng `sys.exit(1)` trong signal handler làm dừng Event Loop đột ngột, runner kích hoạt `current_task.cancel()`.
- Ngoại lệ `asyncio.CancelledError` kích hoạt phương thức `__aexit__` của `EvaluationContext`, gọi `DELETE /api/v1/documents/{doc_id}` để dọn sạch toàn bộ tài liệu kiểm thử trước khi tiến trình kết thúc.

---

### 3.8. Kiến Trúc Dual-Output & Quality Budget Cho Đường Ống CI/CD

- **Mô hình Dual-Output:**
  1. **Tệp Markdown (`docs/eval-reports/<api_name>.md`):** Tinh gọn (< 50 KB), chứa Executive Summary, Spatial IoU, Precision/Recall, Linter Warnings và các mẫu lỗi đại diện cho người và AI Agent review.
  2. **Tệp JSON Chỉ Số Máy Đọc (`tests/.artifacts/eval_metrics.json`):** Chứa các thông số định lượng phục vụ máy chủ CI.
- **Quality Budget Gate:**
  - Cấu hình ngưỡng chất lượng tối thiểu: `min_recall = 0.90`, `min_precision = 0.95`, `min_spatial_iou = 0.70`.
  - Nếu bất kỳ chỉ số cốt lõi nào tụt dưới ngưỡng, runner tự động thoát với **`exit code 1`** để ngắt đường ống CI ngay lập tức.
- **Khai báo `.gitignore`:** Thư mục `tests/.artifacts/` được bỏ qua không commit vào Git repo.

---

## 4. Chiến Lược Tập Dữ Liệu Chuẩn (Golden Papers Dataset)

Bộ tài liệu kiểm thử được đặt tại thư mục `data/papers/`, gồm 7 nhóm tài liệu (4 Happy Path kèm Ground Truth + 3 Chaos Negative):

| Nhóm Tài Liệu | Tệp PDF & Expected JSON | Đặc Điểm Thử Nghiệm | Mục Tiêu Đánh Giá |
| :--- | :--- | :--- | :--- |
| **1. Conference 2-Column** | `1706.03762v7.pdf`<br>`1706.03762v7.expected.json` | 15 trang, bố cục 2 cột NeurIPS, nhiều công thức Toán LaTeX, trích dẫn dạng bracket `[1]`. | Kiểm tra khả năng đọc đúng thứ tự cột, không trộn lẫn văn bản giữa 2 cột song song. |
| **2. Long Preprint LNCS** | `2504.19754v1.pdf`<br>`2504.19754v1.expected.json` | 24 trang, phong cách Springer LNCS (tác giả cách nhau bằng dấu hai chấm `: `), URL ngắt dòng. | Kiểm tra thuật toán bóc tách tài liệu tham khảo, chuẩn hóa URL ngắt dòng và loại bỏ running header. |
| **3. Fast Smoke Sample** | `sample_short_paper.pdf`<br>`sample_short_paper.expected.json` | 2 đến 3 trang, dung lượng nhẹ (< 500 KB). | Dùng cho Tầng 1 (Smoke Snapshot) chạy nhanh < 15 giây trên CI/CD pipeline. |
| **4. Scanned PDF (OCR)** | `scanned_sample_noisy.pdf`<br>`scanned_sample_noisy.expected.json` | Tệp PDF dạng ảnh quét đen trắng mờ, không có text layer số hóa. | Kiểm chứng nhánh Fallback OCR qua VCR Replay Fixture (hoặc Live Azure nếu bật cờ `--live-cloud`). |
| **5. Corrupted Header** | `corrupted_structure.pdf` | Tệp nhị phân hỏng cấu trúc `%PDF-`. | Xác thực mã lỗi `422 UNSUPPORTED_PDF_FORMAT`. |
| **6. Encrypted File** | `password_protected.pdf` | Tệp PDF khóa mật khẩu AES-128. | Xác thực mã lỗi `422 UNSUPPORTED_PDF_ENCRYPTED`. |
| **7. Oversized File** | `oversized_55mb.pdf` | Tệp dung lượng 55 MB (> 50 MB limit). | Xác thực middleware từ chối `422 VALIDATION_ERROR`. |

---

## 5. Tích Hợp Toàn Diện 9 Endpoints Swagger (Module 1 Specification Mapping)

Toàn bộ 9 endpoint thuộc **Module 1 (Deep Read & Ingestion)** trong [swagger.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md) được ánh xạ tương ứng vào bộ harness:

```
                                MODULE 1: SWAGGER ENDPOINTS MATRIX
┌────┬─────────────────────────────────────────────────┬────────────────────────────────────────────┬─────────────────────────────┐
│ TT │ Swagger Endpoint & Phương Thức                  │ Tệp Báo Cáo Markdown Sinh Tự Động          │ Trọng Tâm Đánh Giá Snapshot │
├────┼─────────────────────────────────────────────────┼────────────────────────────────────────────┼─────────────────────────────┤
│ 1  │ POST /api/v1/documents                          │ post_documents_upload.md                   │ CAS Hash & Deduplication    │
│ 2  │ GET  /api/v1/documents                          │ get_documents_list.md                      │ Pagination & Search Filters │
│ 3  │ GET  /api/v1/documents/{document_id}            │ get_documents_detail.md                    │ Metadata & Pages Dimensions │
│ 4  │ GET  /api/v1/documents/{document_id}/file       │ get_documents_file_stream.md               │ 200 Full & 206 Byte Ranges  │
│ 5  │ GET  /api/v1/documents/{document_id}/status     │ get_documents_status.md                    │ Pipeline Stages Detail & %  │
│ 6  │ POST /api/v1/documents/{document_id}:star       │ post_documents_star.md                     │ Persistence & Folder Toggle │
│ 7  │ DELETE /api/v1/documents/{document_id}          │ delete_documents.md                        │ CAS Ref-count & Soft Purge  │
│ 8  │ POST /api/v1/documents/{document_id}:parse      │ post_documents_parse.md                    │ 202 Barrier & Spatial IoU   │
│ 9  │ POST /api/v1/documents/{id}:extract-references  │ post_documents_extract_references.md       │ Token Jaccard Linters       │
└────┴─────────────────────────────────────────────────┴────────────────────────────────────────────┴─────────────────────────────┘
```

---

## 6. Mẫu Cấu Trúc Báo Cáo Markdown Tinh Gọn (`docs/eval-reports/<api_name>.md`)

````markdown
# API Evaluation Snapshot: POST /api/v1/documents/{id}:extract-references

> **Audit Header**: 2026-09-14 16:15:00 UTC | Session Tag: `test_eval_f81d4fae` | Mode: VCR Replay  
> **Raw Artifacts**: `tests/.artifacts/post_documents_extract_references/`  
> **Quality Gate**: PASSED (Thresholds: Recall >= 0.90, Precision >= 0.95)

---

## 1. Executive Summary & Ground Truth Verification

| Paper Key | HTTP Status | Latency | Extracted / Expected | Recall (Độ Phủ) | Precision (Độ Chuẩn) | Match Method | Quality Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `2504.19754v1.pdf` | `200 OK` | 412 ms | 20 / 20 items | 100.0% (20/20) | 100.0% (20/20) | 14 ID, 6 Token-Jaccard | PASSED |
| `1706.03762v7.pdf` | `200 OK` | 385 ms | 39 / 39 items | 100.0% (39/39) | 97.4% (38/39) | 37 ID, 1 Token-Jaccard | PASSED |
| `corrupted_structure.pdf` | `422 Unproc`| 18 ms | 0 / 0 items | N/A | N/A | Schema Error Catch | PASSED |

---

## 2. Metric Analysis & Edge-Case Samples

### Case: 2504.19754v1.pdf (Long Preprint Springer Style)
- **Extracted References Sample (Item 1)**:
  ```json
  {
    "ref_index": 1,
    "title": "Phi-3 technical report: A highly capable language model locally on your phone",
    "authors_count": 129,
    "year": 2024,
    "arxiv_id": "2404.14219",
    "doi": null,
    "match_status": "ground_truth_confirmed"
  }
  ```

---

## 3. Zero-Token Semantic Linter Log
- `[INFO]` `2504.19754v1.pdf`: Khôi phục thành công 2 URL bị ngắt dòng vắt qua trang (`hyphenated-url-stitched`).
- `[WARN]` `1706.03762v7.pdf`: Mục 38 thiếu tên tác giả cuối (chỉ có `et al.`), chấp nhận theo quy chuẩn Springer/NeurIPS.
````

---

## 7. Thiết Kế Kiến Trúc Script Runner (`scripts/eval_api.py`)

Cấu trúc script runner hoàn chỉnh:

```python
import asyncio
from dataclasses import dataclass
import json
from pathlib import Path
import re
import signal
import sys
from typing import Any, Protocol
import uuid
import httpx


@dataclass(frozen=True)
class QualityBudget:
  min_recall: float = 0.90
  min_precision: float = 0.95
  min_spatial_iou: float = 0.70
  allow_critical_warnings: bool = False


def calculate_bbox_iou(
    bbox_pred: list[float], bbox_gt: list[float]
) -> float:
  """Tính toán IoU giữa 2 Bounding Box [x0, y0, x1, y1]."""
  x0 = max(bbox_pred[0], bbox_gt[0])
  y0 = max(bbox_pred[1], bbox_gt[1])
  x1 = min(bbox_pred[2], bbox_gt[2])
  y1 = min(bbox_pred[3], bbox_gt[3])

  intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
  area_pred = (bbox_pred[2] - bbox_pred[0]) * (bbox_pred[3] - bbox_pred[1])
  area_gt = (bbox_gt[2] - bbox_gt[0]) * (bbox_gt[3] - bbox_gt[1])
  union = area_pred + area_gt - intersection

  return intersection / union if union > 0 else 0.0


def token_jaccard_similarity(title_a: str, title_b: str) -> float:
  """Khớp tiêu đề mờ theo tập từ vựng (Token Jaccard)."""
  tokens_a = set(re.findall(r'\w+', title_a.lower()))
  tokens_b = set(re.findall(r'\w+', title_b.lower()))
  if not tokens_a or not tokens_b:
    return 0.0
  return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))


class EvaluationContext:
  """Context Manager thực thi kiểm thử khép kín qua chuẩn REST API."""

  def __init__(self, base_url: str):
    self.base_url = base_url
    self.session_tag = f'test_eval_{uuid.uuid4().hex[:8]}'
    self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
    self.created_document_ids: list[str] = []

  async def __aenter__(self):
    return self

  def track_document(self, document_id: str):
    self.created_document_ids.append(document_id)

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    # Dọn dẹp hợp thức qua đúng chuẩn DELETE /api/v1/documents/{id}
    for doc_id in self.created_document_ids:
      try:
        await self.client.delete(f'/api/v1/documents/{doc_id}')
      except Exception as e:
        sys.stderr.write(f'Cảnh báo: Lỗi dọn dẹp document {doc_id}: {e}\n')
    await self.client.aclose()


async def main():
  current_task = asyncio.current_task()
  loop = asyncio.get_running_loop()

  def shutdown_handler():
    if current_task and not current_task.done():
      current_task.cancel()

  for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, shutdown_handler)

  try:
    async with EvaluationContext('http://localhost:8000') as ctx:
      # Thực thi quy trình kiểm thử và đối chiếu...
      pass
  except asyncio.CancelledError:
    sys.stderr.write(
        '\n[WARN] Nhận tín hiệu dừng. Đã dọn dẹp an toàn qua REST API.\n'
    )
```

### Các lệnh điều khiển CLI:
```bash
# Chạy nhanh Smoke Snapshot cho 1 API (chạy trên paper ngắn < 15 giây)
uv run python scripts/eval_api.py --api extract-references --smoke

# Đánh giá toàn diện đối chiếu Ground Truth Baseline trên toàn bộ Golden Papers
uv run python scripts/eval_api.py --api extract-references --all

# Tự động cập nhật baseline Ground Truth khi thuật toán mới tốt hơn
uv run python scripts/eval_api.py --api extract-references --bless

# Chạy đánh giá toàn bộ 9 Endpoints của Module 1 kèm kiểm tra Quality Budget
uv run python scripts/eval_api.py --module module1 --ci-gate

# Chạy kiểm toán thực tế gọi Azure OCR đám mây (tiêu hao hạn ngạch F0)
uv run python scripts/eval_api.py --all --live-cloud
```

---

## 8. Quy Trình Phối Hợp Giữa Kỹ Sư & AI (Human-in-the-Loop Workflow)

1. **Kỹ sư hoặc AI hoàn tất chỉnh sửa thuật toán bóc tách.**
2. **Kích hoạt công cụ autotest:** Chạy `uv run python scripts/eval_api.py --api <name>`.
3. **Cơ chế tự động dọn dẹp & ghi nhận:** Script tự xóa báo cáo `.md` cũ, gửi request vào API, chờ xử lý ngầm (Barrier), kiểm toán chất lượng đối chiếu Ground Truth qua Token Jaccard và Spatial IoU, xuất Markdown tinh gọn và file JSON chỉ số.
4. **AI Self-Audit:** AI đọc trực tiếp file `.md` vừa sinh, đối soát bảng chỉ số và các cảnh báo linter.
5. **Kỹ sư Review & CI Automation:** Kỹ sư mở file `.md` hoặc dùng `git diff docs/eval-reports/` để kiểm tra độ tin cậy. Máy chủ CI tự động kiểm tra exit code của `eval_metrics.json` để quyết định cho phép merge Pull Request.

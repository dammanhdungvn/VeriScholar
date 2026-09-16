# KẾ HOẠCH KỸ THUẬT: ĐÁNH GIÁ CHẤT LƯỢNG CHUNKING ĐẠT CHUẨN PRODUCTION
**Tài liệu tham chiếu:** `docs/vi/design-architecture.md`, `docs/vi/design-api-eval-snapshots.md`, `tests/evals/test_parse_chunking_eval.py`  
**Ngày khởi tạo:** 2026-09-16  
**Trạng thái:** SẴN SÀNG TRIỂN KHAI (APPROVED)  
**Phạm vi:** Core Domain Chunking Quality, NLP Invariants, Multi-Column Layout, Multi-Paper Benchmark

---

## 1. Bối cảnh & Vấn đề Cốt lõi

### 1.1. Hiện trạng
- API `GET /api/v1/documents/{id}/chunks` (API #11) và runner `get_documents_chunks.py` đã hoàn thành kiểm thử tầng giao thức (Protocol & API Layer): HTTP 200 OK, pagination RFC 8288, database caching dưới 15ms, include_content projection, schema validation.
- **Thách thức:** Các bài báo khoa học trong thực tế có hình thái và cấu trúc hoàn toàn không đồng nhất:
  1. **Bố cục đa cột (Multi-column layout):** Bài báo 2 cột (như ArXiv AI papers) nếu đọc sai thứ tự sẽ bị quét ngang qua 2 cột, làm trộn lẫn hai luồng ý niệm hoàn toàn tách biệt.
  2. **Công thức toán học (Math equations):** Công thức toán học nhiều dòng nếu bị ngắt đôi sẽ khiến vector embedding mất hoàn toàn ý nghĩa ngữ nghĩa.
  3. **Bảng biểu (Data Tables):** Các hàng số liệu bị tách khỏi dòng tiêu đề cột dẫn đến hallucination khi RAG trả lời.
  4. **Nhiễu lặp (Boilerplate noise):** Header tạp chí, footer, số trang lặp lại ở đầu và cuối trang bị cắt thành các "micro-chunks" vô nghĩa.

### 1.2. Mục tiêu kỹ thuật
Xây dựng một hệ thống đánh giá tự động (**Production Chunking Evaluation Harness**) có thể:
1. Định lượng hóa 100% chất lượng phân đoạn trên tập bài báo mẫu đa dạng mà không phụ thuộc vào cảm tính.
2. Thiết lập **Quality Gate (Ngưỡng chất lượng bắt buộc)** trong CI/CD: Bất kỳ thay đổi nào làm giảm độ chính xác bóc tách đều bị chặn merge.
3. Xuất ma trận so sánh chi tiết và báo cáo phân phối thống kê (*Token Distribution Histogram, Reading Flow, Anomaly Audit*).

---

## 2. Hệ thống Chỉ số Đánh giá Chuẩn Production (Quantitative Metrics)

Hệ thống đánh giá sẽ đo lường 6 khía cạnh độc lập:

| Nhóm chỉ số | Tên chỉ số | Công thức / Quy tắc tính | Ngưỡng sản xuất (SLA) |
| :--- | :--- | :--- | :---: |
| **1. Tính toàn vẹn Ngôn ngữ** | **Linguistic Boundary Integrity (LBI)** | (Số chunk kết thúc bằng dấu ngắt câu hợp lệ: chấm, chấm than, hỏi chấm, hai chấm) / (Tổng số chunk) | **>= 98.0%** |
| | **Dehyphenation Error Rate** | Tỷ lệ chunk kết thúc bằng từ bị chém ngang dấu gạch nối (ví dụ: `trans-` xuống dòng `former`) | **= 0.0%** |
| **2. Trật tự đọc Bố cục** | **Column-Reading Flow Integrity** | Tỷ lệ các bounding box liên tiếp tuân thủ thứ tự đọc chuẩn (đọc hết cột trái xong mới sang cột phải) | **100%** |
| | **Section Leakage Rate (SLR)** | Tỷ lệ chunk chứa ranh giới nhảy đột ngột giữa 2 Heading cấp 1 khác nhau | **<= 1.0%** |
| **3. Cấu trúc Toán & Bảng** | **Formula Integrity Score** | Tỷ lệ các khối công thức toán học nhiều dòng được giữ nguyên vẹn | **>= 95.0%** |
| | **Table Continuity Score** | Tỷ lệ bảng biểu giữ nguyên header kèm dòng dữ liệu | **>= 95.0%** |
| **4. Phân phối Thống kê** | **Micro-Chunk Rate (< 25 tokens)** | Tỷ lệ các chunk vụn vặt do header/footer/số trang sót lại | **<= 2.0%** |
| | **Bloated-Chunk Rate (> 800 tokens)** | Tỷ lệ các chunk quá lớn gây loãng ngữ cảnh vector embedding | **<= 1.0%** |
| | **Standard Deviation (Độ lệch chuẩn)** | Độ lệch chuẩn độ dài token của các chunk văn bản | **<= 180 tokens** |
| **5. Không gian Bounding Box** | **Spatial Coordinate Validity** | Tọa độ chuẩn hóa: `0.0 <= x0 < x1 <= 1.0` và `0.0 <= y0 < y1 <= 1.0` | **100%** |
| | **Text Area Coverage Ratio** | Tỷ lệ diện tích text layer trong PDF được bao phủ bởi các hộp giới hạn | **>= 95.0%** |
| **6. Hiệu năng Xử lý** | **Throughput / Latency SLA** | Thời gian bóc tách trung bình trên mỗi trang PDF | **< 35 ms/trang** |

---

## 3. Tập Dữ liệu Đối chuẩn Vàng (Golden Benchmark Dataset)

Hệ thống đánh giá sẽ chạy kiểm chuẩn trên 3 bài báo đại diện có sẵn trong thư mục `data/papers/`:

```
data/papers/
├── Attention Is All You Need.pdf
│   └── Benchmark 1: Bố cục 2 cột, công thức toán dày đặc, bảng tham số
├── Advancing Retrieval-Augmented Generation for Structured Enterprise and Internal Data.pdf
│   └── Benchmark 2: Cấu trúc văn bản doanh nghiệp, bảng biểu thực nghiệm
└── Reconstructing Context Evaluating Advanced Chunking Strategies for Retrieval-Augmented Generation.pdf
    └── Benchmark 3: Bài báo nghiên cứu chuyên sâu về các chiến lược chunking
```

### Đặc tả Bộ bất biến Kiểm chuẩn (Structural Invariants):
1. **Paper 1 (`Attention Is All You Need.pdf`):**
   - Định dạng 2 cột kinh điển ArXiv.
   - Bắt buộc bảo tồn nguyên vẹn khối công thức: `Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V`.
   - Bắt buộc không đọc chéo từ dòng cuối cột 1 sang dòng đầu cột 2 ở trang 2 và trang 3.
2. **Paper 2 (`Advancing Retrieval-Augmented Generation...`):**
   - Văn bản mô tả cấu trúc doanh nghiệp và bảng biểu so sánh.
   - Bắt buộc loại bỏ toàn bộ chuỗi Header/Footer lặp lại của IEEE/ArXiv.
3. **Paper 3 (`Reconstructing Context...`):**
   - Phân tích cấu trúc phân đoạn, cây phân cấp tiêu đề.
   - Bắt buộc giữ nguyên vẹn trật tự tiêu đề các mục (1 Introduction, 2 Related Work, ...).

---

## 4. Thiết kế Kiến trúc Module Đánh giá

```
                                  CLI / CI Pipeline
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
       scripts/eval_api.py                        scripts/eval_chunking_quality.py
   (Protocol & Integration Gate)               (Algorithmic & NLP Quality Benchmark)
                   │                                           │
                   ▼                                           ▼
       API Driving Adapters                        Core Extractor Port
     (FastAPI Endpoints)                   (IChunkExtractorPort / PyMuPDFChunkExtractor)
                   │                                           │
                   ▼                                           ▼
        Database / Network                           scripts/eval/chunking_metrics.py
    (PostgreSQL / Redis / CAS)                   (Pure Math & NLP Quality Calculus)
                                                               │
                                                               ▼
                                                  temp/output/test/chunking_quality_matrix.md
                                                  (Histogram, Cross-Paper Anomaly Audit)
```

### 4.1. File `scripts/eval/chunking_metrics.py` (Domain Quality Calculator)
Module thuần túy (Pure functions, không phụ thuộc database/network):
- `calculate_boundary_integrity(chunks: list[ExtractedChunk]) -> float`
- `detect_reading_order_violations(chunks: list[ExtractedChunk]) -> list[Violation]`
- `detect_micro_and_bloated_chunks(chunks: list[ExtractedChunk]) -> ChunkSizeDistribution`
- `calculate_spatial_coverage(chunks: list[ExtractedChunk], page_dims: list) -> float`
- `audit_anomalies(chunks: list[ExtractedChunk]) -> list[ChunkAnomaly]`

### 4.2. File `scripts/eval_chunking_quality.py` (CLI Runner & Report Generator)
Runner chạy dòng lệnh chuyên nghiệp:
- **Tham số CLI:**
  - `--paper <filename>`: Chạy đánh giá trên 1 bài cụ thể.
  - `--all`: Quét qua toàn bộ bài báo trong `data/papers/`.
  - `--ci-gate`: Trả về `exit(1)` nếu bất kỳ bài nào không đạt SLA sản xuất.
  - `--save-artifacts`: Lưu JSON phân tích chi tiết vào `tests/.artifacts/chunking_eval/`.
- **In-Terminal Display:**
  - Bảng thống kê so sánh đa chiều (Cross-paper comparison matrix).
  - Biểu đồ phân phối độ dài token (Token count histogram dạng ký tự ASCII).
- **Snapshot Report Markdown:**
  - Tự động ghi ra `temp/output/test/chunking_quality_matrix.md`.

---

## 5. Kế hoạch Triển khai Chi tiết (Action Plan)

### Bước 1: Xây dựng Thư viện Đo lường Chất lượng (`scripts/eval/chunking_metrics.py`)
- Cài đặt các thuật toán kiểm tra ranh giới câu bằng Regex phân tích ngữ pháp tiếng Anh khoa học.
- Cài đặt thuật toán phát hiện vi phạm thứ tự đọc 2 cột dựa trên tọa độ X-Y của Bounding Box.
- Tính toán các chỉ số thống kê phân phối: Min, Max, Mean, P50 (Trung vị), P90, P99, Độ lệch chuẩn.

### Bước 2: Xây dựng CLI Benchmark Runner (`scripts/eval_chunking_quality.py`)
- Nạp trực tiếp các tệp PDF từ `data/papers/`.
- Thực thi bóc tách qua `PyMuPDFChunkExtractor`.
- Thu thập dữ liệu, chạy bộ metrics, và tính toán điểm tổng hợp (Composite Quality Score).
- Kết xuất giao diện đóng khung trên Terminal và ghi file báo cáo Markdown chuẩn mực.

### Bước 3: Đăng ký Kiểm chuẩn Tự động vào Test Suite (`tests/evals/test_chunking_quality.py`)
- Tạo test case pytest tự động xác thực các ngưỡng SLA bắt buộc:
  - `test_all_papers_boundary_integrity_sla`
  - `test_all_papers_no_dehyphenation_violations`
  - `test_all_papers_micro_chunk_tolerance`
  - `test_all_papers_bounding_box_validity`

### Bước 4: Chạy Thử nghiệm Thực tế & Tinh chỉnh
- Chạy thử nghiệm trên cả 3 bài báo khoa học.
- Quan sát các dị biệt (anomalies) được phát hiện: nếu có hiện tượng cắt gãy câu hoặc sót cột, tiến hành tinh chỉnh bộ tách câu trong `PyMuPDFChunkExtractor`.
- Xác nhận toàn bộ 3 bài báo vượt qua Quality Gate với điểm số trên 95/100.

---

## 6. Tiêu chuẩn Chấp thuận (Acceptance Criteria)

1. [ ] Có file `scripts/eval/chunking_metrics.py` chứa toàn bộ công thức tính toán toán học/ngôn ngữ.
2. [ ] Có file `scripts/eval_chunking_quality.py` chạy độc lập với cờ `--all` và `--ci-gate`.
3. [ ] Chạy thành công qua 100% các file PDF trong `data/papers/`.
4. [ ] Báo cáo `temp/output/test/chunking_quality_matrix.md` được sinh ra tự động với số liệu thống kê chi tiết.
5. [ ] Bộ test pytest tích hợp `tests/evals/test_chunking_quality.py` chạy xanh (100% PASS).
6. [ ] Không có lỗi cú pháp hay cảnh báo ruff/mypy (`ruff check .`, `mypy apps/ packages/`).

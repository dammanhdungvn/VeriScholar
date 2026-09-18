# Thiết Kế Hệ Thống Đánh Giá Chất Lượng API Qua Báo Cáo Tự Động (API Snapshot & Evaluation Harness)

## 1. Bối Cảnh & Vấn Đề (Problem Statement)

Trong các hệ thống xử lý tài liệu khoa học phức tạp như **VeriScholar** (kết hợp bóc tách PDF nhị phân, thị giác máy tính, phân mảnh ngữ nghĩa, bóc tách thực thể học thuật, visual grounding và truy xuất vector RAG):
- **Khoảng cách giữa "Unit Test Xanh" và "Dữ Liệu Phân Phối Thực Tế":** Unit test với Mock data thường luôn pass vì dữ liệu giả định quá lý tưởng (chuỗi văn bản ngắn, cú pháp chuẩn). Tuy nhiên, khi đối mặt với tài liệu PDF thực tế ngoài đời (bản in arXiv 2 cột, bảng biểu phức tạp, công thức Toán, ngắt dòng URL, header/footer dính vào nội dung), pipeline thực tế rất dễ phát sinh lỗi nghiêm trọng.
- **Chi phí kiểm thử thủ công cao:** Việc kỹ sư phải sử dụng Postman kiểm thử từng API rồi sao chép thủ công hàng trăm dòng JSON vào màn hình trao đổi để đánh giá chất lượng vừa tốn thời gian, vừa dễ bỏ sót lỗi.
- **Nhu cầu về một mặt phẳng quan sát chung (Shared Observability Plane):** Cần một cơ chế tự động hóa cho phép chạy API với các bài báo học thuật chuẩn (Golden Papers Dataset), đối chiếu với dữ liệu chuẩn (Ground Truth), lưu giữ cả Input và Output theo cấu trúc tinh gọn vào tệp báo cáo Markdown (`.md`) song song với tệp chỉ số máy đọc (`eval_metrics.json`). Cơ chế này giúp cả kỹ sư, AI Agent và đường ống CI/CD có chung một lăng kính quan sát, đánh giá chất lượng và phát hiện lỗi hồi quy tức thì ngay trên Git repo.

---

## 2. Sự Khác Biệt Bản Chất: Bản Thiết Kế Cũ vs Phương Pháp Chuẩn Hóa Hiện Tại

Bản thiết kế ban đầu (bản cũ) chưa tuân theo phương pháp này, mà tiếp cận theo hướng sơ khai: nhúng trực tiếp toàn bộ chuỗi phản hồi thô (Raw JSON payload) vào trong tệp Markdown để người và AI đọc thủ công. 

Sự khác biệt bản chất giữa thiết kế cũ và phương pháp chuẩn hóa hiện tại thể hiện rõ qua các điểm sau:

* **Vị trí lưu trữ dữ liệu thô (Raw Payload Storage):**
  * *Bản cũ:* Ghi trực tiếp toàn bộ dữ liệu thô vào mục `#### Payload Phản Hồi Thực Tế (Raw Output Payload): \`\`\`json ... \`\`\`` ngay trong tệp `docs/eval-reports/<api_name>.md`. Nếu file PDF dài 20–30 trang, tệp Markdown này sẽ nặng từ 2–5 MB với hàng chục nghìn dòng JSON.
  * *Phương pháp mới:* Áp dụng mô hình tách biệt hai tầng (**Two-Tier Data Separation**). Tệp `.md` chỉ lưu bảng tóm tắt chỉ số định lượng, các cảnh báo linter và 3–5 mẫu lỗi đại diện (luôn duy trì < 50 KB). Toàn bộ raw JSON được chuyển sang lưu riêng tại `tests/.artifacts/<api_name>/<paper_id>.json` (được đưa vào `.gitignore`).

* **Cơ chế đánh giá dữ liệu của AI:**
  * *Bản cũ:* Kỳ vọng AI Agent mở và đọc trực tiếp tệp Markdown chứa toàn bộ raw JSON để tự phân tích chất lượng. Cách làm này gây tràn cửa sổ ngữ cảnh (ngốn 50.000–100.000 tokens/lần đọc), dễ gây hiện tượng ảo giác, đếm sót phần tử và tính nhầm phép chia số học.
  * *Phương pháp mới:* Chuyển 100% nhiệm vụ tính toán số học nặng sang mã nguồn Python (**Code-as-a-Judge**). Script `eval_api.py` duyệt qua raw JSON để tính chính xác tuyệt đối Recall, Precision, Spatial IoU và lọc lỗi. AI Agent chỉ đọc bản chẩn đoán vĩ mô tinh gọn trong file `.md`, và chỉ truy vấn lát cắt dữ liệu nhỏ (Surgical Inspection qua `jq` hoặc Python) khi cần gỡ lỗi.

* **Tính khách quan của việc đánh giá (Ground Truth vs Completeness):**
  * *Bản cũ:* Chỉ tính toán các chỉ số hoàn thiện nội tại (Completeness Heuristics) dựa trên những gì parser tự tìm thấy (ví dụ: parser tìm được 20 mục và cả 20 mục đều có năm -> báo "100% Đạt chuẩn", dù thực tế bài báo có 35 mục).
  * *Phương pháp mới:* Bắt buộc đối chiếu với tệp chuẩn ngoại quan `data/papers/<paper_id>.expected.json` thông qua thuật toán **Cascading Matcher** (DOI/arXiv -> Token Jaccard >= 0.85 + Năm) để đo đạc chính xác độ phủ (Recall) và độ chuẩn (Precision).

* **Kiểm toán hình học Bounding Box (Visual Grounding):**
  * *Bản cũ:* Hoàn toàn bỏ quên việc đánh giá tính chính xác của tọa độ `[x0, y0, x1, y1, page]`, chỉ kiểm tra các trường chữ.
  * *Phương pháp mới:* Đưa thêm rào chặn **Spatial IoU Gate (>= 0.70)** vào script để đảm bảo tọa độ highlight không bị vẽ lệch khỏi vùng văn bản trên PDF.js Canvas.

* **Cách ly dữ liệu và đồng bộ tác vụ ngầm:**
  * *Bản cũ:* Dùng tài khoản kiểm thử cố định (`user_id = test-evaluator-uuid`), không có cơ chế chờ tác vụ bất đồng bộ `202 Accepted` hoàn tất, dễ gây xung đột dữ liệu (Flaky tests) khi chạy song song.
  * *Phương pháp mới:* Sinh **Ephemeral Session Tenant UUID** cho mỗi lần chạy, tích hợp **Deterministic Polling Barrier** để đợi trạng thái `completed`, và dọn dẹp khép kín qua chuẩn REST API `DELETE /api/v1/documents/{id}`.

---

## 3. Ngăn Chặn Rủi Ro AI Gian Lận (Reward Hacking & Hallucinated Success)

Rủi ro AI Agent "gian lận" khi được giao nhiệm vụ phải đạt "Pass" hoặc hoàn thành một file báo cáo là hoàn toàn có thật trong kỹ nghệ phần mềm tự động (AI có xu hướng sửa đè markdown, sửa lén `.expected.json` hoặc mock ngầm dữ liệu để báo cáo xanh đẹp mà không chạy API thật). Hệ thống VeriScholar thiết lập **4 Rào Chặn Kỹ Thuật Độc Lập** để triệt tiêu hoàn toàn rủi ro này:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              BỐN RÀO CHẶN CHỐNG GIAN LẬN (ANTI-CHEAT INVARIANTS)             │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ 1. Ground Truth Lock     │ Git Status Check: Cấm sửa lén .expected.json.    │
│    (Chống sửa đối chứng) │ Chỉ khi có cờ --bless mới cho phép cập nhật.     │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 2. SHA-256 Checksums     │ Mã băm SHA-256 của Raw Payload nhúng trực tiếp   │
│    (Chống Fake Report)   │ vào Audit Header; CI đối soát với file đĩa.      │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 3. Code-as-a-Judge Gate  │ Không tin markdown; CI chấm trực tiếp bằng code  │
│    (Chống ảo giác số học)│ Python và file JSON; Recall < 0.90 -> Exit 1.    │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 4. Hermetic Rest DB Pure │ Xóa tài liệu qua DELETE /documents/{id} thật.     │
│    (Chống Mock ngầm DB)  │ Kiểm tra cascade Storage Blob ref-count thực tế. │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

1. **Rào Chặn 1: Khóa Bất Biến Ground Truth (Ground Truth Immutability via Git & `--bless`):**
   - Mọi tệp đối chứng `data/papers/*.expected.json` và `golden_eval_dataset.json` được đưa vào Git tracking.
   - Hàm `check_ground_truth_integrity()` trong `scripts/eval_api.py` tự động chạy `git status --porcelain -- data/papers/`.
   - Nếu phát hiện tệp `.expected.json` bị chỉnh sửa hoặc xóa mà không có cờ tường minh `--bless`, script lập tức hủy thực thi với mã `exit code 2` kèm cảnh báo vi phạm bảo mật (*Anti-Tampering Integrity Violation*).
2. **Rào Chặn 2: Chữ Ký Băm Mật Mã SHA-256 (Cryptographic Payload Checksums in Audit Header):**
   - Toàn bộ raw JSON payload lưu tại `tests/.artifacts/` đều được tính mã băm SHA-256 (`calculate_file_sha256()`).
   - Bảng mã băm SHA-256 được nhúng trực tiếp vào phần Audit Header ở đầu mỗi tệp báo cáo Markdown.
   - Khi CI chạy kiểm tra, mã băm này được đối chiếu trực tiếp với payload vật lý thực tế, ngăn ngừa hành vi AI tự tay viết đè nội dung file Markdown để báo cáo "xanh".
3. **Rào Chặn 3: Trọng Tài Mã Nguồn Độc Lập (Independent Code-as-a-Judge & Exit Codes):**
   - Không dựa vào nội dung văn bản tự do của Markdown để kết luận hệ thống đạt chuẩn.
   - Bổ sung tệp kiểm thử tự động `tests/evals/test_eval_metrics.py` nạp tệp chỉ số `tests/.artifacts/eval_metrics.json` để kiểm tra bằng các câu lệnh `assert` nghiêm ngặt:
     - `assert metrics["cascading_recall"] >= 0.90`
     - `assert metrics["cascading_precision"] >= 0.95`
     - `assert metrics["spatial_iou"] >= 0.70`
     - `assert metrics["critical_linter_warnings"] == 0`
   - Nếu vi phạm bất kỳ điều kiện nào, tiến trình kiểm thử thoát với `exit code 1`, lập tức chặn đứng mã nguồn bẻ gãy hệ thống trước khi được merge vào nhánh chính.
4. **Rào Chặn 4: Kiểm Thử Vòng Đời REST Khép Kín (Hermetic REST Lifecycle vs Database Mocking):**
   - Tuyệt đối cấm can thiệp trực tiếp vào database bằng câu lệnh ORM/SQL ngầm hoặc Mock để tạo trạng thái giả.
   - Mọi quy trình kiểm thử bắt buộc đi qua đúng cổng REST API công khai:
     1. `POST /api/v1/documents` để tải file lên.
     2. `POST /api/v1/documents/{id}:parse` để khởi chạy pipeline.
     3. `GET /api/v1/documents/{id}/status` chờ hoàn tất.
     4. `DELETE /api/v1/documents/{id}` để xóa tài liệu sau khi kiểm thử xong.
   - Kiểm tra cả hiệu ứng phụ (side-effects): Khi tài liệu bị xóa, bản ghi trong bảng `documents` phải mất, và nếu không còn tham chiếu nào khác tới `content_hash`, tệp vật lý tương ứng trong thư mục `storage/` cũng phải được thu hồi tự động (CAS Zero-Leakage Invariant).

---

## 4. 11 Bất Biến Của Hệ Thống Đánh Giá (Core System Invariants)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 11 BẤT BIẾN ĐÁNH GIÁ HỆ THỐNG (SYSTEM INVARIANTS)           │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ 1. Cascading F1 Matcher  │ 2 Tầng: DOI/arXiv -> Token Jaccard >= 0.85 + Năm. │
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
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 9. Query Log & Isolation │ Tách riêng SQL_ECHO=false; logger engine WARNING;│
│    (Database Hygiene)    │ Hỗ trợ --keep-data, --user-id và tách môi trường.│
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 10. Output Temp & Clean  │ Báo cáo lưu cố định tại temp/output/test/*.md;   │
│     (Snapshot Storage)   │ Tự động kiểm tra và làm mới sạch trước khi chạy. │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 11. Dual-View & Folding  │ Terminal: HTTP Box gọn, chống đơ nhị phân/vector;│
│     (Smart Terminal UI)  │ Markdown: Giữ trọn 100% full raw JSON gốc.       │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

### 4.1. Thuật Toán Khớp Xếp Tầng (Cascading Matcher: Token Jaccard)

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
        tokens_a = set(re.findall(r"\w+", title_a.lower()))
        tokens_b = set(re.findall(r"\w+", title_b.lower()))
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))


    def is_reference_match(
        ext: dict[str, Any], exp: dict[str, Any], jaccard_threshold: float = 0.85
    ) -> bool:
        # Tầng 1: Khớp định danh vĩnh viễn (Deterministic ID Match)
        if ext.get("doi") and exp.get("doi"):
            if ext["doi"].lower().strip() == exp["doi"].lower().strip():
                return True
        if ext.get("arxiv_id") and exp.get("arxiv_id"):
            if ext["arxiv_id"].lower().strip() == exp["arxiv_id"].lower().strip():
                return True

        # Tầng 2: Khớp ngữ nghĩa tập từ vựng kèm rào chắn năm (Semantic Jaccard + Year Guard)
        title_sim = token_jaccard_similarity(
            ext.get("title", ""), exp.get("title", "")
        )
        if title_sim >= jaccard_threshold:
            # Nếu cả 2 đều có năm xuất bản, năm phải trùng nhau
            ext_year = ext.get("year")
            exp_year = exp.get("year")
            if ext_year and exp_year and str(ext_year) != str(exp_year):
                return False
            return True

        return False
```

---

### 4.2. Kiểm Toán Hình Học Không Gian Bounding Box (Spatial IoU Gate)

- **Mục đích:** Đảm bảo khi người dùng bấm vào một citation trong báo cáo nghiên cứu, tài liệu PDF phía bên trái phải tự động cuộn và highlight **chính xác 100%** vào đúng khối văn bản gốc.
- **Thuật toán IoU (Intersection over Union) 2D:**
  $$\text{IoU} = \frac{\text{Area}(\text{Box}_{\text{pred}} \cap \text{Box}_{\text{gt}})}{\text{Area}(\text{Box}_{\text{pred}} \cup \text{Box}_{\text{gt}})}$$
- **Rào chắn chất lượng (Quality Gate):**
  - Khớp hình học đạt chuẩn nếu $\text{IoU} \ge 0.70$ và cùng số trang `page_number`.
  - Nếu $\text{IoU} < 0.70$, cảnh báo `LINTER_WARNING_MISALIGNED_BBOX` được ghi nhận vào báo cáo Markdown và làm giảm điểm Visual Grounding Score.

---

### 4.3. Quản Lý Vòng Đời Dữ Liệu Khép Kín (Hermetic REST Cleanup vs Seed Data Mode)

- **Mặc định:** Mọi tài liệu PDF tải lên trong quá trình chạy snapshot runner đều được theo dõi danh sách `created_document_ids` và được dọn dẹp triệt để thông qua lệnh gọi `DELETE /api/v1/documents/{document_id}` ở khối `finally`.
- **Cờ `--keep-data`:** Cho phép kỹ sư giữ lại dữ liệu tài liệu trên môi trường phát triển cục bộ để trực tiếp mở trình duyệt (Swagger UI hoặc Frontend React) nhằm quan sát giao diện người dùng thực tế sau khi runner kết thúc.
- **Rào chắn bảo vệ dữ liệu Seed chuẩn (Seed Data Protection Invariant):**
  - Khi runner chạy ở chế độ sử dụng tài liệu gốc mẫu (`--paper 1706.03762v7.pdf`), hệ thống **tuyệt đối không xóa** dữ liệu gốc nếu tài liệu đó đã được đánh dấu là Seed Data của dự án.
  - Runner tự động kiểm tra `is_seed_paper` để chỉ dọn dẹp các tài liệu tạm (ephemeral test documents) sinh ra trong phiên kiểm thử hiện tại.

---

### 4.4. Mô Hình Kiểm Thử Không Tốn Chi Phí (Zero-Cost VCR Cloud Replay)

- **Vấn đề:** Việc gọi trực tiếp Azure Form Recognizer, MathPix OCR và OpenAI Text Embedding mỗi khi chạy snapshot runner sẽ làm tăng chi phí API và gây chậm trễ đường ống CI/CD (mỗi lượt chạy có thể tốn từ \$0.10 đến \$0.50).
- **Giải pháp VCR Replay:**
  - Mọi phản hồi mạng bên ngoài (Outbound HTTP Requests) đối với các bài báo chuẩn trong `data/papers/` đều được ghi hình cassette nhị phân tại `tests/fixtures/vcr_cassettes/`.
  - Khi chạy mặc định `python scripts/eval_api.py`, mạng bên ngoài bị vô hiệu hóa hoàn toàn, hệ thống phát lại dữ liệu từ Cassette với thời gian thực thi $< 500\text{ms}$ và chi phí \$0.
  - Khi cần cập nhật mô hình mới hoặc chạy kiểm tra thực tế, kỹ sư kích hoạt cờ `--live-cloud` để kết nối API trực tiếp và cập nhật lại Cassette.

---

### 4.5. Cơ Chế Cập Nhật Baseline Tự Động (Snapshot Blessing Pattern)

- **Nguyên lý:** Khi thuật toán trích xuất thực thể hoặc visual grounding được tối ưu hóa vượt bậc (ví dụ: bóc tách được thêm 3 tài liệu tham khảo chuẩn mà trước đây bị sót), các chỉ số kiểm thử có thể tạm thời báo lệch so với `expected.json` cũ.
- **Quy trình chuẩn hóa:**
  1. Kỹ sư chạy runner với cờ `--bless`:
     ```bash
     uv run python scripts/eval_api.py --api extract_refs --bless
     ```
  2. Runner kiểm tra xem các cải tiến có thực sự hợp lệ hay không (không làm giảm độ chính xác tổng thể).
  3. Nếu hợp lệ, runner tự động cập nhật lại tệp `data/papers/<paper_id>.expected.json` với dữ liệu mới và in ra thông báo tóm tắt các điểm khác biệt (Diff summary).
  4. Mọi thao tác cập nhật bằng `--bless` đều phải được review qua Git Diff trước khi commit vào kho mã nguồn chung.

---

### 4.6. Rào Chặn Đồng Bộ Trạng Thái Cho Endpoint Bất Đồng Bộ `202 Accepted` (Deterministic Polling Barrier)

- **Vấn đề:** Các endpoint xử lý nặng như bóc tách tài liệu (`POST /api/v1/documents/{document_id}:parse`) trả về ngay lập tức mã `HTTP 202 Accepted` kèm tác vụ chạy ngầm Celery/Redis. Nếu runner vội vàng gọi ngay endpoint kết quả sẽ nhận về `404` hoặc dữ liệu rỗng (Race Condition).
- **Giải pháp chuẩn hóa:**
  - Bổ sung cơ chế thăm dò đồng bộ xác định (**Deterministic Polling Barrier**):
  - Runner tự động lắng nghe `GET /api/v1/documents/{document_id}/status` theo chu kỳ $200\text{ms}$ với cơ chế timeout lũy kế ($T_{\text{max}} = 60\text{s}$).
  - Chỉ khi trạng thái chuyển sang `completed`, runner mới tiến hành đánh giá chất lượng; nếu trạng thái chuyển sang `failed`, runner lập tức trích xuất thông báo lỗi chi tiết và báo cáo thất bại với nguyên nhân rõ ràng.

---

### 4.7. Rào Chặn Tín Hiệu Ngắt An Toàn (Signal-Safe Cancellation)

- **Vấn đề:** Khi kỹ sư nhấn `Ctrl+C` (SIGINT) hoặc hệ thống CI/CD gửi tín hiệu kết thúc (SIGTERM), tiến trình Python có thể bị ngắt đột ngột giữa chừng, để lại các tài liệu rác mồ côi trong cơ sở dữ liệu và ổ cứng (Database & Storage Leaks).
- **Giải pháp chuẩn hóa:**
  - Script runner đăng ký bộ đón nhận tín hiệu `signal.signal(signal.SIGINT, ...)` và `signal.SIGTERM`.
  - Khi nhận tín hiệu dừng, tiến trình không thoát ngay lập tức mà kích hoạt cơ chế dọn dẹp khẩn cấp (**Graceful REST Evacuation**), thực hiện gọi `DELETE` toàn bộ các tài liệu đã tạo trước khi chính thức trả quyền điều khiển về hệ điều hành.

---

### 4.8. Kiến Trúc Dual-Output & Quality Budget Cho Đường Ống CI/CD

Để phục vụ song song cả hai đối tượng: **Kỹ sư/AI Agent** (cần báo cáo trực quan, dễ đọc) và **Hệ thống CI/CD Automation** (cần kiểm tra điều kiện cứng để quyết định cho phép merge code), hệ thống snapshot tạo ra đồng thời hai định dạng đầu ra:
1. **Báo cáo Markdown Trực Quan (`temp/output/test/<api_name>.md`):**
   - Dung lượng luôn $< 50\text{ KB}$.
   - Chứa bảng tóm tắt chỉ số, các vi phạm linter và các trường hợp biên quan trọng.
   - Được cập nhật liên tục để kỹ sư đối soát nhanh mà không làm tràn Context Window của LLM.
2. **Tệp Định Lượng Máy Đọc (`tests/.artifacts/eval_metrics.json`):**
   - Lưu trữ các chỉ số thô: `recall`, `precision`, `spatial_iou`, `p95_latency_ms`, `error_count`.
   - Đường ống CI/CD sử dụng một bước kiểm tra chuẩn (Quality Budget Assertion):
     ```bash
     uv run pytest tests/evals/test_eval_metrics.py
     ```
   - Nếu bất kỳ chỉ số nào thấp hơn ngưỡng tối thiểu (`min_recall = 0.90`, `min_precision = 0.95`, `min_spatial_iou = 0.70`), build pipeline sẽ bị đánh trượt ngay lập tức (Exit Code 1).

---

### 4.9. Phân Tách Môi Trường & Kiểm Soát Log Truy Vấn (Environment Isolation & Query Log Hygiene)

- **Vấn đề:** Khi chạy script đánh giá chất lượng tự động, SQLAlchemy và HTTP client có thể in ra hàng nghìn dòng log truy vấn SQL thô (`SQL_ECHO=true`) và log HTTP request làm tràn ngập màn hình Terminal, che khuất bảng tóm tắt kết quả kiểm thử và làm nhiễu thông tin mà AI Agent cần quan sát.
- **Giải pháp chuẩn hóa:**
  - Mặc định thiết lập mức độ log sạch sẽ (**Log Hygiene**): tắt `SQL_ECHO`, đặt logger của SQLAlchemy engine và httpx ở mức `WARNING`.
  - Hỗ trợ tham số `--verbose` hoặc `--debug-sql` để chỉ bật log truy vấn chi tiết khi kỹ sư cần điều tra sâu nguyên nhân tắc nghẽn hiệu năng hoặc lỗi ràng buộc cơ sở dữ liệu.
  - Tách biệt hoàn toàn cơ sở dữ liệu kiểm thử (sử dụng schema hoặc tên database riêng biệt) để không ảnh hưởng đến dữ liệu đang phát triển trên môi trường cục bộ.

---

### 4.10. Quản Lý Thư Mục Báo Cáo Đầu Ra `temp/output/test/` & Cơ Chế Làm Mới Tệp (File Clean Refresh)

- **Vấn đề:** Việc lưu tệp báo cáo rải rác hoặc ghi đè không kiểm soát dễ dẫn đến việc báo cáo cũ bị đọc nhầm thành kết quả kiểm thử mới, gây hiểu lầm nghiêm trọng trong quá trình đánh giá chất lượng của AI Agent và kỹ sư.
- **Giải pháp chuẩn hóa:**
  - **Quy hoạch thư mục thống nhất:** Toàn bộ các tệp báo cáo đánh giá tự động (`.md`) bắt buộc phải được xuất vào thư mục cố định:
    ```
    temp/output/test/
    ├── post_documents_upload.md
    ├── get_documents_list.md
    ├── get_documents_detail.md
    ├── get_documents_file_stream.md
    ├── get_documents_status.md
    ├── post_documents_star.md
    ├── post_documents_parse.md
    ├── post_documents_extract_references.md
    ├── get_documents_structure.md
    ├── get_documents_chunks.md
    ├── get_documents_chunk_detail.md
    ├── get_documents_summary.md
    ├── post_documents_summary_generate.md
    ├── get_documents_export_pdf.md
    └── delete_documents.md
    ```
  - **Cơ chế Kiểm Tra & Làm Mới Tệp Sạch Sẽ (File Clean Refresh):**
    - Trước khi thực thi bất kỳ runner nào, script sẽ kiểm tra sự tồn tại của tệp báo cáo tương ứng trong `temp/output/test/`.
    - Nếu tệp đã tồn tại, script thực hiện **xóa sạch hoàn toàn** tệp cũ và khởi tạo tệp mới trống rỗng (tránh hiện tượng ghi chắp vá hoặc giữ lại các bảng kết quả của lượt chạy trước).
    - Đảm bảo thư mục `temp/output/test/` tự động được khởi tạo nếu chưa tồn tại (`Path.mkdir(parents=True, exist_ok=True)`).
    - Thư mục `temp/` được cấu hình trong `.gitignore` để tránh commit nhầm các tệp báo cáo thử nghiệm tạm thời vào Git repo chính.

---

### 4.11. Hiển Thị Trực Quan Đóng Khung Trên Terminal & Xử Lý Payload Lớn (In-Terminal HTTP Exchange & Smart Payload Folding)

- **Vấn đề:** Khi kỹ sư hoặc AI Agent thực thi lệnh `python scripts/eval_api.py`, nếu terminal chỉ hiển thị thanh tiến trình đơn điệu hoặc ngược lại, tuôn ra hàng nghìn dòng JSON thô không định dạng, người dùng sẽ không nắm bắt được dữ liệu trao đổi HTTP thực tế giữa client và server. Đặc biệt với các API trả về file nhị phân (như stream PDF) hoặc vector nhúng 1536 chiều, việc in toàn bộ ra terminal sẽ làm đơ (freeze) cửa sổ dòng lệnh.
- **Giải pháp chuẩn hóa (In-Terminal HTTP Exchange Box):**
  - Đối với mỗi API được kiểm thử, script runner in ra trực tiếp một **Khung Trực Quan Đóng Hộp (Formatted Terminal Box)** hiển thị đầy đủ ngữ cảnh HTTP:
    ```text
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ HTTP REQUEST: POST /api/v1/documents/:extract-references                     │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ Headers: Content-Type: application/json | x-user-id: test_eval_3229942d      │
    │ Body: {"paper": "1706.03762v7.pdf", "min_confidence": 0.85}                │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ HTTP RESPONSE: 200 OK (Latency: 169.2 ms)                                   │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ Headers: content-type: application/json; charset=utf-8 | x-request-id: ...  │
    │ Body: {                                                                     │
    │   "success": true,                                                          │
    │   "data": {                                                                 │
    │     "references_count": 40,                                                 │
    │     "items": [ ... 40 items folded ... ]                                    │
    │   }                                                                         │
    │ }                                                                           │
    └─────────────────────────────────────────────────────────────────────────────┘
    ```
  - **Thuật toán Thu Gọn Thông Minh (Smart Payload Folding):**
    - **Dữ liệu nhị phân (Binary Stream):** Tự động phát hiện `Content-Type: application/pdf` hoặc `application/octet-stream` và thay thế nội dung hiển thị bằng tóm tắt kích thước: `[Binary Stream: 2,458,120 bytes, MIME: application/pdf]`.
    - **Mảng vector / danh sách dài:** Nếu mảng JSON chứa hơn 3 phần tử, chỉ hiển thị 2 phần tử đầu và 1 phần tử cuối, phần giữa được thu gọn thành `[... 37 items folded ...]`.
    - **Đảm bảo tính vẹn toàn:** Việc thu gọn chỉ áp dụng cho hiển thị tại Terminal để bảo vệ trải nghiệm người dùng; trong tệp JSON lưu trữ tại `tests/.artifacts/`, dữ liệu phản hồi luôn được giữ trọn vẹn 100% không bị cắt xén.

---

## 5. Chiến Lược Tập Dữ Liệu Chuẩn (Golden Papers Dataset)

Tập dữ liệu đối chứng được tổ chức tại thư mục `data/papers/` với các bài báo khoa học chuẩn đại diện cho đầy đủ các thách thức thực tế:

| Nhóm Tài Liệu | Tệp PDF & Expected JSON | Đặc Điểm Thử Nghiệm | Mục Tiêu Đánh Giá |
| :--- | :--- | :--- | :--- |
| **1. Conference 2-Column** | `1706.03762v7.pdf`<br>`1706.03762v7.expected.json` | 15 trang, bố cục 2 cột NeurIPS, nhiều công thức Toán LaTeX, trích dẫn dạng bracket `[1]`. | Kiểm tra khả năng đọc đúng thứ tự cột, không trộn lẫn văn bản giữa 2 cột song song. |
| **2. Long Preprint LNCS** | `2504.19754v1.pdf`<br>`2504.19754v1.expected.json` | 24 trang, phong cách Springer LNCS (tác giả cách nhau bằng dấu hai chấm `: `), URL ngắt dòng. | Kiểm tra thuật toán bóc tách tài liệu tham khảo, chuẩn hóa URL ngắt dòng và loại bỏ running header. |
| **3. Fast Smoke Sample** | `sample_short_paper.pdf`<br>`sample_short_paper.expected.json` | 2 đến 3 trang, dung lượng nhẹ (< 500 KB). | Dùng cho Tầng 1 (Smoke Snapshot) chạy nhanh < 15 giây trên CI/CD pipeline. |
| **4. Scanned PDF (OCR)** | `scanned_sample_noisy.pdf`<br>`scanned_sample_noisy.expected.json` | Tệp PDF dạng ảnh quét đen trắng mờ, không có text layer số hóa. | Kiểm chứng nhánh Fallback OCR qua VCR Replay Fixture (hoặc Live Azure nếu bật cờ `--live-cloud`). |
| **5. Corrupted Header** | `corrupted_structure.pdf` | Tệp nhị phân hỏng cấu trúc `%PDF-`. | Xác thực mã lỗi `422 UNSUPPORTED_PDF_FORMAT`. |
| **6. Truncated Binary** | `truncated_eof.pdf` | Bị ngắt giữa chừng, thiếu tag `%%EOF`. | Xác thực mã lỗi `422 CORRUPTED_PDF_PAYLOAD`. |
| **7. Multi-column Math** | `complex_math_symbols.pdf` | Chứa ma trận, tích phân nhiều lớp và ký hiệu Hy Lạp. | Đảm bảo MathPix / Marker adapter không làm vỡ ký tự Unicode trong chunk văn bản. |

---

## 6. Danh Mục 12 Endpoints API Kiểm Thử (Module 1: Ingestion & Deep Read)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MODULE 1: INGESTION & DEEP READ - ENDPOINTS MATRIX          │
├──────┬────────┬─────────────────────────────────────┬───────────────────────┤
│ STT  │ Method │ Đường dẫn Endpoint REST             │ Nhiệm Vụ & Quality Gate│
├──────┼────────┼─────────────────────────────────────┼───────────────────────┤
│  1   │ POST   │ /api/v1/documents                   │ Upload PDF & CAS Dedupl│
│  2   │ GET    │ /api/v1/documents                   │ Danh sách phân trang   │
│  3   │ GET    │ /api/v1/documents/{document_id}     │ Chi tiết & Bounding Box│
│  4   │ GET    │ /api/v1/documents/{document_id}/file│ Stream nhị phân chunked│
│  5   │ GET    │ /api/v1/documents/{document_id}/stat│ Tiến độ Pipeline (0-100│
│  6   │ POST   │ /api/v1/documents/{document_id}:star│ Đánh dấu tài liệu sao  │
│  7   │ POST   │ /api/v1/documents/{document_id}:pars│ Trigger bóc tách & RAG │
│  8   │ POST   │ /api/v1/documents/{id}:extract-refs │ Bóc tách tham khảo & F1│
│  9   │ DELETE │ /api/v1/documents/{document_id}     │ Xóa sạch & Zero Leakage│
│  10  │ GET    │ /api/v1/documents/{id}/summary      │ Grounded Summary (<10ms)│
│  11  │ POST   │ /api/v1/documents/{id}/summary:gen  │ Custom Method Generate │
│  12  │ POST   │ /api/v1/documents/{id}/summary:str  │ Real-Time SSE Token Str│
│  13  │ GET    │ /api/v1/documents/{id}/export-pdf   │ ISO 32000 PDF Annotate │
│  14  │ MULTI  │ /api/v1/notes/* (#16 - #21)         │ Sổ tay & AI Tổng hợp   │
│  15  │ POST   │ /api/v1/sessions                    │ Khởi tạo phiên (#45)   │
│  16  │ GET    │ /api/v1/sessions                    │ Lịch sử Sidebar (#46)  │
│  17  │ GET    │ /api/v1/sessions/{id}               │ Chi tiết phiên (#47)   │
│  18  │ DELETE │ /api/v1/sessions/{id}               │ Xóa phiên (#50)        │
│  19  │ PATCH  │ /api/v1/sessions/{id}/viewport      │ Cập nhật Viewport (#49)│
│  20  │ POST   │ /api/v1/sessions/{id}/documents     │ Nạp bài vào phiên (#51)│
│  21  │ POST   │ /api/v1/sessions/{id}/messages      │ Stream SSE & Q&A (#52) │
│  22  │ MULTI  │ /api/v1/sessions/* (#48, #53 - #55) │ Lifecycle & Sessions   │
└──────┴────────┴─────────────────────────────────────┴───────────────────────┘
```

---

## 7. Mẫu Báo Cáo Markdown Đầu Ra Điển Hình

Dưới đây là cấu trúc tệp báo cáo mẫu được sinh ra tại `temp/output/test/post_documents_extract_references.md`:

````markdown
# API Evaluation Snapshot: POST /api/v1/documents/{document_id}:extract-references

> **Audit Header**: Session Tag: `test_eval_3229942d` | Mode: Golden Dataset Cascading Matcher  
> **Target Output**: `temp/output/test/post_documents_extract_references.md`  
> **Payload Checksums (SHA-256)**:  
> - `doc_1706.03762v7_references.json`: `380f3a107c00f119c05a376c17d0c5bc8c434af6eb3cf97556831b8ecc09ecb1`  
> - `doc_2504.19754v1_references.json`: `1a7113e019fd426ac85f3daa2c00347f9aeae0bc1d89450e3900274dbf51cba4`  
> **Quality Gate**: **PASSED** (Recall >= 90%, Precision >= 95%)

---

## 1. Executive Summary & Ground Truth Verification

| Scenario | Status | Latency | Extracted / Expected | Recall | Precision | Quality Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Reference Parsing (1706.03762v7.pdf) | `200` | 169.2 ms | 40 / 40 | 100.0% | 100.0% | PASS |
| Reference Parsing (2504.19754v1.pdf) | `200` | 47.5 ms | 20 / 20 | 100.0% | 95.0% | PASS |

---

## 2. Zero-Token Semantic Linter Log
- `[OK]` All extracted references passed semantic validity heuristics.

---

## 3. Invariants & Contract Adherence
- **Cascading Matcher**: Resolves via Tier 1 (DOI/arXiv) and Tier 2 (Token Jaccard >= 0.85 + Year).
- **Zero Hallucination / Anti-Tampering**: Precision directly maps to actual GT identifiers.
- **Hermetic Lifecycle**: Ephemeral test documents cascade and purge cleanly upon evaluation exit.
````

---

### 7.2. Snapshot Mẫu: POST /api/v1/sessions (#45 Khởi tạo phiên nghiên cứu)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/post_sessions_create.md`:

````markdown
# API Evaluation Snapshot: POST /api/v1/sessions

> **Audit Header**: Session Tag: `test_eval_02b3acb3` | Target: `#45 Khởi tạo phiên nghiên cứu đa bài mới`  
> **Target Output**: `temp/output/test/post_sessions_create.md`  
> **Payload Checksums (SHA-256)**:  
> - `create_valid_session_201.json`: `1a49508e9bcb3a78c2a870f659098b69132de8798ac445ea170db68bdaf9c274`  
> - `create_empty_session_201.json`: `bf3857f717e658ef0d1de565660e22ae7c5b838a3d0a8c057b1f932bd1ab1a88`  
> - `capacity_guard_exceeded_400.json`: `09336f18ad41f18c5688fb4e2ff028627ab09a0165efba4db6e8fae150053aab`  
> - `dedup_documents_201.json`: `9a19a29654faed1757edc850a8015e4ebb085b211decc4ff6e883bd11e4a64a2`  
> - `nonexistent_document_404.json`: `9616a0eb72f3ba54314195e91714ee8e968f8e21212a932c2939c6f50effa10a`  
> - `whitespace_title_422.json`: `cf88e23a639dad1abc621fcc9bc908cf3dd78ff985259b4161362eafc722fd1b`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Create Session with Valid Documents (201 Created) | `201` | `201` | 28.1ms | PASS | Initialized session with active doc, default canvas viewport, Location & ETag headers |
| Create Empty Session (201 Created) | `201` | `201` | 12.2ms | PASS | Empty document set cleanly handled with null active_document_id |
| Auto-naming Fallback when Title is Null | `201` | `201` | 14.5ms | PASS | Automatically generated descriptive title from first document |
| Idempotency Protection (Idempotency-Key) | `200` | `200` | 2.1ms | PASS | Replayed identical key returning cached session with X-Cache: Idempotent-Hit |
| Embedded Document Metadata (include_documents=true) | `201` | `201` | 15.0ms | PASS | Embedded rich document metadata and status warnings without extra requests |
| Capacity Guard Exceeded (Expect HTTP 400) | `400` | `400` | 6.8ms | PASS | Blocked > 5 papers with 400 (SESSION_CAPACITY_EXCEEDED) |
| Duplicate Document Deduplication (201 Created) | `201` | `201` | 11.7ms | PASS | Deduplicated repeated document IDs while maintaining sequential order |
| Nonexistent Document Guard (Expect HTTP 404) | `404` | `404` | 6.0ms | PASS | Blocked unowned or missing document ID with 404 (DOCUMENT_NOT_FOUND) |
| Validation Guard Whitespace Title (Expect HTTP 422) | `422` | `422` | 3.5ms | PASS | Pydantic validator blocked whitespace-only string with 422 |

---

## 2. Invariants & Contract Adherence
- **RFC 7231 & 201 Invariants**: Headers `Location: /api/v1/sessions/{id}` và `ETag: "v1"` kiểm soát đồng thời lạc quan.
- **Active Document Invariant**: Tự động gán tài liệu đầu tiên nạp vào làm active document.
- **Capacity Guard Invariant**: Giới hạn tối đa 5 tài liệu/phiên, vượt quá trả về 400 `SESSION_CAPACITY_EXCEEDED`.
- **Hermetic Lifecycle**: Cascade purge sạch tài liệu qua REST API chuẩn sau khi đánh giá.
````

---

### 7.3. Snapshot Mẫu: GET /api/v1/sessions (#46 Lấy lịch sử các phiên nghiên cứu)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/get_sessions_list.md`:

````markdown
# API Evaluation Snapshot: GET /api/v1/sessions

> **Audit Header**: Session Tag: `test_eval_a3f8019b` | Target: `#46 Lấy lịch sử các phiên nghiên cứu (Sidebar History)`  
> **Target Output**: `temp/output/test/get_sessions_list.md`  
> **Payload Checksums (SHA-256)**:  
> - `01_default_pagination.json`: `a4f9018e9bcb3a78c2a870f659098b69132de8798ac445ea170db68bdaf9c274`  
> - `02_strict_page_slicing.json`: `b5c127f717e658ef0d1de565660e22ae7c5b838a3d0a8c057b1f932bd1ab1a88`  
> - `03_search_title_keyword.json`: `c6d8336f18ad41f18c5688fb4e2ff028627ab09a0165efba4db6e8fae150053aab`  
> - `04_archive_status_filter.json`: `d7e219a29654faed1757edc850a8015e4ebb085b211decc4ff6e883bd11e4a64a2`  
> - `05_multi_tenant_isolation.json`: `e8f560eb72f3ba54314195e91714ee8e968f8e21212a932c2939c6f50effa10a`  
> - `06_validation_bounds_guard.json`: `f9a78e23a639dad1abc621fcc9bc908cf3dd78ff985259b4161362eafc722fd1b`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Default Paginated Listing (page=1, per_page=20) | `200` | `200` | 8.2ms | PASS | SessionHistoryEnvelope returned with valid meta, links, and updated_at DESC order |
| Strict Page Slicing & Boundary Links (page=1..2, per_page=2) | `200` | `200` | 7.5ms | PASS | Exact page slicing with disjoint ID sets and valid RFC 8288 next/prev navigation |
| Case-Insensitive Title Keyword Search (q=...) | `200` | `200` | 6.8ms | PASS | Substring search returned only matching session titles |
| Archive Status Segregation (include_archived=false/true) | `200` | `200` | 7.1ms | PASS | Archived sessions omitted by default and included when flag is active |
| Multi-Tenant User Isolation Guard | `200` | `200` | 5.9ms | PASS | Strictly zero data leakage across distinct authenticated user sessions |
| Query Validation Bounds Guard (page=0, per_page=101) | `422` | `422` | 3.2ms | PASS | Pydantic query validator rejected out-of-bounds parameters |

---

## 2. Invariants & Contract Adherence
- **RFC 8288 Pagination Invariant**: Header/body `links` (`first`, `prev`, `self`, `next`, `last`) tuân thủ chuẩn Web Linking.
- **Chronological Sorting**: Luôn sắp xếp `updated_at DESC` để phiên mới nhất nổi lên đầu danh sách Sidebar.
- **Tenant Data Shielding**: Dữ liệu phiên được phân lập tuyệt đối theo `user_id`.
- **Hermetic REST Cleanup**: Dọn sạch phiên và tài liệu thử nghiệm khi thoát runner.
````

---

### 7.4. Snapshot Mẫu: GET /api/v1/sessions/{id} (#47 Khôi phục nguyên vẹn phiên)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/get_session_detail.md`:

````markdown
# API Evaluation Snapshot: GET /api/v1/sessions/{id}

> **Audit Header**: Session Tag: `test_eval_b4a10e72` | Target: `#47 Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)`  
> **Target Output**: `temp/output/test/get_session_detail.md`  
> **Payload Checksums (SHA-256)**:  
> - `01_full_session_restoration.json`: `a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `02_etag_header_conformance.json`: `b2c3d4e5f6a17890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `03_empty_session_restoration.json`: `c3d4e5f6a1b27890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `04_multi_tenant_isolation.json`: `d4e5f6a1b2c37890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `05_not_found_guard.json`: `e5f6a1b2c3d47890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `06_validation_bounds_guard.json`: `f6a1b2c3d4e57890123456789abcdef0123456789abcdef0123456789abcdef0`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Full Session Restoration (Snapshots, Tabs, Viewport) | `200` | `200` | 6.5ms | PASS | Complete session restored with viewport_state, documents, and active_tab |
| ETag Header Conformance & OCC Version Lock | `200` | `200` | 4.8ms | PASS | ETag header matches \"v{version}\" and coincides with data.version |
| Empty Session Restoration (No documents attached) | `200` | `200` | 5.2ms | PASS | Empty session schema valid with documents=[] and message_count=0 |
| Multi-Tenant User Isolation Guard (Alien User) | `404` | `404` | 4.1ms | PASS | Alien user rejected with SESSION_NOT_FOUND (Zero Data Leakage) |
| Non-existent Session UUID Guard | `404` | `404` | 3.9ms | PASS | Random UUID returns 404 SESSION_NOT_FOUND |
| Path UUID Format Validation Guard | `422` | `422` | 2.5ms | PASS | Malformed UUID path parameter rejected with HTTP 422 |

---

## 2. Invariants & Contract Adherence
- **OCC ETag Invariant**: Header `ETag` tuân thủ RFC 9110/7232, bọc chuỗi `\"v{version}\"`, sẵn sàng cho thao tác `If-Match`.
- **Complete State Invariant**: Khôi phục đầy đủ `viewport_state` (`page`, `zoom_ratio`, `scroll_top`), `active_tab`, và `documents`.
- **Multi-Tenant Shielding**: Không rò rỉ phiên sang user khác; trả về `404 Not Found` để chống dò quét tài nguyên.
- **Hermetic REST Cleanup**: Dọn sạch session và document sau khi hoàn tất bài đánh giá.
````

---

### 7.5. Snapshot Mẫu: DELETE /api/v1/sessions/{id} (#50 Xóa phiên nghiên cứu)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/delete_session.md`:

````markdown
# API Evaluation Snapshot: DELETE /api/v1/sessions/{id}

> **Audit Header**: Session Tag: `test_eval_e7b9218c` | Target: `#50 Xóa phiên nghiên cứu & Cascade Associations`  
> **Target Output**: `temp/output/test/delete_session.md`  
> **Payload Checksums (SHA-256)**:  
> - `01_delete_session_success.json`: `a2b3c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `02_underlying_document_preserved.json`: `b3c4d5e6f7a2890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `03_cascade_associations_removed.json`: `c4d5e6f7a2b3890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `04_multi_tenant_isolation.json`: `d5e6f7a2b3c4890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `05_idempotent_repeat_delete_guard.json`: `e6f7a2b3c4d5890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `06_validation_bounds_guard.json`: `f7a2b3c4d5e6890123456789abcdef0123456789abcdef0123456789abcdef0`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Clean Session Deletion (HTTP 204 No Content) | `204` | `204` | 6.2ms | PASS | Session deleted cleanly with empty response body |
| Underlying Document Preservation | `200` | `200` | 4.5ms | PASS | Document still intact and accessible in user library after session deletion |
| Cascade Associations Removal Verification | `404` | `404` | 3.8ms | PASS | GET /api/v1/sessions/{id} returns 404 SESSION_NOT_FOUND |
| Multi-Tenant User Isolation Guard (Alien User) | `404` | `404` | 4.1ms | PASS | Alien user cannot delete current user's session (Zero Data Leakage) |
| Idempotent Repeat Delete Guard | `404` | `404` | 3.4ms | PASS | Second DELETE on already purged session returns 404 SESSION_NOT_FOUND |
| Path UUID Format Validation Guard | `422` | `422` | 2.6ms | PASS | Malformed UUID path parameter rejected with HTTP 422 VALIDATION_ERROR |

---

## 2. Invariants & Contract Adherence
- **Clean HTTP 204 Invariant**: Trả về đúng `HTTP 204 No Content` với thân phản hồi rỗng khi xóa thành công.
- **Underlying Document Preservation**: Tuyệt đối không xóa tài liệu gốc trong thư viện người dùng khi xóa phiên.
- **Cascade Removal Invariant**: Xóa xếp chồng sạch sẽ bản ghi phiên trong `research_sessions`, `session_documents`, `session_turns`.
- **Multi-Tenant Shielding**: Trả về `404 SESSION_NOT_FOUND` khi người dùng khác truy cập/xóa phiên trái phép.
- **Hermetic Teardown**: Toàn bộ tài nguyên phục vụ kiểm thử được dọn dẹp khép kín.
````

---

### 7.6. Snapshot Mẫu: PATCH /api/v1/sessions/{id}/viewport (#49 Tự động lưu vị trí cuộn trang PDF và Tab đang mở với OCC)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/patch_session_viewport.md`:

````markdown
# API Evaluation Snapshot: PATCH /api/v1/sessions/{id}/viewport

> **Audit Header**: Session Tag: `test_eval_f3e82a91` | Target: `#49 Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)`  
> **Target Output**: `temp/output/test/patch_session_viewport.md`  
> **Payload Checksums (SHA-256)**:  
> - `01_viewport_update_success.json`: `a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `02_concurrency_conflict_guard.json`: `b2c3d4e5f6a17890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `03_precondition_required_guard.json`: `c3d4e5f6a1b27890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `04_invalid_active_document_guard.json`: `d4e5f6a1b2c37890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `05_multi_tenant_isolation.json`: `e5f6a1b2c3d47890123456789abcdef0123456789abcdef0123456789abcdef0`  
> - `06_validation_bounds_guard.json`: `f6a1b2c3d4e57890123456789abcdef0123456789abcdef0123456789abcdef0`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Valid Viewport Update with OCC (If-Match: "v1") | `200` | `200` | 8.4ms | PASS | Viewport updated: page=3, zoom=1.25, ETag="v2", version=2 |
| Stale Version Concurrency Conflict Guard | `412` | `412` | 3.2ms | PASS | Stale If-Match "v1" rejected with CONCURRENCY_CONFLICT |
| Missing Precondition Header Guard | `428` | `428` | 2.1ms | PASS | Missing If-Match rejected with PRECONDITION_REQUIRED |
| Unassociated Document Attachment Guard | `400` | `400` | 3.5ms | PASS | Unlinked document_id rejected with INVALID_ACTIVE_DOCUMENT |
| Multi-Tenant User Isolation Guard | `404` | `404` | 3.6ms | PASS | Alien user cannot update session (404 SESSION_NOT_FOUND) |
| Path UUID Format Validation Guard | `422` | `422` | 2.5ms | PASS | Malformed UUID path parameter rejected with HTTP 422 VALIDATION_ERROR |

---

## 2. Invariants & Contract Adherence
- **OCC Version Increment Invariant**: Phiên bản tự động tăng `+1`, response header `ETag: "v{version+1}"` đồng nhất hoàn toàn với `data.version`.
- **Precondition Required Invariant**: Bắt buộc client gửi `If-Match` theo chuẩn RFC 7232; thiếu header trả về `428 Precondition Required`.
- **Lost Update Protection**: Chặn đứng việc ghi đè trạng thái cũ bằng mã `412 Precondition Failed` (`CONCURRENCY_CONFLICT`).
- **Document Boundary Invariant**: Chỉ chấp nhận `active_document_id` đã được gắn kết vào phiên; truyền tài liệu lạ trả về `400 Bad Request`.
- **Hermetic Teardown**: Dọn dẹp phiên và tài liệu thử nghiệm khép kín.
````

---

### 7.7. Snapshot Mẫu: POST /api/v1/sessions/{id}/documents (#51 Nạp bài vào phiên - Pure JSON AIP Pattern)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/post_session_documents.md`:

````markdown
# API Evaluation Snapshot: POST /api/v1/sessions/{id}/documents

> **Audit Header**: Session Tag: `test_eval_a1b2c3d4` | Target: `#51 Nạp bài vào phiên (Pure JSON AIP Pattern)`  
> **Target Output**: `temp/output/test/post_session_documents.md`  
> **Payload Checksums (SHA-256)**:  
> - `01_add_existing_document_success.json`: `c3fafd97909eb0e8b6244707038446616134aa6fcabd1d2321ef18681b710851`  
> - `02_add_document_via_url_success.json`: `4a34e3647a5ee794d75cd87af0694f5aebe494f30063ca6943bbc9e9981fd5df`  
> - `03_duplicate_document_conflict_guard.json`: `59a3bee24c1a9c5a79ed793ece5daa324bd3234e77e8f712af3c4f520c02d57a`  
> - `04_capacity_cap_guard.json`: `085aea870246d164f684dbf634bbf39cc9c59cc84a6a73456c52d0e2bce4ccd9`  
> - `05_multi_tenant_isolation.json`: `13e714039a03134a0aae8b1f35bf2393445c4e74fb08349bcd72565f09416c57`  
> - `06_validation_error_guard.json`: `76677cf2c682b20617627017b51d342f035e929274684b9c4491427eb92ab173`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Add Existing Document via ID | `202` | `202` | 9.2ms | PASS | Document associated; status=associated, version incremented |
| Add Document via Online URL | `202` | `202` | 14.5ms | PASS | Background ingestion queued; status=queued, version incremented |
| Duplicate Document Attachment Guard | `409` | `409` | 3.8ms | PASS | Duplicate attachment rejected with DOCUMENT_ALREADY_IN_SESSION |
| Max Capacity Cap Guard (Limit 5 Papers) | `422` | `422` | 4.1ms | PASS | Exceeding 5 papers rejected with SESSION_CAPACITY_EXCEEDED |
| Multi-Tenant User Isolation Guard | `404` | `404` | 3.5ms | PASS | Alien user cannot attach document to private session (404) |
| URL Scheme & Validation Bounds Guard | `422` | `422` | 2.8ms | PASS | Invalid URL scheme rejected with HTTP 422 VALIDATION_ERROR |

---

## 2. Invariants & Contract Adherence
- **202 Accepted Asynchronous Invariant**: Nạp tài liệu qua Pure JSON phản hồi mã HTTP 202 Accepted và cập nhật version của phiên.
- **Session Capacity Invariant**: Ngưỡng trần tối đa 5 tài liệu/phiên được cưỡng chế tuyệt đối; cố nạp bài thứ 6 bị chặn với mã 422.
- **Duplicate Document Guard**: Ngăn chặn tình trạng gắn trùng 1 tài liệu nhiều lần trong cùng phiên làm việc (HTTP 409).
- **Tenant Privacy Invariant**: Cách ly dữ liệu hoàn toàn giữa các người dùng (Zero Leakage).
- **Hermetic Teardown**: Dọn dẹp khép kín toàn bộ phiên và tài liệu thử nghiệm.
````

---

### 7.8. Snapshot Mẫu: POST /api/v1/sessions/{id}/messages (#52 Gửi câu hỏi & Stream SSE - Cross-Document Namespacing)

Dưới đây là cấu trúc tệp báo cáo mẫu sinh ra tại `temp/output/test/post_session_messages.md`:

````markdown
# API Evaluation Snapshot: POST /api/v1/sessions/{id}/messages

> **Audit Header**: Session Tag: `test_eval_6c6ba19f` | Target: `#52 Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)`  
> **Target Output**: `temp/output/test/post_session_messages.md`  
> **Raw Artifacts**: `tests/.artifacts/post_session_messages/`  
> **Payload Checksums (SHA-256)**:  
> - `01_ambiguous_roadmap_options_200.json`: `7710f3dd33a1b884b507f79135c6955c93063bd98e8c9c1f582408b2396b151e`  
> - `02_tailored_roadmap_tokens_200.json`: `fe911648209d48dbbadd57272059ff0dc4f0ea1e84853e4ee493c7ef357cb369`  
> - `03_table1_complexity_grounding_200.json`: `7b5c257bbbbe1e7771598cd48442ed79831f320bee0c494294e20cafd32feb27`  
> - `04_presupposition_refutation_200.json`: `aa1f0799c7d5cfaa35ad9bbb465e9cf348c44fbf292231ddcdc2732631edb2d3`  
> - `05_out_of_domain_mitigation_200.json`: `94eab0d2907fd4066d052bacd88075e590f4104a9f0a87c62cedabbe2500ec73`  
> - `06_metric_trap_mitigation_200.json`: `cd2f5c6065fdbf2821f8adbc063e2fccb4bf8641cd1cdf6dcc2382e9150ee0ec`  
> - `07_get_chat_history_200.json`: `390e76d23537d8917d113ed4b538f4d113a2a964f90a83b36a730f7450a8995a`  
> - `08_stream_resumption_and_callback.json`: `96ed6ede9c8037b6208b086b63ef97ea229d3bf3fd0964df1035befe3662d1b0`  
> - `08_clear_chat_history_204.json`: `7be6258065b766cb7ee1a25ea0f35ace54aee0ce59499caddd383df8a74be293`  
> - `09_archived_session_error_200.json`: `a20114cb3d493eace1c1e54c065f785d0e43c8a1009530093f7aa74ee45a086e`  
> **Quality Gate**: **PASSED** (100% Invariants Verified)

---

## 1. Test Cases Matrix

| Test Scenario | Actual HTTP | Expected HTTP | Latency | Result | Verification Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| 1. Ambiguous Query Clarification (event: interactive_options) | `200` | `200` | 1454.1ms | PASS | Emitted 3 Personas and 3 Diagnostic Micro-Quiz questions for zero-knowledge prompt |
| 2. Multi-turn Tailored Roadmap (Persona B 5-Stage Path) | `200` | `200` | 1672.9ms | PASS | Streamed 5-stage personalized roadmap anchored to Figure 1 and Table 1 |
| 3. Table 1 Complexity Math & Spatial Grounding (Page 6) | `200` | `200` | 1142.3ms | PASS | Compared O(n^2 · d) vs O(n · d^2) and accurately anchored citation to Page 6 |
| 4. Socratic False Presupposition Refutation (RNN Trap) | `200` | `200` | 813.3ms | PASS | Rebutted false RNN premise, directed user to Positional Encoding at Section 3.5 Page 6 |
| 5. Out-of-Domain Distractor Mitigation (GSM8K / GPT-4) | `200` | `200` | 1031.7ms | PASS | Rejected modern benchmark/model hallucination, citing 2017 paper publication date |
| 6. Experimental Metric Trap Mitigation (BLEU 45.0 -> 28.4) | `200` | `200` | 999.8ms | PASS | Rebutted 45.0 BLEU trap, confirmed actual 28.4 EN-DE at Table 2 Page 8 |
| 7. GET /api/v1/sessions/{id}/messages (History Pagination) | `200` | `200` | 8.0ms | PASS | Retrieved 6 turns (total: 6) with full question/answer contracts |
| 8. Stream Resumption (RFC 8895) & Structured Callback | `200` | `200` | 2218.1ms | PASS | Successfully skipped events <= Last-Event-ID: 2 and accepted structured callback |
| 9. DELETE /api/v1/sessions/{id}/messages (Idempotent 204) | `204` | `204` | 9.6ms | PASS | Cleared all conversation turns; subsequent fetch returned total=0 |
| 10. Archived Session Message Guard (Expect event: error) | `200` | `200` | 3.8ms | PASS | Emitted event: error with code SESSION_ARCHIVED on archived session |

---

## 2. Invariants & Contract Adherence
- **RFC 8895 Server-Sent Events (SSE) Streaming**: Tuân thủ chuẩn `text/event-stream`, phát chuỗi sự kiện `start`, `reasoning`, `citations`, `token`, `interactive_options`, `done`.
- **AT-CoT Ambiguity Resolution**: Tự động nhận diện truy vấn mơ hồ, phát sự kiện SSE `interactive_options` với 3 Personas và 3 câu hỏi Diagnostic Micro-Quiz.
- **Table 1 Mathematical Precision**: So sánh chuẩn xác độ phức tạp $\mathcal{O}(n^2 \cdot d)$ vs $\mathcal{O}(n \cdot d^2)$, đính kèm trích dẫn không gian Trang 6.
- **Socratic Presupposition Refutation**: Bác bỏ tiền đề sai lệch gán ghép RNN vào Encoder Transformer, điều hướng tới Positional Encoding (Mục 3.5, Trang 6).
- **Anti-Hallucination Scope & Metric Guards**: Từ chối các truy vấn ngoài miền (GSM8K/GPT-4 trên bài báo 2017) và bác bỏ bẫy điểm BLEU 45.0.
- **Stream Resumption (RFC 8895)**: Bỏ qua các sự kiện đã gửi dựa trên header `Last-Event-ID`.
- **Archived Session Message Guard**: Chặn tin nhắn trên phiên đã archive và phát sự kiện `error` (`SESSION_ARCHIVED`).
- **Hermetic REST Lifecycle & Clean Up**: Tự động thu hồi và xóa sạch tài nguyên sau autotest (Zero Retention).
````

---

## 8. Thiết Kế Kiến Trúc Script Runner (`scripts/eval_api.py`)

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


def calculate_bbox_iou(bbox_pred: list[float], bbox_gt: list[float]) -> float:
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
    tokens_a = set(re.findall(r"\w+", title_a.lower()))
    tokens_b = set(re.findall(r"\w+", title_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))


class EvaluationContext:
    """Context Manager thực thi kiểm thử khép kín qua chuẩn REST API."""

    def __init__(
        self,
        base_url: str,
        keep_data: bool = False,
        user_id: str | None = None,
    ):
        self.base_url = base_url
        self.keep_data = keep_data
        self.user_id = user_id
        self.session_tag = user_id if user_id else f"test_eval_{uuid.uuid4().hex[:8]}"
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
        self.created_document_ids: list[str] = []

    async def __aenter__(self):
        return self

    def track_document(self, document_id: str):
        self.created_document_ids.append(document_id)

    async def cleanup(self) -> list[str]:
        if self.keep_data:
            return []
        cleaned = []
        for doc_id in self.created_document_ids:
            try:
                res = await self.client.delete(f"/api/v1/documents/{doc_id}")
                if res.status_code in (200, 204, 404):
                    cleaned.append(doc_id)
            except Exception as e:
                sys.stderr.write(f"Cảnh báo: Lỗi dọn dẹp document {doc_id}: {e}\n")
        self.created_document_ids.clear()
        return cleaned

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.cleanup()
        finally:
            if self.client:
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
        async with EvaluationContext("http://localhost:8000") as ctx:
            # Thực thi quy trình kiểm thử và đối chiếu...
            pass
    except asyncio.CancelledError:
        sys.stderr.write(
            "\n[WARN] Nhận tín hiệu dừng. Đã dọn dẹp an toàn qua REST API.\n"
        )
```

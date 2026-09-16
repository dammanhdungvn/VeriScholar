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
│    (Chống Fake Report)   │ vào Audit Header; CI đối soát với file đĩa.     │
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
        extracted: dict[str, Any], expected: dict[str, Any]
    ) -> bool:
        # Tầng 1: Khớp định danh duy nhất (DOI / arXiv ID)
        if extracted.get("doi") and expected.get("doi"):
            return extracted["doi"].strip().lower() == expected["doi"].strip().lower()
        if extracted.get("arxiv_id") and expected.get("arxiv_id"):
            return (
                extracted["arxiv_id"].strip().lower()
                == expected["arxiv_id"].strip().lower()
            )

        # Tầng 2: Khớp tiêu đề mờ theo Token Jaccard
        title_ext = extracted.get("title", "")
        title_exp = expected.get("title", "")
        similarity = token_jaccard_similarity(title_ext, title_exp)

        if similarity >= 0.85:
            # Kiểm tra từ định danh phiên bản/phần (part 1, part 2, v1, v2) nếu có
            for tag in ["part 1", "part 2", "part i", "part ii", "v1", "v2"]:
                if (tag in title_ext.lower()) != (tag in title_exp.lower()):
                    return False
            # Kiểm tra năm xuất bản nếu cả 2 bên đều có
            year_ext = str(extracted.get("year", ""))
            year_exp = str(expected.get("year", ""))
            if year_ext and year_exp and year_ext != year_exp:
                return False
            return True

        return False
    ```

---

### 4.2. Kiểm Toán Hình Học Không Gian Bounding Box (Spatial IoU Gate)

- **Nguy cơ tiềm ẩn:** Parser trả về text chính xác nhưng tọa độ `bounding_box` bị sai (ví dụ: tọa độ âm, tọa độ vượt kích thước trang, hoặc `x1 < x0`), khiến tính năng highlight trên UI của VeriScholar hiển thị lệch vị trí.
- **Giải pháp chuẩn hóa:**
  - **Công thức IoU hình chữ nhật:**
    $$IoU = \frac{\text{Area}(B_{pred} \cap B_{gt})}{\text{Area}(B_{pred} \cup B_{gt})}$$
  - **Quy chuẩn đo lường:**
    - Mỗi khối trích xuất (section/chunk/reference) có bounding box phải thỏa mãn:
      - `0 <= x0 < x1 <= page_width`
      - `0 <= y0 < y1 <= page_height`
    - Đối chiếu với Ground Truth hình học: Trung bình cộng `Spatial IoU >= 0.70`.
    - Bất kỳ khối nào có `IoU == 0` (hoàn toàn lệch trang hoặc lệch vị trí) bị ghi nhận là một vi phạm chất lượng nghiêm trọng (*Spatial Misalignment Warning*).

---

### 4.3. Quản Lý Vòng Đời Dữ Liệu Khép Kín (Hermetic REST Cleanup vs Seed Data Mode)

Hệ thống hỗ trợ 2 chế độ vận hành dọn dẹp dữ liệu:

1. **Chế độ Mặc định (Hermetic Zero-Retention Mode):**
   - Toàn bộ tài liệu được tạo trong phiên kiểm thử đều được theo dõi (`ctx.track_document(doc_id)`).
   - Khi khối lệnh thoát (`__aexit__`), runner tự động gọi `DELETE /api/v1/documents/{doc_id}` đối với từng tài liệu.
   - Sau khi chạy xong, cơ sở dữ liệu và vùng lưu trữ vật lý hoàn toàn sạch sẽ, không để lại dữ liệu rác hay làm sai lệch chỉ số phân trang.

2. **Chế độ Giữ Dữ Liệu (Seed Data Mode via `--keep-data` / `-k`):**
   - Khi lập trình viên muốn nạp nhanh tài liệu mẫu vào cơ sở dữ liệu để mở Swagger UI (`/docs`) hoặc trình duyệt kiểm thử thủ công, thêm cờ `--keep-data` (hoặc `-k`):
     ```bash
     uv run python scripts/eval_api.py --api upload --paper "Attention Is All You Need.pdf" --keep-data --bless
     ```
   - Runner sẽ bỏ qua bước gọi lệnh `DELETE`, bảo tồn nguyên vẹn bản ghi trong PostgreSQL và tệp PDF vật lý trong `storage/`.
   - Có thể kết hợp với cờ **`--user-id <tenant_id>`** để gán tài liệu vào một tài khoản/phiên làm việc cụ thể.

---

### 4.4. Mô Hình Kiểm Thử Không Tốn Chi Phí (Zero-Cost VCR Cloud Replay)

- Sử dụng thư viện `vcrpy` để ghi lại (record) và phát lại (replay) toàn bộ các phản hồi từ API đám mây bên ngoài (Azure Document Intelligence OCR, OpenAI Embedding API, Crossref API).
- Các bản ghi cassette được lưu tại `tests/fixtures/vcr_cassettes/`.
- **Mặc định (CI Gate & Local Dev):** Sử dụng mock cassette, tiêu tốn **0 token và 0 request đám mây**.
- **Chế độ kiểm toán trực tiếp (`--live-cloud`):** Chỉ kích hoạt khi có lệnh kiểm toán phát hành chính thức.

---

### 4.5. Cơ Chế Cập Nhật Baseline Tự Động (Snapshot Blessing Pattern)

- **Nguy cơ tiềm ẩn:** Khi kỹ sư cải tiến thuật toán bóc tách giúp tìm thấy nhiều tài liệu tham khảo chính xác hơn dữ liệu cũ, toàn bộ test suite sẽ báo fail do lệch với `.expected.json`. Nếu phải cập nhật thủ công hàng trăm trường JSON bằng tay thì chi phí bảo trì sẽ rất lớn.
- **Giải pháp chuẩn hóa:**
  - Bổ sung cờ **`--bless`** (tương tự như Jest / Pytest-Snapshot):
    ```bash
    uv run python scripts/eval_api.py --api extract-references --bless
    ```
  - Khi kỹ sư đã xem xét báo cáo Markdown và xác nhận kết quả mới là chính xác, lệnh trên sẽ tự động đồng bộ output mới vào tệp `.expected.json`.
  - Cờ `--bless` là cơ chế duy nhất cho phép bypass rào chắn kiểm tra toàn vẹn Git của Ground Truth.

---

### 4.6. Rào Chặn Đồng Bộ Trạng Thái Cho Endpoint Bất Đồng Bộ `202 Accepted` (Deterministic Polling Barrier)

- Gửi lệnh `POST :parse` và nhận mã `202 Accepted`.
- Tự động chuyển sang vòng lặp polling `GET /documents/{id}/status` với Exponential Backoff (chu kỳ 500ms đến 2s, timeout cứng 30 giây).
- Chỉ khi `status == "completed"`, runner mới gọi `GET /documents/{id}` để nạp payload thực tế vào bộ linter ngữ nghĩa.

---

### 4.7. Rào Chặn Tín Hiệu Ngắt An Toàn (Signal-Safe Cancellation)

- Thay vì dùng `sys.exit(1)` trong signal handler làm dừng Event Loop đột ngột, runner kích hoạt `current_task.cancel()`.
- Ngoại lệ `asyncio.CancelledError` kích hoạt phương thức `__aexit__` của `EvaluationContext`, gọi `DELETE /api/v1/documents/{doc_id}` để dọn sạch toàn bộ tài liệu kiểm thử trước khi tiến trình kết thúc.

---

### 4.8. Kiến Trúc Dual-Output & Quality Budget Cho Đường Ống CI/CD

- **Mô hình Dual-Output:**
  1. **Tệp Markdown Báo Cáo:** Tinh gọn (< 50 KB), chứa Executive Summary, Spatial IoU, Precision/Recall, Linter Warnings và các mẫu lỗi đại diện cho người và AI Agent review. Chứa Audit Header có mã băm SHA-256 của các tệp payload tương ứng.
  2. **Tệp JSON Chỉ Số Máy Đọc (`tests/.artifacts/eval_metrics.json`):** Chứa các thông số định lượng phục vụ máy chủ CI.
- **Quality Budget Gate:**
  - Cấu hình ngưỡng chất lượng tối thiểu: `min_recall = 0.90`, `min_precision = 0.95`, `min_spatial_iou = 0.70`.
  - Nếu bất kỳ chỉ số cốt lõi nào tụt dưới ngưỡng, runner tự động thoát với **`exit code 1`** để ngắt đường ống CI ngay lập tức.
- **Khai báo `.gitignore`:** Thư mục `tests/.artifacts/` được bỏ qua không commit vào Git repo.

---

### 4.9. Phân Tách Môi Trường & Kiểm Soát Log Truy Vấn (Environment Isolation & Query Log Hygiene)

- **Nguy cơ tiềm ẩn:**
  - Khi `DEBUG=True`, SQLAlchemy Engine tự động in ra toàn bộ câu lệnh SQL thô (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, transaction `BEGIN`/`COMMIT`), gây ngập lụt màn hình terminal (terminal flooding) với hàng trăm dòng log kỹ thuật, che khuất ma trận kết quả benchmark và cảnh báo nghiệp vụ.
  - Chạy bài kiểm thử tự động trên cùng một cơ sở dữ liệu đang dùng để phát triển cục bộ dễ gây xung đột dữ liệu và làm sai lệch chỉ số phân trang.
- **Giải pháp chuẩn hóa:**
  - **Phân tách biến cấu hình `SQL_ECHO`:** Tách riêng tính năng in log SQL ra khỏi cờ `DEBUG`. Khai báo `SQL_ECHO: bool = False` trong `config.py` và `.env.example`. Mặc định tắt log SQL thô trong môi trường phát triển và kiểm thử.
  - **Kiểm soát log trong Script Runner:** Script `eval_api.py` tự động cấu hình logger `sqlalchemy.engine` ở mức `WARNING`. Khi kỹ sư muốn điều tra chuyên sâu câu lệnh SQL và kế hoạch truy vấn ORM, cung cấp cờ `--debug-sql` để bật lại chế độ echo chi tiết.
  - **Mô hình kiến trúc 3 tầng Database chuẩn Production:**
    1. *Local Dev Database (`verischolar`)*: Phục vụ chạy ứng dụng cục bộ, giao diện Swagger UI và kiểm thử thủ công của lập trình viên.
    2. *Isolated Test Database (`verischolar_test`)*: Phục vụ `pytest` và kiểm thử tự động CI/CD hoàn toàn khép kín.
    3. *Production Synthetic Canary*: Môi trường sản xuất thực tế chỉ chạy kiểm thử tổng hợp (Canary) định kỳ với tenant giám sát riêng (`usr_canary_monitor`), tuyệt đối không đụng chạm đến dữ liệu người dùng thật.

---

### 4.10. Quản Lý Thư Mục Báo Cáo Đầu Ra `temp/output/test/` & Cơ Chế Làm Mới Tệp (File Clean Refresh)

- **Vị trí lưu trữ chuyên biệt:**
  - Mọi tệp báo cáo đánh giá tự động dạng Markdown được lưu tại thư mục: **`temp/output/test/`**.
  - Thư mục này nằm trong quy tắc `.gitignore`, đảm bảo không gây bẩn Git repository nhưng vẫn bền vững trên đĩa để lập trình viên và AI mở xem ngay khi cần.
- **Quy ước đặt tên tệp cố định (Deterministic Filenames):**
  - Mỗi API endpoint có một tên tệp báo cáo duy nhất và cố định:
    - `temp/output/test/post_documents_upload.md`
    - `temp/output/test/get_documents_list.md`
    - `temp/output/test/get_documents_detail.md`
    - `temp/output/test/get_documents_file_stream.md`
    - `temp/output/test/get_documents_status.md`
    - `temp/output/test/post_documents_star.md`
    - `temp/output/test/post_documents_parse.md`
    - `temp/output/test/post_documents_extract_references.md`
    - `temp/output/test/get_documents_structure.md`
    - `temp/output/test/get_documents_chunks.md`
    - `temp/output/test/get_documents_chunk_detail.md`
    - `temp/output/test/get_documents_summary.md`
    - `temp/output/test/delete_documents.md`
- **Cơ chế kiểm tra tệp tồn tại & Làm mới (Clean Refresh):**
  - Trước khi ghi báo cáo mới, runner gọi hàm `check_and_prepare_output_file(target_file)`.
  - Nếu tệp đã tồn tại từ lần chạy trước:
    - *Chế độ Mặc định (Tự động / CI / Non-interactive):* Thông báo ngắn gọn và ghi đè sạch (Clean Refresh), đảm bảo báo cáo luôn phản ánh trung thực kết quả chạy mới nhất mà không bị lẫn dữ liệu cũ.
    - *Chế độ Tương tác (`--confirm-overwrite` / `-i`):* Dừng lại hỏi lập trình viên `(y/n)` trước khi xóa/ghi đè.

---

### 4.11. Hiển Thị Trực Quan Đóng Khung Trên Terminal & Xử Lý Payload Lớn (In-Terminal HTTP Exchange & Smart Payload Folding)

- **Vấn đề cốt lõi:**
  - Nếu terminal chỉ in `[PASS]`, lập trình viên và AI rơi vào trạng thái "hộp đen", không biết Request Input gửi gì và Response Output trả về cấu trúc ra sao.
  - Ngược lại, nếu in toàn bộ dữ liệu thô:
    - **Binary stream (`/file`)**: In byte nhị phân thô làm đơ/treo terminal.
    - **Vector Embeddings**: Mảng số thực 1,536 chiều làm trôi toàn bộ màn hình.
    - **Danh sách phân trang lớn (`per_page=20`, nhiều chunks/references)**: Chiếm hàng nghìn dòng.
- **Quy chuẩn thiết kế "Dual-View & Smart Payload Folding":**
  - **Tại Terminal:** Hiển thị 3 khối đóng khung trực quan (`HTTP Exchange Box`):
    1. `┌── [REQUEST INPUT]`: Hiển thị Method, Path, Headers cốt lõi và Form-Data/Body preview.
    2. `┌── [RESPONSE OUTPUT]`: Hiển thị Status, Latency (ms), Headers và JSON Body đã qua bộ lọc rút gọn thông minh (**Smart Folding**):
       - *Dữ liệu nhị phân (Binary)*: Không in bytes; in tóm tắt: `[Binary stream: 2,215,244 bytes (application/pdf) | Content-Range ...]`.
       - *Danh sách dài (List > 2 items)*: Áp dụng quy tắc **Head-Tail Folding** (hiển thị item 1, item 2, sau đó in `"... [N items folded - xem toàn bộ tại temp/output/test/...] ..."` và item cuối).
       - *Vector nhiều chiều (Embeddings)*: Rút gọn thành `[float vector x 1536 dims: 0.012, -0.045, ... 0.891]`.
       - *Chuỗi văn bản dài (> 200 ký tự)*: Hiển thị đoạn đầu và ghi chú `"... [X ký tự tiếp theo]"`.
       - *Chuỗi Base64*: Rút gọn thành `[base64 image/png: 48,230 bytes]`.
    3. `┌── [KIỂM CHỨNG CHẤT LƯỢNG NGHIỆP VỤ]`: Hiển thị thẻ tóm tắt các chỉ số nghiệp vụ trọng tâm (Document ID, CAS Content Hash, Trạng thái deduplication, Chunk count, Bounding Box IoU).
  - **Tại Tệp Báo Cáo Markdown (`temp/output/test/*.md`):** Lưu trữ **100% đầy đủ nguyên vẹn (Full Raw Payloads)** cả Request Input và Response Output, không bị rút gọn, đi kèm mã băm SHA-256 đối soát.

---

## 5. Chiến Lược Tập Dữ Liệu Chuẩn (Golden Papers Dataset)

Bộ tài liệu kiểm thử được đặt tại thư mục `data/papers/`, gồm 7 nhóm tài liệu (4 Happy Path kèm Ground Truth + 3 Chaos Negative):

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

## 6. Danh Mục 9 Endpoints API Kiểm Thử (Module 1: Ingestion & Deep Read)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MODULE 1: INGESTION & DEEP READ - 9 ENDPOINTS               │
├─────┬────────┬─────────────────────────────────────┬────────────────────────┤
│ STT │ Method │ Đường dẫn Endpoint REST             │ Nhiệm Vụ & Quality Gate│
├─────┼────────┼─────────────────────────────────────┼────────────────────────┤
│  1  │ POST   │ /api/v1/documents                   │ Upload PDF & CAS Dedupl│
│  2  │ GET    │ /api/v1/documents                   │ Danh sách phân trang   │
│  3  │ GET    │ /api/v1/documents/{document_id}     │ Chi tiết & Bounding Box│
│  4  │ GET    │ /api/v1/documents/{document_id}/file│ Stream nhị phân chunked│
│  5  │ GET    │ /api/v1/documents/{document_id}/stat│ Tiến độ Pipeline (0-100│
│  6  │ POST   │ /api/v1/documents/{document_id}:star│ Đánh dấu tài liệu sao  │
│  7  │ POST   │ /api/v1/documents/{document_id}:pars│ Trigger bóc tách & RAG │
│  8  │ POST   │ /api/v1/documents/{id}:extract-refs │ Bóc tách tham khảo & F1│
│  9  │ DELETE │ /api/v1/documents/{document_id}     │ Xóa sạch & Zero Leakage│
└─────┴────────┴─────────────────────────────────────┴────────────────────────┘
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

# 🛠️ Hướng Dẫn Vận Hành Scripts Kiểm Thử Tự Động (Evaluation Harness)

Thư mục `scripts/` chứa toàn bộ công cụ dòng lệnh (CLI) phục vụ việc chạy kiểm thử tự động (**Autotest Snapshots**), đo lường độ trễ, kiểm chứng chất lượng nghiệp vụ (CAS Deduplication, Phân trang RFC 8288, Trích xuất tham khảo, Bounding Box IoU) và soi chiếu dữ liệu chi tiết của hệ thống **VeriScholar**.

---

## 📌 1. Bảng Tra Cứu Lệnh Chạy Từng API (API Evaluation Reference Table)

Hệ thống hỗ trợ 2 chế độ chạy cho mỗi API:
- **Chạy Trọn Vẹn (Full Dataset - Mặc Định):** Duyệt qua toàn bộ danh mục tài liệu mẫu có trong `data/papers/` và các kịch bản biên.
- **Chạy Lẻ (Single Target):** Thêm cờ `--paper "<tên_bài_báo.pdf>"` khi bạn muốn tập trung debug nhanh một bài báo cụ thể.

Bạn có thể sử dụng tên chuẩn canonical (`post_documents_upload`, `get_documents_list`, ...) hoặc alias ngắn gọn (`upload`, `list`, ...):

| STT | API Endpoint | Tên Runner (`--api`) | Chế Độ Chạy Trọn Vẹn (Khuyên Dùng Mặc Định) | Chế Độ Chạy Lẻ (Tập Trung 1 File) | Mục Đích & Hành Vi Kiểm Thử |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `POST /api/v1/documents` | `upload`<br>`post_documents_upload` | `uv run python scripts/eval_api.py --api upload --bless` | `uv run python scripts/eval_api.py --api upload --paper "Attention Is All You Need.pdf" --bless` | Duyệt qua tất cả PDF trong `data/papers/`, xác thực SHA-256 CAS, kiểm chứng Deduplication (tái sử dụng blob ~13ms), kiểm tra file lỗi (corrupted). |
| **2** | `GET /api/v1/documents` | `list`<br>`get_documents_list` | `uv run python scripts/eval_api.py --api list --bless` | *(Tự động seed 3 file mẫu & dọn dẹp sạch)* | Tự động seed 3 tài liệu vào database để kiểm thử phân trang RFC 8288 (`page=1&per_page=2`), liên kết `next`/`prev`, sắp xếp `created_at DESC`, lọc `status=uploaded`, chặn lỗi `page=0`, `per_page=101` (422), sau đó tự động xóa dọn dẹp (hoặc dùng `-k` để giữ lại). |
| **3** | `GET /api/v1/documents/{id}` | `detail`<br>`get_documents_detail` | `uv run python scripts/eval_api.py --api detail --bless` | `uv run python scripts/eval_api.py --api detail --paper "Attention Is All You Need.pdf" --bless` | Lấy chi tiết tài liệu, kiểm chứng cấu trúc hình học trang (`PageMetadataItem`), typographical points `[width, height]`, góc xoay `rotation_deg`. |
| **4** | `GET /api/v1/documents/{id}/file` | `stream`<br>`get_documents_file_stream` | `uv run python scripts/eval_api.py --api stream --bless` | `uv run python scripts/eval_api.py --api stream --paper "Attention Is All You Need.pdf" --bless` | Stream nhị phân PDF an toàn, hỗ trợ phân đoạn `Range: bytes=0-1023` (HTTP 206) và tải trọn vẹn (HTTP 200). Đã có cơ chế chặn in byte thô gây đơ terminal. |
| **5** | `GET /api/v1/documents/{id}/status` | `status`<br>`get_documents_status` | `uv run python scripts/eval_api.py --api status --bless` | `uv run python scripts/eval_api.py --api status --paper "Attention Is All You Need.pdf" --bless` | Polling tiến độ bóc tách nền (`stage`, `progress: 0..100`), xác thực máy trạng thái hợp lệ. |
| **6** | `POST /api/v1/documents/{id}:star` | `star`<br>`post_documents_star` | `uv run python scripts/eval_api.py --api star --bless` | `uv run python scripts/eval_api.py --api star --paper "Attention Is All You Need.pdf" --bless` | Đánh dấu sao/lưu trữ vĩnh viễn (`is_persistent = true/false`), kiểm tra tính lũy kế và phân quyền bảo vệ tài liệu. |
| **7** | `POST /api/v1/documents/{id}:parse` | `parse`<br>`post_documents_parse` | `uv run python scripts/eval_api.py --api parse --bless` | `uv run python scripts/eval_api.py --api parse --paper "Attention Is All You Need.pdf" --bless` | Kích hoạt worker bóc tách PDF (Semantic Chunking, Visual Grounding Bounding Box), kiểm định chất lượng bóc tách văn bản. |
| **8** | `POST /api/v1/documents/{id}:extract-references` | `extract-references`<br>`post_documents_extract_references` | `uv run python scripts/eval_api.py --api extract-references --bless` | `uv run python scripts/eval_api.py --api extract-references --paper "Attention Is All You Need.pdf" --bless` | Bóc tách thư mục tài liệu tham khảo, đối soát ngoại quan Cascading F1 với Ground Truth (`expected_reference_count`, `expected_dois`, `expected_arxiv_ids`). |
| **9** | `DELETE /api/v1/documents/{id}` | `delete`<br>`delete_documents` | `uv run python scripts/eval_api.py --api delete --bless` | `uv run python scripts/eval_api.py --api delete --paper "Attention Is All You Need.pdf" --bless` | Xóa tài liệu khỏi hệ thống (HTTP 204 No Content), xác minh truy vấn sau khi xóa trả về HTTP 404 Not Found. |

---

## ⚡ 2. Chạy Toàn Bộ Chuỗi API Module 1 (Pipeline Suite)

Để kiểm thử tích hợp xuyên suốt toàn bộ vòng đời tài liệu từ Upload $\rightarrow$ Parse $\rightarrow$ Chunk $\rightarrow$ References $\rightarrow$ Delete trên toàn hệ thống:

```bash
uv run python scripts/eval_api.py --all --bless
```

> **Ghi chú**: Lệnh `--all` sẽ tự động thực thi cả 9 runners theo đúng thứ tự phụ thuộc kiến trúc (`MODULE_1_ORDER`).

---

## 🔄 3. Cơ Chế Tự Động Nạp (Seed) & Dọn Dẹp (Hermetic Lifecycle)

### Tại sao các lệnh `GET` lại thấy log `POST` ở đầu và `DELETE` ở cuối?
Khi kiểm thử các API dạng truy vấn (như `GET /api/v1/documents` hoặc `GET /api/v1/documents/{id}`), hệ thống cần có tài liệu thực tế trong database để kiểm tra:
1. **Giai đoạn tiền đề (Pre-requisite Seeding):** Script tự động chạy `POST /api/v1/documents` để nạp tạm 1 hoặc 3 tài liệu mẫu vào phiên làm việc (`session_tag`) và đăng ký vào danh sách theo dõi `ctx.track_document(doc_id)`.
2. **Giai đoạn kiểm thử (Evaluation):** Thực thi các câu lệnh `GET` để đo lường độ trễ, kiểm tra phân trang, sắp xếp và lọc dữ liệu.
3. **Giai đoạn hoàn trả (Teardown Cleanup):** Khi kết thúc bài test, script tự động duyệt danh sách và gọi `DELETE /api/v1/documents/{doc_id}` để **giải phóng cơ sở dữ liệu**, tránh để lại dữ liệu rác làm sai lệch các lượt kiểm thử kế tiếp.

### Làm thế nào để giữ lại dữ liệu vừa seed trên database?
Nếu bạn muốn giữ lại dữ liệu vừa tạo để mở Swagger UI (`http://localhost:8000/docs`) kiểm tra bằng tay, chỉ cần thêm cờ **`-k`** hoặc **`--keep-data`**:
```bash
# Giữ lại dữ liệu danh sách documents trên DB:
uv run python scripts/eval_api.py --api list --bless -k
```

---

## 🎛️ 4. Các Cờ Tùy Chọn Hữu Ích Khi Chạy Lệnh

| Cờ Lệnh | Tên Viết Tắt | Ý Nghĩa & Tình Huống Sử Dụng | Ví Dụ Mẫu |
| :--- | :---: | :--- | :--- |
| `--api <tên>` | `-a` | Chỉ định chạy riêng một API cụ thể. | `--api upload` hoặc `--api post_documents_upload` |
| `--paper "<tên_file>"` | `-p` | **Chạy lẻ:** Giới hạn phạm vi kiểm thử trên đúng 1 file PDF trong `data/papers/`. Nếu không truyền cờ này, script sẽ **tự động quét toàn bộ** file PDF có trong thư mục. | `--paper "Attention Is All You Need.pdf"` |
| `--bless` | `-b` | Tự động làm mới và cập nhật bản snapshot đánh giá hợp lệ. | Thêm cờ `--bless` khi muốn tạo báo cáo kiểm thử mới nhất. |
| `--keep-data` | `-k` | **Bảo tồn dữ liệu:** Không xóa tài liệu sau khi chạy xong để bạn có thể mở Swagger UI (`http://localhost:8000/docs`) kiểm tra thực tế. | `uv run python scripts/eval_api.py --api list -k` |
| `--confirm-overwrite` | `-i` | **Chế độ hỏi an toàn:** Nếu tệp báo cáo kết quả cũ đã tồn tại, CLI sẽ hỏi bạn `(y/n)` trước khi xóa/ghi đè. | `uv run python scripts/eval_api.py --api list -i` |
| `--live-cloud` | | Cho phép gọi dịch vụ AI Cloud thực tế (Azure Document Intelligence) thay vì dùng VCR replay fixture. | `uv run python scripts/eval_api.py --api parse --live-cloud` |

---

## 🔬 5. Công Cụ Soi Chi Tiết Payload Dữ Liệu (`surgical_inspect.py`)

Khi cần xem xét cấu trúc JSON thô hoặc gỡ lỗi chuyên sâu mà không làm tràn cửa sổ terminal:

| Mục Đích | Lệnh Thực Thi |
| :--- | :--- |
| **Xem danh mục toàn bộ báo cáo & artifact hiện có** | `uv run python scripts/eval/surgical_inspect.py --summary` |
| **Soi chi tiết một artifact cụ thể** | `uv run python scripts/eval/surgical_inspect.py -a "Attention Is All You Need_initial"` |
| **Soi cấu trúc của đoạn Chunk thứ `n`** | `uv run python scripts/eval/surgical_inspect.py -a "Attention Is All You Need_initial" --chunk 0` |
| **Chỉ lọc ra các lỗi bất thường (Anomalies/Errors)** | `uv run python scripts/eval/surgical_inspect.py -a "Attention Is All You Need_initial" --errors-only` |

---

## 📂 6. Cấu Trúc Báo Cáo & Dữ Liệu Đầu Ra

1. **Hiển thị trực quan trên Terminal (Dual-View Boxed Format):**
   - `┌── [REQUEST INPUT]`: Hiển thị Method, Path, Headers, Form-Data.
   - `┌── [RESPONSE OUTPUT]`: Hiển thị HTTP Status Code, Thời gian phản hồi TTFB (ms) và JSON Body qua bộ lọc **Smart Folding** (chống đơ máy: tự động thu gọn byte nhị phân, chuỗi dài, vector 1,536 chiều và danh sách phân trang dài theo quy tắc Head-Tail).
   - `┌── [KIỂM CHỨNG CHẤT LƯỢNG NGHIỆP VỤ]`: Hiển thị ma trận tick xanh `✓` cho các bất biến quan trọng (Status code, Deduplication hit, Sorting order, RFC links, Boundary guards).

2. **Thư mục báo cáo Markdown chuyên biệt:**  
   `temp/output/test/`
   - Chứa các tệp báo cáo cố định: `post_documents_upload.md`, `get_documents_list.md`,...
   - **Lưu trữ 100% Full Raw JSON Payloads** (nguyên vẹn, không bị cắt bớt) để lập trình viên và AI agent dễ dàng đọc đối soát.
   - Tự động làm mới sạch sẽ (Clean Refresh) ở mỗi lần chạy mà không gây ô nhiễm kho lưu trữ Git.

3. **Thư mục lưu Payload gốc (Raw Artifacts):**  
   `tests/.artifacts/<api_name>/<scenario_name>.json`
   - Phục vụ kiểm toán độc lập mã băm SHA-256 đối soát.

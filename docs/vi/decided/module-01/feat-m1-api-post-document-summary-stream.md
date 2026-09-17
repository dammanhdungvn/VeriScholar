# Kế Hoạch Kỹ Thuật & Quyết Định Thiết Kế: Real-Time Grounded Summary Stream (POST /api/v1/documents/{id}/summary:stream)

> **Mã tài liệu:** `FEAT-M1-API-57`  
> **Trạng thái:** `DECIDED / APPROVED`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 17/09/2026  
> **Nhánh Git triển khai:** `feat/m1-notes-and-knowledge-digest`  
> **API Canonical:** `POST /api/v1/documents/{document_id}/summary:stream`  
> **Chuẩn thiết kế:** Google AIP-136 (Custom Methods), W3C Server-Sent Events (SSE), RFC 7807 (Problem Details), Hexagonal Architecture.

---

## 1. Hiện Trạng & Đánh Giá Mức Độ Sẵn Sàng (Gap Analysis)

### 1.1. Bối cảnh & Vấn đề Kỹ thuật (Problem Statement)
- **Rào cản độ trễ (Latency Bottleneck):** Trong các nghiên cứu học thuật phức tạp, bài báo có thể dài từ 10 đến 50 trang. Khi gọi endpoint đồng bộ `POST /api/v1/documents/{document_id}/summary:generate`, người dùng phải đợi toàn bộ 3 mục cốt lõi (`problem_statement`, `contributions`, `limitations`) được sinh xong (mất từ 3 đến 8 giây).
- **Trải nghiệm người dùng (UX Perception):** Việc chờ đợi lâu mà màn hình không có phản hồi trực quan tạo cảm giác hệ thống bị treo.
- **Yêu cầu Deep Reading Canvas:** Giao diện Canvas PDF.js cần highlight ngay lập tức vùng dẫn chứng trên trang tài liệu ngay khi từng luận điểm xuất hiện, thay vì chờ đợi toàn bộ payload JSON trả về cùng một lúc.

### 1.2. Những thành phần kế thừa và đã hoàn thiện
1. **Core Domain Entities & Value Objects:**
   - `DocumentSummary` và `SummaryPoint` tại `packages/core/src/core/domain/entities/summary.py`.
   - `BoundingBox` tại `packages/core/src/core/domain/value_objects/bounding_box.py`.
2. **Hạ tầng Tóm tắt Tri thức & Micro-precision Bounding Box Search:**
   - `IDocumentSummarizerPort` và adapter sinh toạ độ PyMuPDF kết hợp LLM.
   - Hàm `generate_document_summary` trong `DocumentService` với khả năng cache hit (< 10ms) và on-demand fallback.
3. **Application Service Streaming Generator:**
   - Hàm `DocumentService.stream_summary()` trong `apps/api/src/api/services/document_service.py` thực hiện phân tách token theo thời gian thực và phát ra các khung sự kiện SSE.
4. **Endpoint Router & OpenAPI Docs:**
   - Endpoint `POST /api/v1/documents/{document_id}/summary:stream` được khai báo đầy đủ trong `apps/api/src/api/v1/endpoints/documents.py`.
   - Mô tả chi tiết `STREAM_SUMMARY_DESCRIPTION` tích hợp trực tiếp vào Swagger UI (`/docs`).

---

## 2. Rà Soát Biến Môi Trường (.env.example)

Tuân thủ nguyên tắc bảo mật **TUYỆT ĐỐI KHÔNG ĐỌC FILE `.env`**, đối chiếu với `.env.example`:
- Endpoint streaming kế thừa hoàn toàn cấu hình LLM hiện có:
  - `LLM_PROVIDER=openai` (hoặc `docker-model-runner`)
  - `OPENAI_API_KEY=`
  - `OPENAI_BASE_URL=https://api.openai.com/v1`
  - `OPENAI_MODEL=5.6-luna`
- **Không phát sinh biến môi trường mới**, đảm bảo tính tương thích ngược 100%.

---

## 3. Phân Tích Rủi Ro & Đánh Đổi Kỹ Thuật (Risk Analysis & Trade-offs)

| Rủi ro kỹ thuật | Mức độ | Giải pháp kỹ thuật xử lý triệt để |
| :--- | :---: | :--- |
| **Client đột ngột đóng tab / ngắt kết nối (Client Disconnection)** | **CAO** | Lắng nghe `request.is_disconnected`. Nếu client ngắt socket, generator lập tức thoát vòng lặp, hủy luồng tính toán nhằm tiết kiệm tài nguyên tính toán LLM/CPU server. |
| **Proxy đệm dữ liệu (Proxy Buffering on Nginx/Cloudflare)** | **CAO** | Cấu hình HTTP headers bắt buộc: `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no` (chỉ thị cho Nginx không buffer gói tin SSE). |
| **Xung đột định dạng dữ liệu SSE** | **TRUNG BÌNH** | Chuẩn hóa format khung SSE: `event: <name>
data: <json>

`. Payload JSON luôn được mã hóa UTF-8 với `ensure_ascii=False`. |
| **Lỗi vòng đời tài liệu (Processing/Failed)** | **TRUNG BÌNH** | Kiểm tra trạng thái tài liệu trước khi mở luồng stream: Trả về HTTP 409 nếu `status == processing`, trả về HTTP 422 nếu `status == failed`. |
| **Multi-tenant Data Leakage** | **CAO** | Luôn ràng buộc `DocumentModel.user_id == current_user.id`. Nếu không khớp, trả về ngay HTTP 404 `DOCUMENT_NOT_FOUND`. |

---

## 4. Phân Rã Thiết Kế Theo Kiến Trúc Lục Giác (Hexagonal Architecture)

### 4.1. Tầng Domain & Value Objects (`packages/core`)
- `BoundingBox`: Đối tượng giá trị bất biến (immutable value object) đại diện cho toạ độ không gian `[x0, y0, x1, y2, page]`.
- `DocumentSummary`: Thực thể chứa 3 luận điểm cốt lõi kèm danh sách dẫn chứng.

### 4.2. Tầng Application Services (`DocumentService`)
Phương thức `stream_summary` trong `apps/api/src/api/services/document_service.py`:
- Đầu vào: `document_id: UUID`, `user_id: UUID`, `db: AsyncSession`, `is_disconnected: Callable`.
- Quy trình:
  1. Kiểm tra cache tóm tắt hiện có hoặc kích hoạt sinh tóm tắt thông qua `generate_document_summary(force=False)`.
  2. Bắn sự kiện `summary_start` chứa `document_id` và cờ `status: "streaming"`.
  3. Lần lượt duyệt qua 3 mục: `problem_statement`, `contributions`, `limitations`:
     - Tách văn bản thành các token từ ngữ và phát sự kiện `summary_chunk`.
     - Sau khi hoàn thành token cuối của mục, phát sự kiện `summary_box` chứa danh sách Bounding Boxes.
  4. Bắn sự kiện `summary_end` báo hiệu hoàn thành.

### 4.3. Tầng Presentation / HTTP Router (`apps/api`)
- Đường dẫn: `POST /api/v1/documents/{document_id}/summary:stream`.
- Response Type: `StreamingResponse(generator, media_type="text/event-stream")`.
- Tích hợp OpenAPI `description=STREAM_SUMMARY_DESCRIPTION` và các mã phản hồi 200, 404, 409, 422.

---

## 5. Đặc Tả Chi Tiết Giao Thức Luồng Sự Kiện (SSE Event Protocol)

### 5.1. Khung sự kiện `summary_start`
Báo hiệu client khởi tạo giao diện stream và chuẩn bị bộ đệm hiển thị.
```text
event: summary_start
data: {"document_id": "6a6cbadb-517c-40db-bcdf-c57975cc016a", "status": "streaming"}
```

### 5.2. Khung sự kiện `summary_chunk`
Phát từng token từ ngữ hiển thị hiệu ứng gõ chữ (typewriter effect).
```text
event: summary_chunk
data: {"section": "problem_statement", "token": "Conventional "}
```

### 5.3. Khung sự kiện `summary_box`
Phát toạ độ Bounding Boxes để Canvas PDF highlight dẫn chứng trực tiếp.
```text
event: summary_box
data: {"section": "problem_statement", "bounding_boxes": [[0.1176, 0.3165, 0.2185, 0.3346, 1]]}
```

### 5.4. Khung sự kiện `summary_end`
Báo hiệu hoàn tất quá trình stream.
```text
event: summary_end
data: {"document_id": "6a6cbadb-517c-40db-bcdf-c57975cc016a", "finish_reason": "completed"}
```

---

## 6. Kế Hoạch Triển Khai & Kiểm Thử (TDD & Matrix)

1. **Unit & Integration Tests (`apps/api/tests/test_documents_summary_generate.py`):**
   - `test_stream_summary_success`: Xác thực mã trạng thái 200, header `text/event-stream`, sự hiện diện của đủ 4 loại sự kiện (`summary_start`, `summary_chunk`, `summary_box`, `summary_end`).
   - `test_stream_summary_not_found`: Xác thực mã trạng thái 404 khi UUID không tồn tại.
2. **Golden Paper Integration Matrix (`apps/api/tests/test_golden_papers_matrix.py`):**
   - `test_level_4_realtime_grounded_summary_stream`: Kiểm thử stream trực tiếp trên bài báo thật `Attention Is All You Need.pdf`.
3. **OpenAPI & Swagger Documentation Verification:**
   - Swagger UI (`/docs`) hiển thị đầy đủ tiêu đề, mô tả và cấu trúc response mẫu.
   - File `docs/vi/swagger.md` đồng bộ 100% tài liệu kỹ thuật offline.

---

## 7. Tiêu Chí Nghiệm Thu & Kiểm Thử Thẩm Định (Acceptance Criteria)

- [x] **TTFT < 1s:** Token đầu tiên bắt đầu đổ về client dưới 1 giây.
- [x] **Trực quan hóa Bounding Boxes:** Mỗi section đều có sự kiện `summary_box` chứa toạ độ hợp lệ `[x0, y0, x1, y2, page]`.
- [x] **Multi-tenant Security:** Chặn 404 khi truy cập tài liệu của user khác.
- [x] **Client Disconnect Resilience:** Tự động hủy stream khi client ngắt kết nối socket.
- [x] **100% Lint & Test Pass:** Toàn bộ test suite và ruff linter đạt trạng thái thành công tuyệt đối.

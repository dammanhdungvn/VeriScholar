# Thiết Kế Chi Tiết Toàn Bộ API - Nền Tảng VeriScholar (RESTful & SSE Specification)

Tài liệu này định nghĩa chi tiết toàn bộ các điểm cuối (REST Endpoints & SSE Streaming), hợp đồng dữ liệu (API Contracts), ranh giới bảo mật, cơ chế kiểm soát đồng thời và bảng mã lỗi cho **toàn bộ 4 Module cốt lõi, Quản lý Phiên nghiên cứu (Session Persistence) và Chia sẻ cộng tác (Sharing & Collaboration)** của hệ thống **VeriScholar** dựa trên chuẩn mực [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md).

Tài liệu tuân thủ nghiêm ngặt các nguyên lý thiết kế API chuẩn mực quốc tế:
- **RESTful Resource Modeling & Google Cloud AIP-136 / AIP-151 Standards** (Custom Methods chuẩn cú pháp `:<verb>`, Long-Running Operations & Real-time SSE Streams).
- **Phân trang Bắt buộc & Điều hướng Hai chiều (RFC 8288 Web Linking)** với đầy đủ các quan hệ `first`, `prev`, `self`, `next`, `last`.
- **Tải nội dung linh hoạt (`include_content: boolean`)** với hợp đồng kiểu dữ liệu tường minh `Optional[str] = None`.
- **Khóa Lạc Quan Chuẩn Giao Thức (RFC 9110 / RFC 7232 OCC)** qua HTTP Headers `ETag` / `If-Match`, phản hồi chuẩn **HTTP 412 Precondition Failed**, loại bỏ hoàn toàn trường `version` trong request body để triệt tiêu xung đột dữ liệu kép (Single Source of Truth).
- **Tính toán Bất biến & Khử trùng lặp (Idempotency Patterns)** với `Idempotency-Key` lưu giữ trên Redis trong cửa sổ 24 giờ.
- **Sự kiện dòng chảy SSE an toàn (Fail-Safe SSE Stream Protocol)** với `start`, `citations`, `token`, `done` (kèm `finish_reason`), `error`, và cơ chế xử lý hủy kết nối máy trạm **HTTP 499 (Client Closed Request)** kèm dập tắt container Sandbox ngay lập tức (`docker kill`).
- **Bất biến Bounding Box phi null & Góc xoay trang (Non-null Bounding Box & Rotation Invariant)**: luôn trả về `[]` thay vì `null`, chuẩn hóa theo Visual Reading Coordinates với `page_dimensions: [width_pt, height_pt]` và `rotation_deg: 0 | 90 | 180 | 270`.
- **Mã lỗi nghiệp vụ đặc thù cho bài toán RAG học thuật (Domain-Specific Error Codes)**.

---

## 0. BẢNG THUẬT NGỮ GIAO THỨC & API DÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

Để giúp các kỹ sư mới (Fresher / Junior) dễ dàng tiếp cận và làm chủ bản đặc tả API gồm 59 endpoints chuẩn công nghiệp của VeriScholar, bảng dưới đây giải thích trực quan các thuật ngữ và giao thức cốt lõi:

| Thuật ngữ | Tiêu chuẩn / Tên đầy đủ | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **RESTful API** | Representational State Transfer | Kiến trúc thiết kế API tiêu chuẩn, coi mọi thực thể (bài báo, ghi chú, phiên nghiên cứu) là một "tài nguyên" (Resource) và thao tác với chúng thông qua các phương thức HTTP chuẩn (`GET`, `POST`, `PATCH`, `DELETE`). |
| **AIP-136 Custom Methods (`:<verb>`)** | Google Cloud API Improvement Proposal 136 | Quy chuẩn thiết kế API của Google dành cho các hành động nghiệp vụ đặc biệt không thể diễn đạt trọn vẹn bằng động từ HTTP cơ bản. Cú pháp sử dụng dấu hai chấm `:` gắn vào sau URL, ví dụ: `POST /drafts/{id}:compile` (yêu cầu biên dịch mã LaTeX sang PDF) hoặc `POST /documents/{id}:reindex` (yêu cầu tính toán lại vector). |
| **AIP-151 Streaming & Operations** | Google Cloud AIP-151 (LRO & Streams) | Chuẩn mực cho các tác vụ tốn nhiều thời gian và các luồng phản hồi dữ liệu theo thời gian thực (Real-time Streaming). |
| **SSE (Server-Sent Events)** | Server-Sent Events (HTML5 Protocol) | Giao thức truyền dữ liệu một chiều thời gian thực từ máy chủ về trình duyệt qua một kết nối HTTP duy nhất. Giúp giao diện hiển thị từng chữ gõ ra mượt mà như ChatGPT (`event: token`) mà không phải tải lại toàn bộ trang web. |
| **OCC (Khóa Lạc Quan)** | Optimistic Concurrency Control | Cơ chế chống xung đột dữ liệu khi nhiều người hoặc nhiều tab cùng sửa một tài liệu: Trước khi lưu, hệ thống kiểm tra xem tài liệu có bị ai khác sửa mất chưa. Nếu đã bị người khác sửa trước, hệ thống sẽ từ chối lưu bằng mã lỗi `412 Precondition Failed` thay vì ghi đè làm mất công sức của người khác. |
| **`ETag` & `If-Match`** | RFC 9110 / RFC 7232 HTTP Headers | Bộ đôi tiêu đề HTTP thực thi khóa lạc quan: Máy chủ trả về mã hiệu phiên bản trong tiêu đề `ETag: "v1"`. Khi Client gửi yêu cầu sửa, Client phải đính kèm tiêu đề `If-Match: "v1"`. Nếu máy chủ nhận thấy version hiện tại đã nhảy lên `"v2"`, máy chủ lập tức từ chối với mã lỗi `412`. |
| **RFC 8288** | Web Linking Specification (RFC 8288) | Tiêu chuẩn quốc tế cho điều hướng phân trang; trả về các đường dẫn liên kết đầy đủ (`first`: trang đầu, `prev`: trang trước, `self`: trang hiện tại, `next`: trang kế tiếp, `last`: trang cuối) giúp frontend chuyển trang an toàn và chính xác tuyệt đối. |
| **Idempotency (`Idempotency-Key`)** | Idempotency Pattern (Tính lũy đẳng) | Đảm bảo khi người dùng bấm nút "Gửi" nhiều lần do mạng chập chờn hoặc máy chủ tự động thử lại (retry), hệ thống chỉ thực thi nghiệp vụ 1 lần duy nhất trong vòng 24 giờ. |
| **HTTP 499 (Client Closed Request)** | Client Disconnect Status Code | Mã trạng thái ghi nhận khi người dùng đóng tab trình duyệt hoặc bấm nút "Hủy" (Cancel) giữa chừng khi máy chủ đang xử lý; backend sẽ lập tức dừng container Sandbox ngay (`docker kill`) để tiết kiệm RAM và CPU. |
| **Bounding Box** | Bounding Box Coordinate `[x0, y0, x1, y1, page]` | Khung chữ nhật bao quanh đoạn văn bản, hình vẽ hoặc công thức toán học trên trang PDF. Tọa độ được chuẩn hóa tỉ lệ `[0.0, 1.0]` với gốc tọa độ `(0.0, 0.0)` nằm ở góc trên cùng bên trái (Top-Left) và số trang bắt đầu từ 1 (`page >= 1`). |
| **Single Resource Envelope** | Single Resource JSON Envelope | Vỏ bọc bao thư phản hồi cho 1 tài nguyên duy nhất, luôn gồm 3 trường: `success` (trạng thái thành công/thất bại), `data` (dữ liệu chính) và `meta` (mã vết `request_id`, thời gian `timestamp`). |
| **Paginated Collection Envelope** | Collection Envelope Wrapper | Vỏ bọc bao thư cho danh sách phân trang, bổ sung thêm đối tượng `meta` (tổng số bản ghi, trang hiện tại, số bản ghi mỗi trang, tổng số trang) và đối tượng `links` (đường dẫn RFC 8288). |

---

## 1. QUY CHUẨN DỮ LIỆU & BẢNG MÃ LỖI TOÀN HỆ THỐNG

### 1.1. Quy chuẩn Bất biến Tọa độ Bounding Box & Khổ Trang (Spatial Invariants)
Mọi tọa độ trích dẫn trong hệ thống VeriScholar tuân thủ các quy tắc bất biến:
- Mảng 2 chiều chứa các hộp chữ nhật: `[[x0, y0, x1, y1, page], ...]`
  - Hỗ trợ câu/đoạn trích dẫn vắt qua 2 cột hoặc vắt qua 2 trang liên tiếp (mỗi vùng là 1 phần tử con).
  - **Quy tắc Non-null tuyệt đối:** Nếu một công thức, bảng biểu hoặc đoạn văn không xác định được tọa độ chính xác, trường này **BẮT BUỘC trả về mảng rỗng `[]`**, tuyệt đối **KHÔNG** trả về `null` để bảo vệ frontend React/TypeScript khỏi lỗi crash `TypeError: Cannot read properties of null`.
- `x0, y0, x1, y1`: Tọa độ chuẩn hóa số thực trong đoạn `[0.0, 1.0]`.
- Gốc tọa độ `(0.0, 0.0)` nằm ở **góc trên cùng bên trái (Top-Left)** của trang tài liệu theo hệ trục thị giác thực tế (Visual Reading Coordinate System).
- `page`: Số trang nguyên dương, đánh số từ 1 (**1-indexed**, `page >= 1`).
- **Thông số khổ trang & góc xoay gốc:** Mọi tài nguyên trang/tài liệu trả về kèm `page_dimensions: [width_pt, height_pt]` (72 DPI) và `rotation_deg: 0 | 90 | 180 | 270` để PDF.js Canvas render khung highlight viền vàng khớp chính xác tuyệt đối 100%.

### 1.2. Chuẩn Phản Hồi Thành Công Đơn Lẻ (Single Resource Envelope)
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
    "timestamp": "2026-09-12T10:00:00.000Z"
  }
}
```

### 1.3. Chuẩn Phản Hồi Danh Sách Phân Trang (RFC 8288 Paginated Collection Envelope)
Áp dụng cho mọi danh sách tập hợp (`/documents`, `/chunks`, `/notes`, `/drafts`, `/folders`, `/sessions`):
```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "total": 148,
    "page": 2,
    "per_page": 50,
    "total_pages": 3,
    "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
    "timestamp": "2026-09-12T10:00:00.000Z"
  },
  "links": {
    "first": "/api/v1/documents?page=1&per_page=50",
    "prev": "/api/v1/documents?page=1&per_page=50",
    "self": "/api/v1/documents?page=2&per_page=50",
    "next": "/api/v1/documents?page=3&per_page=50",
    "last": "/api/v1/documents?page=3&per_page=50"
  }
}
```
*(Ghi chú RFC 8288: Khi client ở trang đầu `page=1`, trường `prev` trả về `null`. Khi client ở trang cuối cùng, trường `next` trả về `null`).*

### 1.4. Quy Chuẩn Khử Trùng Lặp Idempotency Key (24-Hour Retention Window)
- Mọi endpoint đột biến tài nguyên nặng (`:compile`, `:synthesize`, `messages`, `bulk-import`) hỗ trợ HTTP Header `Idempotency-Key: <UUID>`.
- **Cửa sổ lưu trữ:** Khóa được lưu trữ trên Redis với thời gian sống **TTL = 24 giờ** (86.400 giây).
- Trong vòng 24 giờ, mọi request gửi lại cùng khóa sẽ nhận lại ngay lập tức phản hồi ban đầu từ Redis cache (kèm header `X-Cache: Idempotent-Hit`) mà không tái thực thi pipeline tốn kém.

### 1.5. Chuẩn Phản Hồi Thất Bại & Bảng Mã Lỗi Toàn Hệ Thống
Thống nhất với Pydantic schema [`ErrorResponse`](apps/api/src/api/schemas/error.py):
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_PROCESSING",
    "message": "Bài báo đang trong tiến trình bóc tách/nhúng vector. Vui lòng chờ trạng thái completed.",
    "field": "id",
    "action": "Vui lòng kiểm tra tiến độ tại GET /api/v1/documents/{id}/status."
  },
  "meta": {
    "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
    "timestamp": "2026-09-12T10:00:00.000Z"
  }
}
```

#### Bảng Mã Lỗi Chuẩn Hóa Toàn Hệ Thống:
| Mã Lỗi (`error.code`) | HTTP Status / SSE Frame | Field Gây Lỗi | Ý Nghĩa Kỹ Thuật & Hành Động Khắc Phục |
| :--- | :---: | :---: | :--- |
| `DOCUMENT_PROCESSING` | `409 Conflict` | `id` | Bài báo đang trong quá trình parse/embed. Chờ hoàn tất trước khi truy vấn summary/messages. |
| `UNSUPPORTED_PDF_ENCRYPTED` | `422 Unprocessable Entity` | `file` | PDF bị đặt mật khẩu bảo vệ hoặc bị khóa DRM. Từ chối tiếp nhận ngay lập tức. |
| `UNSUPPORTED_PDF_FORMAT` | `422 Unprocessable Entity` | `file` | Tệp PDF bị hỏng cấu trúc (corrupted), không đọc được luồng byte hoặc không phải định dạng PDF. |
| `SESSION_CAPACITY_EXCEEDED` | `422 Unprocessable Entity` | `document_id` | Phiên đọc vượt quá giới hạn tối đa 5 bài báo. Cần bỏ bớt bài hoặc lưu vào Thư viện (Module 4). |
| `QUERY_NO_GROUNDED_CONTEXT` | `200 OK` (`status: "abstention"`) hoặc SSE `finish_reason: "abstention"` | `question` | Không tìm thấy bất kỳ đoạn trích dẫn (chunks) nào có điểm liên quan >= 0.35. Trả lời từ chối nhã nhặn (Abstention Prompting) thay vì 404. |
| `CONTEXT_WINDOW_EXCEEDED` | `422 Unprocessable Entity` | `question` | Ngân sách ngữ cảnh vượt trần 3.500 tokens sau khi áp dụng Global Token Budgeting. |
| `CONCURRENCY_CONFLICT` | `412 Precondition Failed` | `Header If-Match` | Xung đột phiên bản khóa lạc quan (OCC) theo chuẩn RFC 9110 / RFC 7232. Client cần tải lại dữ liệu mới nhất và gửi lại với ETag mới. |
| `LATEX_SYNTAX_ERROR` | `422 Unprocessable Entity` | `content` | Lỗi cú pháp LaTeX tĩnh phát hiện bởi AST Linter trước khi đưa vào container Sandbox. |
| `LATEX_COMPILE_TIMEOUT` | SSE `event: error` (hoặc `504 Gateway Timeout` nếu non-streaming) | `id` | Quá trình biên dịch trong Sandbox vượt ngưỡng cứng 15 giây (Denial of Service protection). |
| `LATEX_SELF_HEALING_FAILED`| `422 Unprocessable Entity` | `patch_history` | Vòng lặp tự vá lỗi biên dịch LaTeX thất bại sau 3 lần thử. Chuyển sang can thiệp thủ công. |
| `RATE_LIMIT_EXCEEDED` | `429 Too Many Requests` | `null` | Vượt quá hạn ngạch gọi API ngoài hoặc Sandbox. Trả về kèm header `Retry-After`. |
| `RESOURCE_NOT_FOUND` | `404 Not Found` | `id` | Không tìm thấy tài liệu, chunk, note, draft hoặc session tương ứng trên URI. |
| `SHARE_LINK_REVOKED` | `410 Gone` | `token` | Liên kết chia sẻ công khai đã bị chủ sở hữu thu hồi hoặc xóa bỏ. |

---

## 2. BẢNG TỔNG HỢP TOÀN BỘ ENDPOINTS HỆ THỐNG VERISCHOLAR

```text
========================================================================================================
MODULE 1: ĐỌC SÂU & ĐỐI THOẠI KÉP ĐA BÀI BÁO (1 - 5 PAPERS & NOTES)
========================================================================================================
POST   /api/v1/documents                          # 1. Tải lên PDF bài báo (nhận session_id tùy chọn)
GET    /api/v1/documents                          # 2. Danh sách bài báo (phân trang page/per_page)
GET    /api/v1/documents/{id}                     # 3. Lấy metadata chi tiết (page_dimensions, rotation_deg)
GET    /api/v1/documents/{id}/file                # 4. Stream nhị phân PDF cho Canvas (HTTP 206 Partial Content)
GET    /api/v1/documents/{id}/status              # 5. Polling tiến độ bóc tách (stage: running_ocr, progress)
POST   /api/v1/documents/{id}:star                # 6. Atomic Promotion Transition (lưu vào thư viện cá nhân)
DELETE /api/v1/documents/{id}                     # 7. Xóa bài báo theo đồ thị phụ thuộc (Zero-Retention)
POST   /api/v1/documents/{id}:parse               # 8. Custom Method: Kích hoạt / Bóc tách lại với Idempotency
POST   /api/v1/documents/{id}:extract-references  # 9. Custom Method: Bóc tách danh mục tài liệu tham khảo
GET    /api/v1/documents/{id}/structure           # 10. Singleton: Cấu trúc bài báo (TOC, Headings, Sections)
GET    /api/v1/documents/{id}/chunks              # 11. Danh sách Chunks (phân trang + include_content)
GET    /api/v1/documents/{id}/chunks/{chunk_id}   # 12. Chi tiết 1 đoạn bằng chứng
GET    /api/v1/documents/{id}/summary             # 13. Singleton: Lấy bản tóm tắt 3 ý cốt lõi
POST   /api/v1/documents/{id}/summary:generate    # 14. Custom Method: Sinh mới tóm tắt 3 ý
GET    /api/v1/documents/{id}/export-pdf          # 15. Xuất file PDF kèm Native Annotations chuẩn ISO

--------------------------------------------------------------------------------------------------------
SỔ TAY NGHIÊN CỨU & AI TỔNG HỢP (SMART NOTEBOOK & KNOWLEDGE DIGEST)
--------------------------------------------------------------------------------------------------------
POST   /api/v1/notes                              # 16. Lưu trích dẫn & ghi chú cá nhân (Add to Note)
GET    /api/v1/notes                              # 17. Danh sách ghi chú (lọc theo document_id, tag, folder_id)
GET    /api/v1/notes/{id}                         # 18. Chi tiết ghi chú kèm Frozen Evidence Snapshot
PATCH  /api/v1/notes/{id}                         # 19. Sửa ghi chú / tag (Kiểm soát đồng thời OCC If-Match)
DELETE /api/v1/notes/{id}                         # 20. Xóa ghi chú khỏi sổ tay
POST   /api/v1/notes:synthesize                   # 21. AI Tổng hợp ghi chú thành bài học (3 modes + Badges)

========================================================================================================
MODULE 2: HỖ TRỢ VIẾT BÀI, BIÊN DỊCH SANDBOX & KIỂM CHỨNG SỰ THẬT (SAFE)
========================================================================================================
POST   /api/v1/drafts                             # 22. Khởi tạo bản thảo LaTeX / Markdown mới
GET    /api/v1/drafts                             # 23. Danh sách bản thảo người dùng (phân trang)
GET    /api/v1/drafts/{id}                        # 24. Chi tiết bản thảo kèm mã nguồn và version OCC
PUT    /api/v1/drafts/{id}                        # 25. Cập nhật toàn bộ mã nguồn bản thảo (OCC If-Match)
PATCH  /api/v1/drafts/{id}                        # 26. Cập nhật từng phần (tiêu đề, metadata)
DELETE /api/v1/drafts/{id}                        # 27. Xóa bản thảo
POST   /api/v1/drafts/{id}:compile                # 28. Biên dịch Sandbox 2 tầng & Vòng lặp Agentic (SSE Stream)
GET    /api/v1/drafts/{id}/preview-pdf            # 29. Stream file PDF kết quả biên dịch Live Preview
POST   /api/v1/drafts/{id}:verify-claims          # 30. Custom Method: Quy trình 4 bước SAFE kiểm chứng sự thật
GET    /api/v1/drafts/{id}/bundle                 # 31. Xuất Camera-Ready Bundle (.zip đầy đủ hoặc .pdf)
POST   /api/v1/drafts/{id}/comments               # 32. Phản biện nhóm: để lại bình luận trên từng câu/dòng
GET    /api/v1/drafts/{id}/comments               # 33. Lấy danh sách bình luận phản biện (phân trang)

========================================================================================================
MODULE 3: KHAI THÁC TÀI LIỆU THAM KHẢO & ĐỒ THỊ TRI THỨC
========================================================================================================
POST   /api/v1/references:resolve                 # 34. Batch Resolving & Leaky Bucket qua Global Academic Cache
GET    /api/v1/documents/{id}/graph               # 35. Khai thác Đồ thị Trích dẫn (Cycle Breaking, k-hop <= 2)

========================================================================================================
MODULE 4: QUẢN LÝ THƯ VIỆN BÀI BÁO CÁ NHÂN & TỔNG HỢP ĐA BÀI
========================================================================================================
GET    /api/v1/folders                            # 36. Danh sách thư mục đề tài nghiên cứu
POST   /api/v1/folders                            # 37. Tạo thư mục đề tài mới
PATCH  /api/v1/folders/{id}                       # 38. Đổi tên / Di chuyển thư mục
DELETE /api/v1/folders/{id}                       # 39. Xóa thư mục đề tài
GET    /api/v1/library/documents                  # 40. Danh sách bài báo trong thư viện cá nhân (đã Star)
POST   /api/v1/library/documents:bulk-import      # 41. Nạp hàng loạt 10 - 50 bài báo (.bib hoặc DOI list)
POST   /api/v1/folders/{id}:synthesize            # 42. Agentic Hierarchical RAG trên thư mục (Sufficiency Gate)
POST   /api/v1/library:synthesize                 # 43. Agentic Hierarchical RAG trên toàn bộ thư viện
POST   /api/v1/library:compare                    # 44. Custom Method: Dựng bảng so sánh tự động giữa các bài báo

========================================================================================================
QUẢN LÝ PHIÊN NGHIÊN CỨU & CHIA SẺ CỘNG TÁC (SESSION PERSISTENCE & SHARING)
========================================================================================================
POST   /api/v1/sessions                           # 45. Khởi tạo phiên nghiên cứu đa bài mới (Research Session)
GET    /api/v1/sessions                           # 46. Lấy lịch sử các phiên nghiên cứu (Sidebar History)
GET    /api/v1/sessions/{id}                      # 47. Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)
PATCH  /api/v1/sessions/{id}                      # 48. Cập nhật tiêu đề / metadata phiên nghiên cứu (OCC If-Match)
PATCH  /api/v1/sessions/{id}/viewport             # 49. Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)
DELETE /api/v1/sessions/{id}                      # 50. Xóa phiên nghiên cứu
POST   /api/v1/sessions/{id}/documents            # 51. Nạp bài vào phiên (Pure JSON: url hoặc document_id)
POST   /api/v1/sessions/{id}/messages             # 52. Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)
GET    /api/v1/sessions/{id}/messages             # 53. Lấy lịch sử hội thoại của phiên (phân trang)
DELETE /api/v1/sessions/{id}/messages             # 54. Xóa lịch sử hội thoại của phiên (Idempotent 204)
POST   /api/v1/sessions/{id}:restore-archived     # 55. Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL
POST   /api/v1/shares                             # 56. Tạo liên kết chia sẻ công khai (Note, Draft, Collection)
GET    /api/v1/shares/{token}                     # 57. Xem tài nguyên chia sẻ (Public Read-only, No Auth)
GET    /api/v1/shares/{token}/file                # 58. Stream PDF cho khách xem chia sẻ (No Auth, HTTP 206)
DELETE /api/v1/shares/{token}                     # 59. Thu hồi chia sẻ tức thời (Instant Revocation -> 410 Gone)
```

---

## 3. MODULE 1: ĐỌC SÂU & ĐỐI THOẠI KÉP ĐA BÀI BÁO (DEEP READING API)

### 3.1. `POST /api/v1/documents` (Tải lên PDF bài báo)
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: Binary PDF (`max 50MB`, header `%PDF`, tối đa 100 trang).
  - `title`: `string` (tùy chọn, tối đa 255 ký tự).
  - `auto_parse`: `boolean` (mặc định `true`). Nếu `true`, tự động kích hoạt Ingestion Pipeline; nếu `false`, chỉ lưu trữ an toàn và đặt trạng thái `uploaded`.
  - `session_id`: `UUID` (tùy chọn). Nếu truyền lên, hệ thống sẽ tự động liên kết bài báo vừa nạp vào phiên nghiên cứu tương ứng trong một giao dịch ACID.
- **Headers:** `Idempotency-Key: <UUID>` (tùy chọn).
- **Phản hồi:**
  - `202 Accepted` (File mới, bắt đầu bóc tách ngầm):
    ```json
    {
      "success": true,
      "data": {
        "id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "filename": "attention_is_all_you_need.pdf",
        "file_size_bytes": 2215144,
        "content_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
        "status": "processing",
        "stage": "queued",
        "progress": 0,
        "is_persistent": false,
        "session_id": "a1b2c3d4-e5f6-47a8-b9c0-1234567890de",
        "created_at": "2026-09-12T10:00:00.000Z",
        "links": {
          "self_url": "/api/v1/documents/c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
          "status_url": "/api/v1/documents/c7a2e8c5-9231-419b-a0eb-4a1796d8e05c/status",
          "file_url": "/api/v1/documents/c7a2e8c5-9231-419b-a0eb-4a1796d8e05c/file",
          "parse_url": "/api/v1/documents/c7a2e8c5-9231-419b-a0eb-4a1796d8e05c:parse"
        }
      },
      "meta": {
        "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
        "timestamp": "2026-09-12T10:00:00.000Z"
      }
    }
    ```
  - `200 OK` (Deduplication Cache Hit - Đã bóc tách từ trước với cùng `content_hash`).

### 3.2. `GET /api/v1/documents` (Danh sách bài báo)
- **Method:** `GET`
- **Query Params:** `page` (int, default 1), `per_page` (int, default 20, max 100), `status` (string, filter).
- **Response (`200 OK` - Paginated Collection Envelope):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "filename": "attention_is_all_you_need.pdf",
        "title": "Attention Is All You Need",
        "status": "completed",
        "is_persistent": false,
        "created_at": "2026-09-12T10:00:00.000Z"
      }
    ],
    "meta": {
      "total": 1,
      "page": 1,
      "per_page": 20,
      "total_pages": 1,
      "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
      "timestamp": "2026-09-12T10:00:00.000Z"
    },
    "links": {
      "first": "/api/v1/documents?page=1&per_page=20",
      "prev": null,
      "self": "/api/v1/documents?page=1&per_page=20",
      "next": null,
      "last": "/api/v1/documents?page=1&per_page=20"
    }
  }
  ```

### 3.3. `GET /api/v1/documents/{id}` (Chi tiết tài liệu kèm Spatial Metadata)
- **Method:** `GET`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "filename": "attention_is_all_you_need.pdf",
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "publication_year": 2017,
      "doi": "10.48550/arXiv.1706.03762",
      "page_count": 11,
      "chunk_count": 48,
      "file_size_bytes": 2215144,
      "status": "completed",
      "is_persistent": false,
      "pages_metadata": [
        { "page_number": 1, "dimensions": [595.28, 841.89], "rotation_deg": 0 },
        { "page_number": 6, "dimensions": [841.89, 595.28], "rotation_deg": 90 }
      ],
      "created_at": "2026-09-12T10:00:00.000Z"
    },
    "meta": { ... }
  }
  ```

### 3.4. `GET /api/v1/documents/{id}/file` (Stream PDF nhị phân cho Canvas)
- **Method:** `GET`
- **Headers Hỗ trợ:** `Range: bytes=0-1024` (Hỗ trợ HTTP 206 Partial Content để lazy-load từng trang trong PDF.js Canvas).
- **Response Headers:** `Content-Type: application/pdf`, `Accept-Ranges: bytes`, `Content-Disposition: inline; filename="..."`.

### 3.5. `GET /api/v1/documents/{id}/status` (Polling tiến độ bóc tách)
- **Method:** `GET`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "status": "processing",
      "stage": "running_ocr",
      "progress": 45,
      "stages_detail": {
        "validation": "completed",
        "layout_detection": "completed",
        "ocr": "in_progress",
        "chunking": "pending",
        "embedding": "pending"
      },
      "error_message": null
    },
    "meta": { ... }
  }
  ```

### 3.6. `POST /api/v1/documents/{id}:star` (Atomic Promotion Transition)
- **Method:** `POST`
- **URI:** `/api/v1/documents/{id}:star`
- **Request Body (JSON):**
  ```json
  {
    "folder_id": "7a1b8c2d-93e4-419b-b0eb-5a1796d8e05d"
  }
  ```
- **Response (`200 OK`):** Trả về tài liệu với `is_persistent: true` và `folder_id` đã gán trong một giao dịch ACID.

### 3.7. `DELETE /api/v1/documents/{id}` (Graph Cascade Purge - Zero Retention)
- **Method:** `DELETE`
- **Response (`204 No Content`):** Thực thi `ON DELETE CASCADE` xóa toàn bộ chunks, vectors và metadata của người dùng trong PostgreSQL; giảm `ref_count` tại `document_storage_blobs` (xóa vĩnh viễn tệp PDF vật lý trên đĩa khi `ref_count == 0`); dọn dẹp quan hệ tạm trong Graph và chuyển ghi chú liên quan sang trạng thái `[Source Document Detached]`.

### 3.8. `POST /api/v1/documents/{id}:parse` (Custom Method: Bóc tách lại với Idempotency)
- **Method:** `POST`
- **URI:** `/api/v1/documents/{id}:parse`
- **Headers:** `Idempotency-Key: <UUID>`
- **Request Body (JSON):**
  ```json
  {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "extract_tables": true,
    "force_reparse": false
  }
  ```
- **Response (`202 Accepted`):** Trả về tiến trình bóc tách mới được kích hoạt.

### 3.9. `POST /api/v1/documents/{id}:extract-references` (Bóc tách Danh mục Tham khảo)
- **Method:** `POST`
- **URI:** `/api/v1/documents/{id}:extract-references`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "total_extracted": 38,
      "references": [
        {
          "ref_index": 1,
          "raw_text": "Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.",
          "parsed": {
            "title": "Layer normalization",
            "authors": ["Jimmy Lei Ba", "Jamie Ryan Kiros", "Geoffrey E Hinton"],
            "year": 2016,
            "arxiv_id": "1607.06450",
            "doi": null
          }
        }
      ]
    },
    "meta": { ... }
  }
  ```

### 3.10. `GET /api/v1/documents/{id}/structure` (Singleton Sub-resource: Cấu trúc bài báo)
- **Method:** `GET`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      "abstract_bounding_boxes": [[0.1, 0.2, 0.9, 0.28, 1]],
      "sections": [
        { "title": "1 Introduction", "page_number": 1, "bounding_boxes": [[0.1, 0.35, 0.5, 0.38, 1]] },
        { "title": "2 Background", "page_number": 2, "bounding_boxes": [[0.1, 0.15, 0.5, 0.18, 2]] },
        { "title": "3 Model Architecture", "page_number": 2, "bounding_boxes": [[0.5, 0.45, 0.9, 0.48, 2]] }
      ]
    },
    "meta": { ... }
  }
  ```

### 3.11. `GET /api/v1/documents/{id}/chunks` (Danh sách Chunks - Phân trang & Tối ưu Băng thông)
- **Method:** `GET`
- **Query Parameters:**
  - `page`: `integer` (mặc định `1`).
  - `per_page`: `integer` (mặc định `50`, tối đa `200`).
  - `page_number`: `integer` (tùy chọn, lọc theo trang).
  - `include_content`: `boolean` (mặc định `true`). Nếu `false`, trường `content` trả về `null` (`Optional[str] = None`) để giảm 80% băng thông tải bounding boxes ban đầu.
- **Response (`200 OK` - Paginated Collection Envelope):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "8f3b110e-8f20-4e09-91dc-879e9508d812",
        "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "chunk_index": 3,
        "page_number": 2,
        "content": "The Transformer is the first transduction model relying entirely on self-attention...",
        "bounding_boxes": [[0.125, 0.342, 0.875, 0.395, 2]],
        "token_count": 84
      }
    ],
    "meta": {
      "total": 48,
      "page": 1,
      "per_page": 50,
      "total_pages": 1,
      "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
      "timestamp": "2026-09-12T10:00:00.000Z"
    },
    "links": {
      "first": "/api/v1/documents/c7a2e8c5-.../chunks?page=1&per_page=50",
      "prev": null,
      "self": "/api/v1/documents/c7a2e8c5-.../chunks?page=1&per_page=50",
      "next": null,
      "last": "/api/v1/documents/c7a2e8c5-.../chunks?page=1&per_page=50"
    }
  }
  ```

### 3.12. `GET /api/v1/documents/{id}/chunks/{chunk_id}` (Chi tiết đoạn bằng chứng)
- **Method:** `GET`
- **Response (`200 OK`):** Trả về đầy đủ nội dung chunk, vector embedding dimension, và bounding boxes.

### 3.13. `GET /api/v1/documents/{id}/summary` (Singleton: Bản tóm tắt 3 ý cốt lõi)
- **Method:** `GET`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "problem_statement": {
        "text": "Mô hình RNN/LSTM xử lý tuần tự không thể song song hóa hiệu quả trên chuỗi dài.",
        "bounding_boxes": [[0.1, 0.4, 0.9, 0.45, 1]]
      },
      "contributions": {
        "text": "Đề xuất kiến trúc thuần Self-Attention đầu tiên, tăng tốc độ huấn luyện gấp nhiều lần.",
        "bounding_boxes": [[0.1, 0.5, 0.9, 0.58, 2]]
      },
      "limitations": {
        "text": "Độ phức tạp tính toán O(N^2) với độ dài câu và thiếu khả năng quy nạp cấu trúc đệ quy.",
        "bounding_boxes": [[0.1, 0.6, 0.9, 0.65, 6]]
      }
    },
    "meta": { ... }
  }
  ```

### 3.14. `POST /api/v1/documents/{id}/summary:generate` (Custom Method: Sinh tóm tắt 3 ý)
- **Method:** `POST`
- **URI:** `/api/v1/documents/{id}/summary:generate`
- **Headers:** `Idempotency-Key: <UUID>`
- **Request Body:** `{ "force": false }`
- **Response (`200 OK`):** Trả về bản tóm tắt 3 ý đã sinh.

### 3.15. `GET /api/v1/documents/{id}/export-pdf` (Xuất PDF kèm Native Annotations)
- **Method:** `GET`
- **Query Params:** `include_highlights=true` (boolean).
- **Response Headers:** `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="annotated_paper.pdf"`.
- **Mô tả:** Trả về luồng nhị phân PDF được nhúng Native ISO Highlight Annotations mở xem được trên Acrobat, Foxit, GoodNotes.

---

### SỔ TAY NGHIÊN CỨU & AI TỔNG HỢP (SMART NOTEBOOK)

### 3.16. `POST /api/v1/notes` (Tạo ghi chú mới)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "chunk_id": "8f3b110e-8f20-4e09-91dc-879e9508d812",
    "selected_text": "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
    "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]],
    "page_number": 4,
    "user_note": "Công thức cốt lõi cần trích dẫn.",
    "tags": ["methodology", "core-formula"]
  }
  ```
- **Response (`201 Created`):**
  - **Headers:** `ETag: "v1"`
  - **Body:** Trả về ghi chú kèm `version: 1`, `frozen_snapshot` lưu toàn vẹn ngữ cảnh phòng khi bài báo gốc bị xóa.

### 3.17. `GET /api/v1/notes` (Danh sách ghi chú)
- **Method:** `GET`
- **Query Params:** `document_id` (UUID, tùy chọn), `tag` (string, tùy chọn), `page` (int, default 1), `per_page` (int, default 50).
- **Response (`200 OK` - Paginated Collection Envelope).**

### 3.18. `GET /api/v1/notes/{id}` (Chi tiết ghi chú)
- **Method:** `GET`
- **Response (`200 OK`):** Trả về chi tiết ghi chú kèm `ETag: "v1"`.

### 3.19. `PATCH /api/v1/notes/{id}` (Cập nhật ghi chú có OCC)
- **Method:** `PATCH`
- **Headers:** `If-Match: "v1"` (**Bắt buộc**).
- **Request Body (JSON):**
  ```json
  {
    "user_note": "Công thức cốt lõi (đã kiểm chứng lại số mũ).",
    "tags": ["methodology", "verified"]
  }
  ```
- **Response (`200 OK`):** Trả về dữ liệu đã cập nhật kèm header `ETag: "v2"` và trường `version: 2`.
- **Error (`412 Precondition Failed`):** Nếu `If-Match` không khớp ETag hiện tại trong DB (`CONCURRENCY_CONFLICT`).

### 3.20. `DELETE /api/v1/notes/{id}` (Xóa ghi chú)
- **Method:** `DELETE`
- **Response (`204 No Content`).**

### 3.21. `POST /api/v1/notes:synthesize` (AI Tổng Hợp Ghi Chú Thành Bản Đúc Kết)
- **Method:** `POST`
- **URI:** `/api/v1/notes:synthesize`
- **Headers:** `Idempotency-Key: <UUID>`
- **Request Body (JSON):**
  ```json
  {
    "note_ids": [
      "3d10c24e-7212-40f9-b883-cf3da8490a15",
      "4e21d35f-8323-41a0-c994-df4eb9501b26"
    ],
    "mode": "concept_lesson",
    "language": "vi",
    "target_title": "Bản Đúc Kết Kiến Trúc Scaled Dot-Product Attention"
  }
  ```
- **Response (`200 OK`):** Trả về nội dung tổng hợp Markdown kèm danh sách `interactive_badges`.

---

## 4. MODULE 2: HỖ TRỢ VIẾT BÀI, BIÊN DỊCH SANDBOX & KIỂM CHỨNG SAFE (DRAFTING API)

### 4.1. `POST /api/v1/drafts` (Khởi tạo bản thảo mới)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "title": "Nghiên cứu Cải tiến Tốc độ Reranker Đa Ngữ",
    "format": "latex",
    "template": "ieee_conference",
    "initial_content": "\\documentclass[conference]{IEEEtran}\n\\begin{document}\n\\title{...}\n\\maketitle\n\\end{document}"
  }
  ```
- **Response (`201 Created`):**
  - **Headers:** `Location: /api/v1/drafts/8b12c34d-5678-49ab-cdef-1234567890ab`, `ETag: "v1"`.
  - **Body:** Trả về đối tượng `draft` với `version: 1`.

### 4.2. `GET /api/v1/drafts` (Danh sách bản thảo)
- **Method:** `GET`
- **Query Params:** `page` (int, default 1), `per_page` (int, default 20).
- **Response (`200 OK` - Paginated Collection Envelope).**

### 4.3. `GET /api/v1/drafts/{id}` (Chi tiết bản thảo)
- **Method:** `GET`
- **Response (`200 OK`):** Trả về chi tiết mã nguồn bản thảo kèm header `ETag: "v1"`.

### 4.4. `PUT /api/v1/drafts/{id}` (Cập nhật toàn bộ mã nguồn với RFC 9110 / RFC 7232 OCC)
- **Method:** `PUT`
- **Headers:** `If-Match: "v1"` (**Bắt buộc** theo chuẩn HTTP OCC).
- **Request Body (JSON):**
  ```json
  {
    "content": "\\documentclass[conference]{IEEEtran}\n..."
  }
  ```
- **Phản hồi:**
  - `200 OK`: Cập nhật thành công. Trả về header `ETag: "v2"` và `version: 2`.
  - `412 Precondition Failed`: Nếu header `If-Match` không khớp phiên bản hiện tại trong DB (`CONCURRENCY_CONFLICT`).

### 4.5. `PATCH /api/v1/drafts/{id}` (Cập nhật từng phần bản thảo)
- **Method:** `PATCH`
- **Headers:** `If-Match: "v1"`.
- **Request Body:** `{ "title": "Tiêu đề cập nhật" }`.
- **Response (`200 OK`):** Trả về dữ liệu đã cập nhật kèm header `ETag: "v2"`.
- **Error (`412 Precondition Failed`):** Nếu `If-Match` không khớp.

### 4.6. `DELETE /api/v1/drafts/{id}` (Xóa bản thảo)
- **Method:** `DELETE`
- **Response (`204 No Content`).**

### 4.7. `POST /api/v1/drafts/{id}:compile` (Biên Dịch Trong Sandbox & Agentic Self-Healing via SSE Stream)
- **Method:** `POST`
- **URI:** `/api/v1/drafts/{id}:compile`
- **Accept Header:** `text/event-stream` (**Bắt buộc** để loại trừ hoàn toàn nguy cơ `504 Gateway Timeout` khi Self-Healing chạy từ 30 - 60s).
- **Headers:** `Idempotency-Key: <UUID>`.
- **Request Body (JSON):**
  ```json
  {
    "compiler_engine": "tectonic",
    "auto_self_heal": true,
    "max_heal_attempts": 3
  }
  ```
- **Dòng sự kiện SSE mẫu:**
  ```text
  event: linter_status
  data: {"status": "passed", "duration_ms": 42}

  event: sandbox_started
  data: {"engine": "tectonic", "container_id": "sbx_8a9b", "timestamp": "2026-09-12T10:10:01.000Z"}

  event: compile_failed
  data: {"attempt": 1, "error": "Undefined control sequence \\blabla at line 24", "action": "triggering_agentic_patch"}

  event: healing_attempt
  data: {"attempt": 1, "diff_summary": "Replaced undefined sequence with \\textbf{...}", "status": "recompiling"}

  event: compile_success
  data: {"draft_id": "8b12c34d-...", "pdf_preview_url": "/api/v1/drafts/8b12c34d-.../preview-pdf", "total_heal_attempts": 1, "total_duration_ms": 3420}
  ```
  *(Trường hợp timeout tại giây thứ 15, server phát frame lỗi an toàn:*
  ```text
  event: error
  data: {"code": "LATEX_COMPILE_TIMEOUT", "message": "Quá trình biên dịch trong Sandbox vượt ngưỡng cứng 15 giây.", "action": "Vui lòng tối ưu lại các gói package hoặc kiểm tra vòng lặp macro."}
  ```
  *sau đó đóng kết nối một cách an toàn).*
- **Xử lý Ngắt kết nối Máy trạm khi Đang Biên dịch (Sandbox Cancellation):**
  Trong quá trình stream SSE của `POST /drafts/{id}:compile`, nếu client đóng kết nối (HTTP 499 - Client Closed Request), server bắt ngoại lệ ngắt dòng, lập tức gửi lệnh dừng container Sandbox (`docker kill {container_id}`) và giải phóng tài nguyên CPU/RAM, ngăn chặn triệt để tình trạng container mồ côi chạy ngầm.

### 4.8. `GET /api/v1/drafts/{id}/preview-pdf` (Stream PDF Live Preview)
- **Method:** `GET`
- **Response Headers:** `Content-Type: application/pdf`, `Accept-Ranges: bytes`.

### 4.9. `POST /api/v1/drafts/{id}:verify-claims` (Quy trình SAFE Fact-Checking 4 Bước)
- **Method:** `POST`
- **URI:** `/api/v1/drafts/{id}:verify-claims`
- **Request Body (JSON):**
  ```json
  {
    "selected_text": "Mô hình Transformer chuẩn đạt 28.4 BLEU trên tập dữ liệu WMT 2014 English-to-German, vượt qua tất cả các mô hình ensemble trước đó.",
    "document_ids": ["c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"]
  }
  ```
- **Phản hồi (`200 OK`):** Trả về mảng mệnh đề phân rã, nhãn NLI (`entailment`, `contradiction`, `neutral`) kèm dẫn chứng trích đoạn và Bounding Box.

### 4.10. `GET /api/v1/drafts/{id}/bundle` (Xuất Camera-Ready Bundle)
- **Method:** `GET`
- **Query Params:** `format=zip` (`zip` hoặc `pdf`).
- **Response Headers:** `Content-Type: application/zip`, `Content-Disposition: attachment; filename="camera_ready_bundle.zip"`.

### 4.11. `POST /api/v1/drafts/{id}/comments` (Phản Biện Nhóm / Reviewer Mode)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "line_number": 42,
    "selected_text": "Mô hình Transformer chuẩn đạt 28.4 BLEU...",
    "comment": "Chỗ này cần bổ sung so sánh thêm với mô hình MoE mới nhất của năm 2025."
  }
  ```
- **Response (`201 Created`).**

### 4.12. `GET /api/v1/drafts/{id}/comments` (Lấy Danh Sách Bình Luận)
- **Method:** `GET`
- **Query Params:** `page` (int, default 1), `per_page` (int, default 50).
- **Response (`200 OK` - Paginated Collection Envelope).**

---

## 5. MODULE 3: KHAI THÁC TÀI LIỆU THAM KHẢO & ĐỒ THỊ TRI THỨC (REFERENCES API)

### 5.1. `POST /api/v1/references:resolve` (Batch Resolving & Leaky Bucket API)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "references": [
      { "ref_id": "ref_1", "doi": "10.48550/arXiv.1607.06450", "title": "Layer normalization" },
      { "ref_id": "ref_2", "doi": "10.18653/v1/N18-1202", "title": "Deep contextualized word representations" }
    ]
  }
  ```
- **Ranh giới Cách ly Bộ đệm:**
  - Siêu dữ liệu từ Crossref, Semantic Scholar, arXiv, PubMed được lưu và đọc từ *Global Academic Cache* (< 10ms).
  - Bản thảo người dùng tải lên được cô lập tuyệt đối trong *Tenant-Isolated Cache*.
- **Response (`200 OK`):** Trả về mảng bài báo đã phân giải kèm cờ `has_open_access_pdf` và `pdf_download_url`.

### 5.2. `GET /api/v1/documents/{id}/graph` (Truy vấn Đồ thị Tri thức Trích dẫn)
- **Method:** `GET`
- **Query Params:** `max_hops=2` (mặc định 2, tối đa 2), `relations=CITES,EXTENDS,BENCHMARKS_ON`.
- **Thuật toán Ngắt chu trình (Cycle Breaking):** Tự động bẻ gãy các liên kết trích dẫn chéo vòng tròn qua `visited` node set.
- **Response (`200 OK` - Graph Node-Link Schema):**
  ```json
  {
    "success": true,
    "data": {
      "root_document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "nodes": [
        { "id": "doc_A", "title": "Attention Is All You Need", "year": 2017, "type": "root" },
        { "id": "doc_B", "title": "Layer Normalization", "year": 2016, "type": "cited" }
      ],
      "edges": [
        { "source": "doc_A", "target": "doc_B", "relation": "CITES", "confidence": 1.0 }
      ]
    },
    "meta": { ... }
  }
  ```

---

## 6. MODULE 4: QUẢN LÝ THƯ VIỆN & TỔNG HỢP ĐA BÀI (LIBRARY API)

### 6.1. `GET /api/v1/folders` (Danh sách thư mục đề tài)
- **Method:** `GET`
- **Response (`200 OK`):** Trả về danh sách thư mục đề tài nghiên cứu kèm số lượng bài báo trong từng thư mục.

### 6.2. `POST /api/v1/folders` (Tạo thư mục đề tài mới)
- **Method:** `POST`
- **Request Body:** `{ "name": "Deep Learning Architectures", "parent_id": null }`
- **Response (`201 Created`).**

### 6.3. `PATCH /api/v1/folders/{id}` (Đổi tên / Di chuyển thư mục)
- **Method:** `PATCH`
- **Request Body:** `{ "name": "Transformers & Attention Mechanisms", "parent_id": null }`
- **Response (`200 OK`).**

### 6.4. `DELETE /api/v1/folders/{id}` (Xóa thư mục đề tài)
- **Method:** `DELETE`
- **Response (`204 No Content`).**

### 6.5. `GET /api/v1/library/documents` (Kho bài báo cá nhân đã Star)
- **Method:** `GET`
- **Query Params:** `folder_id` (UUID, tùy chọn), `page` (int, default 1), `per_page` (int, default 20).
- **Response (`200 OK` - Paginated Collection Envelope).**

### 6.6. `POST /api/v1/library/documents:bulk-import` (Nạp Hàng Loạt 10 - 50 Bài Báo)
- **Method:** `POST`
- **Content-Type:** `multipart/form-data` hoặc `application/json`
- **Body:**
  - `bibtex_file`: Tệp `.bib` (tùy chọn).
  - `identifiers`: Danh sách mã DOI hoặc arXiv ID (`["10.1145/3308558.3313562", "1706.03762"]`).
  - `target_folder_id`: UUID thư mục đích.
- **Quota:** Tối đa 50 bài/ngày/người dùng.
- **Response (`202 Accepted`):** Trả về `batch_id`, số lượng tác vụ đã tiếp nhận và endpoint kiểm tra tiến độ nạp lô.

### 6.7. `POST /api/v1/folders/{id}:synthesize` & `POST /api/v1/library:synthesize` (Hierarchical RAG & Sufficiency Gate)
- **Method:** `POST`
- **URI:** `/api/v1/folders/{id}:synthesize` (hoặc `/api/v1/library:synthesize` cho toàn bộ thư viện).
- **Request Body (JSON):**
  ```json
  {
    "query": "Trong các bài báo tôi đã lưu, những bài nào thử nghiệm mô hình Vision Transformer trên ImageNet và độ chính xác Top-1 cao nhất là bao nhiêu?"
  }
  ```
- **Cổng Đánh Giá Mức Độ Đầy Đủ Bằng Chứng (Sufficiency Verification Gate):**
  - Quét Tầng 1 (Smart Notes) + Tầng 2 (Metadata & Abstracts).
  - Nếu `Sufficiency_Score >= 0.80` và không yêu cầu bảng số liệu thô: Early-exit (Fast-path <= 2s).
  - Nếu `Sufficiency_Score < 0.80` hoặc yêu cầu so sánh thực nghiệm chi tiết: Kích hoạt truy vấn sâu Tầng 3 (Deep Raw Chunks qua Hybrid Search + Global Cross-Encoder Reranker có ngưỡng cắt >= 0.35).
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "answer": "Có 2 bài báo trong thư mục của bạn nghiên cứu về Vision Transformer trên ImageNet: (1) Dosovitskiy et al. (2020) đạt 88.55% Top-1 với ViT-H/14, (2) Touvron et al. (2021) với DeiT-B đạt 83.1% Top-1.",
      "retrieval_tier_reached": "tier_3_deep_raw_chunks",
      "sufficiency_score": 0.92,
      "sources": [
        {
          "document_id": "d1e2f3a4-...",
          "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
          "page_number": 6,
          "bounding_boxes": [[0.1, 0.3, 0.9, 0.35, 6]]
        }
      ]
    },
    "meta": { ... }
  }
  ```

### 6.8. `POST /api/v1/library:compare` (Dựng Bảng So Sánh Tự Động)
- **Method:** `POST`
- **URI:** `/api/v1/library:compare`
- **Request Body (JSON):**
  ```json
  {
    "document_ids": [
      "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "d1e2f3a4-5678-49ab-cdef-1234567890ab"
    ],
    "columns": ["Method", "Dataset", "Top-1 Accuracy", "Limitation"]
  }
  ```
- **Response (`200 OK`):** Trả về bảng so sánh đối chiếu đa chiều, trong đó mỗi ô số liệu đều kèm tọa độ Bounding Box dẫn chứng trực tiếp về trang bài báo gốc.

---

## 7. QUẢN LÝ PHIÊN NGHIÊN CỨU & CHIA SẺ (SESSION & SHARING API)

### 7.1. `POST /api/v1/sessions` (Khởi tạo phiên nghiên cứu mới)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "title": "Nghiên cứu Kiến trúc Attention & Transformer",
    "initial_document_ids": ["c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"]
  }
  ```
- **Response (`201 Created`):**
  - **Headers:** `Location: /api/v1/sessions/a1b2c3d4-e5f6-47a8-b9c0-1234567890de`, `ETag: "v1"`.
  - **Body:** Trả về đối tượng `session` với `version: 1`.

### 7.2. `GET /api/v1/sessions` (Lấy lịch sử các phiên nghiên cứu - Sidebar History)
- **Method:** `GET`
- **Query Params:** `page` (int, default 1), `per_page` (int, default 20), `include_archived` (boolean, default false).
- **Response (`200 OK` - Paginated Collection Envelope).**

### 7.3. `GET /api/v1/sessions/{id}` (Khôi Phục Toàn Vẹn Phiên Làm Việc)
- **Method:** `GET`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "a1b2c3d4-e5f6-47a8-b9c0-1234567890de",
      "title": "Nghiên cứu Kiến trúc Attention & Transformer",
      "document_ids": [
        "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "d1e2f3a4-5678-49ab-cdef-1234567890ab"
      ],
      "active_document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
      "viewport_state": {
        "page": 4,
        "zoom_ratio": 1.25,
        "scroll_top": 450.5
      },
      "active_tab": "chat",
      "is_archived": false,
      "version": 14,
      "updated_at": "2026-09-12T10:10:00.000Z"
    },
    "meta": { ... }
  }
  ```

### 7.4. `PATCH /api/v1/sessions/{id}` (Cập nhật Thông tin / Tiêu đề Phiên Nghiên Cứu)
- **Method:** `PATCH`
- **Headers:** `If-Match: "v14"` (**Bắt buộc** theo chuẩn HTTP OCC RFC 9110 / RFC 7232).
- **Request Body (JSON):**
  ```json
  {
    "title": "Nghiên cứu Nâng cao Kiến trúc Multi-Head Attention"
  }
  ```
- **Response (`200 OK`):** Trả về đối tượng `session` với `title` mới kèm header `ETag: "v15"` và `version: 15`.
- **Error (`412 Precondition Failed`):** Nếu `If-Match` không khớp ETag phiên bản hiện tại trong DB (`CONCURRENCY_CONFLICT`).

### 7.5. `PATCH /api/v1/sessions/{id}/viewport` (Tự động Lưu Vết Viewport & Active Tab với OCC)
- **Method:** `PATCH`
- **Headers:** `If-Match: "v14"` (**Bắt buộc** theo RFC 9110 / RFC 7232).
- **Request Body (JSON):**
  ```json
  {
    "active_document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "viewport_state": { "page": 5, "zoom_ratio": 1.25, "scroll_top": 120.0 },
    "active_tab": "notes"
  }
  ```
- **Response (`200 OK`):** Trả về `version: 15` và `ETag: "v15"`.
- **Error (`412 Precondition Failed`):** Nếu header `If-Match` không khớp phiên bản hiện tại (`CONCURRENCY_CONFLICT`).

### 7.6. `DELETE /api/v1/sessions/{id}` (Xóa phiên nghiên cứu)
- **Method:** `DELETE`
- **Response (`204 No Content`):** Dọn dẹp bản ghi phiên; các bài báo unstarred trong phiên nếu không thuộc phiên nào khác sẽ được lên lịch thu dọn TTL.

### 7.7. `POST /api/v1/sessions/{id}/documents` (Nạp Bài Vào Phiên - Pure JSON AIP Pattern)
- **Method:** `POST`
- **Content-Type:** `application/json` (**Bắt buộc**; tải file nhị phân trực tiếp thực hiện qua `POST /api/v1/documents` kèm `session_id`).
- **Request Body (JSON):**
  ```json
  {
    "source_type": "url",
    "url": "https://arxiv.org/pdf/1607.06450.pdf",
    "title": "Layer Normalization"
  }
  ```
  hoặc:
  ```json
  {
    "source_type": "document_id",
    "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"
  }
  ```
- **Ràng buộc Ngưỡng trần Phiên:**
  - Nếu phiên hiện tại đã nạp đủ 5 bài: Trả về lỗi `422 Unprocessable Entity` kèm mã `SESSION_CAPACITY_EXCEEDED`.
- **Response (`202 Accepted`):** Trả về ID tài liệu mới, tự động bóc tách ngầm và bổ sung Tab trên UI.

### 7.8. `POST /api/v1/sessions/{id}/messages` (Hỏi Đáp Đa Bài Báo & Stream SSE)
- **Method:** `POST`
- **Accept:** `text/event-stream`
- **Headers:** `Idempotency-Key: <UUID>`
- **Request Body (JSON):**
  ```json
  {
    "question": "So sánh hàm kích hoạt giữa Paper gốc và Paper Vaswani et al.?",
    "stream": true,
    "scope": "multi_paper",
    "focused_document_id": null
  }
  ```
  *(Ghi chú `scope`: Có thể chọn `"multi_paper"` để tổng hợp đối chiếu trên toàn bộ 1 - 5 bài báo trong phiên, hoặc chọn `"single_paper"` kèm `"focused_document_id"` để chỉ đào sâu vào 1 bài báo đang mở tại Tab hiện tại).*
- **Nguyên lý Đóng Gói Ngữ Cảnh Tầng Server:**
  Áp dụng **Cross-Document Context Namespacing** đóng gói XML tường minh `<document id="...">` và **Elastic Table Budgeting** cắt tỉa bảng biểu đảm bảo TTFT < 1s.
- **Dòng Sự kiện SSE Phản hồi:**
  ```text
  event: start
  data: {"turn_id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c", "message_id": "msg_9f1a2b3c", "created_at": "2026-09-12T10:15:00.000Z"}

  event: citations
  data: {"citations": [{"citation_id": "cit_1", "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c", "document_title": "Attention Is All You Need", "page_number": 5, "bounding_boxes": [[0.1, 0.2, 0.8, 0.28, 5]]}]}

  event: token
  data: {"token": "Trong bài báo của Vaswani et al., hàm kích hoạt được sử dụng là ReLU..."}

  event: done
  data: {"turn_id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c", "message_id": "msg_9f1a2b3c", "total_tokens": 128, "finish_reason": "stop"}
  ```
  *(Khi không tìm thấy ngữ cảnh nào đạt ngưỡng rerank >= 0.35, server phát dòng phản hồi từ chối nhã nhặn kèm `finish_reason: "abstention"` thay vì trả về mã HTTP 404).*
- **Xử lý Ngắt kết nối Máy trạm (Cancellation):** Nếu client bấm "Dừng sinh", server phát hiện đóng kết nối TCP và ngắt ngay coroutine LLM, ghi log mã **HTTP 499 (Client Closed Request)** để bảo toàn chi phí token.

### 7.9. `GET /api/v1/sessions/{id}/messages` (Lịch sử hội thoại của phiên)
- **Method:** `GET`
- **Query Params:** `page` (int, default 1), `per_page` (int, default 50).
- **Response (`200 OK` - Paginated Collection Envelope):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
        "session_id": "8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e",
        "question": "So sánh hàm kích hoạt giữa Paper gốc và Paper Vaswani et al.?",
        "answer": "Trong bài báo của Vaswani et al., hàm kích hoạt được sử dụng là ReLU...",
        "citations": [
          {
            "citation_id": "cit_1",
            "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
            "document_title": "Attention Is All You Need",
            "page_number": 5,
            "bounding_boxes": [[0.1, 0.2, 0.8, 0.28, 5]]
          }
        ],
        "total_tokens": 128,
        "finish_reason": "stop",
        "created_at": "2026-09-12T10:15:00.000Z"
      }
    ],
    "meta": {
      "total": 1,
      "page": 1,
      "per_page": 50,
      "total_pages": 1,
      "request_id": "55b5aa93-3a91-4a22-b0bb-b01dc2c8c3a6",
      "timestamp": "2026-09-12T10:20:00.000Z"
    },
    "links": {
      "first": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50",
      "prev": null,
      "self": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50",
      "next": null,
      "last": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50"
    }
  }
  ```

### 7.10. `DELETE /api/v1/sessions/{id}/messages` (Xóa toàn bộ tin nhắn - Idempotent)
- **Method:** `DELETE`
- **Response (`204 No Content`):** Luôn trả về 204 ngay cả khi danh sách đã trống.

### 7.11. `POST /api/v1/sessions/{id}:restore-archived` (Khôi phục phiên quá hạn TTL 30 ngày)
- **Method:** `POST`
- **URI:** `/api/v1/sessions/{id}:restore-archived`
- **Content-Type:** `multipart/form-data`
- **Body:** `file`: Binary PDF gốc của bài báo cần phục hồi.
- **Response (`200 OK`):** Tự động bóc tách lại và khôi phục trạng thái hoạt động của phiên.

### 7.12. `POST /api/v1/shares` (Tạo Liên Kết Chia Sẻ Công Khai)
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "resource_type": "note_synthesis",
    "resource_id": "5f32e46a-9434-42b1-da05-ef5fc0612c37",
    "allow_comments": false
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "success": true,
    "data": {
      "share_token": "sh_7b9a1c2d3e4f5a6b",
      "share_url": "https://verischolar.app/s/sh_7b9a1c2d3e4f5a6b",
      "resource_type": "note_synthesis",
      "created_at": "2026-09-12T10:20:00.000Z"
    },
    "meta": { ... }
  }
  ```

### 7.13. `GET /api/v1/shares/{token}` (Xem Tài Nguyên Chia Sẻ Công Khai - No Auth)
- **Method:** `GET`
- **Headers:** Không yêu cầu `Authorization` Header (công khai).
- **Phản hồi:**
  - `200 OK` (Khi liên kết hợp lệ):
    ```json
    {
      "success": true,
      "data": {
        "resource_type": "note_synthesis",
        "resource_title": "Bản Đúc Kết Kiến Trúc Scaled Dot-Product Attention",
        "owner_name": "Đàm Mạnh Dũng",
        "payload": {
          "markdown_content": "### 1. Bản chất Toán học\nCơ chế Attention...",
          "interactive_badges": [
            {
              "badge_text": "Vaswani et al., 2017 • Tr. 4",
              "page_number": 4,
              "bounding_boxes": [[0.21, 0.52, 0.79, 0.58, 4]]
            }
          ]
        },
        "pdf_stream_url": "/api/v1/shares/sh_7b9a1c2d3e4f5a6b/file",
        "allow_comments": false,
        "expires_at": null
      },
      "meta": { ... }
    }
    ```
  - `410 Gone` (Khi liên kết đã bị thu hồi qua `DELETE /shares/{token}`):
    ```json
    {
      "success": false,
      "error": {
        "code": "SHARE_LINK_REVOKED",
        "message": "Liên kết chia sẻ này đã bị chủ sở hữu thu hồi quyền truy cập.",
        "field": "token",
        "action": "Vui lòng liên hệ chủ sở hữu để nhận liên kết chia sẻ mới."
      },
      "meta": { ... }
    }
    ```

### 7.14. `GET /api/v1/shares/{token}/file` (Stream PDF cho Khách Xem Chia Sẻ - No Auth)
- **Method:** `GET`
- **Headers Hỗ trợ:** `Range: bytes=0-1024` (HTTP 206 Partial Content).
- **Bảo mật:** Xác thực quyền đọc dựa trên `share_token` hợp lệ (không đòi hỏi Bearer Token).
- **Phản hồi:**
  - `200 OK` hoặc `206 Partial Content`: Stream nhị phân PDF phục vụ PDF.js Canvas trên màn hình người nhận chia sẻ để vẽ khung highlight viền vàng khớp chính xác tuyệt đối.
  - `410 Gone`: Nếu liên kết chia sẻ đã bị chủ sở hữu thu hồi.

### 7.15. `DELETE /api/v1/shares/{token}` (Thu Hồi Quyền Chia Sẻ Tức Thời - Instant Revocation)
- **Method:** `DELETE`
- **Response (`204 No Content`):** Vô hiệu hóa ngay lập tức. Mọi truy cập sau đó vào `GET /api/v1/shares/{token}` và `GET /api/v1/shares/{token}/file` lập tức trả về `410 Gone`.

---

## 8. BẢO MẬT HẠ TẦNG & QUẢN TRỊ LƯU LƯỢNG (INFRASTRUCTURE SECURITY)

1. **Phân Cấp Chỉ Thị (Instruction Hierarchy) Chống Prompt Injection Gián Tiếp:**
   Toàn bộ văn bản bóc tách từ file PDF hoặc tham chiếu ngoài đưa vào prompt LLM bắt buộc phải được bọc trong thẻ dữ liệu cách ly:
   ```xml
   <data_context_untrusted>
   ... nội dung thô từ file PDF ...
   </data_context_untrusted>
   ```
2. **Bộ Điều Phối Hạn Ngạch Ngoài (Leaky Bucket Limiter):**
   Khống chế tần suất gọi ra Semantic Scholar (tối đa 1 req/sec unauthenticated hoặc 10 req/sec với partner key) và Crossref, kết hợp Global Academic Cache để loại bỏ triệt để nguy cơ nghẽn mạng HTTP 429.
3. **Giới Hạn Tần Suất & Quota (Denial-of-Wallet Protection):**
   - Tối đa 50 bài nạp hàng loạt (`bulk-import`) mỗi ngày cho mỗi người dùng.
   - Tối đa 30 lượt biên dịch LaTeX Sandbox mỗi giờ cho mỗi người dùng.
   - Giới hạn tần suất chung: 100 requests/phút trên mỗi địa chỉ IP.
   - Cửa sổ lưu trữ `Idempotency-Key` trên Redis: 24 giờ (86.400 giây).

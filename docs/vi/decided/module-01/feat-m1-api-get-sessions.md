# Kế Hoạch Kỹ Thuật: Lấy Lịch Sử Các Phiên Nghiên Cứu (GET /api/v1/sessions)

> **Mã tài liệu:** `FEAT-M1-API-46`  
> **Trạng thái:** `APPROVED / SẴN SÀNG TRIỂN KHAI EVALUATION HARNESS`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 17/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-get-sessions`  
> **API Canonical:** `GET /api/v1/sessions` (#46 trong danh mục API VeriScholar)  
> **Chuẩn thiết kế:** RFC 9110 (HTTP Semantics), RFC 8288 (Web Linking Pagination), RFC 7807 (Problem Details), Google AIP-158 (Pagination Design), Hexagonal Clean Architecture.

---

## 1. Bối Cảnh Nghiệp Vụ & Khảo Sát Thế Giới (Context & SOTA Survey)

### 1.1. Bối Cảnh Người Dùng & Giao Diện Dual-Pane Workspace
Trong giao diện VeriScholar, thanh Sidebar bên trái hiển thị danh sách các phiên làm việc nghiên cứu trước đây của người dùng (Research Sessions History).
- Khi người dùng quay trở lại hệ thống, họ cần thấy ngay danh sách các phiên gần đây nhất, tiêu đề gợi nhớ, số lượng tài liệu đã nạp vào phiên (`document_count`), và tab làm việc đang mở dở dang (`active_tab`).
- Khi danh sách phiên trở nên nhiều sau thời gian dài sử dụng, hệ thống cần hỗ trợ:
  1. Phân trang chuẩn RFC 8288 (`page`, `per_page`) để đảm bảo thời gian tải trang ban đầu (Initial Page Load) luôn $< 30\text{ms}$.
  2. Tìm kiếm nhanh không phân biệt hoa thường theo từ khóa tiêu đề (`q=...`).
  3. Lọc các phiên đã bị đưa vào lưu trữ quá hạn TTL (`include_archived=true/false`).
  4. Cô lập dữ liệu đa người dùng tuyệt đối (Multi-tenant Data Shielding).

### 1.2. Khảo Sát Kiến Trúc Quốc Tế (State of the Art)
- **Google NotebookLM:** Hiển thị danh sách Notebooks ở trang chủ, hỗ trợ tìm kiếm nhanh theo tiêu đề và hiển thị số lượng nguồn tài liệu (Sources count) kèm thời điểm chỉnh sửa gần nhất (`updated_at DESC`).
- **Perplexity Pro & ChatGPT:** Cung cấp sidebar threads phân trang cuộn vô tận (infinite scroll), tìm kiếm nhanh qua API backend được index hóa trường `title`.
- **VeriScholar Customization:**
  - Kết hợp chỉ số `document_count` bằng phép gom nhóm tối ưu trong cơ sở dữ liệu `(GROUP BY session_id)`.
  - Hỗ trợ đầy đủ liên kết `links` RFC 8288 (`first`, `prev`, `self`, `next`, `last`) giúp frontend dễ dàng pre-fetch trang tiếp theo.
  - Tối ưu hóa truy vấn qua index tổng hợp `(user_id, is_archived, updated_at DESC)` trên bảng `research_sessions`.

---

## 2. Đặc Tả API Kỹ Thuật (API Technical Specification)

### 2.1. Request Thông Tin
- **Method:** `GET`
- **Path:** `/api/v1/sessions`
- **Headers:**
  - `Authorization: Bearer <token>` hoặc cookie phiên đăng nhập.
  - `x-user-id: <UUID>` (trong môi trường kiểm thử nội bộ hoặc ASGI transport).
- **Query Parameters:**
  | Tên tham số | Kiểu dữ liệu | Mặc định | Giới hạn | Mô tả |
  | :--- | :---: | :---: | :---: | :--- |
  | `page` | `int` | `1` | $\ge 1$ | Số thứ tự trang (1-indexed). |
  | `per_page` | `int` | `20` | $1 \le \text{per\_page} \le 100$ | Số lượng phiên trả về trên mỗi trang. |
  | `include_archived` | `boolean` | `false` | `true / false` | Khi `true`, bao gồm cả các phiên đã bị lưu trữ do quá hạn TTL 7 ngày. |
  | `q` | `string` | `null` | Tùy chọn | Từ khóa tìm kiếm mờ (case-insensitive substring) theo tiêu đề phiên. |

### 2.2. Response Thông Tin
- **Mã HTTP:** `200 OK`
- **Content-Type:** `application/json; charset=utf-8`
- **Cấu trúc dữ liệu:** `SessionHistoryEnvelope` (kế thừa `PaginatedResponseEnvelope[SessionHistoryItem]`)
```json
{
  "success": true,
  "data": [
    {
      "id": "c26ba51e-8233-41a6-8e93-ab6adc4785fa",
      "title": "Nghiên cứu Cơ chế Chú ý và Mô hình Biến đổi Transformer",
      "document_count": 2,
      "active_tab": "chat",
      "is_archived": false,
      "created_at": "2026-09-17T15:02:09.927129Z",
      "updated_at": "2026-09-17T15:02:09.927132Z"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  },
  "links": {
    "first": "/api/v1/sessions?page=1&per_page=20",
    "prev": null,
    "self": "/api/v1/sessions?page=1&per_page=20",
    "next": null,
    "last": "/api/v1/sessions?page=1&per_page=20"
  }
}
```

---

## 3. Các Bất Biến Của Hệ Thống (Core System Invariants)

1. **Bất biến Phân tách Đa Người Dùng (Multi-tenant Strict Isolation):**
   - Người dùng A chỉ có thể xem danh sách các phiên do chính người dùng A tạo ra (`WHERE user_id = :user_id`).
   - Không rò rỉ bất kỳ thông tin nào về số lượng hoặc tiêu đề phiên của người dùng B.
2. **Bất biến Thứ tự Thời Gian (Chronological Ordering Invariant):**
   - Danh sách phiên luôn được sắp xếp theo thời điểm tương tác gần nhất giảm dần (`ORDER BY updated_at DESC`), giúp phiên vừa thao tác luôn nổi lên đầu danh sách sidebar.
3. **Bất biến Toàn vẹn Phân Trang (Pagination Integrity RFC 8288):**
   - `page=1` có `prev: null`.
   - Trang cuối cùng có `next: null`.
   - Không xuất hiện bản ghi trùng lặp giữa hai trang kế tiếp (`Set(Page 1) ∩ Set(Page 2) = ∅`).
4. **Bất biến Bảo Vệ Lưu Trữ (Archive Segregation Invariant):**
   - Mặc định (`include_archived=false`), các phiên có `is_archived = true` bị ẩn khỏi danh sách để giữ thanh Sidebar gọn gàng.
   - Khi truyền `include_archived=true`, các phiên lưu trữ được trả về đầy đủ với cờ `is_archived: true`.
5. **Bất biến Rào chắn Tham số (Input Validation Bounds):**
   - `page < 1`, `per_page < 1` hoặc `per_page > 100` phải lập tức bị chặn tại router với `HTTP 422 Unprocessable Entity`.

---

## 4. Thiết Kế API Evaluation Snapshot Runner (`get_sessions_list.py`)

Kế thừa `BaseAPIRunner`, runner `ListSessionsAPIRunner` sẽ triển khai 6 kịch bản kiểm thử độc lập:
1. **Scenario 1: Default Paginated Query (`page=1, per_page=20`)**
   - Kiểm tra khởi tạo phiên mặc định, xác nhận `status_code == 200`, `success == True`, cấu trúc `SessionHistoryItem` đầy đủ các trường, `updated_at DESC`.
2. **Scenario 2: Strict Page Slicing & Boundary Navigation (`page=1, per_page=2` vs `page=2, per_page=2`)**
   - Kiểm tra số lượng item mỗi trang chính xác bằng `per_page`.
   - Kiểm tra liên kết `links` RFC 8288 (`first`, `prev`, `next`, `last`).
   - Kiểm tra tính rời rạc của tập ID giữa các trang (`Set(page 1) ∩ Set(page 2) == ∅`).
3. **Scenario 3: Case-Insensitive Title Keyword Search (`q=...`)**
   - Tạo các phiên với tiêu đề khác nhau (ví dụ: "Nghiên cứu Transformer Attention", "Khảo sát Y sinh học").
   - Gửi truy vấn `q=transformer` (chữ thường), kiểm tra kết quả chỉ chứa phiên khớp từ khóa và loại trừ các phiên khác.
4. **Scenario 4: Archive Status Segregation (`include_archived=false` vs `include_archived=true`)**
   - Tạo phiên và đánh dấu `is_archived = true`.
   - Kiểm tra khi `include_archived=false`: phiên lưu trữ không xuất hiện.
   - Kiểm tra khi `include_archived=true`: phiên lưu trữ xuất hiện với `is_archived: true`.
5. **Scenario 5: Multi-Tenant Data Isolation Guard**
   - Gửi request dưới danh tính người dùng khác (`x-user-id: test_other_user`).
   - Xác nhận danh sách trả về không chứa bất kỳ phiên nào của người dùng hiện tại (kết quả `total == 0` hoặc chỉ chứa phiên của chính họ).
6. **Scenario 6: Query Parameter Validation Bounds (`page=0` & `per_page=101`)**
   - Gửi `page=0` -> Kỳ vọng `HTTP 422 Unprocessable Entity`.
   - Gửi `per_page=101` -> Kỳ vọng `HTTP 422 Unprocessable Entity`.

---

## 5. Tiêu Chuẩn Báo Cáo Markdown & Artifacts
- **File báo cáo:** `temp/output/test/get_sessions_list.md`
- **Thư mục artifacts:** `tests/.artifacts/get_sessions_list/`
- **Mã băm SHA-256:** Lưu vết toàn bộ 6 payloads JSON phục vụ đối soát CI/CD.

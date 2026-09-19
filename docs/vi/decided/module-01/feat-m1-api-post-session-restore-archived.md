# Kế Hoạch Thiết Kế Kỹ Thuật: POST /api/v1/sessions/{id}:restore-archived

> **Mã tính năng**: `FEAT-M1-API-POST-SESSION-RESTORE-ARCHIVED`  
> **Endpoint**: `POST /api/v1/sessions/{id}:restore-archived`  
> **STT API PRD**: `#55. Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: Google AIP-136 (Custom Methods), RFC 9110 (HTTP Semantics), RFC 7232 (Conditional Requests / ETag OCC), Multi-Part Form-Data Upload, Multi-Tenancy & Zero Data Leakage.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Trong kiến trúc VeriScholar, nhằm tối ưu hóa tài nguyên lưu trữ và tuân thủ chính sách vòng đời dữ liệu (Data Retention Lifecycle), các phiên làm việc và tệp PDF tạm thời sẽ chuyển sang trạng thái lưu trữ (archived) sau thời hạn TTL 30 ngày (`is_archived = true`).

Khi người dùng quay trở lại một phiên nghiên cứu đã hết hạn TTL:
1. **Bảo tồn toàn bộ ngữ cảnh nghiên cứu lịch sử**: Toàn bộ ghi chú, cấu trúc phiên, danh mục bài báo đã nạp và lịch sử hội thoại (`session_turns`) vẫn được bảo tồn toàn vẹn trong cơ sở dữ liệu.
2. **Kích hoạt lại phiên (Reactivation via Binary Re-upload)**: Người dùng tải lại tệp PDF gốc của bài báo thông qua giao thức `multipart/form-data`.
3. **Phục hồi trạng thái hoạt động & Cập nhật OCC Version**:
   - Xác thực header nhị phân tệp tải lên bắt buộc phải là PDF (`%PDF-`).
   - Cập nhật trạng thái phiên: `is_archived = false`, `archived_at = null`, tự động tăng số phiên bản `version += 1`.
   - Cung cấp ETag mới (`ETag: "v{version}"`) trong response header nhằm duy trì tính nhất quán kiểm soát đồng thời lạc quan (OCC).

---

## 2. 6 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **Active Reactivation State Transition**:
   - Khi tải lên tệp PDF hợp lệ, phiên từ trạng thái `is_archived = true` phải chuyển thành `is_archived = false` và `archived_at = null`.
2. **OCC Version Monotonicity & ETag Synchronization**:
   - Thao tác kích hoạt lại bắt buộc phải tăng trường `version` thêm đúng 1 đơn vị (`version_after == version_before + 1`), và header phản hồi `ETag` phải trùng khớp với `"v{version_after}"`.
3. **Binary Magic Bytes Header Guard**:
   - Tệp tải lên bắt buộc phải có nội dung bắt đầu bằng magic bytes chuẩn PDF `b"%PDF"` (RFC 8118 / ISO 32000). Mọi tệp không đúng định dạng (ví dụ: plain text, file rỗng, binary giả mạo) phải bị từ chối ngay với mã `HTTP 400 Bad Request` và error code `INVALID_PDF_HEADER`.
4. **Multi-Tenant Shielding (Zero Privilege Escalation)**:
   - Chỉ chủ sở hữu phiên (`current_user.id == session.user_id`) mới có quyền kích hoạt lại phiên. Người dùng lạ (Alien Tenant) cố tình khôi phục phiên sẽ nhận `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
5. **Non-Existent Session Guard**:
   - Gọi endpoint với session UUID không tồn tại trong hệ thống phải nhận phản hồi `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
6. **UUID Format Validation Guard**:
   - Mã định danh `id` trên path không đúng chuẩn UUIDv4 (RFC 4122) bị chặn tại tầng schema validation với mã `HTTP 422 Unprocessable Content`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `POST`
- **Route**: `/api/v1/sessions/{id}:restore-archived`
- **Content-Type**: `multipart/form-data`
- **Headers**:
  - `Authorization`: `Bearer <token>`
- **Request Body (Form Data)**:
  - `file`: `UploadFile` (Binary PDF gốc)

### 3.2. Response Envelope (`200 OK`)
```json
{
  "success": true,
  "data": {
    "id": "8b5cdbd2-afe6-44b5-8666-a64d6fbfa465",
    "title": "Nghiên cứu Transformers và Cơ chế Attention",
    "document_ids": ["c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"],
    "active_document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "viewport_state": {
      "page": 1,
      "zoom_ratio": 1.0,
      "scroll_top": 0.0
    },
    "active_tab": "chat",
    "is_archived": false,
    "version": 2,
    "created_at": "2026-09-18T10:00:00.000000Z",
    "updated_at": "2026-09-19T02:00:00.000000Z"
  },
  "meta": {
    "request_id": "req_f1e2d3c4b5a6",
    "timestamp": "2026-09-19T02:00:00.000000Z"
  }
}
```
- **Response Headers**:
  - `ETag`: `"v2"`

### 3.3. Error Responses
- **`400 Bad Request`**:
  ```json
  {
    "detail": {
      "code": "INVALID_PDF_HEADER",
      "message": "Tệp tải lên không phải là định dạng PDF hợp lệ.",
      "action": "Provide a valid PDF file."
    }
  }
  ```
- **`404 Not Found`**:
  ```json
  {
    "detail": {
      "code": "SESSION_NOT_FOUND",
      "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
      "action": "Verify session ID."
    }
  }
  ```
- **`422 Unprocessable Content`**: Mã lỗi validation của FastAPI khi `id` không phải UUID.

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`post_session_restore_archived.py`)

| STT | Kịch Bản Kiểm Thử | Hành Động & Tham Số | HTTP Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Active History Reactivation & State Invariant** | Tạo session archived (`is_archived=True`), upload PDF hợp lệ `%PDF-1.4...` | `200 OK` | `is_archived == False`, `version` tăng từ 1 lên 2 |
| **02** | **ETag Header & OCC Synchronization** | Kiểm tra response header `ETag` từ request khôi phục | `200 OK` | Header `ETag` tồn tại và khớp giá trị `f'"v{version}"'` |
| **03** | **Binary Magic Header Guard (Invalid PDF)** | Tải lên file text không có magic bytes `%PDF` | `400 Bad Request` | `code == "INVALID_PDF_HEADER"`, session không bị sửa đổi |
| **04** | **Multi-Tenant Isolation Guard** | Tenant lạ gửi request upload kích hoạt session của user khác | `404 Not Found` | `code == "SESSION_NOT_FOUND"`, không lộ trạng thái phiên |
| **05** | **Non-Existent Session Guard** | Upload khôi phục với UUID ngẫu nhiên không tồn tại | `404 Not Found` | `code == "SESSION_NOT_FOUND"` |
| **06** | **UUID Format Validation Guard** | Gửi upload với `id="invalid-uuid-string"` | `422 Unprocessable` | Bị từ chối tại validation guard trước khi đọc binary |

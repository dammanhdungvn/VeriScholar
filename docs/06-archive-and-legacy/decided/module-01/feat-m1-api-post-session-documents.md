# Kế Hoạch Thiết Kế Kỹ Thuật: POST /api/v1/sessions/{id}/documents

> **Mã tính năng**: `FEAT-M1-API-POST-SESSION-DOCUMENTS`  
> **Endpoint**: `POST /api/v1/sessions/{id}/documents`  
> **STT API PRD**: `#51. Nạp bài vào phiên (Pure JSON: url hoặc document_id)`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: Google AIP-136 (Custom Methods), RFC 9110 (HTTP Semantics - 202 Accepted), Multi-Tenancy & Zero Data Leakage.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Trong mô hình nghiên cứu đa tài liệu (Multi-Paper Comparative Reading) của VeriScholar, một phiên làm việc (`ResearchSession`) cho phép người dùng nạp tối đa **5 bài báo khoa học** vào cùng một không gian làm việc.

Trước khi người dùng tiến hành hội thoại RAG đa tài liệu hoặc tổng hợp tri thức chéo, họ cần nạp thêm tài liệu vào phiên đã có sẵn. Theo chuẩn Google AIP-136, API nạp bài sử dụng **Pure JSON Body** thay vì `multipart/form-data`:
1. **Nạp bài đã có trong thư viện cá nhân** (`source_type = "document_id"`): Gắn kết liên kết `SessionDocumentModel` ngay lập tức, chuyển trạng thái `associated`.
2. **Nạp bài qua URL trực tuyến** (`source_type = "url"`): Tự động tạo bản ghi tài liệu ngầm với trạng thái `queued` và đưa vào hàng đợi tải về bóc tách.

---

## 2. 5 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **202 Accepted Asynchronous Acknowledgement Invariant**:
   - Thao tác nạp tài liệu qua Pure JSON trả về mã `HTTP 202 Accepted`, phản hồi ID tài liệu mới được đính kèm và cập nhật phiên bản `version` tăng thêm 1.
2. **Strict Session Capacity Cap (Max 5 Documents)**:
   - Một phiên đọc sâu chỉ chứa tối đa 5 tài liệu (`MAX_SESSION_DOCUMENTS = 5`). Nếu phiên đã có đủ 5 bài báo, yêu cầu nạp thêm sẽ lập tức bị chặn với mã `HTTP 422 Unprocessable Entity` và mã lỗi nghiệp vụ `SESSION_CAPACITY_EXCEEDED`.
3. **Duplicate Document Association Guard**:
   - Một tài liệu không thể nạp trùng lặp vào cùng một phiên làm việc. Nếu phát hiện `document_id` đã tồn tại trong `SessionDocumentModel`, hệ thống từ chối với mã `HTTP 409 Conflict` (`DOCUMENT_ALREADY_IN_SESSION`).
4. **Document & Session Ownership Integrity (Zero Data Leakage)**:
   - Chỉ được phép nạp tài liệu thuộc sở hữu của người dùng hiện tại vào phiên làm việc của chính người dùng đó. Nếu tài khoản khác (Alien Tenant) cố tình nạp tài liệu vào phiên không phải của mình, hệ thống trả về `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
5. **URL Format & Scheme Validation Guard**:
   - Với `source_type = "url"`, URL bắt buộc phải có schema hợp lệ (`http://` hoặc `https://`). Nếu vi phạm, hệ thống từ chối ngay tại tầng schema validation với mã `HTTP 422 Unprocessable Entity`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `POST`
- **Route**: `/api/v1/sessions/{id}/documents`
- **Headers**:
  - `Content-Type: application/json`
  - `X-User-ID: <user_id>` (hoặc JWT Bearer)
- **Status Code Thành Công**: `HTTP 202 Accepted`

### 3.2. Request Payloads

#### Cách 1: Nạp bài có sẵn qua Document ID
```json
{
  "source_type": "document_id",
  "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"
}
```

#### Cách 2: Nạp bài qua URL trực tuyến
```json
{
  "source_type": "url",
  "url": "https://arxiv.org/pdf/1706.03762.pdf",
  "title": "Attention Is All You Need"
}
```

### 3.3. Response Envelope (`202 Accepted`)
```json
{
  "success": true,
  "data": {
    "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "session_id": "f865fd72-5837-4167-a941-485dcb547810",
    "status": "associated",
    "version": 2
  },
  "meta": {
    "request_id": "req_a1b2c3d4e5f6",
    "timestamp": "2026-09-18T15:35:00.000000Z"
  }
}
```

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`post_session_documents.py`)

| STT | Kịch Bản Kiểm Thử | Dữ Liệu Đầu Vào | Mã Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Add Existing Document Success** | `source_type="document_id"`, valid `document_id` | `202 Accepted` | `success=True`, `status="associated"`, `version=2` |
| **02** | **Add Document Via URL Success** | `source_type="url"`, valid `url` & `title` | `202 Accepted` | `success=True`, `status="queued"`, `version=3` |
| **03** | **Duplicate Document Conflict Guard** | Nạp lại `document_id` đã có trong phiên | `409 Conflict` | `DOCUMENT_ALREADY_IN_SESSION` |
| **04** | **Session Capacity Cap Guard (Max 5)** | Nạp bài thứ 6 khi phiên đã có 5 bài | `422 Unprocessable` | `SESSION_CAPACITY_EXCEEDED` |
| **05** | **Multi-Tenant User Isolation Guard** | Alien tenant cố nạp vào phiên người khác | `404 Not Found` | `SESSION_NOT_FOUND` |
| **06** | **Validation Bounds & URL Scheme Guard** | URL không có `https://` hoặc UUID sai | `422 Unprocessable` | `VALIDATION_ERROR` |

---

## 5. Dọn Dẹp Khép Kín (Hermetic Teardown)
Mọi phiên thử nghiệm và các tài liệu được gieo tạo trong quá trình autotest đều được dọn dẹp khép kín qua `DELETE /api/v1/sessions/{id}` và `DELETE /api/v1/documents/{id}`, bảo đảm 0% rò rỉ dữ liệu (Zero Retention).

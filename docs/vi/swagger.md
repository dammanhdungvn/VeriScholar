# Swagger UI Offline Specification (Module 1 - Deep Read & Ingestion)

> **Mục đích:** Tài liệu này đóng vai trò như giao diện Swagger UI ngoại tuyến (Offline Swagger Docs).  
> Khi môi trường backend chưa được khởi chạy hoặc cần gửi tài liệu tích hợp cho Frontend Dev / đối tác, file này cung cấp đầy đủ thông tin kỹ thuật chính xác 100% như trên Swagger UI (`/docs`).

* **OpenAPI Version:** `3.1.0`
* **Base URL:** `http://localhost:8000`
* **API Prefix:** `/api/v1`
* **Content-Type Mặc định:** `application/json` (trừ Upload dùng `multipart/form-data` và Stream File dùng `application/pdf`)
* **Xác thực (Authentication):** Bearer Token (trong giai đoạn phát triển Dev, hệ thống tự động inject Developer Identity)

---

## 1. Quy Chuẩn Phản Hồi Toàn Hệ Thống (Envelopes)

### 1.1. Single Resource Envelope (`200 OK` / `201 Created`)
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
    "timestamp": "2026-09-13T10:00:00Z"
  }
}
```

### 1.2. Paginated Resource Envelope (`200 OK`)
```json
{
  "success": true,
  "data": {
    "items": [ ... ]
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3,
    "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
    "timestamp": "2026-09-13T10:00:00Z"
  },
  "links": {
    "self": "/api/v1/documents?page=1&per_page=20",
    "first": "/api/v1/documents?page=1&per_page=20",
    "prev": null,
    "next": "/api/v1/documents?page=2&per_page=20",
    "last": "/api/v1/documents?page=3&per_page=20"
  }
}
```

### 1.3. Structured Error Envelope (`4xx` / `5xx`)
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document 'f47ac10b-58cc-4372-a567-0e02b2c3d479' not found.",
    "field": "id",
    "action": "Verify document ID or check access permissions."
  },
  "meta": {
    "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
    "timestamp": "2026-09-13T10:00:00Z"
  }
}
```

---

## 2. Chi Tiết Các Endpoints (Module 1: Documents)

```
TAG: Module 1: Documents
```

---

### [POST] `/api/v1/documents`
**Summary:** `Tải lên PDF bài báo (nhận session_id tùy chọn)`  
**Operation ID:** `upload_document_api_v1_documents_post`

#### Mô tả (Description)
🎯 **Mục đích:** Tải tệp PDF bài báo lên hệ thống để bắt đầu quy trình bóc tách.

📥 **Đầu vào (`multipart/form-data`):**
* `file`: Tệp PDF bài báo (bắt buộc, tối đa 50MB, magic bytes `%PDF-`).
* `session_id`: UUID phiên nghiên cứu cần gắn tài liệu (tùy chọn, tối đa 5 bài/phiên).

📤 **Đầu ra (HTTP 201):**
* Trả về `id`, `status: uploaded`, và các liên kết HATEOAS (`status_url`, `file_url`).

⚠️ **Lưu ý:**
* Khử trùng lặp CAS: file trùng hash SHA-256 sẽ tái sử dụng bản ghi cũ.
* Lỗi thường gặp: `400` (sai định dạng), `413` (>50MB), `409` (phiên đã đầy 5 bài).

#### Request Body (`multipart/form-data`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `file` | `binary` | **Có** | - | Tệp PDF bài báo học thuật (tối đa 50MB, kiểm tra magic bytes `%PDF-`) |
| `session_id` | `string (uuid)` | Không | `null` | UUID phiên nghiên cứu cần gắn kết tài liệu (tối đa 5 bài/phiên) |

#### Responses
* **`201 Created`** - Tải lên thành công, tài liệu đã được ghi nhận vào hàng đợi.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "filename": "transformer_attention.pdf",
      "file_size_bytes": 2215144,
      "status": "uploaded",
      "stage": "queued",
      "session_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "is_duplicate": false,
      "links": {
        "self": "/api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924",
        "status": "/api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924/status",
        "file": "/api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924/file"
      }
    },
    "meta": {
      "request_id": "7bf34b1a-8c20-4e4b-bb2a-df3a4f8d9c12",
      "timestamp": "2026-09-13T10:00:00Z"
    }
  }
  ```
* **`400 Bad Request`** - Tệp không hợp lệ (không phải định dạng PDF hoặc thiếu magic bytes `%PDF-`).
* **`404 Not Found`** - Không tìm thấy `session_id` được chỉ định.
* **`409 Conflict`** - Phiên nghiên cứu đã đạt trần tối đa 5 bài báo.
* **`413 Payload Too Large`** - Dung lượng tệp vượt quá giới hạn 50MB.

---

### [GET] `/api/v1/documents`
**Summary:** `Danh sách bài báo (phân trang page/per_page)`  
**Operation ID:** `list_documents_api_v1_documents_get`

#### Mô tả (Description)
🎯 **Mục đích:** Hiển thị danh sách bài báo người dùng trên thư viện hoặc sidebar.

📥 **Đầu vào (Query parameters):**
* `page`: Số thứ tự trang kết quả (mặc định: `1`, tối thiểu: `1`).
* `per_page`: Số lượng bài báo mỗi trang (mặc định: `20`, tối đa: `100`).
* `status`: Lọc theo trạng thái (`uploaded`, `processing`, `completed`, `failed`).

📤 **Đầu ra (HTTP 200):**
* Mảng `items` tóm tắt bài báo (`id`, `filename`, `title`, `status`, `created_at`).
* Object `meta` phân trang và `links` điều hướng RFC 8288 (`next`, `prev`...).

⚠️ **Lưu ý:**
* Sắp xếp mặc định: `created_at DESC` (bài báo mới nhất hiển thị trước).
* Đảm bảo cô lập dữ liệu: chỉ hiển thị tài liệu của người dùng hiện tại.

#### Parameters (Query)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mặc định | Giới hạn | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `page` | `integer` | Không | `1` | `ge=1` | Số thứ tự trang (1-indexed) |
| `per_page` | `integer` | Không | `20` | `ge=1, le=100` | Số lượng bài báo trên một trang |
| `status` | `string` | Không | `null` | Enum | Lọc theo: `uploaded`, `pending`, `processing`, `completed`, `failed` |

#### Responses
* **`200 OK`** - Truy vấn danh sách bài báo thành công kèm siêu dữ liệu phân trang.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
          "filename": "attention_is_all_you_need.pdf",
          "title": "Attention Is All You Need",
          "status": "completed",
          "page_count": 11,
          "file_size_bytes": 2215144,
          "created_at": "2026-09-13T09:30:00Z"
        }
      ]
    },
    "meta": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "total_pages": 1,
      "request_id": "8cf45b2b-9d31-5f5c-cc3b-ef4b5f9e0d23",
      "timestamp": "2026-09-13T10:00:00Z"
    },
    "links": {
      "self": "/api/v1/documents?page=1&per_page=20",
      "first": "/api/v1/documents?page=1&per_page=20",
      "prev": null,
      "next": null,
      "last": "/api/v1/documents?page=1&per_page=20"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Tham số phân trang không hợp lệ (`page < 1` hoặc `per_page > 100`).

---

### [GET] `/api/v1/documents/{document_id}`
**Summary:** `Chi tiết tài liệu kèm Spatial Metadata cho Canvas`  
**Operation ID:** `get_document_detail_api_v1_documents__document_id__get`

#### Mô tả (Description)
🎯 **Mục đích:** Lấy siêu dữ liệu học thuật và kích thước trang cho Canvas (PDF.js).

📥 **Đầu vào (Path parameter):**
* `document_id`: UUID của bài báo khoa học.

📤 **Đầu ra (HTTP 200):**
* Thông tin học thuật (`title`, `authors`, `doi`, `page_count`, `chunk_count`...).
* `pages_metadata`: Mảng kích thước `[width, height]` và góc xoay từng trang PDF.

⚠️ **Lưu ý:**
* Trả về `404` nếu tài liệu không tồn tại hoặc không thuộc quyền sở hữu.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | Định danh UUID duy nhất của bài báo khoa học |

#### Responses
* **`200 OK`** - Lấy chi tiết tài liệu và Spatial Metadata thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "filename": "attention_is_all_you_need.pdf",
      "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "file_size_bytes": 2215144,
      "status": "completed",
      "stage": "completed",
      "progress": 100,
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "publication_year": 2017,
      "doi": "10.48550/arXiv.1706.03762",
      "page_count": 11,
      "chunk_count": 48,
      "pages_metadata": [
        {
          "page_number": 1,
          "dimensions": [595.276, 841.89],
          "rotation_deg": 0
        },
        {
          "page_number": 2,
          "dimensions": [595.276, 841.89],
          "rotation_deg": 0
        }
      ],
      "created_at": "2026-09-13T09:30:00Z",
      "updated_at": "2026-09-13T09:32:15Z"
    },
    "meta": {
      "request_id": "9df56c3c-0e42-6a6d-dd4c-fa5c6a0f1e34",
      "timestamp": "2026-09-13T10:00:00Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập.
* **`422 Unprocessable Entity`** - Định dạng `document_id` không phải UUID hợp lệ.

---

### [GET] `/api/v1/documents/{document_id}/file`
**Summary:** `Stream PDF nhị phân cho Canvas (HTTP 206 Partial Content)`  
**Operation ID:** `stream_document_file_api_v1_documents__document_id__file_get`

#### Mô tả (Description)
🎯 **Mục đích:** Cung cấp luồng PDF nhị phân cho Canvas xem trước (PDF.js).

📥 **Đầu vào:**
* `document_id`: UUID bài báo (Path parameter).
* `Range`: Header tùy chọn (ví dụ: `bytes=0-1024`) để yêu cầu phân đoạn byte.

📤 **Đầu ra:**
* Stream nhị phân `application/pdf`.
* `HTTP 200 OK`: Tải toàn bộ tệp PDF.
* `HTTP 206 Partial Content`: Tải phân đoạn byte phục vụ lazy-load Canvas.

⚠️ **Lưu ý:**
* Trả về `416 Range Not Satisfiable` nếu dải byte yêu cầu vượt quá dung lượng tệp.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | **Có** | UUID của bài báo |
| `header` | `Range` | `string` | Không | Dải byte phân đoạn theo chuẩn RFC 7233 (ví dụ: `bytes=0-1024` hoặc `bytes=1048576-`) |

#### Responses
* **`200 OK`** - Tải toàn bộ tệp PDF thành công.  
  *Content-Type:* `application/pdf`  
  *Headers đi kèm:*
  * `Accept-Ranges: bytes`
  * `Content-Length: 2215144`
  * `Content-Disposition: inline; filename="attention_is_all_you_need.pdf"`
* **`206 Partial Content`** - Phản hồi phân đoạn tệp PDF cho Canvas lazy-loading.  
  *Content-Type:* `application/pdf`  
  *Headers đi kèm:*
  * `Accept-Ranges: bytes`
  * `Content-Range: bytes 0-1024/2215144`
  * `Content-Length: 1025`
  * `Content-Disposition: inline; filename="attention_is_all_you_need.pdf"`
* **`404 Not Found`** - Không tìm thấy tài liệu hoặc tệp nhị phân bị thiếu trên CAS storage.  
  *Content-Type:* `application/json`
* **`416 Range Not Satisfiable`** - Dải byte yêu cầu nằm ngoài phạm vi kích thước tệp.  
  *Content-Type:* `application/json`  
  *Header đi kèm:* `Content-Range: bytes */2215144`

---

### [GET] `/api/v1/documents/{document_id}/status`
**Summary:** `Polling tiến độ bóc tách bài báo (0 - 100%)`  
**Operation ID:** `get_document_status_api_v1_documents__document_id__status_get`

#### Mô tả (Description)
🎯 **Mục đích:** Frontend polling định kỳ (1-2s) hiển thị tiến độ bóc tách bài báo.

📥 **Đầu vào (Path parameter):**
* `document_id`: UUID của bài báo đang xử lý.

📤 **Đầu ra (HTTP 200):**
* `status`: Trạng thái tổng quát (`uploaded`, `processing`, `completed`, `failed`).
* `progress`: Phần trăm hoàn thành tổng thể (`0` đến `100%`).
* `stage`: Tên bước hiện tại (`running_ocr`, `chunking`, `embedding`...).
* `stages_detail`: Trạng thái con 5 chặng (`validation`, `ocr`, `chunking`...).
* `error_message`: Chi tiết lỗi nếu bước xử lý gặp sự cố.

⚠️ **Lưu ý:**
* Dừng polling ngay khi `status == "completed"` hoặc `status == "failed"`.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | UUID của bài báo đang bóc tách |

#### Responses
* **`200 OK`** - Lấy thông tin tiến độ bóc tách thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
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
    "meta": {
      "request_id": "0ef67d4d-1f53-7b7e-ee5d-0b6d7b1a2f45",
      "timestamp": "2026-09-13T10:00:00Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
* **`422 Unprocessable Entity`** - `document_id` không phải định dạng UUID hợp lệ.  
  *Content-Type:* `application/json`

---

### [POST] `/api/v1/documents/{document_id}:star`
**Summary:** `Lưu bài báo vào thư viện cá nhân (Star/Promotion)`  
**Operation ID:** `star_document_api_v1_documents__document_id__star_post`

#### Mô tả (Description)
🎯 **Mục đích:** Lưu bài báo từ phiên nghiên cứu tạm thời vào kho thư viện cá nhân vĩnh viễn (Star).

📥 **Đầu vào:**
* `document_id`: UUID của bài báo khoa học (bắt buộc, Path parameter).
* `folder_id`: UUID thư mục đề tài nghiên cứu (tùy chọn, Request body). Mặc định là `{ "folder_id": null }` để lưu bài báo vào thư viện chung.

📤 **Đầu ra (HTTP 200):**
* Trả về thông tin bài báo với `is_persistent: true` và `folder_id` đã gán trong một giao dịch ACID.

⚠️ **Lưu ý:**
* Thao tác mang tính lũy thừa (Idempotent): gọi lại nhiều lần sẽ cập nhật `folder_id` mà không tạo bản ghi trùng lặp.
* Khi thao tác trên Swagger UI: hãy chọn example 'Lưu vào thư viện chung' (`{ "folder_id": null }`). Chỉ truyền UUID vào `folder_id` khi bạn đã tạo thư mục thực tế trong hệ thống (nếu truyền UUID ngẫu nhiên sẽ nhận lỗi `404 FOLDER_NOT_FOUND`).
* Lỗi thường gặp: `404` (tài liệu hoặc thư mục không tồn tại / không thuộc quyền sở hữu của user), `422` (sai UUID).

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | UUID của bài báo cần lưu vào thư viện cá nhân |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `folder_id` | `string (uuid)` | Không | `null` | UUID thư mục nghiên cứu muốn phân loại tài liệu vào (để trống hoặc `null` nếu lưu tự do) |

**Ví dụ 1 (Mặc định - Lưu vào thư viện chung không gán thư mục):**
```json
{
  "folder_id": null
}
```

**Ví dụ 2 (Lưu kèm phân loại vào thư mục nghiên cứu):**
```json
{
  "folder_id": "8a391512-4217-48f1-a1b7-d1fa18600d89"
}
```

#### Responses
* **`200 OK`** - Lưu bài báo vào thư viện cá nhân thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "filename": "attention_is_all_you_need.pdf",
      "title": "Attention Is All You Need",
      "status": "completed",
      "is_persistent": true,
      "folder_id": "8a391512-4217-48f1-a1b7-d1fa18600d89",
      "updated_at": "2026-09-13T10:05:00Z"
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc thư mục được chỉ định.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "FOLDER_NOT_FOUND",
      "message": "Folder '8a391512-4217-48f1-a1b7-d1fa18600d89' not found or access denied.",
      "field": "folder_id",
      "action": "Verify folder ID or check user permissions."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - `document_id` hoặc `folder_id` không phải định dạng UUID hợp lệ.  
  *Content-Type:* `application/json`

---

### [DELETE] `/api/v1/documents/{document_id}`
**Summary:** `Xóa bài báo theo đồ thị phụ thuộc (Zero-Retention)`  
**Operation ID:** `delete_document_api_v1_documents__document_id__delete`

#### Mô tả (Description)
🎯 **Mục đích:** Xóa vĩnh viễn bài báo khỏi hệ thống theo cam kết không lưu giữ (Zero-Retention Guarantee).

📥 **Đầu vào:**
* `document_id`: UUID của bài báo khoa học cần xóa (bắt buộc, Path parameter).

📤 **Đầu ra (HTTP 204 No Content):**
* Phản hồi trống (Empty response body), xác nhận đã hoàn tất xóa bài báo và các thực thể phụ thuộc.

⚠️ **Lưu ý:**
* Tự động thực thi `ON DELETE CASCADE` xóa sạch các đoạn văn bản (chunks), vector nhúng (embeddings), và liên kết phiên làm việc (session_documents).
* Tự động giải phóng Content-Addressable Storage (CAS): giảm `ref_count` trong bảng `document_storage_blobs`; chỉ xóa tệp PDF vật lý trên đĩa khi `ref_count == 0`.
* Thao tác mang tính lũy thừa (Idempotent): gọi lần 1 trả về `204 No Content`, các lần gọi tiếp theo khi tài liệu đã bị xóa sẽ trả về `404 DOCUMENT_NOT_FOUND`.
* Đảm bảo cô lập dữ liệu (Multi-tenant): Cố gắng xóa tài liệu của người khác hoặc tài liệu không tồn tại sẽ nhận mã lỗi `404 DOCUMENT_NOT_FOUND`.
* Lỗi thường gặp: `404` (tài liệu không tồn tại hoặc không thuộc quyền sở hữu của user), `422` (sai định dạng UUID).

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | UUID của bài báo khoa học cần xóa khỏi hệ thống |

#### Request Body
*Không yêu cầu Request Body (Body trống).*

#### Responses
* **`204 No Content`** - Xóa bài báo và các dữ liệu liên quan thành công. Không có nội dung trả về trong response body.
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 'e3b0c442-98fc-1c14-9afb-f4c8996fb924' not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - `document_id` không phải định dạng UUID hợp lệ.  
  *Content-Type:* `application/json`

---

### [POST] `/api/v1/documents/{document_id}:parse`
**Summary:** `Kích hoạt / Bóc tách lại với Idempotency`  
**Operation ID:** `parse_document_api_v1_documents__document_id__parse_post`

#### Mô tả (Description)
🎯 **Mục đích:** Kích hoạt hoặc tái kích hoạt tiến trình bóc tách (parsing), trích xuất văn bản, bảng biểu và sinh embedding cho bài báo khoa học. Cung cấp cơ chế Idempotency với cửa sổ 24 giờ chống gửi yêu cầu trùng lặp.

📥 **Đầu vào:**
* `document_id`: UUID của bài báo khoa học cần bóc tách (bắt buộc, Path parameter).
* `Idempotency-Key`: Chuỗi UUID định danh yêu cầu chống trùng lặp trong 24 giờ (tùy chọn, Header parameter).
* `chunk_size`: Kích thước token mục tiêu cho từng đoạn văn bản (mặc định: `512`, khoảng giá trị: `100` đến `2048`).
* `chunk_overlap`: Số lượng token gối đầu giữa các đoạn liền kề (mặc định: `50`, khoảng giá trị: `0` đến `200`, phải nhỏ hơn `chunk_size`).
* `extract_tables`: Bật nhận diện bố cục bảng biểu và hình ảnh chuyên sâu (mặc định: `true`).
* `force_reparse`: Bắt buộc tái bóc tách lại bài báo (mặc định: `false`).

📤 **Đầu ra (HTTP 202 Accepted):**
* Trả về thông tin tiến trình đã được tiếp nhận: `id`, `status: processing`, `stage: validation`, `progress: 0`, thông điệp hướng dẫn và các siêu liên kết HATEOAS (`status_url`, `detail_url`).
* Nếu có header `Idempotency-Key`, phản hồi trả về kèm header `X-Cache: Miss` (lần đầu) hoặc `X-Cache: Idempotent-Hit` (nếu trùng lặp trong 24 giờ).

⚠️ **Lưu ý:**
* Khử trùng lặp Idempotency 24 giờ: Khi gửi kèm header `Idempotency-Key`, hệ thống lưu kết quả xử lý và trả về phản hồi gốc kèm header `X-Cache: Idempotent-Hit` đối với các yêu cầu trùng lặp tiếp theo mà không kích hoạt lại pipeline.
* Máy trạng thái (State Machine):
  - Nếu tài liệu đang xử lý (`status == "processing"`) và `force_reparse == false`: Hệ thống chặn và trả về lỗi `409 DOCUMENT_PROCESSING`.
  - Nếu tài liệu đang xử lý (`status == "processing"`) và `force_reparse == true`: Hệ thống hủy tác vụ cũ và khởi động lại tiến trình từ đầu (`stage: validation`, `progress: 0`).
  - Nếu tài liệu đã hoàn tất (`status == "completed"`) và `force_reparse == false`: Hệ thống trả về trạng thái hoàn tất hiện tại kèm thông điệp hướng dẫn sử dụng `force_reparse`.
  - Nếu tài liệu đã hoàn tất (`status == "completed"`) và `force_reparse == true`: Hệ thống chuyển trạng thái sang `processing` và tiến hành bóc tách lại.
* Cô lập người dùng (Multi-tenant): Chỉ chủ sở hữu bài báo mới có quyền kích hoạt bóc tách; truy cập tài liệu người khác sẽ trả về lỗi `404 DOCUMENT_NOT_FOUND`.
* Lỗi thường gặp: `404` (tài liệu không tồn tại), `409` (đang xử lý), `422` (sai định dạng UUID hoặc chunk_overlap >= chunk_size).

#### Parameters (Path & Header)
| Tên tham số | Vị trí | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `document_id` | `path` | `string (uuid)` | **Có** | - | UUID của bài báo khoa học cần kích hoạt bóc tách |
| `Idempotency-Key` | `header` | `string` | Không | `null` | Khóa UUID khử trùng lặp trong vòng 24 giờ |

#### Request Body
*Content-Type:* `application/json`

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Mặc định | Giới hạn | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `chunk_size` | `integer` | Không | `512` | 100 <= x <= 2048 | Số token mục tiêu cho mỗi chunk |
| `chunk_overlap` | `integer` | Không | `50` | 0 <= x <= 200 | Số token gối đầu (< chunk_size) |
| `extract_tables` | `boolean` | Không | `true` | - | Bật phát hiện bố cục bảng biểu / hình ảnh |
| `force_reparse` | `boolean` | Không | `false` | - | Bắt buộc tái bóc tách ngay cả khi đã hoàn tất |

##### Ví dụ Request Body:
```json
{
  "chunk_size": 512,
  "chunk_overlap": 50,
  "extract_tables": true,
  "force_reparse": false
}
```

#### Responses
* **`202 Accepted`** - Tiến trình bóc tách bài báo được tiếp nhận thành công.  
  *Headers:*  
  - `X-Cache`: `Miss` (lần đầu) hoặc `Idempotent-Hit` (khi trùng lặp khóa trong 24 giờ)  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "status": "processing",
      "stage": "validation",
      "progress": 0,
      "message": "Document parsing pipeline initiated.",
      "links": {
        "status_url": "/api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924/status",
        "detail_url": "/api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924"
      }
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 'e3b0c442-98fc-1c14-9afb-f4c8996fb924' not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`409 Conflict`** - Bài báo đang trong tiến trình xử lý và chưa hoàn tất.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_PROCESSING",
      "message": "Document 'e3b0c442-98fc-1c14-9afb-f4c8996fb924' is already being processed (stage: ocr).",
      "field": "id",
      "action": "Poll progress via GET /api/v1/documents/e3b0c442-98fc-1c14-9afb-f4c8996fb924/status or pass force_reparse=true to restart."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Tham số đầu vào hoặc định dạng UUID không hợp lệ (ví dụ: chunk_overlap >= chunk_size).  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Value error, chunk_overlap must be strictly less than chunk_size",
      "field": "body",
      "action": "Ensure request payload matches the OpenAPI schema specification."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```

---

### [POST] `/api/v1/documents/{document_id}:extract-references`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Bóc tách danh mục tài liệu tham khảo (References / Bibliography).
* **Mục đích:** Bóc tách toàn bộ danh mục tài liệu tham khảo từ bài báo khoa học, phân tích cú pháp chi tiết thành các trường học thuật cấu trúc (`title`, `authors`, `year`, `arxiv_id`, `doi`) và lưu trữ vào cơ sở dữ liệu `reference_items`.
* **Cơ chế lưu đệm cơ sở dữ liệu (Database Cache):** Sau khi bóc tách lần đầu, toàn bộ danh mục được lưu vào cơ sở dữ liệu. Các lần gọi tiếp theo sẽ trả về kết quả ngay lập tức (< 15ms) mà không cần quét lại tệp PDF.
* **Tái bóc tách (Force Re-extract):** Cho phép truyền `force_reextract: true` để xóa bỏ dữ liệu cũ và bóc tách lại từ tệp nhị phân PDF lưu trong Content-Addressable Storage (CAS).
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập dữ liệu của người dùng khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string` (UUID) | Có | UUID định danh duy nhất của bài báo khoa học cần bóc tách tham khảo. |

#### Request Body (`application/json`)
Body tùy chọn (Optional). Mặc định là `{ "force_reextract": false }`.

##### Ví dụ Request Body:
```json
{
  "force_reextract": false
}
```

#### Responses
* **`200 OK`** - Bóc tách hoặc truy xuất danh mục tài liệu tham khảo thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "document_id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "total_extracted": 3,
      "references": [
        {
          "ref_index": 1,
          "raw_text": "Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.",
          "parsed": {
            "title": "Layer normalization",
            "authors": [
              "Jimmy Lei Ba",
              "Jamie Ryan Kiros",
              "Geoffrey E Hinton"
            ],
            "year": 2016,
            "arxiv_id": "1607.06450",
            "doi": null
          }
        },
        {
          "ref_index": 2,
          "raw_text": "Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. arXiv:1409.0473, 2014.",
          "parsed": {
            "title": "Neural machine translation by jointly learning to align and translate",
            "authors": [
              "Dzmitry Bahdanau",
              "Kyunghyun Cho",
              "Yoshua Bengio"
            ],
            "year": 2014,
            "arxiv_id": "1409.0473",
            "doi": null
          }
        },
        {
          "ref_index": 3,
          "raw_text": "Ashish Vaswani et al. Attention is all you need. In NeurIPS, 2017. doi:10.5555/3295222.3295349",
          "parsed": {
            "title": "Attention is all you need",
            "authors": [
              "Ashish Vaswani et al."
            ],
            "year": 2017,
            "arxiv_id": null,
            "doi": "10.5555/3295222.3295349"
          }
        }
      ]
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 'e3b0c442-98fc-1c14-9afb-f4c8996fb924' not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Định dạng UUID không hợp lệ.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1",
      "field": "document_id",
      "action": "Ensure request payload matches the OpenAPI schema specification."
    },
    "meta": {
      "request_id": "2b3cd45e-6f78-90ab-cdef-1234567890ab",
      "timestamp": "2026-09-13T10:05:00Z"
    }
  }
  ```


---

### [GET] `/api/v1/documents/{document_id}/structure`
**Summary:** `Truy xuất cấu trúc bài báo (TOC, Headings, Sections, Abstract)`  
**Operation ID:** `get_document_structure_api_v1_documents__document_id__structure_get`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Truy xuất cấu trúc bài báo khoa học (Table of Contents, Headings, Sections).
* **Mục đích:** Cung cấp thông tin cấu trúc phân cấp (Sections, Headings) và toàn văn Abstract kèm tọa độ Bounding Box chuẩn hóa `[x0, y0, x1, y1, page]` nhằm phục vụ điều hướng (TOC navigation bar) và hiển thị tương tác trên giao diện Deep Reading Canvas (PDF.js).
* **Cơ chế lưu đệm cơ sở dữ liệu (Database Cache):** Cấu trúc được lưu trực tiếp vào trường `parsed_metadata["structure"]` (PostgreSQL JSONB với GIN index). Lần truy vấn sau trả về tức thì trong < 15ms mà không cần bóc tách lại từ PDF.
* **Tái bóc tách (Force Refresh):** Cho phép truyền Query parameter `?force_refresh=true` để bỏ qua bộ đệm cơ sở dữ liệu và ép phân tích lại từ tệp nhị phân PDF lưu trong CAS storage.
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập dữ liệu của người dùng khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học. |
| `query` | `force_refresh` | `boolean` | Không | Nếu `true`, bỏ qua bộ nhớ đệm và phân tích lại cấu trúc từ PDF gốc. Mặc định: `false`. |

#### Responses
* **`200 OK`** - Truy xuất cấu trúc bài báo thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "document_id": "e3b0c442-98fc-1c14-9afb-f4c8996fb924",
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      "abstract_bounding_boxes": [
        [0.2346, 0.5219, 0.7654, 0.6543, 1]
      ],
      "sections": [
        {
          "title": "1 Introduction",
          "page_number": 2,
          "bounding_boxes": [
            [0.1765, 0.0919, 0.3118, 0.107, 2]
          ]
        },
        {
          "title": "2 Background",
          "page_number": 2,
          "bounding_boxes": [
            [0.1765, 0.4585, 0.3085, 0.4736, 2]
          ]
        },
        {
          "title": "3 Model Architecture",
          "page_number": 2,
          "bounding_boxes": [
            [0.1765, 0.8112, 0.3694, 0.8263, 2]
          ]
        }
      ]
    },
    "meta": {
      "request_id": "req_51ad5379d56e",
      "timestamp": "2026-09-16T03:27:18.047347Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 'e3b0c442-98fc-1c14-9afb-f4c8996fb924' not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "req_404_abc123",
      "timestamp": "2026-09-16T03:27:18.113645Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Định dạng `document_id` không phải UUID hợp lệ.  
  *Content-Type:* `application/json`

---

### [GET] `/api/v1/documents/{document_id}/chunks`
**Summary:** `Danh sách Chunks (phân trang + include_content)`  
**Operation ID:** `get_document_chunks_api_v1_documents__document_id__chunks_get`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Truy xuất danh sách các đoạn văn bản ngữ nghĩa (Chunks) kèm tọa độ không gian chính xác (Bounding Boxes).
* **Mục đích:** Cung cấp tọa độ không gian chuẩn hóa `[x0, y0, x1, y1, page]` và nội dung văn bản của từng khối đoạn văn phục vụ hiển thị lớp phủ highlight trực quan trên PDF.js Canvas và hỗ trợ Hybrid RAG retrieval.
* **Tối ưu hóa băng thông (Bandwidth Optimization):** Hỗ trợ tham số `include_content=false`. Khi đặt giá trị này, trường `content` trả về `null`, giúp tiết kiệm hơn 80% dung lượng payload truyền tải khi frontend chỉ cần tọa độ hình học để vẽ bounding boxes.
* **Lọc theo trang vật lý (Page Filtering):** Cho phép truyền `?page_number={n}` để chỉ lấy các chunks thuộc riêng một trang vật lý của file PDF, tối ưu hóa quá trình lazy-load từng trang trên Canvas.
* **Tự động bóc tách & Lưu đệm (On-Demand Extraction & Persistence):** Nếu tài liệu chưa được phân đoạn trước đó, hệ thống tự động bóc tách từ file PDF gốc qua PyMuPDF, lưu vào bảng `document_chunks` và cập nhật `chunk_count` của tài liệu trong một giao dịch ACID. Các lần truy vấn sau trả về trực tiếp từ cơ sở dữ liệu trong < 15ms.
* **Phân trang chuẩn RFC 8288 (HATEOAS Links):** Trả về đầy đủ siêu dữ liệu phân trang và các liên kết điều hướng `first`, `prev`, `self`, `next`, `last`.
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập tài liệu của người khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học. |
| `query` | `page` | `integer` | Không | Số thứ tự trang kết quả (1-indexed). Mặc định: `1`, tối thiểu: `1`. |
| `query` | `per_page` | `integer` | Không | Số lượng chunks tối đa mỗi trang. Mặc định: `50`, từ `1` đến `200`. |
| `query` | `page_number` | `integer` | Không | Tùy chọn lọc các chunk thuộc riêng một trang vật lý của file PDF (1-indexed). |
| `query` | `include_content` | `boolean` | Không | Nếu `false`, trường `content` trả về `null` giúp tiết kiệm >80% dung lượng payload phục vụ vẽ Canvas. Mặc định: `true`. |

#### Responses
* **`200 OK`** - Truy xuất danh sách chunks thành công kèm siêu dữ liệu phân trang.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "1cf7b489-e75d-425b-b52d-7c310ef90d51",
        "document_id": "6697dc74-f24c-4ae2-8993-ec83f6817078",
        "chunk_index": 0,
        "page_number": 1,
        "content": "Advancing Retrieval-Augmented Generation for Structured Enterprise Data...",
        "bounding_boxes": [
          [0.1663, 0.1292, 0.8337, 0.1854, 1]
        ],
        "token_count": 5
      }
    ],
    "meta": {
      "total": 154,
      "page": 1,
      "per_page": 10,
      "total_pages": 16,
      "request_id": "req_0562b36b173b",
      "timestamp": "2026-09-16T04:01:32.612558Z"
    },
    "links": {
      "first": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks?page=1&per_page=10",
      "prev": null,
      "self": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks?page=1&per_page=10",
      "next": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks?page=2&per_page=10",
      "last": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks?page=16&per_page=10"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 6b26d29f-ad24-4c96-b2bc-a02def948ee8 not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "req_404_chunk123",
      "timestamp": "2026-09-16T04:01:32.638705Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Tham số phân trang hoặc định dạng UUID không hợp lệ (ví dụ: `per_page > 200` hoặc `page < 1`).  
  *Content-Type:* `application/json`


---

### [GET] `/api/v1/documents/{document_id}/chunks/{chunk_id}`
**Summary:** `Chi tiết 1 đoạn bằng chứng (Chunk Detail + Nav Links)`  
**Operation ID:** `get_document_chunk_detail_api_v1_documents__document_id__chunks__chunk_id__get`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Truy xuất toàn văn nội dung, tọa độ Bounding Boxes hình học chuẩn hóa và liên kết điều hướng lân cận cho một đoạn bằng chứng (Chunk) cụ thể.
* **Mục đích:** Cung cấp đầy đủ nội dung văn bản gốc, tọa độ chuẩn hóa `[x0, y0, x1, y1, page]` và liên kết lân cận (`prev_chunk`, `next_chunk`) phục vụ giao diện Deep Reading Canvas nhảy đến vị trí đoạn văn bản, đồng thời hỗ trợ Citation Inspector duyệt mở rộng ngữ cảnh trước và sau của bằng chứng khoa học.
* **Liên kết HATEOAS & Điều hướng (Hypermedia Links):**
  - `self`: URL định danh đoạn văn bản hiện tại.
  - `document`: URL tài liệu cha (`/api/v1/documents/{document_id}`).
  - `chunks`: URL danh sách tất cả chunks (`/api/v1/documents/{document_id}/chunks`).
  - `prev_chunk`: URL đoạn văn bản đứng liền trước (`chunk_index - 1`), hoặc `null` nếu là chunk đầu tiên.
  - `next_chunk`: URL đoạn văn bản đứng liền sau (`chunk_index + 1`), hoặc `null` nếu là chunk cuối cùng.
* **Tự động bóc tách On-demand (On-Demand Extraction):** Nếu tài liệu chưa từng được phân đoạn, hệ thống tự động bóc tách và lưu vào cơ sở dữ liệu trước khi truy xuất chunk.
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập tài liệu của người dùng khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học. |
| `path` | `chunk_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của đoạn bằng chứng (Chunk). |

#### Responses
* **`200 OK`** - Truy xuất chi tiết đoạn bằng chứng thành công kèm tọa độ bounding boxes và navigational links.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "1cf7b489-e75d-425b-b52d-7c310ef90d51",
      "document_id": "6697dc74-f24c-4ae2-8993-ec83f6817078",
      "chunk_index": 1,
      "page_number": 1,
      "content": "Attention mechanisms have become an integral part of compelling sequence modeling and transduction models...",
      "bounding_boxes": [
        [0.1663, 0.2292, 0.8337, 0.3854, 1]
      ],
      "token_count": 42,
      "embedding_dimension": 1536,
      "created_at": "2026-09-16T04:01:32.612558Z",
      "updated_at": "2026-09-16T04:01:32.612558Z",
      "links": {
        "self": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks/1cf7b489-e75d-425b-b52d-7c310ef90d51",
        "document": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078",
        "chunks": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks",
        "prev_chunk": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks/0bf6a378-d14c-42eb-9112-aa310ef90d10",
        "next_chunk": "/api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks/2de8c590-f86d-43bc-a43e-8c420fa01e62"
      }
    },
    "meta": {
      "request_id": "req_0562b36b173b",
      "timestamp": "2026-09-16T04:01:32.612558Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy tài liệu hoặc không tìm thấy chunk tương ứng.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "CHUNK_NOT_FOUND",
      "message": "Chunk 1cf7b489-e75d-425b-b52d-7c310ef90d51 not found for document 6697dc74-f24c-4ae2-8993-ec83f6817078.",
      "field": "chunk_id",
      "action": "Verify chunk ID or query GET /api/v1/documents/6697dc74-f24c-4ae2-8993-ec83f6817078/chunks for available chunks."
    },
    "meta": {
      "request_id": "req_404_chunk123",
      "timestamp": "2026-09-16T04:01:32.638705Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Định dạng UUID của `document_id` hoặc `chunk_id` không hợp lệ.  
  *Content-Type:* `application/json`

---

### [GET] `/api/v1/documents/{document_id}/summary`
**Summary:** `Lấy bản tóm tắt 3 ý cốt lõi (Problem, Contributions, Limitations) kèm Bounding Boxes`  
**Operation ID:** `get_document_summary_api_v1_documents__document_id__summary_get`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Truy xuất bản tóm tắt 3 ý cốt lõi (Vấn đề nghiên cứu, Đóng góp chính, và Giới hạn/Hướng phát triển tương lai) kèm tọa độ không gian Bounding Boxes chuẩn hóa cho bài báo.
* **Mục đích:** Cung cấp thông tin tóm tắt nhanh, cô đọng phục vụ hiển thị trên thẻ bài báo (Document Card), thanh bên (Sidebar Summary), hoặc Quick Inspect Modal mà không cần đọc toàn bộ văn bản. Hỗ trợ bấm vào từng ý tóm tắt để nhảy đến bằng chứng trực quan trên giao diện đọc PDF Canvas (Visual Grounding).
* **Chuẩn thiết kế Singleton Sub-resource (Google AIP-130):** Endpoint `/summary` đóng vai trò là một singleton sub-resource trực thuộc `documents/{id}` (mỗi bài báo chỉ có duy nhất 1 bản tóm tắt, không cần ID con).
* **Tự động tổng hợp On-Demand:** Trường hợp bài báo đã hoàn thành xử lý nhưng chưa có bản tóm tắt trong CSDL, hệ thống tự động bóc tách và trích xuất bằng chứng theo heuristic / LLM, lưu vào CSDL và trả về ngay trong cùng một yêu cầu.
* **Bảo vệ vòng đời tài liệu (Lifecycle Protection):**
  - Trả về `409 Conflict` (`DOCUMENT_PROCESSING`) nếu bài báo đang trong hàng đợi hoặc đang bóc tách.
  - Trả về `422 Unprocessable Content` (`DOCUMENT_FAILED`) nếu bài báo bị lỗi khi nạp.
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập tài liệu của người dùng khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học. |

#### Responses
* **`200 OK`** - Truy xuất bản tóm tắt 3 ý cốt lõi thành công kèm tọa độ Visual Grounding Bounding Boxes.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "document_id": "1960d8cb-f708-49b0-aa05-8ae54c869306",
      "problem_statement": {
        "text": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder.",
        "bounding_boxes": [
          [0.102, 0.155, 0.898, 0.182, 1]
        ]
      },
      "contributions": {
        "text": "On the WMT 2014 English-to-French translation task, our model establishes a new state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs.",
        "bounding_boxes": [
          [0.102, 0.450, 0.898, 0.485, 2]
        ]
      },
      "limitations": {
        "text": "Computational complexity scales quadratically with sequence length, posing challenges for long documents.",
        "bounding_boxes": [
          [0.102, 0.720, 0.898, 0.755, 9]
        ]
      },
      "total_tokens": 130,
      "latency_ms": 1
    },
    "meta": {
      "request_id": "0779c162-e9e2-40e0-ac01-439b05cae079",
      "timestamp": "2026-09-16T08:08:05.544031Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document "ad48ceb3-dc25-464a-9d75-08adcddf02f8" not found.",
      "field": "id",
      "action": "Verify document ID or check access permissions."
    },
    "meta": {
      "request_id": "8f700731-e725-44ff-a8fd-e248f1ba0b00",
      "timestamp": "2026-09-16T08:08:05.557020Z"
    }
  }
  ```
* **`409 Conflict`** - Bài báo đang được xử lý trong hàng đợi, chưa thể trích xuất tóm tắt.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_PROCESSING",
      "message": "Document is still being processed. Wait for completion before querying summary.",
      "field": "id",
      "action": "Poll GET /api/v1/documents/{id}/status until status is "completed"."
    }
  }
  ```
* **`422 Unprocessable Entity`** - Bài báo bị lỗi bóc tách hoặc định dạng UUID không hợp lệ.  
  *Content-Type:* `application/json`


---

### [POST] `/api/v1/documents/{document_id}/summary:generate`
**Summary:** `Custom Method (AIP-136): Sinh mới / Tái tổng hợp tóm tắt 3 ý cốt lõi (Problem, Contributions, Limitations) kèm Bounding Boxes`  
**Operation ID:** `generate_document_summary_api_v1_documents__document_id__summary_generate_post`

#### Mô tả (Description)
* **Tóm tắt (Summary):** Kích hoạt quy trình sinh mới hoặc tái tổng hợp bản tóm tắt 3 ý cốt lõi (Vấn đề nghiên cứu, Đóng góp chính, Giới hạn/Hướng phát triển tương lai) kèm tọa độ Bounding Boxes chuẩn hóa từ mô hình LLM với cơ chế phân rã trích dẫn (visual grounding).
* **Chuẩn thiết kế Custom Method (Google AIP-136):** Sử dụng cú pháp custom method chuẩn `:generate` gắn trực tiếp vào singleton resource `documents/{document_id}/summary`.
* **Cơ chế Cache và Tái tổng hợp (`force` parameter):**
  - Khi `force=false` (mặc định): Tự động trả về bản tóm tắt hiện có trong cơ sở dữ liệu (Cache Hit SLA < 100ms) kèm HTTP header `X-Cache: Cache-Hit`. Nếu chưa có trong CSDL, hệ thống mới gọi LLM để sinh bản tóm tắt đầu tiên và trả về `X-Cache: Generated`.
  - Khi `force=true`: Ép buộc hệ thống bỏ qua cache CSDL, gọi LLM tái sinh bản tóm tắt mới nhất, cập nhật lại CSDL và trả về `X-Cache: Generated`.
* **Bảo vệ chống gửi trùng lặp (Idempotency Key):**
  - Hỗ trợ HTTP header tùy chọn `Idempotency-Key` (hoặc `X-Idempotency-Key`).
  - Khi client gửi cùng một khóa idempotency trong khoảng thời gian hiệu lực, hệ thống trả về kết quả đã cache kèm HTTP header `X-Cache: Idempotent-Hit`.
* **Khả năng dự phòng lỗi (Resilient Fallback):**
  - Trong trường hợp dịch vụ LLM bên ngoài bị gián đoạn hoặc gặp lỗi, hệ thống tự động kích hoạt bộ trích dẫn Heuristic Grounded Summarizer dựa trên phân tích cấu trúc tài liệu để đảm bảo tính liên tục của dịch vụ.
* **Bảo vệ vòng đời tài liệu (Lifecycle Protection):**
  - Trả về `409 Conflict` (`DOCUMENT_PROCESSING`) nếu bài báo đang trong hàng đợi hoặc đang bóc tách.
  - Trả về `422 Unprocessable Content` (`DOCUMENT_FAILED`) nếu bài báo bị lỗi khi nạp.
* **Bảo mật & Cô lập:** Tuân thủ đa người dùng (Multi-tenant isolation), từ chối truy cập tài liệu của người dùng khác với mã lỗi `404 DOCUMENT_NOT_FOUND`.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học. |

#### Request Headers
| Tên Header | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `Idempotency-Key` | `string` | Không | Khóa định danh yêu cầu chống gửi lặp lại (Idempotency Key). |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `force` | `boolean` | Không | `false` | Cờ ép buộc tái tổng hợp: `false` sử dụng cache CSDL (nếu có); `true` ép gọi LLM sinh mới. |

#### Responses
* **`200 OK`** - Sinh mới hoặc truy xuất tóm tắt 3 ý cốt lõi thành công kèm tọa độ Visual Grounding Bounding Boxes.  
  *Headers:* `X-Cache: Cache-Hit | Generated | Idempotent-Hit`  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "document_id": "6a6cbadb-517c-40db-bcdf-c57975cc016a",
      "problem_statement": {
        "text": "The research addresses the inability of conventional RAG systems to handle structured enterprise data.",
        "bounding_boxes": [
          [0.1176, 0.3165, 0.2185, 0.3346, 1]
        ]
      },
      "contributions": {
        "text": "The work proposes an enterprise-focused RAG framework that combines semantic routing with schema linking.",
        "bounding_boxes": [
          [0.1176, 0.3509, 0.4919, 0.9121, 1]
        ]
      },
      "limitations": {
        "text": "The framework currently does not support multimodal data or complex tabular reasoning.",
        "bounding_boxes": [
          [0.5081, 0.3199, 0.8824, 0.5047, 1]
        ]
      },
      "total_tokens": 1825,
      "latency_ms": 7573
    },
    "meta": {
      "request_id": "8dbfde90-4f96-426d-9306-7223dcd7d5d5",
      "timestamp": "2026-09-16T08:48:10.980100Z"
    }
  }
  ```
* **`404 Not Found`** - Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document \"ad48ceb3-dc25-464a-9d75-08adcddf02f8\" not found.",
      "field": "id",
      "action": "Ensure UUID exists and belongs to the authenticated user."
    },
    "meta": {
      "request_id": "8f700731-e725-44ff-a8fd-e248f1ba0b00",
      "timestamp": "2026-09-16T08:08:05.557020Z"
    }
  }
  ```
* **`409 Conflict`** - Bài báo đang được xử lý trong hàng đợi, chưa thể trích xuất tóm tắt.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_PROCESSING",
      "message": "Document is still being processed. Wait for completion before querying summary.",
      "field": "id",
      "action": "Poll GET /api/v1/documents/{id}/status until status is \"completed\"."
    }
  }
  ```
* **`422 Unprocessable Entity`** - Bài báo bị lỗi bóc tách hoặc định dạng UUID / tham số không hợp lệ.  
  *Content-Type:* `application/json`

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

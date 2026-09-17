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

---

### [GET] `/api/v1/documents/{document_id}/export-pdf`

Xuất file PDF gốc kèm các lớp Highlight trực quan (Native PDF Annotations chuẩn ISO 32000-1 / ISO 32000-2), cây thư mục điều hướng (Bookmarks / Outlines) và Metadata chuẩn hóa được gắn trực tiếp vào luồng nhị phân PDF. Các điểm trích dẫn grounded (Problem Statement, Contributions, Limitations) xuất hiện dưới dạng highlight màu tương ứng và sticky popup notes có thể đọc và tương tác trên Adobe Acrobat, Preview, Chrome PDF Viewer, Foxit Reader, Zotero, Mendeley.

#### Đặc điểm kỹ thuật
* **Chuẩn ISO 32000 Conformance:** Sử dụng subtype `/Highlight` và `/QuadPoints` để vẽ highlight chuẩn quốc tế, không làm hỏng cấu trúc văn bản tệp PDF gốc (vẫn copy text, tìm kiếm Ctrl+F bình thường).
* **Semantic Color Hierarchy:**
  - Problem Statement: San hô / Coral (`RGB(0.95, 0.40, 0.30)`)
  - Contributions: Ngọc lục bảo / Emerald (`RGB(0.15, 0.75, 0.45)`)
  - Limitations: Thạch anh tím / Violet (`RGB(0.60, 0.35, 0.85)`)
* **Metadata & Popup Notes:** Mỗi highlight chứa tiêu đề danh mục và nội dung text trích xuất nguyên bản để tra cứu tức thì khi hover/click.
* **Tự động nhúng PDF Bookmarks (Outlines Navigation):** Tự động chèn cây mục lục điều hướng ở thanh bên trái (Sidebar Table of Contents) trỏ trực tiếp đến trang và vị trí của từng phát hiện AI:
  ```text
  📑 VeriScholar AI Grounded Summary
     ├── 🟧 Problem Statement
     ├── 🟩 Contributions
     └── 🟪 Limitations
  ```
* **Chuẩn hóa Document Metadata (Zotero / Mendeley / EndNote Support):** Cập nhật metadata nhị phân của tài liệu (`Title`, `Author`, `Subject`, `Keywords`, `Producer`) giúp các phần mềm quản lý trích dẫn tự động nhận diện thông tin bài báo.
* **Lọc danh mục linh hoạt (`categories`):** Hỗ trợ lọc các danh mục cần highlight thông qua query parameter `categories=problem_statement,contributions`.
* **Tùy chọn xuất file sạch:** Hỗ trợ query parameter `include_highlights=false` để tải tệp PDF gốc không chứa annotations.
* **Tương thích RFC 6266:** Header `Content-Disposition: attachment; filename="<tên_tệp>_annotated.pdf"; filename*=UTF-8''...` hỗ trợ tên file Unicode tiếng Việt an toàn.
* **Header đếm số lượng:** Header `X-Annotation-Count` phản ánh chính xác số lượng highlight được gắn vào tài liệu.

#### Parameters
| Vị trí | Tên tham số | Kiểu dữ liệu | Mặc định | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `path` | `document_id` | `string (uuid)` | - | **Có** | UUID định danh duy nhất của tài liệu cần xuất PDF. |
| `query` | `include_highlights` | `boolean` | `true` | Không | Nếu `true`, gắn các highlight ISO 32000 tương ứng các ý cốt lõi. Nếu `false`, trả về PDF gốc. |
| `query` | `categories` | `string` | `null` | Không | Danh sách các danh mục cần highlight cách nhau bởi dấu phẩy (`problem_statement`, `contributions`, `limitations`). Bỏ trống = tất cả. |

#### Responses
* **`200 OK`** - Luồng dữ liệu nhị phân PDF chuẩn ISO.  
  *Content-Type:* `application/pdf`  
  *Headers:*
  - `Content-Disposition`: `attachment; filename="..._annotated.pdf"; filename*=UTF-8''...`
  - `Content-Length`: `438500`
  - `X-Annotation-Count`: `7`
  - `Cache-Control`: `private, no-transform`
* **`404 Not Found`** - Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập (Multi-tenant isolation).  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document 'f47ac10b-58cc-4372-a567-0e02b2c3d479' not found.",
      "field": "id",
      "action": "Ensure UUID exists and belongs to the authenticated user."
    },
    "meta": {
      "request_id": "8f700731-e725-44ff-a8fd-e248f1ba0b00",
      "timestamp": "2026-09-16T15:40:00Z"
    }
  }
  ```
* **`422 Unprocessable Entity`** - Định dạng UUID không hợp lệ hoặc dữ liệu PDF vật lý bị lỗi.  
  *Content-Type:* `application/json`

---

### [POST] `/api/v1/documents/{document_id}/summary:stream`
**Summary:** `# 57. Tóm tắt 3 ý cốt lõi luồng động SSE (Real-Time Grounded Summary Stream)`  
**Operation ID:** `stream_document_summary_api_v1_documents__document_id__summary_stream_post`

#### Mô tả (Description)
* **Mục đích:** Tối ưu hóa trải nghiệm đọc sâu thời gian thực (Deep Reading Experience), giải quyết triệt để rào cản độ trễ (latency) khi chờ đợi mô hình AI tổng hợp toàn bộ bài báo. Bằng cách thiết lập luồng truyền Server-Sent Events (SSE), người dùng nhận được phản hồi ngay lập tức với **Time-to-First-Token (TTFT) < 1 giây**.
* **Đặc tính truyền luồng sự kiện (SSE Event Protocol):** Luồng dữ liệu truyền theo định dạng `text/event-stream` với 4 sự kiện tuần tự:
  1. `summary_start`: Báo hiệu bắt đầu luồng tóm tắt.
     - Payload: `{"document_id": "<UUID>", "status": "streaming"}`
  2. `summary_chunk`: Phát từng token văn bản của luận điểm đang xử lý.
     - Payload: `{"section": "problem_statement" | "contributions" | "limitations", "token": "..."}`
  3. `summary_box`: Ngay khi một luận điểm hoàn tất, server gửi ngay danh sách các toạ độ Bounding Boxes 5-tuples `[x0, y0, x1, y2, page]` trích xuất từ PDF gốc.
     - Payload: `{"section": "problem_statement" | "contributions" | "limitations", "bounding_boxes": [[0.1, 0.2, 0.8, 0.4, 1]]}`
  4. `summary_end`: Báo hiệu kết thúc toàn bộ luồng truyền tải dữ liệu.
     - Payload: `{"document_id": "<UUID>", "finish_reason": "completed"}`
* **Cơ chế Visual Grounding trực quan hóa Canvas:** Giao diện Deep Reading Canvas (PDF.js) lắng nghe sự kiện `summary_box` để lập tức cuộn trang và vẽ highlight vùng bằng chứng màu vàng/cam/tím tương ứng, đồng bộ hoàn hảo với dòng chữ đang được in ra.
* **Xử lý ngắt kết nối (Client Disconnection Resilience):** Server liên tục kiểm tra tín hiệu ngắt kết nối qua `request.is_disconnected`. Nếu người dùng đóng trình duyệt hoặc chuyển trang, server lập tức hủy bỏ tác vụ sinh token và giải phóng tài nguyên CPU/GPU/RAM.
* **Tối ưu hóa Proxy & Buffering Bypass:**
  - Header `Cache-Control: no-cache`
  - Header `Connection: keep-alive`
  - Header `X-Accel-Buffering: no` (ngăn cản Nginx, Cloudflare hoặc Ingress Controller buffer dữ liệu SSE).
* **Bảo vệ vòng đời tài liệu & Multi-tenant:**
  - Trả về `404 DOCUMENT_NOT_FOUND` nếu tài liệu không tồn tại hoặc không thuộc quyền sở hữu của người dùng.
  - Trả về `409 DOCUMENT_PROCESSING` nếu tài liệu đang trong quá trình bóc tách/OCR nền.
  - Trả về `422 DOCUMENT_FAILED` nếu tài liệu thất bại trong quá trình tiền xử lý.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | **Có** | UUID định danh duy nhất của bài báo khoa học (hỗ trợ alias path `{id}`). |

#### Request Headers
| Tên Header | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `Accept` | `string` | Không | Khuyến nghị `text/event-stream`. |
| `Authorization` | `string` | **Có** | Bearer Token của người dùng đã xác thực. |

#### Request Body
*Không có (Endpoint singleton method thao tác trực tiếp trên document_id).*

#### Responses
* **`200 OK`** - Luồng sự kiện Server-Sent Events (`text/event-stream`).  
  *Headers:*
  - `Content-Type: text/event-stream; charset=utf-8`
  - `Cache-Control: no-cache`
  - `Connection: keep-alive`
  - `X-Accel-Buffering: no`

  ```text
  event: summary_start
  data: {"document_id": "6a6cbadb-517c-40db-bcdf-c57975cc016a", "status": "streaming"}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "Conventional "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "RAG "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "systems "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "struggle "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "with "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "structured "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "enterprise "}

  event: summary_chunk
  data: {"section": "problem_statement", "token": "data. "}

  event: summary_box
  data: {"section": "problem_statement", "bounding_boxes": [[0.1176, 0.3165, 0.2185, 0.3346, 1]]}

  event: summary_chunk
  data: {"section": "contributions", "token": "The "}

  event: summary_chunk
  data: {"section": "contributions", "token": "authors "}

  event: summary_chunk
  data: {"section": "contributions", "token": "propose "}

  event: summary_chunk
  data: {"section": "contributions", "token": "hybrid "}

  event: summary_chunk
  data: {"section": "contributions", "token": "schema "}

  event: summary_chunk
  data: {"section": "contributions", "token": "linking. "}

  event: summary_box
  data: {"section": "contributions", "bounding_boxes": [[0.1176, 0.3509, 0.4919, 0.9121, 1]]}

  event: summary_chunk
  data: {"section": "limitations", "token": "Evaluation "}

  event: summary_chunk
  data: {"section": "limitations", "token": "is "}

  event: summary_chunk
  data: {"section": "limitations", "token": "limited "}

  event: summary_chunk
  data: {"section": "limitations", "token": "to "}

  event: summary_chunk
  data: {"section": "limitations", "token": "internal "}

  event: summary_chunk
  data: {"section": "limitations", "token": "benchmarks. "}

  event: summary_box
  data: {"section": "limitations", "bounding_boxes": [[0.5081, 0.3199, 0.8824, 0.5047, 1]]}

  event: summary_end
  data: {"document_id": "6a6cbadb-517c-40db-bcdf-c57975cc016a", "finish_reason": "completed"}
  ```

* **`404 Not Found`** - Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Document '6a6cbadb-517c-40db-bcdf-c57975cc016a' not found.",
      "field": "id",
      "action": "Ensure UUID exists and belongs to authenticated user."
    },
    "meta": {
      "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
      "timestamp": "2026-09-17T10:00:00Z"
    }
  }
  ```

* **`409 Conflict`** - Tài liệu đang trong quá trình bóc tách/OCR nền (`DOCUMENT_PROCESSING`).  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_PROCESSING",
      "message": "Document is currently being processed by background worker.",
      "field": "status",
      "action": "Poll /api/v1/documents/{document_id}/status until status reaches 'completed'."
    },
    "meta": {
      "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
      "timestamp": "2026-09-17T10:00:00Z"
    }
  }
  ```

* **`422 Unprocessable Content`** - Tài liệu bị lỗi tiền xử lý hoặc định dạng UUID không hợp lệ.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_FAILED",
      "message": "Document processing failed permanently. Cannot synthesize summary.",
      "field": "id",
      "action": "Re-upload the document or inspect processing error message."
    },
    "meta": {
      "request_id": "c1f7a2d4-e69c-4b53-9118-2e63ad0ec2e9",
      "timestamp": "2026-09-17T10:00:00Z"
    }
  }
  ```

#### Ví dụ gọi lệnh cURL (Streaming without buffer)
```bash
curl -N -X POST "http://localhost:8000/api/v1/documents/6a6cbadb-517c-40db-bcdf-c57975cc016a/summary:stream" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Accept: text/event-stream"
```


---

## 3. Nhóm API Phiên nghiên cứu đa bài (Research Sessions)

### [POST] `/api/v1/sessions`
**Summary:** `# 45. Khởi tạo phiên nghiên cứu đa bài mới (Research Session)`  
**Operation ID:** `create_session_api_v1_sessions_post`

#### Mô tả (Description)
* **Khởi tạo phiên nghiên cứu (Research Session):** Tạo một workspace làm việc mới cho phép nạp từ 0 đến tối đa 5 bài báo khoa học cùng lúc phục vụ tổng hợp, so sánh, đối chiếu đa tài liệu.
* **Cơ chế Idempotency chống gửi trùng lặp:** Hỗ trợ header `Idempotency-Key` (hoặc `X-Idempotency-Key`). Khi gửi cùng một key trong 24 giờ, hệ thống trả về phiên đã tạo kèm header `X-Cache: Idempotent-Hit`.
* **Cơ chế Auto-naming Fallback:** Trường `title` là tùy chọn. Nếu không truyền, hệ thống tự động đặt tên theo bài báo đầu tiên `Nghiên cứu: {doc.title}` hoặc `Phiên nghiên cứu {DD/MM/YYYY HH:mm}` nếu phiên rỗng. Chuỗi chỉ gồm khoảng trắng vẫn bị chặn `422`.
* **Cơ chế Active Document:** Tự động gán `active_document_id` trỏ đến tài liệu đầu tiên trong danh sách `initial_document_ids` (hoặc `null` nếu phiên khởi tạo rỗng).
* **Trạng thái Viewport Canvas:** Khởi tạo `viewport_state` với các giá trị mặc định chuẩn `{"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}` và tab mặc định `active_tab: "chat"`.
* **Nhúng Metadata Bài Báo (`include_documents=true`):** Tùy chọn trả về mảng `documents` chi tiết (title, filename, status, file_size_bytes, added_at, display_order) giúp frontend hiển thị tab ngay mà không cần gọi nhiều request phụ.
* **Cảnh báo trạng thái (`warnings`):** Tự động phát hiện và cảnh báo nếu có tài liệu nạp vào chưa hoàn tất bóc tách (status `processing` hoặc `failed`).
* **RFC 7231 & REST Headers:**
  - Trả về mã trạng thái HTTP `201 Created` (hoặc `200 OK` khi Idempotent Cache Hit).
  - Cung cấp header `Location: /api/v1/sessions/{session_id}`.
  - Cung cấp header `ETag: "v1"` kiểm soát đồng thời lạc quan (Optimistic Concurrency Control).
* **Ràng buộc dung lượng (Capacity Guard):** Nếu số lượng tài liệu trong `initial_document_ids` vượt quá 5, hệ thống từ chối và trả về lỗi `400 Bad Request` với mã lỗi `SESSION_CAPACITY_EXCEEDED`.
* **Bảo mật Đa người dùng (Multi-tenant Isolation):** Tất cả tài liệu nạp vào phải thuộc quyền sở hữu của người dùng hiện tại; nếu có tài liệu không tồn tại hoặc thuộc người khác, trả về `404 Not Found` (`DOCUMENT_NOT_FOUND`).

#### Request Headers
| Tên Header | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `Idempotency-Key` | `string` | Không | Khóa định danh duy nhất chống trùng lặp request (cửa sổ 24 giờ). |

#### Parameters (Query)
| Tên tham số | Kiểu dữ liệu | Mặc định | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `include_documents` | `boolean` | `false` | Không | Nếu `true`, trả về metadata chi tiết của các bài báo trong phiên. |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `title` | `string` | Không | `null` | Tiêu đề của phiên. Nếu để trống, tự động sinh từ bài báo đầu tiên. Nếu truyền chuỗi khoảng trắng thì bị chặn `422`. |
| `initial_document_ids` | `list[string (uuid)]` | Không | `[]` | Danh sách UUID của các bài báo nạp vào phiên ban đầu (tối đa 5 bài báo). Trùng lặp sẽ tự động được khử. |

#### Responses
* **`201 Created`** - Phiên nghiên cứu được khởi tạo thành công.  
  *Headers:*
  - `Location`: `/api/v1/sessions/{session_id}`
  - `ETag`: `"v1"`
  - `Content-Type`: `application/json`

  ```json
  {
    "success": true,
    "data": {
      "id": "e7f68b8d-a238-423b-adb0-7f59e5ddcb63",
      "title": "Nghiên cứu: Attention Is All You Need",
      "document_ids": [
        "e3771a46-74cc-4fb7-a238-fd7994cf6303"
      ],
      "active_document_id": "e3771a46-74cc-4fb7-a238-fd7994cf6303",
      "viewport_state": {
        "page": 1,
        "zoom_ratio": 1.0,
        "scroll_top": 0.0
      },
      "active_tab": "chat",
      "is_archived": false,
      "version": 1,
      "documents": [
        {
          "id": "e3771a46-74cc-4fb7-a238-fd7994cf6303",
          "title": "Attention Is All You Need",
          "filename": "1706.03762v7.pdf",
          "status": "completed",
          "file_size_bytes": 2215244,
          "added_at": "2026-09-16T17:58:37.483023Z",
          "display_order": 0
        }
      ],
      "warnings": [],
      "created_at": "2026-09-16T17:58:37.483023Z",
      "updated_at": "2026-09-16T17:58:37.483027Z"
    },
    "meta": {
      "request_id": "req_f4b868e17f6c",
      "timestamp": "2026-09-16T17:58:37.500206Z"
    }
  }
  ```
* **`200 OK` (Khi Idempotent Cache Hit)** - Phản hồi phiên đã tạo trước đó kèm header `X-Cache: Idempotent-Hit`.
* **`400 Bad Request`** - Vượt quá dung lượng 5 bài báo trong một phiên nghiên cứu.  
  ```json
  {
    "success": false,
    "error": {
      "code": "SESSION_CAPACITY_EXCEEDED",
      "message": "Phiên đọc tối đa chỉ chứa 5 bài báo. Vui lòng gỡ bớt bài báo trước khi nạp thêm.",
      "action": "Reduce initial_document_ids to 5 or fewer documents."
    }
  }
  ```
* **`404 Not Found`** - Một hoặc nhiều tài liệu không tồn tại hoặc người dùng không có quyền truy cập.  
  ```json
  {
    "success": false,
    "error": {
      "code": "DOCUMENT_NOT_FOUND",
      "message": "Tài liệu không tồn tại hoặc bạn không có quyền truy cập.",
      "action": "Ensure all document IDs exist and belong to current user."
    }
  }
  ```
* **`422 Unprocessable Entity`** - Tiêu đề không hợp lệ (chuỗi chỉ gồm khoảng trắng hoặc dài hơn 255 ký tự).
---

### [GET] `/api/v1/sessions`
**Summary:** `# 46. Lấy lịch sử các phiên nghiên cứu (Sidebar History)`  
**Operation ID:** `list_sessions_api_v1_sessions_get`

#### Mô tả (Description)
* **Mục đích:** Trả về danh sách các phiên nghiên cứu của người dùng hiện tại phục vụ hiển thị lịch sử trên thanh Sidebar, sắp xếp giảm dần theo thời gian cập nhật gần nhất (`updated_at DESC`).
* **Phân trang chuẩn (Pagination Envelope):** Hỗ trợ `page`, `per_page` kèm theo `PaginationMeta` (total, page, per_page, total_pages) và `PaginationLinks` (first, prev, self, next, last).
* **Lọc phiên lưu trữ (`include_archived`):** Mặc định `false` chỉ trả về các phiên hoạt động (active). Khi `true`, bao gồm cả các phiên đã quá hạn TTL (is_archived = true).
* **Tìm kiếm theo tiêu đề (`q`):** Lọc mờ không phân biệt hoa thường theo từ khóa tiêu đề phiên.

#### Parameters (Query)
| Tên tham số | Kiểu dữ liệu | Mặc định | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `page` | `integer` | `1` | Không | Chỉ số trang (1-indexed, tối thiểu 1). |
| `per_page` | `integer` | `20` | Không | Số lượng phiên trên mỗi trang (1 đến 100). |
| `include_archived` | `boolean` | `false` | Không | Có bao gồm các phiên đã bị lưu trữ quá hạn TTL hay không. |
| `q` | `string` | `null` | Không | Từ khóa tìm kiếm theo tiêu đề phiên nghiên cứu. |

#### Responses
* **`200 OK`** - Danh sách các phiên nghiên cứu phân trang thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "e7f68b8d-a238-423b-adb0-7f59e5ddcb63",
        "title": "Nghiên cứu Transformer & Attention",
        "document_count": 2,
        "message_count": 5,
        "is_archived": false,
        "created_at": "2026-09-16T17:58:37Z",
        "updated_at": "2026-09-16T18:30:00Z"
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

### [GET] `/api/v1/sessions/{id}`
**Summary:** `# 47. Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)`  
**Operation ID:** `get_session_api_v1_sessions__id__get`

#### Mô tả (Description)
* **Mục đích:** Khôi phục trạng thái nguyên vẹn của phiên nghiên cứu khi người dùng quay lại từ Sidebar hoặc reload trình duyệt.
* **Chi tiết trạng thái khôi phục:** Trả về toàn bộ danh sách `document_ids`, tài liệu đang xem `active_document_id`, tọa độ cuộn trang và tỷ lệ thu phóng `viewport_state`, tab đang mở `active_tab`, và số lượng tin nhắn `message_count`.
* **RFC 7232 ETag Header:** Trả về header `ETag: "v{version}"` tương ứng với số phiên bản hiện tại để phục vụ Optimistic Concurrency Control khi client gửi cập nhật.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `string (uuid)` | **Có** | UUID định danh duy nhất của phiên nghiên cứu. |

#### Responses
* **`200 OK`** - Trạng thái nguyên vẹn của phiên nghiên cứu được khôi phục thành công.  
  *Headers:* `ETag: "v3"`  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": {
      "id": "e7f68b8d-a238-423b-adb0-7f59e5ddcb63",
      "title": "Nghiên cứu Transformer & Attention",
      "document_ids": ["e3771a46-74cc-4fb7-a238-fd7994cf6303"],
      "active_document_id": "e3771a46-74cc-4fb7-a238-fd7994cf6303",
      "viewport_state": {
        "page": 3,
        "zoom_ratio": 1.25,
        "scroll_top": 450.0
      },
      "active_tab": "chat",
      "is_archived": false,
      "version": 3,
      "message_count": 12,
      "created_at": "2026-09-16T17:58:37Z",
      "updated_at": "2026-09-16T18:45:00Z"
    },
    "meta": {
      "request_id": "req_8a9b1c2d3e4f",
      "timestamp": "2026-09-16T18:45:01Z"
    }
  }
  ```
* **`404 Not Found`** - Phiên nghiên cứu không tồn tại hoặc người dùng không có quyền truy cập.

---

### [PATCH] `/api/v1/sessions/{id}`
**Summary:** `# 48. Cập nhật tiêu đề / metadata phiên nghiên cứu (OCC If-Match)`  
**Operation ID:** `update_session_metadata_api_v1_sessions__id__patch`

#### Mô tả (Description)
* **Mục đích:** Đổi tên tiêu đề hoặc cập nhật metadata của phiên nghiên cứu với cơ chế kiểm soát đồng thời lạc quan (OCC).
* **Kiểm soát đồng thời (OCC):**
  - Bắt buộc phải có header `If-Match: "v{version}"` (theo RFC 7232 / RFC 9110).
  - Nếu thiếu header `If-Match`: Trả về `428 Precondition Required`.
  - Nếu `If-Match` không khớp với phiên bản trong CSDL: Trả về `412 Precondition Failed` (`CONCURRENCY_CONFLICT`).
  - Khi cập nhật thành công: Tự động tăng `version` lên 1 và trả về header `ETag` mới.

#### Parameters (Path & Header)
| Tên tham số | Vị trí | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `string (uuid)` | **Có** | UUID của phiên nghiên cứu cần cập nhật. |
| `If-Match` | `header` | `string` | **Có** | Chuỗi ETag phiên bản hiện tại (ví dụ: `"v1"` hoặc `"v3"`). |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `title` | `string` | **Có** | `min_length=1, max_length=255` | Tiêu đề mới của phiên nghiên cứu (không được chỉ chứa khoảng trắng). |

#### Responses
* **`200 OK`** - Cập nhật tiêu đề thành công. Header `ETag` mang số phiên bản mới.  
  *Headers:* `ETag: "v4"`  
  *Content-Type:* `application/json`
* **`412 Precondition Failed`** - Xung đột phiên bản đồng thời do trạng thái đã bị thay đổi bởi request khác (`CONCURRENCY_CONFLICT`).
* **`428 Precondition Required`** - Yêu cầu thiếu header bắt buộc `If-Match`.
* **`404 Not Found`** - Phiên không tồn tại hoặc không thuộc người dùng.

---

### [PATCH] `/api/v1/sessions/{id}/viewport`
**Summary:** `# 49. Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)`  
**Operation ID:** `update_session_viewport_api_v1_sessions__id__viewport_patch`

#### Mô tả (Description)
* **Mục đích:** Tự động lưu trữ vị trí đọc của người dùng (số trang `page`, tỷ lệ phóng to/thu nhỏ `zoom_ratio`, tọa độ cuộn `scroll_top`), tab đang thao tác `active_tab` và tài liệu đang chọn `active_document_id`.
* **Kiểm soát đồng thời (OCC):** Sử dụng header `If-Match: "v{version}"` đảm bảo không ghi đè mất mát dữ liệu điều hướng của người dùng khi chuyển đổi thiết bị.

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `viewport_state` | `object` | **Có** | - | Trạng thái hiển thị canvas: `page` (int >= 1), `zoom_ratio` (float 0.25 - 5.0), `scroll_top` (float >= 0). |
| `active_tab` | `string` | Không | `null` | Tab đang chọn: `chat`, `notes`, `highlights`, `mindmap`. |
| `active_document_id` | `string (uuid)` | Không | `null` | UUID tài liệu đang hiển thị trên canvas (phải thuộc danh sách tài liệu của phiên). |

#### Responses
* **`200 OK`** - Cập nhật trạng thái viewport thành công kèm ETag mới.
* **`412 Precondition Failed`** - Xung đột phiên bản đồng thời.
* **`422 Unprocessable Entity`** - `active_document_id` không thuộc tài liệu của phiên hoặc tham số viewport không hợp lệ.

---

### [DELETE] `/api/v1/sessions/{id}`
**Summary:** `# 50. Xóa phiên nghiên cứu`  
**Operation ID:** `delete_session_api_v1_sessions__id__delete`

#### Mô tả (Description)
* **Mục đích:** Xóa hoàn toàn một phiên nghiên cứu và xóa xếp chồng (cascade) các liên kết bài báo và lượt hội thoại trong phiên đó.
* **Bảo vệ tài liệu gốc:** Việc xóa phiên nghiên cứu **không** xóa tài liệu gốc trong kho thư viện chung của người dùng.

#### Responses
* **`204 No Content`** - Xóa phiên nghiên cứu thành công (không có body trả về).
* **`404 Not Found`** - Phiên không tồn tại hoặc không thuộc người dùng.

---

### [POST] `/api/v1/sessions/{id}/documents`
**Summary:** `# 51. Nạp bài vào phiên (Pure JSON: url hoặc document_id)`  
**Operation ID:** `add_document_to_session_api_v1_sessions__id__documents_post`

#### Mô tả (Description)
* **Mục đích:** Nạp thêm bài báo vào phiên nghiên cứu đang hoạt động bằng định dạng Pure JSON (không dùng multipart form).
* **Hai nguồn nạp (`source_type`):**
  - `document_id`: Nạp tài liệu có sẵn trong thư viện của người dùng vào phiên (trả về trạng thái `associated`).
  - `url`: Nhận URL bài báo khoa học (arXiv, PubMed, DOI...), hệ thống đưa vào hàng đợi nạp nền (trả về trạng thái `queued`).
* **Ràng buộc dung lượng trần 5 bài:** Nếu phiên đã chứa 5 bài báo, hệ thống từ chối nạp thêm và trả về `422 Unprocessable Content` (`SESSION_CAPACITY_EXCEEDED`).
* **Chống trùng lặp:** Nếu bài báo đã có trong phiên, trả về `409 Conflict` (`DOCUMENT_ALREADY_IN_SESSION`).

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `source_type` | `string` | **Có** | Nguồn bài báo: `"document_id"` hoặc `"url"`. |
| `document_id` | `string (uuid)` | Không | Bắt buộc khi `source_type == "document_id"`. |
| `url` | `string` | Không | Bắt buộc khi `source_type == "url"` (URL định dạng hợp lệ). |
| `title` | `string` | Không | Tiêu đề gợi nhớ tùy chọn khi nạp bài từ URL. |

#### Responses
* **`202 Accepted`** - Bài báo đã được liên kết hoặc đưa vào hàng đợi xử lý nền thành công.  
  ```json
  {
    "success": true,
    "data": {
      "session_id": "e7f68b8d-a238-423b-adb0-7f59e5ddcb63",
      "document_id": "e3771a46-74cc-4fb7-a238-fd7994cf6303",
      "status": "associated",
      "display_order": 1,
      "message": "Bài báo đã được thêm vào phiên nghiên cứu thành công."
    },
    "meta": {
      "request_id": "req_1a2b3c4d5e6f",
      "timestamp": "2026-09-16T19:00:00Z"
    }
  }
  ```
* **`409 Conflict`** - Bài báo đã tồn tại trong phiên (`DOCUMENT_ALREADY_IN_SESSION`).
* **`422 Unprocessable Content`** - Đã đạt giới hạn tối đa 5 bài báo trong một phiên.

---

### [POST] `/api/v1/sessions/{id}/messages`
**Summary:** `# 52. Gửi câu hỏi & Stream SSE (Cross-Document Namespacing & Resumption)`  
**Operation ID:** `post_session_message_api_v1_sessions__id__messages_post`

#### Mô tả (Description)
* **Mục đích:** Gửi câu hỏi nghiên cứu đa bài báo và nhận luồng dữ liệu trả lời trực tiếp thời gian thực theo định dạng Server-Sent Events (`text/event-stream`).
* **Cross-Document Namespacing:** Trích xuất ngữ cảnh kết hợp từ nhiều bài báo trong phiên, tiền tố hóa rõ ràng nguồn tài liệu `[Doc 1: {title}]`, `[Doc 2: {title}]`.
* **Trích dẫn trực quan (Grounded Visual Citations):** Trả về sự kiện `citations` chứa danh sách trích dẫn chính xác kèm tọa độ bounding boxes `[ymin, xmin, ymax, xmax, page]` để frontend vẽ vùng highlight tương ứng trên PDF canvas.
* **Stream Resumption (RFC 8895 & W3C EventSource):** Từng sự kiện SSE được định danh tuần tự bằng trường `id: <seq_id>`. Hỗ trợ header `Last-Event-ID` từ client để nối lại luồng stream mượt mà khi mạng bị ngắt quãng giữa chừng.
* **Suy luận minh bạch (Reasoning Tokens Transparency):** Hỗ trợ sự kiện `event: reasoning` (CoT / Thinking Stream) truyền tải quá trình lập luận phản biện học thuật trước khi xuất tokens câu trả lời, cho phép UI hiển thị collapsible thought box.
* **Phản hồi tương tác có cấu trúc (Structured Interactive Callback):** Hỗ trợ trường `interactive_response` trong Request Body (`{"persona_id": "persona_b", "quiz_answers": {...}}`), cho phép người dùng click 1 chạm trên UI thay vì gửi văn bản thô.
* **Client Disconnect Guard:** Tự động lắng nghe `request.is_disconnected()` khi client hủy kết nối hoặc đóng tab để dừng ngay vòng lặp sinh token, tiết kiệm tài nguyên GPU/LLM.
* **Các loại sự kiện SSE chuẩn:**
  - `id: 1` -> `event: start` - Bắt đầu sinh câu trả lời, trả về `turn_id` và `message_id`.
  - `id: 2` -> `event: reasoning` - (Tùy chọn) Luồng suy luận logic CoT phản biện học thuật.
  - `id: 3` -> `event: interactive_options` - (Tùy chọn) Phát sinh khi hệ thống phát hiện ý định mơ hồ hoặc cần chẩn đoán lộ trình học (AT-CoT Intent Elicitation). Trả về JSON chứa Personas (`Nhóm A/B/C`) và Micro-Quiz để Frontend render thẻ 1-click.
  - `id: 4` -> `event: citations` - Danh sách các trích dẫn và bounding box định vị trang `[ymin, xmin, ymax, xmax, page]`.
  - `id: 5...N` -> `event: token` - Các token từ vựng được stream từng phần `{"token": "..."}`.
  - `id: N+1` -> `event: done` - Hoàn tất sinh câu trả lời kèm số liệu thống kê `finish_reason`, `latency_ms`, `intent`, `ambiguity_type`.
  - `event: error` - Báo lỗi chi tiết nếu phiên bị khóa hoặc lỗi pipeline.

#### Request Headers
| Tên Header | Kiểu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `Last-Event-ID` | `string` | Không | ID sự kiện cuối cùng client đã nhận được, phục vụ cơ chế tự động nối lại luồng stream (RFC 8895). |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `question` | `string` | **Có** | - | Câu hỏi của nhà nghiên cứu (1 đến 2000 ký tự). |
| `stream` | `boolean` | Không | `true` | Yêu cầu stream dữ liệu SSE thời gian thực. |
| `scope` | `string` | Không | `multi_paper` | Phạm vi truy vấn: `multi_paper` (toàn phiên) hoặc `active_paper` (chỉ bài đang chọn). |
| `interactive_response` | `object` | Không | `null` | Dữ liệu phản hồi tùy chọn khi người dùng tương tác với thẻ chẩn đoán (`persona_id`, `quiz_answers`). |

#### Responses
* **`200 OK`** - Luồng SSE phản hồi câu hỏi trực tiếp.  
  *Content-Type:* `text/event-stream`  
  *Headers:* `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`

  ```http
  id: 1
  event: start
  data: {"turn_id": "11111111-2222-3333-4444-555555555555", "message_id": "msg_11111111", "created_at": "2026-09-17T12:00:00Z"}

  id: 2
  event: reasoning
  data: {"thought": "Xác định câu hỏi liên quan đến kiến trúc Multi-Head Attention tại Phần 3.2. Truy xuất tài liệu..."}

  id: 3
  event: citations
  data: {"citations": [{"citation_id": "cit_1", "document_id": "e3771a46-74cc-4fb7-a238-fd7994cf6303", "document_title": "Attention Is All You Need", "page_number": 3, "bounding_boxes": [[0.12, 0.35, 0.49, 0.91, 3]], "score": 0.88}]}

  id: 4
  event: token
  data: {"token": "Kiến "}

  id: 5
  event: token
  data: {"token": "trúc "}

  id: 6
  event: token
  data: {"token": "Transformer..."}

  id: 7
  event: done
  data: {"finish_reason": "stop", "prompt_tokens": 820, "completion_tokens": 145, "total_tokens": 965, "latency_ms": 320.0, "intent": "fact_extraction"}
  ```
* **`403 Forbidden`** - Phiên nghiên cứu đã bị lưu trữ quá hạn TTL (`SESSION_ARCHIVED`).
* **`404 Not Found`** - Phiên nghiên cứu không tồn tại.

---

### [GET] `/api/v1/sessions/{id}/messages`
**Summary:** `# 53. Lấy lịch sử hội thoại của phiên (phân trang)`  
**Operation ID:** `get_session_messages_api_v1_sessions__id__messages_get`

#### Mô tả (Description)
* **Mục đích:** Lấy toàn bộ lịch sử các lượt hỏi đáp trong phiên theo trình tự thời gian tăng dần (`created_at ASC`), bao gồm câu hỏi, câu trả lời, trích dẫn bounding boxes và thông số hiệu năng latency/token usage.

#### Parameters (Path & Query)
| Tên tham số | Vị trí | Kiểu dữ liệu | Mặc định | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `string (uuid)` | - | **Có** | UUID của phiên nghiên cứu. |
| `page` | `query` | `integer` | `1` | Không | Trang số (tối thiểu 1). |
| `per_page` | `query` | `integer` | `50` | Không | Số lượt hội thoại trên mỗi trang (1 đến 100). |

#### Responses
* **`200 OK`** - Danh sách các lượt hội thoại phân trang thành công.  
  *Content-Type:* `application/json`
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "11111111-2222-3333-4444-555555555555",
        "session_id": "e7f68b8d-a238-423b-adb0-7f59e5ddcb63",
        "question": "Kiến trúc Transformer hoạt động như thế nào?",
        "answer": "Kiến trúc Transformer dựa hoàn toàn trên cơ chế Attention...",
        "citations": [
          {
            "citation_number": 1,
            "document_id": "e3771a46-74cc-4fb7-a238-fd7994cf6303",
            "document_title": "Attention Is All You Need",
            "page_number": 3,
            "bounding_box": [0.12, 0.35, 0.49, 0.91, 3],
            "snippet": "Multi-head attention allows the model to jointly attend..."
          }
        ],
        "prompt_tokens": 820,
        "completion_tokens": 145,
        "latency_ms": 620,
        "finish_reason": "stop",
        "created_at": "2026-09-16T19:10:00Z"
      }
    ],
    "meta": {
      "total": 1,
      "page": 1,
      "per_page": 50,
      "total_pages": 1
    },
    "links": {
      "first": "/api/v1/sessions/e7f68b8d-a238-423b-adb0-7f59e5ddcb63/messages?page=1&per_page=50",
      "prev": null,
      "self": "/api/v1/sessions/e7f68b8d-a238-423b-adb0-7f59e5ddcb63/messages?page=1&per_page=50",
      "next": null,
      "last": "/api/v1/sessions/e7f68b8d-a238-423b-adb0-7f59e5ddcb63/messages?page=1&per_page=50"
    }
  }
  ```

---

### [DELETE] `/api/v1/sessions/{id}/messages`
**Summary:** `# 54. Xóa lịch sử hội thoại của phiên (Idempotent 204)`  
**Operation ID:** `delete_session_messages_api_v1_sessions__id__messages_delete`

#### Mô tả (Description)
* **Mục đích:** Xóa toàn bộ các lượt hỏi đáp trong phiên nghiên cứu để bắt đầu lại ngữ cảnh sạch, bảo đảm tính Idempotent (gọi nhiều lần vẫn trả về `204 No Content`).
* **Bảo tồn tài liệu và viewport:** Các tài liệu đã nạp trong phiên và vị trí cuộn trang không bị ảnh hưởng.

#### Responses
* **`204 No Content`** - Đã xóa sạch lịch sử hội thoại của phiên.
* **`404 Not Found`** - Phiên không tồn tại hoặc không thuộc người dùng.

---

### [POST] `/api/v1/sessions/{id}:restore-archived`
**Summary:** `# 55. Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL`  
**Operation ID:** `restore_archived_session_api_v1_sessions__id__restore_archived_post`

#### Mô tả (Description)
* **Mục đích:** Kích hoạt lại một phiên nghiên cứu đã bị lưu trữ tự động do quá hạn TTL (7 ngày không hoạt động).
* **Quy trình tái kích hoạt:**
  1. Người dùng tải lại tệp PDF gốc lên endpoint.
  2. Hệ thống kiểm tra tính hợp lệ của tệp PDF (Magic bytes `%PDF-`).
  3. Khôi phục cờ `is_archived = False`, xóa `archived_at`, tăng số phiên bản `version` lên 1.
  4. Trả về chi tiết phiên đã được kích hoạt lại cùng header `ETag`.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `string (uuid)` | **Có** | UUID của phiên nghiên cứu đã bị lưu trữ cần kích hoạt lại. |

#### Request Body (`multipart/form-data`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `file` | `binary (file)` | **Có** | Tệp PDF gốc hợp lệ (application/pdf) dùng để kích hoạt lại phiên. |

#### Responses
* **`200 OK`** - Phiên nghiên cứu đã được kích hoạt lại thành công (`is_archived: false`).  
  *Headers:* `ETag: "v5"`  
  *Content-Type:* `application/json`
* **`400 Bad Request`** - Tệp tải lên không phải là PDF hợp lệ (`INVALID_PDF_HEADER`).
* **`404 Not Found`** - Phiên không tồn tại hoặc không thuộc người dùng.

---

## 4. Sổ Tay Nghiên Cứu & AI Tổng Hợp (Smart Notebook & Knowledge Digest)

### [POST] `/api/v1/notes`
**Summary:** `# 16. Lưu trích dẫn & ghi chú cá nhân (Add to Note)`  
**Operation ID:** `create_note_api_v1_notes_post`

#### Mô tả (Description)
* **Mục đích:** Lưu trữ đoạn trích dẫn được bôi đen trực tiếp từ văn bản học thuật kèm toạ độ không gian (bounding boxes) và ghi chú phân tích của nhà nghiên cứu. Nếu không truyền `document_id`, ghi chú được lưu dạng ý tưởng tự do (Free Note).
* **Frozen Evidence Snapshot:** Nếu đính kèm `document_id`, hệ thống tự động trích xuất và sao chụp bất biến toàn bộ metadata tài liệu nguồn (tiêu đề, tác giả, năm xuất bản, DOI, arXiv ID, thông tin chunk) vào trường `frozen_snapshot`. Khi tài liệu nguồn bị xóa hoặc ngắt kết nối (`is_source_detached = true`), giá trị học thuật của ghi chú vẫn được bảo toàn nguyên vẹn.
* **Headers phản hồi:**
  - `Location: /api/v1/notes/{id}`
  - `ETag: "v1"`

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `selected_text` | `string` | **Có** | - | Đoạn trích dẫn hoặc nội dung ghi chú (1 - 10,000 ký tự). |
| `document_id` | `string (uuid)` | Không | `null` | UUID tài liệu nguồn đính kèm (nếu có). |
| `chunk_id` | `string (uuid)` | Không | `null` | UUID của chunk tương ứng trong tài liệu. |
| `bounding_boxes` | `array[array[float]]` | Không | `[]` | Tọa độ chuẩn hóa `[x0, y0, x1, y1, page]` phục vụ highlight trực tiếp trên PDF. |
| `page_number` | `integer` | Không | `1` | Số trang chứa trích dẫn (>= 1). |
| `user_note` | `string` | Không | `null` | Nhận xét, phân tích chuyên môn của người nghiên cứu. |
| `tags` | `array[string]` | Không | `[]` | Danh sách nhãn dán phân loại (tự động loại bỏ trùng lặp và chuẩn hóa viết thường). |
| `folder_id` | `string (uuid)` | Không | `null` | Thư mục lưu trữ sổ tay cá nhân. |

#### Responses
* **`201 Created`** - Tạo ghi chú nghiên cứu thành công.
* **`404 Not Found`** - Tài liệu nguồn `document_id` không tồn tại (`DOCUMENT_NOT_FOUND`).
* **`422 Unprocessable Entity`** - Dữ liệu trích dẫn rỗng hoặc không hợp lệ.

---

### [GET] `/api/v1/notes`
**Summary:** `# 17. Danh sách ghi chú (lọc theo document_id, tag, folder_id)`  
**Operation ID:** `list_notes_api_v1_notes_get`

#### Mô tả (Description)
* **Mục đích:** Truy vấn danh sách các ghi chú cá nhân với phân trang chuẩn RFC 8288. Hỗ trợ lọc theo tài liệu nguồn, thư mục, hoặc tìm kiếm nhãn dán thông qua chỉ mục PostgreSQL GIN.

#### Parameters (Query)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `document_id` | `string (uuid)` | Không | `null` | Lọc theo tài liệu nguồn cụ thể. |
| `tag` | `string` | Không | `null` | Lọc theo nhãn dán (hỗ trợ GIN containment search). |
| `folder_id` | `string (uuid)` | Không | `null` | Lọc theo thư mục sổ tay. |
| `page` | `integer` | Không | `1` | Số thứ tự trang (>= 1). |
| `per_page` | `integer` | Không | `20` | Số lượng ghi chú mỗi trang (1 - 100). |

#### Responses
* **`200 OK`** - Danh sách ghi chú kèm siêu dữ liệu phân trang `meta` và điều hướng `links`.

---

### [GET] `/api/v1/notes/{id}`
**Summary:** `# 18. Chi tiết ghi chú kèm Frozen Evidence Snapshot`  
**Operation ID:** `get_note_detail_api_v1_notes__id__get`

#### Mô tả (Description)
* **Mục đích:** Khôi phục chi tiết một ghi chú, bao gồm toạ độ highlight không gian và ảnh chụp dẫn chứng bất biến `frozen_snapshot`.
* **Headers:** Cung cấp `ETag: "v{version}"` phục vụ kiểm soát đồng thời lạc quan.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `string (uuid)` | **Có** | UUID của ghi chú nghiên cứu cần truy vấn. |

#### Responses
* **`200 OK`** - Chi tiết ghi chú nghiên cứu.
* **`404 Not Found`** - Không tìm thấy ghi chú hoặc không có quyền truy cập (`NOTE_NOT_FOUND`).

---

### [PATCH] `/api/v1/notes/{id}`
**Summary:** `# 19. Sửa ghi chú / tag (Kiểm soát đồng thời OCC If-Match)`  
**Operation ID:** `update_note_api_v1_notes__id__patch`

#### Mô tả (Description)
* **Mục đích:** Chỉnh sửa nhận xét cá nhân hoặc gắn lại nhãn dán.
* **Giao thức OCC (RFC 7232):**
  - Bắt buộc phải có header `If-Match: "v{version}"`.
  - Nếu thiếu header: phản hồi `428 Precondition Required`.
  - Nếu `version` trong cơ sở dữ liệu không khớp: phản hồi `412 Precondition Failed`.
  - Nếu thành công: tự động tăng `version` lên 1 và trả về `ETag: "v{version+1}"`.

#### Headers (Request)
| Tên Header | Kiểu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `If-Match` | `string` | **Có** | ETag phiên bản hiện tại, ví dụ `"v1"`. |

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `string (uuid)` | **Có** | UUID của ghi chú cần chỉnh sửa. |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `user_note` | `string` | Không | Nhận xét phân tích mới. |
| `tags` | `array[string]` | Không | Danh sách nhãn dán mới (thay thế danh sách cũ). |
| `folder_id` | `string (uuid)` | Không | Chuyển ghi chú sang thư mục mới. |

#### Responses
* **`200 OK`** - Cập nhật ghi chú thành công. Trả về `ETag: "v{version+1}"`.
* **`412 Precondition Failed`** - Xung đột phiên bản dữ liệu (`CONCURRENCY_CONFLICT`).
* **`428 Precondition Required`** - Thiếu header `If-Match` (`PRECONDITION_REQUIRED`).
* **`404 Not Found`** - Không tìm thấy ghi chú.

---

### [DELETE] `/api/v1/notes/{id}`
**Summary:** `# 20. Xóa ghi chú khỏi sổ tay`  
**Operation ID:** `delete_note_api_v1_notes__id__delete`

#### Mô tả (Description)
* **Mục đích:** Xóa một ghi chú khỏi sổ tay nghiên cứu.
* **Lũy đẳng (Idempotency):** Gọi nhiều lần với cùng ID đều phản hồi `204 No Content`.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `string (uuid)` | **Có** | UUID của ghi chú cần xóa. |

#### Responses
* **`204 No Content`** - Xóa thành công (hoặc ghi chú đã được xóa trước đó).

---

### [POST] `/api/v1/notes:synthesize`
**Summary:** `# 21. AI Tổng hợp ghi chú thành bài học (4 modes + Badges)`  
**Operation ID:** `synthesize_notes_api_v1_notes_synthesize_post`

#### Mô tả (Description)
* **Mục đích:** Sử dụng AI để đúc kết và tổng hợp tri thức từ tập hợp các trích dẫn trong sổ tay nghiên cứu thành văn bản hoàn chỉnh.
* **4 Chế độ Tổng hợp (Synthesis Modes):**
  1. `concept_lesson`: Bài học khái niệm sư phạm có giải thích logic từng bước.
  2. `literature_review`: Điểm luận văn hiến tổng quan học thuật, đối chiếu và trích dẫn đa chiều.
  3. `research_gap`: Xác định lỗ hổng nghiên cứu và định hướng các hướng đi tiếp theo.
  4. `active_recall_quiz`: Đúc kết tri thức dạng bài tự kiểm tra thấu hiểu (3 - 5 câu hỏi/Flashcards kèm đáp án ẩn).
* **Hệ thống Interactive Citation Badges:** Tự động neo các ký hiệu dẫn chứng `[^badge_1]`, `[^badge_2]` trong nội dung markdown trỏ trực tiếp đến `note_id`, `document_id`, số trang và bounding box.
* **Cơ chế Lũy đẳng (Idempotency):** Hỗ trợ header `Idempotency-Key`. Khi nhận cùng khóa, hệ thống trả lại kết quả lưu trong cache kèm header `X-Cache: Idempotent-Hit`.

#### Headers (Request)
| Tên Header | Kiểu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `Idempotency-Key` | `string` | Không | Chuỗi định danh thao tác chống trùng lặp. |

#### Request Body (`application/json`)
| Tên trường | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `note_ids` | `array[string (uuid)]` | **Có** | - | Danh sách UUID của các ghi chú cần tổng hợp (tối thiểu 1, tối đa 50 ghi chú). |
| `mode` | `string` | Không | `concept_lesson` | Chế độ tổng hợp: `concept_lesson`, `literature_review`, `research_gap`, `active_recall_quiz`. |
| `language` | `string` | Không | `vi` | Ngôn ngữ bài học đầu ra (`vi`, `en`). |
| `target_title` | `string` | Không | `null` | Tiêu đề tùy chỉnh cho bài học tổng hợp. |

#### Responses
* **`200 OK`** - Tổng hợp tri thức thành công.  
  *Headers:* `X-Cache: Idempotent-Hit` (nếu trùng khóa lũy đẳng).
* **`404 Not Found`** - Một hoặc nhiều ghi chú không tồn tại hoặc không thuộc quyền sở hữu (`NOTE_NOT_FOUND`).
* **`422 Unprocessable Entity`** - Danh sách `note_ids` rỗng hoặc chế độ `mode` không hợp lệ.

---

### [POST] `/api/v1/sessions/{id}:export-bundle`
**Summary:** `# 56. Xuất Gói Nghiên Cứu Ngoại Tuyến Trọn Gói (Full Offline Research Bundle .zip)`  
**Operation ID:** `export_session_bundle_api_v1_sessions__id__export_bundle_post`

#### Mô tả (Description)
* **Mục đích:** Đóng gói toàn bộ tài nguyên của một phiên nghiên cứu vào một tệp nén ZIP duy nhất để phục vụ nghiên cứu ngoại tuyến (Offline Research) khi không có Internet.
* **Thành phần tệp ZIP (`application/zip`):**
  1. `documents/`: Toàn bộ các tệp PDF gốc trong phiên đã được nhúng sẵn Native PDF Annotations (chuẩn ISO 32000-1) tại các vị trí đã highlight.
  2. `master_lesson.md`: Bài học tổng hợp tri thức chuẩn Markdown tích hợp YAML frontmatter và các interactive badges.
  3. `chat_transcript.html`: Bản ghi lịch sử hỏi đáp độc lập tự chứa CSS/JS (self-contained viewer) cho phép tra cứu câu hỏi và đối chiếu trích dẫn ngoại tuyến.

#### Parameters (Path)
| Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :

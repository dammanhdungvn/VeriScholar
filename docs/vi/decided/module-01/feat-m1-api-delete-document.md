# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Xóa Bài Báo Theo Đồ Thị Phụ Thuộc (Zero-Retention Delete)

* **Tên Branch:** `feat/m1-api-delete-document`
* **API Endpoint:** `DELETE /api/v1/documents/{id}`
* **Mã Phản Hồi:** `204 No Content`
* **Loại Endpoint:** Standard REST Entity Deletion Endpoint (Resource Lifecycle)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.7: API Xóa bài báo theo đồ thị phụ thuộc)
  - [`docs/vi/design-database.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-database.md) (Ràng buộc `ON DELETE CASCADE` trên bảng `chunks`, `embeddings`, `session_documents`)
  - [`docs/vi/design-architecture.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-architecture.md) (Mục 5: Cam kết Zero-Retention Guarantee & Thu hồi lưu trữ CAS)
  - [`AGENTS.md`](file:///home/VeriScholar/Workspace/VeriScholar/AGENTS.md) (Quy tắc Zero-Retention và quản trị rò rỉ dữ liệu)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Cam kết cốt lõi của nền tảng VeriScholar là **Zero-Retention Guarantee** (Bảo đảm không lưu trữ dữ liệu trái phép). Khi nhà nghiên cứu yêu cầu xóa một bài báo, hệ thống phải đảm bảo toàn bộ dữ liệu phái sinh phát sinh từ bài báo đó (các đoạn văn bản bóc tách `chunks`, các vector nhúng ngữ nghĩa `embeddings`, các liên kết phiên làm việc `session_documents`) phải bị tiêu hủy vĩnh viễn và không thể khôi phục. Đồng thời, tệp PDF vật lý lưu trong hệ thống Content-Addressable Storage (CAS) chỉ được xóa khi không còn bất kỳ người dùng nào khác tham chiếu đến.

### 1.2 Quyết định kiến trúc (Decisions)
1. **Lan Truyền Xóa Bậc Thang Tự Động (Database ON DELETE CASCADE):**
   - Thay vì thực hiện nhiều câu lệnh xóa thủ công dễ gây sót dữ liệu hoặc lỗi khóa ngoại (foreign key violation), hệ thống dựa trên cơ chế `ON DELETE CASCADE` đã được thiết kế sẵn tại tầng cơ sở dữ liệu PostgreSQL.
   - Khi bản ghi `documents` bị xóa, PostgreSQL tự động dọn sạch mọi bản ghi liên quan trong `chunks`, `embeddings`, `session_documents`.
2. **Thu Hồi Tài Nguyên Lưu Trữ CAS Nguyên Tử (Atomic CAS Garbage Collection):**
   - Xác định `blob_id` của tài liệu trước khi xóa.
   - Khóa bản ghi lưu trữ vật lý bằng `SELECT ... FOR UPDATE` trên bảng `document_storage_blobs`.
   - Giảm tham chiếu: `ref_count = ref_count - 1`.
   - **Nếu `ref_count <= 0`:** Xóa bản ghi `document_storage_blobs` và đồng thời gọi `IStoragePort.delete_file()` để xóa tệp PDF vật lý trên đĩa.
   - **Nếu `ref_count > 0`:** Giữ nguyên tệp vật lý trên đĩa để phục vụ người dùng khác đang chia sẻ cùng nội dung tệp.
3. **Tính Lũy Thừa & Phản Hồi Chuẩn RESTful:**
   - Khi xóa thành công lần đầu: Trả về mã `204 No Content` với body rỗng.
   - Khi gọi lại lần thứ hai (tài liệu đã bị xóa): Trả về mã `404 DOCUMENT_NOT_FOUND`.
4. **Cô Lập Đa Người Dùng Tuyệt Đối:**
   - Người dùng chỉ được xóa tài liệu của chính mình (`user_id == current_user.id`). Cố tình xóa tài liệu của người khác sẽ nhận mã `404 DOCUMENT_NOT_FOUND`.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-delete-document`.

### Bước 2: Bổ Sung Phương Thức Xóa Tệp Trong Storage Port & Adapter
1. Trong `packages/core/src/core/ports/storage.py`:
   - Bổ sung `async def delete_file(self, storage_path: str) -> bool`.
2. Trong `packages/core/src/core/adapters/storage/local.py`:
   - Triển khai xóa tệp an toàn; nếu tệp vật lý đã bị mất hoặc không tồn tại, trả về `False` một cách an toàn mà không ném lỗi làm hỏng tiến trình database.

### Bước 3: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `delete_document(document_id: UUID, user_id: UUID, db: AsyncSession, storage_port: IStoragePort) -> None`:
   - Truy vấn `DocumentModel` theo `id == document_id AND user_id == user_id`.
   - Nếu không tìm thấy: Raise `HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND", ...})`.
   - Lấy thông tin `blob_id` và `content_hash`.
   - Xóa bản ghi `DocumentModel` khỏi database: `await db.delete(doc)`.
   - Xử lý CAS Blob:
     - Nếu có `blob_id`: Khóa bản ghi `DocumentStorageBlobModel` bằng `with_for_update()`.
     - Giảm `ref_count -= 1`.
     - Nếu `ref_count <= 0`:
       - `await db.delete(blob)`
       - Xóa tệp vật lý: `await storage_port.delete_file(blob.storage_path)`.
   - Commit toàn bộ giao dịch.

### Bước 4: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)`
2. Tham số: `document_id: UUID = Path(...)`
3. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Xóa vĩnh viễn bài báo khoa học và toàn bộ dữ liệu phụ thuộc (Zero-Retention Guarantee).
   - **Đầu vào:** `document_id: UUID` (Path parameter).
   - **Đầu ra:** HTTP `204 No Content` (Empty body).
   - **Lưu ý:** Tự động lan truyền xóa chunks, vector embeddings qua ON DELETE CASCADE; giảm `ref_count` CAS; chỉ xóa tệp vật lý khi `ref_count == 0`.

### Bước 5: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_delete.py`.
   - Các ca kiểm thử bao phủ:
     - Xóa tài liệu thành công khi chỉ có 1 chủ sở hữu: Tệp vật lý bị xóa, bản ghi blob bị xóa, trả về `204 No Content`.
     - Xóa tài liệu thành công khi có nhiều chủ sở hữu chia sẻ blob: `ref_count` giảm từ 2 xuống 1, tệp vật lý trên đĩa vẫn được giữ nguyên.
     - Lũy thừa: Gọi lại lần 2 nhận mã `404 DOCUMENT_NOT_FOUND`.
     - Xử lý khi `document_id` không tồn tại trả về `404 DOCUMENT_NOT_FOUND`.
     - Cô lập multi-tenant: User B không thể xóa tài liệu của User A (nhận mã `404`).
     - Xác thực UUID không hợp lệ nhận mã `422 Unprocessable Entity`.
     - Xử lý khi tệp vật lý bị mất trước đó vẫn hoàn tất xóa logic trong database một cách êm đẹp.
     - Kiểm tra endpoint xuất hiện trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy tích hợp toàn bộ qua `apps/api/tests/run_all_api_tests.py`.

### Bước 6: Quy Trình Hoàn Tất
1. Commit code: `feat(api): implement DELETE /api/v1/documents/{id} zero-retention cascade purge`.
2. Bổ sung mục `[DELETE] /api/v1/documents/{document_id}` vào `docs/vi/swagger.md` (uncommitted) để user review.

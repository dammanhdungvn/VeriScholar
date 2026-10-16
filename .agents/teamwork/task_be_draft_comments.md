# TASK CONTRACT: DRAFT PEER REVIEW COMMENTS & ANNOTATIONS (BACKEND)
**Mã Task:** `TASK-BE-DRAFT-COMMENTS`  
**Đơn vị thực thi:** Senior Backend & AI Specialist (`backend` @ pane `w2:p3`)  
**Người giao nhiệm vụ:** CTO VeriScholar  
**Người thẩm định độc lập:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
**Nhánh:** `feat/vps-module2-remediation`  
**Mục tiêu PRD:** PRD §3.2 (Chia Sẻ Bản Thảo & Phản Biện Nhóm - Quyền Nhận Xét & Phản Biện / Comment Mode)  

---

## 1. MỤC TIÊU & PHẠM VI (OBJECTIVE & SCOPE)

Xây dựng hệ thống bình luận phản biện (Peer Review Comments & Line Annotations) cho bản thảo nghiên cứu (Drafts), hỗ trợ đầy đủ luồng phản biện học thuật cho giảng viên, đồng tác giả và người phản biện độc lập mà không can thiệp sửa đổi trực tiếp nội dung văn bản gốc.

### Phạm vi bao gồm:
1. **Core Domain Entity (`packages/core/src/core/domain/entities/draft.py`):**
   - Định nghĩa entity `DraftComment`:
     - `id: UUID`
     - `draft_id: UUID`
     - `author_id: UUID`
     - `author_name: str`
     - `start_offset: int` (Vị trí ký tự bắt đầu của đoạn được nhận xét)
     - `end_offset: int` (Vị trí ký tự kết thúc)
     - `selected_text: str` (Trích đoạn văn bản được bôi đen nhận xét)
     - `comment_text: str` (Nội dung nhận xét phản biện)
     - `parent_id: UUID | None` (Hỗ trợ luồng trả lời dạng cây / threaded replies)
     - `is_resolved: bool` (Đánh dấu đã tiếp thu/giải quyết)
     - `created_at: datetime`
     - `updated_at: datetime`

2. **Database Models & Tables (`apps/api/src/api/db/models/draft.py`):**
   - Tạo `DraftCommentModel` kế thừa `IdentifiableTimestampedModel`:
     - `draft_id`: ForeignKey `drafts.id` ondelete `CASCADE`
     - `author_id`: ForeignKey `users.id` ondelete `CASCADE`
     - `author_name`: String(255)
     - `start_offset`: Integer
     - `end_offset`: Integer
     - `selected_text`: Text
     - `comment_text`: Text
     - `parent_id`: ForeignKey `draft_comments.id` ondelete `CASCADE`, nullable=True
     - `is_resolved`: Boolean default False
     - Indexes trên `(draft_id, created_at)` và `parent_id`.

3. **Service & RBAC Layer (`apps/api/src/api/services/draft_service.py`):**
   - `create_comment`: Kiểm tra quyền draft. Cho phép `DraftRole.OWNER`, `DraftRole.EDITOR`, và `DraftRole.COMMENTER`. Cấm `DraftRole.VIEWER` (`HTTP 403`).
   - `list_comments`: Trả về danh sách bình luận (kèm danh sách replies lồng nhau hoặc phẳng theo parent_id) cho bất kỳ ai có quyền truy cập bản thảo (`OWNER`, `EDITOR`, `COMMENTER`, `VIEWER`).
   - `update_comment`: Cho phép sửa `comment_text` (chỉ author), hoặc chuyển đổi trạng thái `is_resolved` (`OWNER`, `EDITOR`, `COMMENTER`).
   - `delete_comment`: Xóa bình luận (chỉ author hoặc `OWNER` của bản thảo).

4. **API Endpoints (`apps/api/src/api/v1/endpoints/drafts.py`):**
   - `POST /api/v1/drafts/{id}/comments` -> Tạo comment hoặc reply
   - `GET /api/v1/drafts/{id}/comments` -> Lấy danh sách comments
   - `PATCH /api/v1/drafts/{id}/comments/{comment_id}` -> Cập nhật text hoặc resolve
   - `DELETE /api/v1/drafts/{id}/comments/{comment_id}` -> Xóa comment

5. **Kiểm thử tự động:**
   - Tạo bộ kiểm thử toàn diện tại `apps/api/tests/test_draft_comments.py`.
   - Kiểm tra đầy đủ: CRUD comment, thread replies, phân quyền RBAC (commenter được tạo, viewer bị 403), multi-tenant isolation.
   - Đảm bảo 100% tests PASSED (`uv run pytest`), linter sạch (`ruff check` & `ruff format`).

---

## 2. BẤT BIẾN KỸ THUẬT BẮT BUỘC (INVARIANTS)
1. **Multi-tenant isolation:** Người dùng không có quyền trên draft không thể xem hay tạo comment (404/403).
2. **Commenter RBAC:** `DraftRole.COMMENTER` có thể tạo comment, đọc comment và resolve comment, nhưng tuyệt đối không được sửa đổi `content` bản thảo (HTTP 403 khi gọi `PUT /drafts/{id}`).
3. **Data Integrity:** Xóa draft cha sẽ CASCADE xóa toàn bộ comments liên quan. Xóa comment cha sẽ CASCADE xóa replies.

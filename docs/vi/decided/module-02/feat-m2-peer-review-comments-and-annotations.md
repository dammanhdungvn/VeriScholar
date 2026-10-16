# Đặc Tả Tính Năng: Hệ Thống Bình Luận & Ghi Chú Bản Thảo Ngang Hàng (PRD §3.2)
## Peer Review Comments & Inline Annotation System

**Module:** Module 2 — Academic Writing Assistant & SAFE Fact-Checking  
**Quy chuẩn:** PRD §3.2 (Collaborative Writing & Review)  
**Nhánh Git:** `feat/m2-draft-comments-annotation` (Commit `f2555f5`)

---

## 1. MỤC TIÊU NGHIỆP VỤ

Trong quá trình chuẩn bị bài báo khoa học, các tác giả (Authors) và người phản biện (Reviewers/Collaborators) cần trao đổi, thảo luận trực tiếp trên từng đoạn văn bản cụ thể của bản thảo mà không làm thay đổi trực tiếp nội dung nguồn.

Hệ thống cung cấp:
1. **Ghi chú neo theo dòng/offset (Inline Line/Offset Annotations):** Neo bình luận vào vị trí ký tự chính xác `[start_offset, end_offset]` và đoạn văn bản được chọn `selected_text`.
2. **Luồng phản hồi phân cấp (Threaded Nested Replies):** Hỗ trợ trả lời (reply) theo cấu trúc cây thông qua `parent_id`.
3. **Giải quyết bình luận (Resolve/Unresolve Toggle):** Cho phép đánh dấu hoàn tất trao đổi.
4. **Phân quyền nghiêm ngặt (Strict RBAC):**
   - `owner`: Toàn quyền quản trị, xóa và chỉnh sửa bản thảo.
   - `editor`: Chỉnh sửa bản thảo, tạo và giải quyết bình luận.
   - `commenter`: Chỉ được phép đọc, tạo bình luận và giải quyết bình luận; **nghiêm cấm tuyệt đối chỉnh sửa văn bản nguồn bản thảo (HTTP 403 `FORBIDDEN_ROLE_RESTRICTED`)**.
   - `viewer`: Chỉ được phép đọc bản thảo và đọc bình luận; **nghiêm cấm tạo hoặc giải quyết bình luận (HTTP 403 `FORBIDDEN_ROLE_RESTRICTED`)**.
5. **Dọn dẹp liên hoàn (Cascade Clean-up):** Khi bản thảo bị xóa (`DELETE /api/v1/drafts/{id}`), toàn bộ các bình luận và phản hồi liên quan tự động được xóa sạch khỏi cơ sở dữ liệu (SQLite/PostgreSQL cascade).

---

## 2. THIẾT KẾ DỮ LIỆU & KIẾN TRÚC

### Entity Domain ([`DraftComment`](file:///home/VeriScholar/Workspace/VeriScholar/packages/core/src/core/domain/entities/draft.py))
```python
class DraftComment(BaseModel):
    id: UUID
    draft_id: UUID
    author_id: UUID
    author_name: str
    start_offset: int | None = None
    end_offset: int | None = None
    selected_text: str | None = None
    comment_text: str
    parent_id: UUID | None = None
    is_resolved: bool = False
    created_at: datetime
    updated_at: datetime
    replies: list["DraftComment"] = Field(default_factory=list)
```

### Database Model ([`DraftCommentModel`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/src/api/db/models/draft.py))
Bảng `draft_comments`:
- `id`: UUID (Primary Key)
- `draft_id`: UUID (Foreign Key `drafts.id` with `ondelete="CASCADE"`, indexed)
- `author_id`: UUID (Foreign Key `users.id`, indexed)
- `author_name`: String(255)
- `start_offset`, `end_offset`: Integer (nullable)
- `selected_text`: Text (nullable)
- `comment_text`: Text (not null)
- `parent_id`: UUID (Foreign Key `draft_comments.id` with `ondelete="CASCADE"`, nullable, indexed)
- `is_resolved`: Boolean (default False, indexed)
- `created_at`, `updated_at`: Timestamp with timezone

---

## 3. DANH SÁCH REST ENDPOINTS

| Phương thức | Đường dẫn API | Mô tả & Ràng buộc RBAC |
|---|---|---|
| `GET` | `/api/v1/drafts/{id}/comments` | Lấy danh sách bình luận (lồng cấu trúc cây replies). Yêu cầu quyền tối thiểu: `viewer`. |
| `POST` | `/api/v1/drafts/{id}/comments` | Tạo bình luận mới hoặc gửi câu trả lời (`parent_id`). Yêu cầu quyền: `owner`, `editor`, `commenter`. Bị chặn 403 đối với `viewer`. |
| `PATCH` | `/api/v1/drafts/{id}/comments/{comment_id}` | Cập nhật nội dung hoặc trạng thái giải quyết (`is_resolved`). Yêu cầu quyền: `owner`, `editor`, `commenter`. |
| `DELETE` | `/api/v1/drafts/{id}/comments/{comment_id}` | Xóa bình luận. Tác giả bình luận hoặc `owner`/`editor` có quyền xóa. |

---

## 4. GIAO DIỆN NGƯỜI DÙNG & TÍCH HỢP FRONTEND

Component [`DraftCommentsPane.tsx`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/writing/components/DraftCommentsPane.tsx):
- Nằm trên thanh tiêu đề `WritingHeaderBar.tsx` với nút bật/tắt `[💬 Bình luận (N)]`.
- Hiển thị danh sách card bình luận với avatar tác giả, thời gian, trích đoạn văn bản được chọn.
- Hộp thoại phản hồi phân cấp (Threaded replies).
- Bộ lọc: `Tất cả` | `Đang mở` | `Đã giải quyết`.
- Tự động cuộn và highlight vùng chữ tương ứng trên trình soạn thảo khi nhấp vào bình luận.

---

## 5. BẰNG CHỨNG KIỂM THỬ TỰ ĐỘNG
- **Backend:** [`apps/api/tests/test_draft_comments.py`](file:///home/VeriScholar/Workspace/VeriScholar/apps/api/tests/test_draft_comments.py) — **9/9 tests PASS**:
  - CRUD bình luận & luồng replies phân cấp.
  - Chặn sửa văn bản đối với Commenter (HTTP 403).
  - Chặn tạo bình luận đối với Viewer (HTTP 403).
  - Cách ly đa người dùng (Multi-tenant isolation 404).
  - Xóa bản thảo cascade toàn bộ bình luận.
- **Frontend:** [`apps/web/src/features/writing/components/DraftCommentsPane.test.tsx`](file:///home/VeriScholar/Workspace/VeriScholar/apps/web/src/features/writing/components/DraftCommentsPane.test.tsx) — **7/7 tests PASS**.

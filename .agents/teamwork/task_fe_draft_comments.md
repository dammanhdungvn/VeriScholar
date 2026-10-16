# TASK CONTRACT: DRAFT PEER REVIEW COMMENTS UI (FRONTEND)
**Mã Task:** `TASK-FE-DRAFT-COMMENTS`  
**Đơn vị thực thi:** Senior Frontend Specialist (`frontend` @ pane `w2:p4`)  
**Người giao nhiệm vụ:** CTO VeriScholar  
**Người thẩm định độc lập:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
**Nhánh:** `feat/vps-module2-remediation`  
**Mục tiêu PRD:** PRD §3.2 (Chia Sẻ Bản Thảo & Phản Biện Nhóm - Quyền Nhận Xét & Phản Biện / Comment Mode)  

---

## 1. MỤC TIÊU & PHẠM VI (OBJECTIVE & SCOPE)

Xây dựng giao diện phản biện trực quan (Peer Review Comments & Annotation Panel) trên không gian soạn thảo bản thảo (Writing Workspace), cho phép người dùng bôi đen đoạn văn bản để để lại nhận xét, xem danh sách nhận xét, phản hồi theo luồng (threaded replies) và đánh dấu giải quyết (resolve).

### Phạm vi bao gồm:
1. **API Client & Type Definitions (`apps/web/src/features/writing/`):**
   - Trong `types/index.ts`: Định nghĩa interface `DraftComment`:
     ```typescript
     export interface DraftComment {
       id: string;
       draft_id: string;
       author_id: string;
       author_name: string;
       start_offset: number;
       end_offset: number;
       selected_text: string;
       comment_text: string;
       parent_id?: string | null;
       is_resolved: boolean;
       created_at: string;
       updated_at: string;
       replies?: DraftComment[];
     }
     ```
   - Trong `api/draftsApi.ts`: Bổ sung các phương thức:
     - `getComments(draftId: string): Promise<DraftComment[]>`
     - `createComment(draftId: string, payload: { start_offset: number; end_offset: number; selected_text: string; comment_text: string; parent_id?: string }): Promise<DraftComment>`
     - `updateComment(draftId: string, commentId: string, payload: { comment_text?: string; is_resolved?: boolean }): Promise<DraftComment>`
     - `deleteComment(draftId: string, commentId: string): Promise<void>`

2. **Zustand State Store (`apps/web/src/features/writing/stores/useWritingStore.ts`):**
   - Bổ sung state:
     - `comments: DraftComment[]`
     - `activeCommentId: string | null`
     - `isCommentsPaneOpen: boolean`
   - Actions:
     - `setComments(comments: DraftComment[]): void`
     - `addComment(comment: DraftComment): void`
     - `updateCommentInStore(comment: DraftComment): void`
     - `removeCommentFromStore(commentId: string): void`
     - `setActiveCommentId(id: string | null): void`
     - `setCommentsPaneOpen(open: boolean): void`

3. **Giao diện Bảng Nhận xét (`apps/web/src/features/writing/components/DraftCommentsPane.tsx`):**
   - Tạo component `DraftCommentsPane.tsx`:
     - Thanh tiêu đề kèm bộ lọc: "Chưa giải quyết (Active)" vs "Đã giải quyết (Resolved)".
     - Thẻ bình luận hiển thị: Tên tác giả nhận xét, thời gian, trích đoạn bôi đen `selected_text` (nền vàng nhạt), nội dung nhận xét `comment_text`.
     - Nút "Đánh dấu đã giải quyết" (Resolve) và nút "Xóa" (Delete).
     - Hỗ trợ trả lời (Threaded Reply input) để trao đổi nhiều vòng phản biện.

4. **Tích hợp Tương tác Trình Soạn Thảo (`WritingEditorPane.tsx` & `WritingHeaderBar.tsx`):**
   - Khi người dùng bôi đen văn bản trong `WritingEditorPane`, hiển thị thanh công cụ nổi hoặc nút nhanh `[💬 Nhận xét / Add Comment]`.
   - Nhấp vào nút sẽ mở ô nhập nhận xét và tự động gắn `start_offset`, `end_offset`, `selected_text`.
   - Trong `WritingHeaderBar.tsx`: Thêm nút bật/tắt bảng nhận xét với huy hiệu đếm số nhận xét chưa giải quyết (ví dụ: `💬 2`).

5. **Kiểm thử tự động:**
   - Tạo bộ kiểm thử Vitest tại `apps/web/src/features/writing/components/DraftCommentsPane.test.tsx`.
   - Cập nhật test liên quan trong `WritingWorkspace.test.tsx` và `WritingHeaderBar.test.tsx`.
   - Đảm bảo 100% tests PASSED (`pnpm --prefix apps/web test`), TypeScript không lỗi (`pnpm --prefix apps/web exec tsc -b`), và linter sạch (`oxlint`).

---

## 2. BẤT BIẾN KỸ THUẬT BẮT BUỘC (INVARIANTS)
1. **Non-destructive:** Tuyệt đối không thay đổi mã nguồn bản thảo khi người dùng thêm hoặc sửa bình luận.
2. **Commenter Protection:** Khi người dùng ở vai trò `commenter`, họ vẫn có thể tạo và xem bình luận mượt mà mà không gặp lỗi phân quyền.

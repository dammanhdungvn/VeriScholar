# TASK CONTRACT: REVIEW-DEFECT-01-OCC
## Đánh Giá Độc Lập Bản Vá DEFECT-01 (OCC Local Offset Drift & HTTP 412 Conflict)

> **Contract Version:** 1.0  
> **Task ID:** `REVIEW-DEFECT-01-OCC`  
> **Assignee:** Lead Quality & Security Reviewer (`reviewer` @ pane `w2:p2`)  
> **Author/Owner of Fix:** Senior Frontend Engineer (`frontend` @ pane `w2:p4`)  
> **Repository:** `/home/VeriScholar/Workspace/VeriScholar`  
> **Branch:** `feat/vps-module2-remediation`  
> **Commit Revision:** [`90d03fa`](file:///home/VeriScholar/Workspace/VeriScholar) (Fix commit) to [`484e13d`](file:///home/VeriScholar/Workspace/VeriScholar) (HEAD)

---

### 1. Mục Tiêu & Bối Cảnh
Khắc phục khiếm khuyết **DEFECT-01** (đã được ghi nhận trong `docs/handoff/module2-milestone1-review.md`):
- **Cơ chế lỗi cũ:** Header `If-Match: "v{version}"` chỉ phát hiện xung đột khi server version đã tăng. Nếu người dùng gõ thêm ký tự cục bộ (`isDirty: true`) mà chưa kịp autosave, server version vẫn là v1. Khi bấm Accept đề xuất cũ, server trả HTTP 200 OK nhưng việc thay thế theo offset cũ làm cắt/chèn đè mất nội dung người dùng vừa gõ mới.
- **Bản vá hiện tại:** Commit `90d03fa` bổ sung thuật toán `calculateRebasedRange` trong `diffUtils.ts`, tích hợp vào `handleAcceptSuggestion` trong `WritingWorkspace.tsx`, đồng thời bắt mã lỗi HTTP 412 để hiển thị alert banner cho người dùng thay vì nuốt lỗi.

---

### 2. Phạm Vi Thẩm Định (Scope)
- **Tệp nguồn:**
  - `apps/web/src/features/writing/components/WritingWorkspace.tsx`
  - `apps/web/src/features/writing/lib/diffUtils.ts`
  - `apps/web/src/features/writing/types/index.ts`
- **Tệp kiểm thử:**
  - `apps/web/src/features/writing/components/WritingWorkspace.test.tsx`
  - `apps/web/src/features/writing/lib/diffUtils.test.ts`
- **Ngoài phạm vi:** Tuyệt đối không sửa đổi mã nguồn trong đợt review này; nếu phát hiện lỗi hoặc thiếu sót, ghi rõ vào findings để tác giả sửa.

---

### 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
1. **Toàn vẹn thuật toán rebase:**
   - Người dùng gõ trước range đề xuất $\rightarrow$ offset đề xuất dịch chuyển tương ứng.
   - Người dùng gõ sau range đề xuất $\rightarrow$ offset đề xuất không bị ảnh hưởng.
   - Trùng khớp nội dung `original_text` được kiểm tra để tránh chèn nhầm vị trí.
2. **Xử lý xung đột HTTP 412 (Precondition Failed):**
   - Khi server trả về 412, hiển thị banner thông báo xung đột rõ ràng trên UI.
   - Panel đề xuất **không bị đóng đột ngột** để người dùng không bị mất nội dung đề xuất.
   - Nội dung cục bộ đang soạn thảo không bị xóa hoặc ghi đè mất mát.
3. **Chất lượng kiểm thử:**
   - Chạy lệnh kiểm tra:
     ```bash
     pnpm --prefix apps/web test src/features/writing/components/WritingWorkspace.test.tsx src/features/writing/lib/diffUtils.test.ts
     pnpm --prefix apps/web exec tsc -b
     pnpm --prefix apps/web lint
     ```
   - 100% tests PASS, zero compile errors, zero linter warnings.
4. **Phân tích rủi ro & Edge cases:**
   - Trường hợp người dùng xóa mất một phần hoặc toàn bộ `original_text` trước khi bấm Accept.
   - Xung đột mạng hoặc chuỗi rỗng.

---

### 4. Bàn Giao & Định Dạng Báo Cáo
Viết báo cáo đánh giá độc lập vào tệp:  
📁 `/home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-01-review.md`

Báo cáo phải kết luận rõ ràng một trong hai trạng thái:
- **`VERDICT: PASS`** (Đủ điều kiện đóng DEFECT-01 kèm các ghi chú kiểm chứng).
- **`VERDICT: FAIL`** (Chỉ ra chính xác test case bị lỗi hoặc rủi ro mất dữ liệu chưa xử lý).

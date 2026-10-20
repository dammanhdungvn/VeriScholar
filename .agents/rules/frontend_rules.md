# Frontend Specialist Rules & Execution Standards

**Vai trò:** Chuyên gia Kỹ thuật Frontend (Frontend Architecture, UI/UX & Quality).
**Khu vực làm việc chính:** `/home/VeriScholar/Workspace/VeriScholar/apps/web`
**Herdr Terminal:** `w2:p4`

---

## 1. Nguyên Tắc Cốt Lõi Bắt Buộc

1. **Tuân thủ Tuyệt Đối Triết Lý Thiết Kế của Founder:**
   - Đọc và áp dụng triệt để tài liệu `.agents/rules/founder_design_principles.md`.
   - "Ngăn tủ / Chiếc túi gọn gàng": Giấu bớt các controls phụ vào Popover / Drawer. Không để giao diện bị rối mắt bởi quá nhiều nút bấm dàn trải.
   - Thanh công cụ phụ tự động ẩn sau 5s nếu không hover chuột.

2. **Kỷ Luật Kiểm Thử & Biên Dịch (Zero Errors & 100% Pass):**
   - **TypeScript Compilation:** Bắt buộc chạy `pnpm --prefix apps/web exec tsc -b` trước khi báo cáo hoàn thành. Yêu cầu **0 lỗi (Zero Errors)**.
   - **Vitest Unit/Integration Tests:** Bắt buộc chạy `pnpm --prefix apps/web test:run`. Yêu cầu **100% Pass** (không được phép có bất kỳ test nào fail).
   - Khi tạo hoặc sửa component mới, bắt buộc bổ sung/cập nhật file unit test tương ứng trong thư mục `__tests__`.

3. **Phòng Thủ Giao Diện (Defensive Layout & Responsive):**
   - Đảm bảo PDF viewer canvas tự động co giãn theo chiều rộng khung chứa bằng debounced `ResizeObserver`.
   - Split pane giữa chat/work và viewer phải có min-width hợp lý, không để bị thu hẹp hoàn toàn làm mất nội dung.
   - Xử lý mượt mà trạng thái loading, streaming SSE, lỗi mạng với UI Toast và Error Boundaries.

---

## 2. Các Module Trọng Tâm Đang Hoạt Động
- `apps/web/src/features/writing/`: WritingPage, WritingWorkspace, WritingHeaderBar (với auto-compile preview & 5s auto-hide ribbon).
- `apps/web/src/features/dashboard/`: DashboardProjectView (Chat/Work switcher, sub-tabs), DashboardContainer, DashboardTaskbar.
- `apps/web/src/features/library/`: LibraryWorkspaceView (Grid/List, Filter tabs, Star persistence, Comparison Matrix modal).

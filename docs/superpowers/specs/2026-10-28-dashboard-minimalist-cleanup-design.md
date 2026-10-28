# Thiết Kế Kỹ Thuật: Tinh Giản Giao Diện Dashboard & Trợ Lý Socratic (11 Tinh Chỉnh)

- **Ngày tạo:** 2026-10-28
- **Tác giả:** Antigravity AI
- **Trạng thái:** Chờ phê duyệt (Pending Approval)
- **Mục tiêu:** Thực hiện 11 yêu cầu tinh chỉnh giao diện người dùng theo chuẩn phong cách tối giản hiện đại (alphaXiv / Claude / ChatGPT), loại bỏ hoàn toàn các thành phần dư thừa, làm sạch khối tư duy suy luận và chuẩn hóa trích dẫn tương tác trên PDF.

---

## 1. Bối Cảnh & Yêu Cầu Người Dùng

Dựa trên phản hồi thực tế từ trải nghiệm trình duyệt và 4 ảnh chụp màn hình (`media_...`):
1. **Xóa bỏ Mode View** trên giao diện `/dashboard`.
2. **Xóa bỏ Zen PDF** trên thanh công cụ điều khiển đọc.
3. Trong menu **Tùy chọn** của PDF: Xóa bỏ mode view, xóa bỏ Đọc tập trung Zen PDF, bổ sung 1 tùy chọn mở **Sổ ghi chú**.
4. Trong **Header Assistant**: Xóa bỏ New Chat, bỏ chữ Assistant, bỏ nút Setting, bỏ nút Dark/Light, bỏ nút Zen Chat.
5. **Đổi tên thương hiệu trợ lý**: Chuyển toàn bộ `Socratic Copilot` thành `Socratic Assistant`.
6. **Xử lý trùng lặp bong bóng**: Xóa bỏ thanh dock 3 bong bóng nổi phía trên (bỏ bong bóng sổ ghi chú, thông tin bài báo, assistant phía trên). Giữ lại duy nhất 1 bong bóng Assistant ở góc dưới cùng bên phải và đổi icon sang Sparkles.
7. **Menu Avatar Taskbar**: Chuyển nút chuyển chế độ Dark/Light vào menu popover khi bấm vào avatar, thay thế cho mục "Nâng cấp gói".
8. **Hiệu ứng Taskbar**: Xóa bỏ hiệu ứng viền/nền phát sáng khi tab đang active. Ở chế độ taskbar thu nhỏ, nút `(+)` phải là hình tròn hoàn hảo `rounded-full` 100% với dấu `+` nằm chính giữa.
9. **Lịch sử Chat (Chuẩn Ảnh 2)**: Thiết kế danh sách lịch sử có nhóm `Recents ∨` cho phép click thu gọn / mở rộng; menu `...` gồm: Ghim (Pin), Đánh dấu chưa đọc (Mark as unread), Đổi tên (Rename) và Xóa (Delete) — loại bỏ hoàn toàn "Add to project".
10. **Khung Suy Luận (Chuẩn Claude / ChatGPT - Sửa Ảnh 3)**: Xóa bỏ danh sách in log máy móc lặp lại (`Analyzed Bounding Box #Page X`). Thay bằng luồng suy luận tự nhiên: hiển thị `Thought for Xs >`, tự động thu gọn khi hoàn thành, bấm mở rộng để đọc phân tích logic mượt mà.
11. **Trích Dẫn Ngữ Nghĩa (Sửa Ảnh 4)**: Định dạng tên trích dẫn chuẩn học thuật có khoảng cách (ví dụ: `[ ↪ Selective Attention ]`), không để dính chữ PascalCase; chuẩn hóa ánh xạ số trang và bounding box để click nhảy chính xác 100% vào đoạn nội dung trong PDF.

---

## 2. Các Phương Án Kỹ Thuật Đã Cân Nhắc

- **Phương án 1 (Đã chọn): Tinh chỉnh trực tiếp trên các Component cốt lõi (In-place Refactor & Modular Cleanup)**
  - Tối ưu trực tiếp các file: `DashboardTaskbar.tsx`, `AvatarDropdownPopover.tsx`, `ViewportControls.tsx`, `WorkspaceToolsMenu.tsx`, `DashboardWorkspace.tsx`, `SocraticThinkingBlock.tsx`, `AcademicMarkdownRenderer.tsx`.
  - *Lý do chọn:* Giữ trọn tính toàn vẹn của state máy học (Zustand & React Query), tránh phân mảnh mã nguồn, không làm phình cấu trúc thư mục, kiểm thử nhanh và an toàn tuyệt đối.
- **Phương án 2 (Bị loại): Tách nhỏ thành các Sub-Component mới (Micro-Component Extraction)**
  - *Lý do loại:* Sinh thêm nhiều file trung gian gây phân mảnh code, tốn chi phí đồng bộ state và dễ phát sinh lỗi regression.

---

## 3. Đặc Tả Chi Tiết Từng Module

### Module 1: Thanh Taskbar & Menu Avatar
- **File:** `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
  - *Xóa hiệu ứng phát sáng tab active:* Bỏ class `bg-coral-500/15 border-coral-500/25` trên `navItems.map`, chỉ giữ màu chữ/icon sắc nét tối giản.
  - *Chuẩn hóa nút `(+)`:* Khi `!isExpanded` (thu nhỏ), render dạng `w-10 h-10 rounded-full mx-auto flex items-center justify-center p-0` để đảm bảo tỷ lệ tròn 100% và dấu `+` nằm chính giữa tâm.
  - *Nhóm `Recents ∨`:* Bổ sung state `isRecentsCollapsed` (mặc định `false`). Header "Recents" có icon `ChevronDown` xoay mượt mà khi bấm để toggle danh sách.
  - *Menu `...` trên từng phiên (Ảnh 2):* Khi hover vào phiên, hiển thị nút `...`. Bấm vào sẽ mở menu ngữ cảnh nổi với 4 mục:
    1. 📌 `Pin` (Ghim phiên lên đầu danh sách)
    2. ✉ `Mark as unread` (Đánh dấu chưa đọc - hiển thị chấm nhỏ)
    3. ✏ `Rename` (Đổi tên phiên tại chỗ)
    4. 🗑 `Delete` (Xóa phiên - màu đỏ)
    *(Tuyệt đối không có "Add to project")*.
- **File:** `apps/web/src/features/auth/components/AvatarDropdownPopover.tsx`
  - Thay thế nút `popover-upgrade-btn` ("Nâng cấp gói") bằng item:
    - Icon: `Sun` (nếu đang dark) hoặc `Moon` (nếu đang light).
    - Nhãn: Chuyển sang chế độ sáng / Chuyển sang chế độ tối.
    - Click: Gọi `toggleTheme()` từ hook `useTheme`.

### Module 2: Thanh Công Cụ Đọc PDF & Menu Tùy Chọn
- **File:** `apps/web/src/features/reader/components/ViewportControls.tsx`
  - Xóa bỏ nút Zen PDF (`zen-pdf-btn`).
  - Xóa bỏ các nút Mode View (`single`, `two-page`, v.v.).
- **File:** `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx`
  - Xóa mục "Mode view" (Xem 1 trang / 2 trang).
  - Xóa mục "Đọc tập trung Zen PDF".
  - Bổ sung mục "Sổ ghi chú" (Icon `BookMarked`, nhãn "Sổ ghi chú", khi click kích hoạt mở tab/panel Notes).

### Module 3: Cửa Sổ Trợ Lý & Bong Bóng Nổi
- **File:** `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
  - *Dọn sạch Header Chat:* Xóa nút `(+) New Chat`, xóa nhãn `Assistant`, xóa nút cài đặt `Settings`, xóa nút đổi theme `Sun/Moon`, xóa nút `Zen Chat`. Chỉ giữ lại nút thu phóng toàn màn hình hoặc nút đóng `✕`.
  - *Đổi tên:* Thay thế mọi chuỗi `Socratic Copilot` thành `Socratic Assistant`.
  - *Xóa bỏ bong bóng thừa:*
    - Xóa bỏ hoàn toàn component `VerticalEdgeDock` (vốn chứa 3 bong bóng: thông tin bài báo, sổ ghi chú, assistant phía trên).
    - Giữ lại duy nhất 1 nút bong bóng nổi `floating-assistant-fab` ở góc phải dưới (khi đóng chat), chuyển icon sang biểu tượng `Sparkles` màu cam nổi bật đồng bộ với giao diện.

### Module 4: Khung Suy Luận Socratic & Điều Hướng Trích Dẫn
- **File:** `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx`
  - Loại bỏ hoàn toàn vòng lặp map in chuỗi log lặp lại: `Analyzed Bounding Box #Page X`.
  - Thiết kế theo chuẩn Claude / ChatGPT:
    - Khi đang suy nghĩ: Hiển thị badge tinh tế với hiệu ứng pulse `Thought for {elapsed}s >`.
    - Khi hoàn tất: Thu gọn mặc định thành thanh ngang tối giản `Thought for {total}s >` hoặc `✓ Thinking Finished ∨`.
    - Khi người dùng bấm vào: Mở rộng khối suy luận hiển thị văn bản tư duy tự nhiên (monologue reasoning) được căn lề thụt đầu dòng, kiểu chữ nhẹ nhàng, không gây rối mắt.
- **File:** `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx` & Data Matcher:
  - *Định dạng tên Concept Pill:* Viết hàm tiền xử lý tên nhãn: tách từ viết hoa liền nhau thành từ có dấu cách (ví dụ `SelectiveAttention` $\rightarrow$ `Selective Attention`, `ContextNoise` $\rightarrow$ `Context Noise`, `PerformanceGain` $\rightarrow$ `Performance Gain`).
  - *Chuẩn hóa ánh xạ trang & Bounding Box:* Đảm bảo khi bấm vào pill, dữ liệu truyền vào `setActiveBbox` chứa đúng `page_number` và mảng tọa độ `[x1, y1, x2, y2]`, gọi `jumpToPage(page)` để trang PDF cuộn mượt và highlight khung chính xác 100%.

---

## 4. Kế Hoạch Xác Minh (Verification Gates)

Theo hiến pháp `AGENTS.md`, toàn bộ 4 Cổng Xác Minh phải đạt 100% exit code 0:
1. **Cổng 1 (Lint & Format):** `uv run ruff check . && uv run ruff format --check .`
2. **Cổng 2 (Backend Tests):** `uv run pytest`
3. **Cổng 3 (Frontend Tests):** `npm --prefix apps/web run test` (cập nhật hoặc bổ sung các test suite cho Taskbar, Avatar Popover, ViewportControls, ThinkingBlock).
4. **Cổng 4 (Web Build):** `npm --prefix apps/web run build`
5. **Kiểm thử trực quan (Visual Verification):** Chạy lệnh Google Chrome headless chụp ảnh màn hình giao diện thực tế để đối chiếu xác nhận từng điểm yêu cầu.

---
Mời bạn xem qua bản thiết kế trên và cho biết bạn đã đồng ý để tôi tiến hành lập Implementation Plan chi tiết chưa?

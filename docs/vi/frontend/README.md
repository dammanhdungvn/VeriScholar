# Tổng Quan Kiến Trúc Frontend Nền Tảng VeriScholar (`apps/web`)

Thư mục này chứa toàn bộ tài liệu kỹ thuật, đặc tả kiến trúc, quy chuẩn mã nguồn và hướng dẫn chuyển giao thiết kế dành cho ứng dụng Web Client (`apps/web`) của nền tảng **VeriScholar**.

---

## 1. MỤC LỤC TÀI LIỆU & LỘ TRÌNH ĐỌC (DOCUMENTATION INDEX)

| STT | Tài liệu | Nội dung chính & Phạm vi áp dụng |
| :---: | :--- | :--- |
| **1** | [**`techstack-frontend.md`**](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/techstack-frontend.md) | **Lựa chọn công nghệ & Đánh đổi kỹ thuật (Production-Ready Architecture)**<br>• Bảng thuật ngữ Fresher cho Frontend kỹ thuật cao.<br>• Ma trận 14 tầng công nghệ: React 19, Vite 8, Tailwind CSS v4, Radix UI, Mozilla `pdfjs-dist`, TanStack Query v5, Zustand, `@microsoft/fetch-event-source`, KaTeX $\LaTeX$.<br>• Phân tích sâu: Trình hiển thị PDF đa tầng, cơ chế đệm token `requestAnimationFrame` chống bão re-render khi stream SSE, phân tách Server Cache vs Client UI State. |
| **2** | [**`design-system-integration.md`**](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/design-system-integration.md) | **Hướng dẫn tích hợp Hệ thống thiết kế chuẩn [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md)**<br>• Triết lý Warm-Canvas Editorial: Nền giấy kem `#faf9f5`, San hô ấm `#cc785c`, Bề mặt tối `#181715`.<br>• Bảng mã hóa CSS Variables toàn cục (`:root`).<br>• Đặc tả chi tiết các Component: Nút bấm (`button-primary`, `button-secondary`), thanh tab tài liệu (`DocumentTabBar`), khung highlight (`BoundingBoxOverlay`), thẻ tin nhắn chat và khối công thức/mã nguồn.<br>• Quy tắc DO'S & DON'TS kiểm soát chất lượng thiết kế học thuật. |
| **3** | [**`directory-structure.md`**](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/directory-structure.md) | **Cấu trúc thư mục chuẩn Production & Ranh giới Module**<br>• Sơ đồ cây thư mục chi tiết (`apps/web/src/`).<br>• Tổ chức theo tính năng (Feature-Driven: `library`, `reader`, `chat`, `notes`, `sessions`).<br>• Sơ đồ luồng dữ liệu 2 chiều (Data Flow Architecture) giữa Backend FastAPI $\leftrightarrow$ TanStack Query / SSE Client $\leftrightarrow$ Zustand Store $\leftrightarrow$ Resizable Split-Pane UI.<br>• Quy ước đặt tên (Naming Conventions) nhất quán. |
| **4** | [**`coding-standards.md`**](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/frontend/coding-standards.md) | **Quy chuẩn lập trình & Chuẩn mực Production**<br>• TypeScript nghiêm ngặt: Cấm `any`, chuẩn hóa kiểu dữ liệu tọa độ `bounding_box: [number, number, number, number, number]`.<br>• Kỷ luật React 19: Mã mẫu Token Buffer `requestAnimationFrame`, tránh thác nước truy vấn (Waterfalls), Fine-grained Zustand Selectors.<br>• Quản lý Khóa Lạc Quan (OCC): Optimistic updates, snapshot rollback khi gặp xung đột phiên bản (HTTP 409/412).<br>• An toàn XSS cho nội dung Markdown và biểu thức $\LaTeX$.<br>• Tiêu chuẩn tiếp cận WAI-ARIA (Keyboard navigation, Focus Trap, screen-reader labels). |

---

## 2. NGUYÊN TẮC BẤT BIẾN KỸ THUẬT (FRONTEND TECHNICAL INVARIANTS)

1. **Bất biến Tọa độ Bounding Box (Spatial Coordinates Invariant):**
   - Tọa độ trích dẫn luôn ở định dạng chuẩn hóa 5 phần tử `[x0, y0, x1, y1, page]` trong khoảng $[0.0, 1.0]$.
   - Lớp hiển thị phải áp dụng công thức *Dynamic Viewport Matrix Scaling* để khung viền highlight không bị trôi lệch khi zoom, cuộn hoặc xoay trang.
2. **Bất biến Stream Thời gian thực (Zero-Jank SSE Invariant):**
   - Kết nối SSE qua endpoint `POST /api/v1/sessions/{id}/messages` bắt buộc sử dụng `@microsoft/fetch-event-source` để gửi kèm Bearer JWT và payload.
   - Tuyệt đối không kích hoạt `setState` trên từng chunk token đơn lẻ; bắt buộc gom nhóm qua hàng đợi đệm và xả bằng `requestAnimationFrame`.
3. **Bất biến Khóa Lạc Quan (Optimistic Concurrency Control - OCC Invariant):**
   - Mọi thao tác thay đổi trạng thái phiên hoặc ghi chú (`PATCH /api/v1/sessions/{id}/viewport`) phải gửi kèm số hiệu phiên bản `version`.
   - Nếu máy chủ trả về mã lỗi `409 Conflict` hoặc `412 Precondition Failed`, client phải tự động phục hồi về bản chụp dữ liệu trước đó và đồng bộ lại trạng thái mới nhất từ server.
4. **Bất biến Thẩm mỹ Học thuật (Editorial Design Invariant):**
   - Tuân thủ 100% hướng dẫn từ [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md): Tuyệt đối không dùng nền trắng tinh `#ffffff` toàn trang hoặc màu xanh công nghiệp. Luôn dùng nền giấy kem `#faf9f5` kết hợp nút bấm San hô ấm `#cc785c` và mặt sàn tối `#181715` cho mã nguồn.

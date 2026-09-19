# BỘ KHUNG PROMPT CHUẨN PRODUCTION DÀNH CHO PHÁT TRIỂN FRONTEND (FULLSTACK INTEGRATION)

Tài liệu này cung cấp 2 mẫu prompt tiêu chuẩn phục vụ quy trình phát triển Frontend của nền tảng **VeriScholar**:
1. **Prompt 1 (`/plan`):** Lập kế hoạch kỹ thuật chi tiết cho từng API / Cụm tính năng màn hình.
2. **Prompt 2 (`Execution`):** Triển khai coding, kiểm thử tự động, visual audit và tích hợp Fullstack hoàn chỉnh.

---

## PROMPT 1: LẬP KẾ HOẠCH KỸ THUẬT FRONTEND CHI TIẾT (`/plan`)

```markdown
/plan Hãy lập kế hoạch kỹ thuật chi tiết để xây dựng giao diện Frontend, tích hợp API và kiểm chuẩn chuẩn production cho VeriScholar:
TARGET: "[TÊN CỤM TÍNH NĂNG / MÀN HÌNH FRONTEND & DANH SÁCH API CẦN TÍCH HỢP]
--------------------------------------------------------------------------------------------------------
[Phương thức HTTP]   [Đường dẫn API]              # [Số thứ tự API trong swagger.md & Mô tả nghiệp vụ]
"

YÊU CẦU NGUYÊN TẮC & TÀI LIỆU THAM CHIẾU:
1. Tuân thủ tuyệt đối các tài liệu thiết kế & kiến trúc của VeriScholar:
   - Frontend Architecture & Engineering Trade-offs: docs/vi/frontend/techstack-frontend.md
   - Directory Structure & Data Flow: docs/vi/frontend/directory-structure.md
   - Coding Standards & Performance Guidelines: docs/vi/frontend/coding-standards.md
   - Design System Integration & Semantic Tokens: docs/vi/frontend/design-system-integration.md
   - Hồ sơ Thiết kế Giao diện gốc: DESIGN.md (Warm-Canvas Editorial, Tinted Cream #faf9f5, Coral #cc785c, Dark Navy #181715, Copernicus/Tiempos Serif + Inter/StyreneB Sans + JetBrains Mono)
   - Product Requirements Document: docs/vi/PRD.md
   - Backend API Specification & Envelopes: docs/vi/design-api.md và docs/vi/swagger.md
   - Database Schema DDL & Data Contracts: docs/vi/design-database.md
   - Agent Protocol & Skills: AGENTS.md và các skills trong .agents/skills/ (react-patterns, react-performance, ui-styling, ui-ux-pro-max, e2e-testing, verification-loop)
   - Cấu hình công cụ MCP hỗ trợ: .agents/mcp_config.json (chrome-devtools, puppeteer, context7-docs, sequential-thinking)
   - Danh mục các kế hoạch đã duyệt: docs/vi/decided/

2. Phân rã kế hoạch theo 5 Trụ cột Frontend Chuẩn Production & Fullstack:
   - UI/UX & Design System Specification (DESIGN.md):
     + Đặc tả các component cần xây dựng mới hoặc mở rộng trong apps/web/src/components/ui/ và src/features/<module>/components/.
     + Áp dụng chính xác Semantic Tokens: Bảng màu (nền giấy kem, nút san hô coral, viền hairline 1px, mặt sàn tối cho code/toán học), Typography (phân cấp Serif Display cho h1-h3, Sans cho body/button, Monospace cho số liệu/mã), thang bo góc (8px cho controls, 12px cho card, 9999px cho badge).
     + Thiết kế đầy đủ 5 trạng thái giao diện: Default, Loading/Skeleton, Empty State, Error State (kèm nút Retry), và Active/Highlight state.
     + Quy chuẩn tiếp cận WAI-ARIA: Hỗ trợ phím Tab, Enter, Esc; Focus Trap cho Modal; thuộc tính role và aria-label rõ ràng cho trình đọc màn hình.
   - Data Layer, State Management & TypeScript Contracts:
     + Định nghĩa TypeScript interfaces/types trong src/types/ khép kín 1-1 với OpenAPI schema từ Backend (Cấm sử dụng any).
     + Phân định rạch ròi Server Cache (@tanstack/react-query v5) và Client UI State (zustand store).
     + Xử lý Khóa Lạc Quan (OCC Optimistic Updates): Cơ chế snapshot rollback khi máy chủ trả về lỗi xung đột phiên bản (HTTP 409 / 412).
     + Xử lý Real-time Streaming (nếu có SSE): Cơ chế Token Buffer qua requestAnimationFrame (rAF) chống bão re-render (Zero-Jank Engine).
   - Component Architecture & Layout Integration:
     + Sắp xếp phân tầng Container (Smart) Component vs Presentation (Dumb) Component.
     + Tích hợp vào khung không gian làm việc Resizable Split-Pane (react-resizable-panels) và Document Tab Bar.
     + Xử lý thuật toán tọa độ không gian (nếu liên quan PDF / Bounding Box): Dynamic Viewport Matrix Scaling giữ khung highlight không bị lệch khi zoom/cuộn/xoay trang.
   - Kế hoạch Kiểm thử Đa tầng & Visual Audit (Testing & Verification Plan):
     + Component & Hook Unit Tests (Vitest + React Testing Library): Kiểm thử logic biến đổi dữ liệu, OCC rollback và render component.
     + E2E / User Flow Tests: Kịch bản giả lập hành vi người dùng gọi API thực tế từ trình duyệt.
     + Visual & Console Inspection: Sử dụng chrome-devtools MCP và puppeteer MCP để kiểm tra sạch lỗi console (Console Error = 0), bắt network payload và chụp ảnh giao diện đối chiếu.
   - Nghiên cứu & Đối sánh Quốc tế (State-of-the-Art Benchmarking):
     + Tìm hiểu cách các sản phẩm AI / Academic hàng đầu thế giới (Claude.ai, Perplexity, NotebookLM, ChatPDF, Elicit) giải quyết bài toán UI/UX và luồng tương tác tương tự.
     + So sánh với giải pháp hiện tại và đề xuất các cải tiến tinh tế (micro-interactions, keyboard shortcuts, animations) nếu nâng cao trải nghiệm người dùng thực tế.

3. Ràng buộc an toàn & Quy trình vận hành:
   - Phân tích cẩn trọng các rủi ro kỹ thuật, đánh đổi (trade-offs) trước khi đề xuất.
   - CHỈ DỪNG LẠI Ở VIỆC LẬP KẾ HOẠCH, TUYỆT ĐỐI CHƯA ĐƯỢC VIẾT MÃ NGUỒN CODING khi tôi chưa phê duyệt.
   - Đề xuất tên Git branch mới chuẩn quy ước (ví dụ: feat/fe-m1-[tên-rút-gọn]) cho TARGET này.
   - Rà soát các biến môi trường Vite cần thiết (VITE_...) từ .env.example (tuyệt đối KHÔNG đọc file .env). Nếu TARGET cần thêm biến môi trường, hãy liệt kê rõ để tôi cập nhật.
   - Không được tự động git add, git commit hoặc tạo Pull Request khi chưa nhận lệnh.
   - Tắt toàn bộ terminal/background task ngầm sau khi lập xong kế hoạch.
   - Lưu toàn bộ nội dung kế hoạch vào tệp: docs/vi/decided/frontend/[tên-rút-gọn-của-target].md và dừng lại chờ tôi phê duyệt.
```

---

## PROMPT 2: THỰC THI CODING FRONTEND HOÀN CHỈNH TỪNG API (`Execution`)

```markdown
Tôi đồng ý! Hãy bắt đầu coding thực hiện xây dựng tính năng Frontend & tích hợp Fullstack:
TARGET: "[TÊN CỤM TÍNH NĂNG / MÀN HÌNH FRONTEND & DANH SÁCH API CẦN TÍCH HỢP]
--------------------------------------------------------------------------------------------------------
[Phương thức HTTP]   [Đường dẫn API]              # [Số thứ tự API trong swagger.md & Mô tả nghiệp vụ]
"

QUY TRÌNH & TIÊU CHUẨN THỰC THI (PRODUCTION-GRADE FRONTEND):
1. Tuân thủ 100% Kế hoạch đã duyệt và Bộ tài liệu thiết kế:
   - Kế hoạch kỹ thuật tại: docs/vi/decided/frontend/[tên-rút-gọn-của-target].md
   - docs/vi/frontend/techstack-frontend.md, docs/vi/frontend/directory-structure.md, docs/vi/frontend/coding-standards.md, docs/vi/frontend/design-system-integration.md, và DESIGN.md.
   - Nguyên tắc AGENTS.md và các skills trong .agents/skills/.

2. Các bước triển khai mã nguồn tuần tự (Thực hiện dứt điểm từng thành phần):
   - Bước 1 (Branching): Tạo và chuyển sang Git branch mới theo kế hoạch đã duyệt (nếu chưa tạo).
   - Bước 2 (Types & Contracts): Khai báo đầy đủ kiểu dữ liệu TypeScript trong src/types/ (Envelopes, Requests, Responses). Tuyệt đối cấm any.
   - Bước 3 (Data Layer & Hooks): Xây dựng TanStack Query hooks, Mutation hooks với Optimistic Updates / OCC rollback, và SSE streaming client qua @microsoft/fetch-event-source kết hợp requestAnimationFrame Token Buffer.
   - Bước 4 (UI Primitives & Feature Components): Xây dựng các component giao diện tại src/components/ui/ và src/features/<module>/components/ theo đúng 100% Design Tokens từ DESIGN.md (Màu kem #faf9f5, San hô #cc785c, Mặt sàn tối #181715, Serif Copernicus/Tiempos, bo góc 8px/12px/9999px). Đảm bảo đầy đủ Loading skeleton, Empty state, Error boundary.
   - Bước 5 (Fullstack Screen Integration): Gắn kết các component vào bố cục không gian làm việc chính (SplitWorkspace, TabBar, Header/Sidebar).
   - Bước 6 (Testing & Verification):
     + Viết unit/component test cho logic xử lý dữ liệu và component state.
     + Sử dụng công cụ MCP (chrome-devtools hoặc puppeteer) mở trang kiểm tra thực tế: Bảo đảm 0 lỗi Console Error, network calls gọi đúng endpoint Backend, giao diện hiển thị đúng chuẩn.
   - Bước 7 (Checklist Hoàn Thiện): Xác nhận API này đã hoạt động hoàn hảo 100% từ Frontend đến Backend trước khi chuyển sang API tiếp theo.

3. Nguyên tắc an toàn dữ liệu, công cụ & môi trường:
   - Sử dụng import.meta.env cho biến môi trường frontend. Tuyệt đối KHÔNG đọc file .env, chỉ đọc .env.example. Nếu cần biến mới, thêm vào .env.example và thông báo cho tôi.
   - Sử dụng các MCP tools chính thức đã cấu hình: context7-docs (tra cứu docs React 19/Tailwind v4), chrome-devtools (inspect console, network, chụp UI screenshot), filesystem.
   - TUYỆT ĐỐI KHÔNG tự động git add, git commit hoặc tạo Pull Request khi chưa có lệnh trực tiếp từ tôi.
   - Dọn dẹp, đóng các tiến trình ngầm sau khi hoàn tất.
```

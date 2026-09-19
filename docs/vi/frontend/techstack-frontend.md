# Lựa Chọn Công Nghệ Frontend & Đánh Đổi Kỹ Thuật (Production-Ready Architecture)

Tài liệu này tổng hợp các quyết định lựa chọn công nghệ cốt lõi, đánh đổi kỹ thuật (Engineering Trade-offs) và kiến trúc giao diện người dùng chuẩn Production cho ứng dụng **Web Client (`apps/web`)** của nền tảng **VeriScholar**, kế thừa trực tiếp từ các tài liệu đặc tả [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md), [design-architecture.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md), [design-api.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) và tuân thủ 100% hồ sơ thiết kế [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md).

---

## 0. BẢNG THUẬT NGỮ FRONTEND DÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ | Khái niệm tiếng Anh | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Split-Pane Layout** | Resizable Split-Pane Workspace | Bố cục màn hình chia đôi có thể kéo co giãn mượt mà: Nửa trái là trình đọc PDF đa tab, nửa phải là khung chat AI và sổ tay nghiên cứu. |
| **PDF Canvas & Text Layer** | Two-Layer PDF Rendering | Kiến trúc render PDF 2 lớp của PDF.js: Lớp dưới là Canvas vẽ pixel hình ảnh/nội dung bài báo, lớp trên là Text Layer trong suốt dạng HTML DOM để người dùng có thể bôi đen, chọn chữ và copy. |
| **Bounding Box Overlay** | Spatial Coordinate Highlight Layer `[x0, y0, x1, y1, page]` | Lớp phủ đồ họa độc lập định vị tuyệt đối (`position: absolute`) nằm đè lên trang PDF để vẽ khung viền vàng highlight đúng vị trí bằng chứng mà AI trích dẫn. |
| **Dynamic Viewport Matrix Scaling** | Page Dimension & Rotation Invariant Scaling | Công thức toán học chuyển đổi tọa độ chuẩn hóa từ Backend `[0.0, 1.0]` sang tọa độ pixel thực tế trên màn hình `[px]`, đảm bảo khung highlight không bị lệch khi người dùng zoom (50% - 300%), cuộn trang hoặc xoay màn hình. |
| **Optimistic Updates** | Optimistic Concurrency Control (OCC) UI | Kỹ thuật cập nhật giao diện ngay lập tức trước khi server phản hồi (ví dụ: đổi tên phiên, đánh dấu sao bài báo, lưu vị trí trang đọc), tự động rollback nếu server báo lỗi version xung đột (409/412). |
| **Zero-Jank Streaming** | RequestAnimationFrame (rAF) Token Buffer | Cơ chế đệm chữ (token buffer) khi nhận stream SSE tốc độ cao từ LLM (30 - 80 tokens/giây): gom nhóm các token trong cùng 1 animation frame (~16ms) thay vì gọi `setState` sau mỗi token, chống đơ giật UI và tụt fps. |
| **KaTeX Math Rendering** | LaTeX Formula Web Rendering | Thư viện dịch các chuỗi công thức toán học LaTeX (như `$E=mc^2$` hoặc `$$\int_{-\infty}^\infty e^{-x^2} dx$$`) thành HTML/MathML siêu nhanh, hiển thị mượt mà các biểu thức giải thuật khoa học. |
| **Server State vs Client UI State** | Server Cache vs Ephemeral State Separation | Nguyên tắc phân tách dữ liệu rõ ràng: Server State (danh sách bài báo, lịch sử phiên, chi tiết turns) do TanStack Query quản lý; Client UI State (tab đang mở, tỷ lệ chia màn hình, mức zoom) do Zustand quản lý. |
| **WAI-ARIA Accessibility** | Web Accessibility Standards | Bộ quy chuẩn giúp các thành phần giao diện (dialog, dropdown, tab, tooltip) có thể thao tác hoàn toàn bằng bàn phím (Phím Tab, Enter, Esc, Mũi tên) và thân thiện với trình đọc màn hình. |

---

## 1. BẢNG MA TRẬN LỰA CHỌN CÔNG NGHỆ FRONTEND CHUẨN PRODUCTION

| Tầng Kiến Trúc | Công Nghệ Lựa Chọn | Vai Trò Trong VeriScholar Web Client | Đánh Đổi Kỹ Thuật & Lý Do Lựa Chọn |
| :--- | :--- | :--- | :--- |
| **Core Framework** | **React 19 (TSX)** + **Vite 8** | Nền tảng xây dựng Single-Page Application (SPA) hiện đại với TypeScript nghiêm ngặt. | Hỗ trợ Actions, `useOptimistic`, `useActionState` và tương thích tối đa với hệ sinh thái thư viện AI. Vite 8 mang lại tốc độ HMR dưới 50ms và tối ưu kích thước bundle khi build production với Rollup/ESBuild. |
| **Styling & Design Tokens** | **Tailwind CSS v4** | Hệ thống utility-first CSS, định nghĩa bộ Semantic Design Tokens chuẩn [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md) (Nền giấy kem canvas, san hô coral, typography serif/sans). | Không phát sinh runtime CSS-in-JS overhead; kích thước CSS build siêu nhỏ (< 15KB gzipped). Cung cấp biến CSS tùy biến cho chế độ Tinted Cream Canvas và Dark Navy Surface. |
| **UI Component Primitives** | **Radix UI** + **shadcn/ui** | Cung cấp các headless primitives (Dialog, Tabs, Tooltip, DropdownMenu, Popover, Slider). | **Không bị bó hẹp trong giao diện cứng nhắc như Ant Design hay MUI.** Mã nguồn component nằm trực tiếp trong codebase (`src/components/ui/`), 100% tuân thủ WAI-ARIA, dễ dàng tùy biến theo chuẩn [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md). |
| **CSS Utilities & Icons** | **`clsx`** + **`tailwind-merge`** + **`lucide-react`** | Xử lý ghép nối class linh hoạt và cung cấp hệ thống icon vector đồng bộ. | `cn()` helper giải quyết triệt để vấn đề ghi đè class Tailwind (như `p-4` vs `p-2`). `lucide-react` cung cấp icon vector sắc nét, tải theo dạng tree-shaking từng icon. |
| **Workspace Layout** | **`react-resizable-panels`** | Bố cục chia đôi màn hình Split-Pane giữa PDF Viewer và AI Workspace. | Tác giả BVaughn (thành viên React Core Team). Đảm bảo kéo co giãn mượt mà 60fps, hỗ trợ ẩn/hiện nhanh panel, tự động lưu tỷ lệ màn hình vào `localStorage`. |
| **PDF Rendering Engine** | **`pdfjs-dist` (Mozilla PDF.js)** | Hiển thị tài liệu PDF gốc đa tab, render Canvas và tạo lớp phủ văn bản (Text Layer). | Tiêu chuẩn công nghiệp của Mozilla (ISO 32000-1). Hỗ trợ Web Worker đa luồng để giải mã tệp PDF lớn (> 50MB) mà không chặn main thread giao diện người dùng. |
| **Server State & Cache** | **`@tanstack/react-query` v5** | Quản lý dữ liệu máy chủ, caching, tự động refetch ngầm, request deduplication và Optimistic Updates. | Triệt tiêu 100% tình trạng dữ liệu bất đồng bộ giữa các tabs; hỗ trợ rollback khi gặp xung đột OCC (mã lỗi 409/412); giảm tải tới 70% số lượng request trùng lặp tới Backend FastAPI. |
| **Client UI State** | **`zustand`** | Quản lý trạng thái UI cục bộ (Tab tài liệu đang chọn, mức zoom PDF, highlight active, panel state). | Dung lượng siêu nhẹ (< 1.2KB), không boilerplate như Redux Toolkit, không gây re-render toàn cây DOM như React Context thuần, hỗ trợ middleware devtools và persist. |
| **Real-time SSE Streaming** | **`@microsoft/fetch-event-source`** | Tiếp nhận dòng dữ liệu Server-Sent Events (SSE) thời gian thực cho tính năng AI Chat & Summary Stream. | **Vượt trội so với Native `EventSource` của trình duyệt:** Hỗ trợ gửi HTTP `POST` kèm Authorization Bearer Header và JSON body phức tạp, tự động reconnect, hỗ trợ `AbortController` ngắt dòng khi người dùng bấm "Dừng sinh". |
| **Markdown & LaTeX Math** | **`react-markdown`** + **`remark-gfm`** + **`remark-math`** + **`rehype-katex`** + **`katex`** | Hiển thị bài viết học thuật, bảng biểu, danh mục trích dẫn và công thức toán học $\LaTeX$. | Render an toàn qua AST (Abstract Syntax Tree), ngăn chặn triệt để XSS; hiển thị công thức toán học từ các bài báo arXiv chuẩn xác với tốc độ vượt trội so với MathJax. |
| **Syntax Highlighting** | **`rehype-highlight`** (hoặc **`shiki`**) | Tô màu cú pháp mã nguồn (Python, PyTorch, C++, SQL) trong phản hồi của AI trên bề mặt tối `surface-dark`. | Tạo trải nghiệm đọc mã nguồn trực quan trên nền `#181715`, hỗ trợ nút bấm "Copy Code" tiện lợi. |
| **Routing & Navigation** | **`react-router-dom` v7** | Định tuyến SPA (`/library`, `/sessions/:id`, `/shares/:token`). | Hỗ trợ lưu trữ trạng thái vị trí đọc vào URL search params (`?page=4&tab=chat`), giúp người dùng có thể chia sẻ liên kết hoặc F5 trình duyệt mà không mất vị trí đọc. |
| **Forms & Validation** | **`react-hook-form`** + **`zod`** | Quản lý form nhập liệu (Tạo phiên, đổi tên, ghi chú, tìm kiếm). | Không gây re-render khi gõ phím; `zod` chia sẻ cùng quy tắc xác thực kiểu dữ liệu với Pydantic Backend, ngăn chặn lỗi nhập liệu ngay tại client. |
| **Toast & UX Feedback** | **`sonner`** | Hệ thống thông báo toast (Thành công, Lỗi mạng, Cảnh báo OCC). | Thiết kế thanh lịch, hỗ trợ hành động trực tiếp (Undo, Retry), tự động gom nhóm thông báo thông minh. |

---

## 2. PHÂN TÍCH KỸ THUẬT CHUYÊN SÂU & CÁC ĐÁNH ĐỔI SỐNG CÒN

### 2.1. Tại sao chọn Tailwind CSS + Radix UI thay vì Ant Design hay Material UI (MUI)?

1. **Ngôn ngữ thiết kế Academic Editorial đặc thù:**
   - Các thư viện nguyên khối như Ant Design hay MUI bị đóng khung trong phong cách ứng dụng quản trị doanh nghiệp (Enterprise CRUD) với viền bo tròn lớn và màu xanh công nghiệp, đi ngược lại hoàn toàn triết lý ấm áp và trang nhã của [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md).
   - Radix UI cung cấp các headless primitives (chỉ có logic hành vi và accessibility, không chứa CSS). Đội ngũ phát triển có thể tự do định hình từng pixel bằng Tailwind CSS để đạt chuẩn thẩm mỹ học thuật tinh tế của Anthropic Claude.
2. **Kích thước gói tải về (Bundle Size):**
   - MUI và Ant Design thường kéo theo từ 350KB đến 800KB mã nguồn JavaScript runtime vào bundle ban đầu.
   - Tailwind CSS v4 tạo file CSS tĩnh được purge sạch sẽ chỉ chứa các class thực sự sử dụng (< 20KB), giúp tốc độ tải trang lần đầu (First Contentful Paint - FCP) dưới 0.8 giây.

---

### 2.2. Kiến Trúc Render PDF Đa Tầng & Lớp Phủ Tọa Độ Bounding Box (Spatial Invariants)

Một trong những tính năng tạo nên sự khác biệt của VeriScholar là **khung viền vàng highlight đúng đoạn văn bằng chứng** trên PDF khi người dùng nhấp vào huy hiệu trích dẫn của AI.

#### Cơ Chế 3 Lớp Xếp Chồng (Layer Stacking Architecture):
```text
┌─────────────────────────────────────────────────────────┐
│ 3. Highlight Overlay Layer (DIVs absolute, pointer-none) │
├─────────────────────────────────────────────────────────┤
│ 2. Text Layer (HTML Spans trong suốt, selectable text)  │
├─────────────────────────────────────────────────────────┤
│ 1. Canvas Layer (PDF.js rendered image bitmap)          │
└─────────────────────────────────────────────────────────┘
```

1. **Lớp 1 - Canvas Layer:**
   - PDF.js render từng trang PDF vào thẻ `<canvas>` dựa trên tỷ lệ `scale = zoom_ratio * window.devicePixelRatio`.
2. **Lớp 2 - Text Layer:**
   - Tạo các thẻ `<span>` văn bản trong suốt đè chính xác lên từng dòng chữ trên canvas, cho phép người dùng bôi đen, tra từ điển hoặc copy trích dẫn nguyên bản.
3. **Lớp 3 - Highlight Overlay Layer:**
   - Nhận mảng tọa độ chuẩn hóa từ Backend `[x0, y0, x1, y1, page]`.
   - **Công thức chuyển đổi tọa độ bất biến (Dynamic Matrix Scaling):**
     $$\text{left} = x_0 \times \text{viewport.width}$$
     $$\text{top} = y_0 \times \text{viewport.height}$$
     $$\text{width} = (x_1 - x_0) \times \text{viewport.width}$$
     $$\text{height} = (y_1 - y_0) \times \text{viewport.height}$$
   - Nhờ áp dụng công thức theo kích thước thực tế của `viewport` tại thời điểm render, khung viền highlight bảo đảm **chính xác 100% không bị lệch tọa độ** bất kể người dùng phóng to 200%, thu nhỏ 75%, hay đọc trên màn hình Retina độ phân giải cao.

---

### 2.3. Trình Đọc Dữ Liệu SSE Chống Bão Re-render (Zero-Jank Streaming Engine)

Khi LLM sinh văn bản, Backend FastAPI đẩy liên tục các sự kiện SSE qua kết nối HTTP (`POST /api/v1/sessions/{id}/messages`). Tốc độ truyền có thể đạt tới 60 - 100 chunks/giây.

#### Vấn đề nếu dùng State thông thường:
Nếu mỗi chunk SSE nhận về đều gọi `setTurnAnswer(prev => prev + token)`, React sẽ kích hoạt 60 - 100 lần re-render mỗi giây trên toàn bộ cây thành phần Chat, gây nghẽn Main Thread, tụt FPS nghiêm trọng và giật lag khi người dùng đang cuộn tài liệu.

#### Giải pháp kỹ thuật Production:
1. **RequestAnimationFrame (rAF) Token Buffer:**
   - Khi sự kiện SSE tới, token được đưa vào một mảng hàng đợi tạm thời (`bufferQueue.push(token)`).
   - Một vòng lặp `requestAnimationFrame` sẽ xả toàn bộ buffer vào React state đúng 1 lần trong mỗi khung hình render của màn hình (~16.6ms với màn hình 60Hz hoặc ~8.3ms với màn hình 120Hz).
2. **Thư viện `@microsoft/fetch-event-source`:**
   - Cho phép gửi kèm Bearer JWT Token trong request header và body JSON (khắc phục hoàn toàn hạn chế của `EventSource` chỉ cho phép GET không có Authorization header).
   - Hỗ trợ `AbortController` cho phép người dùng bấm nút "Dừng sinh phản hồi" ngay lập tức, ngắt kết nối socket phía client và báo hiệu Backend giải phóng tài nguyên LLM.

---

### 2.4. Phân Tách Trạng Thái: TanStack Query (Server) vs Zustand (Client UI)

| Tiêu Chí | Server State (`@tanstack/react-query`) | Client UI State (`zustand`) |
| :--- | :--- | :--- |
| **Bản chất dữ liệu** | Dữ liệu thuộc quyền sở hữu của Backend (Sessions, Documents, Turns, Notes, Chunks). | Dữ liệu giao diện tạm thời (Tab đang mở, zoom level, vị trí split pane, modal open/close). |
| **Cơ chế lưu trữ** | Caching theo `queryKey`, tự động dọn dẹp khi stale, tự động revalidate khi focus cửa sổ. | Bộ nhớ JavaScript thuần túy trong client session, đồng bộ chọn lọc vào `localStorage`. |
| **Xử lý OCC & Version** | Hỗ trợ Mutation với **Optimistic Updates**; rollback tự động nếu backend báo lỗi `409 Conflict`. | Quản lý các cờ hiển thị (`isDragging`, `isStreaming`, `activeHighlightId`). |
| **Tránh Re-render** | Dùng cơ chế `select` selector để chỉ re-render component khi trường dữ liệu cụ thể thay đổi. | Đăng ký trực tiếp qua Zustand selector: `const zoom = useReaderStore(s => s.zoomRatio)`. |

---

## 3. THIẾT KẾ GIAO DIỆN HỌC THUẬT TUÂN THỦ DESIGN.MD (ACADEMIC DESIGN SYSTEM)

VeriScholar kế thừa trọn vẹn đặc tả từ [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md) để xây dựng hệ thống Design Tokens:

### 3.1. Bảng Màu & Bề Mặt Học Thuật (Academic Color Tokens)
* **Nền giấy kem ấm áp (Canvas `#faf9f5`):** Nền sàn mặc định cho toàn bộ màn hình đọc và thư viện.
* **Bề mặt thẻ nội dung (Surface Card `#efe9de`):** Nền thẻ tài liệu, các khối ghi chú và tóm tắt.
* **Mặt sàn sản phẩm công nghệ (Surface Dark `#181715`):** Khối hiển thị mã nguồn, terminal dòng lệnh và các biểu đồ phân tích sâu.
* **Điểm nhấn San hô ấm (Primary Coral `#cc785c`):** Sử dụng cho toàn bộ các nút bấm chính (Primary CTA), biểu tượng thương hiệu và huy hiệu nổi bật.
* **Đường viền tóc mỏng (Hairline `#e6dfd8`):** Đường kẻ 1px phân tách các panel Split-Pane và thanh công cụ.
* **Điểm nhấn trích dẫn & Bounding Box:**
  - Viền khung Bounding Box: Màu Hổ phách ấm `accent-amber` (`#e8a55a`) với lớp phủ mờ `rgba(232, 165, 90, 0.18)`.
  - Huy hiệu trích dẫn đã kích hoạt: Màu San hô ấm `primary` (`#cc785c`).

### 3.2. Cấu Trúc Typography Đối Xứng
* **Tiêu đề Display (h1, h2, h3):** Slab-Serif Display (`Copernicus` / `Tiempos Headline`, fallback `Cormorant Garamond` hoặc `EB Garamond`) tại trọng số `weight: 400` với khoảng cách chữ âm (`letterSpacing: -0.3px` đến `-1.5px`), mang lại chất giọng văn chương hàn lâm sâu sắc.
* **Nội dung & Nhãn điều hướng (Body & UI):** Humanist Sans (`StyreneB`, fallback `Inter`) tại trọng số `weight: 400` cho văn bản thường và `weight: 500` cho nhãn, nút bấm.
* **Mã nguồn & Tọa độ Bounding Box:** `JetBrains Mono` tại trọng số `weight: 400` trên nền tối `surface-dark`.

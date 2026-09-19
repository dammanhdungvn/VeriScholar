# Kế Hoạch Kỹ Thuật Chi Tiết: Xây Dựng Phân Hệ Frontend Dashboard (VeriScholar)

> **TARGET:** Frontend Dashboard — Không Gian Nghiên Cứu & Hợp Tác Học Thuật  
> **Trạng thái:** Đã nghiệm thu và hoàn tất triển khai (Approved & Fully Implemented)  
> **Git Branch:** `feat/fe-dashboard` (đã khởi tạo từ `feat/fe-auth`)  
> **Vị trí lưu trữ tài liệu:** `docs/vi/decided/frontend/dashboard.md`  
> **Mã nguồn tính năng mục tiêu:** [`apps/web/src/features/dashboard/`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/dashboard/)  
> **Tài liệu tham chiếu:** [PRD.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md), [DESIGN.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/DESIGN.md), [design-api.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md), [swagger.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/swagger.md), [auth.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/decided/frontend/auth.md), [landing-page.md](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/decided/frontend/landing-page.md)  
> **Mẫu tham khảo đối chiếu:** [`temp/dashboard/`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/temp/dashboard/)

---

## 1. TỔNG QUAN MỤC TIÊU & NGUYÊN TẮC THIẾT KẾ CỐT LÕI

### 1.1. Mục Tiêu Nghiệp Vụ
Dashboard là trung tâm điều hành nghiên cứu của VeriScholar sau khi người dùng xác thực (`/dashboard`). Nơi đây hợp nhất hai phương thức làm việc học thuật cao cấp:
1. **Chế độ Đối thoại Socratic (`Chat Mode`):** Hỏi đáp sâu trên tài liệu nghiên cứu, kiểm chứng công thức toán LaTeX, tự động uốn nắn tiền đề sai (Presupposition Validation) và truy nguyên bằng chứng Bounding Box trực quan.
2. **Chế độ Không gian Hợp tác (`Cowork Mode`):** Phân rã mục tiêu nghiên cứu thành kế hoạch thực thi (Work Intake & ExecPlan), duyệt hành động nhạy cảm (Human Approval Gate) và soạn thảo bài học tổng hợp (Smart Knowledge Digest) song song bên cạnh tài liệu gốc.

### 1.2. Nguyên Tắc Sống Còn: Triệt Tiêu Giao Diện Rườm Rà Nhiều Chữ (Zero Verbal Clutter)
> **Quy tắc thiết kế:** Giao diện học thuật KHÔNG đồng nghĩa với giao diện ngập tràn chữ kể lể, quảng bá tính năng hoặc các đoạn hướng dẫn dài dòng. Nhà nghiên cứu cần môi trường tĩnh lặng, tập trung cao độ (Deep Work).
- **Quy tắc Micro-copy tinh gọn:**
  - Tiêu đề chào mừng: Tối đa 4–5 từ (Ví dụ: `Chào buổi tối, TS. Dũng` hoặc `Không gian nghiên cứu`).
  - Nhãn nút bấm: 1–2 từ (Ví dụ: `Gửi`, `Tải bài`, `Phê duyệt`, `Sao chép`).
  - Thẻ hành động gợi ý: Ngắn gọn dưới 6 từ, tập trung vào hành động học thuật, không văn hoa tiếp thị.
  - Thay thế chữ giải thích bằng Icon trực quan (Lucide Icons) kết hợp Tooltip nhẹ nhàng.
  - Loại bỏ hoàn toàn các banner cảnh báo/chú thích bản quyền thừa thãi.

---

## 2. RÀ SOÁT BIẾN MÔI TRƯỜNG VITE (`.env.example`)

Qua rà soát `apps/web/.env.example`, hệ thống cần bổ sung biến cấu hình sau để phân tách rạch ròi chế độ Mock phát triển độc lập và kết nối Backend thật:

```bash
# ==============================================================================
# VeriScholar Dashboard Configuration (apps/web)
# ==============================================================================
# Cờ bật/tắt chế độ Mock Dashboard khi Backend FastAPI chưa khởi chạy hoặc trong Unit Tests
VITE_ENABLE_MOCK_DASHBOARD=true
```

---

## 3. NĂM TRỤ CỘT FRONTEND PRODUCTION

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VERISCHOLAR FRONTEND DASHBOARD                         │
│                                                                             │
│  ┌─────────────────────────┐             ┌───────────────────────────────┐  │
│  │ Trụ Cột 1: UI/UX Tokens │             │ Trụ Cột 2: Data & Contracts   │  │
│  │ • Warm-Canvas Editorial │             │ • TypeScript OpenAPI 1-1      │  │
│  │ • Taskbar Rail 52px-260 │             │ • React Query v5 Server Cache │  │
│  │ • Auto-Resize ChatInput │             │ • Zustand Client UI State     │  │
│  │ • 5 Interface States    │             │ • rAF Token Buffer Stream     │  │
│  └────────────┬────────────┘             └───────────────┬───────────────┘  │
│               │                                          │                  │
│               └───────────────────┬──────────────────────┘                  │
│                                   ▼                                         │
│                      ┌─────────────────────────┐                            │
│                      │ Trụ Cột 3: Architecture │                            │
│                      │ • Smart vs Presentation │                            │
│                      │ • Chat vs Cowork Split  │                            │
│                      │ • Spatial BBox Scaling  │                            │
│                      └────────────┬────────────┘                            │
│                                   ▼                                         │
│                      ┌─────────────────────────┐                            │
│                      │ Trụ Cột 4: Verification │                            │
│                      │ • Vitest Unit Tests     │                            │
│                      │ • OCC Conflict Rollback │                            │
│                      │ • Puppeteer Audit       │                            │
│                      └─────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### TRỤ CỘT 1: ĐẶC TẢ UI/UX & DESIGN SYSTEM (DESIGN.MD SPECIFICATION)

#### 1.1. Bảng Token Màu Ngữ Nghĩa Đồng Bộ Tuyệt Đối
Kế thừa hoàn toàn từ `apps/web/src/index.css` và `docs/vi/decided/frontend/landing-page.md`:

| Token CSS | Giá trị Light Mode | Giá trị Dark Mode | Ý nghĩa & Vị trí ứng dụng trong Dashboard |
| :--- | :--- | :--- | :--- |
| `--color-canvas` | `#FAF9F5` (Giấy kem ấm) | `#181715` (Obsidian sâu) | Mặt sàn làm việc chính |
| `--color-surface-soft` | `#F5F0E8` | `#201E1B` (Slate tối) | Nền thanh Taskbar bên trái, ô nhập liệu, pill switch |
| `--color-surface-card` | `#EFE9DE` | `#262420` | Thẻ nổi, khung chat stream, card gợi ý |
| `--color-primary` | `#CC785C` (San hô Coral) | `#CC785C` | Nút Send, icon active, trạng thái đang chạy |
| `--color-accent-amber` | `#E8A55A` (Hổ phách) | `#E8A55A` | Viền highlight Bounding Box, badge cảnh báo tiền đề |
| `--color-accent-teal` | `#5DB8A6` (Xanh ngọc) | `#5DB8A6` | Huy hiệu tài liệu đã xác thực, bước hoàn tất |
| `--color-hairline` | `#E6DFD8` | `#332F28` | Đường phân cách 1px giữa Sidebar và Canvas |
| `--color-ink` | `#141413` | `#F5F3ED` | Tiêu đề chính, tên tác vụ |
| `--color-body` | `#3D3D3A` | `#D1CCC2` | Văn bản đối thoại |
| `--color-muted` | `#6C6A64` | `#9C988F` | Metadata, thời gian, placeholder |

#### 1.2. Phân Cấp Typography Chuẩn Editorial
- **Display Serif (`font-display`):** `Cormorant Garamond` (weight 400–500). Tiêu đề lời chào mừng (`HeroSection`), tiêu đề tác vụ Cowork.
- **Humanist Sans (`font-sans`):** `Inter` (weight 400, 500, 600). Toàn bộ nhãn nút, nội dung chat, bước thực thi.
- **Monospace (`font-mono`):** `JetBrains Mono`. Tọa độ `[x0, y0, x1, y1]`, khối mã nguồn, thời gian xử lý, SHA-256.

#### 1.3. Hệ Thống 5 Trạng Thái Giao Diện Bắt Buộc (5 Interface States)
1. **Default State:** Khung làm việc thoáng đạt, các nút ở độ tương phản chuẩn WCAG AA.
2. **Loading / Skeleton State:** Hiệu ứng Warm Shimmer (`#e8e0d2` $\leftrightarrow$ `#f5f0e8`) cho danh sách phiên và nội dung phản hồi, không layout shift (CLS = 0).
3. **Empty State:** Khi chưa chọn phiên hoặc chưa có tin nhắn: Hiển thị `HeroSection` với ô nhập nổi và 3 thẻ gợi ý hành động.
4. **Error State:** Hiển thị thông báo theo chuẩn RFC 7807 với nút `[Thử lại]` và mã lỗi rõ ràng (`SESSION_NOT_FOUND`, `CONCURRENCY_CONFLICT`).
5. **Active / Highlight State:** Viền hổ phách phát sáng khi trích dẫn được kích hoạt hoặc khi đang kéo rê Split-Pane.

---

### TRỤ CỘT 2: DATA LAYER, STATE MANAGEMENT & TYPESCRIPT CONTRACTS

#### 2.1. Hợp Đồng TypeScript Khép Kín 1-1 Với Backend (`src/types/dashboard.ts`)

```typescript
// Định dạng phiên nghiên cứu
export interface SessionItem {
  id: string; // UUID v4
  title: string;
  document_ids: string[];
  created_at: string;
  updated_at: string;
  version: number;
}

// Định dạng tin nhắn Socratic Chat
export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  is_streaming?: boolean;
  citations?: CitationBadgeData[];
  presupposition_alert?: {
    flawed_premise: string;
    correction: string;
    grounded_bbox: [number, number, number, number, number];
  };
}

export interface CitationBadgeData {
  paper_id: string;
  paper_title: string;
  page: number;
  bbox: [number, number, number, number, number];
}

// Chế độ Cowork: Tác vụ & Kế hoạch thực thi
export interface ExecStep {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "waiting_approval";
  details: string;
}

export interface CoworkArtifact {
  id: string;
  title: string;
  type: "markdown" | "latex" | "json";
  content: string;
  version: string;
  updated_at: string;
}

export interface CoworkTask {
  id: string;
  title: string;
  goal: string;
  status: "draft" | "running" | "waiting_approval" | "completed";
  progress: number;
  steps: ExecStep[];
  artifact?: CoworkArtifact;
}
```

#### 2.2. Phân Tách Server Cache (TanStack Query) vs Client UI State (Zustand)
- **Server Cache (`@tanstack/react-query v5`):**
  - Quản lý danh sách phiên (`useQuery(['sessions'])`).
  - Quản lý lịch sử tin nhắn (`useQuery(['sessions', sessionId, 'messages'])`).
  - Quản lý danh sách tài liệu (`useQuery(['documents'])`).
  - Tự động revalidate khi có thay đổi, quản lý stale time 60s.
- **Client UI State (`zustand` - `useDashboardStore`):**
  - `sidebarState`: `'collapsed'` (52px) vs `'expanded'` (260px).
  - `appMode`: `'chat'` vs `'cowork'`.
  - `activeSessionId`: Chuỗi UUID phiên đang mở.
  - `activeBbox`: Tọa độ Bounding Box đang được highlight `[x0, y0, x1, y1, page]`.
  - `selectedModel`: Model AI hiện tại (Fast vs Deep Reasoning).
  - `effortLevel`: Mức độ suy luận (`'Thấp'` | `'Tiêu chuẩn'` | `'Cao'`).

#### 2.3. Khóa Lạc Quan Chuẩn RFC 9110 (OCC Optimistic Concurrency Control)
- Khi đổi tên phiên, cập nhật ghi chú hoặc chỉnh sửa Artifact:
  - Client đính kèm tiêu đề HTTP `If-Match: "v{version}"`.
  - Nếu máy chủ trả về `HTTP 412 Precondition Failed`: TanStack Query tự động snapshot rollback về trạng thái trước đó, hiển thị thông báo nhẹ: *"Nội dung đã được cập nhật từ phiên khác. Đang làm mới dữ liệu..."* và refetch bản ghi mới nhất.

#### 2.4. Động Cơ Xử Lý SSE Token Buffer Chống Giật Lag (Zero-Jank Stream Engine)
- Khi máy chủ bắn luồng sự kiện SSE từ `POST /api/v1/sessions/{id}/messages`:
  - Không gọi `setState` trên từng ký tự (token) riêng lẻ (tránh bão re-render 100 lần/giây).
  - Sử dụng hàng đợi nội bộ (Queue Buffer) kết hợp `requestAnimationFrame` (rAF) để gom các token nhận được và cập nhật DOM đồng bộ theo chu kỳ quét 60Hz/120Hz của màn hình.

---

### TRỤ CỘT 3: KIẾN TRÚC COMPONENT & TÍCH HỢP BỐ CỤC (LAYOUT INTEGRATION)

```text
apps/web/src/features/dashboard/
├── components/
│   ├── DashboardContainer.tsx         # [SMART] Điều phối toàn cục, kết nối State & URL
│   ├── DashboardTaskbar.tsx           # [PRESENTATION] Sidebar thu phóng (52px <-> 260px)
│   ├── DashboardHeader.tsx            # [PRESENTATION] Thanh header tối giản kèm status
│   ├── DashboardHeroSection.tsx       # [PRESENTATION] Empty State: Greeting + Input Box + 3 Pills
│   ├── DashboardChatInputBox.tsx      # [SMART] Hộp nhập nổi, auto-resize, Model & Mode Switch
│   ├── DashboardChatStreamView.tsx    # [PRESENTATION] Cuộn hội thoại, KaTeX, Code blocks, Citations
│   ├── DashboardCoworkView.tsx        # [SMART] Split-Pane: ExecPlan (Trái) & Artifact Editor (Phải)
│   ├── CitationBadge.tsx              # [PRESENTATION] Huy hiệu trích dẫn học thuật tương tác
│   ├── PresuppositionBanner.tsx       # [PRESENTATION] Cảnh báo tiền đề sai của Socratic Mentor
│   ├── ModelSelectorModal.tsx         # [MODAL] Hộp thoại chọn model & mức độ nỗ lực
│   └── QuickUploadDocModal.tsx        # [MODAL] Modal nạp PDF nhanh tính SHA-256
├── data/
│   └── mockDashboardData.ts           # Dữ liệu mô phỏng chuẩn IEEE & phiên mẫu
├── hooks/
│   ├── useStreamingChat.ts            # Hook điều khiển luồng SSE qua rAF
│   └── useDashboardSessions.ts        # React Query hooks cho sessions & documents
├── stores/
│   ├── useDashboardStore.ts           # Zustand store lưu UI preferences
│   └── useDashboardStore.test.ts      # Unit test cho store
└── types/
    └── dashboard.ts                   # Type contracts khép kín
```

#### Chi Tiết Các Màn Hình & Trải Nghiệm Người Dùng:

1. **Thanh Điều Hướng Thu Phóng (Collapsible Taskbar Rail):**
   - Nút thu/phóng luôn nằm ở vị trí đầu tiên trên cùng (`SidebarToggleIcon`).
   - Khi thu gọn (`52px`): Chỉ hiển thị icon tinh gọn (Logo VeriScholar, Nút New Chat `+`, Chats, Tài liệu, Sổ tay, Code LaTeX, Chuyển theme, Avatar).
   - Khi mở rộng (`260px`): Hiển thị đầy đủ danh sách các phiên nghiên cứu gần đây với tiêu đề gọn gàng, ngày tháng mờ, nút New Chat có chữ rõ nét.

2. **Hộp Nhập Liệu Nổi Trung Tâm (`DashboardChatInputBox`):**
   - Đặt giữa màn hình ở Empty State và ghim cố định ở đáy màn hình khi trong hội thoại Chat.
   - Thanh trượt chế độ dứt khoát: `[ Hỏi đáp (Chat) | Không gian hợp tác (Cowork) ]`.
   - Nút `+` đính kèm bài báo PDF.
   - Dropdown chọn Model học thuật (`Socratic 2.5 Pro` • `Cao`).
   - Nút Micro thu âm giọng nói.
   - Nút Gửi (`ArrowUp`) tự động chuyển màu nổi bật khi có ký tự.

3. **Chế độ Cowork (Bố cục 2 nửa Resizable Split-Pane):**
   - **Cột Trái (40%):** Quản lý mục tiêu công việc, tiến độ từng bước (`Analyze Requirements` $\rightarrow$ `Draft Plan` $\rightarrow$ `Generate Artifact`), và Cổng phê duyệt của con người (`Human Approval Gate` với nút xanh/đỏ dứt khoát).
   - **Cột Phải (60%):** Trình biên tập/xem trước Artifact (Markdown / LaTeX / Tài liệu tổng hợp) có hỗ trợ nút Sao chép và Tải về.

---

### TRỤ CỘT 4: KẾ HOẠCH KIỂM THỬ ĐA TẦNG & VISUAL AUDIT

#### 4.1. Bộ Kiểm Thử Đơn Vị & Tích Hợp (Vitest + React Testing Library)
- `DashboardTaskbar.test.tsx`:
  - Kiểm tra mở rộng/thu gọn sidebar khi bấm nút toggle.
  - Kiểm tra chuyển phiên làm việc khi bấm vào danh sách recent chats.
- `DashboardChatInputBox.test.tsx`:
  - Kiểm tra tự động co giãn chiều cao theo nội dung (`scrollHeight`).
  - Kiểm tra chuyển đổi chế độ giữa `chat` và `cowork`.
  - Kiểm tra submit bằng phím `Enter` (không kèm `Shift`).
- `DashboardChatStreamView.test.tsx`:
  - Kiểm tra render chuẩn xác công thức toán KaTeX.
  - Kiểm tra kích hoạt sự kiện highlight khi click vào `CitationBadge`.
  - Kiểm tra hiển thị `PresuppositionBanner` khi phát hiện tiền đề câu hỏi sai.
- `DashboardCoworkView.test.tsx`:
  - Kiểm tra bấm nút `Phê duyệt` chuyển trạng thái bước từ `waiting_approval` sang `completed`.
- `useDashboardStore.test.ts`:
  - Kiểm tra đồng bộ state UI và LocalStorage.

#### 4.2. Kiểm Định Chất Lượng Bằng Trình Duyệt Tự Động (Puppeteer & Chrome DevTools)
1. **Console Error = 0:** Kiểm tra toàn bộ vòng đời ứng dụng không phát sinh bất kỳ lỗi console hay cảnh báo React nào.
2. **Kiểm Tra Trực Quan Đa Nền (Visual Audit):** Chụp ảnh màn hình đối chiếu và lưu vào thư mục artifacts:
   - `dashboard_taskbar_collapsed_light.png` / `_dark.png`
   - `dashboard_taskbar_expanded_light.png` / `_dark.png`
   - `dashboard_hero_input_light.png` / `_dark.png`
   - `dashboard_chat_stream_light.png` / `_dark.png`
   - `dashboard_cowork_splitpane_light.png` / `_dark.png`
   - `dashboard_mobile_view.png` (375px)

---

### TRỤ CỘT 5: NGHIÊN CỨU & ĐỐI SÁNH QUỐC TẾ (STATE-OF-THE-ART BENCHMARKING)

| Tiêu chí | Claude.ai | Perplexity.ai | NotebookLM | **VeriScholar Dashboard (Đề xuất)** |
| :--- | :--- | :--- | :--- | :--- |
| **Bố cục Sidebar** | Thu gọn rail 56px hoặc mở rộng drawer. | Cố định icon rail bên trái. | Ẩn/hiện danh sách nguồn bên trái. | **Collapsible Rail mượt mà (52px $\leftrightarrow$ 260px)** kế thừa từ `temp/dashboard`. |
| **Hộp nhập liệu** | Nổi giữa màn hình, đính kèm file, chọn model. | Khung tìm kiếm ngang. | Ô nhập chat cố định ở đáy. | **Hộp nhập nổi tích hợp Mode Switcher (Chat vs Cowork) & Model Picker**. |
| **Trích dẫn bằng chứng** | Chỉ ghi text trích dẫn thuần túy. | Huy hiệu số nhỏ `[1]`, hover xem trích đoạn. | Huy hiệu số `[1]`, click mở đoạn trích. | **Huy hiệu tương tác `[Paper • Trang • BBox]` kết hợp nhảy viền Bounding Box quang học**. |
| **Chống Ảo Giác & Nịnh Hót** | Phụ thuộc vào system prompt chung. | Trích xuất web, dễ bị phân tán. | Giới hạn theo nguồn tải lên. | **Cơ chế Socratic Mentor: Thẩm định tiền đề (Presupposition Validation) trước khi trả lời**. |
| **Không gian Hợp tác** | Cửa sổ Artifacts bên phải. | Không có. | Sổ tay ghi chú Studio bên phải. | **Cowork View tích hợp quy trình từng bước & Cổng phê duyệt (Human Approval Gate)**. |

---

## 4. DANH MỤC THAY ĐỔI DỰ KIẾN (PROPOSED CHANGES)

### Component: Frontend Dashboard (`apps/web/src/features/dashboard/`)
- [NEW] `apps/web/src/types/dashboard.ts`
- [NEW] `apps/web/src/features/dashboard/data/mockDashboardData.ts`
- [NEW] `apps/web/src/features/dashboard/api/dashboardApi.ts`
- [NEW] `apps/web/src/features/dashboard/stores/useDashboardStore.ts`
- [NEW] `apps/web/src/features/dashboard/stores/useDashboardStore.test.ts`
- [NEW] `apps/web/src/features/dashboard/hooks/useDashboardQueries.ts`
- [NEW] `apps/web/src/features/dashboard/hooks/useDashboardQueries.test.tsx`
- [NEW] `apps/web/src/features/dashboard/hooks/useStreamingChat.ts`
- [NEW] `apps/web/src/features/dashboard/hooks/useDashboardSessions.ts`
- [NEW] `apps/web/src/components/ui/DashboardErrorBoundary.tsx`
- [NEW] `apps/web/src/components/ui/DashboardErrorBoundary.test.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardSkeleton.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardTaskbar.test.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardHeader.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardHeroSection.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardChatInputBox.test.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardChatStreamView.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardChatStreamView.test.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardCoworkView.tsx`
- [NEW] `apps/web/src/features/dashboard/components/DashboardCoworkView.test.tsx`
- [NEW] `apps/web/src/features/dashboard/components/CitationBadge.tsx`
- [NEW] `apps/web/src/features/dashboard/components/PresuppositionBanner.tsx`
- [NEW] `apps/web/src/features/dashboard/components/ModelSelectorModal.tsx`
- [NEW] `apps/web/src/features/dashboard/components/QuickUploadDocModal.tsx`
- [MODIFY] `apps/web/src/lib/api-client.ts` (JWT injection, 204 No Content, ETag)
- [MODIFY] `apps/api/src/api/__init__.py` (CORSMiddleware cho frontend-backend integration)
- [MODIFY] `apps/web/src/features/dashboard/components/DashboardPage.tsx` (Tích hợp `DashboardContainer`)
- [MODIFY] `apps/web/src/features/dashboard/components/DashboardPage.test.tsx` (Cập nhật suite với QueryClientProvider)
- [MODIFY] `apps/web/.env.example` (Bổ sung `VITE_ENABLE_MOCK_DASHBOARD=true`)
- [NEW] `docs/vi/decided/frontend/dashboard.md` (Tài liệu kiến trúc chính thức sau khi duyệt)

---

## 5. KẾ HOẠCH XÁC MINH (VERIFICATION PLAN)

### Automated Tests
1. Chạy toàn bộ kiểm thử đơn vị frontend:
   ```bash
   pnpm --prefix apps/web test
   ```
2. Kiểm tra linter và typecheck:
   ```bash
   pnpm --prefix apps/web lint
   pnpm --prefix apps/web exec tsc -b
   ```
3. Kiểm tra build sản phẩm:
   ```bash
   pnpm --prefix apps/web build
   ```

### Manual & Visual Verification
1. Khởi chạy dev server: `pnpm --prefix apps/web dev --port 5173`.
2. Truy cập `http://localhost:5173/dashboard`.
3. Kiểm tra hành vi đóng/mở Taskbar bên trái: Chuyển đổi trơn tru giữa 52px và 260px.
4. Kiểm tra gõ tin nhắn và gửi thử: Luồng streaming chữ mượt mà qua rAF và fetchEventSource.
5. Kiểm tra chuyển tab sang `Cowork`: Bố cục chia đôi hiển thị rõ nét, bấm `Phê duyệt` hoàn thành tác vụ.
6. Kiểm tra chuyển đổi Dark / Light mode: Giữ nguyên vẹn độ tương phản Warm-Canvas Editorial.

---

## 6. KẾT QUẢ NGHIỆM THU & QUALITY GATE CHECKLIST

| Tiêu chí chất lượng | Công cụ kiểm chuẩn | Kết quả đạt được | Trạng thái |
| :--- | :--- | :--- | :--- |
| **Frontend Unit Tests** | Vitest (In-memory, TanStack Query & OCC) | **20/20 test suites, 67/67 tests passed** (100%) |  PASS |
| **Backend Integration Tests** | Pytest (`pytest apps/api/tests packages/core/tests`) | **269 passed, 10 skipped, 0 failures** |  PASS |
| **Code Style & Linting** | Oxlint (`pnpm lint`) | **0 warnings, 0 errors** trên 92 tệp nguồn |  PASS |
| **Python Formatting & Lint** | Ruff (`uv run ruff check . && uv run ruff format --check .`) | **All checks passed**, 171 tệp chuẩn PEP 8 |  PASS |
| **TypeScript Type Checking** | TypeScript Compiler (`tsc -b`) | **0 errors, strict typing** |  PASS |
| **Production Bundle Build** | Vite v8.2.2 (`pnpm build`) | **Bundle thành công trong 1.12s**, KaTeX fonts nhúng chuẩn |  PASS |
| **Visual Audit & Console Verification** | Puppeteer Chrome Headless (1440x900) | **0 console errors**, network calls reach backend API |  PASS |

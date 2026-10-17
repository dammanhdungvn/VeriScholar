# Cấu Trúc Thư Mục Frontend Chuẩn Production (`apps/web`)

Tài liệu này định nghĩa cấu trúc phân bổ mã nguồn, quy ước đặt tên và luồng điều hướng dữ liệu cho ứng dụng Web Client của nền tảng **VeriScholar** tại thư mục `apps/web/`.

---

## 1. SƠ ĐỒ CÂY THƯ MỤC TOÀN DIỆN (PROJECT DIRECTORY TREE)

```text
apps/web/
├── public/                     # Tệp tĩnh, favicon, PDF.js Web Worker scripts
│   └── pdf.worker.min.mjs      # Worker giải mã PDF đa luồng không chặn Main Thread
├── src/
│   ├── app/                    # Điểm khởi tạo ứng dụng, định tuyến và tầng bọc ngữ cảnh
│   │   ├── App.tsx             # Root component gắn kết Router và Providers
│   │   ├── routes.tsx          # Bảng định tuyến ứng dụng (React Router v7)
│   │   └── providers/          # Các tầng Provider toàn cục
│   │       ├── QueryProvider.tsx   # TanStack Query Client cấu hình cache & retry
│   │       ├── ThemeProvider.tsx   # Dark/Light/Academic Paper Mode Context
│   │       └── ToastProvider.tsx   # Sonner Toast container
│   │
│   ├── assets/                 # Vector icons, logos, học thuật assets
│   │
│   ├── components/             # Thành phần giao diện dùng chung (Shared Components)
│   │   ├── ui/                 # Headless primitives từ Radix UI & shadcn
│   │   │   ├── button.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── badge.tsx
│   │   │   └── scroll-area.tsx
│   │   ├── layout/             # Khung sườn bố cục giao diện
│   │   │   ├── AppHeader.tsx       # Thanh điều hướng trên cùng (Logo, User, Theme)
│   │   │   ├── AppSidebar.tsx      # Thanh bên quản lý kho bài báo & lịch sử phiên
│   │   │   └── SplitWorkspace.tsx  # Bộ chia đôi màn hình react-resizable-panels
│   │   └── shared/             # Thành phần bổ trợ đa dụng
│   │       ├── ErrorBoundary.tsx   # Bắt ngoại lệ React, hiển thị màn hình fallback
│   │       ├── LoadingOverlay.tsx  # Spinner tải trang học thuật
│   │       └── MarkdownRenderer.tsx# Trình hiển thị Markdown + KaTeX LaTeX Math
│   │
│   ├── features/               # Cấu trúc module hóa theo chức năng nghiệp vụ (Feature-Driven)
│   │   ├── library/            # Quản lý kho bài báo cá nhân (Library Management)
│   │   │   ├── components/
│   │   │   │   ├── DocumentCard.tsx       # Thẻ hiển thị bài báo, metadata & tags
│   │   │   │   ├── DocumentUploadModal.tsx# Hộp thoại kéo thả tệp PDF tải lên
│   │   │   │   └── DocumentListTable.tsx  # Bảng danh mục bài báo kèm phân trang
│   │   │   ├── hooks/
│   │   │   │   ├── useDocuments.ts        # TanStack Query hook lấy danh sách bài báo
│   │   │   │   └── useUploadDocument.ts   # Mutation hook tải lên tài liệu mới
│   │   │   └── types/
│   │   │
│   │   ├── reader/             # Không gian đọc sâu & PDF Canvas Engine (Deep Reading)
│   │   │   ├── components/
│   │   │   │   ├── PdfCanvasViewer.tsx    # Trình vẽ PDF.js Canvas + Text Layer
│   │   │   │   ├── BboxHighlightLayer.tsx # Lớp phủ vẽ khung vàng Bounding Box
│   │   │   │   ├── DocumentTabBar.tsx     # Thanh tab chuyển đổi nhanh 1 - 5 bài báo
│   │   │   │   ├── ViewportControls.tsx   # Thanh điều khiển Zoom, xoay trang, nhảy trang
│   │   │   │   └── TableViewerModal.tsx   # Xem phóng to bảng biểu vắt trang
│   │   │   ├── hooks/
│   │   │   │   ├── usePdfDocument.ts      # Quản lý vòng đời tải tệp PDF từ API
│   │   │   │   ├── useBboxScaler.ts       # Tính toán ma trận co giãn tọa độ highlight
│   │   │   │   └── useViewportPersistence.ts # Debounced auto-save vị trí đọc (OCC)
│   │   │   └── types/
│   │   │
│   │   ├── chat/               # Trợ lý đối thoại AI & SSE Streaming (Socratic Mentor)
│   │   │   ├── components/
│   │   │   │   ├── ChatPanel.tsx          # Khung đối thoại chính
│   │   │   │   ├── MessageTurnItem.tsx    # Hiển thị cặp câu hỏi và câu trả lời
│   │   │   │   ├── CitationBadge.tsx      # Huy hiệu trích dẫn [Paper • Trang • BBox]
│   │   │   │   ├── ThinkingBlock.tsx      # Khối hiển thị chuỗi suy luận (Thinking Mode)
│   │   │   │   └── PromptInputBox.tsx     # Ô nhập câu hỏi kèm phím tắt Cmd+Enter
│   │   │   ├── hooks/
│   │   │   │   ├── useChatHistory.ts      # Lấy lịch sử hội thoại phân trang (GET)
│   │   │   │   ├── useChatStream.ts       # Đọc dòng SSE thời gian thực (POST)
│   │   │   │   └── useClearChatHistory.ts # Xóa lịch sử phiên hội thoại (Idempotent 204)
│   │   │   └── types/
│   │   │
│   │   ├── notes/              # Sổ tay nghiên cứu & Tổng hợp tri thức (Synthesis & Recall)
│   │   │   ├── components/
│   │   │   │   ├── NoteCard.tsx           # Thẻ ghi chú cá nhân kèm liên kết bài báo
│   │   │   │   ├── SynthesisDigest.tsx    # Bảng tổng hợp tri thức tự động
│   │   │   │   └── ActiveRecallQuiz.tsx   # Thẻ câu hỏi tự vấn / Flashcard
│   │   │   ├── hooks/
│   │   │   └── types/
│   │   │
│   │   └── sessions/           # Vòng đời phiên nghiên cứu & Xuất dữ liệu
│   │       ├── components/
│   │       │   ├── SessionHistoryList.tsx # Danh sách phiên làm việc gần đây
│   │       │   ├── SessionSettingsModal.tsx # Đổi tên, cấu hình OCC version
│   │       │   └── ExportBundleDialog.tsx # Xuất gói ngoại tuyến .zip (#56)
│   │       ├── hooks/
│   │       └── types/
│   │
│   ├── hooks/                  # Các Custom Hooks dùng chung toàn ứng dụng
│   │   ├── useDebounce.ts      # Trì hoãn thực thi (dùng cho tìm kiếm, auto-save)
│   │   ├── useEventListener.ts # Lắng nghe sự kiện bàn phím/window an toàn
│   │   └── useLocalStorage.ts  # Đồng bộ trạng thái vào LocalStorage có kiểu dữ liệu
│   │
│   ├── lib/                    # Các tiện ích hạ tầng mạng và định dạng
│   │   ├── apiClient.ts        # Axios/Fetch cấu hình base URL, JWT Interceptor
│   │   ├── sseClient.ts        # Bộ bọc @microsoft/fetch-event-source
│   │   ├── pdfUtils.ts         # Tiện ích tính toán ma trận tọa độ Bounding Box
│   │   └── utils.ts            # Hàm bổ trợ chung (cn helper ghép class)
│   │
│   ├── stores/                 # Zustand Global UI Stores
│   │   ├── useWorkspaceStore.ts# Lưu tỷ lệ màn hình, tab đang mở, trạng thái sidebar
│   │   └── useReaderStore.ts   # Lưu zoomRatio, currentPage, activeCitationId
│   │
│   └── types/                  # Khai báo kiểu dữ liệu TypeScript toàn cục (Mapping API)
│       ├── api.ts              # Single & Paginated Envelopes, Error Schema
│       ├── document.ts         # Schema Document, Chunk, Structure
│       ├── session.ts          # Schema ResearchSession, ViewportState
│       └── chat.ts             # Schema SessionTurn, Citation, SSE Event Types
│
├── index.html                  # Điểm neo HTML chính, nạp phông chữ Inter & KaTeX CSS
├── package.json                # Danh mục thư viện phụ thuộc và scripts
├── tsconfig.json               # Cấu hình TypeScript nghiêm ngặt (Strict Mode)
└── vite.config.ts              # Cấu hình Vite, Alias đường dẫn `@/*` trỏ tới `src/*`
```

---

## 2. NGUYÊN TẮC PHÂN TÁCH VAI TRÒ CỦA TỪNG TẦNG (SEPARATION OF CONCERNS)

### 2.1. `app/` (Application Shell & Routing)
- Chỉ đảm nhiệm việc khởi chạy ứng dụng, gắn các Provider (React Query, Theme, Toast) và định tuyến đường dẫn URL.
- Tuyệt đối không chứa logic nghiệp vụ tính toán hoặc gọi trực tiếp API tại tầng này.

### 2.2. `features/<module>/` (Feature-Driven Modularization)
- Mỗi module nghiệp vụ lớn (`library`, `reader`, `chat`, `notes`, `sessions`) là một thực thể độc lập có cấu trúc khép kín gồm:
  - `components/`: Các thành phần giao diện phục vụ riêng cho module đó.
  - `hooks/`: Các logic hook xử lý dữ liệu và mutation dành riêng cho module.
  - `types/`: Kiểu dữ liệu đặc thù của module.
- **Quy tắc ranh giới (Module Boundary Invariant):** Không được import chéo component nội bộ giữa các module với nhau nếu không thông qua file `index.ts` công khai của module đó.

### 2.3. `components/ui/` (Headless UI Primitives)
- Chỉ chứa các thành phần giao diện nguyên tử, phi nghiệp vụ (Agnostic UI) như nút bấm (`button`), hộp thoại (`dialog`), thanh cuộn (`scroll-area`).
- Nhận dữ liệu qua `props` thuần túy, không được phụ thuộc vào bất kỳ Zustand store hay API hook nào.

### 2.4. `stores/` (Ephemeral Client State)
- Chỉ lưu trữ các trạng thái giao diện tạm thời cần chia sẻ giữa các panel khác nhau (ví dụ: người dùng nhấp vào trích dẫn ở Chat Panel -> Reader Store cập nhật `activeCitationId` -> PDF Canvas Viewer cuộn đến trang tương ứng).
- Không lạm dụng Zustand để lưu trữ dữ liệu danh mục bài báo hay lịch sử hội thoại (các dữ liệu này bắt buộc thuộc quyền quản lý của TanStack Query).

---

## 3. LUỒNG DỮ LIỆU ĐIỀU PHỐI HAI CHIỀU (DATA FLOW ARCHITECTURE)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND FASTAPI (/api/v1)                          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP REST & SSE Stream
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TẦNG MẠNG & CLIENT HOOKS                         │
│   • apiClient.ts (Axios / TanStack Query) ──> Lấy dữ liệu & Caching         │
│   • sseClient.ts (@microsoft/fetch-event-source) ──> Nhận luồng SSE         │
└───────────────────────┬─────────────────────────────┬───────────────────────┘
                        │ Cập nhật Server Cache        │ Stream Token Buffer (rAF)
                        ▼                             ▼
┌───────────────────────────────────┐     ┌───────────────────────────────────┐
│     SERVER STATE (React Query)    │     │       CLIENT UI STATE (Zustand)   │
│ • Danh mục bài báo trong thư viện │     │ • Zoom Level, Active Document Tab │
│ • Lịch sử phiên nghiên cứu        │     │ • Tỷ lệ chia màn hình Split-Pane  │
│ • Lịch sử tin nhắn đã lưu         │     │ • Active Citation & Highlight ID  │
└─────────────────┬─────────────────┘     └─────────────────┬─────────────────┘
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       │ Selectors & Hooks
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WORKSPACE LAYOUT (react-resizable-panels)             │
│                                                                             │
│  ┌──────────────────────────────┐        ┌──────────────────────────────┐  │
│  │     PANEL TRÁI: PDF READER   │        │     PANEL PHẢI: AI WORKSPACE │  │
│  │                              │        │                              │  │
│  │ • Document Tabs (1 - 5 bài)  │   ◄──► │ • Chat & Socratic Mentor     │  │
│  │ • PDF.js Canvas + Text Layer │  Đồng  │ • SSE Streaming Markdown     │  │
│  │ • Bounding Box Overlay Layer │  bộ    │ • LaTeX Formula Render       │  │
│  │ • Auto-save Viewport (OCC)   │  tọa   │ • Interactive Citation Badges│  │
│  │                              │  độ    │ • Notes & Knowledge Digest   │  │
│  └──────────────────────────────┘        └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. QUY ƯỚC ĐẶT TÊN & ĐỊNH DANH (NAMING CONVENTIONS)

1. **Thư mục (Directories):** Đặt theo định dạng `kebab-case` (ví dụ: `components/ui`, `document-card`, `features/reader`).
2. **Tệp Component (React Components):** Đặt theo định dạng `PascalCase.tsx` (ví dụ: `PdfCanvasViewer.tsx`, `CitationBadge.tsx`).
3. **Tệp Hooks:** Bắt đầu bằng tiền tố `use` theo định dạng `camelCase.ts` (ví dụ: `useChatStream.ts`, `useBboxScaler.ts`).
4. **Tệp Tiện ích & Hỗ trợ:** Đặt theo định dạng `camelCase.ts` (ví dụ: `apiClient.ts`, `pdfUtils.ts`).
5. **Types & Interfaces:** Đặt theo định dạng `PascalCase` và không dùng tiền tố `I` (ví dụ: `SessionResponseData`, `CitationBoundingBox`, `ViewportCoordinates`).

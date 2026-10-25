# Cấu Trúc Thư Mục Frontend Chuẩn Production (`apps/web`)

Tài liệu này định nghĩa cấu trúc phân bổ mã nguồn, quy ước đặt tên và luồng điều hướng dữ liệu cho ứng dụng Web Client của nền tảng **VeriScholar** tại thư mục `apps/web/`, đồng bộ với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 1. BẢNG ĐỊNH TUYẾN MVP CHUẨN (`routes.tsx`)

Ứng dụng Frontend chỉ bao gồm 4 không gian làm việc chính (cùng các trang xác thực công khai):
- `/dashboard` & `/dashboard/:sessionId`: Không gian Đọc sâu đa bài báo (1–5 PDF), Hỏi đáp Hybrid RAG + GraphRAG, Sổ tay Ghi chú và Tham khảo.
- `/discovery`: Tìm kiếm và khám phá bài báo học thuật ngoài (Semantic Scholar, arXiv, Crossref, PubMed, Exa).
- `/library`: Quản lý Thư viện cá nhân (Cây thư mục phân cấp và danh sách bài báo đã Star).
- `/writing` & `/writing/:draftId`: Không gian Soạn thảo LaTeX 3 cột (Code Editor, Live PDF Preview, AI Writing Assistant).

---

## 2. SƠ ĐỒ CÂY THƯ MỤC TOÀN DIỆN (PROJECT DIRECTORY TREE)

```text
apps/web/
├── public/                     # Tệp tĩnh, favicon, PDF.js Web Worker scripts
│   └── pdf.worker.min.mjs      # Worker giải mã PDF đa luồng không chặn Main Thread
├── src/
│   ├── app/                    # Điểm khởi tạo ứng dụng, định tuyến và tầng bọc ngữ cảnh
│   │   ├── App.tsx             # Root component gắn kết Router và Providers
│   │   └── routes.tsx          # Bảng định tuyến ứng dụng chuẩn MVP (4 routes chính)
│   │
│   ├── components/             # Thành phần giao diện dùng chung (Shared Components)
│   │   ├── ui/                 # Headless primitives từ Radix UI & shadcn
│   │   └── layout/             # Khung sườn bố cục giao diện
│   │
│   ├── features/               # Cấu trúc module hóa theo chức năng nghiệp vụ (Feature-Driven)
│   │   ├── auth/               # Xác thực JWT, Google GIS & Hồ sơ Học giả 3 Tabs
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   ├── SocialAuthButtons.tsx
│   │   │   │   └── AccountSettingsModal.tsx
│   │   │   ├── hooks/
│   │   │   └── stores/
│   │   │
│   │   ├── dashboard/          # Không gian Đọc sâu & Hỏi đáp đa bài báo (/dashboard)
│   │   │   ├── components/
│   │   │   │   ├── DashboardTaskbar.tsx        # Taskbar 4 mục điều hướng + Lịch sử phiên đọc
│   │   │   │   ├── DashboardContainer.tsx      # Điều phối Standby Dropzone & Split Workspace
│   │   │   │   ├── DashboardWorkspace.tsx      # Split-pane PDF Reader & Chat/Notes/Summary
│   │   │   │   ├── DashboardChatStreamView.tsx # Luồng đối thoại SSE kèm Citation Badges
│   │   │   │   └── DashboardChatInputBox.tsx   # Ô nhập câu hỏi kèm nút Suy luận sâu
│   │   │   └── stores/
│   │   │       └── useDashboardStore.ts
│   │   │
│   │   ├── discovery/          # Tìm kiếm & Khám phá bài báo học thuật ngoài (/discovery)
│   │   │   └── pages/
│   │   │       └── DiscoveryPage.tsx
│   │   │
│   │   ├── documents/          # Quản trị tài liệu PDF & Hộp thoại chọn bài báo
│   │   │   ├── api/
│   │   │   │   └── documentsApi.ts
│   │   │   └── components/
│   │   │       └── DocumentLibraryModal.tsx
│   │   │
│   │   ├── library/            # Quản lý kho bài báo cá nhân & Thư mục (/library)
│   │   │   ├── api/
│   │   │   │   └── foldersApi.ts
│   │   │   ├── components/
│   │   │   │   ├── FolderTreeView.tsx
│   │   │   │   └── LibraryWorkspaceView.tsx
│   │   │   └── hooks/
│   │   │       └── useFolderQueries.ts
│   │   │
│   │   ├── notes/              # Sổ tay ghi chú thông minh (Smart Notes)
│   │   │   ├── api/
│   │   │   │   └── notesApi.ts
│   │   │   ├── components/
│   │   │   │   └── NotesPanelContainer.tsx
│   │   │   └── hooks/
│   │   │       └── useNotesQuery.ts
│   │   │
│   │   ├── reader/             # PDF Canvas Engine, Reference Drawer & Citation Graph
│   │   │   ├── components/
│   │   │   │   ├── PdfViewport.tsx
│   │   │   │   ├── BoundingBoxOverlay.tsx
│   │   │   │   ├── ViewportControls.tsx
│   │   │   │   ├── SmartReferenceDrawer.tsx
│   │   │   │   └── CitationGraphModal.tsx
│   │   │   └── stores/
│   │   │       └── useReaderStore.ts
│   │   │
│   │   ├── sessions/           # Vòng đời phiên nghiên cứu đa bài báo (1 - 5 bài)
│   │   │   ├── api/
│   │   │   │   └── sessionsApi.ts
│   │   │   └── hooks/
│   │   │       └── useSessionsQuery.ts
│   │   │
│   │   └── writing/            # Không gian Soạn thảo LaTeX 3 cột (/writing)
│   │       ├── api/
│   │       │   └── draftsApi.ts
│   │       ├── components/
│   │       │   ├── WritingWorkspace.tsx
│   │       │   ├── WritingHeaderBar.tsx
│   │       │   ├── WritingSidebar.tsx
│   │       │   ├── WritingEditorPane.tsx
│   │       │   ├── WritingPreviewPane.tsx
│   │       │   ├── WritingAssistantPane.tsx
│   │       │   └── DraftAssetManagementModal.tsx
│   │       └── stores/
│   │           └── useWritingStore.ts
│   │
│   ├── lib/                    # Các tiện ích hạ tầng mạng và định dạng
│   │   ├── api-client.ts       # Fetch/Axios wrapper cấu hình base URL, JWT Interceptor
│   │   └── utils.ts            # Hàm bổ trợ chung (cn helper ghép class)
│   │
│   └── types/                  # Khai báo kiểu dữ liệu TypeScript toàn cục
│       └── dashboard.ts
│
├── index.html                  # Điểm neo HTML chính
├── package.json                # Danh mục thư viện phụ thuộc và scripts
├── tsconfig.json               # Cấu hình TypeScript nghiêm ngặt (Strict Mode)
└── vite.config.ts              # Cấu hình Vite, Alias đường dẫn `@/*` trỏ tới `src/*`
```

---

## 3. NGUYÊN TẮC PHÂN TÁCH VAI TRÒ CỦA TỪNG TẦNG (SEPARATION OF CONCERNS)

1. **`app/` (Application Shell & Routing):** Chỉ đảm nhiệm việc khởi chạy ứng dụng, gắn các Provider và định tuyến URL chuẩn MVP.
2. **`features/<module>/` (Feature-Driven Modularization):** Mỗi module nghiệp vụ có cấu trúc khép kín gồm `api/`, `components/`, `hooks/`, `stores/`, `types/`.
3. **`components/ui/` (Headless UI Primitives):** Chỉ chứa các thành phần giao diện nguyên tử, phi nghiệp vụ.
4. **Zustand Stores vs. TanStack Query:** Zustand quản lý trạng thái UI tức thời (tab đang mở, vị trí cuộn, tỷ lệ zoom, vùng chọn văn bản), trong khi TanStack Query quản lý dữ liệu bất đồng bộ từ máy chủ.

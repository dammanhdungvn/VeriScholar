# Session CRUD, Mermaid Caching, and Reader UX Refinements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục triệt để lỗi Mermaid bị đen khi cuộn PDF bằng SVG in-memory cache, hoàn thiện đầy đủ CRUD Session (Rename, Delete) với API backend, thêm cơ chế Read/Unread và Click-outside menu `...`, căn chỉnh icon Workspace ngang hàng, thống nhất header Socratic Assistant, và cập nhật thanh công cụ đọc PDF (Lưu bài báo trong menu "Tùy chọn", nút đóng tab `✕` hover đỏ).

**Architecture:** Sử dụng kiến trúc bộ nhớ đệm module-level Map cho SVG Mermaid nhằm đạt thời gian hiển thị 0ms khi re-render; tích hợp `sessionsApi` với Optimistic Concurrency Control (OCC ETag) cho chức năng đổi tên và xóa phiên; quản lý trạng thái unread cục bộ kết hợp UI indicator san hô; cấu trúc lại layout Header và Tabbar theo tiêu chuẩn Radical Minimalism (Rule 6).

**Tech Stack:** React 19, TypeScript, Vitest, React Testing Library, Mermaid.js, Tailwind CSS, Lucide React, FastAPI, SQLAlchemy.

**Spec:** [`docs/superpowers/specs/2026-10-28-session-crud-and-reader-ux-refinements-design.md`](../specs/2026-10-28-session-crud-and-reader-ux-refinements-design.md)

## Global Constraints

- Tuân thủ 100% 4 Cổng Xác Minh Bắt Buộc: Ruff (Cổng 1), Pytest (Cổng 2), Vitest (Cổng 3), Build (Cổng 4).
- Kiến trúc lục giác bất biến: Không sửa đổi trái phép `packages/core/`.
- Tối giản cấp tiến (Rule 6): Loại bỏ các chi tiết thừa thãi, badge cồng kềnh, không để lặp lại tiêu đề Assistant.
- Tự động đồng bộ VPS sau mỗi commit có kiểm thử thành công (Rule 9).

## Review Focus

1. **Mermaid Cache Hit on Mount:** Khi cuộn PDF kích hoạt re-render liên tục, `MermaidRenderer` phải đọc ngay SVG từ `mermaidSvgCache` mà không tạo ra bất kỳ frame nào hiển thị khung đen rỗng.
2. **Session Rename OCC Handling:** Gọi `getSessionDetail` lấy ETag trước khi gọi `updateSessionMetadata` để đảm bảo không bị lỗi 428 Precondition Required.
3. **Session Delete Navigation:** Khi xóa phiên đang kích hoạt (`activeSessionId === id`), điều hướng an toàn về `/dashboard` và xóa messages rác.
4. **Click-outside Context Menu:** Click bất kỳ vị trí nào bên ngoài dropdown context menu `...` phải đóng menu ngay lập tức.
5. **Read/Unread Toggle:** Trạng thái chưa đọc hiển thị chấm tròn màu san hô; khi mở phiên hoặc bấm "Đánh dấu đã đọc" thì chấm tròn biến mất.

---

### Task 1: Mermaid In-Memory SVG Cache & Memoization

**Files:**
- Modify: `apps/web/src/components/shared/MermaidRenderer.tsx`
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx:480-498`
- Test: `apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx`

**Interfaces:**
- Consumes: `chart: string`, `className?: string`
- Produces: `MermaidRenderer` với `mermaidSvgCache` module-level Map và `React.memo`

- [ ] **Step 1: Write failing test for Mermaid caching behavior**

Thêm test case kiểm tra bộ nhớ đệm `mermaidSvgCache` khởi tạo SVG ngay lập tức trên render tiếp theo trong `MermaidExportRenderer.test.tsx`:
```tsx
it("instantly serves cached SVG on re-render without blanking", async () => {
  const chartCode = "graph TD\n  A --> B";
  const { rerender } = render(<MermaidRenderer chart={chartCode} />);
  await waitFor(() => {
    expect(screen.getByText("A")).toBeInTheDocument();
  });
  // Rerender with same code should retain SVG synchronously without blank state
  rerender(<MermaidRenderer chart={chartCode} />);
  expect(screen.getByText("A")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx`
Expected: FAIL or passes if partly mocked.

- [ ] **Step 3: Implement SVG Cache & Memoization in `MermaidRenderer.tsx` and `AcademicMarkdownRenderer.tsx`**

1. Trong `MermaidRenderer.tsx`:
   - Thêm `const mermaidSvgCache = new Map<string, string>();`
   - Khởi tạo `useState<string>(() => mermaidSvgCache.get(cacheKey) || "");`
   - Trong `useEffect`, kiểm tra nếu đã có trong cache thì gán `setSvgContent(cached)` và return sớm, không gọi `mermaid.render()`.
   - Khi render thành công, lưu vào `mermaidSvgCache.set(cacheKey, svg);`.
   - Xuất khẩu với `export const MermaidRenderer = React.memo(MermaidRendererComponent);`.
2. Trong `AcademicMarkdownRenderer.tsx`:
   - Gán `key={codeString}` cho `<MermaidRenderer chart={codeString} />`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add apps/web/src/components/shared/MermaidRenderer.tsx apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx
git commit -m "fix(reader): add mermaid in-memory svg cache to prevent blanking on pdf scroll"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 2: Unified Socratic Assistant Header

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1053-1096`
- Test: `apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx`

**Interfaces:**
- Consumes: `isAssistantOpen`, `setIsAssistantOpen`, `activeRightTab`
- Produces: Header cố định trên cùng hiển thị `[ ✨ ] Socratic Assistant` + `✕`, xóa bỏ khối Header Badge lặp lại bên dưới.

- [ ] **Step 1: Write failing test asserting Socratic Assistant header layout**

Trong `AssistantPanelUnification.test.tsx`, kiểm tra tiêu đề `Socratic Assistant` nằm trong `<header>` và không có khối badge lặp lại:
```tsx
it("renders Socratic Assistant in sticky header and removes duplicate scroll badge", () => {
  renderWithClient(<DashboardWorkspace initialAssistantOpen={true} />);
  const header = screen.getByRole("banner");
  expect(header).toHaveTextContent("Socratic Assistant");
  expect(screen.queryByTestId("chat-scroll-header-badge")).toBeNull();
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx`
Expected: FAIL

- [ ] **Step 3: Update `DashboardWorkspace.tsx`**

1. Trong `<header className="h-11 px-3 ...">`:
   - Bổ sung `<h2 className="font-serif font-bold text-xs sm:text-sm text-ink dark:text-[#f3f2ef] leading-tight">Socratic Assistant</h2>` bên cạnh icon Sparkles.
2. Trong khung cuộn tin nhắn chat:
   - Xóa bỏ hoàn toàn khối `Header Badge` (dòng 1084-1096).

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 2**

```bash
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx
git commit -m "refactor(assistant): unify socratic assistant header and eliminate duplicate badge"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 3: Workspace Header Layout (Horizontal Icon Alignment)

**Files:**
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx:194-201`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

**Interfaces:**
- Consumes: `isDark`
- Produces: Tiêu đề `Workspace` nằm ngang hàng bên phải icon `AcademicLogo` (`flex-row items-center justify-center gap-3`)

- [ ] **Step 1: Write failing test verifying horizontal header layout**

Trong `UnifiedHeroWorkspace.test.tsx`:
```tsx
it("renders workspace logo horizontally aligned with the Workspace title", () => {
  const { container } = render(
    <UnifiedHeroWorkspace
      inputText=""
      onChangeText={vi.fn()}
      onSendChat={vi.fn()}
      onIngestFile={vi.fn()}
      onOpenPaper={vi.fn()}
    />
  );
  const titleContainer = container.querySelector(".workspace-header-title");
  expect(titleContainer).toHaveClass("flex-row");
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`
Expected: FAIL

- [ ] **Step 3: Update `UnifiedHeroWorkspace.tsx`**

Cập nhật khối tiêu đề:
```tsx
<div className="workspace-header-title flex flex-row items-center justify-center gap-3 mb-6">
  <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white dark:bg-[#24221f] border border-[#e5dfd4] dark:border-[#38332c] p-1.5 shadow-xs flex items-center justify-center shrink-0">
    <AcademicLogo size="sm" inverted={isDark} showWordmark={false} />
  </div>
  <h1 className="font-sans text-2xl sm:text-3xl md:text-4xl tracking-tight text-ink dark:text-[#f7f5ef] font-semibold">
    Workspace
  </h1>
</div>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 3**

```bash
git add apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx
git commit -m "style(dashboard): align workspace logo horizontally with workspace title"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 4: Session CRUD, Click-Outside Menu, and Read/Unread Status

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`

**Interfaces:**
- Consumes: `sessionsApi.getSessionDetail`, `sessionsApi.updateSessionMetadata`, `sessionsApi.deleteSession`
- Produces:
  - Inline input rename session với hotkeys Enter/Esc.
  - Xóa session có confirm dialog và điều hướng nếu session đang active.
  - Read/Unread toggle & visual coral dot.
  - Click-outside hook đóng menu context.

- [ ] **Step 1: Write failing tests for Session CRUD, Click-outside, and Unread indicator**

Trong `DashboardTaskbar.test.tsx`:
```tsx
it("closes context menu when clicking outside", async () => { ... });
it("allows renaming a session via inline input and calls sessionsApi", async () => { ... });
it("deletes session and invalidates sessions cache", async () => { ... });
it("shows unread coral indicator for unread sessions and toggles status", async () => { ... });
```

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement features in `DashboardTaskbar.tsx`**

1. Click-outside: `useRef` gắn vào menu ngữ cảnh và `document.addEventListener("mousedown", handleClickOutside)`.
2. Inline rename: State `editingSessionId`, `editingTitle`; khi submit gọi `sessionsApi.getSessionDetail` lấy ETag và gọi `sessionsApi.updateSessionMetadata`.
3. Xóa session: State `deletingSessionId`, modal xác nhận nhỏ gọn, gọi `sessionsApi.deleteSession` và điều hướng về `/dashboard` nếu đang active.
4. Read/Unread: State `unreadSessionIds` đồng bộ với `localStorage`, hiển thị `<span className="w-2 h-2 rounded-full bg-coral-500 shrink-0" />` khi chưa đọc; menu `...` hiển thị "Đánh dấu đã đọc" hoặc "Đánh dấu chưa đọc". Khi click mở session, tự động bỏ trạng thái unread.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 4**

```bash
git add apps/web/src/features/dashboard/components/DashboardTaskbar.tsx apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx
git commit -m "feat(taskbar): implement session rename, delete, read-unread indicators, and click-outside dismissal"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 5: PDF Tabbar Close Icon Hover Red & Viewport "Tùy chọn" Menu Bookmark Controls

**Files:**
- Modify: `apps/web/src/features/reader/components/DocumentTabBar.tsx`
- Modify: `apps/web/src/features/reader/components/ViewportOverflowMenu.tsx`
- Modify: `apps/web/src/features/reader/components/ViewportControls.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
- Test: `apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx`
- Test: `apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx`

**Interfaces:**
- Consumes: `onCloseDocument`, `handleToggleStar`, `effectiveDocuments`
- Produces:
  - Tab PDF không còn Star, nút đóng tab là `✕` hover đỏ (`hover:text-rose-600 hover:bg-rose-500/10`).
  - Menu "Tùy chọn" (`ViewportOverflowMenu`) có tùy chọn "Lưu vào kho yêu thích" / "Bỏ lưu bài báo" kết nối với `handleToggleStar`.

- [ ] **Step 1: Write failing tests for tab close button hover style and viewport overflow bookmark menu item**

Trong `DocumentTabBar.test.tsx` và `ViewportControlsCleanup.test.tsx`:
```tsx
it("renders tab close button with X icon and does not render star on tab", () => {
  // Star icon must not be in document tab
  // Tab close button has X and hover:text-rose-600
});
it("renders save bookmark option inside Tùy chọn overflow menu", () => {
  // ViewportOverflowMenu includes 'Lưu vào kho yêu thích' / 'Bỏ lưu bài báo'
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement changes in `DocumentTabBar.tsx`, `ViewportOverflowMenu.tsx`, `ViewportControls.tsx`, and `DashboardWorkspace.tsx`**

1. `DocumentTabBar.tsx`:
   - Xóa bỏ hoàn toàn render `Star` trên từng tab item.
   - Nút đóng tab: sử dụng icon `X`, áp dụng class `hover:text-rose-600 hover:bg-rose-500/10 dark:hover:text-rose-400 dark:hover:bg-rose-500/20`.
2. `ViewportOverflowMenu.tsx`:
   - Thêm props `isBookmarked?: boolean; onToggleBookmark?: () => void;`.
   - Trong khối "Công cụ", bổ sung nút "Lưu vào kho yêu thích" (hoặc "Bỏ lưu bài báo") với icon `Bookmark`.
3. `ViewportControls.tsx`:
   - Nhận `isBookmarked` và `onToggleBookmark`, truyền xuống `ViewportOverflowMenu`.
4. `DashboardWorkspace.tsx`:
   - Truyền `isBookmarked` và `onToggleBookmark` vào `<ViewportControls />`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 5**

```bash
git add apps/web/src/features/reader/components/DocumentTabBar.tsx apps/web/src/features/reader/components/ViewportOverflowMenu.tsx apps/web/src/features/reader/components/ViewportControls.tsx apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx
git commit -m "feat(reader): add bookmark action to overflow menu and style tab close icon with red hover"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 6: Comprehensive Verification Gates & Visual Audit

**Files:** All modified files across frontend and backend.

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: Exit code 0, 0 errors.

- [ ] **Step 2: Gate 2 - Backend Pytest**

Run: `uv run pytest`
Expected: 100% passed (269+ tests).

- [ ] **Step 3: Gate 3 - Frontend Vitest**

Run: `npm --prefix apps/web run test`
Expected: 100% passed (all suites).

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`
Expected: Exit code 0, no TypeScript errors.

- [ ] **Step 5: Headless Chrome Visual Audit**

Chạy kịch bản audit bằng Node.js Puppeteer/Chrome để chụp ảnh màn hình kiểm chứng:
1. `screenshot_session_mermaid_scrolled.png`: Kiểm chứng Mermaid không bị đen khi cuộn PDF.
2. `screenshot_session_crud_menu.png`: Kiểm chứng menu `...` với Rename, Delete, Unread.
3. `screenshot_workspace_horizontal_header.png`: Kiểm chứng icon Workspace nằm ngang.
4. `screenshot_reader_viewport_bookmark.png`: Kiểm chứng icon Bookmark cạnh prev/next và tab `✕` hover đỏ.

---

### Task 7: VPS Deployment Sync

- [ ] **Step 1: Execute auto-deployment script**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0 (cập nhật thành công VPS nếu online hoặc bỏ qua an toàn nếu offline).

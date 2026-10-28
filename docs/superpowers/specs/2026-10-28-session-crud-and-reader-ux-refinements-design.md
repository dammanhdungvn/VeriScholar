# ĐẶC TẢ THIẾT KẾ: SỬA LỖI MERMAID CUỘN PDF, SESSION CRUD & TINH CHỈNH GIAO DIỆN ĐỌC

> **Bản quyền kiến trúc:** VeriScholar MVP — Monorepo Agent Harness
> **Tài liệu tham chiếu:** [`AGENTS.md`](../../../AGENTS.md), [`docs/PRD/`](../../PRD), [`docs/specs/`](../../specs)
> **Trạng thái:** Sẵn sàng thực thi (Ready for Implementation)

---

## 1. Bối Cảnh & Vấn Đề (Problem Statement)

Qua quá trình tương tác và phản hồi của người dùng với các ảnh chụp màn hình kiểm chứng:

1. **Lỗi vuốt PDF làm mất sơ đồ Mermaid bên Chatbot (Ảnh 5 & 6):**
   - **Hiện tượng:** Khi người dùng cuộn xem nội dung tài liệu PDF bên cột trái, khung sơ đồ trực quan Mermaid bên cột Chatbot bị chớp giật, biến mất hoặc hiển thị thành một khung màu đen rỗng (`min-h-[140px]`).
   - **Nguyên nhân cốt lõi:**
     - Trong [`MermaidRenderer.tsx`](../../../apps/web/src/components/shared/MermaidRenderer.tsx), state `svgContent` được khởi tạo là chuỗi rỗng `useState<string>("")`.
     - Mỗi khi người dùng cuộn PDF, sự kiện trang (`currentPage`, `scrollOffset`) kích hoạt re-render ở `DashboardWorkspace`.
     - `MermaidRenderer` bị re-render không cần thiết và `mermaid.render()` thực hiện bất đồng bộ; trong thời gian xử lý, `svgContent` là rỗng dẫn đến khung đen rỗng.
2. **Lỗi CRUD Sessions chat trên Frontend:**
   - **Tạo mới (Create):** Nút "+ Đoạn chat mới" đã hoạt động.
   - **Đọc (Read):** Click mở phiên chat đã hoạt động.
   - **Đổi tên (Update/Rename):** Trong menu `...` của mỗi session, nút "Đổi tên" chỉ đóng menu mà chưa cho phép nhập tên mới và chưa gọi API cập nhật metadata (`PATCH /api/v1/sessions/{id}`).
   - **Xóa (Delete):** Nút "Xóa" chỉ đóng menu, chưa có cơ chế xác nhận và chưa gọi API xóa phiên (`DELETE /api/v1/sessions/{id}`).
3. **Chế độ Đánh dấu Đã đọc / Chưa đọc (Read / Unread):**
   - Thiếu chỉ báo trạng thái trên từng session item.
   - Người dùng yêu cầu: Session chưa đọc phải có dấu hiệu nhận biết (chấm tròn màu san hô nổi bật); khi đã đọc (hoặc khi click mở session), chấm tròn tự động biến mất.
   - Trong menu `...`, hỗ trợ chuyển đổi linh hoạt: "Đánh dấu chưa đọc" $\leftrightarrow$ "Đánh dấu đã đọc".
4. **Đóng Menu `...` khi click ra ngoài (Click-outside dismissal):**
   - Menu ngữ cảnh của session item hiện tại chỉ đóng khi click vào một hành động bên trong. Cần cơ chế click-outside để đóng menu tự nhiên khi click ra ngoài.
5. **Vị trí Icon Workspace ([`UnifiedHeroWorkspace.tsx`](../../../apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx)):**
   - Icon logo `AcademicLogo` hiện đang xếp dọc bên trên chữ "Workspace", chiếm nhiều diện tích và không cân đối.
   - Người dùng đã chốt **Phương án A**: Đặt icon logo nằm ngang hàng bên trái chữ **Workspace** (`[Icon] Workspace`).
6. **Thống nhất Header Socratic Assistant (Ảnh 7):**
   - Hiện tại thanh header trên cùng chỉ có icon `[ ✨ ]` (trong vòng tròn nhỏ) và nút đóng `✕`, trong khi ngay bên dưới trong khung cuộn lại lặp lại một khối `[ ✨ ] Socratic Assistant`.
   - Cần đưa nhãn chữ `Socratic Assistant` lên thẳng thanh header trên cùng (`[ ✨ ] Socratic Assistant` + `✕`), và xóa bỏ hoàn toàn khối lặp lại bên dưới.
7. **Tab PDF & Thanh công cụ đọc (Ảnh 8, 9, 10):**
   - Trên tab tài liệu PDF ([`DocumentTabBar.tsx`](../../../apps/web/src/features/reader/components/DocumentTabBar.tsx)), xóa bỏ icon ngôi sao (`Star`).
   - Nút xóa/đóng tab hiện tại đổi thành dấu `✕` (`X`), khi hover đổi sang màu đỏ (`text-zinc-400 hover:text-rose-600 hover:bg-rose-500/10`).
   - Tính năng Lưu/Bookmark bài báo được đặt trong menu **"Tùy chọn"** ([`ViewportOverflowMenu.tsx`](../../../apps/web/src/features/reader/components/ViewportOverflowMenu.tsx)), giúp thanh công cụ đọc giữ trọn vẹn sự tối giản, gọn gàng và tinh tế.

---

## 2. Giải Pháp Kỹ Thuật Chi Tiết (Technical Specification)

### 2.1. Cải tiến `MermaidRenderer` với Bộ Nhớ Đệm SVG (SVG Memory Cache) & Memoization
- Tạo bộ nhớ đệm module-level:
  ```typescript
  const mermaidSvgCache = new Map<string, string>();
  ```
- Khởi tạo state tức thì (0ms) từ cache nếu đã vẽ trước đó:
  ```typescript
  const isDark = typeof document !== "undefined" && document.documentElement.classList.contains("dark");
  const cacheKey = `${isDark ? "dark" : "light"}:${chart?.trim() || ""}`;
  const [svgContent, setSvgContent] = useState<string>(() => mermaidSvgCache.get(cacheKey) || "");
  ```
- Trong `useEffect`: Nếu `mermaidSvgCache.has(cacheKey)`, gán ngay `setSvgContent` và return; chỉ gọi `mermaid.render()` khi cache miss. Khi render xong, lưu vào cache: `mermaidSvgCache.set(cacheKey, svg)`.
- Bọc component bằng `React.memo(MermaidRenderer)`.
- Trong `AcademicMarkdownRenderer.tsx`, gán `key={codeString}` cho `<MermaidRenderer />` để React duy trì DOM node ổn định khi re-render.

### 2.2. CRUD Session & Quản Lý Trạng Thái tại `DashboardTaskbar.tsx`
- **Click-outside Hook:**
  - Thêm `useRef<HTMLDivElement>(null)` cho container menu `...`.
  - Đăng ký `mousedown` event listener trên `document`: nếu click ngoài menu ref, đặt `setActiveMenuSessionId(null)`.
- **Rename Session:**
  - State: `editingSessionId: string | null`, `editingTitle: string`, `isSubmittingRename: boolean`.
  - Khi click "Đổi tên" trong menu: đặt `editingSessionId = session.id`, `editingTitle = session.title`.
  - Hiển thị inline `<input>` với nút xác nhận (Check/Enter) và hủy (X/Esc).
  - Khi xác nhận: Gọi API cập nhật:
    ```typescript
    const detail = await sessionsApi.getSessionDetail(sessionId);
    const etag = detail.headers?.get?.("etag") || `v${detail.data.version}`;
    await sessionsApi.updateSessionMetadata(sessionId, newTitle, etag);
    queryClient.invalidateQueries({ queryKey: ["sessions"] });
    ```
- **Delete Session:**
  - State: `deletingSessionId: string | null`.
  - Khi click "Xóa": hiển thị hộp thoại xác nhận nhỏ gọn (Confirm dialog).
  - Khi xác nhận xóa:
    ```typescript
    await sessionsApi.deleteSession(sessionId);
    queryClient.invalidateQueries({ queryKey: ["sessions"] });
    if (activeSessionId === sessionId) {
      navigate("/dashboard");
    }
    ```
- **Đánh dấu Đã đọc / Chưa đọc (Read / Unread):**
  - Quản lý danh sách ID các phiên chưa đọc qua `localStorage` (`unread_session_ids_v1`) và React state.
  - Khi session có trong tập `unreadSessionIds`:
    - Hiển thị chấm tròn màu san hô: `<span className="w-2 h-2 rounded-full bg-coral-500 shrink-0 shadow-xs" title="Chưa đọc" />`.
    - Menu `...` hiển thị: `<MailOpen className="w-3.5 h-3.5" /> <span>Đánh dấu đã đọc</span>`.
  - Khi session không có trong tập `unreadSessionIds`:
    - Menu `...` hiển thị: `<Mail className="w-3.5 h-3.5" /> <span>Đánh dấu chưa đọc</span>`.
  - Khi người dùng click vào session để mở đọc (`onSelectSession`): tự động xóa `sessionId` khỏi tập `unreadSessionIds`.

### 2.3. Vị Trí Icon Workspace tại `UnifiedHeroWorkspace.tsx`
- Chuyển đổi container tiêu đề từ `flex-col items-center mb-6` sang `flex-row items-center justify-center gap-3 mb-6`.
- Đặt `AcademicLogo` kích thước `w-9 h-9 sm:w-10 sm:h-10` nằm ngang hàng bên trái chữ `Workspace`.

### 2.4. Thống Nhất Header Socratic Assistant tại `DashboardWorkspace.tsx`
- **Header cố định (`<header className="h-11 px-3 ...">`):**
  - Cụm bên trái:
    ```tsx
    <div className="flex items-center gap-2 select-none">
      <div className="w-6 h-6 rounded-lg bg-[#cc785c]/15 text-[#cc785c] flex items-center justify-center">
        <Sparkles className="w-3.5 h-3.5" />
      </div>
      <h2 className="font-serif font-bold text-xs sm:text-sm text-ink dark:text-[#f3f2ef] leading-tight">
        Socratic Assistant
      </h2>
    </div>
    ```
  - Cụm bên phải: Nút đóng `✕` (`data-testid="close-assistant-btn"`).
- **Khung cuộn nội dung chat:**
  - Xóa bỏ hoàn toàn khối `Header Badge` (dòng 1084-1096 trong `DashboardWorkspace.tsx`).

### 2.5. Tab PDF & Menu "Tùy chọn" Đọc (`DocumentTabBar.tsx` & `ViewportOverflowMenu.tsx`)
- Trong `DocumentTabBar.tsx`:
  - Loại bỏ hoàn toàn nút `Star` và prop `onToggleStar` khỏi tab.
  - Loại bỏ nút `Trash2` riêng biệt trên tab.
  - Nút đóng tab: sử dụng icon `X` với style hover chuyển sang màu đỏ:
    ```tsx
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onCloseDocument(docId);
      }}
      aria-label={`Đóng tab ${displayName}`}
      className="p-1 rounded text-zinc-400 hover:text-rose-600 hover:bg-rose-500/10 dark:hover:text-rose-400 dark:hover:bg-rose-500/20 transition-colors cursor-pointer"
    >
      <X className="w-3.5 h-3.5 stroke-[2.2]" />
    </button>
    ```
- Trong `ViewportOverflowMenu.tsx` (Menu "Tùy chọn"):
  - Thêm props: `isBookmarked?: boolean; onToggleBookmark?: () => void;`.
  - Bổ sung mục chọn Lưu bài báo trong cụm "Công cụ":
    ```tsx
    {onToggleBookmark && (
      <button
        type="button"
        role="menuitem"
        data-testid="overflow-toggle-bookmark-btn"
        onClick={() => {
          onClose();
          onToggleBookmark();
        }}
        className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
      >
        <Bookmark className={cn("w-3.5 h-3.5 shrink-0", isBookmarked ? "text-amber-500 fill-amber-500" : "text-primary")} />
        <span className="flex-1 font-medium">
          {isBookmarked ? "Bỏ lưu bài báo (Kho yêu thích)" : "Lưu vào kho yêu thích"}
        </span>
      </button>
    )}
    ```
- Trong `ViewportControls.tsx`:
  - Nhận props `isBookmarked` và `onToggleBookmark` và truyền tiếp xuống `ViewportOverflowMenu`.
- Trong `DashboardWorkspace.tsx`:
  - Truyền `isBookmarked={Boolean(effectiveDocuments.find((d) => d.id === activeDocumentId)?.is_persistent)}` và `onToggleBookmark={() => activeDocumentId && handleToggleStar(activeDocumentId)}` vào `<ViewportControls />`.

---

## 3. Tiêu Chí Nghiệm Thu (Acceptance Criteria)
1. **Mermaid Cuộn PDF:** Khi cuộn trang PDF ở bất kỳ tốc độ nào, sơ đồ Mermaid bên Chatbot giữ nguyên hiển thị liên tục, không bị reset trắng hoặc chuyển sang hộp đen rỗng.
2. **Session Rename & Delete:**
   - Click "Đổi tên" $\rightarrow$ inline input hiển thị, lưu tên mới thành công, hiển thị tức thì trên danh sách Recents.
   - Click "Xóa" $\rightarrow$ hiển thị xác nhận, xóa thành công khỏi backend, nếu phiên đang mở thì điều hướng về `/dashboard`.
3. **Read / Unread:**
   - Phiên chưa đọc có chấm tròn san hô `bg-coral-500`.
   - Click mở phiên $\rightarrow$ chấm tròn biến mất.
   - Menu `...` có thể chuyển đổi thủ công Đã đọc / Chưa đọc.
4. **Click-outside:** Click chuột ra ngoài menu `...` tự động đóng menu.
5. **Workspace Icon:** Icon logo nằm ngang hàng bên trái chữ `Workspace`.
6. **Socratic Header:** Header trên cùng hiển thị `[ ✨ ] Socratic Assistant` + `✕`, không còn dòng lặp lại bên dưới.
7. **Tab PDF & Viewport Controls:** Tab PDF không còn Star, nút đóng tab là `✕` hover màu đỏ; mục Lưu bài báo được đặt trong menu "Tùy chọn".
8. **4 Gates Pass:** Ruff 0 lỗi, Pytest passed, Vitest passed, Build thành công 100%.

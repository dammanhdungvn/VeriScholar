# Academic Writing, PDF Reader, and GraphRAG Library UX Refinements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triệt tiêu hiện tượng reload/flicker chuyển trang bằng Persistent App Layout; thiết kế không gian "Viết paper" chuẩn Overleaf tối giản kết hợp Socratic Assistant FAB; tự động chọn XeLaTeX sửa lỗi biên dịch tiếng Việt; bổ sung tab PDF Outline; đồng bộ hóa Save/Unsave và chỉ hiển thị tài liệu đã lưu trong My Library; hợp nhất GraphRAG thành thanh tìm kiếm thông minh tự động phân rã intent (Decomposer & Router).

**Architecture:** Sử dụng React Router Persistent Layout giữ Taskbar liên tục; cấu trúc lại Writing Workspace theo chuẩn Overleaf với FAB Socratic Assistant ở góc dưới; nâng cấp `CLSILatexCompiler` với bộ phát hiện Unicode tự động kích hoạt `xelatex` và fallback E2B; mở rộng `PdfThumbnailSidebar` hỗ trợ `getOutline()` của PDF.js; đồng bộ cờ `is_persistent` toàn hệ thống; xây dựng `GraphRAGRouter` tích hợp `AcademicQueryDecomposer` để định tuyến câu hỏi tự động.

**Tech Stack:** React 19, TypeScript, Vitest, React Router, Tailwind CSS, Lucide React, FastAPI, SQLAlchemy 2.0 Async, pdfjs-dist, latexmk, xelatex, E2B Cloud Sandbox.

**Spec:** [`docs/superpowers/specs/2026-10-29-academic-writing-and-library-ux-refinements-design.md`](../specs/2026-10-29-academic-writing-and-library-ux-refinements-design.md)

## Global Constraints

- Tuân thủ 100% 4 Cổng Xác Minh Bắt Buộc: Ruff (Cổng 1), Pytest (Cổng 2), Vitest (Cổng 3), Build (Cổng 4).
- Kiến trúc lục giác bất biến: Tuyệt đối không import thư viện I/O hay framework ngoài vào `packages/core/`.
- Tối giản cấp tiến (Rule 6): Loại bỏ các nút thừa đè chữ (`🧹 Xóa đệm & Dựng lại`, `Bản Dựng PDF Trực Tiếp`), badge `completed` lặp lại, và các nút chọn chế độ kỹ thuật nội bộ (`Local/Global/Hybrid`).
- Tự động đồng bộ VPS sau mỗi commit có kiểm thử thành công (Rule 9).

## Review Focus

1. **Persistent Taskbar Mount Integrity:** Khi điều hướng qua lại giữa `/dashboard`, `/library` và `/writing`, component `DashboardTaskbar` không bao giờ bị unmount hoặc reset trạng thái thu/phóng.
2. **Vietnamese Unicode Compilation Success:** Biên dịch các mẫu văn bản tiếng Việt có dấu (`Ế, ớ, ả, ư, ơ`) phải đạt exit code 0 thông qua `xelatex` mà không xảy ra lỗi `Unicode character ... [COMPILATION_FAILED]`.
3. **Socratic Assistant FAB on Writing Workspace:** Bong bóng AI nổi ở góc dưới bên phải mở drawer trượt ngang 420px mượt mà mà không chiếm cố định 1 cột layout gây chật màn hình.
4. **PDF Outline Tree Jump Navigation:** Nhấp chuột vào bất kỳ mục nào trên cây Outline (`Abstract`, `1. Introduction`, `2. Methods`) phải cuộn chính xác trang PDF đến đúng vị trí đề mục.
5. **Universal Save/Unsave Consistency:** Bài báo đã lưu (`is_persistent: true`) khi mở lại ở bất kỳ đâu (Reader, Upload, Search) phải hiển thị trạng thái "Đã lưu", bấm vào sẽ kích hoạt Unsave mà không nhân bản dữ liệu.

---

### Task 1: Persistent App Layout & Taskbar Refinement

**Files:**
- Create: `apps/web/src/features/dashboard/components/AppLayout.tsx`
- Modify: `apps/web/src/app/routes.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx:250-280`
- Modify: `apps/web/src/features/writing/components/WritingPage.tsx:110-120`
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx:280-290`
- Modify: `apps/web/src/features/library/components/LibraryPage.tsx:40-60`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/AppLayoutNavigation.test.tsx`

**Interfaces:**
- Consumes: `DashboardTaskbar`, `useDashboardSessions`, `Outlet`
- Produces: `AppLayout` bọc các route chính; Taskbar chỉ có: `+ Đoạn chat mới`, `Kho Yêu thích`, `Viết paper`, `Recents`; loại bỏ hoàn toàn `Khám phá & Phiên đọc`.

- [ ] **Step 1: Write failing tests for Taskbar items and Persistent App Layout**

Trong `DashboardTaskbar.test.tsx` và `AppLayoutNavigation.test.tsx`:
```tsx
it("renders 'Viết paper' and does not render 'Khám phá & Phiên đọc' in taskbar", () => {
  renderWithRouter(<DashboardTaskbar />);
  expect(screen.getByText("Viết paper")).toBeInTheDocument();
  expect(screen.queryByText(/Khám phá & Phiên đọc/i)).toBeNull();
});

it("renders AppLayout with persistent taskbar and renders outlet content", () => {
  render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <AppLayout />
    </MemoryRouter>
  );
  expect(screen.getByLabelText("Thanh điều hướng chính")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/AppLayoutNavigation.test.tsx apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement `AppLayout` and update `DashboardTaskbar.tsx`, `routes.tsx`, `WritingPage.tsx`, `LibraryPage.tsx`**

1. Tạo `AppLayout.tsx` render `<div className="flex h-screen w-screen overflow-hidden"><DashboardTaskbar /><Outlet /></div>`.
2. Trong `DashboardTaskbar.tsx`:
   - Xóa bỏ mục `Khám phá & Phiên đọc`.
   - Đổi label và title của `writing` thành `"Viết paper"`.
3. Trong `routes.tsx`:
   - Cấu hình route cha `element: <AppLayout />` chứa các children: `/dashboard`, `/dashboard/:sessionId`, `/library`, `/writing`, `/writing/:draftId`.
4. Trong `WritingPage.tsx`:
   - Xóa bỏ màn hình đệm full-screen `h-screen w-screen` chặn taskbar; hiển thị skeleton loading cục bộ cho editor/preview.
5. Loại bỏ thẻ `<DashboardTaskbar />` bị lặp bên trong `WritingWorkspace.tsx` và `LibraryPage.tsx`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix apps/web run test -- apps/web/src/features/dashboard/__tests__/AppLayoutNavigation.test.tsx apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add apps/web/src/features/dashboard/components/AppLayout.tsx apps/web/src/app/routes.tsx apps/web/src/features/dashboard/components/DashboardTaskbar.tsx apps/web/src/features/writing/components/WritingPage.tsx apps/web/src/features/writing/components/WritingWorkspace.tsx apps/web/src/features/library/components/LibraryPage.tsx apps/web/src/features/dashboard/__tests__/AppLayoutNavigation.test.tsx apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx
git commit -m "feat(layout): introduce persistent app layout and rename writing taskbar to 'Viết paper'"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 2: XeLaTeX Engine Auto-Detection & CLSI Compilation Unification

**Files:**
- Modify: `apps/api/src/api/services/clsi_latex_compiler.py:38-55, 195-215`
- Modify: `apps/api/src/api/services/draft_service.py:545-580`
- Test: `apps/api/tests/test_clsi_latex_compiler.py`
- Test: `apps/api/tests/test_drafts_endpoints.py`

**Interfaces:**
- Consumes: `main_tex: str`, `draft_id: UUID`, `clear_cache: bool`
- Produces: `CLSILatexCompiler.detect_engine` trả về `("xelatex", "-xelatex")` cho văn bản Unicode tiếng Việt; `compile_draft` chuẩn hóa qua `CLSILatexCompiler` với caching.

- [ ] **Step 1: Write failing tests for XeLaTeX auto-detection and Vietnamese compilation**

Trong `test_clsi_latex_compiler.py`:
```python
def test_detect_engine_selects_xelatex_for_vietnamese_unicode():
    vietnamese_tex = r"\title{KIẾN TRÚC MÔ HÌNH SOCRATIC COPILOT: TỰ ĐỘNG PHẢN BIỆN}"
    engine, flag = CLSILatexCompiler.detect_engine(vietnamese_tex)
    assert engine == "xelatex"
    assert flag == "-xelatex"

@pytest.mark.asyncio
async def test_compile_vietnamese_template_succeeds_with_xelatex(tmp_path):
    compiler = CLSILatexCompiler(work_dir=str(tmp_path))
    content = "\\documentclass{article}\\begin{document}Học giả VeriScholar\\end{document}"
    res = await compiler.compile(draft_id=uuid4(), main_tex=content)
    assert res["success"] is True
    assert res["engine"] == "xelatex"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest apps/api/tests/test_clsi_latex_compiler.py`
Expected: FAIL

- [ ] **Step 3: Implement Unicode detection and compiler unification in `clsi_latex_compiler.py` and `draft_service.py`**

1. Trong `CLSILatexCompiler.detect_engine`:
   - Thêm kiểm tra: `has_unicode = any(ord(c) > 127 for c in main_tex)`
   - Nếu `has_unicode` hoặc `fontspec` hoặc `xelatex`: trả về `("xelatex", "-xelatex")`.
2. Trong `draft_service.py`:
   - Cập nhật `compile_draft` gọi qua `self.clsi_compiler.compile(...)` với `clear_cache=False` theo mặc định.
   - Khi có lỗi, chuyển diagnostics qua `LatexLogParser` để cấp gợi ý sửa cú pháp hoặc fallback an toàn sang `E2BLatexCompiler`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest apps/api/tests/test_clsi_latex_compiler.py apps/api/tests/test_drafts_endpoints.py`
Expected: PASS

- [ ] **Step 5: Commit Task 2**

```bash
git add apps/api/src/api/services/clsi_latex_compiler.py apps/api/src/api/services/draft_service.py apps/api/tests/test_clsi_latex_compiler.py apps/api/tests/test_drafts_endpoints.py
git commit -m "fix(compiler): auto-detect xelatex for unicode vietnamese and unify clsi draft compilation"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 3: Overleaf-Grade "Viết Paper" Workspace & Floating Socratic FAB

**Files:**
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- Modify: `apps/web/src/features/writing/components/WritingPreviewPane.tsx`
- Modify: `apps/web/src/features/writing/components/WritingHeaderBar.tsx`
- Test: `apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`

**Interfaces:**
- Consumes: `isCompiling`, `previewPdfBlobUrl`, `handleCompile`, `isAssistantOpen`
- Produces:
  - Header Preview chỉ có 1 nút `Recompile` xanh lá có dropdown "Recompile" / "Clear Cache & Recompile"; loại bỏ `🧹 Xóa đệm & Dựng lại` và `Bản Dựng PDF Trực Tiếp`.
  - Floating Action Button (FAB) `[ ✨ ] Socratic Assistant` ở góc dưới bên phải, bấm vào mở drawer overlay 420px.

- [ ] **Step 1: Write failing tests for Overleaf-grade layout and FAB Assistant**

Trong `WritingWorkspace.test.tsx`:
```tsx
it("renders single smart Recompile button and removes bulky clear-cache action bar", async () => {
  renderWithRouter(<WritingWorkspace />);
  expect(screen.getByTestId("recompile-btn")).toBeInTheDocument();
  expect(screen.queryByText(/Bản Dựng PDF Trực Tiếp/i)).toBeNull();
  expect(screen.queryByText(/🧹 Xóa đệm & Dựng lại/i)).toBeNull();
});

it("renders Socratic Assistant floating action button at bottom right", async () => {
  renderWithRouter(<WritingWorkspace />);
  const fab = screen.getByTestId("writing-assistant-fab");
  expect(fab).toBeInTheDocument();
  fireEvent.click(fab);
  expect(screen.getByTestId("writing-assistant-drawer")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`
Expected: FAIL

- [ ] **Step 3: Refactor `WritingPreviewPane.tsx` and `WritingWorkspace.tsx`**

1. Trong `WritingPreviewPane.tsx`:
   - Xóa bỏ nút cam `[ 🧹 Xóa đệm & Dựng lại ]` và text `Bản Dựng PDF Trực Tiếp`.
   - Giữ lại nút tải PDF, thanh lật trang `1 / N`, zoom controls.
2. Trong `WritingHeaderBar.tsx`:
   - Bổ sung nút `Recompile` xanh lá thông minh với dropdown menu nhỏ (Click chính: Biên dịch nhanh; Click mũi tên: "Xóa bộ đệm & Dựng lại").
3. Trong `WritingWorkspace.tsx`:
   - Chuyển `WritingAssistantPane` từ cột cố định thành drawer trượt ngang overlay (`fixed inset-y-0 right-0 w-[420px] shadow-2xl z-40`).
   - Thêm FAB tròn ở góc dưới bên phải (`fixed bottom-5 right-5 z-30 p-3 rounded-full bg-coral-500 text-white shadow-xl hover:scale-105 transition-all`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix apps/web run test -- apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 3**

```bash
git add apps/web/src/features/writing/components/WritingWorkspace.tsx apps/web/src/features/writing/components/WritingPreviewPane.tsx apps/web/src/features/writing/components/WritingHeaderBar.tsx apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx
git commit -m "feat(writing): polish overleaf-style toolbar and implement socratic assistant fab drawer"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 4: PDF Reader Dual-Mode Sidebar (Thumbnails & Outline)

**Files:**
- Modify: `apps/web/src/features/reader/components/PdfThumbnailSidebar.tsx`
- Modify: `apps/web/src/features/reader/components/DeepReadingWorkspace.tsx`
- Test: `apps/web/src/features/reader/__tests__/PdfThumbnailSidebar.test.tsx`

**Interfaces:**
- Consumes: `pdfDoc: PDFDocumentProxy`, `onSelectPage: (page: number) => void`
- Produces: Sidebar có segmented control `[ 🖼️ Trang ]` | `[ 📑 Mục lục ]`; khi chọn Mục lục, trích xuất `pdfDoc.getOutline()` và hiển thị cây phân cấp có thể nhấp để nhảy trang.

- [ ] **Step 1: Write failing tests for PDF Outline view mode and navigation**

Trong `PdfThumbnailSidebar.test.tsx`:
```tsx
it("toggles between thumbnail and outline view modes in PDF sidebar", async () => {
  const mockGetOutline = vi.fn().mockResolvedValue([
    { title: "1. Introduction", dest: 1, items: [] },
    { title: "2. Methodology", dest: 5, items: [] },
  ]);
  const mockPdfDoc = { getOutline: mockGetOutline, getPage: vi.fn() } as any;

  render(
    <PdfThumbnailSidebar
      isOpen={true}
      onClose={vi.fn()}
      totalPages={10}
      currentPage={1}
      onSelectPage={vi.fn()}
      pdfDoc={mockPdfDoc}
    />
  );

  const outlineTab = screen.getByRole("tab", { name: /Mục lục/i });
  fireEvent.click(outlineTab);
  expect(await screen.findByText("1. Introduction")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/reader/__tests__/PdfThumbnailSidebar.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement Outline Tab & Destination Navigation in `PdfThumbnailSidebar.tsx`**

1. Thêm state `viewMode: "thumbnails" | "outline"` và render segmented control ở header thanh bên.
2. Tạo component `PdfOutlineTree` gọi `pdfDoc.getOutline()`:
   - Xử lý đệ quy các cấp đề mục (cấp 1, cấp 2...).
   - Khi click vào đề mục, giải quyết `dest` (số trang hoặc destination array) và gọi `onSelectPage(resolvedPage)`.
   - Nếu tài liệu không có bookmark, hiển thị thông báo nhẹ: *"Tài liệu này không có mục lục nhúng."*

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix apps/web run test -- apps/web/src/features/reader/__tests__/PdfThumbnailSidebar.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit Task 4**

```bash
git add apps/web/src/features/reader/components/PdfThumbnailSidebar.tsx apps/web/src/features/reader/components/DeepReadingWorkspace.tsx apps/web/src/features/reader/__tests__/PdfThumbnailSidebar.test.tsx
git commit -m "feat(reader): add pdf outline table-of-contents navigation to reader sidebar"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 5: My Library Strict Persistence, Save/Unsave Sync & Icon Actions

**Files:**
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx:90-115, 600-720`
- Modify: `apps/api/src/api/services/document_service.py:1000-1050, 1430-1460`
- Test: `apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`
- Test: `apps/api/tests/test_library_endpoints.py`

**Interfaces:**
- Consumes: `rawDocuments: DocumentListItem[]`, `toggleStar`
- Produces:
  - My Library chỉ hiển thị các bài báo có `is_persistent: true` hoặc có `folder_id`.
  - Thay thế chữ `Config` và `Delete` thành các icon `SlidersHorizontal` và `Trash2` (hover đỏ).
  - Ẩn các badge `completed` lặp lại.
  - Đồng bộ trạng thái Lưu/Hủy lưu (Unsave) không gây trùng bản ghi.

- [ ] **Step 1: Write failing tests for library persistence filtering and icon actions**

Trong `LibraryWorkspaceView.test.tsx`:
```tsx
it("only displays persistent or categorized documents in My Library", () => {
  const mockDocs = [
    { id: "1", title: "Saved Paper", is_persistent: true },
    { id: "2", title: "Temporary Paper", is_persistent: false },
  ];
  renderWithQueryClient(<LibraryWorkspaceView documents={mockDocs} />);
  expect(screen.getByText("Saved Paper")).toBeInTheDocument();
  expect(screen.queryByText("Temporary Paper")).toBeNull();
});

it("renders icon buttons for config and delete instead of raw text", () => {
  renderWithQueryClient(<LibraryWorkspaceView documents={[{ id: "1", title: "Paper 1", is_persistent: true }]} />);
  expect(screen.queryByText("Config")).toBeNull();
  expect(screen.queryByText("Delete")).toBeNull();
  expect(screen.getByTestId("doc-delete-btn-1")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify failure**

Run: `npm --prefix apps/web run test -- apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement persistence filtering, deduplication, and icon actions**

1. Trong `LibraryWorkspaceView.tsx`:
   - Sửa `documents` memo filter: Mặc định lọc `rawDocuments.filter(d => Boolean(d.is_persistent || d.starred_at || d.folder_id))`.
   - Đổi các nút text `Config` và `Delete` thành icon `<SlidersHorizontal className="w-3.5 h-3.5" />` và `<Trash2 className="w-3.5 h-3.5 text-muted hover:text-rose-600" />`.
   - Ẩn nhãn badge `completed` trên từng card.
2. Trong `document_service.py`:
   - Đảm bảo khi người dùng tải lên bài báo có `content_hash` hoặc `doi` đã tồn tại và đã `is_persistent: True`, giữ nguyên quyền sở hữu và không tạo trùng bản ghi.

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix apps/web run test -- apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`
Run: `uv run pytest apps/api/tests/test_library_endpoints.py`
Expected: PASS

- [ ] **Step 5: Commit Task 5**

```bash
git add apps/web/src/features/library/components/LibraryWorkspaceView.tsx apps/api/src/api/services/document_service.py apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx apps/api/tests/test_library_endpoints.py
git commit -m "feat(library): enforce persistent-only view, convert actions to icons, and sync save-unsave"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 6: GraphRAG Query Decomposer & Multi-Intent Router

**Files:**
- Create: `apps/api/src/api/services/graph_rag_router.py`
- Modify: `apps/api/src/api/services/graph_rag_service.py:35-135`
- Modify: `apps/api/src/api/v1/endpoints/library.py:30-70`
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx:340-380`
- Test: `apps/api/tests/unit/test_graph_rag_router.py`
- Test: `apps/api/tests/test_graph_rag_query.py`

**Interfaces:**
- Consumes: `AcademicQueryDecomposer`, `query: str`, `folder_id: UUID | None`
- Produces: `GraphRAGRouter.route_and_query(...)` tự động phân loại intent (macro, micro, citation) và tổng hợp kết quả; giao diện loại bỏ hoàn toàn radio buttons `Local/Global/Hybrid`.

- [ ] **Step 1: Write failing tests for GraphRAG multi-intent decomposition and routing**

Trong `test_graph_rag_router.py`:
```python
@pytest.mark.asyncio
async def test_router_dispatches_macro_community_for_comparative_query():
    router = GraphRAGRouter(graph_service=mock_graph_service)
    res = await router.route_and_query(query="Tổng quan so sánh SOTA các mô hình Transformer")
    assert "community_macro_scan" in res["dispatched_tools"]

@pytest.mark.asyncio
async def test_router_dispatches_entity_subgraph_for_metric_query():
    router = GraphRAGRouter(graph_service=mock_graph_service)
    res = await router.route_and_query(query="Công thức tính và kết quả giảm bộ nhớ của Selective Attention")
    assert "entity_subgraph_lookup" in res["dispatched_tools"]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest apps/api/tests/unit/test_graph_rag_router.py`
Expected: FAIL

- [ ] **Step 3: Implement `GraphRAGRouter` and update library endpoint and UI**

1. Tạo `apps/api/src/api/services/graph_rag_router.py`:
   - Nhận diện query bằng `AcademicQueryDecomposer`:
     - Nếu có từ khóa so sánh/tổng quan/xu hướng: gọi `_execute_global_scan`.
     - Nếu có từ khóa công thức/số liệu/tên mô hình/thực thể cụ thể: gọi `_execute_2_step_cte`.
     - Nếu có từ khóa trích dẫn/nền tảng: gọi `compute_bibliometrics`.
   - Tổng hợp kết quả và chèn các huy hiệu trích dẫn (`[ 🌐 2 cụm nghiên cứu ]`, `[ 📍 4 thực thể đối chiếu ]`).
2. Trong `apps/api/src/api/v1/endpoints/library.py`:
   - Cho phép `mode: Literal["auto", "hybrid", "local", "global"] = "auto"`.
3. Trong `LibraryWorkspaceView.tsx`:
   - Xóa bỏ hoàn toàn cụm radio `[ Chế độ Tra Cứu Tri Thức: Hybrid | Local | Global ]`.
   - Giữ lại duy nhất thanh tìm kiếm thông minh: `🔍 Tra cứu tri thức, đối chiếu mô hình hoặc hỏi đáp trên toàn bộ thư viện...`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest apps/api/tests/unit/test_graph_rag_router.py apps/api/tests/test_graph_rag_query.py`
Expected: PASS

- [ ] **Step 5: Commit Task 6**

```bash
git add apps/api/src/api/services/graph_rag_router.py apps/api/src/api/services/graph_rag_service.py apps/api/src/api/v1/endpoints/library.py apps/web/src/features/library/components/LibraryWorkspaceView.tsx apps/api/tests/unit/test_graph_rag_router.py apps/api/tests/test_graph_rag_query.py
git commit -m "feat(library): eliminate manual mode toggles and introduce graphrag intent decomposer router"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 7: Comprehensive Verification Gates & VPS Deployment Sync

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

- [ ] **Step 5: Headless Browser Visual Audit**

Chụp ảnh màn hình kiểm chứng:
1. `screenshot_app_layout_seamless.png`: Kiểm chứng Taskbar không bị unmount/chớp nháy khi điều hướng.
2. `screenshot_overleaf_writing_workspace.png`: Kiểm chứng giao diện soạn thảo chuẩn Overleaf, nút Recompile tinh giản và FAB Socratic Assistant.
3. `screenshot_pdf_outline_sidebar.png`: Kiểm chứng tab Mục lục và khả năng nhảy trang.
4. `screenshot_library_clean_router.png`: Kiểm chứng `/library` không còn radio buttons `Local/Global/Hybrid`, icon Actions tinh tế.

- [ ] **Step 6: Task 7 Deployment Sync**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0.

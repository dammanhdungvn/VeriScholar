# Writing Agentic Tools, LaTeX Error Visual Highlighter, and Library LLM Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục lỗi 401 preview.pdf, bóc tách chính xác dòng lỗi biên dịch LaTeX và đánh dấu trực quan trong editor; tối giản thanh tab và header `/writing` (bỏ nút thừa, thêm nút mở lại sidebar và đóng tab); hỗ trợ upload nhiều asset cùng lúc; xây dựng bộ LangGraph tools cho AI Assistant kèm cơ chế Hoàn tác/Khôi phục 2 chiều và resizable chat drawer; bổ sung tab tải file PDF vào modal phiên đọc và khử trùng lặp; đại tu Thư viện với Đồ thị Tri thức tương tác (LLM Wiki Canvas) và bong bóng GraphRAG Assistant FAB.

**Architecture:** Nâng cấp bộ phân tích log regex trong `packages/core` và `clsi_latex_compiler` để trích xuất dòng lỗi thực; sử dụng `getCachedPdfDocument` kèm Bearer token cho PDF.js; cấu trúc lại `DraftAssetManagementModal` hỗ trợ `multiple`; nâng cấp `LatexCoauthorAgent` thành LangGraph ReAct Agent với tool-calling và snapshot swap 2 chiều `undo/redo` trong `JSONType`; nâng cấp `AddDocumentModal` với tab upload và filter thư viện chuẩn; xây dựng endpoint `GET /api/v1/library/graph` và canvas đồ thị tri thức trực quan tương tác tại `/library`.

**Tech Stack:** React 19, TypeScript, Vitest, Tailwind CSS, Lucide React, FastAPI, SQLAlchemy 2.0 Async, pdfjs-dist, LangGraph, LangChain, E2B Cloud Sandbox.

**Spec:** [`docs/superpowers/specs/2026-10-29-writing-agent-tools-and-library-llm-wiki-design.md`](../specs/2026-10-29-writing-agent-tools-and-library-llm-wiki-design.md)

## Global Constraints

- Tuân thủ 100% 4 Cổng Xác Minh Bắt Buộc: Ruff (Cổng 1), Pytest (Cổng 2), Vitest (Cổng 3), Build (Cổng 4).
- Kiến trúc lục giác bất biến: Tuyệt đối không import thư viện I/O hay framework ngoài vào `packages/core/`.
- Không thay đổi schema cơ sở dữ liệu quan hệ (Zero DB Schema Migration): Dùng trường `previous_snapshot` dạng `JSONType` để lưu trữ cả `undo` và `redo`.
- Tối giản cấp tiến (Rule 6): Loại bỏ các nút thừa đè chữ (`<-`, `Files`, `v1`, `syncTex`), badge `completed` lặp lại, và các khối rỗng cồng kềnh.
- Tự động đồng bộ VPS sau mỗi commit có kiểm thử thành công (Rule 9).

## Review Focus

1. **LaTeX Compiler Error Line Accuracy:** Khi biên dịch gặp lỗi cú pháp ở dòng $N$, parser phải trích xuất đúng dòng $N$, gutter phải hiển thị icon cảnh báo và click vào banner phải cuộn mượt đến dòng $N$.
2. **Zero 401 on Preview PDF:** Khi tải bản xem trước PDF bản thảo, `Authorization: Bearer <token>` phải luôn được đính kèm và không bị từ chối 401.
3. **Undo/Redo 2-Way Symmetrical Snapshot:** Khi nhấn Hoàn tác, code quay về bản trước và nút đổi thành "Khôi phục (Redo)"; khi nhấn Khôi phục, code trở lại bản AI vừa sinh.
4. **Knowledge Graph Canvas Performance:** Endpoint `/api/v1/library/graph` trả về top-50 thực thể mấu chốt, canvas hiển thị mượt mà không đơ lag trên trình duyệt.
5. **Universal Save & Deduplication Consistency:** Modal thêm tài liệu chỉ hiện tài liệu đã lưu trong Thư viện và không bị trùng lặp tên.

---

### Task 1: LaTeX Compiler Error Log Regex Parser & Interactive Line Highlighting

**Files:**
- Modify: `packages/core/src/core/services/latex_compiler.py:440-475`
- Modify: `packages/core/src/core/services/latex_log_parser.py:50-120`
- Modify: `apps/api/src/api/services/clsi_latex_compiler.py:180-240`
- Modify: `apps/web/src/features/writing/components/WritingEditorPane.tsx:355-425`
- Test: `packages/core/tests/test_draft_skeleton_and_log_parser.py`
- Test: `apps/api/tests/test_clsi_latex_compiler.py`
- Test: `apps/web/src/features/writing/__tests__/WritingEditorPane.test.tsx`

**Interfaces:**
- Parser outputs `LatexSyntaxError(line=extracted_line, message=clean_msg, rule="SYNTAX_ERROR")`.
- `WritingEditorPane` renders a red indicator in the gutter for lines in `errors`, and clicking an error in the banner calls `scrollToLine(error.line)`.

- [ ] **Step 1: Write failing tests for LaTeX log error parser extracting exact line numbers**
- [ ] **Step 2: Run backend tests to verify failure** (`uv run pytest packages/core/tests/test_draft_skeleton_and_log_parser.py`)
- [ ] **Step 3: Implement regex log error parser in `latex_compiler.py`, `latex_log_parser.py`, and `clsi_latex_compiler.py`**
- [ ] **Step 4: Update `WritingEditorPane.tsx` with gutter error icon and click-to-scroll to error line**
- [ ] **Step 5: Write and run frontend tests** (`npm --prefix apps/web run test -- src/features/writing/__tests__/WritingEditorPane.test.tsx`)
- [ ] **Step 6: Commit Task 1** (`git commit -m "feat(writing): extract exact latex error lines and highlight in editor gutter"`)

---

### Task 2: Writing PDF Preview 401 Fix & Minimalist Header/Tabs Cleanups

**Files:**
- Modify: `apps/web/src/features/writing/components/WritingPreviewPane.tsx:350-385`
- Modify: `apps/web/src/features/writing/components/WritingHeaderBar.tsx:95-165`
- Modify: `apps/web/src/features/writing/components/WritingEditorPane.tsx:180-230`
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx:310-330`
- Modify: `apps/web/src/features/writing/stores/useWritingStore.ts`
- Test: `apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`

**Interfaces:**
- `WritingPreviewPane`: uses `getCachedPdfDocument(effectivePdfUrl)` ensuring Bearer token is attached.
- `WritingHeaderBar`: removes `<-`, `Files`, `v1`.
- `WritingEditorPane`: removes `({lineCount} dòng)`, removes `SyncTeX` button, adds `X` close button on file tabs.
- `WritingWorkspace`: when `isFileTreeOpen === false`, renders `<PanelLeft className="w-4 h-4 text-[#c15f3e]" />` button on tab strip to unhide sidebar.

- [ ] **Step 1: Write failing tests for PDF preview auth header, tab close button, and unhide sidebar toggle**
- [ ] **Step 2: Run tests to verify failure** (`npm --prefix apps/web run test -- src/features/writing/__tests__/WritingWorkspace.test.tsx`)
- [ ] **Step 3: Implement `getCachedPdfDocument` in `WritingPreviewPane.tsx` to fix 401 error**
- [ ] **Step 4: Remove `<-`, `Files`, `v1`, `SyncTeX`, and line count in Header & Editor tabs**
- [ ] **Step 5: Add `X` tab close button and `PanelLeft` unhide button in `WritingWorkspace.tsx`**
- [ ] **Step 6: Run tests and commit Task 2** (`git commit -m "fix(writing): eliminate preview 401 error and refine minimalist tabs and header"`)

---

### Task 3: Multi-File Asset Upload & Radical Minimalist Asset Modal

**Files:**
- Modify: `apps/web/src/features/writing/components/DraftAssetManagementModal.tsx:260-350`
- Test: `apps/web/src/features/writing/__tests__/DraftAssetManagementModal.test.tsx`

**Interfaces:**
- Input has `multiple`, supports batch uploading an array of files concurrently via `Promise.all`.
- Removes the large empty state container below dropzone, keeping dropzone clean and compact.

- [ ] **Step 1: Write failing test for multiple asset file uploads and minimalist layout**
- [ ] **Step 2: Run tests to verify failure**
- [ ] **Step 3: Update `DraftAssetManagementModal.tsx` to accept `multiple` files and remove redundant empty container**
- [ ] **Step 4: Run tests to verify passing**
- [ ] **Step 5: Commit Task 3** (`git commit -m "feat(writing): support batch asset upload and streamline modal layout"`)

---

### Task 4: Autonomous LangGraph Agent Tool-Calling & Undo/Redo 2-Way Snapshots

**Files:**
- Modify: `apps/api/src/api/agents/latex_agent.py:670-790`
- Modify: `apps/api/src/api/services/draft_service.py:795-840, 875-935`
- Modify: `apps/api/src/api/v1/endpoints/drafts.py:410-440`
- Modify: `apps/web/src/features/writing/components/WritingAssistantPane.tsx:165-225`
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx:445-470`
- Test: `apps/api/tests/test_latex_agent_react.py`
- Test: `apps/api/tests/test_drafts_endpoints.py`
- Test: `apps/web/src/features/writing/__tests__/WritingAssistantPane.test.tsx`

**Interfaces:**
- LangGraph ReAct agent tools: `create_file`, `edit_file`, `delete_file`, `read_file`, `list_files`, `query_library_graph_rag`, `recompile_latex`.
- `DraftService.undo_draft_snapshot`: toggles `undo` $\leftrightarrow$ `redo` in `previous_snapshot` JSON.
- `WritingAssistantPane`: removes duplicate emoji icon, toggles Hoàn tác / Khôi phục, supports draggable left resize handle.

- [ ] **Step 1: Write failing tests for LangGraph tools and Undo/Redo snapshot swap**
- [ ] **Step 2: Run backend tests to verify failure** (`uv run pytest apps/api/tests/test_drafts_endpoints.py apps/api/tests/test_latex_agent_react.py`)
- [ ] **Step 3: Implement LangGraph tools in `latex_agent.py` and snapshot swap in `draft_service.py`**
- [ ] **Step 4: Update `WritingAssistantPane.tsx` with Undo/Redo button and resizable drawer handle**
- [ ] **Step 5: Run backend and frontend tests to verify passing**
- [ ] **Step 6: Commit Task 4** (`git commit -m "feat(writing): introduce langgraph tool-calling agent, 2-way undo-redo, and resizable chat drawer"`)

---

### Task 5: Dashboard "Add Document Modal" Local PDF Upload & Library Deduplication

**Files:**
- Modify: `apps/web/src/features/sessions/components/AddDocumentModal.tsx:20-130`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1580-1600`
- Test: `apps/web/src/features/sessions/__tests__/AddDocumentModal.test.tsx`

**Interfaces:**
- Tab 3: `[ Tải lên PDF ]` with dropzone to upload directly into the session (`is_persistent = false`).
- Library Tab Filter: filters documents strictly by `is_persistent === true`, deduplicated by content hash or title.

- [ ] **Step 1: Write failing tests for local PDF upload tab and persistent library deduplication**
- [ ] **Step 2: Run frontend test to verify failure**
- [ ] **Step 3: Implement Tab 3 `[ Tải lên PDF ]` and deduplicated persistent filter in `AddDocumentModal.tsx`**
- [ ] **Step 4: Run frontend test to verify passing**
- [ ] **Step 5: Commit Task 5** (`git commit -m "feat(dashboard): add direct pdf upload tab and deduplicate library papers in modal"`)

---

### Task 6: Library Overhaul & Interactive LLM Wiki Knowledge Graph

**Files:**
- Create: `apps/api/src/api/v1/endpoints/library_graph.py`
- Modify: `apps/api/src/api/v1/endpoints/library.py`
- Create: `apps/web/src/features/library/components/KnowledgeGraphCanvas.tsx`
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Modify: `apps/web/src/features/library/api/libraryApi.ts`
- Test: `apps/api/tests/test_library_endpoints.py`
- Test: `apps/web/src/features/library/__tests__/KnowledgeGraphCanvas.test.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`

**Interfaces:**
- `GET /api/v1/library/graph?folder_id=...`: returns top-50 entity nodes and relationship edges for persistent documents.
- `KnowledgeGraphCanvas`: interactive SVG / Canvas force graph with node inspection.
- Tab toggle `[ 📄 Danh sách ]` | `[ 🕸️ Đồ thị Tri thức ]`.
- Floating GraphRAG Assistant FAB at bottom-right of `/library`.
- Save-time folder modal to select or create a folder.

- [ ] **Step 1: Write failing tests for `/library/graph` endpoint and KnowledgeGraphCanvas view toggle**
- [ ] **Step 2: Run backend & frontend tests to verify failure**
- [ ] **Step 3: Implement `GET /api/v1/library/graph` in backend**
- [ ] **Step 4: Implement `KnowledgeGraphCanvas.tsx` and integrate into `LibraryWorkspaceView.tsx`**
- [ ] **Step 5: Add GraphRAG Assistant FAB and Save-to-folder modal in `/library`**
- [ ] **Step 6: Run tests to verify passing**
- [ ] **Step 7: Commit Task 6** (`git commit -m "feat(library): introduce interactive llm wiki knowledge graph canvas and assistant fab"`)

---

### Task 7: Comprehensive Verification Gates & VPS Deployment Sync

**Files:** All modified files across frontend and backend.

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**
  - Run: `uv run ruff check . && uv run ruff format --check .`
  - Expected: Exit code 0, 0 errors.

- [ ] **Step 2: Gate 2 - Backend Pytest**
  - Run: `uv run pytest`
  - Expected: 100% passed (276+ tests).

- [ ] **Step 3: Gate 3 - Frontend Vitest**
  - Run: `npm --prefix apps/web run test`
  - Expected: 100% passed (all suites).

- [ ] **Step 4: Gate 4 - Frontend Production Build**
  - Run: `npm --prefix apps/web run build`
  - Expected: Exit code 0, no TypeScript errors.

- [ ] **Step 5: Headless Browser Visual Audit**
  - Capture verification screenshots:
    1. `screenshot_writing_error_highlight.png`: Check gutter error icon and line highlight.
    2. `screenshot_writing_resizable_chat.png`: Check resizable drawer and Undo/Redo button.
    3. `screenshot_dashboard_add_document_upload_tab.png`: Check Tab 3 Tải lên PDF.
    4. `screenshot_library_llm_wiki_graph.png`: Check Knowledge Graph Canvas view and GraphRAG Assistant FAB.

- [ ] **Step 6: Task 7 Deployment Sync**
  - Run: `bash scripts/deploy_to_vps.sh --fast || true`
  - Expected: Exit code 0.

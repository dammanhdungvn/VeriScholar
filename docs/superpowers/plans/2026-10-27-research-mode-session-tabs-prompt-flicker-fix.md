# Research Mode Bugfixes: Session Persistence, Multi-Tab Staging, Prompt Execution & Anti-Flicker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triệt để khắc phục 4 lỗi trọng yếu trong chế độ Nghiên cứu (`/dashboard`): lỗi không tạo/lưu phiên chat mới ở mục Gần đây, lỗi thiếu tab bài báo khi tải lên nhiều file ($\le 5$), lỗi không chạy prompt đi kèm, và lỗi màn hình PDF Canvas nhấp nháy liên tục khi cuộn trang.

**Architecture:** Kiến trúc tương tác toàn trình giữa FastAPI/PostgreSQL (Backend) và React 19/Zustand/PDF.js/TanStack Query (Frontend). Chuẩn hóa luồng nạp đa tài liệu (Multi-file Ingestion), cơ chế vô hiệu hóa cache (Query Invalidation), giới hạn trần 5 tài liệu/phiên, và tách biệt hoàn toàn trạng thái cuộn viewport khỏi vòng đời kết xuất HTML5 Canvas của PDF.js.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+, React 19, Vite, TanStack Query v5, Zustand, PDF.js, Tailwind CSS, Vitest, Pytest.

**Spec:** `docs/specs/03-sessions-and-deep-reading.md`, `docs/specs/02-discovery-and-documents.md`, `docs/PRD/PRD-03-visual-evidence-grounding-and-canvas.md`.

## Global Constraints
- Tuân thủ nghiêm ngặt 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm run build`).
- TDD bắt buộc: Viết test đỏ $\rightarrow$ Viết code xanh tối thiểu $\rightarrow$ Refactor.
- Hexagonal Isolation: Không làm rò rỉ web framework/ORM vào `packages/core`.
- Invariant: Giới hạn tối đa 5 tài liệu/phiên ($N_{\text{docs}} \le 5$). Ẩn hoàn toàn nút thêm bài báo khi đủ 5 bài.
- 60fps Scrolling: Cuộn PDF không được phép xóa trắng canvas hay gây giật/nháy màn hình.

## Review Focus
1. **Database NotNullViolation on Reference Extraction:** Chèn `ReferenceItemModel` vào DB mà thiếu `user_id` dẫn tới crash 500 toàn bộ quy trình parse.
2. **Premature Navigation Race Condition:** Điều hướng router sớm trước khi các tệp phụ upload xong làm đứt gãy polling ingestion và hủy stream chat.
3. **Stale Session Query Cache:** Tạo session qua client API thuần không invalidate query key khiến danh sách "Gần đây" không cập nhật.
4. **Canvas Clearing on Viewport Observer Trigger:** Thuộc tính `currentPageNumber` kích hoạt re-render canvas không cần thiết làm canvas bị reset trắng liên hồi.
5. **Session Capacity Overflow:** Người dùng cố tình kéo thả hoặc upload vượt quá trần 5 tài liệu.

---

### Task 1: Backend Fix `ReferenceItemModel` User ID Integrity

**Files:**
- Modify: `apps/api/src/api/services/document_service.py:1470-1486`
- Test: `apps/api/tests/unit/test_document_references_user_id.py`

**Interfaces:**
- Consumes: `doc: DocumentModel`, `extracted_refs: list[ExtractedReference]`
- Produces: `ReferenceItemModel(user_id=doc.user_id, document_id=document_id, ...)`

- [x] **Step 1: Write the failing unit test**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement fix in `apps/api/src/api/services/document_service.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add apps/api/src/api/services/document_service.py apps/api/tests/unit/test_document_references_user_id.py
git commit -m "fix(api): assign user_id to ReferenceItemModel in extract_references"
```

---

### Task 2: Multi-File Staging, Session Invalidation & Safe Prompt Dispatch in `DashboardContainer`

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx:243-305`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardContainer.test.tsx`

**Interfaces:**
- Consumes: `prompt: string`, `files: File[]`, `queryClient`
- Produces: Sequence an toàn: Tạo phiên $\rightarrow$ Invalidate sessions list $\rightarrow$ Upload tất cả file (1..N) $\rightarrow$ Cập nhật `openDocumentIds` $\rightarrow$ Navigate $\rightarrow$ Gửi prompt an toàn.

- [x] **Step 1: Write/Update the failing test**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement fix in `apps/web/src/features/dashboard/components/DashboardContainer.tsx`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add apps/web/src/features/dashboard/components/DashboardContainer.tsx apps/web/src/features/dashboard/__tests__/DashboardContainer.test.tsx
git commit -m "fix(dashboard): orchestrate atomic multi-file upload, query invalidation and prompt execution"
```

---

### Task 3: Enforce $\le 5$ Papers Limit & Hide Upload Button in `DocumentTabBar`

**Files:**
- Modify: `apps/web/src/features/reader/components/DocumentTabBar.tsx:157-181`
- Modify: `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx:88-108`
- Create Test: `apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx`

**Interfaces:**
- Consumes: `openDocumentIds: string[]` (tối đa 5)
- Produces: UI Tab Bar tự động ẩn nút `+` khi `openDocumentIds.length >= 5`; hiển thị lại khi $< 5$.

- [x] **Step 1: Write the failing unit test**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement fix in `DocumentTabBar.tsx` & `DashboardChatInputBox.tsx`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/components/DocumentTabBar.tsx apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx apps/web/src/features/reader/__tests__/DocumentTabBar.test.tsx
git commit -m "feat(reader): strictly hide add document button when session reaches 5 papers cap"
```

---

### Task 4: Eliminate PDF Canvas Strobe / Flickering on Scroll in `PdfPageCanvas`

**Files:**
- Modify: `apps/web/src/features/reader/components/PdfPageCanvas.tsx:100-210, 285-300`
- Test: `apps/web/src/features/reader/__tests__/PdfPageCanvas.test.tsx`

**Interfaces:**
- Consumes: `pdfDoc: PDFDocumentProxy | null`, `pageNumber: number`, `zoomRatio: number`, `rotationDeg: number`
- Produces: 60fps stable rendering. Cuộn trang không xóa trắng canvas, không hiển thị lại spinner trên trang đã render.

- [x] **Step 1: Write unit test for Render Stability**
- [x] **Step 2: Run test to verify render behavior**
- [x] **Step 3: Implement fix in `PdfPageCanvas.tsx`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/components/PdfPageCanvas.tsx apps/web/src/features/reader/__tests__/PdfPageCanvas.test.tsx
git commit -m "fix(reader): eliminate canvas flicker and clearing during viewport scrolling"
```

---

### Task 5: End-to-End Verification across the 4 Mandatory Verification Gates

**Files:**
- Repository-wide verification across all 4 gates.

- [x] **Step 1: Run Gate 1 (Python Linter & Formatter)**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors, 0 format warnings. (Status: PASSED - 158 files checked)

- [x] **Step 2: Run Gate 2 (Backend Unit & Integration Tests)**
Run: `uv run pytest`
Expected: 100% tests passed. (Status: PASSED - 102 passed in 7.64s)

- [x] **Step 3: Run Gate 3 (Frontend Unit Tests)**
Run: `npm --prefix apps/web run test`
Expected: 100% tests passed. (Status: PASSED - 16 test files, 72 tests passed)

- [x] **Step 4: Run Gate 4 (Production Build Frontend)**
Run: `npm --prefix apps/web run build`
Expected: Exit code 0, build thành công thư mục `apps/web/dist/`. (Status: PASSED - built in 1.91s)

- [x] **Step 5: Final Clean Commit & Summary**
Ghi nhận kết quả xác minh toàn diện, chuẩn bị bàn giao.

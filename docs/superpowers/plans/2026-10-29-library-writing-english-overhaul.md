# Library & Writing Overhaul, English UI, and Navigation Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize VeriScholar's UI across `/dashboard`, `/library`, and `/writing` by switching to English-first copy, implementing a floating context selection popover in the LaTeX editor, fixing library-to-reader paper navigation, replacing the parse config modal with automatic defaults, introducing Folder Cards with full CRUD operations and paper drill-down, making Knowledge Graph a primary ribbon tab, eliminating sidebar context menu clipping, and seeding 12 landmark LLM papers into the knowledge graph.

**Architecture:** Frontend components follow React 19 + Tailwind CSS + Lucide icons with strict TypeScript types in `apps/web/`. Backend services in `apps/api/` and `packages/core/` preserve Hexagonal Architecture isolation. All data mutations integrate with existing REST endpoints for sessions, documents, and folders.

**Tech Stack:** React 19, TypeScript 5.9, Tailwind CSS 4, Zustand, TanStack Query 5, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+ pgvector, Vitest, Pytest.

**Spec:** [`docs/superpowers/specs/2026-10-29-library-writing-english-overhaul-design.md`](../specs/2026-10-29-library-writing-english-overhaul-design.md)

## Global Constraints

- **Language Policy:** All user-facing UI labels, placeholders, buttons, and system tooltips must use concise, idiomatic academic English.
- **Radical Minimalism (Rule 6):** No developer chunking parameters, internal IDs, or redundant badges on user interfaces.
- **Hexagonal Isolation (Rule 2):** Pure domain logic in `packages/core/` must never import web frameworks or I/O adapters.
- **The 4 Verification Gates (Rule 4):** Every task must pass:
  1. `uv run ruff check . && uv run ruff format --check .`
  2. `uv run pytest`
  3. `npm --prefix apps/web run test`
  4. `npm --prefix apps/web run build`
- **In-Plan VPS Sync Protocol (Rule 9):** Run `bash scripts/deploy_to_vps.sh --fast || true` after every successful task commit.

## Review Focus

1. **Text selection popover boundary clipping:** When selecting text near the top or edges of the editor, popover must not render off-screen or trigger horizontal scroll.
2. **Library paper click navigation failure:** Selecting a paper from `/library` must guarantee that `sessionsApi.addDocumentToSession` completes before navigating to `/dashboard/:sessionId`, preventing empty ghost states.
3. **Sidebar context menu upward flip:** Clicking `...` on sessions near the bottom of the list must flip upward (`bottom-full mb-1`) without clipping inside the scroll container.
4. **Folder drill-down navigation state:** Navigating into a folder and back must preserve search filters and breadcrumbs cleanly without memory leaks.
5. **Seeded papers integrity:** The 12 landmark LLM papers must have valid document IDs, storage blobs, and citation references so the Knowledge Graph renders interconnected clusters without graph crashes.

---

### Task 1: Sidebar Upward Placement & English Navigation Alignment

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`

- [ ] **Step 1.1: Write failing Vitest test for upward context menu and English labels**
  - In `apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`, add test verifying that when a session menu is triggered near the bottom, the dropdown renders with upward positioning classes (`bottom-full mb-1` or `data-placement="top"`), and navigation labels are in English (`New`, `My Library`, `Writing`, `Discovery`, `Recents`, `Pin`, `Unpin`, `Rename`, `Delete`).

- [ ] **Step 1.2: Run test to verify failure**
  - Run: `npm --prefix apps/web run test src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
  - Verify failure due to missing English strings or downward-only placement.

- [ ] **Step 1.3: Implement adaptive menu placement and English labels in `DashboardTaskbar.tsx`**
  - Calculate menu position: if the session index is in the last 3 items of `displayedSessions` or item's `getBoundingClientRect().bottom > window.innerHeight - 200`, render popup container with `bottom-full mb-1 origin-bottom-right` instead of `top-full mt-1 origin-top-right`.
  - Ensure parent containers have adequate `z-index` and overflow handling so dropdown floats above footer rail.
  - Update all labels and placeholders to English:
    - `"Tìm phiên..."` $\rightarrow$ `"Search sessions..."`
    - `"Ghim"` $\rightarrow$ `"Pin"`, `"Bỏ ghim"` $\rightarrow$ `"Unpin"`
    - `"Đánh dấu chưa đọc"` $\rightarrow$ `"Mark as unread"`, `"Đánh dấu đã đọc"` $\rightarrow$ `"Mark as read"`
    - `"Đổi tên"` $\rightarrow$ `"Rename"`, `"Xóa"` $\rightarrow$ `"Delete"`
    - `"Lưu trữ"` $\rightarrow$ `"Archived"`
    - `"Không tìm thấy phiên"` $\rightarrow$ `"No sessions found"`
    - `"Chưa có phiên nào"` $\rightarrow$ `"No sessions yet"`

- [ ] **Step 1.4: Run Vitest and Gate 1-4 checks**
  - Run: `npm --prefix apps/web run test src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
  - Ensure 100% tests pass.

- [ ] **Step 1.5: Commit and sync to VPS**
  - Commit: `git commit -m "feat(ui): add upward context menu placement and english labels in sidebar"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 2: Floating Text Selection Popover & Compile Header Cleanup in `/writing`

**Files:**
- Create: `apps/web/src/features/writing/components/WritingSelectionPopover.tsx`
- Modify: `apps/web/src/features/writing/components/WritingEditorPane.tsx`
- Modify: `apps/web/src/features/writing/components/WritingHeaderBar.tsx`
- Modify: `apps/web/src/features/writing/components/WritingWorkspace.tsx`
- Test: `apps/web/src/features/writing/__tests__/WritingSelectionPopover.test.tsx`
- Test: `apps/web/src/features/writing/__tests__/WritingWorkspace.test.tsx`

- [ ] **Step 2.1: Write failing Vitest test for `WritingSelectionPopover`**
  - Create `apps/web/src/features/writing/__tests__/WritingSelectionPopover.test.tsx`.
  - Assert that when text is highlighted in editor, the floating popover renders with `Add to Chat` and `Ask AI` buttons, and triggering them calls the corresponding callback with the selected text.

- [ ] **Step 2.2: Run test to verify failure**
  - Run: `npm --prefix apps/web run test src/features/writing/__tests__/WritingSelectionPopover.test.tsx`

- [ ] **Step 2.3: Implement `WritingSelectionPopover.tsx`**
  - Build floating glassmorphism pill with `[Add to Chat]` and `[Ask AI]`.
  - Compute coordinates using selection range / textarea position, constrained within the editor bounds.
  - In `WritingEditorPane.tsx`:
    - Remove the bottom notification badge `Đã chọn ... ký tự [Thêm vào chat]`.
    - Integrate `<WritingSelectionPopover />` on mouseup/keyup when selection length $\ge 2$.
  - In `WritingHeaderBar.tsx`:
    - Remove the duplicate `Compile` button on the top-right header bar. Keep `Save` and `Export Bundle`.
    - Update remaining labels to English (`Save`, `Export`, `Files`, `Outline`, `Recompile`).

- [ ] **Step 2.4: Verify tests pass**
  - Run: `npm --prefix apps/web run test src/features/writing/__tests__/`
  - Ensure all writing tests pass.

- [ ] **Step 2.5: Commit and sync to VPS**
  - Commit: `git commit -m "feat(writing): add floating selection popover and remove duplicate compile button"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 3: Library Paper Selection & Deep Reading Session Binding Fix

**Files:**
- Modify: `apps/web/src/features/library/components/LibraryPage.tsx`
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryPaperSelectionNavigation.test.tsx`

- [ ] **Step 3.1: Write failing Vitest test for library paper navigation**
  - Create `apps/web/src/features/library/__tests__/LibraryPaperSelectionNavigation.test.tsx`.
  - Mock `sessionsApi.createSession` and `sessionsApi.addDocumentToSession`.
  - Render `LibraryPage`, simulate clicking a paper card, and assert that `sessionsApi.addDocumentToSession` is awaited with the newly created session ID and paper document ID before navigation.

- [ ] **Step 3.2: Run test to verify failure**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/LibraryPaperSelectionNavigation.test.tsx`

- [ ] **Step 3.3: Implement session-document binding in `LibraryPage.tsx`**
  - In `handleSelectDocument` of `LibraryPage.tsx`:
    ```typescript
    const newSession = await createSession(`Research: ${targetTitle}`);
    try {
      await sessionsApi.addDocumentToSession(newSession.id, {
        source_type: "document_id",
        document_id: doc.id,
      });
    } catch (err) {
      console.warn("Failed to attach document to session:", err);
    }
    useReaderStore.getState().setOpenDocumentIds([doc.id]);
    useReaderStore.getState().setActiveDocumentId(doc.id);
    selectSession(newSession.id);
    navigate(`/dashboard/${newSession.id}`);
    ```
  - Ensure `DashboardContainer.tsx` sets the active document without falling back to the empty dropzone when the session has documents.

- [ ] **Step 3.4: Verify tests pass**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/LibraryPaperSelectionNavigation.test.tsx`
  - Ensure all navigation tests pass.

- [ ] **Step 3.5: Commit and sync to VPS**
  - Commit: `git commit -m "fix(library): bind document to session before navigating to deep reader"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 4: Library Ribbon 3-Tab Restructuring & Elimination of Parse Config Modal

**Files:**
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Modify: `apps/web/src/features/documents/components/DocumentLibraryModal.tsx`
- Modify: `apps/web/src/features/library/types/index.ts`
- Test: `apps/web/src/features/library/__tests__/LibraryWorkspaceView.test.tsx`
- Test: `apps/web/src/features/library/__tests__/LibraryAndGraphRAG.test.tsx`

- [ ] **Step 4.1: Write failing Vitest test for 3-tab ribbon and absence of Parse Config**
  - Update `LibraryWorkspaceView.test.tsx` to assert:
    - Ribbon tabs are `All Papers`, `Folders`, and `Knowledge Graph`.
    - `SlidersHorizontal` / Parse Document modal trigger is NOT present in the DOM.
    - Labels are in English (`My Library`, `All Papers`, `Folders`, `Knowledge Graph`, `Upload PDF`).

- [ ] **Step 4.2: Run test to verify failure**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/LibraryWorkspaceView.test.tsx`

- [ ] **Step 4.3: Implement 3-tab structure and remove Parse Config in `LibraryWorkspaceView.tsx`**
  - Set tab type `type LibraryTab = "all" | "folders" | "graph"`.
  - Render ribbon with 3 tabs: `All Papers`, `Folders`, and `Knowledge Graph`.
  - When tab is `"graph"`, render `KnowledgeGraphCanvas` directly in main viewport.
  - Remove `selectedParseDoc`, `onOpenParseConfig`, `ParseConfigModal`, and `SlidersHorizontal` buttons.
  - Update all header text and empty state messages to English.

- [ ] **Step 4.4: Verify tests pass**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/`
  - Ensure 100% tests pass.

- [ ] **Step 4.5: Commit and sync to VPS**
  - Commit: `git commit -m "feat(library): add 3-tab ribbon layout and remove obsolete parse config modal"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 5: Folder Cards & Full CRUD Operations with Paper Drill-Down

**Files:**
- Create: `apps/web/src/features/library/components/FolderCard.tsx`
- Create: `apps/web/src/features/library/components/CreateFolderModal.tsx`
- Create: `apps/web/src/features/library/components/RenameFolderModal.tsx`
- Create: `apps/web/src/features/library/components/MoveToFolderModal.tsx`
- Modify: `apps/web/src/features/library/components/LibraryWorkspaceView.tsx`
- Modify: `apps/web/src/features/folders/api/foldersApi.ts`
- Test: `apps/web/src/features/library/__tests__/FolderCardsAndCrud.test.tsx`

- [ ] **Step 5.1: Write failing Vitest test for Folder Cards and CRUD**
  - Create `apps/web/src/features/library/__tests__/FolderCardsAndCrud.test.tsx`.
  - Test folder card rendering with title, paper count, and action menu.
  - Test clicking card drills down to paper list with breadcrumb.
  - Test Rename, Delete folder, and Move Paper to Folder flows.

- [ ] **Step 5.2: Run test to verify failure**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/FolderCardsAndCrud.test.tsx`

- [ ] **Step 5.3: Implement `FolderCard.tsx` and CRUD Modals**
  - `FolderCard.tsx`: Display folder title, paper count badge, date, and `...` menu with `Rename` and `Delete`.
  - `CreateFolderModal.tsx`: Simple dialog to enter folder title and create via `foldersApi.createFolder`.
  - `RenameFolderModal.tsx`: Dialog to update folder name via `foldersApi.updateFolder`.
  - `MoveToFolderModal.tsx`: Replaces the legacy Star modal with a clean dialog to select a target folder or unassign (`All Papers`), updating via `documentsApi` or `foldersApi.assignDocuments`.
  - In `LibraryWorkspaceView.tsx`:
    - In `"folders"` tab, render folder card grid with top `+ New Folder` button.
    - When `selectedFolderId` is set, render folder drill-down view: header with `<- Back to Folders`, folder title, paper count, and `+ Add Papers` button.
    - Render papers filtered to `doc.folder_id === selectedFolderId`.

- [ ] **Step 5.4: Verify tests pass**
  - Run: `npm --prefix apps/web run test src/features/library/__tests__/`
  - Ensure all folder CRUD tests pass.

- [ ] **Step 5.5: Commit and sync to VPS**
  - Commit: `git commit -m "feat(library): implement folder cards, paper drill-down and full crud operations"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 6: Landmark LLM Literature Seeding (12 Papers with Graph Citations)

**Files:**
- Create: `scripts/dev/seed_landmark_papers.py`
- Modify: `scripts/dev/seed.py`
- Create: `apps/api/tests/test_landmark_papers_seeding.py`

- [ ] **Step 6.1: Write failing Pytest test for landmark papers seeding**
  - Create `apps/api/tests/test_landmark_papers_seeding.py`.
  - Verify that seeding creates 12 landmark papers attached to the target user with valid storage blobs, document records (`is_persistent=True`), chunks, and interconnected citation edges.

- [ ] **Step 6.2: Run test to verify failure**
  - Run: `uv run pytest apps/api/tests/test_landmark_papers_seeding.py`

- [ ] **Step 6.3: Implement `scripts/dev/seed_landmark_papers.py`**
  - Define dataset of 12 landmark LLM papers:
    1. *Attention Is All You Need* (Vaswani et al., 2017)
    2. *BERT: Pre-training of Deep Bidirectional Transformers* (Devlin et al., 2018)
    3. *Language Models are Few-Shot Learners [GPT-3]* (Brown et al., 2020)
    4. *LoRA: Low-Rank Adaptation of Large Language Models* (Hu et al., 2021)
    5. *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al., 2022)
    6. *Chain-of-Thought Prompting in Neural Networks* (Wei et al., 2022)
    7. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (Lewis et al., 2020)
    8. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (Edge et al., 2024)
    9. *Toolformer: Language Models Can Teach Themselves to Use Tools* (Schick et al., 2023)
    10. *LLaMA: Open and Efficient Foundation Language Models* (Touvron et al., 2023)
    11. *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (Es et al., 2023)
    12. *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* (Rafailov et al., 2023)
  - Generate valid PDF binaries in CAS (`storage/blobs/`), insert `documents` with `is_starred=True` and `is_persistent=True`, create `document_chunks`, and establish cross-paper citation links in `reference_items` and `graph_nodes`/`graph_edges`.
  - Run the script against local database to seed the active user account (`dammanhdungvn@gmail.com`).

- [ ] **Step 6.4: Verify tests pass**
  - Run: `uv run pytest apps/api/tests/test_landmark_papers_seeding.py`
  - Ensure 100% tests pass.

- [ ] **Step 6.5: Commit and sync to VPS**
  - Commit: `git commit -m "feat(data): seed 12 landmark llm papers with citation graph edges"`
  - Sync: `bash scripts/deploy_to_vps.sh --fast || true`

---

### Task 7: Full 4-Gate Verification and Production Deployment

**Files:**
- Repository-wide verification across all modified files.

- [ ] **Step 7.1: Run Gate 1 (Ruff Linter & Formatter)**
  - Run: `uv run ruff check . && uv run ruff format --check .`
  - Ensure 0 errors.

- [ ] **Step 7.2: Run Gate 2 (Backend Pytest)**
  - Run: `uv run pytest`
  - Ensure all 280+ tests pass.

- [ ] **Step 7.3: Run Gate 3 (Frontend Vitest)**
  - Run: `npm --prefix apps/web run test`
  - Ensure all 217+ tests pass.

- [ ] **Step 7.4: Run Gate 4 (Frontend Production Build)**
  - Run: `npm --prefix apps/web run build`
  - Ensure 0 TypeScript or Vite bundling errors.

- [ ] **Step 7.5: Final VPS Deployment**
  - Run: `bash scripts/deploy_to_vps.sh --fast`
  - Verify live health check at `https://verischolar.duckdns.org/health`.

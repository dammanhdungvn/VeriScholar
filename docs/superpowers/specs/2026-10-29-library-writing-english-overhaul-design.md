# Design Document: Library & Writing Overhaul, English UI, and Navigation Alignment

- **Date:** 2026-10-29
- **Status:** Draft / In Review
- **Author:** Antigravity AI & Human Scholar
- **Target Release:** VeriScholar MVP v1.1

---

## 1. Intent & The Why

VeriScholar provides a scientific research copilot combining deep paper reading, Socratic reasoning, literature drafting, and personal knowledge graphs (LLM Wiki).
Feedback from real-world usage identified 11 UX friction points across `/dashboard`, `/library`, and `/writing`:
1. Disjointed text-selection in `/writing` (`Đã chọn ... ký tự [Thêm vào chat]`) rather than a modern Cursor/Medium-style floating toolbar directly above the selected text.
2. Duplicate compile buttons in `/writing` (both in the top header and above the PDF preview pane).
3. Clicking a paper in `/library` navigated to `/dashboard` with an empty reader ("Chưa có tài liệu nghiên cứu nào") due to missing session-document association.
4. UI inconsistency across `/dashboard`, `/writing`, and `/library` where layout paradigms differed.
5. Obsolete "Parse Document" configuration modal displaying internal chunk parameters (chunk size, overlap) that burden users instead of automatically using optimal defaults.
6. The Knowledge Graph (LLM Wiki) lacking sufficient landmark literature to show connected papers and community clusters.
7. Mixed Vietnamese technical terms that are less intuitive and verbose compared to standard English academic terms (`New`, `My Library`, `Writing`, `Deep Reading`, `All Papers`, `Folders`).
8. Awkward "Star Document" modal inside `/library` (where documents are already starred/saved) instead of a clean "Move to Folder" action.
9. Folder tab currently rendering a desktop split-pane rather than interactive Folder Cards with paper drill-down and full CRUD operations (Create, Read, Update/Rename, Delete).
10. Knowledge Graph toggle hidden in an obscure view-mode header dropdown rather than being a prominent first-class tab alongside `All Papers` and `Folders`.
11. Sidebar session action menu (`...`) getting clipped or rendered under the footer when triggering sessions near the bottom of the list.

The goal is to eliminate these friction points, align the interface with international standards (English-first, radical minimalism 80/20), and provide a unified, responsive scholarly workflow.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **G1 (Floating Context Toolbar):** Implement a sleek floating action pill hovering directly above selected text in both LaTeX editor and Reader (`[Add to Chat]`, `[Ask AI]`).
- **G2 (Single Recompile Action):** Remove duplicate top-bar compile button in `/writing`; standardize on the Overleaf-style green `Recompile` split button above the PDF pane.
- **G3 (Seamless Library Paper Open):** Clicking any paper in `/library` immediately associates the document with the session in DB (`sessionsApi.addDocumentToSession`) and opens it in Deep Reading mode with 0 latency or empty fallback.
- **G4 (English-First UI Localization):** Switch all user-facing interface text across navigation, headers, buttons, placeholders, dialogs, and states to concise, professional academic English.
- **G5 (Remove Parse Config):** Completely eliminate `ParseConfigModal` and the `SlidersHorizontal` button on paper cards. Ingestion automatically defaults to optimal parameters (`chunk_size=512, chunk_overlap=50, extract_tables=True`).
- **G6 (Folder Cards & Full CRUD):** Redesign `Folders` tab into a modern Folder Card grid. Clicking a card opens the folder's paper list with breadcrumb (`<- Back to Folders`). Support full CRUD for Folders (Create, Rename, Delete) and Papers (Upload/Add, Move to Folder, Delete from Library).
- **G7 (Knowledge Graph Tab):** Elevate Knowledge Graph to a primary ribbon tab: `[ All Papers ] [ Folders ] [ Knowledge Graph ]`.
- **G8 (Adaptive Upward Context Menu):** Dynamic dropdown placement in `DashboardTaskbar` that opens upwards (`bottom-full mb-1`) when near the bottom of the sidebar to avoid clipping.
- **G9 (Landmark LLM Literature Seeding):** Seed 10–15 landmark papers (Attention Is All You Need, BERT, GPT-3, LoRA, Toolformer, Chain-of-Thought, ReAct, RAG, GraphRAG, LLaMA) with cross-entity bibliometrics into the user's library.

### Non-Goals
- Replacing the core CLSI LaTeX compilation backend (CLSI + E2B engine remains unchanged).
- Re-architecting database schemas (existing `folders`, `documents`, `research_sessions`, `session_documents` tables already support required fields).
- Supporting multi-language i18n runtime toggles (the system will adopt standard academic English directly).

### Anti-Goals
- Cluttering the interface with developer-centric controls (no chunk sliders, token counts, or technical error codes).
- Breaking existing test coverage or changing core business rules in `packages/core`.

---

## 3. Constraints

- **Hexagonal Architecture:** Frontend changes must remain in `apps/web/`; backend changes in `apps/api/` and `packages/core/` must strictly respect boundary isolation.
- **Radical Minimalism (Rule 6):** No unnecessary badges, no technical jargon in user-facing UI, clean typography using Anthropic Sans & Serif.
- **Automated Verification:** All changes must pass the 4 Verification Gates (`ruff`, `pytest`, `vitest`, `vite build`) and auto-sync to VPS via `scripts/deploy_to_vps.sh --fast`.

---

## 4. Approaches Considered & Trade-Offs

### Approach 1: Incremental Patching (Ad-hoc component updates)
- *Pros:* Faster to make individual tweaks.
- *Cons:* Leaves UI inconsistencies across routes (`/dashboard`, `/writing`, `/library`), prone to lingering Vietnamese strings and fragmented state management.

### Approach 2: Unified Design Alignment (Chosen Approach)
- Standardize layout patterns across all three primary workspaces (`/dashboard`, `/writing`, `/library`) using `AppLayout`, a consistent header hierarchy, and matching chat containers.
- Reorganize `/library` into a 3-tab layout (`All Papers` | `Folders` | `Knowledge Graph`), with Folder Cards and dedicated CRUD modals.
- Implement reusable floating text-selection popover for editor and reader.
- Switch entire UI copy to academic English.
- *Pros:* Clean, maintainable architecture, 100% visual and interactive parity, radical minimalism compliant.
- *Cons:* Touches multiple frontend components and requires updating corresponding Vitest test assertions.

---

## 5. Detailed Component Specifications

### 5.1 Floating Context Selection Popover (`/writing` & Reader)
- Replaces the bottom badge `Đã chọn ... ký tự [Thêm vào chat]` in `WritingEditorPane.tsx`.
- Listens to selection events in the editor textarea. When text is highlighted ($L \ge 2$ chars), computes coordinates using textarea caret coordinates.
- Displays a floating pill hovering directly above the selection with dark glassmorphism styling (`bg-zinc-900/90 text-white rounded-lg shadow-lg border border-white/10 px-2 py-1 text-xs flex items-center gap-2 animate-in fade-in zoom-in-95`):
  - **`Add to Chat`**: appends selected excerpt wrapped in markdown quotes to the chat input without clearing focus.
  - **`Ask AI`**: appends excerpt and focuses input with prompt placeholder `"Ask about this section..."`.
- *PDF Reader Scoping (Builder Check Call):* In the Deep Reading PDF viewer, `ScholarSelectionMenu` is preserved to maintain bounding-box coordinates (`bbox`) grounding and citation anchors, while its labels are localized to English (`Add to Chat`, `Copy Citation`, `Add Note`).

### 5.2 Header Cleanup in `/writing`
- In `WritingHeaderBar.tsx`, remove the duplicate `Compile` button on the top-right.
- Keep `Save` and `Export` in `WritingHeaderBar`.
- Standardize compilation trigger on `WritingPreviewPane.tsx`: the green Overleaf-style `Recompile` split button with dropdown for `Clear cache & Recompile`.

### 5.3 Library Navigation & Paper Selection Fix
- In `LibraryPage.tsx` and `LibraryWorkspaceView.tsx`:
  - When user clicks a paper card, execute:
    ```typescript
    const newSession = await createSession(`Research: ${doc.title || doc.filename}`);
    await sessionsApi.addDocumentToSession(newSession.id, {
      source_type: "document_id",
      document_id: doc.id,
    });
    useReaderStore.getState().setOpenDocumentIds([doc.id]);
    useReaderStore.getState().setActiveDocumentId(doc.id);
    navigate(`/dashboard/${newSession.id}`);
    ```
  - This ensures the database persists the session-document relationship so `/dashboard` immediately renders the PDF canvas without ghost fallbacks.

### 5.4 Elimination of Parse Config Modal
- Delete/deprecate `ParseConfigModal.tsx` from `LibraryWorkspaceView.tsx` and `DocumentLibraryModal.tsx`.
- Remove the `SlidersHorizontal` settings button on paper cards.
- Background ingestion automatically applies standard optimal presets (`chunk_size: 512, chunk_overlap: 50, extract_tables: true`).

### 5.5 Library 3-Tab Structure, Folder Cards & CRUD Actions
- Ribbon tabs in `LibraryWorkspaceView.tsx`:
  - `All Papers` (`all`): Card grid of all starred/persistent papers with action menu (`Move to Folder`, `Remove`).
  - `Folders` (`folders`): Grid of Folder Cards (`FolderCard.tsx`).
    - Card shows folder title, description, paper count badge, creation date, and action menu (`Rename`, `Delete`).
    - Top bar has `+ New Folder` button opening `CreateFolderModal`.
    - Clicking a card enters drill-down mode (`selectedFolderId = folder.id`), displaying the papers inside that folder with a header `<- Back to Folders | [Folder Name]`.
    - *Folder Paper Management (Builder Check Call):* The folder drill-down provides a dual-action `Add Papers` dropdown/modal: (A) `Upload New PDF` directly into this folder, or (B) `Select from Library` to move existing papers into this folder.
  - `Knowledge Graph` (`graph`): Full-height interactive `KnowledgeGraphCanvas` with zoom/pan and node inspector.
- Replaces "Star Document" modal with `MoveToFolderModal.tsx`:
  - Clean selector of available folders or `[+] Create new folder`.
  - Action button: `Move to Folder`.

### 5.6 English Localization Standard
- **Sidebar:** `New`, `My Library`, `Writing`, `Discovery`, `Recents`, `Pinned`, `Mark as Read`, `Mark as Unread`, `Rename`, `Delete`, `Account Settings`, `Sign Out`.
- **Dashboard / Reader:** `Deep Reading`, `Context Table`, `References`, `Socratic Reasoning`, `Ask AI...`, `Send`, `Stop Generation`, `Open Document`, `Upload PDF`.
- **Writing:** `Editor`, `Preview`, `Recompile`, `Clear Cache & Recompile`, `Files`, `Assets`, `AI Assistant`, `Undo Changes`, `Redo`.
- **Library:** `My Library`, `All Papers`, `Folders`, `Knowledge Graph`, `New Folder`, `Move to Folder`, `Delete`, `No documents found`, `Upload PDF to start researching`.

### 5.7 Sidebar Menu Overflow & Upward Placement
- In `DashboardTaskbar.tsx`, update context menu rendering:
  - Detect button vertical position relative to viewport / container height.
  - If triggering session is in the lower 40% of the viewport or index is among the last 3 items, render with `bottom-full mb-1` instead of `top-full mt-1`.
  - Ensure parent containers have proper stacking context so dropdown floats above footer rail.

### 5.8 Landmark Papers Seeding
- *Target & Execution (Builder Check Call):* The 12 landmark LLM papers will be seeded directly into the current active user's account (`dammanhdungvn@gmail.com`) and integrated into `scripts/dev/seed.py` for persistent environment reproducibility.
- Papers will be backed by real/valid PDFs and metadata extracted to form rich citation edges in `reference_items` and `graph_nodes`/`graph_edges`:
  1. *Attention Is All You Need* (Vaswani et al.)
  2. *BERT: Pre-training of Deep Bidirectional Transformers* (Devlin et al.)
  3. *Language Models are Few-Shot Learners [GPT-3]* (Brown et al.)
  4. *LoRA: Low-Rank Adaptation of Large Language Models* (Hu et al.)
  5. *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al.)
  6. *Chain-of-Thought Prompting in Neural Networks* (Wei et al.)
  7. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (Lewis et al.)
  8. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (Edge et al.)
  9. *Toolformer: Language Models Can Teach Themselves to Use Tools* (Schick et al.)
  10. *LLaMA: Open and Efficient Foundation Language Models* (Touvron et al.)
  11. *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (Es et al.)
  12. *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* (Rafailov et al.)

---

## 6. What's Left to the Builder

- Exact micro-animations and tailwind transition classes for the floating selection pill.
- Exact icon choices for Folder Card actions (lucide-react `Folder`, `FolderPlus`, `MoreVertical`, `Pencil`, `Trash2`).
- Mocking or handling tests in Vitest for updated tab names (`All Papers`, `Folders`, `Knowledge Graph`).

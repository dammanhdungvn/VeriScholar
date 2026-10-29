# Writing Agentic Tools, LaTeX Error Visual Highlighter, and Library LLM Wiki Knowledge Graph Design

> **Document Type:** Technical Specification & Architectural Design  
> **Status:** Approved by User  
> **Target Date:** 2026-10-29  
> **Author:** Antigravity (Advanced Agentic Pair Programmer)

---

## 1. Intent & The Why

VeriScholar aims to provide a world-class, frictionless academic research and writing experience. Through real-world testing, several concrete usability, correctness, and architectural gaps have been identified across three core modules:

1. **LaTeX Writing Workspace (`/writing`):**
   - **401 Unauthorized on `preview.pdf`:** PDF.js loads the preview URL directly without the `Authorization: Bearer <token>` header, preventing the user from viewing compiled drafts.
   - **Missing Syntax Error Line Highlighting:** When LaTeX compilation fails, the compiler reports a generic `Dòng 1, Cột 0 [COMPILATION_FAILED]` because the log parser defaults to line 1 instead of extracting the real error line (e.g. `! LaTeX Error: ... l.42`). Furthermore, the code editor lacks visual gutter markers, red line highlights, and click-to-jump navigation.
   - **Cluttered & Inconsistent Controls:** Unnecessary buttons (`<-`, `Files`, `v1`, `syncTex`), lack of an "unhide sidebar" icon when the file tree is collapsed, missing file close (`X`) buttons on tabs, and line counts (`106 dòng`) crowding the tab bar.
   - **AI Assistant Lacks Real Capabilities ("Tools/Chân tay"):** The assistant currently runs on rigid keyword heuristics instead of an autonomous tool-calling agent. It cannot create, edit, delete, or list project files, nor recompile LaTeX on demand.
   - **AI Chat UX Flaws:** Duplicate icons for Undo (`<RotateCcw>` + emoji), lack of a Redo capability if the user accidentally reverts, skewed fixed width causing CSS layout distortion, and non-resizable chat drawer.
   - **Asset Management Redundancy:** The asset modal features a massive redundant empty-state container below the dropzone and only supports uploading a single file at a time.

2. **Session Document Onboarding (`/dashboard`):**
   - **Missing Local PDF Upload in Modal:** The "Thêm tài liệu (0/5)" modal only offers "Thư viện" and "Đường dẫn (URL)", lacking direct local file drag-and-drop / upload into the active session.
   - **Duplicated & Unfiltered Library List:** The modal queries raw database records without filtering for persistent papers (`is_persistent = true`), displaying cluttered temporary test records and duplicate filenames.

3. **Academic Library & GraphRAG (`/library`):**
   - **Broken Library Upload Flow:** Files uploaded directly in `/library` fail to display because they are not marked `is_persistent = true`.
   - **Folder Organization & Save-Time Categorization:** Users need to organize papers into folders, and whenever clicking "Save" across the platform, they should be able to select an existing folder or create a new one on the fly.
   - **Andrej Karpathy LLM Wiki Paradigm:** Transitioning from static search inputs to a **compounding personal knowledge base**:
     - An **Interactive Knowledge Graph View** (interlinked papers, extracted concept nodes, and relationship edges).
     - A **Floating GraphRAG Assistant (FAB)** at the bottom-right for conversational multi-document Q&A.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- **100% Zero 401 Errors:** In all PDF preview tasks, Bearer token is properly attached via `getCachedPdfDocument`.
- **Accurate LaTeX Log Error Extraction & Editor Jump:** Regex-based log parser extracts exact line numbers and messages; editor highlights the faulty line with red gutter icon, subtle row tint, and click-to-scroll navigation from the error banner.
- **Overleaf-Grade Radical Minimalist Writing Header & Tabs:** File tabs have `X` close buttons (hover red), no line counts; Header removes `<-`, `Files`, `v1`, `syncTex`; Sidebar collapse state preserves a sleek `PanelLeftOpen` icon to unhide.
- **Autonomous Tool-Calling AI Coauthor Agent:** LangGraph ReAct agent bound with concrete LLM tools (`create_file`, `edit_file`, `delete_file`, `read_file`, `list_files`, `recompile_latex`, `query_library_graph_rag`).
- **Safe 2-Way Undo/Redo & Resizable Chat:** Snapshot management enabling seamless toggle between Undo and Redo; draggable left resize handle on the chat drawer.
- **Multi-File Asset Upload & Clean Asset Modal:** Input supports `multiple`, concurrent batch uploads, and eliminates the redundant empty-state box.
- **Dashboard Add Document Modal Enhancement:** Add direct local PDF upload tab; filter library documents strictly by `is_persistent = true` with title/hash deduplication.
- **Library GraphRAG & LLM Wiki:** Upload from library marks `is_persistent = true`; folder creation & moving; Save modal with folder selection; dual-mode `[ Danh sách ]` | `[ Đồ thị Tri thức ]`; floating GraphRAG Assistant FAB.

### Non-Goals
- Full rewrite of Monaco / CodeMirror editor (the current lightweight, responsive textarea editor is retained and enhanced with line-level error navigation).
- Changing backend database relational schema (utilizing existing `DocumentModel`, `FolderModel`, `DraftModel`, `GraphEntityModel`, `GraphRelationshipModel`).

### Anti-Goals
- No technical jargon, hex color codes, or algorithm names exposed to users (Rule 6).
- No violation of Hexagonal Architecture: `packages/core/` remains pure Python stdlib + Pydantic (Rule 2).
- No disruptive blocking modals during AI edits: User confirmed **Approach A** (direct application with 1-click Undo/Redo).

---

## 3. Approaches Considered & Selected

### AI Assistant Code Editing Strategy
- **Approach A (Selected): Direct Editor Execution with 1-Click Undo/Redo**
  - *Mechanism:* AI calls `edit_file` / `create_file`, updates editor state, triggers recompile, and captures a `previous_snapshot`.
  - *User Experience:* Instant, fluid, matching Cursor and modern agentic Overleaf workflows. If the user dislikes the AI output or pressed undo by mistake, the header button toggles `Undo` $\leftrightarrow$ `Redo`.
  - *Trade-off:* Requires robust snapshot swapping in `draft_service.py`, which is fully supported by our transaction model.

- **Approach B (Rejected): Diff Preview Modal with Manual Accept / Reject**
  - *Trade-off:* High interaction friction, tedious for multi-file or multi-section modifications.

---

## 4. Architectural & Component Specifications

### 4.1. LaTeX Error Log Parser & Editor Highlighting
- **Backend Log Parser (`packages/core/src/core/services/latex_compiler.py` & `apps/api/src/api/services/clsi_latex_compiler.py`):**
  - Parse error lines with regex patterns:
    ```python
    re.compile(r"^!\s+(?:LaTeX Error:|Package \w+ Error:|Undefined control sequence\.)\s*(.*?)(?:\nl\.(\d+)|$)", re.MULTILINE | re.DOTALL)
    re.compile(r"(?:main\.tex|\.tex):(\d+):\s*(.*)")
    re.compile(r"^l\.(\d+)\s+(.*)")
    ```
  - Map extracted line numbers into `LatexSyntaxError(line=extracted_line, message=clean_msg, rule="SYNTAX_ERROR")`.
- **Frontend Editor (`apps/web/src/features/writing/components/WritingEditorPane.tsx`):**
  - Gutter renders a red `AlertTriangle` / badge on faulty lines.
  - Clicking on an error card in the bottom error banner scrolls the textarea smoothly to `lineHeight * (line - 1)` and flashes a highlight.

### 4.2. Overleaf Minimalist Cleanups (`/writing`)
- **Tabs:** Remove `({lineCount} dòng)`. Add `X` button on active file tab with `hover:text-red-500` to close custom files.
- **Header:** Remove `<-` (Link to dashboard), `Files` button, and `v1` badge from `WritingHeaderBar.tsx`.
- **Sidebar Toggle:** When `isFileTreeOpen === false`, render a sticky icon button `<PanelLeft className="w-4 h-4 text-primary" />` on the tab strip to unhide sidebar.
- **SyncTeX:** Remove unused forward `SyncTeX` button from `WritingEditorPane.tsx`.

### 4.3. Multi-File Asset Modal (`DraftAssetManagementModal.tsx`)
- Add `multiple` to `<input type="file" multiple />`.
- Handle batch file uploads in `handleDrop` and `handleFileChange` via `Promise.all`.
- Remove the redundant `Chưa có asset nào trong bản thảo` lower container when assets array is empty, letting the dropzone remain the clean primary visual focus.

### 4.4. AI Assistant LangGraph Tool-Calling Engine & Project Files
- **Project Files Scope:**
  - The core editable LaTeX project documents are `main.tex` and `references.bib` (which map to `content` and `bib_content` in `DraftModel`).
  - Auxiliary project files (styles `.sty`, classes `.cls`, or sub-tex files) and figures are stored in `draft_assets`.
  - LangGraph Tools:
    1. `create_file(filename: str, content: str)`: Creates/initializes a project file. If `references.bib` or `main.tex`, updates the primary draft content; if auxiliary, registers in `draft_assets`.
    2. `edit_file(filename: str, content: str)`: Updates `main.tex`, `references.bib`, or asset file.
    3. `delete_file(filename: str)`: Deletes auxiliary file from assets (protecting `main.tex`).
    4. `read_file(filename: str)`: Reads content of `main.tex`, `references.bib`, or asset.
    5. `list_files()`: Returns all project files (`main.tex`, `references.bib`, and all assets in `draft_assets`).
    6. `query_library_graph_rag(query: str, top_k: int = 5)`: Tra cứu tri thức từ thư viện.
    7. `recompile_latex(clear_cache: bool = False)`: Tự động chạy biên dịch và kiểm tra lỗi.
  - Agent uses Gemini / OpenAI from environment variables (`.env`) via LangChain / LangGraph standard `bind_tools`.
  - Stream tool execution status (`✍️ Đang sửa main.tex`, `⚙️ Đang biên dịch...`) and conversational responses.

- **Undo / Redo 2-Way Snapshot Architecture (Zero DB Migration):**
  - `DraftModel.previous_snapshot` is a `JSONType` column.
  - Structure:
    ```json
    {
      "undo": { "content": "...", "bib_content": "...", "saved_at": "..." },
      "redo": { "content": "...", "bib_content": "...", "saved_at": "..." }
    }
    ```
  - When AI applies an edit: current state is pushed to `snapshot["undo"]`, and `snapshot["redo"]` is cleared.
  - `POST /api/v1/drafts/{id}:undo` toggles or accepts `{"action": "undo" | "redo"}`:
    - On undo: current state is saved to `redo`, and `undo` state is restored.
    - On redo: current state is saved to `undo`, and `redo` state is restored.
  - In frontend, button toggles label between `Hoàn tác` and `Khôi phục (Redo)`.

- **Chat Drawer Resizing & Styling (`WritingAssistantPane.tsx`):**
  - Remove fixed `w-80` from inner container, use `w-full h-full`.
  - Add draggable left border handle (`assistantWidth`, `onMouseDown` handler) allowing width adjustment from 360px to 720px.
  - Remove duplicate emoji icon in header: keep `<RotateCcw className="w-3.5 h-3.5" /> <span>Hoàn tác</span>` (or `Khôi phục`).

### 4.5. Dashboard Add Document Modal (`AddDocumentModal.tsx`)
- **Tab 3: `[ Tải lên PDF ]`:** Allows users to pick and upload a local PDF directly into the active session.
- **Session-Bound Invariant:** Uploading via this session modal creates a document linked to the session with `is_persistent = false`. It only enters permanent "My Library" when the user clicks the "Save / Bookmark" button, preventing library clutter.
- **Library Tab Filter & Deduplication:** When browsing the Library tab, query documents with `is_persistent=true`, deduplicate by content hash / title, hiding temporary non-persistent files.

### 4.6. Library Overhaul & LLM Wiki Knowledge Graph (`/library`)
- **Direct Library Upload:** Upload handler in `LibraryWorkspaceView.tsx` automatically calls `POST /api/v1/documents/{id}:star` with `toggle=true` and folder assignment so documents appear immediately in the library.
- **Folder Modal on Save:** When clicking Save on any document, open `StarDocumentModal` offering folder selection or inline folder creation (`+ Tạo thư mục mới`).
- **Knowledge Graph Endpoint (`GET /api/v1/library/graph`):**
  - Returns top-50 high-centrality entities and their relationships for the user's persistent documents (or active folder), preventing client canvas lag.
- **Interactive Knowledge Graph View (`KnowledgeGraphCanvas.tsx`):**
  - Toggle between `[ 📄 Danh sách ]` and `[ 🕸️ Đồ thị Tri thức ]`.
  - Interactive force-directed graph canvas (using SVG / Canvas):
    - **Paper Nodes:** Highlighted with accent color.
    - **Concept / Entity Nodes:** Extracted concepts (e.g. *Attention, Transformer, RAG, Bounding Box*).
    - **Edges:** Connecting papers to concepts and shared citation relations.
    - Clicking a node opens an inspection card showing connected papers and knowledge synthesis.
- **GraphRAG Assistant FAB (`LibraryWorkspaceView.tsx`):**
  - Floating action button at bottom-right of `/library`.
  - Opens resizable chat drawer querying the library via `GraphRAGRouter` (Global / Local / Bibliometrics) in natural scholarly conversation.

---

## 5. Verification Gates & Success Criteria

1. **Gate 1 (Python Linter & Formatter):** `uv run ruff check . && uv run ruff format --check .` (0 errors).
2. **Gate 2 (Backend Pytest):** `uv run pytest` (All existing and new tests pass 100%).
3. **Gate 3 (Frontend Vitest):** `npm --prefix apps/web run test` (All frontend suites pass 100%).
4. **Gate 4 (Production Build):** `npm --prefix apps/web run build` (Clean production bundle, 0 TypeScript errors).
5. **Puppeteer Visual Verification:** Confirm clean layouts, working unhide icons, resizable chat, and interactive graph view.
6. **VPS Deployment Sync:** Run `bash scripts/deploy_to_vps.sh --fast || true` per Rule 9.

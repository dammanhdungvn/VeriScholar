# Academic Writing, PDF Reader, and GraphRAG Library UX Refinements Design

> **Document Path:** `docs/superpowers/specs/2026-10-29-academic-writing-and-library-ux-refinements-design.md`  
> **Status:** Draft  
> **Target Release:** VeriScholar v1.2-alpha  
> **Author:** Antigravity AI & VeriScholar Engineering Team  

---

## 1. Intent & The Why

VeriScholar aims to provide a world-class, frictionless, radical-minimalist academic assistant for researchers, students, and lecturers. Currently, several friction points detract from this vision:
1. Navigating from `/dashboard` or `/library` to the writing workspace unmounts the global navigation taskbar, causing a disruptive full-page flicker/refresh illusion.
2. The writing workspace contains excessive clutter (overlapping buttons like "🧹 Xóa đệm & Dựng lại" and "Bản Dựng PDF Trực Tiếp"), while the Socratic Assistant occupies a fixed vertical column that reduces editor and preview real estate.
3. Compiling academic templates with Vietnamese Unicode characters fails in `pdflatex` with `Unicode character Ế (U+1EBE) [COMPILATION_FAILED]`, despite `xelatex` and `E2B_API_KEY` being available.
4. The PDF reader preview sidebar only supports page thumbnails, lacking a structured outline/table of contents to jump directly between paper sections.
5. "Kho Yêu thích" (My Library) shows all uploaded documents—including temporary session files—rather than strictly user-saved items, and the Save button does not reflect universal persistence state across search/reader interfaces.
6. The GraphRAG knowledge search in My Library forces users to manually choose between "Hybrid", "Local", and "Global" search modes, exposing internal graph mechanisms instead of automatically routing queries.

This design establishes a coherent, production-grade architecture solving all 11 user issues while upholding Radical Minimalism (Rule 6) and Hexagonal Isolation.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **Persistent App Layout:** Provide seamless, zero-flicker client-side navigation across `/dashboard`, `/library`, and `/writing` by retaining the Taskbar in a shared parent layout.
- **Overleaf-Grade Radical Minimalist Writing Workspace:** Clean, un-crammed toolbar with a single smart `Recompile` button; drawer-style collapsable File Tree; and Socratic Assistant as a floating action button (FAB) at bottom-right that opens a slide-out drawer on demand (identical to `/dashboard`).
- **100% Unicode LaTeX Compilation:** Automatic engine selection (`xelatex`) for documents with Unicode/Vietnamese characters alongside cloud execution fallback via E2B Sandbox (`E2B_API_KEY`).
- **Interactive PDF Outline:** Dual-mode preview sidebar supporting both `[ Trang (Thumbnails) ]` and `[ Mục lục (Outline) ]` with instant section navigation.
- **Universal Save/Unsave Sync:** My Library strictly displays saved papers (`is_persistent = true`) or categorized folder items. Save buttons across Search, Upload, and Reader dynamically indicate "Đã lưu" and toggle Unsave safely.
- **Decomposed GraphRAG Router:** A single unified search input in My Library that parses user intent and routes sub-queries to macro community scans, micro entity subgraphs, or bibliometrics without manual mode toggles.

### Non-Goals
- Replacing the Monaco LaTeX code editor or building a custom WYSIWYG rich text engine.
- Altering the core mathematical algorithms of Leiden clustering or 2-hop recursive CTEs in `packages/core/`.
- Permitting unauthenticated access to personal document libraries or cloud sandboxes.

### Anti-Goals
- Never expose internal database engine flags, OCR parameters, or technical chunk settings as primary action buttons in My Library cards.
- Never display redundant `completed` badges across every item in a user's permanent library.
- Never allow duplicate document ingestion records when a user clicks Save on a paper already present in their library.

---

## 3. Global Constraints & Governance

- **Hexagonal Isolation:** Zero imports from database ORMs, FastAPI, or web frameworks into `packages/core/`.
- **Radical Minimalism (Rule 6):** Elimination of boilerplate slogans, algorithm acronyms on UI, and bulky status badges.
- **4 Verification Gates:** 100% exit code 0 on Ruff Linter/Formatter (Gate 1), Pytest (Gate 2, 269+ tests), Vitest (Gate 3, 189+ tests), and Vite Production Build (Gate 4).
- **Automated VPS Deployment (Rule 9):** Fast deployment check via `bash scripts/deploy_to_vps.sh --fast` following commits.

---

## 4. Approaches Considered

### Approach 1: Comprehensive Radical Minimalism & Unified Routing (Selected ⭐)
- **Architecture:**
  - Wrap `/dashboard`, `/library`, and `/writing` inside a persistent `AppLayout` with `<Outlet />` and an unmounting-free `DashboardTaskbar`.
  - Refactor `WritingWorkspace` to adopt an Overleaf layout: collapsible file tree, unified `Recompile` dropdown, and a floating Socratic FAB matching the `/dashboard` pattern.
  - Upgrade `CLSILatexCompiler` and `draft_service` to automatically select `xelatex` upon detecting non-ASCII/Vietnamese characters, with E2B cloud compilation integration.
  - Implement PDF outline extraction via `pdfjs-dist` in the reader sidebar.
  - Refactor `/library` to filter strictly by `is_persistent: true`, replace text actions with icon buttons, and implement an intent router for GraphRAG.
- **Trade-offs:** Touches multiple layers, but delivers a seamless, international-caliber product experience and permanently resolves state fragmentation.

### Approach 2: Fragmented Page-by-Page Quick Fixes
- **Architecture:** Keep independent page routes with ad-hoc loading skeletons in `WritingPage`, keep manual `Local/Global/Hybrid` toggles with a default setting, and add a quick fontenc patch.
- **Trade-offs:** Leaves page transitions slightly delayed, maintains cognitive burden on users regarding GraphRAG internals, and risks recurring state inconsistencies between search, reader, and library.
- **Decision:** Rejected in favor of Approach 1.

---

## 5. Detailed System Architecture & Design

### 5.1. Taskbar & Persistent Layout Architecture
- **Navigation Items:**
  - `+ Đoạn chat mới` (Navigates to `/dashboard` to start fresh research session).
  - `Kho Yêu thích` (Navigates to `/library`).
  - `Viết paper` (Renamed from "Soạn thảo LaTeX", navigates to `/writing`).
  - `Recents` (Collapsible list of chat sessions with unread indicators and `...` context menu).
  - *Removed:* "Khám phá & Phiên đọc" is eliminated as redundant.
- **Zero-Flicker Layout Transition:**
  - `WritingPage` initial draft fetching happens gracefully. If draft is loading, only the central editor and preview panes render animated skeletons; `DashboardTaskbar` remains mounted and interactive.

### 5.2. Overleaf-Grade "Viết Paper" Workspace
- **Layout Structure:**
  - **Left File Tree Drawer:** Collapsible sidebar toggled via a clean `Files` button, listing `main.tex`, `references.bib`, and uploaded figures.
  - **Center Editor Pane:** Monaco LaTeX editor with syntax highlighting, line numbers, and clean shortcut bar.
  - **Right Preview Pane Header:**
    - Single green `[ Recompile ]` button with a subtle chevron dropdown (`Recompile from cache`, `Clear cache & Recompile`).
    - Eliminates cluttered buttons: `🧹 Xóa đệm & Dựng lại` and `Bản Dựng PDF Trực Tiếp` are removed.
    - PDF toolbar: Page jumper (`< 1 / N >`), Zoom controls (`- 100% +`), Download PDF icon.
  - **Socratic Assistant Integration:**
    - Replaced fixed right column with a **Floating Action Button (FAB)** at bottom-right (`✨ Socratic Assistant`), identical to `/dashboard`.
    - Clicking the FAB slides out a 420px drawer overlay featuring AI Co-Author suggestions, literature review synthesis, and LaTeX citation checks, allowing full-screen writing without cramping.

### 5.3. Unicode LaTeX Compilation & E2B Cloud Sandbox
- **Pipeline Unification:**
  - Standardize `POST /api/v1/drafts/{id}/compile` to use `CLSILatexCompiler` as the canonical compilation engine with caching support (`clear_cache: bool = False` by default). The UI's `Recompile` button sends standard requests, while a dropdown option (`Clear Cache & Recompile`) passes `clear_cache=True`.
  - Seamlessly wrap `AgenticLatexHealer` around `CLSILatexCompiler` errors: when compilation fails, the diagnostic logs are parsed by `LatexLogParser` and passed to the healing pipeline.
- **Engine Auto-Detection:**
  - In `CLSILatexCompiler.detect_engine`:
    ```python
    def detect_engine(main_tex: str) -> tuple[str, str]:
        # Detect XeLaTeX requirement: fontspec package OR non-ASCII Vietnamese characters
        has_unicode = any(ord(char) > 127 for char in main_tex)
        if "fontspec" in main_tex or "xelatex" in main_tex.lower() or has_unicode:
            return ("xelatex", "-xelatex")
        return ("pdflatex", "-pdf")
    ```
- **E2B Sandbox Integration & Remote Fallback:**
  - `draft_service.py` connects with `E2B_API_KEY` from `.env`.
  - When local LaTeX binaries (`latexmk`, `xelatex`) are unavailable on the host or in restricted CI environments, compilation transparently falls back to `E2BLatexCompiler`, passing the multi-file bundle (`main.tex`, `references.bib`, `figures/`) to the isolated E2B container.

### 5.4. PDF Reader Deep Reading: Outline (Mục Lục) View
- **Dual-Mode Sidebar in `PdfThumbnailSidebar.tsx`:**
  - Header segment toggle: `[ 🖼️ Trang ]` | `[ 📑 Mục lục ]`.
  - In `Outline` mode:
    - Calls `pdfDoc.getOutline()` via `pdfjs-dist`.
    - Recursively renders document hierarchy (e.g., *Abstract*, *1. Introduction*, *2. Methods*, *3. Results*).
    - Clicking any heading calculates the target page index / destination and triggers `scrollToPage(destPageNumber)` with smooth animation.

### 5.5. My Library & Universal Save/Unsave Synchronization
- **Strict Library Invariant:**
  - `LibraryWorkspaceView` defaults to filtering `documents.filter(d => Boolean(d.is_persistent || d.starred_at || d.folder_id))`. Temporary uploaded files from casual reading sessions do not contaminate the user's permanent library.
- **Universal Save State Reflection & Ingestion Deduplication:**
  - `DocumentService.create_document_record`: When uploading or ingesting via CAS, checks if a document with the same `content_hash` or `doi` already exists for the user. If existing and `is_persistent === True`, retains persistence and prevents duplicate rows.
  - In `DocumentSearchModal`, `ViewportOverflowMenu`, and `DocumentTabBar`:
    - Check if document `id` or `content_hash` has `is_persistent === true`.
    - Active state: Bookmark/Save item in "Tùy chọn" menu displays highlighted coral/gold with text "Đã lưu bài báo".
    - Clicking active state triggers `Unsave` (calls `POST /api/v1/documents/{id}/star` with `toggle=True`, resetting `is_persistent = false`, removing from folder, and pruning the knowledge graph).
- **Actions Column Polish:**
  - Replaces text `Config` and `Delete` with:
    - `SlidersHorizontal` icon button (`Cấu hình trích xuất`).
    - `Trash2` icon button (`Xóa tài liệu khỏi kho`, turns rose-600 on hover with confirm dialog).
  - Hides recurring `completed` badges to maintain radical visual calmness.

### 5.6. GraphRAG Intent Decomposer & Router
- **Elimination of Manual Mode Toggle:**
  - Removes `[ Chế độ Tra Cứu Tri Thức: Hybrid | Local | Global ]` radio buttons.
- **Single Intelligent Search Input:**
  - `🔍 Tra cứu tri thức, đối chiếu mô hình hoặc hỏi đáp trên toàn bộ thư viện...`
- **Backend Decomposition & Multi-Intent Routing (`GraphRAGRouter`):**
  - Uses `AcademicQueryDecomposer` to evaluate queries:
    1. *Comparative / Macro Intent* (e.g., "tổng quan", "so sánh SOTA", "xu hướng"): Dispatches `community_macro_scan` (Global Leiden cluster summaries).
    2. *Entity / Micro Metric Intent* (e.g., "công thức", "BLEU score", "Selective Attention", "giảm bao nhiêu"): Dispatches `entity_subgraph_lookup` (2-hop CTE + Bounding Box chunks).
    3. *Citation / Lineage Intent* (e.g., "trích dẫn", "bài báo nền tảng", "mối liên hệ"): Dispatches `bibliometric_graph_trace` (Connected Papers graph).
  - For compound multi-intent questions, executes parallel sub-retrievals and merges them using `_synthesize_answer`.
  - Embeds interactive evidence badges (`[ 🌐 2 cụm nghiên cứu ]`, `[ 📍 4 thực thể đối chiếu ]`) seamlessly within the synthesized academic markdown response and metadata envelope.

---

## 6. What's Left to the Builder

- Exact icon sizing and responsive breakpoints for the Overleaf drawer on viewports $< 1024\text{px}$.
- LocalStorage caching key for preserving user preference between PDF Thumbnails and Outline view (`pdf_sidebar_view_mode: "thumbnails" | "outline"`).
- Fine-tuning the debounce interval on the Monaco LaTeX editor auto-save hook.

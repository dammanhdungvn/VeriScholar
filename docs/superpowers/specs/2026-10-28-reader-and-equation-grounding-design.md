# Reader UX Polish & Equation-Aware Retrieval Grounding Design

> **Document:** Design Specification  
> **Status:** Approved by User  
> **Target Date:** 2026-10-28  
> **Scope:** `apps/api/src/api/services/session_chat_service.py`, `apps/web/src/components/viewer/PdfCanvasViewer.tsx`, `apps/web/src/components/chat/AcademicMarkdownRenderer.tsx`

---

## 1. Intent & Problem Statement
Live testing on VPS revealed 5 UI/UX and retrieval issues, plus a critical limitation in mathematical equation visual grounding:
1. **Section Query & Typo Fallback:** When asking for sections or headings with minor typos (e.g., "1. Instruction" instead of "1. Introduction", or "Mục 1"), RAG falls into CRAG ambiguous state ($0.20 \le \tau < 0.35$), expands to 23 adjacent chunks, and Socratic rigidly rejects the query.
2. **Infinite Scroll-Snap Trap & Unclosable Bounding Box:** In `PdfCanvasViewer.tsx`, whenever the user scrolls away to another page (`bestPage !== activeBbox[4]`), `lastScrolledBboxKeyRef.current = null` is executed, causing the canvas observer to snap back to Page 1 every time the user scrolls down. In addition, there is no way to dismiss the active bounding box without refreshing the page.
3. **Citation List Overflow (23 items):** In `AcademicMarkdownRenderer.tsx`, when `hasInlineTokens === false`, it dumps all 23 backend candidate chunks into the footer, cluttering the screen.
4. **Zoom > 100% Horizontal Scroll Blocked:** `PdfCanvasViewer.tsx` hardcodes `overflow-x-hidden` on the scroll container, preventing users from scrolling horizontally when zooming into dense two-column academic papers.
5. **Premature Citation Footer During Streaming:** `citation-sources-footer` renders as soon as SSE citations arrive, appearing under the first few words and jumping downward during streaming.
6. **Equation Retrieval & Grounding Failure:** Queries asking for formulas (e.g., "Lấy công thức Attention ra cho tôi", "Công thức A(H) trong paper có ý nghĩa gì") fail to retrieve the exact mathematical formula chunk. FTS filters out short tokens ($< 3$ chars, removing $A$ and $H$), HyDE vectors retrieve generic explanation paragraphs rather than the exact equation line, and bounding boxes highlight large surrounding paragraphs rather than the precise formula.

---

## 2. Architecture & Approach

### 2.1 Backend: Section & Equation-Aware Retrieval Booster
In `apps/api/src/api/services/session_chat_service.py`:
- **Section & Typo Normalizer:** Enhance `_detect_target_section` with regex patterns for `introduction`, `preliminaries`, `method`, `experiments`, `conclusion`, numbered sections (`mục 1`, `phần 1`, `section 1`), and fuzzy typo correction (`instruction` $\rightarrow$ `introduction`).
- **Equation & Formula Intent Detector (`_detect_formula_query`):**
  - Detect math intent: keywords (`công thức`, `formula`, `equation`, `phương trình`, `biểu thức`, `tính toán`, `(1)`, `(2)`, `(3)`, `A(H)`, `softmax`, `Attention(`, etc.).
  - Typo correction: `Attendsion` $\rightarrow$ `Attention`.
  - Extract symbolic targets: regex matching equation numbers (`(1)`, `(3)`, etc.) and symbols (`A(H)`, `Attention`, `softmax`, `e_{ij}`).
- **Symbolic Chunk Matching & Top-1 Boost:**
  - Before or during hybrid search, execute a fast text match on `document_chunks.content` for the detected equation symbols.
  - If a chunk contains the exact formula or equation identifier, boost its RRF score or insert it at Rank #1 in the retrieval pool.
  - Limit the final prompt context chunks to at most 5 highly relevant chunks (preventing 23-chunk prompt pollution).
- **Socratic Formula Synthesis Prompt:**
  - When responding to equation queries, Socratic must format the exact formula using LaTeX block `$$...$$`, explain the individual notation elements ($H$, $\alpha$, etc.), and cite `[1]` to ground the exact formula bounding box on the PDF.

### 2.2 Frontend: Reader UX, Anti-Trap Scrolling & Citation Polish
- **`PdfCanvasViewer.tsx`:**
  - Eliminate the scroll-snap trap: remove `lastScrolledBboxKeyRef.current = null` from the passive page intersection observer. Programmatic scrolling to a bounding box will ONLY trigger when a citation is clicked or `activeBbox` is updated by an explicit user action.
  - Add Dismissability:
    - Allow clicking an active citation badge again to deselect/clear `activeBbox`.
    - Support `Escape` key press to dismiss `activeBbox`.
    - Provide a subtle dismiss button `[✕]` on the active bounding box overlay.
  - Fix Zoom Horizontal Scrolling: replace `overflow-x-hidden` with `overflow-x-auto` on the PDF viewer container.
- **`AcademicMarkdownRenderer.tsx`:**
  - Stream-Gated Footer: Only render `citation-sources-footer` when `!isStreaming`.
  - Concise References: When `hasInlineTokens === false`, do NOT dump all candidate chunks. Only render citations explicitly referenced in the generated text (`[1]`, `[2]`), capped at Top 5 deduplicated entries.

---

## 3. Constraints & Invariants
- 100% backward compatibility with all existing tests.
- Zero extra heavy dependencies.
- Pass all 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm run build`).
- Automated VPS synchronization via `bash scripts/deploy_to_vps.sh --fast`.

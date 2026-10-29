# Design Spec: Reader Zoom/Pan, Loading Skeleton, Text Selection & RAG Contiguous Section Expansion

## 1. Context & Intent
During real-world academic research workflows with multi-column papers (e.g. *Attention Is All You Need*, *A Transformer with Stack Attention*), users encountered 5 usability and AI reasoning friction points:
1. **Empty State Flash on Page Load / Refresh (F5):** The reader pane abruptly flashes *"Chưa có tài liệu nghiên cứu nào. Tải lên tệp PDF..."* for ~500ms before snapping to the loaded PDF.
2. **AI Section Translation Cutoff ("Dịch toàn bộ phần 1 Introduction"):** AI only translated Paragraph 1 (Chunk 6) and outputted a disclaimer: *"Lưu ý: Ngữ cảnh được cung cấp hiện chỉ chứa đoạn trích trên..."* because SQL retrieval only matched chunks with the literal word `"1. Introduction"` (`limit=2`), ignoring Chunks 7, 8, 9 belonging to the same section.
3. **Bounding Box Co-ordinate Desync on Zoom (115%+):** When zoomed in, the PDF canvas grows, but the bounding box highlight overlay is narrower than the text.
4. **Text Selection Bleeding Across Columns/Sections:** Selecting text with mouse drag easily spills into the adjacent column or the next section due to `select-text` being attached to parent container wrappers and gutters.
5. **Horizontal Scroll & Pan Blocked on Zoom:** When zoomed in past 100%, users cannot scroll or pan horizontally to view clipped text on the sides.

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- Provide an instantaneous, elegant scholarly skeleton loader (`PaperLoadingSkeleton`) while documents or sessions are loading, completely eliminating empty state flashes.
- Implement **Contiguous Section Window Expansion** in backend RAG retrieval so that prompts asking for *"toàn bộ / full / all"* of a section retrieve all sequential chunks up to the next section header (or token budget ceiling).
- Ensure Bounding Box coordinate overlays scale 100% pixel-perfect at any zoom level ($100\%, 115\%, 150\%, 200\%$).
- Confine text selection strictly to the PDF.js `.textLayer`, preventing gutter and cross-column selection bleeding.
- Provide a dedicated, 1-click **"Sao chép" (Copy clean plain text)** action in `ScholarSelectionMenu` alongside "Trích dẫn" (Copy with academic citation).
- Enable seamless horizontal scrolling and trackpad panning when zoomed in.

### Non-Goals
- Altering the foundational pgvector hybrid search algorithm (BM25 + Cosine + RRF).
- Modifying PDF.js worker rendering architecture or PDF text extraction parser.

### Anti-Goals
- Hardcoding static chunk limits (e.g. arbitrary limit 10) that blindly pull unrelated sections into LLM context.
- Breaking responsive layout on mobile or split-pane workspace views.

## 3. Approaches Considered & Trade-offs

### Approach 1: Quick Symptom Patching
- Hardcode `limit=5` in SQL for introduction; remove `maxWidth: "100%"` without fixing flex container alignment.
- *Trade-off:* Blindly fetching 5 chunks might spill into Section 2 if Section 1 is short, or cut off if Section 1 is long. Flex centering still clips the left edge on horizontal overflow in CSS.

### Approach 2: Comprehensive Reader Engine & RAG Section Architecture (Selected)
- **Frontend Reader Engine:**
  - `PaperLoadingSkeleton`: active whenever `isLoadingDocs || isLoadingDocDetail || sessionDetailQuery.isLoading`.
  - Zoom & Bbox Alignment: remove `maxWidth: "100%"` from `PdfPageCanvas` and `div.page`; set explicit `width: containerWidth`. Bbox percentages now resolve against `containerWidth` directly.
  - Horizontal Scroll & Pan: update pages wrapper with `min-w-fit w-fit mx-auto` to eliminate CSS flex overflow clipping; allow trackpad two-finger pan and horizontal scroll.
  - Text Selection: set `select-none` on outer wrappers/gutters and `select-text` solely on `.textLayer`. Add a clean "Sao chép" button in `ScholarSelectionMenu`.
- **Backend RAG Contiguous Section Expansion:**
  - Detect intent for *"toàn bộ / full / complete / tất cả"* combined with section detection (`target_section`).
  - When section header chunk $k$ is found, fetch sequential chunks $k, k+1, k+2, \dots$ for the same document until the next section header is detected or token threshold (4,000 tokens) is reached.
- *Trade-off:* Requires updates to both frontend reader canvas and backend retrieval, but permanently fixes all 5 reported issues cleanly and robustly.

## 4. Detailed Implementation Specification

### 4.1 Frontend: `DashboardWorkspace.tsx`
- Replace conditional guard on line 877:
  ```tsx
  // Show skeleton if actively loading docs or session detail, or if document is active but detail is loading
  const isDocumentResolving = (isLoadingDocs || isLoadingDocDetail || sessionDetailQuery.isLoading) && !activeDocumentId;
  ```
- Render `PaperLoadingSkeleton` whenever `isDocumentResolving` is true, ensuring no empty state flash occurs on page refresh.

### 4.2 Frontend: `PdfPageCanvas.tsx`
- Remove `maxWidth: "100%"` from outer container and inner `div.page`.
- Set `width: `${containerWidth}px`` on outer container and inner `div.page`.
- Change outer container class from `select-text` to `select-none`.
- Ensure `.textLayer` and its span children retain `select-text` while the canvas and gutters remain `select-none`.

### 4.3 Frontend: `PdfCanvasViewer.tsx`
- Remove `select-text` from outer viewport container (line 623).
- Update pages wrapper (line 672):
  ```tsx
  <div
    className={cn(
      "min-w-fit w-fit mx-auto pb-16 flex flex-col items-center",
      readingMode === "continuous" && "gap-2 sm:gap-3",
      readingMode === "single" && "justify-center min-h-[calc(100vh-140px)]",
      readingMode === "two-page" && "gap-2"
    )}
  >
  ```
- Ensure `overflow-x-auto` is active and horizontal scrolling/panning is supported on trackpads and mouse wheels.

### 4.4 Frontend: `ScholarSelectionMenu.tsx`
- Add a new "Sao chép" (Copy clean text) button:
  - Icon: `<Copy className="w-3.5 h-3.5" />`
  - Action: `navigator.clipboard.writeText(selectedText)` directly, without adding quotes or document title metadata.
  - Temporary state: shows `<Check className="w-3.5 h-3.5 text-emerald-400" />` with text *"Đã chép"*.
- Keep the existing "Trích dẫn" button for copying with scholarly citation metadata.

### 4.5 Backend: `session_chat_service.py`
- Enhance `_detect_target_section` and query intent:
  - Detect full-section requests: `is_full_section = any(kw in q for kw in ["toàn bộ", "toan bo", "tất cả", "tat ca", "toàn phần", "full", "all", "entire", "trọn vẹn"])`.
- When `target_section` is detected (e.g. `"introduction"`, `"methodology"`, `"abstract"`, or `"section_N"`):
  - Find anchor chunk index $k$ matching the section heading.
  - If `is_full_section` or section has sequential continuation:
    - Query contiguous chunks with `chunk_index >= k` within the same `document_id`, ordered by `chunk_index ASC`.
    - Stop when reaching a chunk whose content begins with the next major section header (e.g. `re.match(r"^\s*(?:[2-9]|\bBackground|\bPreliminaries|\bRelated\s+Work|\bMethodology|\bExperiments)", chunk.content)`).
    - Limit contiguous window to max 6 chunks or 4,000 tokens.
    - Inject these contiguous chunks into `hybrid_candidates` with highest priority (`rrf_score=2.0`).

## 5. Testing & Verification Strategy

### 5.1 Backend Verification
- Unit test in `tests/unit/api/test_section_expansion.py`:
  - Mock a document with chunks 0..5 (abstract/title), chunks 6..9 (Section 1: Introduction), chunk 10 (Section 2: Background).
  - Call retrieval with query `"Dịch toàn bộ phần 1 Introduction sang tiếng việt"`.
  - Assert that all chunks 6, 7, 8, 9 are returned in order and chunk 10 is not included.

### 5.2 Frontend Verification
- Unit test in `apps/web/src/features/reader/__tests__/BboxHighlightZoom.test.tsx`:
  - Render `PdfPageCanvas` with `zoomRatio = 1.15` and `zoomRatio = 1.5`.
  - Verify that page container width equals `Math.floor(viewport.width)` and does NOT clamp to `maxWidth: 100%`.
- Unit test in `apps/web/src/features/reader/__tests__/ScholarSelectionMenuCopy.test.tsx`:
  - Verify "Sao chép" button copies raw text without citation quotes.
  - Verify "Trích dẫn" button copies formatted citation.
- Unit test in `apps/web/src/features/dashboard/__tests__/DashboardWorkspaceSkeleton.test.tsx`:
  - Verify `PaperLoadingSkeleton` is rendered during initial document/session loading and does not flash Empty State.

### 5.3 Verification Gates
Run all 4 gates before completion:
1. `uv run ruff check . && uv run ruff format --check .`
2. `uv run pytest`
3. `npm --prefix apps/web run test`
4. `npm --prefix apps/web run build`
5. `bash scripts/deploy_to_vps.sh --fast`

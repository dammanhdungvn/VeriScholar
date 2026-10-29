# PDF Bounding Box Precision, Citations Grounding, and AI Context Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix PDF text selection bounding box misalignment across columns, fix citation clicks not rendering bounding boxes on the paper, inject permanent Document Anchor Memory (Abstract/TOC) into AI context, and implement Section-Aware Cross-Lingual Retrieval with Working Memory (GPT/Claude/Perplexity standard).

**Architecture:** 
1. Frontend: Correct PDF.js v6 CSS variables (`--total-scale-factor`, `--user-unit`) and compute column-clamped bounding boxes using `range.getClientRects()`. Enable multi-bounding-box overlays in `BboxHighlightLayer` and lock observer scroll during programmatic citation jumps.
2. Backend: Establish 2-Tier Context Memory in `SessionChatService`: Tier-1 Document Anchor (Title, Authors, Full Abstract, TOC outline pinned in prompt), Section-Aware Query Routing (auto-prioritizing Abstract/Intro/Conclusion chunks with exact Bounding Boxes), and Sliding Working Memory with Anaphora Resolution.

**Tech Stack:** React 19, PDF.js v6 (`pdfjs-dist`), Zustand, Tailwind CSS, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16 `pgvector`, Langfuse Tracing, OpenAI GPT-4o.

**Spec:** [docs/PRD/03-sessions-and-deep-reading-crud.md](../../PRD/03-sessions-and-deep-reading-crud.md), [docs/specs/03-sessions-and-deep-reading-spec.md](../../specs/03-sessions-and-deep-reading-spec.md).

## Global Constraints

- Hexagonal Architecture: Core domain must remain isolated (`packages/core/`).
- Radical Minimalism 80/20: No raw technical jargon or unnecessary UI badges.
- Strict TDD: Write failing test first, make it green, refactor, and commit.
- 4 Verification Gates: 100% exit code 0 on Ruff, Pytest, Vitest, and Vite Build before completion.

## Review Focus

1. Text selection on two-column PDF must clamp within the column and never bleed horizontally across the gutter into adjacent columns.
2. Clicking inline citation `[1]`, `[2]`, `[cit_x]` in chat must navigate to the exact page and highlight all bounding boxes of the cited chunk in pulsing gold.
3. Querying "Dịch nội dung abstract sang tiếng việt" or asking for Abstract summaries must directly use the authentic Abstract from the document anchor, never hallucinatory text from footnotes or conclusion.
4. Programmatic scrolling from citation clicks must not be interrupted or reverted by the IntersectionObserver scroll watcher.
5. Multi-turn follow-up queries (e.g. user enters "1" or "phương pháp đó") must retain conversational context and resolve references correctly.

---

### Task 1: Fix PDF.js Text Layer Scaling and Multi-Rect Selection Bounding Box

**Files:**
- Modify: `apps/web/src/features/reader/components/PdfPageCanvas.tsx:175-195`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:255-320`
- Test: `apps/web/src/features/reader/__tests__/PdfTextSelectionBbox.test.tsx`

**Interfaces:**
- Produces: Normalized `calculatedBbox: BoundingBox = [x0, y0, x1, y1, page]` with multi-rect column clamping.
- Consumes: `pdfjsLib.TextLayer`, `range.getClientRects()`.

- [ ] **Step 1: Write failing Vitest test for multi-rect column-clamped text selection**

Create `apps/web/src/features/reader/__tests__/PdfTextSelectionBbox.test.tsx` testing that when selection client rects span within a single column, the calculated bounding box width is bounded by column width and does not exceed the page or gutter.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/PdfTextSelectionBbox.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implement `--total-scale-factor` and column-aware `range.getClientRects()` bounding box calculation**

In `PdfPageCanvas.tsx`:
```typescript
textLayerRef.current.style.setProperty("--scale-factor", `${viewport.scale}`);
textLayerRef.current.style.setProperty("--total-scale-factor", `${viewport.scale}`);
textLayerRef.current.style.setProperty("--user-unit", "1");
```
In `PdfCanvasViewer.tsx`:
Calculate `calculatedBbox` iterating over `range.getClientRects()`, computing the union of rects on the detected page, and clamping `x1` within column boundary.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/PdfTextSelectionBbox.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/components/PdfPageCanvas.tsx apps/web/src/features/reader/components/PdfCanvasViewer.tsx apps/web/src/features/reader/__tests__/PdfTextSelectionBbox.test.tsx
git commit -m "fix(reader): set total-scale-factor for textLayer and compute column-clamped selection bbox"
```

---

### Task 2: Multi-Bounding Box Highlighting, Citation Normalization & Scroll Lock

**Files:**
- Modify: `apps/web/src/features/reader/components/BboxHighlightLayer.tsx:1-45`
- Modify: `apps/web/src/features/reader/components/PdfPageCanvas.tsx:280-295`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:330-380`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1380-1420`
- Test: `apps/web/src/features/reader/__tests__/BboxHighlightLayer.test.tsx`

**Interfaces:**
- Produces: `BboxHighlightLayer` supporting `bboxes?: BoundingBox[] | null`, programmatic scroll lock `isProgrammaticScrollRef` in `PdfCanvasViewer`.
- Consumes: `CitationItemSchema` (`bounding_boxes: BoundingBox[]`, `page_number: number`, `document_id: string`).

- [ ] **Step 1: Write failing Vitest test for multi-box highlight and citation click normalization**

Update `apps/web/src/features/reader/__tests__/BboxHighlightLayer.test.tsx` to assert that when `bboxes` array with multiple boxes on the current page is provided, all boxes are rendered with the golden highlight style.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/BboxHighlightLayer.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implement multi-box rendering and citation handler normalization**

1. In `BboxHighlightLayer.tsx`: accept `bboxes?: BoundingBox[] | null` in addition to `bbox?: BoundingBox | null`. Render all boxes matching `currentPage`.
2. In `PdfPageCanvas.tsx`: pass `activeBbox` or active citation boxes to `BboxHighlightLayer`.
3. In `PdfCanvasViewer.tsx`: add `isProgrammaticScrollRef` so smooth scroll to citation target page does not get overridden by scroll listener.
4. In `DashboardWorkspace.tsx`: normalize `CitationItemSchema` (extract `bounding_boxes`, `page_number`, `document_id`), set active bbox and navigate to `page_number`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- src/features/reader/__tests__/BboxHighlightLayer.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/reader/components/BboxHighlightLayer.tsx apps/web/src/features/reader/components/PdfPageCanvas.tsx apps/web/src/features/reader/components/PdfCanvasViewer.tsx apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/reader/__tests__/BboxHighlightLayer.test.tsx
git commit -m "fix(reader): support multi-bbox overlays and resilient citation jump without scroll conflicts"
```

---

### Task 3: Pinned Document Anchor Memory (Title, Authors, Abstract & Section Outline)

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:1880-1940`
- Test: `apps/api/tests/test_session_document_anchor_memory.py`

**Interfaces:**
- Produces: `_build_document_anchor_context(docs: list[DocumentModel]) -> str` injected into `system_prompt`.
- Consumes: `DocumentModel.parsed_metadata` (`title`, `authors`, `abstract`, `sections`).

- [ ] **Step 1: Write failing Pytest test for Document Anchor Memory in chat prompt**

Create `apps/api/tests/test_session_document_anchor_memory.py` verifying that when a session has completed documents, their verbatim Abstract and section outline are always injected into the System Prompt.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_session_document_anchor_memory.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `_build_document_anchor_context` and prompt injection**

In `SessionChatService`:
Fetch active `DocumentModel` records, extract `abstract` from `parsed_metadata` or chunk 0/4, format a clear `[TÀI LIỆU NGHIÊN CỨU HIỆN TẠI (DOCUMENT ANCHOR)]` block with `[BẢN TÓM TẮT CHÍNH THỨC (OFFICIAL ABSTRACT)]`, and append to `system_prompt`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_session_document_anchor_memory.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_session_document_anchor_memory.py
git commit -m "feat(rag): pin permanent document anchor memory with official abstract into system prompt"
```

---

### Task 4: Section-Aware Query Routing & Bilingual Cross-Lingual Search

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:465-560, 810-870`
- Test: `apps/api/tests/test_section_aware_retrieval.py`

**Interfaces:**
- Produces: Section-aware chunk prioritization (`target_section: str | None`), bilingual FTS tsquery extraction.
- Consumes: `DocumentChunkModel.content`, `plainto_tsquery`.

- [ ] **Step 1: Write failing Pytest test for section-aware query routing**

Create `apps/api/tests/test_section_aware_retrieval.py` verifying that when a user query contains "abstract" or "tóm tắt", the Abstract chunk is guaranteed to be retrieved at Rank 1 with citation `cit_1` and its exact Page 1 bounding box.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_section_aware_retrieval.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement section-aware retrieval and bilingual FTS query extraction**

1. Detect section targeting keywords ("abstract", "tóm tắt", "introduction", "kết luận", etc.).
2. When section targeted, query database for chunks matching the target section heading (e.g. `c.chunk_index IN (0, 1, 2, 3, 4)` or `c.content ILIKE '%Abstract%'`) and prepend directly to candidates.
3. Clean FTS query: strip non-English words when querying `content_tsv` with `plainto_tsquery('english', ...)` or use `to_tsquery('english', ...)` with OR (`|`) rather than rigid AND (`&`).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_section_aware_retrieval.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_section_aware_retrieval.py
git commit -m "feat(rag): implement section-aware chunk routing and robust cross-lingual retrieval"
```

---

### Task 5: Conversational Working Memory & Anaphora Follow-Up Resolution

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:420-460, 1750-1780`
- Test: `apps/api/tests/test_session_working_memory.py`

**Interfaces:**
- Produces: `_condense_query_with_context(query: str, history: list[dict]) -> str` resolving numbers ("1", "2") and pronouns ("nó", "phương pháp này").
- Consumes: `history_turns: list[SessionTurnModel]`.

- [ ] **Step 1: Write failing Pytest test for multi-turn anaphora follow-up resolution**

Create `apps/api/tests/test_session_working_memory.py` verifying that when a user asks "1" after a turn discussing questions or topics, the query expands to the specific topic from the previous turn.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_session_working_memory.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement context condensation and working memory**

In `_condense_query`:
Inspect previous user/assistant turn. If current query is short/anaphoric (e.g. single digit "1", "phương pháp đó", "nó hoạt động thế nào"), combine with the antecedent topic from the previous turn before retrieval and HyDE generation.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_session_working_memory.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_session_working_memory.py
git commit -m "feat(rag): add working memory with conversational anaphora resolution"
```

---

### Task 6: End-to-End Verification Across 4 Mandatory Gates

**Files:**
- Verification only.

- [ ] **Step 1: Run Gate 1 (Python Linter & Formatter)**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 100% clean exit code 0.

- [ ] **Step 2: Run Gate 2 (Backend & Architecture Boundary Tests)**
Run: `uv run pytest`
Expected: All 240+ tests passing.

- [ ] **Step 3: Run Gate 3 (Frontend Vitest Suites)**
Run: `npm --prefix apps/web run test`
Expected: 100% passing.

- [ ] **Step 4: Run Gate 4 (Production Build)**
Run: `npm --prefix apps/web run build`
Expected: Build passes with exit code 0.

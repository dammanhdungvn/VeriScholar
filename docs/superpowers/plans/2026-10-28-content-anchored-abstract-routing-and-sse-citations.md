# Content-Anchored Abstract Routing & SSE Citations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the missing PDF bounding box on citation click and resolve citation misattribution by standardizing SSE citations streaming, preserving multi-bbox arrays in frontend normalizers, and routing abstract queries to genuine abstract chunks via content-fingerprint matching.

**Architecture:**
1. **Frontend SSE Contract Standardization:** Update `useStreamingChat.ts` to recognize `ev.event === "citations"` and `Array.isArray(parsed.citations)`, preventing citations from being discarded during streaming.
2. **Multi-Bbox Array Normalization:** Update `CitationBadgeData` in `types/dashboard.ts` and `normalizeCitation` in `useStreamingChat.ts` to preserve `bounding_boxes`, and forward `activeBboxes` to `PdfCanvasViewer` in `DashboardWorkspace.tsx`.
3. **Content-Anchored Abstract Routing:** In `SessionChatService`, match abstract queries against `parsed_metadata["abstract"]` content prefixes on Page 1-2, penalizing author affiliation header chunks (Chunk 0) so the actual abstract chunk is prioritized at Rank 1.

**Tech Stack:** React 19, TypeScript, Zustand, PDF.js, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16 pgvector, Pytest, Vitest.

**Spec:**
- `docs/PRD/03-sessions-and-deep-reading-crud.md`
- `docs/specs/03-sessions-and-deep-reading-spec.md`

## Global Constraints

- Hexagonal architecture: `packages/core/` domain isolation untouched.
- Radical Minimalism 80/20: No raw tech boast or `#hex` strings on user interface.
- Relative Markdown links only in documentation.
- All 4 verification gates must pass with exit code 0 before task completion.
- Rule 9 VPS deploy protocol (`bash scripts/deploy_to_vps.sh --fast`) executed after every commit.

## Review Focus

1. Streaming assistant messages receive citations in real time before stream completion (`ev.event === "citations"`).
2. Clicking citation `[1]` while streaming or after reload highlights amber dashed boxes on the PDF canvas.
3. Multi-line abstract chunks render multiple highlight rectangles rather than a single collapsed rectangle.
4. Papers where Chunk 0 is author affiliation and Chunk 1 is body abstract (without the word "abstract") correctly attribute Citation 1 to Chunk 1.
5. Papers with no `parsed_metadata["abstract"]` fall back gracefully without raising SQL exceptions.

---

### Task 1: Standardize Frontend SSE Citations Contract & CitationBadgeData Multi-Bbox

**Files:**
- Modify: `apps/web/src/types/dashboard.ts:6-15`
- Modify: `apps/web/src/features/dashboard/hooks/useStreamingChat.ts:17-40,295-325`
- Test: `apps/web/src/features/dashboard/__tests__/useStreamingChat.test.ts`

**Interfaces:**
- Consumes: Server SSE event `event: citations\ndata: {"citations": [...]}\n\n`
- Produces: `CitationBadgeData.bounding_boxes?: BoundingBox[]`, `ChatMessage.citations` populated during stream

- [x] **Step 1: Write failing unit test for SSE citations parsing & multi-bbox normalization**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `bounding_boxes` in `CitationBadgeData` and update `normalizeCitation` & SSE message handler**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit and VPS fast sync**

```bash
git add apps/web/src/types/dashboard.ts apps/web/src/features/dashboard/hooks/useStreamingChat.ts apps/web/src/features/dashboard/__tests__/useStreamingChat.test.ts
git commit -m "fix(chat): support event: citations in sse parser and retain multi-bbox array"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Pass `activeBboxes` into `PdfCanvasViewer` and Connect Reader Store

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:243-248,853-865`
- Test: `apps/web/src/features/reader/__tests__/BboxHighlightLayer.test.tsx`

**Interfaces:**
- Consumes: `useReaderStore.getState().activeBboxes`, `CitationBadgeData.bounding_boxes`
- Produces: `PdfCanvasViewer` received `activeBboxes` prop, rendering all multi-box highlights on matching page

- [x] **Step 1: Write failing test in `BboxHighlightLayer.test.tsx` for multi-box highlight rendering with active citation**
- [x] **Step 2: Run test to verify it passes or fails**
- [x] **Step 3: Update `DashboardWorkspace.tsx` to read `activeBboxes` from reader store and pass to `PdfCanvasViewer`**
- [x] **Step 4: Run frontend tests to verify no regressions**
- [x] **Step 5: Commit and VPS fast sync**

```bash
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx
git commit -m "fix(workspace): pass activeBboxes from reader store to PdfCanvasViewer"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Content-Anchored Abstract Routing with Author Header Chunk Bypass

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:1080-1130`
- Test: `apps/api/tests/test_section_aware_retrieval.py`

**Interfaces:**
- Consumes: `target_section == "abstract"`, `DocumentModel.parsed_metadata["abstract"]`
- Produces: `retrieve_and_prepare_context` places actual Abstract chunk at Rank 1 (`cit_1`) even when Chunk 0 has no "abstract" keyword

- [x] **Step 1: Write failing integration test for paper where Chunk 0 is Author Header and Chunk 1 is body Abstract**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement Content-Anchored Abstract Routing in `session_chat_service.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit and VPS fast sync**

```bash
git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_section_aware_retrieval.py
git commit -m "feat(rag): route abstract retrieval by content fingerprint and bypass header affiliations"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Full 4-Gate Verification and Production VPS Deployment

**Files:**
- N/A (Verification & Ops)

**Interfaces:**
- Gate 1: Ruff linter & format
- Gate 2: Pytest backend suite (250+ tests)
- Gate 3: Vitest frontend suite (113+ tests)
- Gate 4: Vite production build
- Production Rollout: `scripts/deploy_to_vps.sh`

- [x] **Step 1: Run Gate 1 (Ruff)**
- [x] **Step 2: Run Gate 2 (Pytest)**
- [x] **Step 3: Run Gate 3 (Vitest)**
- [x] **Step 4: Run Gate 4 (Build)**
- [x] **Step 5: Execute full VPS deployment**
- [x] **Step 6: Live curl health check verification**

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

- [ ] **Step 1: Write failing unit test for SSE citations parsing & multi-bbox normalization**

Create `apps/web/src/features/dashboard/__tests__/useStreamingChat.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { normalizeCitation } from "../hooks/useStreamingChat";

describe("normalizeCitation", () => {
  it("preserves full bounding_boxes array and assigns primary bbox", () => {
    const raw = {
      citation_id: "cit_1",
      paper_id: "doc-123",
      page_number: 1,
      bounding_boxes: [
        [0.1, 0.2, 0.4, 0.3, 1],
        [0.1, 0.35, 0.4, 0.45, 1],
      ],
      document_title: "Test Paper",
    };

    const normalized = normalizeCitation(raw);
    expect(normalized.citation_id).toBe("cit_1");
    expect(normalized.paper_id).toBe("doc-123");
    expect(normalized.page).toBe(1);
    expect(normalized.bbox).toEqual([0.1, 0.2, 0.4, 0.3, 1]);
    expect(normalized.bounding_boxes).toEqual([
      [0.1, 0.2, 0.4, 0.3, 1],
      [0.1, 0.35, 0.4, 0.45, 1],
    ]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web test src/features/dashboard/__tests__/useStreamingChat.test.ts`
Expected: FAIL (missing export or `bounding_boxes` property)

- [ ] **Step 3: Implement `bounding_boxes` in `CitationBadgeData` and update `normalizeCitation` & SSE message handler**

In `apps/web/src/types/dashboard.ts`:
Add `bounding_boxes?: BoundingBox[];` to `CitationBadgeData`.

In `apps/web/src/features/dashboard/hooks/useStreamingChat.ts`:
Export `normalizeCitation`. Populate `bounding_boxes: rawBoxes.length > 0 ? rawBoxes : [bbox]`.
In `onmessage(ev)`:
Check:
```typescript
} else if (
  ev.event === "citations" ||
  parsed.type === "citation" ||
  parsed.type === "citations" ||
  Array.isArray(parsed.citations)
) {
  const rawCites = Array.isArray(parsed.citations)
    ? parsed.citations
    : parsed.citation
    ? [parsed.citation]
    : [];
  const newCites: CitationBadgeData[] = rawCites.map(normalizeCitation);
  citationsList = [...citationsList, ...newCites];
  setMessages((prev) =>
    prev.map((msg) =>
      msg.id === assistantMsgId
        ? { ...msg, citations: citationsList }
        : msg
    )
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web test src/features/dashboard/__tests__/useStreamingChat.test.ts`
Expected: PASS

- [ ] **Step 5: Commit and VPS fast sync**

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

- [ ] **Step 1: Write failing test in `BboxHighlightLayer.test.tsx` for multi-box highlight rendering with active citation**

Ensure `BboxHighlightLayer` renders all boxes from `bboxes` prop with `border-amber-500` and pulse ring.

- [ ] **Step 2: Run test to verify it passes or fails**

Run: `npm --prefix apps/web test src/features/reader/__tests__/BboxHighlightLayer.test.tsx`
Expected: PASS

- [ ] **Step 3: Update `DashboardWorkspace.tsx` to read `activeBboxes` from reader store and pass to `PdfCanvasViewer`**

In `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`:
```typescript
const activeBboxesReader = useReaderStore((s) => s.activeBboxes);
```
Line 860:
```tsx
<PdfCanvasViewer
  documentId={activeDocumentId}
  documentDetail={documentDetail}
  fileUrl={documentsApi.getDocumentFileUrl(activeDocumentId)}
  currentPage={currentPage}
  zoomRatio={zoomRatio}
  rotationDeg={rotationDeg}
  activeBbox={activeBbox}
  activeBboxes={activeBboxesReader}
  onPageCountDetected={setTotalPages}
  onClearHighlight={() => {
    setActiveBboxStore(null);
    setActiveCitation(null, null);
  }}
...
```

- [ ] **Step 4: Run frontend tests to verify no regressions**

Run: `npm --prefix apps/web test`
Expected: 113+ passed

- [ ] **Step 5: Commit and VPS fast sync**

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

- [ ] **Step 1: Write failing integration test for paper where Chunk 0 is Author Header and Chunk 1 is body Abstract**

In `apps/api/tests/test_section_aware_retrieval.py`:
Add test `test_section_aware_retrieval_matches_abstract_by_prefix_and_bypasses_affiliation_header`:
```python
@pytest.mark.asyncio
async def test_section_aware_retrieval_matches_abstract_by_prefix_and_bypasses_affiliation_header(
    db_session, monkeypatch
):
    # Setup doc where Chunk 0 = Title & Authors (no "abstract" word)
    # Chunk 1 = "Natural languages are believed to be context-sensitive..." (no "abstract" word)
    # doc.parsed_metadata["abstract"] = "Natural languages are believed to be..."
    # Assert citations[0]["chunk_index"] == 1 and bounding_boxes == chunk 1 bboxes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_section_aware_retrieval.py -k "bypasses_affiliation_header" -v`
Expected: FAIL (citations[0]["chunk_index"] == 0)

- [ ] **Step 3: Implement Content-Anchored Abstract Routing in `session_chat_service.py`**

In `session_chat_service.py`:
When `target_section == "abstract"`:
1. Fetch target documents' `parsed_metadata` to retrieve official abstract text if present.
2. If `doc_abstract` has $\ge 30$ chars, extract the leading 50 characters (e.g. `prefix = doc_abstract[:50].strip()`).
3. Construct SQL query prioritizing:
   - Priority 0: `DocumentChunkModel.content.ilike(f"%{prefix[:40]}%")` (exact abstract match)
   - Priority 1: `DocumentChunkModel.content.ilike("%abstract%")` (explicit keyword)
   - Priority 2: `case((and_(DocumentChunkModel.page_number == 1, DocumentChunkModel.chunk_index > 0, func.length(DocumentChunkModel.content) > 150), 2), else_=9)` (body text over header)
   - Priority 3: `DocumentChunkModel.chunk_index.asc()`

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_section_aware_retrieval.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit and VPS fast sync**

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

- [ ] **Step 1: Run Gate 1 (Ruff)**
```bash
uv run ruff check . && uv run ruff format --check .
```
- [ ] **Step 2: Run Gate 2 (Pytest)**
```bash
uv run pytest
```
- [ ] **Step 3: Run Gate 3 (Vitest)**
```bash
npm --prefix apps/web run test
```
- [ ] **Step 4: Run Gate 4 (Build)**
```bash
npm --prefix apps/web run build
```
- [ ] **Step 5: Execute full VPS deployment**
```bash
bash scripts/deploy_to_vps.sh
```
- [ ] **Step 6: Live curl health check verification**
```bash
curl -s -i https://verischolar.duckdns.org/health
```

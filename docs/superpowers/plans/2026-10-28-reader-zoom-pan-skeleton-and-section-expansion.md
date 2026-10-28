# Reader Zoom/Pan, Loading Skeleton, Text Selection & RAG Contiguous Section Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate reader empty-state flashing on load, ensure pixel-perfect Bounding Box scaling on zoom, enable horizontal pan/scroll, isolate text selection with a dedicated clean copy button, and implement RAG Contiguous Section Window Expansion for complete multi-chunk section translations.

**Architecture:**
- **Backend RAG:** In `SessionChatService._hybrid_search`, detect full-section intents and expand sequential chunks starting from the section header until reaching the next section header or a 4,000 token limit.
- **Frontend Viewer:** In `PdfPageCanvas` and `PdfCanvasViewer`, remove `maxWidth: "100%"` to allow canvas and `div.page` to expand with zoom, align page container using `min-w-fit w-fit mx-auto` to prevent flex centering scroll clipping, isolate `select-text` solely to `.textLayer`, add clean copy action in `ScholarSelectionMenu`, and render `PaperLoadingSkeleton` during session/document resolution.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 Async, React 19, Tailwind CSS, PDF.js, Vite, Vitest, Pytest.

**Spec:** [`docs/superpowers/specs/2026-10-28-reader-zoom-pan-skeleton-and-section-expansion-design.md`](../specs/2026-10-28-reader-zoom-pan-skeleton-and-section-expansion-design.md)

## Global Constraints
- Pure Hexagonal Architecture: `packages/core` remains strictly pure Python standard library and Pydantic.
- Radical Minimalism 80/20: Zero clutter, clean typography, no technical jargon or hexadecimal codes in UI.
- Test-Driven Development (TDD): Red test first, minimal green implementation, refactor.
- 4 Verification Gates must pass before task completion (Ruff check/format, Pytest, Web test, Web build).
- In-Plan VPS Sync: Run `bash scripts/deploy_to_vps.sh --fast` after each commit.

## Review Focus
1. **Section boundary overshooting:** Ensure sequential chunk expansion halts immediately upon detecting the next section heading (e.g. `2 Background` or `2 Preliminaries`) so that Section 2 is never leaked into Section 1.
2. **Missing next section header:** If a section runs until the end of the document without a subsequent numbered section, ensure the 6-chunk / 4,000-token ceiling prevents prompt overflow.
3. **Responsive split-view resizing:** Ensure that removing `maxWidth: "100%"` does not break the layout when zoom is 100% or below on smaller screen widths.
4. **Clipboard write failure gracefully handled:** In non-HTTPS environments or blocked clipboard permissions, fallback gracefully without crashing the selection menu.
5. **Skeleton unmount timing:** Ensure the skeleton unmounts seamlessly the instant the active document is ready, without an intermediate blank frame.

---

### Task 1: Backend RAG Contiguous Section Window Expansion

**Files:**
- Create: `tests/unit/api/test_section_expansion.py`
- Modify: `apps/api/src/api/services/session_chat_service.py:1040-1085, 1310-1410`

**Interfaces:**
- Consumes: `SessionChatService._detect_target_section(query: str) -> str | None`
- Produces: `_expand_contiguous_section_chunks(document_id: UUID, start_chunk_index: int, max_chunks: int = 6) -> list[DocumentChunkModel]`

- [ ] **Step 1: Write the failing backend test for contiguous section expansion**

Create `tests/unit/api/test_section_expansion.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from apps.api.src.api.services.session_chat_service import SessionChatService

@pytest.mark.asyncio
async def test_detect_full_section_intent():
    assert SessionChatService._is_full_section_query("Dịch toàn bộ phần 1 Introduction sang tiếng việt") is True
    assert SessionChatService._is_full_section_query("Tóm tắt tất cả mục 2") is True
    assert SessionChatService._is_full_section_query("Công thức A(H) là gì?") is False

@pytest.mark.asyncio
async def test_contiguous_section_expansion_stops_at_next_section():
    # Chunks: 6 (Intro), 7 (Intro p2), 8 (Intro p3), 9 (Intro p4), 10 (2 Background)
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()
    
    mock_chunks = [
        MagicMock(id=uuid4(), document_id=doc_id, chunk_index=6, page_number=2, content="1 Introduction\nRecurrent neural networks..."),
        MagicMock(id=uuid4(), document_id=doc_id, chunk_index=7, page_number=2, content="Recurrent models typically factor computation..."),
        MagicMock(id=uuid4(), document_id=doc_id, chunk_index=8, page_number=2, content="Attention mechanisms have become an integral part..."),
        MagicMock(id=uuid4(), document_id=doc_id, chunk_index=9, page_number=2, content="In this work we propose the Transformer..."),
        MagicMock(id=uuid4(), document_id=doc_id, chunk_index=10, page_number=2, content="2 Background\nThe goal of reducing sequential computation..."),
    ]
    
    expanded = service._filter_contiguous_section_chunks(mock_chunks, start_chunk_index=6)
    assert len(expanded) == 4
    assert [c.chunk_index for c in expanded] == [6, 7, 8, 9]
    assert 10 not in [c.chunk_index for c in expanded]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/api/test_section_expansion.py -v`
Expected: FAIL with AttributeError: `_is_full_section_query` or `_filter_contiguous_section_chunks` not found.

- [ ] **Step 3: Implement contiguous section expansion in `session_chat_service.py`**

In `apps/api/src/api/services/session_chat_service.py`:
1. Add `@staticmethod _is_full_section_query(query: str) -> bool`:
   Checks for keywords `["toàn bộ", "toan bo", "tất cả", "tat ca", "toàn phần", "full", "all", "entire", "trọn vẹn"]`.
2. Add `@staticmethod _filter_contiguous_section_chunks(chunks: list[Any], start_chunk_index: int, max_chunks: int = 6) -> list[Any]`:
   Filters sequential chunks starting from `start_chunk_index`. Checks each chunk after the first for major next-section heading regex `^\s*(?:\d+\.?\s+[A-Z]|\bBackground\b|\bPreliminaries\b|\bRelated\s+Work\b|\bMethodology\b|\bExperiments\b|\bResults\b|\bConclusion\b)`. If matched, stops expansion and returns prior chunks.
3. In `_hybrid_search` section-aware routing (for Introduction, Methodology, section_N):
   When `target_section` is found, fetch sequential chunks from `start_chunk_index` onwards and filter via `_filter_contiguous_section_chunks`. Inject all matching section chunks into `hybrid_candidates`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/api/test_section_expansion.py -v`
Expected: PASS

- [ ] **Step 5: Run full pytest suite and linter**

Run: `uv run ruff check . && uv run ruff format --check . && uv run pytest`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/api/src/api/services/session_chat_service.py tests/unit/api/test_section_expansion.py
git commit -m "feat(api): implement RAG contiguous section window expansion for full-section queries"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Frontend Paper Loading Skeleton (Zero Empty-State Flash)

**Files:**
- Create: `apps/web/src/features/dashboard/__tests__/DashboardWorkspaceSkeleton.test.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:870-965`

**Interfaces:**
- Consumes: `isLoadingDocs`, `isLoadingDocDetail`, `sessionDetailQuery.isLoading`, `activeDocumentId`
- Produces: Polished `PaperLoadingSkeleton` rendered during document/session loading states, eliminating empty-state flashing.

- [ ] **Step 1: Write the failing frontend test for loading skeleton**

Create `apps/web/src/features/dashboard/__tests__/DashboardWorkspaceSkeleton.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

// Mock hooks to simulate initial session & document loading
vi.mock("@/features/documents/hooks/useDocumentIngestion", () => ({
  useDocumentsList: () => ({ data: undefined, isLoading: true }),
  useDocumentDetail: () => ({ data: undefined, isLoading: true }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("@/features/sessions/hooks/useSessionDetail", () => ({
  useSessionDetail: () => ({ data: undefined, isLoading: true }),
  useUpdateSessionViewportMutation: () => ({ mutateAsync: vi.fn() }),
  useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

describe("DashboardWorkspace Loading State", () => {
  it("renders paper-loading-skeleton and does NOT render empty state when loading docs/session", async () => {
    // Dynamic import to pick up mocks
    const { DashboardWorkspace } = await import("../components/DashboardWorkspace");
    render(<DashboardWorkspace />);
    
    expect(screen.getByTestId("paper-loading-skeleton")).toBeInTheDocument();
    expect(screen.queryByText("Chưa có tài liệu nghiên cứu nào")).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DashboardWorkspaceSkeleton.test.tsx`
Expected: FAIL because currently `isRealDocument` is false and Empty State is shown instead of skeleton.

- [ ] **Step 3: Update `DashboardWorkspace.tsx` conditional rendering**

In `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`:
Replace lines 877–945 so that `PaperLoadingSkeleton` is displayed whenever:
```tsx
const isResolvingDocument = Boolean(
  (isLoadingDocs || isLoadingDocDetail || sessionDetailQuery.isLoading) ||
  (activeDocumentId && !documentDetail)
);
```
If `isRealDocument && activeDocumentId`: render `PdfCanvasViewer`.
Else if `isResolvingDocument || (bboxStyle && activeBbox)`: render `PaperLoadingSkeleton`.
Else: render the Empty State.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- DashboardWorkspaceSkeleton.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/__tests__/DashboardWorkspaceSkeleton.test.tsx
git commit -m "fix(web): prevent empty state flash on initial load by prioritizing paper loading skeleton"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Bounding Box Scaling Sync on Zoom

**Files:**
- Create: `apps/web/src/features/reader/__tests__/PdfPageCanvasZoomBbox.test.tsx`
- Modify: `apps/web/src/features/reader/components/PdfPageCanvas.tsx:240-270`

**Interfaces:**
- Consumes: `containerWidth = pageSize?.width || estimatedWidth`
- Produces: Unclamped page container width matching `containerWidth` exactly so `BboxHighlightLayer` percentage widths align 1:1 with canvas text.

- [ ] **Step 1: Write the failing unit test for zoom bounding box alignment**

Create `apps/web/src/features/reader/__tests__/PdfPageCanvasZoomBbox.test.tsx`:
```tsx
import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PdfPageCanvas } from "../components/PdfPageCanvas";

describe("PdfPageCanvas Zoom Bounding Box Scale", () => {
  it("does NOT clamp container or page to maxWidth: 100% when zoom > 1.0", () => {
    const { container } = render(
      <PdfPageCanvas
        pageNumber={1}
        zoomRatio={1.5}
        rotationDeg={0}
        fallbackDimensions={[600, 800]}
      />
    );
    
    const pageWrapper = container.querySelector("#pdf-page-1") as HTMLElement;
    const pageDiv = container.querySelector(".page") as HTMLElement;
    
    // Zoom 1.5 of 600px width = 900px
    expect(pageWrapper.style.width).toBe("900px");
    expect(pageWrapper.style.maxWidth).toBeFalsy();
    expect(pageDiv.style.width).toBe("900px");
    expect(pageDiv.style.maxWidth).toBeFalsy();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- PdfPageCanvasZoomBbox.test.tsx`
Expected: FAIL because `maxWidth: 100%` is currently present.

- [ ] **Step 3: Remove `maxWidth: "100%"` in `PdfPageCanvas.tsx`**

In `apps/web/src/features/reader/components/PdfPageCanvas.tsx:249, 264`:
Remove `maxWidth: "100%"`. Let width be strictly `${containerWidth}px`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- PdfPageCanvasZoomBbox.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/reader/components/PdfPageCanvas.tsx apps/web/src/features/reader/__tests__/PdfPageCanvasZoomBbox.test.tsx
git commit -m "fix(reader): sync bounding box width on zoom by unclamping page maxWidth"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Text Selection Isolation & Clean "Sao chép" Button

**Files:**
- Create: `apps/web/src/features/reader/__tests__/ScholarSelectionMenuCopy.test.tsx`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:623`
- Modify: `apps/web/src/features/reader/components/PdfPageCanvas.tsx:242, 257, 282`
- Modify: `apps/web/src/features/reader/components/ScholarSelectionMenu.tsx:25-115`

**Interfaces:**
- Consumes: `selectedText: string`
- Produces: Dedicated "Sao chép" button copying clean plain text without citation wrap, plus `select-none` on parent containers.

- [ ] **Step 1: Write failing test for clean copy button in ScholarSelectionMenu**

Create `apps/web/src/features/reader/__tests__/ScholarSelectionMenuCopy.test.tsx`:
```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ScholarSelectionMenu } from "../components/ScholarSelectionMenu";

describe("ScholarSelectionMenu Clean Copy Action", () => {
  it("renders 'Sao chép' button and copies raw plain text to clipboard", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText: writeTextMock } });
    
    const onClearMock = vi.fn();
    render(
      <ScholarSelectionMenu
        selectedText="Attention Is All You Need"
        coord={{ x: 100, y: 100 }}
        pageNumber={1}
        documentTitle="Transformer Paper"
        onAddToNote={vi.fn()}
        onClearSelection={onClearMock}
      />
    );
    
    const rawCopyBtn = screen.getByTestId("selection-copy-raw-btn");
    expect(rawCopyBtn).toBeInTheDocument();
    
    fireEvent.click(rawCopyBtn);
    expect(writeTextMock).toHaveBeenCalledWith("Attention Is All You Need");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- ScholarSelectionMenuCopy.test.tsx`
Expected: FAIL with `selection-copy-raw-btn` not found.

- [ ] **Step 3: Implement clean copy button and isolate text selection**

1. In `apps/web/src/features/reader/components/ScholarSelectionMenu.tsx`:
   Add `handleCopyRawText = async () => { await navigator.clipboard.writeText(selectedText); setCopiedRaw(true); ... }` and button with `data-testid="selection-copy-raw-btn"` with label *"Sao chép"*. Keep existing button as *"Trích dẫn"*.
2. In `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:623`:
   Change `select-text` on outer container to `select-none`.
3. In `apps/web/src/features/reader/components/PdfPageCanvas.tsx:242, 257`:
   Change `select-text` on page container and page card to `select-none`.
   Ensure line 282 `.textLayer` retains `select-text`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- ScholarSelectionMenuCopy.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/reader/components/ScholarSelectionMenu.tsx apps/web/src/features/reader/components/PdfCanvasViewer.tsx apps/web/src/features/reader/components/PdfPageCanvas.tsx apps/web/src/features/reader/__tests__/ScholarSelectionMenuCopy.test.tsx
git commit -m "feat(reader): isolate text selection to textLayer and add direct clean copy button"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Horizontal Pan & Trackpad Scroll on Zoom

**Files:**
- Create: `apps/web/src/features/reader/__tests__/PdfCanvasViewerPanZoom.test.tsx`
- Modify: `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:650, 672-680`

**Interfaces:**
- Consumes: `readingMode`, `effectiveZoom`
- Produces: `min-w-fit w-fit mx-auto` pages wrapper and subtle horizontal scroll styling when zoomed in.

- [ ] **Step 1: Write failing test for pages wrapper alignment**

Create `apps/web/src/features/reader/__tests__/PdfCanvasViewerPanZoom.test.tsx`:
```tsx
import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PdfCanvasViewer } from "../components/PdfCanvasViewer";

vi.mock("@/features/reader/lib/pdfjs-init", () => ({}));

describe("PdfCanvasViewer Pan & Zoom Container", () => {
  it("uses min-w-fit w-fit mx-auto to prevent flex horizontal clipping", () => {
    const { container } = render(
      <PdfCanvasViewer
        documentId="doc-test"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1.5}
        rotationDeg={0}
      />
    );
    
    const pagesContainer = container.querySelector(".min-w-fit.w-fit.mx-auto");
    expect(pagesContainer).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- PdfCanvasViewerPanZoom.test.tsx`
Expected: FAIL because `w-full mx-auto` is currently used.

- [ ] **Step 3: Update `PdfCanvasViewer.tsx` container classes**

In `apps/web/src/features/reader/components/PdfCanvasViewer.tsx:672`:
Change `w-full mx-auto pb-16 flex flex-col items-center` to `min-w-fit w-fit mx-auto pb-16 flex flex-col items-center`.
In line 650:
Allow subtle horizontal scrollbar when `effectiveZoom > 1.0` so user sees scroll capability, while supporting trackpad two-finger pan.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- PdfCanvasViewerPanZoom.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/reader/components/PdfCanvasViewer.tsx apps/web/src/features/reader/__tests__/PdfCanvasViewerPanZoom.test.tsx
git commit -m "fix(reader): support horizontal pan and scroll on zoom without flex clipping"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: Comprehensive 4 Gates Verification & Production Deployment

**Files:**
- None (system-wide verification)

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: All clean, 0 errors.

- [ ] **Step 2: Gate 2 - Backend & Boundary Tests**

Run: `uv run pytest`
Expected: 100% tests pass.

- [ ] **Step 3: Gate 3 - Frontend Unit Tests**

Run: `npm --prefix apps/web run test`
Expected: 100% tests pass.

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`
Expected: Clean build with 0 TypeScript/Vite errors.

- [ ] **Step 5: In-Plan VPS Sync**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0, live system updated at `https://verischolar.duckdns.org`.

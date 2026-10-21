# Project: VeriScholar UI/UX Polish & Production Deployment

## Architecture
VeriScholar frontend is a Vite + React + TypeScript single-page application located in `apps/web`.
Key modules:
- `apps/web/src/features/dashboard/`: Chat workspace, streaming chat hook (`useStreamingChat.ts`), chat input box (`DashboardChatInputBox.tsx`), chat stream view (`DashboardChatStreamView.tsx`), workspace layout (`DashboardWorkspace.tsx`).
- `apps/web/src/features/reader/`: Academic markdown rendering (`AcademicMarkdownRenderer.tsx`), PDF canvas viewer (`PdfCanvasViewer.tsx`, `PdfPageCanvas.tsx`), reader state store (`useReaderStore.ts`).
- `apps/web/src/features/landing/`: Demo chat simulation panel (`DemoChatPanel.tsx`).
- `apps/web/src/index.css`: Tailwind styling, CSS variables, Claude-inspired typography tokens, `@font-face` definitions.
- `scripts/deploy_web.sh`: Web bundle production build and static asset deployment script.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Academic Markdown Rendering | Format AI responses with h2/h3, bold, italic, lists, and KaTeX math without raw markdown syntax | M1 | Survey (R1) |
| 2 | Interactive Citation Chips | Parse citation tags (`[^cit_x]`, `[cit_x]`) into clickable chips navigating to PDF bounding box and page | M1 | Survey (R1) |
| 3 | Chat Streaming State Machine | Accurately process SSE `reasoning`, `token`, `citations`, `done`, resetting `isStreaming` and `isReasoning` | M1 | Survey (R2) |
| 4 | Stream Completion & Input Unlock | Instantly remove "Đang suy luận...", hide "Dừng suy luận", and unlock chat textarea upon stream completion/abort | M1 | Survey (R2) |
| 5 | Claude-Style Typography Alignment | Prioritize Google Fonts `Newsreader`/`Lora` for serif titles and `Inter`/`Plus Jakarta Sans` for body text with leading 1.55 and warm tokens | M2 | Survey (R3) |
| 6 | Debounced PDF Canvas Scaling | Implement 80-120ms debounced ResizeObserver preventing PDF.js re-render thrashing during split-pane resizing | M2 | Survey (R4) |
| 7 | Full-Width PDF Auto-Fit & Dynamic Scaling | Ensure 100% paper width remains visible without horizontal clipping, detect true page dimensions, remove `w-max` | M2 | Survey (R4) |
| 8 | Split Pane Bounds & Drag Performance | Remove drag transition lag (`transition-none` when dragging) and enforce minimum width (`max(400px, 35%)`) | M2 | Survey (R4) |
| 9 | Verification & Type Safety | `pnpm --prefix apps/web exec tsc -b` exits with 0 errors and all Vitest tests pass with 100% pass rate | M3 | Survey (R5) |
| 10 | Atomic Web Deployment & Live Validation | Upgrade `deploy_web.sh` with `rsync --delete --delay-updates`, deploy to `/var/www/verischolar/web`, reload Nginx, verify HTTP 200 on `https://verischolar.duckdns.org/dashboard` | M3 | Survey (R5) |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Socratic Chat Engine & Academic Rich-Text | R1 & R2: Markdown parser, citation mapping & click navigation, SSE state machine, token flush, input unlock | none | IN_PROGRESS |
| M2 | Visual Polish & PDF Dynamic Engine | R3 & R4: Font stack order, line-height 1.55, warm color tokens, debounced PDF ResizeObserver, true page width detection, split pane constraints | M1 | PLANNED |
| M3 | Verification, Atomic Deployment & Production Acceptance | R5: TypeScript type checks, full Vitest test suite, deploy_web.sh atomic deployment, Nginx reload, live HTTPS validation | M2 | PLANNED |

## Interface Contracts
### `useStreamingChat.ts` ↔ UI Components
- State contract: `isGenerating` (boolean), `isStreaming` (boolean), `isReasoning` (boolean), `stopGeneration()` (aborts cleanly, flushes queue, resets flags).
- Citation data model:
  ```ts
  interface CitationBadgeData {
    citation_id: string;
    paper_id?: string;
    document_id?: string;
    page: number;
    bbox?: [number, number, number, number, number]; // [x0, y0, x1, y1, page]
    snippet?: string;
    title?: string;
  }
  ```
- Click handler contract: `onCitationClick(citationId: string)` in `DashboardWorkspace` extracts citation by ID or index, updates `activeBbox` in store, calls `setCurrentPage(targetPage)`, and switches mobile view to `reader`.

### Typography Variables (`index.css` ↔ Tailwind Components)
- `--font-serif`: `"Newsreader", "Lora", serif`
- `--font-sans`: `"Inter", "Plus Jakarta Sans", sans-serif`
- Reading text class: `font-sans text-body leading-[1.55]` (body `#3d3d3a`, dark `#d1ccc2`)
- Display heading class: `font-serif text-ink` (ink `#141413`, dark `#f4f0ea`)

### PDF Viewer Scaling Contract (`PdfCanvasViewer.tsx` ↔ Split Pane)
- Container width observed via debounced `ResizeObserver` (80ms debounce).
- `effectiveZoom` computed dynamically against `detectedPageWidth` (measured from page 1 or document metadata).
- `pagesContainer` enforces `w-full max-w-full overflow-x-hidden`.

## Code Layout
- Milestone 1 owned files:
  - `apps/web/src/features/dashboard/hooks/useStreamingChat.ts`
  - `apps/web/src/features/reader/components/AcademicMarkdownRenderer.tsx`
  - `apps/web/src/features/dashboard/components/DashboardChatStreamView.tsx`
  - `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
  - `apps/web/src/features/landing/components/DemoChatPanel.tsx`
  - `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx` (citation click handling & chat layout)
- Milestone 2 owned files:
  - `apps/web/src/index.css`
  - `apps/web/src/features/reader/components/PdfCanvasViewer.tsx`
  - `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx` (split pane width styling & drag transitions)
- Milestone 3 owned files:
  - `scripts/deploy_web.sh`
  - Production build and deployment validation

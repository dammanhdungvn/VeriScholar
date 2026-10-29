# alphaXiv Minimalist Dashboard, Agent Stepper, Concept Pills & Mermaid Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the VeriScholar `/dashboard/:id` experience to match the radical minimalism of `alphaXiv.org` and modern AI Agent steppers: fix scroll & caret bugs, enforce single Bounding Box with instant dismissal, introduce a real-time `Working` / `Thought for Xs` / `Worked for Xs >` collapsible reasoning block, replace legacy `[1][2]` citations with interactive `[ ↪ Concept ]` pills and hover source preview cards, support Mermaid diagram generation with SVG/PNG export, and provide a 100% paper view with a floating AI assistant bubble and slide-over panel.

**Architecture:** Frontend state orchestrates paper visibility via Zustand (`useWorkspaceStore` & `useReaderStore`). Layout container enforces strict viewport boundaries (`h-screen overflow-hidden`) preventing scroll leakage. `AcademicMarkdownRenderer` parses concept tags into interactive pills with hover popover snippets. `MermaidRenderer` compiles syntax to SVG with canvas-based PNG download. `SocraticThinkingBlock` encapsulates reasoning telemetry and step-by-step action logs.

**Tech Stack:** React 19, Tailwind CSS, Lucide React, Zustand, TanStack React Query, Mermaid.js, Vitest, FastAPI, Python 3.12.

**Spec:** [`docs/superpowers/specs/2026-10-28-alphaxiv-minimalist-dashboard-and-frontend-fixes-design.md`](../specs/2026-10-28-alphaxiv-minimalist-dashboard-and-frontend-fixes-design.md)

## Global Constraints
- `packages/core` must remain strictly untouched (Hexagonal Architecture).
- Radical minimalism: zero technical jargon, no raw hex codes or algorithm names on UI.
- All 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm build`) must pass with exit code 0.
- In-Plan VPS Sync: execute `bash scripts/deploy_to_vps.sh --fast` after each task commit.

## Review Focus
1. Bounding Box must never render more than 1 box at a time under any circumstance.
2. Clicking outside the PDF Bounding Box or pressing `Esc` must immediately dismiss the highlight without page reload.
3. Chat stream auto-scroll must never push the browser viewport or header off-screen.
4. Thinking Stepper must collapse automatically to `Worked for Xs >` after stream completion and expand cleanly on click.
5. Concept Pills must show a hover preview card with snippet and `Page X`, and click to jump and highlight without `[1][2]` or footer citations.
6. Mermaid diagrams must download cleanly as both `.svg` and `.png` across browsers.
7. Closing the Assistant panel with `✕` must smoothly expand the paper to 100% and show the floating AI bubble.

---

### Task 1: Fix Scroll Leakage, Horizontal Jitter & Refine Streaming Caret

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:410-430`
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx:490-505`
- Create: `apps/web/src/features/dashboard/__tests__/LayoutScrollAndCaretFix.test.tsx`

- [ ] **Step 1: Write RED unit test for container scroll isolation and streaming caret**
Create `apps/web/src/features/dashboard/__tests__/LayoutScrollAndCaretFix.test.tsx`:
1. `DashboardWorkspace` layout container has `overflow-hidden` and `overflow-x-hidden`.
2. `AcademicMarkdownRenderer` does NOT render a standalone chunky orange block `w-1.5 h-4` on empty stream, but renders an inline subtle pulse caret.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- LayoutScrollAndCaretFix.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement scroll container isolation and refine caret**
1. In `DashboardWorkspace.tsx`:
   - Replace `bboxRef.current.scrollIntoView({ behavior: "smooth", block: "center" })` with local scroll inside the viewer container.
   - Enforce `overflow-x-hidden` on chat scroll container and composer box.
2. In `AcademicMarkdownRenderer.tsx`:
   - Replace `<span className="inline-block w-1.5 h-4 ml-1 rounded-[1px] bg-[#cc785c] ... />` with an inline subtle streaming indicator that only renders adjacent to rendered text.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- LayoutScrollAndCaretFix.test.tsx`
Expected: PASS

- [ ] **Step 5: Run full web tests and commit**
```bash
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/web/src/features/dashboard/__tests__/LayoutScrollAndCaretFix.test.tsx
git commit -m "fix(dashboard): isolate scroll containers and refine streaming caret"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Enforce Single Bounding Box & Instant Dismissal Mechanism

**Files:**
- Modify: `apps/web/src/features/reader/components/BboxHighlightLayer.tsx:20-75`
- Modify: `apps/web/src/features/reader/stores/useReaderStore.ts:50-80`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1395-1415`
- Create: `apps/web/src/features/reader/__tests__/BboxSingleHighlightAndDismiss.test.tsx`

- [ ] **Step 1: Write RED unit test for single Bounding Box and dismiss**
Create `apps/web/src/features/reader/__tests__/BboxSingleHighlightAndDismiss.test.tsx`:
1. When multiple boxes are passed, `BboxHighlightLayer` renders at most ONE bounding box.
2. Pressing `Escape` or clicking `onClear` invokes the dismiss handler.
3. Re-clicking an active citation toggles it off.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- BboxSingleHighlightAndDismiss.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement single Bounding Box cap and instant dismiss**
1. In `BboxHighlightLayer.tsx`:
   - Enforce `resolvedBoxes = resolvedBoxes.slice(0, 1)`.
   - Add global `keydown` listener for `Escape` to call `onClear()`.
   - Ensure dismiss button `✕` is prominently styled and clickable.
2. In `DashboardWorkspace.tsx`:
   - When citation click occurs on the currently active citation, toggle it off (`setActiveBboxStore(null); setActiveCitation(null, null);`).
   - Pass single primary box to reader store.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- BboxSingleHighlightAndDismiss.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web tests and commit**
```bash
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/features/reader/components/BboxHighlightLayer.tsx apps/web/src/features/reader/stores/useReaderStore.ts apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/reader/__tests__/BboxSingleHighlightAndDismiss.test.tsx
git commit -m "feat(reader): enforce single bounding box and instant escape dismissal"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Build Socratic Thinking Block Component with Agent Activity Stepper

**Files:**
- Create: `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx`
- Modify: `apps/web/src/features/dashboard/hooks/useStreamingChat.ts:275-295`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1340-1365`
- Create: `apps/web/src/features/dashboard/__tests__/SocraticThinkingBlock.test.tsx`

- [ ] **Step 1: Write RED unit test for SocraticThinkingBlock**
Create `apps/web/src/features/dashboard/__tests__/SocraticThinkingBlock.test.tsx`:
1. Displays `Working` / `Reading...` / `Thought for Xs >` live stepper during streaming.
2. Automatically collapses to single header `Worked for Xs >` when streaming finishes.
3. Clicking `>` expands the action history and full thought text; clicking `^` or header collapses it back.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- SocraticThinkingBlock.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement SocraticThinkingBlock and hook integration**
1. Create `SocraticThinkingBlock.tsx` following the exact design in User Images 1-4.
2. In `useStreamingChat.ts`:
   - Catch event `parsed.type === "reasoning"` and extract thought steps.
   - Track `thought_duration_seconds`.
3. In `DashboardWorkspace.tsx`:
   - Replace `<details className="group mb-3 ...">` with `<SocraticThinkingBlock />`.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- SocraticThinkingBlock.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web tests and commit**
```bash
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx apps/web/src/features/dashboard/hooks/useStreamingChat.ts apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/__tests__/SocraticThinkingBlock.test.tsx
git commit -m "feat(chat): add SocraticThinkingBlock with agent activity stepper and collapsible header"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Semantic Concept Pills & Hover Source Preview Popover

**Files:**
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx:50-130,500-525`
- Modify: `apps/api/src/api/services/session_chat_service.py:2080-2115`
- Create: `apps/web/src/components/shared/__tests__/ConceptPillsAndPreview.test.tsx`

- [ ] **Step 1: Write RED unit test for concept pills and hover preview**
Create `apps/web/src/components/shared/__tests__/ConceptPillsAndPreview.test.tsx`:
1. Renders concept pills `[ ↪ Architecture ]` instead of `[1] [2]`.
2. Does NOT render the footer `Nguồn trích dẫn (X)`.
3. Hovering over a concept pill renders a floating popover with source snippet and `Page X`.
4. Clicking the concept pill invokes `onCitationClick` to jump and highlight.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- ConceptPillsAndPreview.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement concept pills, hover preview card, and backend prompt update**
1. In `AcademicMarkdownRenderer.tsx`:
   - Parse `[cite:ConceptName]`, `[ConceptName]`, and map to citations.
   - Render concept pill component with hover popover tooltip card (showing snippet + `Page X`).
   - Remove `citation-sources-footer` section.
2. In `session_chat_service.py`:
   - Update prompt rules: attach concept tags `[cite:ConceptName]` instead of numbered `[1] [2]`.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- ConceptPillsAndPreview.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web tests and commit**
```bash
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/api/src/api/services/session_chat_service.py apps/web/src/components/shared/__tests__/ConceptPillsAndPreview.test.tsx
git commit -m "feat(citations): implement semantic concept pills with hover source preview popover"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 5: Mermaid Visualization & SVG/PNG Vector Export

**Files:**
- Modify: `apps/web/src/components/shared/MermaidRenderer.tsx:1-150`
- Modify: `apps/api/src/api/services/session_chat_service.py:120-150`
- Create: `apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx`

- [ ] **Step 1: Write RED unit test for Mermaid export features**
Create `apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx`:
1. Renders Mermaid diagram container with SVG output.
2. Renders "Tải SVG" button and "Tải PNG" button.
3. Clicking copy or export triggers corresponding handler.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- MermaidExportRenderer.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement SVG/PNG export buttons and prompt guidance**
1. In `MermaidRenderer.tsx`:
   - Add `handleDownloadSvg`: serialize container SVG to Blob and trigger download.
   - Add `handleDownloadPng`: draw SVG onto an in-memory `<canvas>` at 2x scale and export `image/png`.
   - Add sleek buttons in the diagram card header: `[Tải SVG]`, `[Tải PNG]`, `[Sao chép mã]`.
2. In `session_chat_service.py`:
   - Add system prompt rule: When explaining architectures, flowcharts, or pipelines, Socratic Copilot generates clean ````mermaid code blocks.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- MermaidExportRenderer.test.tsx`
Expected: PASS

- [ ] **Step 5: Run full tests and commit**
```bash
uv run pytest tests/unit/api/test_section_expansion.py
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/components/shared/MermaidRenderer.tsx apps/api/src/api/services/session_chat_service.py apps/web/src/components/shared/__tests__/MermaidExportRenderer.test.tsx
git commit -m "feat(mermaid): add svg and png export capabilities and system prompt guidance"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 6: alphaXiv-style Minimalist Layout: 100% Paper, Floating FAB & Assistant Slide-Over

**Files:**
- Create: `apps/web/src/features/dashboard/components/VerticalEdgeDock.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:800-1250`
- Create: `apps/web/src/features/dashboard/__tests__/DashboardAlphaXivLayout.test.tsx`

- [ ] **Step 1: Write RED unit test for alphaXiv layout and floating FAB**
Create `apps/web/src/features/dashboard/__tests__/DashboardAlphaXivLayout.test.tsx`:
1. By default or when closed, paper is 100% width and floating AI FAB is visible in bottom-right.
2. Clicking the floating FAB opens Assistant panel.
3. Assistant panel header displays "Assistant", `(+) Đoạn chat mới`, and `✕` close button.
4. Clicking `✕` closes Assistant and restores 100% paper width.

- [ ] **Step 2: Run test to verify it fails**
Run: `npm --prefix apps/web run test -- DashboardAlphaXivLayout.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement alphaXiv layout, floating FAB, and VerticalEdgeDock**
1. Create `VerticalEdgeDock.tsx`:
   - Icons for Info `ⓘ`, Notes `📝`, and Assistant `🤖`.
2. In `DashboardWorkspace.tsx`:
   - Support `isAssistantOpen` state (defaults to open or toggled via FAB).
   - Render Floating AI Chat Bubble at bottom-right (`fixed bottom-6 right-6 z-40`) when assistant is closed.
   - When open, render right panel with header: "Assistant", `(+) Đoạn chat mới`, and `✕` button.
   - Remove noisy 5-tab bar, delegating secondary tools to `VerticalEdgeDock.tsx`.

- [ ] **Step 4: Run test to verify it passes**
Run: `npm --prefix apps/web run test -- DashboardAlphaXivLayout.test.tsx`
Expected: PASS

- [ ] **Step 5: Run full web tests and commit**
```bash
npm --prefix apps/web run test && npm --prefix apps/web run build
git add apps/web/src/features/dashboard/components/VerticalEdgeDock.tsx apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/__tests__/DashboardAlphaXivLayout.test.tsx
git commit -m "feat(dashboard): implement alphaXiv-style 100% paper layout with floating FAB"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 7: Comprehensive 4 Gates Verification & Live VPS Rollout

**Files:**
- None (system-wide verification)

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors.

- [ ] **Step 2: Gate 2 - Backend Tests**
Run: `uv run pytest`
Expected: 100% tests pass (269+ passed).

- [ ] **Step 3: Gate 3 - Frontend Tests**
Run: `npm --prefix apps/web run test`
Expected: 100% tests pass across all test suites.

- [ ] **Step 4: Gate 4 - Frontend Production Build**
Run: `npm --prefix apps/web run build`
Expected: Vite build succeeds with exit code 0.

- [ ] **Step 5: Live VPS Rollout**
Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: 200 OK at `https://verischolar.duckdns.org`.

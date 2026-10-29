# Dashboard Minimalist Cleanup & Socratic Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 11 minimalist UI/UX refinements across Taskbar, Avatar Dropdown, PDF Toolbar, Assistant Header, Socratic Thinking Block, and Grounded Concept Citations according to user specifications and reference images.

**Architecture:** In-place refactoring of existing React components in `apps/web/src/features/{dashboard,reader,auth}`, preserving Zustand store states (`useDashboardStore`, `useWorkspaceStore`, `useReaderStore`) and theme system (`useTheme`). Clean separation between taskbar navigation, reader viewport controls, chat header, modern AI reasoning stepper, and grounded citation pills.

**Tech Stack:** React 19, TypeScript, Tailwind CSS, Lucide React icons, Vitest, React Testing Library, FastAPI backend (untouched), PostgreSQL pgvector.

**Spec:** [`docs/superpowers/specs/2026-10-28-dashboard-minimalist-cleanup-design.md`](../specs/2026-10-28-dashboard-minimalist-cleanup-design.md)

## Global Constraints

- Preserve Hexagonal Architecture: `packages/core/` strictly untouched.
- Radical Minimalism: No technical jargon, no raw hex values, no duplicate floating bubbles or unnecessary decorative glow effects.
- Rule 9 (In-Plan VPS Sync Protocol): After each successful git commit, execute `bash scripts/deploy_to_vps.sh --fast`.
- 4 Verification Gates must pass with 100% exit code 0 before task completion.

## Review Focus

1. **Taskbar Collapsed Button Alignment:** When the sidebar is collapsed to icon-only mode (`w-14`), the `(+)` button must be perfectly circular (`rounded-full w-10 h-10`) with the plus icon precisely centered at (20px, 20px).
2. **Context Menu Outside Click:** Clicking outside or pressing Escape while the session item `...` context menu is open must close it without triggering navigation.
3. **Dark/Light Mode Toggle in Avatar Popover:** Toggling the theme from the avatar menu must immediately update `document.documentElement.classList` (`dark` / `light`) and persist to storage without closing ungracefully.
4. **Thinking Block Monologue Toggle:** Clicking the thought header `Thought for Xs >` or `✓ Thinking Finished ∨` toggles internal reasoning text visibility smoothly without leaking layout scroll.
5. **Concept Pill Space Formatting:** Inline tags like `[ ↪ SelectiveAttention ]` must render as `[ ↪ Selective Attention ]` and retain correct `page_number` and `bounding_boxes` jump handler.

---

### Task 1: Taskbar & Avatar Dropdown Refinements (Req 7, 8, 9)

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
- Modify: `apps/web/src/features/auth/components/AvatarDropdownPopover.tsx`
- Test: `apps/web/src/features/dashboard/components/__tests__/TaskbarAndAvatarRefinements.test.tsx`

**Interfaces:**
- `DashboardTaskbar`: Consumes `sessions`, `activeSessionId`, `onSelectSession`, `onNewSession`. Adds `isRecentsCollapsed` state, context menu state for sessions (Pin, Mark as unread, Rename, Delete). Removes glowing active background.
- `AvatarDropdownPopover`: Consumes `useTheme` hook (`toggleTheme`, `isDark`). Replaces upgrade button with Theme Switcher menu item.

- [ ] **Step 1: Write the failing unit tests**

Create `apps/web/src/features/dashboard/components/__tests__/TaskbarAndAvatarRefinements.test.tsx`:
```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { DashboardTaskbar } from "../DashboardTaskbar";
import { AvatarDropdownPopover } from "@/features/auth/components/AvatarDropdownPopover";

describe("Taskbar and Avatar Refinements", () => {
  it("renders new chat button as circular when collapsed", () => {
    // Renders with sidebarState collapsed
    // Verifies button has rounded-full class and centered Plus icon
  });

  it("toggles recents list when clicking Recents header", () => {
    // Verifies Recents collapsible section toggles session items visibility
  });

  it("renders session context menu with Pin, Mark unread, Rename, Delete but no Add to project", () => {
    // Verifies ... button triggers context menu with 4 options and NOT Add to project
  });

  it("renders Dark/Light mode toggle in AvatarDropdownPopover replacing upgrade button", () => {
    // Verifies popover-theme-toggle-btn exists and popover-upgrade-btn is absent
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- TaskbarAndAvatarRefinements`
Expected: FAIL (missing theme toggle in popover, missing recents collapse toggle, missing session context menu).

- [ ] **Step 3: Implement Taskbar & Avatar refinements**

1. In `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`:
   - Remove `bg-coral-500/15 border border-coral-500/25` glowing styling from `navItems.map`.
   - Update New Chat `(+)` button: When `!isExpanded`, apply `w-10 h-10 rounded-full mx-auto p-0 flex items-center justify-center aspect-square`.
   - Add state `const [isRecentsCollapsed, setIsRecentsCollapsed] = useState(false);`.
   - Render `Recents` header with clickable toggle button and rotating `ChevronDown`.
   - Add `...` action button on session hover with context menu containing `Pin`, `Mark as unread`, `Rename`, `Delete` (no `Add to project`).
2. In `apps/web/src/features/auth/components/AvatarDropdownPopover.tsx`:
   - Import `useTheme` from `@/hooks/useTheme` and `Sun, Moon` from `lucide-react`.
   - Replace `popover-upgrade-btn` with `popover-theme-toggle-btn` that calls `toggleTheme()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- TaskbarAndAvatarRefinements`
Expected: PASS

- [ ] **Step 5: Commit and sync to VPS**

```bash
git add apps/web/src/features/dashboard/components/DashboardTaskbar.tsx apps/web/src/features/auth/components/AvatarDropdownPopover.tsx apps/web/src/features/dashboard/components/__tests__/TaskbarAndAvatarRefinements.test.tsx
git commit -m "feat(dashboard): refine taskbar layout, session recents menu, and avatar theme toggle"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 2: PDF Toolbar & Options Menu Cleanup (Req 1, 2, 3)

**Files:**
- Modify: `apps/web/src/features/reader/components/ViewportControls.tsx`
- Modify: `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx`
- Test: `apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx`

**Interfaces:**
- `ViewportControls`: Remove `Zen PDF` button and `mode view` switcher.
- `WorkspaceToolsMenu`: Remove `mode view` and `Zen PDF`. Add `onOpenNotes` prop and "Sổ ghi chú" menu option.

- [ ] **Step 1: Write the failing unit tests**

Create `apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx`:
```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ViewportControls } from "../ViewportControls";
import { WorkspaceToolsMenu } from "@/features/dashboard/components/WorkspaceToolsMenu";

describe("Viewport Controls and Tools Menu Cleanup", () => {
  it("does not render Zen PDF or Mode View buttons in ViewportControls", () => {
    // Verifies zen-pdf-btn and mode-view buttons are absent
  });

  it("renders Sổ ghi chú in WorkspaceToolsMenu and calls onOpenNotes", () => {
    // Verifies 'Sổ ghi chú' item is present, while Zen PDF and Mode view are absent
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- ViewportControlsCleanup`
Expected: FAIL

- [ ] **Step 3: Implement ViewportControls & WorkspaceToolsMenu cleanup**

1. In `apps/web/src/features/reader/components/ViewportControls.tsx`:
   - Remove `zen-pdf-btn` and any mode-view switcher buttons. Keep page navigation, zoom, and options button.
2. In `apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx`:
   - Remove "Mode view" (Xem 1 trang / 2 trang) section.
   - Remove "Đọc tập trung Zen PDF" item.
   - Add "Sổ ghi chú" item with `BookMarked` icon, triggering `onOpenNotes?.()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- ViewportControlsCleanup`
Expected: PASS

- [ ] **Step 5: Commit and sync to VPS**

```bash
git add apps/web/src/features/reader/components/ViewportControls.tsx apps/web/src/features/dashboard/components/WorkspaceToolsMenu.tsx apps/web/src/features/reader/components/__tests__/ViewportControlsCleanup.test.tsx
git commit -m "refactor(reader): remove zen pdf and mode view, add notebook option in tools menu"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 3: Assistant Panel Header & Floating Bubble Unification (Req 4, 5, 6)

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
- Delete / Refactor: `apps/web/src/features/dashboard/components/VerticalEdgeDock.tsx`
- Test: `apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx`

**Interfaces:**
- `DashboardWorkspace`: Header cleaned of `New Chat`, `Assistant` label, `Settings`, `Dark/Light`, and `Zen Chat`. Renames all `Socratic Copilot` strings to `Socratic Assistant`. Removes `VerticalEdgeDock`. Renders only single `floating-assistant-fab` in the corner with `Sparkles` icon.

- [ ] **Step 1: Write the failing unit tests**

Create `apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DashboardWorkspace } from "../DashboardWorkspace";

describe("Assistant Panel Header and Floating Bubble Unification", () => {
  it("does not render New Chat, Settings, Dark/light or Zen Chat in Assistant header", () => {
    // Verifies header has only close or fullscreen controls
  });

  it("displays Socratic Assistant instead of Socratic Copilot", () => {
    // Verifies text Socratic Assistant is present
  });

  it("does not render top vertical edge dock and keeps only corner assistant FAB", () => {
    // Verifies vertical-edge-dock is not rendered
    // Verifies floating-assistant-fab has Sparkles icon
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- AssistantPanelUnification`
Expected: FAIL

- [ ] **Step 3: Implement Assistant Panel & FAB unification**

1. In `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`:
   - Clean the Assistant Panel header: Remove `(+) New Chat`, remove `Assistant` title, remove `Settings` button, remove `Moon/Sun` toggle, remove `Zen Chat`.
   - Replace any instance of `Socratic Copilot` with `Socratic Assistant`.
   - Remove `<VerticalEdgeDock ... />` from the layout completely.
   - Keep the single corner FAB `floating-assistant-fab` (shown when assistant is closed) styled with `Sparkles` icon.
   - When "Sổ ghi chú" is chosen from tools menu, toggle `activeRightTab` to `"notes"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- AssistantPanelUnification`
Expected: PASS

- [ ] **Step 5: Commit and sync to VPS**

```bash
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/components/__tests__/AssistantPanelUnification.test.tsx
git commit -m "feat(chat): rename to Socratic Assistant, streamline header, and unify floating action button"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 4: Socratic Thinking Block & Grounded Citation Formatting (Req 10, 11)

**Files:**
- Modify: `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx`
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx`
- Test: `apps/web/src/features/dashboard/components/__tests__/ThinkingBlockAndCitationFormat.test.tsx`

**Interfaces:**
- `SocraticThinkingBlock`: Renders high-level AI reasoning state: `Thought for Xs >` (or `Working...`), collapsible reasoning monologue; removes robotic debug log lines (`Analyzed Bounding Box #Page X`).
- `AcademicMarkdownRenderer`: Formats concept pills with spaces (`formatConceptTitle`), jumping to the exact page and highlighting the single bounding box accurately.

- [ ] **Step 1: Write the failing unit tests**

Create `apps/web/src/features/dashboard/components/__tests__/ThinkingBlockAndCitationFormat.test.tsx`:
```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SocraticThinkingBlock } from "../SocraticThinkingBlock";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";

describe("Socratic Thinking Block and Citation Formatting", () => {
  it("does not render repeated Analyzed Bounding Box lines in thinking block", () => {
    // Verifies robotic debug lines are absent and replaced with clean thought header
  });

  it("formats PascalCase concept pill tags with human spaces", () => {
    // Content with "[ ↪ SelectiveAttention ]" renders text "Selective Attention"
  });

  it("triggers jumpToPage and setActiveBbox accurately on concept pill click", () => {
    // Clicking concept pill sends correct page number and single bounding box
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- ThinkingBlockAndCitationFormat`
Expected: FAIL

- [ ] **Step 3: Implement Socratic Thinking Block & Concept Pill Formatting**

1. In `apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx`:
   - Remove the repetitive `Analyzed Bounding Box #Page X` loop.
   - Clean up thinking presentation:
     - Live state: subtle indicator `Thought for {elapsed}s >` with gentle pulse.
     - Finished state: `Thought for {total}s >` (collapsed by default).
     - Expanded state: cleanly formatted monologue reasoning paragraphs.
2. In `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx`:
   - Add helper `formatConceptTitle(raw: string)`:
     Inserts spaces before uppercase letters in camelCase/PascalCase (e.g. `SelectiveAttention` -> `Selective Attention`, `ContextNoise` -> `Context Noise`, `PerformanceGain` -> `Performance Gain`).
   - Ensure the concept pill click handler extracts the matched chunk's `page_number` and `bounding_boxes` and dispatches single bbox activation.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- ThinkingBlockAndCitationFormat`
Expected: PASS

- [ ] **Step 5: Commit and sync to VPS**

```bash
git add apps/web/src/features/dashboard/components/SocraticThinkingBlock.tsx apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/web/src/features/dashboard/components/__tests__/ThinkingBlockAndCitationFormat.test.tsx
git commit -m "feat(citations): format concept pill names with spaces and polish Socratic thinking block"
bash scripts/deploy_to_vps.sh --fast || true
```

---

### Task 5: Full 4-Gate Verification & Headless Chrome Visual Audit

**Files:**
- Verify: Full codebase

- [ ] **Step 1: Run Gate 1 (Ruff Lint & Format)**
```bash
uv run ruff check . && uv run ruff format --check .
```
Expected: All checks pass with 0 errors.

- [ ] **Step 2: Run Gate 2 (Backend Tests)**
```bash
uv run pytest
git checkout report-datn/main.pdf
```
Expected: 269/269 passed.

- [ ] **Step 3: Run Gate 3 (Frontend Tests)**
```bash
npm --prefix apps/web run test
```
Expected: 100% test suites pass.

- [ ] **Step 4: Run Gate 4 (Web Production Build)**
```bash
npm --prefix apps/web run build
```
Expected: Vite build succeeds without error.

- [ ] **Step 5: Visual Verification via Headless Chrome Screenshot**
```bash
google-chrome --headless --no-sandbox --disable-gpu --screenshot=/home/dammanhdungvn/.gemini/antigravity-cli/brain/9a429151-f4f6-428a-8354-b60d9e2b196f/screenshot_final_audit.png --window-size=1920,1080 http://localhost:5173/dashboard
```
Verify screenshot via `read_file` confirming:
- No glowing active nav background
- Circular centered `(+)` button
- Clean PDF toolbar without Zen PDF / Mode view
- Clean Assistant panel header
- Clean thinking block and properly spaced concept pills.

- [ ] **Step 6: Final Git Commit and VPS Sync**
```bash
bash scripts/deploy_to_vps.sh --fast || true
```

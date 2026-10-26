# Workspace UX Refinements & Multi-File Staging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 10 frontend UI/UX refinements on `localhost:5173` including taskbar avatar cleanup, floating popover layer, "Workspace" title, "Nghiên cứu" mode tab, search mode button pruning, Luna 5.6 mouse-drag reasoning slider (Light/Medium/High/Extra High, default Light), standalone dropzone removal, and chat input direct drag-and-drop with multi-file staging and concurrent prompt submission.

**Architecture:** 
- Frontend state and styling refactoring using Tailwind CSS, Zustand stores (`useDashboardStore`, `useWorkspaceStore`), and React components.
- Staged file attachments within `DashboardChatInputBox` providing Claude/ChatGPT-grade UX before committing to session ingestion.
- Core and API reasoning effort value object alignment ensuring backwards compatibility and vendor-agnostic mapping.

**Tech Stack:** React 19, TypeScript, Tailwind CSS, Zustand, Lucide React, FastAPI, Pydantic v2, Vitest, Pytest.

**Spec:** User feedback requirements and design consensus on 2026-10-26.

## Global Constraints
- Radical Minimalism (Rule 6): No verbose slogans, no internal technical jargon, clean Apple/Linear aesthetic.
- Relative Markdown Links Only (Rule 5): Never use `file://` URLs in docs.
- Four Verification Gates: Ruff format & check, Pytest, Vitest, Vite build must all pass with exit code 0.
- Localhost only: VPS is offline, do NOT run deploy scripts or SSH.

## Review Focus
- Taskbar avatar button must never show email, only avatar + name + verified tick icon.
- Avatar menu popup must render in an independent floating overlay layer (`fixed`, `z-[100]`), outside sidebar's `overflow-hidden`.
- "Tìm bài báo" mode must not show upload (+) or microphone buttons.
- Dragging mouse horizontally over the Luna reasoning slider must smoothly adjust between Light, Medium, High, and Extra High.
- Dragging PDF onto the chat box in "Nghiên cứu" mode must stage files with dismissible chips and allow entering prompt text before pressing Enter to submit together.

---

### Task 1: Taskbar Avatar Cleanup & True Floating Overlay Popover

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardTaskbar.tsx`
- Modify: `apps/web/src/features/auth/components/AvatarDropdownPopover.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardTaskbar.test.tsx`
- Test: `apps/web/src/features/auth/__tests__/AvatarDropdownPopover.test.tsx`

- [ ] Step 1: Write failing/updated Vitest test in `DashboardTaskbar.test.tsx` verifying that user email is NOT rendered on the avatar trigger button.
- [ ] Step 2: Remove email element from the avatar button in `DashboardTaskbar.tsx:389-391`. Keep only avatar, user full name, and verified badge (`CheckCircle2`).
- [ ] Step 3: Refactor `AvatarDropdownPopover.tsx` to use fixed positioning (`fixed bottom-16 left-3 z-[100]` or dynamic overlay) with a dedicated backdrop click-outside overlay so it never gets clipped by `aside`'s `overflow-hidden` and stays cleanly on the top layer.
- [ ] Step 4: Run `npm --prefix apps/web run test -- DashboardTaskbar.test.tsx AvatarDropdownPopover.test.tsx` to verify tests pass.
- [ ] Step 5: Commit changes with message `feat(taskbar): remove email from avatar button and elevate popover to floating overlay`.

---

### Task 2: Workspace Header, "Nghiên cứu" Mode Tab, and Standalone Dropzone Pruning

**Files:**
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

- [ ] Step 1: Update `UnifiedHeroWorkspace.test.tsx` to assert "Workspace" heading, "Nghiên cứu" mode button, absence of the standalone dropzone card, and scholarly placeholders.
- [ ] Step 2: In `UnifiedHeroWorkspace.tsx:216-218`, change `"Không gian nghiên cứu, {userGreetingName}"` to `"Workspace"`.
- [ ] Step 3: In `UnifiedHeroWorkspace.tsx:240-254`, change mode tab label from `"Đối thoại AI"` to `"Nghiên cứu"`.
- [ ] Step 4: In `UnifiedHeroWorkspace.tsx:398-426`, delete the standalone dropzone card (`Action A: Compact PDF Upload Dropzone`). Keep the topic chips centered neatly under the input box.
- [ ] Step 5: Update placeholder strings in `UnifiedHeroWorkspace.tsx:265-270`:
  - Search mode: `"Tìm kiếm bài báo khoa học theo tiêu đề, tác giả, DOI hoặc arXiv ID..."`
  - Chat/Research mode: `"Đặt câu hỏi nghiên cứu, kéo thả PDF hoặc yêu cầu tóm tắt..."`
- [ ] Step 6: Pass `mode={mode}` prop to `DashboardChatInputBox`.
- [ ] Step 7: Run `npm --prefix apps/web run test -- UnifiedHeroWorkspace.test.tsx` and ensure all tests pass.
- [ ] Step 8: Commit changes with message `feat(workspace): rename hero to Workspace, tab to Nghiên cứu, remove redundant dropzone`.

---

### Task 3: Luna 5.6 Reasoning Effort (Light/Medium/High/Extra High & Mouse Dragging)

**Files:**
- Modify: `apps/web/src/features/dashboard/stores/useDashboardStore.ts`
- Modify: `apps/web/src/features/dashboard/components/ReasoningPopover.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
- Modify: `packages/core/src/core/domain/value_objects/reasoning_effort.py`
- Modify: `apps/api/src/api/schemas/session.py`
- Test: `apps/web/src/features/dashboard/__tests__/ReasoningPopover.test.tsx`
- Test: `apps/api/tests/test_reasoning_effort_endpoint.py`

- [ ] Step 1: Update `useDashboardStore.ts` defining `type ReasoningEffortLevel = "light" | "medium" | "high" | "extra_high"`. Set initial state `reasoningEffort: "light"`, `isReasoningEnabled: false`. Update `resetReasoningEffort()` to reset to `"light"`.
- [ ] Step 2: Update `packages/core/src/core/domain/value_objects/reasoning_effort.py` and `apps/api/src/api/schemas/session.py` to support `light`, `medium`, `high`, `extra_high`, with `map_reasoning_effort_to_provider` mapping `light` -> `off`/0 tokens and `extra_high` -> `high`/max tokens.
- [ ] Step 3: In `ReasoningPopover.tsx`, configure 4 levels:
  - `light`: label `"Light"`, percent 0%
  - `medium`: label `"Medium"`, percent 33.33%
  - `high`: label `"High"`, percent 66.66%
  - `extra_high`: label `"Extra High"`, percent 100%
- [ ] Step 4: Add mouse drag interaction (`onMouseDown`, `onMouseMove`, `onMouseUp` on track or standard range slider with custom styled track) so users can click or drag left/right to decrease/increase reasoning level.
- [ ] Step 5: In `DashboardChatInputBox.tsx`, update reasoning indicator to show active styling when `reasoningEffort !== "light"`.
- [ ] Step 6: Run tests:
  - `npm --prefix apps/web run test -- ReasoningPopover.test.tsx`
  - `uv run pytest apps/api/tests/test_reasoning_effort_endpoint.py`
- [ ] Step 7: Commit changes with message `feat(reasoning): support 4-level Luna 5.6 effort with mouse-drag slider defaulting to light`.

---

### Task 4: Mode-Aware Input & Multi-File Staging with Direct Drag-and-Drop and Prompt Submission

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardChatInputBox.test.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardContainer.test.tsx`

- [ ] Step 1: Write tests in `DashboardChatInputBox.test.tsx` covering:
  - When `mode="search"`, upload `+` button and `Mic` button are not rendered.
  - Dragging files over the chat box highlights drop zone and stages dropped files.
  - Staged files display chips with remove buttons.
  - Submitting sends both staged files and prompt text via `onSendWithFiles` or `onSend`.
- [ ] Step 2: In `DashboardChatInputBox.tsx`:
  - Add props `mode?: "search" | "chat"`, `onSendWithFiles?: (text: string, files: File[]) => void`.
  - Conditional rendering: when `mode === "search"`, hide `+` upload button and `Mic` button.
  - Maintain `stagedFiles: File[]` state.
  - Add native drag & drop handlers (`onDragOver`, `onDragLeave`, `onDrop`) to the chat box container. Validate that only PDF files are accepted (show error toast if invalid).
  - Render staged files as dismissible chips above textarea with PDF icon, file name, formatted size, and `X` button.
  - In `handleSendMessage`: if `stagedFiles.length > 0`, call `onSendWithFiles(inputText, stagedFiles)` and reset `stagedFiles`. Else call standard `onSend`.
- [ ] Step 3: In `UnifiedHeroWorkspace.tsx` and `DashboardContainer.tsx`:
  - Wire `onSendWithFiles`: When files are submitted alongside prompt text:
    - Ingest the files to create the session.
    - Upon session creation and ingestion completion, auto-post the user's prompt text into the session chat so the AI immediately answers based on the newly uploaded document!
- [ ] Step 4: Run `npm --prefix apps/web run test -- DashboardChatInputBox.test.tsx` to verify all test cases pass.
- [ ] Step 5: Commit changes with message `feat(chat-input): add multi-file staging with direct drag-and-drop and concurrent prompt submission`.

---

### Task 5: End-to-End Verification Across All 4 Gates

**Files:**
- Verification only

- [ ] Step 1: Run Gate 1: `uv run ruff check . && uv run ruff format --check .`
- [ ] Step 2: Run Gate 2: `uv run pytest`
- [ ] Step 3: Run Gate 3: `npm --prefix apps/web run test`
- [ ] Step 4: Run Gate 4: `npm --prefix apps/web run build`
- [ ] Step 5: Verify runtime behavior on `http://localhost:5173`.

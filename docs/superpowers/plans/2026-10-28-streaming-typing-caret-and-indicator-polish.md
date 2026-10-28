# Streaming Typing Caret & Modern AI Indicator Polish Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate chat response UI/UX to international product standards (Claude/ChatGPT) by replacing the plain "Đang suy luận..." text with a smooth 3-dot typing wave indicator for pre-text phases, a blinking typing caret during markdown streaming, a clean author header, and a refined minimalist stop button.

**Architecture:**
1. **TypingWaveIndicator Component & Caret in AcademicMarkdownRenderer:** Create a dedicated staggered 3-dot bouncing wave indicator component and add `isStreaming` support with an inline blinking caret (`typing-caret`) at the end of generated text.
2. **Dashboard Workspace & Stream View Integration:** Clean up the message header by removing the loud `Đang suy luận...` text, render the `TypingWaveIndicator` when `is_streaming` is true before content arrives, pass `isStreaming` to `AcademicMarkdownRenderer`, and polish the stop button label to `Dừng` with minimalist styling.
3. **Verification & VPS Rollout:** Verify with frontend unit tests, 4 Verification Gates, and deploy to live VPS.

**Tech Stack:** React 19, Tailwind CSS, Lucide icons, Vitest, Testing Library.

**Spec:**
- `docs/PRD/03-sessions-and-deep-reading-crud.md`
- `AGENTS.md` (Rule 6: Radical Minimalism 80/20, Rule 9: VPS Sync)

## Global Constraints

- Hexagonal architecture: `packages/core/` domain untouched.
- Radical Minimalism 80/20: No robotic technical jargon or clunky floating badges.
- Relative Markdown links only in documentation.
- All 4 verification gates must pass with exit code 0 before task completion.
- Rule 9 VPS deploy protocol (`bash scripts/deploy_to_vps.sh --fast`) executed after every commit.

## Review Focus

1. When Socratic begins generating before any tokens arrive, user sees an elegant 3-dot typing wave indicator instead of a static text badge.
2. When streaming text begins, a blinking amber/coral caret (`w-1.5 h-4 animate-pulse`) flows smoothly at the end of the text.
3. Once streaming completes, the caret disappears smoothly and the citation sources footer renders cleanly.
4. The message header remains clean ("Socratic") without noisy status badges.
5. The stop button uses concise label ("Dừng") with clean, non-intrusive styling.

---

### Task 1: TypingWaveIndicator & Streaming Caret in AcademicMarkdownRenderer

**Files:**
- Create: `apps/web/src/components/shared/TypingWaveIndicator.tsx`
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx`
- Test: `apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx`

**Interfaces:**
- `TypingWaveIndicator`: `({ className }: { className?: string }) => React.JSX.Element`
- `AcademicMarkdownRendererProps`: adds `isStreaming?: boolean`
- Renders `<span data-testid="typing-caret" />` when `isStreaming && content.length > 0`

- [x] **Step 1: Write failing unit test for `AcademicMarkdownRenderer` typing caret and `TypingWaveIndicator`**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `TypingWaveIndicator` and `isStreaming` in `AcademicMarkdownRenderer`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit and VPS fast sync**

```bash
git add apps/web/src/components/shared/TypingWaveIndicator.tsx apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx
git commit -m "feat(ui): add TypingWaveIndicator and streaming typing caret in AcademicMarkdownRenderer"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Refine Chat Views Header, Indicators & Stop Button

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:1340-1375,1510-1525`
- Modify: `apps/web/src/features/dashboard/components/DashboardChatStreamView.tsx:140-165,255-270`

**Interfaces:**
- When `message.is_streaming && !message.content`: render `<TypingWaveIndicator />`
- Pass `isStreaming={message.is_streaming}` into `AcademicMarkdownRenderer`
- Message header: clean `Socratic` without raw "Đang suy luận..." text
- Stop button: `<Square className="w-3 h-3 fill-current text-[#cc785c]" /> <span>Dừng</span>`

- [x] **Step 1: Update `DashboardWorkspace.tsx` and `DashboardChatStreamView.tsx`**
- [x] **Step 2: Run all frontend unit tests**
- [x] **Step 3: Commit and VPS fast sync**

---

### Task 3: Full 4-Gate Verification and Production VPS Deployment

**Files:**
- Ops / Verification

- [x] **Step 1: Gate 1 (Ruff)**
- [x] **Step 2: Gate 2 (Pytest)**
- [x] **Step 3: Gate 3 (Vitest)**
- [x] **Step 4: Gate 4 (Build)**
- [x] **Step 5: Full VPS deployment & Health Probe**

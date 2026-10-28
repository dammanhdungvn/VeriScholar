# Untruncated Chunk Context & Citation Ghost Badge Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure RAG chunk content is fed in its entirety without the arbitrary 1000-character truncation, and eliminate ghost citation badge buttons for ungrounded bracketed numbers like `[13]` and `[7]`.

**Architecture:** 
1. Backend: Update `session_chat_service.py` context assembly to preserve full chunk text up to a safe 12,000 char ceiling.
2. Frontend: Update `AcademicMarkdownRenderer.tsx` so only tokens matching genuine RAG citations are rendered as interactive citation badge buttons; ungrounded bracketed numbers remain plain text.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, React 19, Vitest, TypeScript, Tailwind CSS.

**Spec:** `docs/superpowers/specs/2026-10-28-untruncated-chunk-context-and-citation-ghost-badge-fix-design.md`

## Global Constraints
- Hexagonal architecture: pure business logic in core, I/O in API.
- Radical Minimalism 80/20 in UI copy and components.
- TDD required: red test -> green implementation -> refactor.
- All 4 Verification Gates must pass 100% exit code 0 before completing.
- Deploy to VPS via `bash scripts/deploy_to_vps.sh --fast` after each commit.

## Review Focus
1. Chunk content >= 1000 chars must not be truncated when passed to LLM context.
2. `[13]`, `[7]` in translated text must render as standard text without `cursor-pointer`, button wrapper, or fake tooltips.
3. Genuine `[1]` must continue to render as a clickable orange badge and scroll to its PDF bounding box.
4. Gated footer `Nguồn trích dẫn (1)` must remain clean and not show ungrounded numbers.

---

### Task 1: Backend Full Chunk Context Delivery (Eliminate 1000-Char Cutoff)

**Files:**
- Modify: `apps/api/src/api/services/session_chat_service.py:2660-2675`
- Test: `apps/api/tests/test_chunk_context_assembly.py`

- [ ] **Step 1: Write red test for full chunk context delivery**
  Create `apps/api/tests/test_chunk_context_assembly.py`:
  Test that a chunk with 1,500 characters of text is preserved completely in `evidence_blocks` without being cut off at 1,000 characters.

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run pytest apps/api/tests/test_chunk_context_assembly.py -v`
  Expected: Fails due to 1,000 char truncation.

- [ ] **Step 3: Update `session_chat_service.py`**
  In `apps/api/src/api/services/session_chat_service.py:2664-2666`, replace `matched_content[:1000]` with `matched_content[:12000]` (or full content).

- [ ] **Step 4: Run test to verify it passes**
  Run: `uv run pytest apps/api/tests/test_chunk_context_assembly.py -v`
  Expected: PASS.

- [ ] **Step 5: Commit & Deploy**
  ```bash
  git add apps/api/src/api/services/session_chat_service.py apps/api/tests/test_chunk_context_assembly.py
  git commit -m "fix(rag): preserve full chunk content up to 12000 chars without mid-word truncation"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 2: Frontend Ghost Citation Badge Elimination

**Files:**
- Modify: `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx:68-125, 354-390`
- Test: `apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx`

- [ ] **Step 1: Write red test in `AcademicMarkdownRenderer.test.tsx`**
  Test that when rendering text like `"LSTM [13] và GRU [7] trong mô hình [1]"` with only `[1]` in `citations`:
  - Exactly ONE `citation-badge` element is rendered.
  - `[13]` and `[7]` are rendered as plain text strings, not buttons.

- [ ] **Step 2: Run test to verify it fails**
  Run: `npm --prefix apps/web run test AcademicMarkdownRenderer.test.tsx`
  Expected: Fails because `[13]` and `[7]` are currently rendered as buttons.

- [ ] **Step 3: Update `AcademicMarkdownRenderer.tsx`**
  In `parseInlineCitationsAndMath`:
  If `!matchedCitation`, return `part` (the plain text string).
  In ReactMarkdown `code` renderer:
  If `!matched`, return standard inline code or text instead of a citation badge.

- [ ] **Step 4: Run test to verify it passes**
  Run: `npm --prefix apps/web run test AcademicMarkdownRenderer.test.tsx`
  Expected: PASS.

- [ ] **Step 5: Commit & Deploy**
  ```bash
  git add apps/web/src/components/shared/AcademicMarkdownRenderer.tsx apps/web/src/components/shared/__tests__/AcademicMarkdownRenderer.test.tsx
  git commit -m "fix(reader): render ungrounded bracketed numbers as plain text and eliminate ghost citation badges"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 3: 4 Verification Gates & Production VPS Verification

- [ ] **Step 1: Gate 1 - Python Linter & Formatter**
  Run: `uv run ruff check . && uv run ruff format --check .`
  Expected: 0 errors.

- [ ] **Step 2: Gate 2 - Backend Pytest Suite**
  Run: `uv run pytest`
  Expected: 100% pass (259+ tests).

- [ ] **Step 3: Gate 3 - Frontend Unit Tests**
  Run: `npm --prefix apps/web run test`
  Expected: 100% pass (126+ tests).

- [ ] **Step 4: Gate 4 - Frontend Production Build**
  Run: `npm --prefix apps/web run build`
  Expected: 0 errors, build succeeds.

- [ ] **Step 5: Final Production VPS Deployment & Live Verification**
  Run: `bash scripts/deploy_to_vps.sh --fast`
  Expected: Exit code 0, deployed to `https://verischolar.duckdns.org`.

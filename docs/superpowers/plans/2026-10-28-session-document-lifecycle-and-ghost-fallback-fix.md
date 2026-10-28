# Session-Document Lifecycle Isolation & Ghost Fallback Elimination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate ghost document retention and involuntary attachment of "Attention Is All You Need", ensuring that plain-text chats and empty sessions strictly display the Empty State with 0 documents.

**Architecture:**
- **Streaming Chat:** In `useStreamingChat.ts`, stop automatically attaching `openDocumentIds` when creating a session from a text prompt.
- **Session Container:** In `DashboardContainer.tsx`, reset `useReaderStore` in `handleNewSession()`, and add an explicit `else` branch in session detail synchronization to clear `openDocumentIds` when `docIds.length === 0`.
- **Workspace Fallback Elimination:** In `DashboardWorkspace.tsx`, remove auto-selection of `documentsData.data[0]` and eliminate `documentsData.data[0]` fallbacks in `effectiveOpenIds` and `currentDocTitle`.

**Tech Stack:** React 19, TypeScript, Zustand, TanStack Query, Vitest, Testing Library.

**Spec:** [`docs/superpowers/specs/2026-10-28-session-document-lifecycle-and-ghost-fallback-fix-design.md`](../specs/2026-10-28-session-document-lifecycle-and-ghost-fallback-fix-design.md)

## Global Constraints
- Pure Hexagonal Architecture: `packages/core` remains strictly untouched.
- Radical Minimalism 80/20: Zero clutter, clean typography, explicit user intent only.
- Test-Driven Development (TDD): Red test first, minimal green implementation, refactor.
- 4 Verification Gates must pass before completion (Ruff check/format, Pytest, Web test, Web build).
- In-Plan VPS Sync: Run `bash scripts/deploy_to_vps.sh --fast` after each commit.

## Review Focus
1. **Involuntary DB Document Insertion:** Verify that sending a plain text message in a new session NEVER calls `sessionsApi.addDocumentToSession`.
2. **Empty Session Switching:** Verify that switching to a session with 0 documents clears `useReaderStore.openDocumentIds` and renders the Empty State without retaining documents from the previous session.
3. **Intentional Document Workflows Preserved:** Verify that uploading a PDF or selecting a document from the Library continues to correctly attach and open the document.
4. **New Chat Button Purity:** Verify that clicking "+ Đoạn chat mới" (`handleNewSession`) resets both `useReaderStore` and `useWorkspaceStore`.
5. **No Regressions on Multi-Document Tabs:** Verify that sessions with multiple documents (up to 5) still render tabs and switch active documents properly.

---

### Task 1: Stop Involuntary Document Attachment in `useStreamingChat.ts`

**Files:**
- Create: `apps/web/src/features/dashboard/__tests__/useStreamingChatSessionDocs.test.ts`
- Modify: `apps/web/src/features/dashboard/hooks/useStreamingChat.ts:130-150`

**Interfaces:**
- Consumes: `sessionsApi.createSession`, `sessionsApi.addDocumentToSession`
- Produces: Text-only session creation that does NOT attach stale `openDocumentIds` to the database.

- [ ] **Step 1: Write failing test in `useStreamingChatSessionDocs.test.ts`**

Create `apps/web/src/features/dashboard/__tests__/useStreamingChatSessionDocs.test.ts`:
```ts
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";

vi.mock("@/features/sessions/api/sessionsApi", () => ({
  sessionsApi: {
    createSession: vi.fn(),
    addDocumentToSession: vi.fn(),
    listSessionMessages: vi.fn().mockResolvedValue({ data: [] }),
    deleteSessionMessage: vi.fn(),
  },
}));

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

describe("useStreamingChat Session Document Isolation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useReaderStore.setState({
      openDocumentIds: ["doc-stale-attention"],
      activeDocumentId: "doc-stale-attention",
    });
  });

  it("does NOT automatically attach stale openDocumentIds when creating a session from a plain-text prompt", async () => {
    vi.mocked(sessionsApi.createSession).mockResolvedValue({
      data: { id: "new-session-123", title: "Nghiên cứu: hello" } as any,
    });

    const { result } = renderHook(() =>
      useStreamingChat({
        activeSessionId: undefined,
      })
    );

    await act(async () => {
      result.current.sendMessage("hello");
    });

    expect(sessionsApi.createSession).toHaveBeenCalledWith({
      title: "Nghiên cứu: hello",
    });
    // Stale documents in reader store must NOT be attached to new session!
    expect(sessionsApi.addDocumentToSession).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- useStreamingChatSessionDocs.test.ts`
Expected: FAIL because `sessionsApi.addDocumentToSession` is currently called with `"doc-stale-attention"`.

- [ ] **Step 3: Remove automatic `addDocumentToSession` loop in `useStreamingChat.ts`**

In `apps/web/src/features/dashboard/hooks/useStreamingChat.ts:135-146`:
Remove the loop that reads `useReaderStore.getState().openDocumentIds` and calls `addDocumentToSession`. Plain text chats should create empty sessions with 0 documents.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- useStreamingChatSessionDocs.test.ts`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/dashboard/hooks/useStreamingChat.ts apps/web/src/features/dashboard/__tests__/useStreamingChatSessionDocs.test.ts
git commit -m "fix(dashboard): prevent involuntary document attachment when creating text-only session"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Reset Reader Store on New Session & Bi-directional Session Sync in `DashboardContainer.tsx`

**Files:**
- Create: `apps/web/src/features/dashboard/__tests__/DashboardContainerSessionLifecycle.test.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx:112-160`

**Interfaces:**
- Consumes: `useReaderStore`, `useWorkspaceStore`, `sessionDetailRes?.data`
- Produces: Clean reader state reset on `handleNewSession` and explicit clearing of `openDocumentIds` when a session has 0 documents.

- [ ] **Step 1: Write failing test in `DashboardContainerSessionLifecycle.test.tsx`**

Create `apps/web/src/features/dashboard/__tests__/DashboardContainerSessionLifecycle.test.tsx`:
```tsx
import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardContainer } from "../components/DashboardContainer";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useWorkspaceStore } from "@/stores/useWorkspaceStore";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";

let mockSessionDetailData: any = null;

vi.mock("@/features/sessions/hooks/useSessionsQuery", () => ({
  useSessionDetail: () => ({ data: mockSessionDetailData }),
  useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
  SESSION_QUERY_KEYS: { all: ["sessions"] },
}));

vi.mock("@/features/dashboard/hooks/useDashboardSessions", () => ({
  useDashboardSessions: () => ({
    sessions: [],
    activeSession: undefined,
    selectSession: vi.fn(),
    createSession: vi.fn(),
  }),
}));

vi.mock("@/features/documents/hooks/useDocumentIngestion", () => ({
  useDocumentIngestion: () => ({
    isProcessing: false,
    ingest: vi.fn(),
  }),
  useDocumentsList: () => ({ data: { data: [] }, isLoading: false }),
  useDocumentDetail: () => ({ data: undefined, isLoading: false }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

describe("DashboardContainer Session Document Lifecycle", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useReaderStore.setState({
      openDocumentIds: ["doc-previous"],
      activeDocumentId: "doc-previous",
    });
    useWorkspaceStore.setState({
      activeDocumentId: "doc-previous",
      documentTitle: "Previous Paper",
    });
  });

  it("clears openDocumentIds and activeDocumentId when session has 0 documents", async () => {
    mockSessionDetailData = {
      data: {
        id: "session-empty",
        title: "Nghiên cứu: Empty Session",
        document_ids: [],
        documents: [],
      },
    };

    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard/session-empty"]}>
          <DashboardContainer />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(useReaderStore.getState().openDocumentIds).toEqual([]);
    expect(useReaderStore.getState().activeDocumentId).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DashboardContainerSessionLifecycle.test.tsx`
Expected: FAIL because `openDocumentIds` retains `["doc-previous"]`.

- [ ] **Step 3: Update `DashboardContainer.tsx` session synchronization & `handleNewSession`**

In `apps/web/src/features/dashboard/components/DashboardContainer.tsx`:
1. In `handleNewSession`:
   ```ts
   useReaderStore.getState().resetReader();
   useWorkspaceStore.getState().resetWorkspace();
   ```
2. In `useEffect` for `sessionDetailRes?.data` (lines 112-132):
   ```ts
   const docIds = detail.document_ids || [];
   if (docIds.length > 0) {
     useReaderStore.getState().setOpenDocumentIds(docIds);
     const activeDocId = detail.active_document_id || docIds[0];
     const matchedDoc = detail.documents?.find((d) => d.id === activeDocId);
     const title = matchedDoc?.title || detail.title;
     setDocument(activeDocId, title);
     useReaderStore.getState().setActiveDocumentId(activeDocId);
   } else {
     useReaderStore.getState().setOpenDocumentIds([]);
     useReaderStore.getState().setActiveDocumentId(null);
     useWorkspaceStore.getState().setDocument(null, "");
   }
   ```
3. In `useEffect` for `activeSession` (lines 135-141):
   Add matching `else` branch to clear if `activeSession.document_ids?.length === 0`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- DashboardContainerSessionLifecycle.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/dashboard/components/DashboardContainer.tsx apps/web/src/features/dashboard/__tests__/DashboardContainerSessionLifecycle.test.tsx
git commit -m "fix(dashboard): reset reader store on new session and clear documents on empty session sync"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Eliminate Hardcoded `documentsData.data[0]` Fallback in `DashboardWorkspace.tsx`

**Files:**
- Create: `apps/web/src/features/dashboard/__tests__/DashboardWorkspaceNoGhostFallback.test.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx:370-410`

**Interfaces:**
- Consumes: `openDocumentIds`, `activeDocumentId`
- Produces: Clean Empty State rendering when a session has 0 documents, with zero fallback to `documentsData.data[0]`.

- [ ] **Step 1: Write failing test in `DashboardWorkspaceNoGhostFallback.test.tsx`**

Create `apps/web/src/features/dashboard/__tests__/DashboardWorkspaceNoGhostFallback.test.tsx`:
```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardWorkspace } from "../components/DashboardWorkspace";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useWorkspaceStore } from "@/stores/useWorkspaceStore";

vi.mock("@/features/documents/hooks/useDocumentIngestion", () => ({
  useDocumentsList: () => ({
    data: {
      data: [
        {
          id: "doc-attention-first",
          title: "Attention Is All You Need",
          filename: "attention.pdf",
          status: "completed",
        },
      ],
    },
    isLoading: false,
  }),
  useDocumentDetail: () => ({ data: undefined, isLoading: false }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("@/features/sessions/hooks/useSessionsQuery", () => ({
  useSessionDetail: () => ({
    data: {
      data: {
        id: "session-empty",
        title: "Nghiên cứu: Empty Session",
        document_ids: [],
        documents: [],
      },
    },
    isLoading: false,
  }),
  useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
}));

describe("DashboardWorkspace No Ghost Fallback", () => {
  beforeEach(() => {
    useReaderStore.setState({
      openDocumentIds: [],
      activeDocumentId: null,
    });
    useWorkspaceStore.setState({
      activeDocumentId: null,
      documentTitle: "",
    });
  });

  it("renders Empty State and does NOT display Attention Is All You Need when session has 0 documents", () => {
    render(
      <DashboardWorkspace
        sessionId="session-empty"
        sessionTitle="Nghiên cứu: Empty Session"
      />
    );

    // Empty state should be rendered
    expect(screen.getByText("Chưa có tài liệu nghiên cứu nào")).toBeInTheDocument();
    // Ghost document must NOT be rendered in tabs or viewer!
    expect(screen.queryByText("Attention Is All You Need")).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- DashboardWorkspaceNoGhostFallback.test.tsx`
Expected: FAIL because `DashboardWorkspace.tsx` currently falls back to `documentsData.data[0]` ("Attention Is All You Need").

- [ ] **Step 3: Remove `documentsData.data[0]` fallback logic in `DashboardWorkspace.tsx`**

In `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`:
1. Remove lines 372-380 (`useEffect` auto-selecting `documentsData.data[0]`).
2. Update `effectiveOpenIds` (lines 390-400):
   ```ts
   const effectiveOpenIds = useMemo(() => {
     if (openDocumentIds.length > 0) return openDocumentIds;
     if (activeDocumentId && activeDocumentId !== "doc-default") return [activeDocumentId];
     return [];
   }, [openDocumentIds, activeDocumentId]);
   ```
3. Update `currentDocTitle` (line 382):
   ```ts
   const currentDocTitle =
     documentDetail?.title ||
     workspaceDocTitle ||
     "Tài liệu nghiên cứu";
   ```
4. Update `effectiveDocuments` (line 402):
   Do not inject `documentsData.data` if `effectiveOpenIds.length === 0`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test -- DashboardWorkspaceNoGhostFallback.test.tsx`
Expected: PASS

- [ ] **Step 5: Run web unit tests & build**

Run: `npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: PASS exit code 0

- [ ] **Step 6: Commit and fast VPS sync**

```bash
git add apps/web/src/features/dashboard/components/DashboardWorkspace.tsx apps/web/src/features/dashboard/__tests__/DashboardWorkspaceNoGhostFallback.test.tsx
git commit -m "fix(dashboard): eliminate hardcoded first-document fallback in workspace"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: Comprehensive 4 Gates Verification & Production Deployment

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
Expected: 100% tests pass across all test files.

- [ ] **Step 4: Gate 4 - Frontend Production Build**

Run: `npm --prefix apps/web run build`
Expected: Clean build with 0 TypeScript/Vite errors.

- [ ] **Step 5: In-Plan VPS Sync**

Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0, live system updated at `https://verischolar.duckdns.org`.

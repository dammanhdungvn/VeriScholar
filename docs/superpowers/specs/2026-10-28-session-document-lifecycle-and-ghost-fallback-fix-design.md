# Design Spec: Session-Document Lifecycle Isolation & Ghost Fallback Elimination

## 1. Context & Problem Statement
In the scholarly research assistant workflow, users reported an intrusive bug where the paper *"Attention Is All You Need"* appeared to be "hardcoded" or involuntarily attached to sessions:
1. **Ghost Attachment on Plain-Text Chat:** In Standby Hero mode, when a user enters a query (e.g. `"hello"`) without uploading a file, the system creates a new session titled `"Nghiên cứu: hello"` and unexpectedly loads and attaches the paper *"Attention Is All You Need"*.
2. **Ghost Document Retention on Session Switching:** When switching to an existing session where all documents were previously deleted (an empty paper session), the reader pane continues to display *"Attention Is All You Need"*, making it impossible to have a clean empty session.
3. **Hardcoded First Document Fallback:** Whenever a session has no active documents, frontend code in `DashboardWorkspace.tsx` and `DashboardContainer.tsx` aggressively falls back to `documentsData.data[0]` (the first paper ever uploaded to the user's database: *"Attention Is All You Need"*), rather than rendering the intended empty state.

## 2. Root Cause Analysis
1. **State Leak on New Session (`DashboardContainer.tsx:148`):**
   `handleNewSession()` resets chat messages and workspace state, but fails to call `useReaderStore.getState().resetReader()` or clear `openDocumentIds` and `activeDocumentId`. The previous session's document IDs remain resident in client memory.
2. **Involuntary Document Attachment (`useStreamingChat.ts:135`):**
   Upon creating a new session from a text prompt, `useStreamingChat` iterates over `useReaderStore.getState().openDocumentIds` and issues `sessionsApi.addDocumentToSession(effectiveSessionId, { document_id: docId })`. Since `openDocumentIds` still contained the stale document from memory, it attached it to the backend database session without user intent.
3. **Missing Empty-State Branch on Session Sync (`DashboardContainer.tsx:112-141`):**
   When `sessionDetailRes` loads, it executes `if (docIds.length > 0) { setOpenDocumentIds(docIds); ... }`. If `docIds.length === 0`, it does nothing, leaving the prior session's documents open.
4. **Aggressive `documentsData.data[0]` Fallback (`DashboardWorkspace.tsx:372, 394`):**
   `effectiveOpenIds` falls back to `[documentsData.data[0].id]` if `openDocumentIds` is empty. Line 372 auto-selects `documentsData.data[0]` if `!activeSessionId`. This completely suppresses the empty state when a session genuinely has no documents.

## 3. Goals, Non-Goals & Anti-Goals

### Goals
- Ensure a brand-new session created from a plain-text query (without documents) starts with 0 documents and does NOT auto-attach any prior documents.
- Ensure switching to a session with 0 documents properly clears `useReaderStore` (`openDocumentIds = []`, `activeDocumentId = null`), displaying the clean Empty State with "+ Tải lên tài liệu PDF".
- Eliminate all silent fallbacks to `documentsData.data[0]`.
- Reset `useReaderStore` completely when clicking "+ Đoạn chat mới" (`handleNewSession`).

### Non-Goals
- Altering the multi-paper tab bar capability (up to 5 documents can still be open if they belong to the session).
- Modifying backend session endpoints or DB schemas.

### Anti-Goals
- Breaking the workflow where a user *intentionally* sends a chat with files attached (`onSendChatWithFiles`).
- Causing blank flickers during session navigation.

## 4. Approaches Considered & Trade-offs

### Approach 1: Quick Cosmetic Patch (UI Fallback Suppression Only)
- Simply remove `documentsData.data[0]` from `effectiveOpenIds`.
- *Trade-off:* Fails to prevent `useStreamingChat` from auto-attaching stale documents on the backend API. The bug would persist in the database.

### Approach 2: Comprehensive Session-Document Lifecycle Standardization (Selected)
- **Client Reset on New Session:** `handleNewSession` calls `useReaderStore.getState().resetReader()`.
- **Zero-Involuntary-Attachment in Streaming Chat:** `useStreamingChat` only attaches documents if they were explicitly provided in the current creation context, NOT from lingering reader state.
- **Bi-directional Session Sync:** When loading any session, if `docIds.length === 0`, explicitly set `openDocumentIds: []` and `activeDocumentId: null`. If `docIds.length > 0`, set those exact IDs.
- **Eliminate Implicit Fallbacks:** Remove all instances of auto-selecting `documentsData.data[0]` in `DashboardWorkspace.tsx` and `DashboardContainer.tsx`.
- *Trade-off:* Clean, robust, eliminates all ghost document bugs permanently across both frontend and backend.

## 5. Detailed Implementation Specification

### 5.1 `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
1. In `handleNewSession`:
   ```ts
   useReaderStore.getState().resetReader();
   useWorkspaceStore.getState().resetWorkspace();
   ```
2. In `useEffect` for `sessionDetailRes?.data`:
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
     // Session has 0 documents -> explicitly clear reader store
     useReaderStore.getState().setOpenDocumentIds([]);
     useReaderStore.getState().setActiveDocumentId(null);
     useWorkspaceStore.getState().setDocument(null, "");
   }
   ```
3. In `useEffect` for `activeSession`:
   Add matching `else` branch when `activeSession.document_ids.length === 0`.

### 5.2 `apps/web/src/features/dashboard/hooks/useStreamingChat.ts`
1. When auto-creating a session for a plain-text prompt (lines 135-145):
   Do NOT blindly loop over `useReaderStore.getState().openDocumentIds`.
   Only attach documents if the session was explicitly initialized with target documents (e.g., via `initialDocumentIds` or when active document is explicitly bound to the chat context). If creating a text-only chat from standby, do not attach any documents.

### 5.3 `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
1. Remove lines 372-380 (`// Auto-select latest/first real document...`).
2. In `effectiveOpenIds` (lines 390-400):
   ```ts
   const effectiveOpenIds = useMemo(() => {
     if (openDocumentIds.length > 0) return openDocumentIds;
     if (activeDocumentId && activeDocumentId !== "doc-default") return [activeDocumentId];
     return [];
   }, [openDocumentIds, activeDocumentId]);
   ```
   Remove `documentsData?.data?.[0]?.id` fallback completely.
3. In `currentDocTitle`:
   Remove fallback to `documentsData?.data?.[0]?.title`. Fall back to `"Tài liệu nghiên cứu"`.

## 6. Testing Strategy
1. **Unit Test: New Session Reset:**
   - In `DashboardContainer.test.tsx`, verify that calling `handleNewSession()` resets `openDocumentIds` to `[]` and `activeDocumentId` to `null`.
2. **Unit Test: Empty Session Switching:**
   - In `DashboardContainer.test.tsx`, mock a session with `document_ids: []`. Verify that `useReaderStore.getState().openDocumentIds` is cleared to `[]`.
3. **Unit Test: Text Chat Without Files:**
   - In `useStreamingChat.test.ts`, verify that creating a session via plain text prompt does not call `addDocumentToSession`.
4. **Verification Gates:**
   - Gate 1: `uv run ruff check . && uv run ruff format --check .`
   - Gate 2: `uv run pytest`
   - Gate 3: `npm --prefix apps/web run test`
   - Gate 4: `npm --prefix apps/web run build`
   - Fast VPS deployment: `bash scripts/deploy_to_vps.sh --fast`

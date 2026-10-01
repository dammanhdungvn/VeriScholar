# Zero DB Junk & Standby Flow Specification

## Problem Statement
Traditional chat systems create an empty database session row as soon as a user clicks "New Chat" or navigates to `/dashboard`. This causes database bloat ("DB Junk") with thousands of empty, abandoned sessions.

## The VeriScholar Standby Solution
1. **Client-Side Standby Mode (`useWorkspaceStore.isStandby = true`)**:
   - When the user visits `/dashboard` without a session ID in the route, the UI enters Standby Mode.
   - Shows the Hero Dropzone or Deep Reader in standby.
   - NO network call `POST /api/v1/sessions` is made.
2. **Lazy Session Creation**:
   - **Trigger A (Document Upload)**:
     1. User drops PDF into dropzone.
     2. Upload PDF to Content Addressable Storage (`POST /api/v1/documents`).
     3. Create valid session linked to the document (`POST /api/v1/sessions`).
     4. Trigger parsing & chunking (`POST /api/v1/documents/{id}:parse`).
     5. Navigate to `/dashboard/:sessionId`.
   - **Trigger B (Direct Chat Input)**:
     1. User types question into the input bar and hits Enter.
     2. `useStreamingChat` detects `!activeSessionId`.
     3. Calls `sessionsApi.createSession({ title: "Nghiên cứu: ..." })`.
     4. Attaches any currently open document in reader store.
     5. Replaces URL with `/dashboard/:newSessionId`.
     6. Connects to SSE streaming endpoint `POST /api/v1/sessions/:id/messages`.
3. **Resetting to Standby**:
   - Clicking "Đoạn chat mới" (`handleNewSession`):
     - Clears client-side message state.
     - Sets `activeSessionId = undefined`.
     - Resets workspace store.
     - Navigates to `/dashboard`.
     - Strictly does NOT hit the backend.

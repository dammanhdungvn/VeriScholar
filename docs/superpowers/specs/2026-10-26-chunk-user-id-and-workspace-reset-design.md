# Design Specification: Fix Ingestion 94% Freeze & New Session Workspace Reset

- **Date:** 2026-10-26
- **Status:** Approved
- **Modules Affected:**
  - `apps/api/src/api/services/document_service.py`
  - `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
  - `apps/web/src/features/dashboard/components/HeroUploadDropzone.tsx`
  - `apps/web/src/features/dashboard/hooks/useDocumentIngestion.ts`
  - `scripts/verify_gates.sh`
  - `scripts/deploy_to_vps.sh`

---

## 1. Problem Statement

1. **Ingestion Freezing at 94%:**
   - When users upload a PDF, `POST /api/v1/documents` and `POST /api/v1/documents/{id}:parse` initiate parsing.
   - When `GET /api/v1/documents/{id}/status` polls for progress, `document_service.py` extracts layout chunks and attempts to insert `DocumentChunkModel` records into PostgreSQL.
   - **Bug:** `DocumentChunkModel` requires `user_id NOT NULL`. The service was instantiating chunks without passing `user_id=doc.user_id`. PostgreSQL threw an `IntegrityError (NotNullViolationError)`.
   - **Bug:** The service silently swallowed the exception (`except Exception: pass`), leaving `doc.status = "processing"` and `doc.progress = 0` forever.
   - **Frontend Symptom:** The smooth perceptual progress controller in `useDocumentIngestion.ts` asymptotically crawls to `Math.min(94, ...)`, freezing at 94% indefinitely waiting for `completed`.
2. **Unable to Exit via "Đoạn chat mới":**
   - Clicking `+ Đoạn chat mới` calls `handleNewSession()`, which reset messages and session ID but **never called `resetWorkspace()`** in `useWorkspaceStore`.
   - `documentStatus` remained `"parsing"`, keeping `isProcessing = true`, trapping the UI on the 94% progress overlay.

---

## 2. Solutions & Architecture

### 2.1 Backend Fixes (`document_service.py`)
- Pass `user_id=doc.user_id` to every `DocumentChunkModel(...)` instantiation across all methods:
  - `get_document_status`
  - `get_document_structure`
  - `get_document_chunks`
  - `get_document_chunk_by_id`
  - `parse_document`
- Remove silent exception swallowing: log any errors with `logger.exception(...)` and update `doc.error_message` and `doc.status = DocumentStatus.FAILED.value` if chunk persistence truly fails.
- Ensure `doc.status = DocumentStatus.COMPLETED.value`, `doc.stage = DocumentStage.COMPLETED.value`, `doc.progress = 100` are saved and returned.

### 2.2 Frontend Fixes
- In `DashboardContainer.tsx`:
  - In `handleNewSession`: call `resetWorkspace()` from `useWorkspaceStore`.
  - When returning to standby chat, all upload/ingestion state is completely cleared, instantly returning the UI to the Standby Hero Workspace.
- In `HeroUploadDropzone.tsx`:
  - Add a subtle "Hủy bỏ" (Cancel) button during ingestion so users can cancel at any time.
- In `useDocumentIngestion.ts`:
  - When cancelled or when polling exceeds `maxPollAttempts`, cleanly abort and reset.

### 2.3 Script Improvements
- Create `scripts/verify_gates.sh`: runs Gate 1 (Ruff), Gate 2 (Pytest), Gate 3 (Vitest), Gate 4 (Vite Build) purely locally in $< 10$ seconds.
- Update `scripts/deploy_to_vps.sh`: add quick SSH connectivity check (timeout 2s); if VPS is offline, exit cleanly with informative notice without hanging.

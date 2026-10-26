# Chunk user_id Fix & Workspace Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix ingestion freezing at 94% by passing `user_id` when persisting `DocumentChunkModel`, remove silent exception swallowing, allow instant exit from processing state when clicking "Đoạn chat mới", and add `scripts/verify_gates.sh`.

**Architecture:** Backend database integrity in `document_service.py` adhering to multi-tenant user isolation. Frontend state reset in `DashboardContainer.tsx` and `useWorkspaceStore`.

**Spec:** [`docs/superpowers/specs/2026-10-26-chunk-user-id-and-workspace-reset-design.md`](../specs/2026-10-26-chunk-user-id-and-workspace-reset-design.md)

---

### Task 1: Backend Fix `user_id` in `DocumentChunkModel` & Error Logging

**Files:**
- Modify: `apps/api/src/api/services/document_service.py`
- Test: `apps/api/tests/test_document_ingestion_and_cas.py`

- [ ] **Step 1: Write failing test in `test_document_ingestion_and_cas.py`**
  Add a test verifying that `get_document_status` parses chunks with non-null `user_id` and successfully transitions `doc.status` to `completed` and `doc.progress` to `100`.
- [ ] **Step 2: Fix `DocumentChunkModel` instantiations in `document_service.py`**
  Add `user_id=doc.user_id` in all chunk model instantiations (lines ~1025, 1844, 2000, 2300, 2476).
  Replace `except Exception: pass` with proper logging.
- [ ] **Step 3: Run pytest and verify all pass**
  ```bash
  uv run pytest apps/api/tests/test_document_ingestion_and_cas.py
  ```
- [ ] **Step 4: Commit Task 1**
  ```bash
  git add apps/api/
  git commit -m "fix(api): populate required user_id on DocumentChunkModel to prevent ingestion hang"
  ```

---

### Task 2: Frontend Fix "Đoạn chat mới" Reset & Dropzone Cancel Button

**Files:**
- Modify: `apps/web/src/features/dashboard/components/DashboardContainer.tsx`
- Modify: `apps/web/src/features/dashboard/components/HeroUploadDropzone.tsx`
- Modify: `apps/web/src/features/dashboard/hooks/useDocumentIngestion.ts`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardContainer.test.tsx`

- [ ] **Step 1: Update `handleNewSession` in `DashboardContainer.tsx`**
  Import `useWorkspaceStore` and call `resetWorkspace()` inside `handleNewSession()`.
- [ ] **Step 2: Add cancel button in `HeroUploadDropzone.tsx`**
  When `isProcessing` is true, render a subtle "Hủy bỏ" button that calls `resetWorkspace()`.
- [ ] **Step 3: Run Vitest and verify all pass**
  ```bash
  npm --prefix apps/web run test
  ```
- [ ] **Step 4: Commit Task 2**
  ```bash
  git add apps/web/
  git commit -m "fix(web): reset workspace store on new session and add dropzone cancel button"
  ```

---

### Task 3: Local Dev Verification Script & Offline VPS Protection

**Files:**
- Create: `scripts/verify_gates.sh`
- Modify: `scripts/deploy_to_vps.sh`

- [ ] **Step 1: Create `scripts/verify_gates.sh`**
  Run Gate 1 (Ruff), Gate 2 (Pytest), Gate 3 (Vitest), Gate 4 (Vite Build) with clear colored banners and exit 0.
- [ ] **Step 2: Update `scripts/deploy_to_vps.sh` with SSH ping check**
  Check `ssh -i $SSH_KEY -o ConnectTimeout=2 -o BatchMode=yes $SSH_USER@$SSH_HOST "echo ok"`. If failing, print `"VPS host is offline. Skipping remote sync."` and exit 0.
- [ ] **Step 3: Make executable and verify locally**
  ```bash
  chmod +x scripts/verify_gates.sh
  ./scripts/verify_gates.sh
  ```
- [ ] **Step 4: Commit Task 3**
  ```bash
  git add scripts/
  git commit -m "feat(scripts): add local verify_gates script and offline VPS pre-flight check"
  ```

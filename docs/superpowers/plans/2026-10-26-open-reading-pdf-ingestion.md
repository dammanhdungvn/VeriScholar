# Open-Reading PDF Ingestion & Abstract-Only Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 404 error when opening scholarly papers via "Mở Đọc Sâu" by downloading Open Access PDFs into CAS storage during `open-reading`, falling back gracefully to `abstract_only`, and providing a dedicated `AbstractOnlyViewer` component in the frontend.

**Architecture:** Hexagonal architecture adhering to core domain isolation. In `apps/api`, `DocumentService` handles external PDF ingestion using `httpx` and stores blobs in `IStoragePort`. In `apps/web`, `DashboardWorkspace` inspects `access_status` and routes between `PdfCanvasViewer` and a minimal `AbstractOnlyViewer` with an attach-PDF upload zone.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 Async, httpx, React 19, Tailwind CSS, PDF.js, Vite, Vitest, Pytest.

**Spec:** [`docs/superpowers/specs/2026-10-26-open-reading-pdf-ingestion-design.md`](../specs/2026-10-26-open-reading-pdf-ingestion-design.md)

---

## Global Constraints

- Monorepo directory structure: `apps/api` (FastAPI), `apps/web` (React 19), `packages/core` (pure domain).
- Hexagonal Isolation: `packages/core` must not import web frameworks or database ORMs.
- Strict TDD: Write red tests first, make green, then refactor.
- Radical Minimalism (Rule 6): No tech jargon (e.g. CAS, SHA-256, HTTP 404, UUID) in user-facing copy.
- Relative Markdown links only in documentation.
- All 4 verification gates must pass with exit code 0 before completion.

## Review Focus

1. **Slow or broken external PDF URL:** If arXiv or Unpaywall returns 404 or times out (>10s), the system must not fail the request; it must fall back to `abstract_only`.
2. **File size safety:** If the downloaded file exceeds 50MB, abort download immediately and fall back to `abstract_only`.
3. **Magic byte validation:** If the downloaded payload is HTML (e.g., Cloudflare challenge or captcha) instead of `%PDF-`, reject and fall back to `abstract_only`.
4. **Abstract-only documents:** Frontend must never invoke `GET /documents/{id}/file` for an `abstract_only` document.
5. **Existing session continuity:** Updating `DocumentModel` during ingestion preserves session link and viewport state.

---

### Task 1: Backend PDF Ingestion from URL with Graceful Abstract Fallback

**Files:**
- Modify: `apps/api/src/api/services/document_service.py`
- Modify: `apps/api/src/api/v1/endpoints/discovery.py`
- Test: `apps/api/tests/test_open_reading_pdf_ingestion.py`

- [ ] **Step 1: Write failing unit/integration tests for PDF ingestion during `open-reading`**
  Create `apps/api/tests/test_open_reading_pdf_ingestion.py`:
  - Test 1: `test_open_reading_downloads_pdf_and_serves_file`: Mock `httpx.AsyncClient.get` returning valid PDF bytes (`b"%PDF-1.4 sample content"`). Verify that `open-reading` saves the real CAS blob, and subsequent `GET /api/v1/documents/{document_id}/file` returns 200 with matching bytes.
  - Test 2: `test_open_reading_handles_download_failure_gracefully`: Mock `httpx.AsyncClient.get` raising `httpx.TimeoutException` or returning 404. Verify `open-reading` returns 201 with `access_status="abstract_only"`, `status="abstract_only"`.
  - Test 3: `test_open_reading_rejects_html_magic_bytes`: Mock `httpx.AsyncClient.get` returning `b"<!DOCTYPE html><html>..."`. Verify fallback to `abstract_only`.

- [ ] **Step 2: Run pytest to verify tests fail (Red)**
  ```bash
  uv run pytest apps/api/tests/test_open_reading_pdf_ingestion.py
  ```

- [ ] **Step 3: Implement `ingest_pdf_from_url` in `DocumentService`**
  In `apps/api/src/api/services/document_service.py`:
  - Add method `async def ingest_pdf_from_url(self, pdf_url: str) -> tuple[str, int] | None`:
    - Perform streaming GET using `httpx.AsyncClient(timeout=10.0, follow_redirects=True)`.
    - Validate status code 200 and initial chunk starts with `%PDF-`.
    - Enforce size ceiling of `50MB` (`MAX_FILE_SIZE_BYTES`).
    - Stream chunks into `self.storage.save_blob` and register CAS blob record.
    - Return `(content_hash, file_size_bytes)` on success, or `None` on any network/validation error.

- [ ] **Step 4: Update `open_reading_session` in `apps/api/src/api/v1/endpoints/discovery.py`**
  - Inject `service: DocumentService = Depends(get_document_service)`.
  - If `payload.pdf_url`:
    - Call `await service.ingest_pdf_from_url(payload.pdf_url)`.
    - If result is `(real_hash, real_size)`:
      - Set `content_hash = real_hash`, `file_size_bytes = real_size`, `status = "parsing"`, `access_status = "open_access_pdf"`.
    - If result is `None`:
      - Set `content_hash = initial_hash`, `file_size_bytes = 0`, `status = "abstract_only"`, `access_status = "abstract_only"`.
  - If `payload.pdf_url` is absent:
    - Set `content_hash = initial_hash`, `file_size_bytes = 0`, `status = "abstract_only"`, `access_status = "abstract_only"`.

- [ ] **Step 5: Run pytest to verify tests pass (Green)**
  ```bash
  uv run pytest apps/api/tests/test_open_reading_pdf_ingestion.py
  uv run pytest apps/api/tests/test_discovery_search_endpoints.py
  ```

- [ ] **Step 6: Commit backend changes**
  ```bash
  git add apps/api/
  git commit -m "feat(api): ingest external open access PDFs into CAS in open-reading endpoint"
  ```

---

### Task 2: Frontend Abstract-Only Reader View & Access Status Routing

**Files:**
- Create: `apps/web/src/features/reader/components/AbstractOnlyViewer.tsx`
- Modify: `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`
- Test: `apps/web/src/features/reader/__tests__/AbstractOnlyViewer.test.tsx`
- Test: `apps/web/src/features/dashboard/__tests__/DashboardWorkspace.test.tsx`

- [ ] **Step 1: Write unit tests for `AbstractOnlyViewer`**
  Create `apps/web/src/features/reader/__tests__/AbstractOnlyViewer.test.tsx`:
  - Test rendering paper title, authors, publication year, abstract text, DOI link.
  - Test drag-and-drop / file input calling the PDF attachment handler.

- [ ] **Step 2: Run frontend tests to verify failure (Red)**
  ```bash
  npm --prefix apps/web run test apps/web/src/features/reader/__tests__/AbstractOnlyViewer.test.tsx
  ```

- [ ] **Step 3: Implement `AbstractOnlyViewer.tsx`**
  In `apps/web/src/features/reader/components/AbstractOnlyViewer.tsx`:
  - Present academic summary header with clean serif title.
  - Author and venue badges.
  - Abstract text block with comfortable reading typography (`font-serif` or `leading-relaxed`).
  - Direct DOI and arXiv external links.
  - Minimalistic attachment dropzone: "Đính kèm tệp PDF đầy đủ" with upload button triggering `documentsApi.attachPdf`.

- [ ] **Step 4: Integrate `AbstractOnlyViewer` in `DashboardWorkspace.tsx`**
  - In `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`:
    - Read `documentDetail?.access_status`.
    - If `documentDetail?.access_status === "abstract_only"`:
      - Render `<AbstractOnlyViewer document={documentDetail} onPdfAttached={...} />`.
      - Do NOT mount `PdfCanvasViewer` (prevents 404 fetch).
    - Else:
      - Render `PdfCanvasViewer`.

- [ ] **Step 5: Run frontend tests to verify all pass (Green)**
  ```bash
  npm --prefix apps/web run test
  ```

- [ ] **Step 6: Commit frontend changes**
  ```bash
  git add apps/web/
  git commit -m "feat(web): add AbstractOnlyViewer and conditional reader routing"
  ```

---

### Task 3: Full 4 Verification Gates & Production Deployment to VPS

**Files:**
- Verification only

- [ ] **Step 1: Run Gate 1 (Python Linter & Formatter)**
  ```bash
  uv run ruff check . && uv run ruff format --check .
  ```

- [ ] **Step 2: Run Gate 2 (All Backend Tests)**
  ```bash
  uv run pytest
  ```

- [ ] **Step 3: Run Gate 3 (Frontend Tests)**
  ```bash
  npm --prefix apps/web run test
  ```

- [ ] **Step 4: Run Gate 4 (Frontend Production Build)**
  ```bash
  npm --prefix apps/web run build
  ```

- [ ] **Step 5: Deploy to Remote VPS & Verify Live**
  - Run `./scripts/deploy_to_vps.sh`
  - Ingest the survey paper via live API or SSH verification to ensure zero 404.

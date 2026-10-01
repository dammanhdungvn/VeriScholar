# VeriScholar Architectural Invariants & Laws

This document provides deep reference for the non-negotiable architectural laws of the VeriScholar platform.

## 1. The Dependency Rule (Ports & Adapters)
- Business logic in `packages/core` is strictly isolated from infrastructure and presentation layers.
- `packages/core` contains:
  - Entities (`DocumentChunk`, `BoundingBox`, `Citation`, `User`)
  - Value Objects (`BoundingBox`, `PdfAnnotation`)
  - Ports (Interfaces/Protocols: `IChunkExtractorPort`, `IPdfAnnotatorPort`, `IStoragePort`)
- `apps/api` implements or injects adapters:
  - `PyMuPDFChunkExtractor`, `PyMuPdfAnnotator`, `LocalStorageAdapter`
  - FastAPI routers, route handlers, DB models, and migrations
- Invariant: `packages/core` must **NEVER** import from `apps/api`, `apps/web`, or any web/HTTP frameworks.

## 2. Coordinate System Norms
When dealing with PDF extraction, rendering, and visual overlays on canvas:
- **Origin**: (0.0, 0.0) is the **Top-Left** of the page.
- **Normalization**: All coordinates `x0, y0, x1, y1` are normalized floats between `0.0` and `1.0`:
  $$x_{\text{norm}} = \frac{x_{\text{pixel}}}{W_{\text{page}}}, \quad y_{\text{norm}} = \frac{y_{\text{pixel}}}{H_{\text{page}}}$$
- **Constraint**: `0.0 <= x0 < x1 <= 1.0` and `0.0 <= y0 < y1 <= 1.0`.
- **Page Indexing**: `page` is strictly a **1-indexed integer** (`page >= 1`).
- When converting from PyMuPDF `fitz.Rect(x0, y0, x1, y1)`:
  ```python
  page_width = page.rect.width
  page_height = page.rect.height
  norm_x0 = rect.x0 / page_width
  norm_y0 = rect.y0 / page_height
  norm_x1 = rect.x1 / page_width
  norm_y1 = rect.y1 / page_height
  norm_page = page.number + 1  # 0-indexed to 1-indexed
  ```

## 3. Grounded Citation & Socratic Stream
- Citations in LLM responses must reference verifiable chunks using `[^cit_N]` syntax.
- Each citation payload must contain:
  - `citation_id`: e.g. `"cit_1"`
  - `document_id`: UUID
  - `document_title`: string
  - `page_number`: 1-indexed int
  - `bounding_box`: `[x0, y0, x1, y1, page]`
- Front-end renders clickable citation badges that immediately jump the PDF reader to the target page and highlight the exact bounding box.

## 4. In-Memory Test Isolation
- All unit tests in `packages/core/tests` and standard unit suites in `apps/api/tests` must run 100% in-memory with zero external dependencies (no live DB, no network calls to OpenAI).
- Use `InMemory*Store` fakes.
- Check `"InMemory" in type(self.db).__name__ or settings.ENVIRONMENT == "test"` before initiating external network requests in services.

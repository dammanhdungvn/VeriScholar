# Academic URL Guardrails & Horizontal Snap Carousel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide secure, instant scholarly URL search (arXiv/DOI whitelisting) with instant guardrail feedback, and transform search results into a horizontal snap carousel that completely eliminates duplicate vertical scrollbars.

**Architecture:** Frontend client-side URL guardrails in `urlGuardrail.ts`, backend direct ID search optimization in `scholarly_search_adapter.py`, and horizontal snap card rail in `UnifiedHeroWorkspace.tsx`.

**Tech Stack:** React 19, Tailwind CSS, Lucide icons, Vitest, FastAPI, Pytest.

**Spec:** [`docs/superpowers/specs/2026-10-26-url-guardrail-and-carousel-ui-design.md`](../specs/2026-10-26-url-guardrail-and-carousel-ui-design.md)

---

## Global Constraints

- Monorepo Hexagonal Isolation: `packages/core` remains pure.
- Radical Minimalism (Rule 6): Clean, polite user-facing error notices without technical jargon or aggressive red banners.
- Strict TDD: Unit tests for URL guardrail, backend direct ID search, and carousel interactions.
- Relative Markdown links only in documentation.
- All 4 verification gates must pass with exit code 0.

## Review Focus

1. **Untrusted URLs:** Inputting `https://pornhub.com`, `http://malware.xyz`, or `bit.ly` must be rejected immediately at the client with a clear notice, never hitting the backend search API.
2. **Valid arXiv & DOI URLs:** Inputting `https://arxiv.org/abs/2404.10981`, `http://arxiv.org/pdf/2404.10981v2.pdf`, or `https://doi.org/10.1145/3805774` extracts the identifier and resolves the exact paper.
3. **Empty Results Feedback:** When 0 papers are returned, the UI shows a clear message and a "Làm mới tìm kiếm" button instead of silent emptiness.
4. **Zero Vertical Scrollbars:** No duplicate vertical scrollbars appear on screen; cards scroll horizontally with `scrollbar-none`.
5. **Keyboard & Arrow Navigation:** Left/Right arrows allow smooth paging through cards for non-touch mouse users.

---

### Task 1: Academic URL Guardrails & Identifier Extraction (Frontend & Backend)

**Files:**
- Create: `apps/web/src/features/discovery/lib/urlGuardrail.ts`
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Modify: `apps/api/src/api/adapters/scholarly_search_adapter.py`
- Test: `apps/web/src/features/discovery/__tests__/urlGuardrail.test.tsx`
- Test: `apps/api/tests/test_discovery_search_endpoints.py`

- [ ] **Step 1: Write unit tests for `urlGuardrail.ts`**
  Create `apps/web/src/features/discovery/__tests__/urlGuardrail.test.tsx`:
  - Test valid arXiv URL (`https://arxiv.org/abs/2305.18290`) returns `{ type: "scholarly_url", idType: "arxiv", identifier: "2305.18290" }`.
  - Test valid DOI URL (`https://doi.org/10.1145/3805774`) returns `{ type: "scholarly_url", idType: "doi", identifier: "10.1145/3805774" }`.
  - Test untrusted URL (`https://pornhub.com/video`, `https://example.com/test`) returns `{ type: "invalid_url", message: "..." }`.
  - Test normal keyword (`Retrieval-Augmented Generation`) returns `{ type: "keyword", query: "Retrieval-Augmented Generation" }`.

- [ ] **Step 2: Implement `urlGuardrail.ts`**
  In `apps/web/src/features/discovery/lib/urlGuardrail.ts`:
  - Whitelist: `arxiv.org`, `doi.org`, `semanticscholar.org`, `acm.org`, `ieee.org`, `nature.com`, `science.org`, `biorxiv.org`, `medrxiv.org`.
  - Regex parser for arXiv IDs and DOIs.
  - Export `parseScholarlyInput`.

- [ ] **Step 3: Update `scholarly_search_adapter.py` for direct ID search**
  - If query is an arXiv ID (e.g. `2404.10981` or `2404.10981v2`):
    - Use arXiv API param `id_list={arxiv_id}` for precision instant lookup.
  - If query is a DOI:
    - Search specifically by DOI.

- [ ] **Step 4: Integrate URL Guardrail in `UnifiedHeroWorkspace.tsx`**
  - When user presses Enter or Send:
    - Call `parseScholarlyInput(text)`.
    - If `invalid_url`: set `searchError` with the polite notice without calling backend.
    - If `scholarly_url`: search using the extracted identifier.
    - If `keyword`: search normally.
  - If search returns 0 results: display clear empty state message: *"Không tìm thấy bài báo phù hợp với yêu cầu này"* with button *"Làm mới"*.

- [ ] **Step 5: Run tests and verify**
  ```bash
  npm --prefix apps/web run test
  uv run pytest apps/api/tests/test_discovery_search_endpoints.py
  ```

- [ ] **Step 6: Commit Task 1**
  ```bash
  git add apps/web/ apps/api/
  git commit -m "feat(discovery): add academic URL guardrail and direct identifier search"
  ```

---

### Task 2: Horizontal Snap Carousel & Elimination of Double Scrollbars

**Files:**
- Modify: `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
- Modify: `apps/web/src/features/discovery/components/ScholarlyResultCard.tsx`
- Modify: `apps/web/src/index.css`
- Test: `apps/web/src/features/dashboard/__tests__/UnifiedHeroWorkspace.test.tsx`

- [ ] **Step 1: Write/update tests for `UnifiedHeroWorkspace` carousel**
  - Verify horizontal snap container is rendered with `overflow-x-auto scrollbar-none`.
  - Verify navigation buttons (Left/Right chevrons) are available.

- [ ] **Step 2: Implement Horizontal Snap Carousel in `UnifiedHeroWorkspace.tsx`**
  - Replace the vertical `grid grid-cols-1 gap-3 max-h-[58vh] overflow-y-auto` container with:
    - Horizontal scroll container: `flex gap-4 overflow-x-auto scrollbar-none snap-x snap-mandatory py-2 px-1 relative`.
    - Floating left and right arrow buttons with smooth scrolling (`scrollBy({ left: +/- 360, behavior: "smooth" })`).
    - Remove outer `overflow-y-auto` from the main hero container when displaying search results to prevent any outer page vertical scrollbar from showing.
  - Ensure cards have fixed width (`w-[340px] sm:w-[380px] shrink-0 snap-start`) and balanced height.

- [ ] **Step 3: Run Vitest and verify all pass**
  ```bash
  npm --prefix apps/web run test
  ```

- [ ] **Step 4: Commit Task 2**
  ```bash
  git add apps/web/
  git commit -m "feat(ui): implement horizontal snap carousel and remove double scrollbars"
  ```

---

### Task 3: 4 Verification Gates, Remote Deployment to VPS & End-to-End Validation

**Files:**
- Verification & Deployment

- [ ] **Step 1: Run Gate 1 (Ruff Linter & Formatter)**
- [ ] **Step 2: Run Gate 2 (Backend Pytest Suite)**
- [ ] **Step 3: Run Gate 3 (Frontend Vitest Suite)**
- [ ] **Step 4: Run Gate 4 (Frontend Production Build)**
- [ ] **Step 5: Deploy to VPS (`./scripts/deploy_to_vps.sh`)**
- [ ] **Step 6: Live validation of URL search & horizontal carousel on `https://verischolar.duckdns.org`**

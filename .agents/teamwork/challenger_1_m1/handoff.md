# Handoff Report: Milestone 1 Empirical Challenge (M1_WRITING_AND_SYNTHESIS)

**Agent**: `challenger_1_m1`  
**Role**: `critic`, `specialist` (EMPIRICAL CHALLENGER)  
**Target Milestone**: `M1_WRITING_AND_SYNTHESIS` (Pillars 2, 3, 4)  
**Working Directory**: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_1_m1`  
**Date**: 2026-10-16  
**Verdict**: **REJECT**

---

## 1. Observation

Direct code inspections and empirical test executions were conducted against the Milestone 1 implementations across `apps/api` and `apps/web`:

### 1.1. Empirical Stress Suite Implementation
Created dedicated empirical stress harness in `apps/api/tests/test_m1_pillars_empirical_stress.py` containing 10 rigorous test cases covering all edge cases requested by the dispatch:
- **Overleaf Export Endpoint (`POST /api/v1/drafts/{id}:export-overleaf` & `GET /api/v1/drafts/{id}/overleaf-launch`)**:
  - `test_overleaf_special_characters_in_title_and_vietnamese`: Tests UTF-8 Vietnamese diacritics (`'Nghiên cứu "Học Máy & Trí Tuệ Nhân Tạo": Đánh giá 100% SOTA? {Draft} $\\alpha + \\beta$'`), double quotes, ampersands, braces, and math symbols.
  - `test_overleaf_empty_content_graceful_handling`: Tests `content=""` and `content=None`.
  - `test_overleaf_custom_latex_code_preservation`: Tests custom LaTeX document preserving `\documentclass[12pt,a4paper]{report}`, packages, and document body verbatim without redundant wrapping.
  - `test_overleaf_export_errors_and_isolation`: Tests 401 unauthenticated, 404 non-existent draft ID, and cross-user tenant isolation.
- **Proactive Associative Suggestions Endpoint (`POST /api/v1/drafts/{id}/associative-suggestions`)**:
  - `test_associative_suggestions_high_similarity_match`: Dense domain overlap matching multi-head attention and transformer concepts against research notes.
  - `test_associative_suggestions_zero_similarity_disjoint_vocabulary`: Completely disjoint vocabulary and high `min_similarity=0.99` threshold.
  - `test_associative_suggestions_empty_draft_text_and_db_fallback`: Empty request payload with empty DB draft, and empty request payload falling back to DB draft content.
- **Library Comparison Matrix Endpoint (`POST /api/v1/folders/comparison-matrix`)**:
  - `test_comparison_matrix_redis_cache_hit_vs_miss_behavior`: Empirical cache hit verification via Database Deletion Oracle (populates cache, deletes documents from SQLite, verifies subsequent identical request succeeds with 200 OK returning all rows from cache, whereas different topic returns 404).
  - `test_comparison_matrix_large_scale_pagination_bounds_120_papers`: 120 papers seeded; tests `limit=200, offset=0`, `limit=50, offset=0` (Page 1), `limit=50, offset=100` (Page 3, remaining 20 papers), page disjointness, `offset=150` empty result, `limit=201` rejection with HTTP 422, and `offset=-1` rejection with HTTP 422.
  - `test_comparison_matrix_search_filtering_methodology_datasets_metrics`: Tests multi-attribute keyword filtering across Core Methodology (`"Reinforcement Learning"`), Datasets (`"CelebA-HQ"`), Metric Keys (`"ROC-AUC"`), Metric Values (`"98.2%"`), and non-matching keyword (`"QuantumSupremacy"`).

### 1.2. Empirical Test Execution Results
Executed:
```bash
uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py -v
```
Verbatim execution summary:
```text
apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_special_characters_in_title_and_vietnamese PASSED [ 10%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_empty_content_graceful_handling PASSED [ 20%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_custom_latex_code_preservation PASSED [ 30%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_export_errors_and_isolation FAILED [ 40%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_associative_suggestions_high_similarity_match PASSED [ 50%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_associative_suggestions_zero_similarity_disjoint_vocabulary PASSED [ 60%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_associative_suggestions_empty_draft_text_and_db_fallback PASSED [ 70%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_comparison_matrix_redis_cache_hit_vs_miss_behavior PASSED [ 80%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_comparison_matrix_large_scale_pagination_bounds_120_papers PASSED [ 90%]
apps/api/tests/test_m1_pillars_empirical_stress.py::test_comparison_matrix_search_filtering_methodology_datasets_metrics PASSED [100%]
========================= 1 failed, 9 passed in 7.23s ==========================
```

### 1.3. Defect Observation: Tenant Isolation Authorization Flaw in `DraftService.export_overleaf`
In `apps/api/src/api/services/draft_service.py` lines 593–600:
```python
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft:
            raise KeyError(f"Draft {draft_id} not found")
```
When User 2 requests export of User 1's draft:
`self.get_user_draft_role(draft_id=draft_id, user_id=user2.id, ...)` returns `(draft, None)` because User 2 is neither the owner nor a collaborator and public sharing is disabled (`apps/api/src/api/services/draft_service.py:141`).
However, `export_overleaf` checks only `if not draft:`, omitting `or not role:`.
In `test_overleaf_export_errors_and_isolation`:
```python
resp_forbidden = await client.post(
    f"/api/v1/drafts/{draft1.id}:export-overleaf",
    headers=headers_user2,
)
assert resp_forbidden.status_code == 404
```
**Actual Result**:
`assert 200 == 404` where `resp_forbidden` was `<Response [200 OK]>`.
User 2 successfully received the full private LaTeX source code and Overleaf web launch URL for User 1's private draft.

By contrast, `export_draft_zip_bundle` in `apps/api/src/api/services/draft_service.py:486` correctly enforces:
```python
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")
```
And `get_draft` in line 155 also correctly enforces:
```python
        if not draft or not role:
            return None
```

### 1.4. Frontend and Quality Gate Execution
- Frontend Writing Tests: `pnpm --prefix apps/web test src/features/writing` -> 16 test files passed, 111 passed in 38.01s.
- Frontend Library Tests: `pnpm --prefix apps/web test src/features/library` -> 5 test files passed, 23 passed in 9.98s.
- TypeScript Compile Check: `pnpm --prefix apps/web exec tsc -b` -> exited with code 0 (0 errors).
- Ruff Check: `uv run ruff check apps/api` -> `All checks passed!`.
- Ruff Format: `uv run ruff format --check apps/api` -> `90 files already formatted`.

---

## 2. Logic Chain

1. **Pillar 2 (Overleaf Export) Evaluation**:
   - `test_overleaf_special_characters_in_title_and_vietnamese` passed: The URL encodes title and LaTeX snippet using `urllib.parse.quote_plus`, and curly braces `{}` are sanitized from `\title{...}` in `draft_service.py:603` to prevent TeX syntax corruption.
   - `test_overleaf_empty_content_graceful_handling` passed: Empty strings and `None` are substituted with `"% Empty draft content\n"` within the `\documentclass{article}` wrapper.
   - `test_overleaf_custom_latex_code_preservation` passed: Existing documents containing `\documentclass` are preserved verbatim without duplicate wrapping.
   - **However**, `test_overleaf_export_errors_and_isolation` failed: `DraftService.export_overleaf()` fails to check `or not role` after calling `get_user_draft_role()`. Any authenticated user can export and read any other user's private draft by ID. This is a severe authorization vulnerability.

2. **Pillar 3 (Associative Suggestions) Evaluation**:
   - `test_associative_suggestions_high_similarity_match` passed: Dense domain overlap extracts keywords, computes combined Jaccard/overlap scores > 0.40, generates `\cite{...}` tags, and contextualizes citation with paper title and page number.
   - `test_associative_suggestions_zero_similarity_disjoint_vocabulary` passed: Disjoint text returns `total_found == 0` and empty list; high threshold `min_similarity=0.99` filters sub-threshold matches.
   - `test_associative_suggestions_empty_draft_text_and_db_fallback` passed: Empty payload with blank draft returns 200 OK cleanly; empty payload with existing draft body successfully falls back to DB draft content.

3. **Pillar 4 (Library Comparison Matrix) Evaluation**:
   - `test_comparison_matrix_redis_cache_hit_vs_miss_behavior` passed: Verified through the Database Deletion Oracle. After the first matrix extraction, rows are cached in Redis/idempotency adapter with TTL 3600s. Deleting all documents from SQLite still allows subsequent queries with identical `(topic, folder_id, document_ids)` to return 200 OK with all rows directly from cache. Querying a new topic misses cache, hits DB, and returns 404 as expected.
   - `test_comparison_matrix_large_scale_pagination_bounds_120_papers` passed: Evaluated across 120 papers. Page 1 (`limit=50, offset=0`) and Page 3 (`limit=50, offset=100`) return non-overlapping document sets. `limit=200, offset=0` returns all 120 papers. Pydantic schema properly enforces `limit <= 200` and `offset >= 0` with HTTP 422 rejections on out-of-bounds inputs.
   - `test_comparison_matrix_search_filtering_methodology_datasets_metrics` passed: Multi-field filtering accurately selects rows across Core Methodology, Datasets, Metric Keys, and Metric Values.

---

## 3. Challenge Report

### Challenge Summary
**Overall Risk Assessment**: **HIGH** (due to authorization bypass in Overleaf export)

### Challenges Evaluated

| # | Component | Attack / Challenge Scenario | Expected Behavior | Actual Behavior | Verdict |
|---|-----------|-----------------------------|-------------------|-----------------|---------|
| 1 | Overleaf Export | Title with UTF-8, quotes, ampersands, braces, math | Clean URL encoding, balanced LaTeX braces | `snip` and `snip_name` valid and reversible | **PASS** |
| 2 | Overleaf Export | Empty content (`""` and `None`) | Graceful article boilerplate with `% Empty draft content` | HTTP 200 with valid Overleaf URL | **PASS** |
| 3 | Overleaf Export | Custom LaTeX code with `\documentclass[12pt]{report}` | Preserved verbatim, no double `\documentclass` | Preserved verbatim, single `\documentclass` | **PASS** |
| 4 | Overleaf Export | Unauthorized tenant requests another user's draft | HTTP 404 (Resource not found / access denied) | **HTTP 200 (Leak of draft source)** | **FAIL (CRITICAL)** |
| 5 | Associative Memory | High conceptual similarity | Ranked matches, similarity > 0.40, `\cite{...}` | Ranked matches, valid citation tag | **PASS** |
| 6 | Associative Memory | Zero similarity / disjoint vocabulary | `total_found == 0`, `suggestions == []` | `total_found == 0`, `suggestions == []` | **PASS** |
| 7 | Associative Memory | Empty draft text (request + DB blank) | HTTP 200, `query_excerpt == ""`, 0 suggestions | HTTP 200, 0 suggestions, no crash | **PASS** |
| 8 | Comparison Matrix | Cache hit vs miss (DB Deletion Oracle) | Subsequent requests served from cache after DB purge | 200 OK from cache; 404 on uncached topic | **PASS** |
| 9 | Comparison Matrix | 100+ papers pagination (`limit=200`, `offset=100`) | Full 120 papers returned; strict page disjointness | 120 returned on limit=200; disjoint pages | **PASS** |
| 10 | Comparison Matrix | Search across methodology, datasets, metrics | Filter rows matching keyword in any of the 3 fields | Exact subset returned for all 3 fields | **PASS** |

### Critical Finding Details: Tenant Isolation Bypass
- **Vulnerability**: Authorization Bypass / Cross-Tenant Draft Leakage
- **File**: `apps/api/src/api/services/draft_service.py:593-600`
- **Root Cause**:
  ```python
  draft, role = await self.get_user_draft_role(
      draft_id=draft_id,
      user_id=user_id,
      user_email=user_email,
  )
  if not draft: # BUG: Missing 'or not role'
      raise KeyError(f"Draft {draft_id} not found")
  ```
- **Blast Radius**: Any authenticated user can export any other user's draft to Overleaf and inspect its contents, bypassing workspace privacy.
- **Recommended Remediation**:
  In `apps/api/src/api/services/draft_service.py:598`, update the check to:
  ```python
  if not draft or not role:
      raise KeyError(f"Draft {draft_id} not found")
  ```

---

## 4. Caveats

- In local testing without an active Redis server, the `RedisIdempotencyAdapter` uses its transparent `InMemoryIdempotencyAdapter` fallback. The cache hit vs miss behavior was verified using this adapter via the Database Deletion Oracle.
- The authorization failure was reproduced directly against the live FastAPI endpoint using `httpx.AsyncClient` with two distinct authenticated users.

---

## 5. Conclusion

**Verdict: REJECT**

While 9 out of 10 empirical stress tests for Milestone 1 passed (including UTF-8/special characters encoding, empty content handling, custom LaTeX preservation, associative suggestions recall, Redis caching oracle, 100+ paper pagination bounds, and multi-field search filtering), Milestone 1 is **REJECTED** due to a critical authorization bypass vulnerability:
- `POST /api/v1/drafts/{id}:export-overleaf` allows cross-tenant draft export because `DraftService.export_overleaf()` does not check if `role` is `None`.
- The worker must patch `apps/api/src/api/services/draft_service.py:598` to `if not draft or not role:` so unauthorized draft access yields HTTP 404.

---

## 6. Verification Method

To independently reproduce the empirical challenge findings:

1. **Run the Full Empirical Stress Suite**:
   ```bash
   uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py -v
   ```
   *Observed*: 9 passed, 1 failed (`test_overleaf_export_errors_and_isolation` asserting `assert 200 == 404`).

2. **Isolate the Authorization Leak**:
   ```bash
   uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py -k "test_overleaf_export_errors_and_isolation" -v
   ```
   *Observed*: `FAILED apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_export_errors_and_isolation - assert 200 == 404`.

3. **Verify Passing Dimensions**:
   ```bash
   uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py -k "not test_overleaf_export_errors_and_isolation" -v
   ```
   *Observed*: 9 passed in ~7.1s.

4. **Verify Frontend Suites**:
   ```bash
   pnpm --prefix apps/web test src/features/writing
   pnpm --prefix apps/web test src/features/library
   pnpm --prefix apps/web exec tsc -b
   ```
   *Observed*: 111 writing tests passed, 23 library tests passed, 0 TypeScript errors.

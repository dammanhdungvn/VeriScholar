# Forensic Audit Report: Milestone 1 (M1_WRITING_AND_SYNTHESIS)

**Work Product**: Milestone 1 Implementation (Pillars 2, 3, and 4)  
**Profile**: General Project  
**Auditor**: Forensic Auditor (`auditor_m1`)  
**Verdict**: **INTEGRITY VIOLATION** (REJECTED)  

---

## Forensic Audit Summary

| Check | Scope | Result | Details |
|---|---|:---:|---|
| **Static Analysis — Hardcoded Values** | `apps/web/src/features/writing/components/WritingWorkspace.tsx` | 🔴 **FAIL** | `activeMemorySuggestion` initialized with pre-populated dummy state (`assoc-1`, "Attention Is All You Need", "vaswani2017attention", 0.94) instead of starting `null`. |
| **Contract Conformance & Security Isolation** | `apps/api/src/api/services/draft_service.py` | 🔴 **FAIL** | `export_overleaf` checks `if not draft:` instead of `if not draft or not role:`. Cross-tenant draft export returned HTTP 200 instead of HTTP 404/403. |
| **Code Hygiene & Quality Gate** | `apps/api/src/api/services/library_synthesis_service.py` | 🔴 **FAIL** | `uv run ruff check` failed with 2 errors: `I001` (unsorted imports) and `E501` (line length 103 > 100). |
| **Empirical Behavioral Verification** | `apps/api/tests/test_m1_pillars_empirical_stress.py` | 🔴 **FAIL** | 1 test failed: `test_overleaf_export_errors_and_isolation` due to authorization leak. |
| **Frontend Compilation & Lint** | `apps/web` (`tsc -b`, `oxlint`) | 🟢 **PASS** | `tsc -b` exits code 0; `oxlint` found 0 errors and 0 warnings. |
| **Frontend Vitest Suites** | `src/features/writing` & `ComparisonMatrixModal` | 🟢 **PASS** | 103/103 tests passed in writing; 7/7 tests passed in ComparisonMatrixModal. |
| **Core Architecture & Ports/Adapters** | Hexagonal Architecture adherence | 🟢 **PASS** | In-memory fallback mechanism in `RedisIdempotencyAdapter` is isolated; no leaky core dependencies. |

---

## 1. Observation

1. **Defect 1: Cross-Tenant Authorization Leak in Overleaf Export**
   - **File**: `apps/api/src/api/services/draft_service.py`, lines 597–603:
     ```python
     draft, role = await self.get_user_draft_role(
         draft_id=draft_id,
         user_id=user_id,
         user_email=user_email,
     )
     if not draft:
         raise KeyError(f"Draft {draft_id} not found")
     ```
   - **Empirical Execution**: In `apps/api/tests/test_m1_pillars_empirical_stress.py`, `test_overleaf_export_errors_and_isolation` tests whether User 2 can export User 1's private draft.
   - **Verbatim Error**:
     ```
     FAILED apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_export_errors_and_isolation - assert 200 == 404
     ```
   - **Log Evidence**:
     ```json
     {'log_type': 'access', 'status_code': 200, 'method': 'POST', 'path': '/api/v1/drafts/811127a0-140d-4086-be56-590548a77f50:export-overleaf', 'request_id': '68508ec4-a8c0-4cb7-90c0-be3ffcf7c921'}
     ```
   - When User 2 invokes `POST /api/v1/drafts/{id}:export-overleaf` for User 1's draft, `get_user_draft_role` returns `(draft, None)`. Because line 602 only checks `if not draft:` rather than `if not draft or not role:`, it does NOT raise `KeyError`, bypassing access control and generating an Overleaf payload for an unauthorized user.

2. **Defect 2: Hardcoded Pre-Populated Dummy Suggestion in UI**
   - **File**: `apps/web/src/features/writing/components/WritingWorkspace.tsx`, lines 168–183:
     ```typescript
     // Proactive Associative Memory Card suggestion state
     const [activeMemorySuggestion, setActiveMemorySuggestion] = useState<{
       id: string;
       title: string;
       page: number;
       citationKey: string;
       noteSnippet?: string;
       noteId?: string;
       similarityScore?: number;
     } | null>({
       id: "assoc-1",
       title: "Attention Is All You Need",
       page: 4,
       citationKey: "vaswani2017attention",
       noteSnippet: "Cơ chế Scaled Dot-Product Attention và Multi-Head Attention loại bỏ hoàn toàn tính tuần tự.",
       similarityScore: 0.94,
     });
     ```
   - Rather than initializing to `null` and displaying insights only when queried from the proactive associative API (`draftsApi.getAssociativeSuggestions`), the UI loads with hardcoded mock research note values.

3. **Defect 3: Ruff Linter Quality Gate Violation**
   - **File**: `apps/api/src/api/services/library_synthesis_service.py`
   - **Command**: `uv run ruff check apps/api/src/api/services/library_synthesis_service.py`
   - **Verbatim Output**:
     ```
     I001 [*] Import block is un-sorted or un-formatted
       --> apps/api/src/api/services/library_synthesis_service.py:5:1

     E501 Line too long (103 > 100)
        --> apps/api/src/api/services/library_synthesis_service.py:139:101
         |
     137 |                 datasets = meta.get("datasets") or (
     138 |                     ["PubMedQA", "BioASQ", "SciFact"]
     139 |                     if "vaccine" in (doc.title or "").lower() or "biology" in (doc.title or "").lower()
         |                                                                                                     ^^^
     140 |                     else ["WMT-14", "GLUE", "ImageNet-1K"]
     141 |                 )
         |
     Found 2 errors.
     [*] 1 fixable with the `--fix` option.
     ```

---

## 2. Logic Chain

1. **Security & Invariant Violation**:
   - `AGENTS.md` and `PROJECT.md` require multi-tenant boundary isolation and proper authorization enforcement across all API endpoints.
   - Other draft endpoints (`get_draft`, `update_draft`, `delete_draft`, `export_bundle`) consistently enforce:
     ```python
     if not draft or not role:
         raise KeyError(f"Draft {draft_id} not found")
     ```
   - `export_overleaf` in `draft_service.py` omits `or not role:`. As directly proven by `test_overleaf_export_errors_and_isolation`, User 2 can export User 1's draft, causing an authorization leak (HTTP 200 instead of 404/403).

2. **Integrity Forensics Prohibited Pattern Violation**:
   - The forensic specification strictly prohibits:
     - Hardcoded test results / expected outputs.
     - Facade implementations where UI renders static mock objects.
   - `WritingWorkspace.tsx` lines 176–183 pre-populates `activeMemorySuggestion` with hardcoded string literals and numeric scores (`assoc-1`, `Attention Is All You Need`, `vaswani2017attention`, `0.94`) on component mount, mimicking a successful suggestion before any dynamic processing takes place.

3. **Quality Gate Failure**:
   - `AGENTS.md` Section 8 explicitly states: *"Zero Warning / Zero Lint: `uv run ruff check .` and `uv run ruff format --check .` exit cleanly with zero errors and warnings."*
   - `library_synthesis_service.py` introduces 2 Ruff errors (`I001`, `E501`), causing `uv run ruff check` to fail with exit code 1.

4. **Test Suite Failure**:
   - `test_m1_pillars_empirical_stress.py` execution results in 1 failure (`test_overleaf_export_errors_and_isolation`).
   - Under the Integrity Forensics core principles: *"If ANY check fails, the verdict is INTEGRITY VIOLATION and the work product must be rejected."*

---

## 3. Caveats

- **Caveat 1**: The basic functional paths in `test_backend_pillars_completion.py` (4/4 tests) and frontend Vitest suites (110/110 tests) passed. However, `test_backend_pillars_completion.py` only tested single-user happy paths and did not verify cross-user isolation or unauthorized access handling.
- **Caveat 2**: As an auditor, per Key Constraints, no source code modifications were made. The identified defects must be resolved by the implementation agent (`worker_m1`).

---

## 4. Conclusion

The work product for Milestone 1 fails forensic integrity verification due to:
1. **Critical Security / Authorization Bypass** in `apps/api/src/api/services/draft_service.py`: `export_overleaf` lacks role verification (`if not draft or not role:`), allowing cross-user draft data leaks.
2. **Prohibited Pattern Violation** in `apps/web/src/features/writing/components/WritingWorkspace.tsx`: Pre-populated static mock data in `useState` for proactive associative suggestions.
3. **Quality Gate Lint Failures** in `apps/api/src/api/services/library_synthesis_service.py`: 2 Ruff errors (`I001`, `E501`).
4. **Empirical Verification Failure**: `uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py` exits with code 1.

**Verdict: INTEGRITY VIOLATION — REJECTED.**

### Required Remediation for Worker M1:
1. In `apps/api/src/api/services/draft_service.py` line 602, change:
   ```python
   if not draft or not role:
       raise KeyError(f"Draft {draft_id} not found")
   ```
2. In `apps/web/src/features/writing/components/WritingWorkspace.tsx` line 176, initialize `activeMemorySuggestion` to `null`:
   ```typescript
   const [activeMemorySuggestion, setActiveMemorySuggestion] = useState<{
     id: string;
     title: string;
     page: number;
     citationKey: string;
     noteSnippet?: string;
     noteId?: string;
     similarityScore?: number;
   } | null>(null);
   ```
3. In `apps/api/src/api/services/library_synthesis_service.py`:
   - Sort imports to satisfy `I001`.
   - Wrap line 139 to under 100 characters to satisfy `E501`.
4. Re-run `uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py` and ensure 10/10 tests pass.

---

## 5. Verification Method

To independently reproduce all forensic audit findings:

1. **Verify Isolation Failure in Overleaf Export**:
   ```bash
   uv run pytest apps/api/tests/test_m1_pillars_empirical_stress.py::test_overleaf_export_errors_and_isolation -v
   ```
   *Actual Result*: Fails with `assert 200 == 404` (User 2 exports User 1 draft).

2. **Verify Ruff Lint Errors**:
   ```bash
   uv run ruff check apps/api/src/api/services/library_synthesis_service.py
   ```
   *Actual Result*: Exits code 1 with 2 errors (`I001`, `E501`).

3. **Verify Hardcoded Mock in WritingWorkspace**:
   Inspect `apps/web/src/features/writing/components/WritingWorkspace.tsx` lines 176–183:
   ```bash
   grep -n -C 5 "assoc-1" apps/web/src/features/writing/components/WritingWorkspace.tsx
   ```
   *Actual Result*: Hardcoded initial state contains dummy mock data.

# Handoff Report: Survey Explorer 1 (CI Frontend Vitest & Quality Gates)

## 1. Observation
- **Workflow File**: `.github/workflows/ci.yml`
  - Lines 42-44: `paths-filter` currently only monitors `frontend: - 'apps/web/**'`. Any changes targeting `.github/workflows/ci.yml` do not trigger `frontend-checks` during PR events.
  - Lines 181-184: `frontend-checks` runs `pnpm test:run` without JUnit XML reporter flags.
  - Missing artifact upload step: Lines 181-188 lack an artifact upload action comparable to `backend-checks` (lines 131-137: `actions/upload-artifact@v4`).
- **Frontend Test Suite Size & Status**:
  - Command: `pnpm exec vitest run` in `apps/web`
  - Output: 63 test files, 378 total tests, 378 passed (100% pass rate).
  - Test categorization: `src/features/auth` contains exactly 83 tests (the historical benchmark referenced in `ORIGINAL_REQUEST.md`), while writing has 119 tests, dashboard has 67 tests, reader has 25 tests, library has 23 tests, and utilities/components have 61 tests.
- **Execution Performance**:
  - Baseline execution (`pool: 'forks'`, default): Took **278.54 seconds** (~4m38s). Vitest warned: `"Environment jsdom was created 63 times · 156.30s total, 63% of tracked time... create it once per worker with pool: 'vmThreads'"`.
  - Optimized execution with `--pool=vmThreads`: Took **33.88 seconds** for all 63 files and 378 tests (an 8.2x speedup / 88% runtime reduction).
  - Auxiliary frontend checks: `pnpm lint` (`oxlint`) takes 0.61s; `pnpm exec tsc -b` takes 15.37s; `pnpm build` (`vite build`) takes 31.73s.
- **JUnit XML Reporter Behavior**:
  - Command: `pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml`
  - Output: Successfully generated standard JUnit XML file at `apps/web/test-results.xml`.
  - Note: `test-results.xml` is already ignored in git via `.gitignore`.
  - Important GitHub Actions runner behavior: `defaults.run.working-directory: apps/web` applies only to `run:` steps, not `uses:` steps. Thus, `actions/upload-artifact@v4` requires `path: apps/web/test-results.xml`.

## 2. Logic Chain
1. *From Observation 1*: The original request asked for running the Vitest suite (83 tests) with JUnit XML in `.github/workflows/ci.yml` and failing PRs on error.
2. *From Observation 2*: The codebase currently contains 378 tests across 63 files (including the 83 auth tests). Running `pnpm test:run` executes all 378 tests.
3. *From Observation 3*: Without optimization, Vitest alone takes 278s, which combined with dependency installation (15s), type checking (15s), and production build (32s) totals ~340-360s (> 5 minutes), violating the < 5 min CI threshold constraint.
4. *From Observation 3*: Configuring `pool: "vmThreads"` reduces Vitest execution to 33.88s, bringing total `frontend-checks` runtime to ~102s (< 2 minutes), comfortably satisfying the < 5 min SLA.
5. *From Observation 4*: Vitest returns non-zero exit code (1) when any test fails, which halts GitHub Actions execution under bash `set -e` and marks the PR check as failed. By using `if: always()` on `actions/upload-artifact@v4`, the JUnit XML report will always be uploaded even when tests fail.
6. *From Observation 4*: Setting `path: apps/web/test-results.xml` avoids the common pitfall where `defaults.run.working-directory` does not apply to action steps.

## 3. Caveats
- Browser-specific end-to-end tests (Playwright scripts under `apps/web/scripts/`) are not part of `pnpm test:run` (they require running browser binaries and live servers).
- In some environments without `canvas` installed, JSDOM emits non-fatal warnings (`HTMLCanvasElement's getContext() method: without installing the canvas npm package`). These warnings do not affect test passes or assertions.
- Vitest `vmThreads` requires Node.js >= 18 (CI uses Node 20 LTS, which is fully supported).

## 4. Conclusion
Requirement R1 can be fully satisfied with high stability and enterprise performance through two targeted modifications:
1. In `apps/web/vite.config.ts`: add `pool: "vmThreads"`, and configure default JUnit XML reporting when `process.env.CI` is true.
2. In `.github/workflows/ci.yml`:
   - Update `pnpm test:run` in `frontend-checks` with `--reporter=default --reporter=junit --outputFile=test-results.xml`.
   - Add an `actions/upload-artifact@v4` step with `name: frontend-test-results`, `path: apps/web/test-results.xml`, and `if: always()`.
   - Add `.github/workflows/ci.yml` to the `frontend` filter in `detect-changes`.
Total job runtime will be ~1m42s, well within the 5-minute requirement, and 100% of the 378 tests (including the 83 auth tests) will be executed on every PR with automatic merge-blocking on failure.

## 5. Verification Method
1. **Vitest Execution & JUnit Verification**:
   ```bash
   cd apps/web && pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml
   ```
   *Expected*: 63 test files pass, 378 tests pass, `apps/web/test-results.xml` is created with valid XML root `<testsuites>`.
2. **Speed Benchmark (< 50s)**:
   ```bash
   cd apps/web && time pnpm exec vitest run --pool=vmThreads
   ```
   *Expected*: Total execution time < 45 seconds.
3. **Workflow Syntax & Path Inspection**:
   Inspect `.github/workflows/ci.yml` to verify `actions/upload-artifact@v4` has `name: frontend-test-results`, `path: apps/web/test-results.xml`, and `if: always()`.

# Legacy Unit Tests Purge & Clean Test Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete all legacy Backend (`apps/api/tests/`), Core (`packages/core/tests/`), and Frontend (`apps/web/src/**/*.test.*`) unit test files while keeping a clean, zero-test-tolerant Pytest + Vitest + CI harness ready for fresh MVP PRD tests.

**Architecture:** We remove all 53 Python test files (`apps/api/tests/test_*.py`, `packages/core/tests/**/test_*.py`) and legacy `aiosqlite` test dependency, all 71 Frontend Vitest files (`apps/web/src/**/*.test.{ts,tsx}`) plus `apps/web/src/test/visual-audit.mjs`, and legacy QA audit docs. To prevent zero-test runs from breaking local workflows or GitHub Actions (`pytest` exit code `5`, `vitest` exit code `1`), we configure `pytest_sessionfinish` in `apps/api/tests/conftest.py`, `passWithNoTests: true` in `apps/web/vite.config.ts`, and align `.github/workflows/ci.yml` and `docs/05-testing-and-qa/`.

**Tech Stack:** Python 3.12+, Pytest, Ruff, UV Workspace, React 19, TypeScript, Vite, Vitest, GitHub Actions.

**Spec:** `docs/PRD/00-overview-and-cleanup.md` (and user directive to purge all legacy Backend/Core/Frontend unit tests and retain only the empty test runner framework).

## Global Constraints

- Zero `test_*.py` or `*_test.py` files may remain in `apps/api/tests/` or `packages/core/tests/`.
- Zero `*.test.ts`, `*.test.tsx`, `*.spec.ts`, or `*.spec.tsx` files (and no `visual-audit.mjs` or `apps/web/dist/`) may remain in `apps/web/`.
- Legacy SQLite test driver `aiosqlite` must be removed from `pyproject.toml` because MVP strictly targets PostgreSQL + `pgvector`.
- Running `uv run pytest`, `uv run pytest --junitxml=test-results.xml`, and `npm --prefix apps/web run test` on the empty suite must exit `0` while still failing (`!= 0`) whenever a future test fails or raises collection errors.
- `.github/workflows/ci.yml` and `docs/` must contain zero references to deleted `deploy/docker-compose.enterprise.yml`, deleted test files, or wrong `docs/PRD/` filenames.

## Review Focus

1. **`pytest` exiting with code `5` (`NO_TESTS_COLLECTED`) when 0 test files exist:** `apps/api/tests/conftest.py` must convert `pytest.ExitCode.NO_TESTS_COLLECTED` (`5`) to `pytest.ExitCode.OK` (`0`) without masking `TESTS_FAILED` (`1`), `INTERNAL_ERROR` (`3`), or `USAGE_ERROR` (`4`) (pinned in Task 1 Steps 2–4).
2. **`pytest-cov` emitting warnings or failing in `.github/workflows/ci.yml` when 0 tests run:** `.github/workflows/ci.yml` must run `uv run pytest --junitxml=test-results.xml` cleanly and no longer reference deleted `deploy/docker-compose.enterprise.yml` (pinned in Task 3 Steps 1–4).
3. **`vitest run` exiting with code `1` (`No test files found`) when 0 test files exist:** `apps/web/vite.config.ts` must set `passWithNoTests: true` while keeping `setupFiles: ["./src/test/setup.ts"]` valid under `tsc -b` (pinned in Task 2 Steps 2–4).
4. **Orphaned test directories, `__pycache__`, or `aiosqlite` dependency left behind:** `packages/core/tests/__init__.py` must keep the `testpaths` directory present in git so `pytest` does not emit missing-testpath warnings, and `aiosqlite` must be absent from `pyproject.toml` (pinned in Task 1 Steps 1 & 4).
5. **Broken `docs/PRD/` links and legacy 71-test / `CitationGraphModal` claims in `docs/`:** `docs/README.md` and `docs/05-testing-and-qa/` must resolve every relative Markdown link on disk and remove deleted `quality-gates-certification.md` and `api-eval-snapshots.md` (pinned in Task 3 Steps 1–4).

---

### Task 1: Purge Backend & Core Unit Tests and Configure Zero-Test Pytest Harness

**Files:**
- Delete: all 36 `apps/api/tests/test_*.py` files and all 17 `packages/core/tests/**/test_*.py` files (plus `packages/core/tests/adapters/`, `packages/core/tests/domain/`, `packages/core/tests/services/`)
- Create: `packages/core/tests/__init__.py`
- Modify: `apps/api/tests/conftest.py`, `pyproject.toml`, `uv.lock`

**Interfaces:**
- Consumes: `pyproject.toml` (`[tool.pytest.ini_options].testpaths = ["apps/api/tests", "packages/core/tests"]`)
- Produces: `pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None` in `apps/api/tests/conftest.py`

- [ ] **Step 1: Delete all `test_*.py` files in `apps/api/tests/` and `packages/core/tests/`, create `packages/core/tests/__init__.py`, and remove `aiosqlite` + `"tests/**"` from `pyproject.toml`**

Delete `apps/api/tests/test_*.py`, `packages/core/tests/adapters`, `packages/core/tests/domain`, `packages/core/tests/services`, and `__pycache__` folders; create `packages/core/tests/__init__.py`; remove `"aiosqlite>=0.20.0"` and `"tests/**" = ["E501"]` from `pyproject.toml` and run `uv sync --all-packages`.

- [ ] **Step 2: Run `uv run pytest` to verify RED exit code `5` (`no tests ran`)**

Run: `uv run pytest`
Expected: FAIL with exit code `5` (`collected 0 items` / `no tests ran`).

- [ ] **Step 3: Implement `pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None` in `apps/api/tests/conftest.py`**

```python
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Allow empty test suite (exit code 5) to pass cleanly while MVP tests are rebuilt."""
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK
```

- [ ] **Step 4: Verify `uv run pytest` and `uv run ruff check .` pass with zero test files**

Run: `test -z "$(find apps/api/tests packages/core/tests -name 'test_*.py')" && ! grep -q 'aiosqlite' pyproject.toml && uv run pytest && uv run ruff check .`
Expected: PASS (`exit code 0`, `collected 0 items`, `All checks passed!`).

- [ ] **Step 5: Commit**

```bash
git add apps/api/tests packages/core/tests pyproject.toml uv.lock
git commit -m "chore(tests): purge legacy backend/core unit tests and configure empty pytest harness"
```

---

### Task 2: Purge Frontend Unit Tests and Configure Zero-Test Vitest Harness

**Files:**
- Delete: all 71 `apps/web/src/**/*.test.{ts,tsx}` files, `apps/web/src/test/visual-audit.mjs`, and `apps/web/dist/`
- Modify: `apps/web/vite.config.ts`

**Interfaces:**
- Consumes: `apps/web/src/test/setup.ts`
- Produces: `test.passWithNoTests: true` in `apps/web/vite.config.ts`

- [ ] **Step 1: Delete all `*.test.ts`, `*.test.tsx`, `apps/web/src/test/visual-audit.mjs`, and `apps/web/dist/`**

Run `find apps/web/src -type f \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" -o -name "*.spec.tsx" \) -delete && rm -f apps/web/src/test/visual-audit.mjs && rm -rf apps/web/dist`.

- [ ] **Step 2: Run `npm --prefix apps/web run test` to verify RED exit code `1` (`No test files found`)**

Run: `npm --prefix apps/web run test`
Expected: FAIL with exit code `1` (`No test files found, exiting with code 1`).

- [ ] **Step 3: Add `passWithNoTests: true` to `test` config in `apps/web/vite.config.ts`**

```ts
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    reporters: ["default"],
    passWithNoTests: true,
  },
```

- [ ] **Step 4: Verify Frontend test runner, linter, and production build pass cleanly**

Run: `test -z "$(find apps/web/src -name '*.test.*' -o -name '*.spec.*')" && test ! -f apps/web/src/test/visual-audit.mjs && npm --prefix apps/web run test && npm --prefix apps/web run lint && npm --prefix apps/web run build && rm -rf apps/web/dist`
Expected: PASS (`No test files found, exiting with code 0`, `oxlint` 0 errors, `tsc -b && vite build` 0 errors).

- [ ] **Step 5: Commit**

```bash
git add apps/web
git commit -m "chore(web): purge legacy frontend unit tests and enable passWithNoTests in vitest"
```

---

### Task 3: Align CI Workflow (`.github/workflows/ci.yml`) and Testing Docs (`docs/`)

**Files:**
- Delete: `docs/05-testing-and-qa/quality-gates-certification.md`, `docs/05-testing-and-qa/api-eval-snapshots.md`
- Modify: `.github/workflows/ci.yml`, `docs/05-testing-and-qa/README.md`, `docs/05-testing-and-qa/testing-strategy.md`, `docs/README.md`

**Interfaces:**
- Consumes: Task 1 zero-test `pytest` harness, Task 2 zero-test `vitest` harness, `docs/PRD/00..07`
- Produces: Valid `.github/workflows/ci.yml` and link-verified `docs/README.md` + `docs/05-testing-and-qa/`

- [ ] **Step 1: Run verification script to confirm RED failures in `.github/workflows/ci.yml` and `docs/`**

Run:
```bash
uv run python -c "
from pathlib import Path
import re, sys
ci = Path('.github/workflows/ci.yml').read_text()
assert 'docker-compose.enterprise.yml' not in ci, 'stale enterprise compose in ci.yml'
readme = Path('docs/README.md').read_text()
for link in re.findall(r'\]\(([^)#]+)\)', readme):
    assert (Path('docs') / link).exists(), f'broken link in docs/README.md: {link}'
"
```
Expected: FAIL (`AssertionError: stale enterprise compose in ci.yml` and broken links in `docs/README.md`).

- [ ] **Step 2: Update `.github/workflows/ci.yml` and clean `docs/05-testing-and-qa/` + `docs/README.md`**

1. In `.github/workflows/ci.yml`:
   - Remove nonexistent filter paths (`apps/worker/**`, `apps/sandbox-broker/**`, `infra/**`).
   - Change Pytest command to `uv run pytest --junitxml=test-results.xml`.
   - Change Vitest command to `pnpm test:run --passWithNoTests --reporter=default --reporter=junit --outputFile=test-results.xml`.
   - Remove the two `Validate Enterprise Docker Compose Configuration` steps referencing deleted `deploy/docker-compose.enterprise.yml` and `deploy/.env.enterprise.example`.
2. Delete `docs/05-testing-and-qa/quality-gates-certification.md` and `docs/05-testing-and-qa/api-eval-snapshots.md`.
3. Rewrite `docs/05-testing-and-qa/README.md` and `docs/05-testing-and-qa/testing-strategy.md` to describe the clean MVP testing architecture (`PostgreSQL + pgvector`, `ENVIRONMENT=test`, `LANGFUSE_ENABLED=false`, `Vitest + jsdom`, Hexagonal boundary gate) without claiming legacy 71-file or SQLite test suites exist.
4. Fix all `docs/PRD/` filenames (`01-auth-and-user.md` through `07-monitoring-and-langfuse.md`), remove `ARQ Worker`, and remove deleted `05-testing-and-qa` file entries in `docs/README.md`.

- [ ] **Step 3: Run link, CI, and JUnit XML verification**

Run:
```bash
uv run python -c "
from pathlib import Path
import re
ci = Path('.github/workflows/ci.yml').read_text()
assert 'docker-compose.enterprise.yml' not in ci
assert '--cov=' not in ci
for doc_path in [Path('docs/README.md'), Path('docs/05-testing-and-qa/README.md'), Path('docs/05-testing-and-qa/testing-strategy.md')]:
    text = doc_path.read_text()
    assert 'CitationGraphModal' not in text and '71 tệp' not in text and '71 Test Files' not in text
    for link in re.findall(r'\]\(([^)#]+)\)', text):
        if not link.startswith(('http://', 'https://', 'mailto:')):
            target = (doc_path.parent / link).resolve()
            assert target.exists(), f'Broken link in {doc_path}: {link} -> {target}'
print('CI & DOCS VERIFICATION PASSED')
" && uv run pytest --junitxml=/tmp/verischolar-junit.xml && rm -f /tmp/verischolar-junit.xml
```
Expected: PASS (`CI & DOCS VERIFICATION PASSED` and `exit code 0`).

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-10-25-legacy-unit-tests-purge.md .github/workflows/ci.yml docs/05-testing-and-qa docs/README.md
git commit -m "chore(ci,docs): align CI workflow and testing docs with clean MVP test harness"
```

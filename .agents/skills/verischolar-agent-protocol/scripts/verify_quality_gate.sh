#!/usr/bin/env bash
set -eo pipefail

echo "=========================================================="
echo "  VeriScholar Production Quality Gate Verification Suite  "
echo "=========================================================="

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${WORKSPACE_ROOT}"

echo "[1/5] Checking Python formatting and linting (Ruff)..."
uv run ruff check .
uv run ruff format --check .
echo "✓ Ruff checks passed."

echo "[2/5] Running Core Domain Unit Tests (In-Memory)..."
uv run pytest packages/core/tests/
echo "✓ Core tests passed."

echo "[3/5] Running Backend API Tests..."
uv run pytest apps/api/tests/
echo "✓ API tests passed."

echo "[4/5] Checking Frontend Linting (OxLint) & TypeScript Types..."
pnpm --prefix apps/web lint
pnpm --prefix apps/web exec tsc -b
echo "✓ Frontend lint and typecheck passed."

echo "[5/5] Building Web Client for Production..."
pnpm --prefix apps/web build
echo "✓ Frontend build passed."

echo "=========================================================="
echo "  ALL QUALITY GATES PASSED CLEANLY! Ready to commit/PR.   "
echo "=========================================================="

#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# VeriScholar 4 Verification Gates (Local Execution)
# -----------------------------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "======================================================================"
echo "== VeriScholar Local Quality & Verification Gates"
echo "======================================================================"

echo "-> [Gate 1/4] Running Ruff Python linter & format check..."
uv run ruff check .
uv run ruff format --check .

echo "-> [Gate 2/4] Running Backend pytest suite..."
uv run pytest

echo "-> [Gate 3/4] Running Frontend vitest suite..."
npm --prefix apps/web run test

echo "-> [Gate 4/4] Building Frontend production bundle..."
npm --prefix apps/web run build

echo "======================================================================"
echo "✅ All 4 Verification Gates passed with exit code 0!"
echo "======================================================================"

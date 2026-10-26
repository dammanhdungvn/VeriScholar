#!/usr/bin/env bash
# VeriScholar 4 Mandatory Verification Gates Runner (Local & Pre-Push Hook)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== VeriScholar: Running 4 Mandatory Verification Gates ===${NC}"

echo -e "\n${GREEN}[Gate 1/4] Python Linter & Formatter (Ruff)...${NC}"
uv run ruff check .
uv run ruff format --check .

echo -e "\n${GREEN}[Gate 2/4] Backend & Architecture Boundary Tests (Pytest)...${NC}"
uv run pytest

echo -e "\n${GREEN}[Gate 3/4] Frontend Unit Tests (Vitest)...${NC}"
npm --prefix apps/web run test

echo -e "\n${GREEN}[Gate 4/4] Frontend Production Build (TypeScript & Vite)...${NC}"
npm --prefix apps/web run build

echo -e "\n${GREEN}✅ All 4 Verification Gates PASSED (100% Exit Code 0)!${NC}"

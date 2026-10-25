#!/usr/bin/env bash
# VeriScholar One-Command Developer Onboarding, DB Bootstrap & Dev Runner
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

START_SERVICES=0
for arg in "$@"; do
    case "$arg" in
        --start)
            START_SERVICES=1
            ;;
    esac
done

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== VeriScholar MVP Developer Environment Setup ===${NC}"

# 1. Check Python version (>= 3.12)
echo -n "1. Checking Python version (>= 3.12)... "
if command -v python3 >/dev/null 2>&1; then
    py_ok=$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 12) else 0)')
    if [ "$py_ok" -eq 1 ]; then
        py_ver=$(python3 --version)
        echo -e "${GREEN}OK (${py_ver})${NC}"
    else
        echo -e "${RED}FAILED: Python 3.12+ required.${NC}"
        exit 1
    fi
else
    echo -e "${RED}FAILED: python3 not found.${NC}"
    exit 1
fi

# 2. Check Node.js version (>= 22)
echo -n "2. Checking Node.js version (>= 22)... "
if command -v node >/dev/null 2>&1; then
    node_ok=$(node -e 'const v = parseInt(process.versions.node.split(".")[0]); console.log(v >= 22 ? 1 : 0);')
    if [ "$node_ok" -eq 1 ]; then
        node_ver=$(node --version)
        echo -e "${GREEN}OK (${node_ver})${NC}"
    else
        echo -e "${YELLOW}WARNING: Node.js 22+ recommended (current: $(node --version)).${NC}"
    fi
else
    echo -e "${YELLOW}WARNING: node not found in PATH.${NC}"
fi

# 3. Check uv and pnpm/npm
echo -n "3. Checking uv & frontend package managers... "
if ! command -v uv >/dev/null 2>&1; then
    echo -e "${RED}FAILED: uv not found. Install from https://astral.sh/uv${NC}"
    exit 1
fi
echo -e "${GREEN}OK ($(uv --version))${NC}"

# 4. Canonical .env & Relative Symlink (Single Source of Truth)
echo -n "4. Ensuring canonical .env and apps/api/.env symlink... "
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
fi
ln -sf ../../.env apps/api/.env
echo -e "${GREEN}OK${NC}"

# 5. Install Backend & Frontend Dependencies
echo "5. Installing Python workspace & Frontend dependencies..."
uv sync --all-packages
if command -v pnpm >/dev/null 2>&1; then
    pnpm --prefix apps/web install
else
    npm --prefix apps/web install
fi

# 6. Start Docker Infrastructure (PostgreSQL pgvector & Redis 7)
echo "6. Starting PostgreSQL 16 (pgvector) & Redis 7 containers..."
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        docker compose up -d postgres redis
    else
        echo -e "${YELLOW}Docker socket requires elevated privileges; running via sudo...${NC}"
        sudo docker compose up -d postgres redis
    fi
else
    echo -e "${YELLOW}Docker CLI not found; assuming host-managed PostgreSQL & Redis.${NC}"
fi

# 7. Run Idempotent 18-Table Database Schema Bootstrap
echo "7. Bootstrapping 18 PostgreSQL tables, OCC triggers & HNSW/GIN indexes..."
uv run python -m api.db.init_db

# 8. Install Git Pre-Push Hook (4 Mandatory Verification Gates)
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/pre-push << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(git rev-parse --show-toplevel)"
exec bash "$ROOT_DIR/scripts/dev/verify.sh"
EOF
    chmod +x .git/hooks/pre-push
    echo -e "8. Installed Git pre-push hook (${GREEN}.git/hooks/pre-push -> scripts/dev/verify.sh${NC})"
fi

echo -e "\n${GREEN}✅ Setup & DB bootstrap completed successfully!${NC}"

# 9. Optionally start Backend API & Frontend Dev Server (--start)
if [ "$START_SERVICES" -eq 1 ]; then
    echo -e "\n${GREEN}Starting Backend API (:8000) and Frontend Web (:5173)... (Press Ctrl+C to stop)${NC}"
    API_PID=""
    WEB_PID=""
    cleanup() {
        echo -e "\n${YELLOW}Stopping VeriScholar dev services...${NC}"
        [ -n "$API_PID" ] && kill "$API_PID" 2>/dev/null || true
        [ -n "$WEB_PID" ] && kill "$WEB_PID" 2>/dev/null || true
        wait 2>/dev/null || true
    }
    trap cleanup SIGINT SIGTERM EXIT

    uv run --package api api &
    API_PID=$!

    npm --prefix apps/web run dev -- --host 0.0.0.0 &
    WEB_PID=$!

    wait "$API_PID" "$WEB_PID"
fi

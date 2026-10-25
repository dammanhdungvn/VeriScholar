#!/usr/bin/env bash
# VeriScholar Developer Environment Healthcheck & Setup Script
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== VeriScholar MVP Developer Environment Setup ===${NC}"

# 1. Check Python version (>= 3.12)
echo -n "Checking Python version (>= 3.12)... "
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
echo -n "Checking Node.js version (>= 22)... "
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

# 3. Check uv and pnpm
echo -n "Checking uv package manager... "
if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}OK ($(uv --version))${NC}"
else
    echo -e "${RED}FAILED: uv not found. Install from https://astral.sh/uv${NC}"
    exit 1
fi

echo -n "Checking pnpm package manager... "
if command -v pnpm >/dev/null 2>&1; then
    echo -e "${GREEN}OK ($(pnpm --version))${NC}"
else
    echo -e "${YELLOW}WARNING: pnpm not found. npm can be used as fallback.${NC}"
fi

# 4. Docker & Services Check
echo -n "Checking Docker daemon... "
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
    echo "Ensuring docker services (pgvector & redis) are running..."
    docker compose up -d postgres redis >/dev/null 2>&1 || true
else
    echo -e "${YELLOW}Docker daemon not reachable. Assuming host-managed services.${NC}"
fi

# 5. Check Database (PostgreSQL with pgvector)
echo -n "Checking PostgreSQL pgvector connectivity... "
uv run python3 -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://verischolar:verischolar@127.0.0.1:5432/verischolar')
    try:
        engine = create_async_engine(url, pool_pre_ping=True)
        async with engine.connect() as conn:
            res = await conn.execute(text(\"SELECT extname FROM pg_extension WHERE extname = 'vector';\"))
            row = res.scalar()
            await engine.dispose()
            return row == 'vector'
    except Exception:
        return False

ok = asyncio.run(check_db())
print('OK' if ok else 'UNAVAILABLE')
" || echo "UNAVAILABLE"

# 6. Check Redis
echo -n "Checking Redis 7 connectivity... "
uv run python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1.0)
try:
    s.connect(('127.0.0.1', 6379))
    s.sendall(b'*1\r\n\$4\r\nPING\r\n')
    reply = s.recv(1024)
    print('OK' if b'+PONG' in reply else 'CONNECTED')
    s.close()
except Exception:
    print('UNAVAILABLE (Start via: docker compose up -d redis)')
"

echo -e "\n${GREEN}Setup healthcheck completed successfully.${NC}"

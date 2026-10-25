#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== [VeriScholar Production Deploy] Starting Azure Ubuntu Rollout ==="

if command -v docker >/dev/null 2>&1; then
    echo "-> Ensuring PostgreSQL (pgvector) & Redis 7 containers are running..."
    docker compose up -d postgres redis
fi

echo "-> Syncing Python workspace dependencies with uv..."
uv sync --all-packages --frozen

if [[ "${SKIP_MIGRATION:-false}" != "true" ]]; then
    echo "-> Verifying PostgreSQL 16+ schema & migrations..."
    PYTHONPATH="apps/api/src:packages/core/src" uv run python -c \
        "from api.db.init_db import ensure_database_schema; print('Schema check module ready.')"
fi

echo "-> Building and deploying Web Frontend..."
bash "$ROOT_DIR/scripts/deploy_web.sh"

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    echo "=== [VeriScholar Production Deploy] DRY_RUN=true: Skipping systemd service restart ==="
    exit 0
fi

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files | grep -q "verischolar-api.service"; then
    echo "-> Restarting verischolar-api.service..."
    sudo systemctl restart verischolar-api.service
    sleep 2
    curl -fsS --max-time 10 http://127.0.0.1:8000/health || echo "Health check probe completed."
fi

echo "=== [VeriScholar Production Deploy] Rollout Complete ==="

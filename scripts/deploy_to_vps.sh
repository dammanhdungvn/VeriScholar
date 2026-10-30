#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# VeriScholar 1-Click Remote VPS Deployment Script
# -----------------------------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Defaults
SSH_KEY="${SSH_KEY:-/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem}"
SSH_HOST="${SSH_HOST:-48.193.46.15}"
SSH_USER="${SSH_USER:-VeriScholar}"
REMOTE_DIR="${REMOTE_DIR:-/home/VeriScholar/Workspace/VeriScholar}"
REMOTE_WEB_DIR="${REMOTE_WEB_DIR:-/var/www/verischolar/web}"
REMOTE_CONTAINER="${REMOTE_CONTAINER:-verischolar-postgres-dev}"
PUBLIC_URL="${PUBLIC_URL:-https://verischolar.duckdns.org}"

DRY_RUN=false
SKIP_GATE=false
FAST_MODE=false
SYNC_DB=true

usage() {
    cat <<EOF
Usage: scripts/deploy_to_vps.sh [OPTIONS]

Options:
  --fast          Fast sync for in-plan tasks (instant probe, skips gates 1-3, builds frontend & syncs in ~5s)
  --dry-run       Simulate the deployment steps without modifying remote files
  --skip-gate     Skip the local 4 Verification Gates before deployment
  --no-sync-db    Skip synchronizing local Dev PostgreSQL database to VPS
  --help, -h      Display this help message and exit

Environment Variables:
  SSH_KEY         Path to SSH identity file (default: $SSH_KEY)
  SSH_HOST        Remote VPS host or IP (default: $SSH_HOST)
  SSH_USER        Remote VPS user (default: $SSH_USER)
  REMOTE_DIR      Remote monorepo workspace directory (default: $REMOTE_DIR)
  REMOTE_WEB_DIR  Remote Nginx web root (default: $REMOTE_WEB_DIR)
  PUBLIC_URL      Production public URL for health check (default: $PUBLIC_URL)
EOF
}

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast)
            FAST_MODE=true
            SKIP_GATE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-gate)
            SKIP_GATE=true
            shift
            ;;
        --no-sync-db)
            SYNC_DB=false
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown argument '$1'" >&2
            usage
            exit 1
            ;;
    esac
done

echo "======================================================================"
echo "== VeriScholar 1-Click Remote VPS Rollout"
echo "== Target Host : $SSH_USER@$SSH_HOST"
echo "== Public URL  : $PUBLIC_URL"
echo "== Dry Run     : $DRY_RUN"
echo "======================================================================"

# 1. SSH Key Verification
if [[ ! -f "$SSH_KEY" ]]; then
    echo "Error: SSH key not found at '$SSH_KEY'" >&2
    exit 1
fi
chmod 400 "$SSH_KEY" 2>/dev/null || true

# 2. Remote Host Pre-flight Probe (Instant 1s Failover before any builds or tests)
if [[ "$DRY_RUN" != "true" ]]; then
    echo "-> Probing remote VPS reachability ($SSH_USER@$SSH_HOST:22)..."
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=1 -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$SSH_USER@$SSH_HOST" "true" 2>/dev/null; then
        echo "======================================================================"
        echo "⚠️ Remote VPS host ($SSH_USER@$SSH_HOST) is currently offline / unreachable."
        echo "-> Skipping remote deployment to save cloud computing costs."
        echo "======================================================================"
        exit 0
    fi
fi

# 3. Verification & Build
if [[ "$FAST_MODE" == "true" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "-> [Fast Mode] [DRY-RUN] Simulating frontend bundle build..."
    else
        echo "-> [Fast Mode] Rebuilding frontend bundle (skipping gates 1-3)..."
        npm --prefix apps/web run build
    fi
elif [[ "$SKIP_GATE" != "true" ]]; then
    echo "-> [Gate 1/4] Running Ruff linter & format check..."
    uv run ruff check .
    uv run ruff format --check .

    echo "-> [Gate 2/4] Running Backend pytest suite..."
    uv run pytest

    echo "-> [Gate 3/4] Running Frontend vitest suite..."
    npm --prefix apps/web run test

    echo "-> [Gate 4/4] Building Frontend bundle..."
    npm --prefix apps/web run build
else
    echo "-> [Gate Skipped] --skip-gate provided. Ensuring frontend dist exists..."
    if [[ ! -d "apps/web/dist" ]] && [[ "$DRY_RUN" != "true" ]]; then
        npm --prefix apps/web run build
    fi
fi

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY-RUN] Simulation completed. Deployment target would be: $PUBLIC_URL"
    exit 0
fi

# 3. Synchronize Web Distribution Bundle
echo "-> Synchronizing frontend distribution to $REMOTE_WEB_DIR..."
rsync -avz --delete \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new" \
    apps/web/dist/ "$SSH_USER@$SSH_HOST:$REMOTE_WEB_DIR/"

# 4. Synchronize Backend Monorepo Code
echo "-> Synchronizing backend workspace to $REMOTE_DIR..."
rsync -avz \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.venv' \
    --exclude='.env' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='apps/web/dist' \
    --exclude='apps/web/node_modules' \
    --exclude='.superpowers/sdd' \
    --exclude='temp' \
    --exclude='report-datn' \
    . "$SSH_USER@$SSH_HOST:$REMOTE_DIR/"

# 5. Remote Environment Sync & Schema Migrations
echo "-> Updating remote dependencies and ensuring schema migrations..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new "$SSH_USER@$SSH_HOST" bash <<REMOTE_SCRIPT
set -euo pipefail
export PATH="\$HOME/.local/bin:\$PATH"
cd "$REMOTE_DIR"
uv sync --all-packages --frozen
uv run python -m api.db.init_db
REMOTE_SCRIPT

# 6. Database Synchronization (Local Dev DB -> VPS)
if [[ "$SYNC_DB" == "true" ]]; then
    echo "-> Synchronizing local Dev PostgreSQL database to VPS container ($REMOTE_CONTAINER)..."
    uv run python scripts/sync_db_to_vps.py
fi

# 7. Remote Service Restart & Nginx Reload
echo "-> Restarting verischolar-api.service and reloading nginx..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new "$SSH_USER@$SSH_HOST" bash <<REMOTE_SCRIPT
set -euo pipefail
sudo systemctl restart verischolar-api.service
if command -v nginx >/dev/null 2>&1; then
    sudo systemctl reload nginx.service || true
fi
REMOTE_SCRIPT

# 8. Post-Deployment Live Verification Probe
echo "-> Probing live health check at $PUBLIC_URL/health..."
MAX_ATTEMPTS=10
ATTEMPT=1
HEALTH_STATUS="FAIL"

while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
    if HEALTH_STATUS=$(curl -fsS --max-time 10 "$PUBLIC_URL/health" 2>/dev/null); then
        if [[ "$HEALTH_STATUS" == *"ok"* ]]; then
            break
        fi
    fi
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS: Waiting for backend startup (2s)..."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

if [[ "$HEALTH_STATUS" == *"ok"* ]]; then
    echo "======================================================================"
    echo "🚀 Deployment Successful! Product is live at:"
    echo "   $PUBLIC_URL"
    echo "======================================================================"
else
    echo "Error: Post-deployment health check failed after $MAX_ATTEMPTS attempts." >&2
    exit 1
fi

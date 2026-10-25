#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DEPLOY_ROOT="${WEB_DEPLOY_ROOT:-/var/www/verischolar/web}"

echo "=== [VeriScholar Web Deploy] Building React 19 Production Bundle ==="
cd "$ROOT_DIR/apps/web"
pnpm install --frozen-lockfile
pnpm build

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    echo "=== [VeriScholar Web Deploy] DRY_RUN=true: Skipping copy to $WEB_DEPLOY_ROOT ==="
    exit 0
fi

if [[ -w "$(dirname "$WEB_DEPLOY_ROOT")" ]] || [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    mkdir -p "$WEB_DEPLOY_ROOT"
    cp -r "$ROOT_DIR/apps/web/dist/." "$WEB_DEPLOY_ROOT/"
    echo "=== [VeriScholar Web Deploy] Synced bundle to $WEB_DEPLOY_ROOT ==="
    if command -v nginx >/dev/null 2>&1; then
        nginx -t && systemctl reload nginx || true
    fi
else
    echo "=== [VeriScholar Web Deploy] Bundle ready at $ROOT_DIR/apps/web/dist (non-root mode) ==="
fi

#!/usr/bin/env bash
set -euo pipefail

# Determine script & repository directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== [1/6] Building Web Frontend (apps/web) ==="
cd "${REPO_ROOT}"
pnpm --dir apps/web build

echo "=== [2/6] Preparing /var/www/verischolar/web ==="
sudo mkdir -p /var/www/verischolar/web

echo "=== [3/6] Deploying static build artifacts ==="
sudo cp -r apps/web/dist/* /var/www/verischolar/web/

echo "=== [4/6] Setting ownership and permissions ==="
sudo chown -R VeriScholar:www-data /var/www/verischolar
sudo chmod -R 755 /var/www/verischolar

echo "=== [5/6] Configuring Nginx Site ==="
sudo cp "${REPO_ROOT}/deploy/nginx/verischolar.conf" /etc/nginx/sites-available/verischolar.conf
sudo ln -sf /etc/nginx/sites-available/verischolar.conf /etc/nginx/sites-enabled/verischolar.conf
if [ -L /etc/nginx/sites-enabled/default ] || [ -f /etc/nginx/sites-enabled/default ]; then
    echo "Removing default nginx site..."
    sudo rm -f /etc/nginx/sites-enabled/default
fi

echo "=== [6/6] Testing and reloading Nginx ==="
sudo nginx -t
sudo systemctl reload nginx

echo "=== Web deployment completed successfully! ==="

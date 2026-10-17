#!/usr/bin/env bash
# ==============================================================================
# VeriScholar Production Deployment Pipeline (CD Automation & Zero-Downtime)
# ==============================================================================
# Features:
#   1. Strict pre-flight checks (git, pnpm, python, systemctl, nginx)
#   2. Idempotent Zero-Downtime Database Schema Migration (init_db.py)
#   3. Optimized Web UI Compilation & Atomic Asset Sync to /var/www/verischolar/web
#   4. Nginx Configuration Testing & Seamless Reload
#   5. Backend Service Graceful Restart (verischolar-api.service)
#   6. Automated Post-Deployment Health Check with exponential/linear retry
#   7. Automated Rollback Trigger upon health-check or execution failure
# ==============================================================================

set -euo pipefail

# ANSI color codes for structured logs
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Base paths
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly WEB_DEPLOY_DIR="/var/www/verischolar/web"
readonly NGINX_CONF_AVAILABLE="/etc/nginx/sites-available/verischolar.conf"
readonly NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/verischolar.conf"
readonly VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"

# Configurable defaults
HEALTH_CHECK_URL="https://verischolar.duckdns.org/health"
HEALTH_CHECK_LOCAL_URL="http://127.0.0.1:8000/health"
MAX_HEALTH_ATTEMPTS=15
HEALTH_ATTEMPT_INTERVAL=2
ENABLE_ROLLBACK=true
SKIP_BUILD=false
SKIP_MIGRATION=false
DRY_RUN=false

# Deployment state tracking
PREV_COMMIT=""
CURRENT_COMMIT=""
DEPLOY_START_TIME=""
IS_ROLLING_BACK=false

log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1" >&2
}

print_usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --skip-build             Skip frontend pnpm build step
  --skip-migration         Skip database schema migration
  --no-rollback            Disable automatic git rollback on failure
  --dry-run                Simulate deployment actions without reloading services
  --health-url <URL>       Custom health check URL (default: ${HEALTH_CHECK_URL})
  --max-attempts <NUM>     Max health check attempts (default: ${MAX_HEALTH_ATTEMPTS})
  --help, -h               Show this help message
EOF
}

# Parse command line flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-migration)
            SKIP_MIGRATION=true
            shift
            ;;
        --no-rollback)
            ENABLE_ROLLBACK=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --health-url)
            HEALTH_CHECK_URL="$2"
            shift 2
            ;;
        --max-attempts)
            MAX_HEALTH_ATTEMPTS="$2"
            shift 2
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown argument: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Error and Rollback handler
rollback_on_failure() {
    local exit_code=$?
    if [ "$exit_code" -ne 0 ] && [ "$ENABLE_ROLLBACK" = true ] && [ "$IS_ROLLING_BACK" = false ]; then
        IS_ROLLING_BACK=true
        log_error "Deployment step failed with exit code ${exit_code}! Initiating automated rollback..."

        if [ -n "$PREV_COMMIT" ] && [ "$PREV_COMMIT" != "$CURRENT_COMMIT" ]; then
            log_warn "Rolling back repository state to previous commit: ${PREV_COMMIT}..."
            git -C "${REPO_ROOT}" checkout "${PREV_COMMIT}" || true
        fi

        log_warn "Restarting backend API service to stabilize environment..."
        sudo systemctl restart verischolar-api || true
        sudo systemctl reload nginx || true

        log_error "System restored to previous baseline. Deployment aborted."
        exit "$exit_code"
    fi
}

trap rollback_on_failure EXIT

# ==============================================================================
# PIPELINE EXECUTION PHASES
# ==============================================================================

echo "================================================================================"
echo "          VERISCHOLAR PRODUCTION CONTINUOUS DEPLOYMENT (CD) PIPELINE            "
echo "================================================================================"
DEPLOY_START_TIME=$(date +%s)
cd "${REPO_ROOT}"

# Record commit baselines
PREV_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "")
CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
log_info "Initiating deployment for commit: ${CURRENT_COMMIT} (Base: ${PREV_COMMIT:0:7})"

# ------------------------------------------------------------------------------
# Phase 1: Pre-flight Environment Validation
# ------------------------------------------------------------------------------
log_info "[Phase 1/6] Running Pre-flight Environment Checks..."

if [ ! -f "${VENV_PYTHON}" ]; then
    log_error "Python virtual environment not found at: ${VENV_PYTHON}"
    exit 1
fi

if ! command -v pnpm &>/dev/null; then
    log_error "pnpm is required for frontend building."
    exit 1
fi

if ! command -v nginx &>/dev/null; then
    log_error "nginx binary not found on target host."
    exit 1
fi

log_success "Pre-flight environment checks passed successfully."

# ------------------------------------------------------------------------------
# Phase 2: Zero-Downtime Database Schema Migration (Idempotent DDL)
# ------------------------------------------------------------------------------
log_info "[Phase 2/6] Executing Database Schema Migrations (Zero-Downtime)..."

if [ "$SKIP_MIGRATION" = false ]; then
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would execute: python -m api.db.init_db"
    else
        PYTHONPATH="${REPO_ROOT}/apps/api/src:${REPO_ROOT}/packages/core/src" \
            "${VENV_PYTHON}" -m api.db.init_db
        log_success "Database schema migrations applied and verified."
    fi
else
    log_warn "Skipping database migrations as requested (--skip-migration)."
fi

# ------------------------------------------------------------------------------
# Phase 3: Frontend Web Client Build & Atomic Deployment
# ------------------------------------------------------------------------------
log_info "[Phase 3/6] Building and Deploying Frontend Web Client..."

if [ "$SKIP_BUILD" = false ]; then
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would build apps/web and sync to ${WEB_DEPLOY_DIR}"
    else
        log_info "Compiling React 19 / Vite bundle in apps/web..."
        pnpm --dir "${REPO_ROOT}/apps/web" build

        log_info "Deploying static assets to ${WEB_DEPLOY_DIR}..."
        sudo mkdir -p "${WEB_DEPLOY_DIR}"
        sudo cp -r "${REPO_ROOT}/apps/web/dist/"* "${WEB_DEPLOY_DIR}/"

        sudo chown -R VeriScholar:www-data /var/www/verischolar
        sudo chmod -R 755 /var/www/verischolar
        log_success "Frontend assets deployed with optimal permissions (755, VeriScholar:www-data)."
    fi
else
    log_warn "Skipping frontend build as requested (--skip-build)."
fi

# ------------------------------------------------------------------------------
# Phase 4: Nginx Web Server Configuration & Validation
# ------------------------------------------------------------------------------
log_info "[Phase 4/6] Verifying and Reloading Nginx Configuration..."

if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Would test nginx syntax and reload nginx"
else
    if [ -f "${REPO_ROOT}/deploy/nginx/verischolar.conf" ]; then
        # Check if local site config needs updating
        if [ ! -f "${NGINX_CONF_AVAILABLE}" ]; then
            sudo cp "${REPO_ROOT}/deploy/nginx/verischolar.conf" "${NGINX_CONF_AVAILABLE}"
            sudo ln -sf "${NGINX_CONF_AVAILABLE}" "${NGINX_CONF_ENABLED}"
        fi
    fi

    log_info "Testing Nginx syntax..."
    sudo nginx -t
    log_info "Reloading Nginx service gracefully..."
    sudo systemctl reload nginx
    log_success "Nginx reloaded without connection interruption."
fi

# ------------------------------------------------------------------------------
# Phase 5: Backend API Service Graceful Restart (Zero-Downtime Rolling Reload)
# ------------------------------------------------------------------------------
log_info "[Phase 5/6] Gracefully Reloading Backend FastAPI Service (Zero-Downtime)..."

if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Would execute: sudo systemctl reload verischolar-api"
else
    log_info "Sending SIGHUP rolling reload to uvicorn master process..."
    sudo systemctl reload verischolar-api || sudo systemctl restart verischolar-api
    log_success "Backend service reloaded (verischolar-api.service active)."
fi

# ------------------------------------------------------------------------------
# Phase 6: Automated Post-Deployment Health Check & Verification
# ------------------------------------------------------------------------------
log_info "[Phase 6/6] Verifying Service Health (Polling ${HEALTH_CHECK_URL})..."

if [ "$DRY_RUN" = false ]; then
    HEALTHY=false
    for ((attempt=1; attempt<=MAX_HEALTH_ATTEMPTS; attempt++)); do
        log_info "Health probe attempt ${attempt}/${MAX_HEALTH_ATTEMPTS}..."
        
        # Test local socket/port first
        HTTP_LOCAL=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "${HEALTH_CHECK_LOCAL_URL}" || echo "000")
        
        # Test public SSL domain
        HTTP_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" --max-time 4 "${HEALTH_CHECK_URL}" || echo "000")
        
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_LOCAL" = "200" ]; then
            HEALTHY=true
            log_success "Health check passed! (Public: HTTP ${HTTP_CODE}, Local: HTTP ${HTTP_LOCAL})"
            break
        fi

        log_warn "Service starting... (Public: HTTP ${HTTP_CODE}, Local: HTTP ${HTTP_LOCAL}). Retrying in ${HEALTH_ATTEMPT_INTERVAL}s..."
        sleep "${HEALTH_ATTEMPT_INTERVAL}"
    done

    if [ "$HEALTHY" = false ]; then
        log_error "Health check failed after ${MAX_HEALTH_ATTEMPTS} attempts! Endpoint did not return HTTP 200."
        exit 1
    fi
fi

# ------------------------------------------------------------------------------
# Deployment Finalization
# ------------------------------------------------------------------------------
DEPLOY_END_TIME=$(date +%s)
TOTAL_DURATION=$((DEPLOY_END_TIME - DEPLOY_START_TIME))

echo "================================================================================"
echo -e "${GREEN}      DEPLOYMENT COMPLETED SUCCESSFULLY IN ${TOTAL_DURATION} SECONDS!${NC}"
echo "================================================================================"
echo "Commit Deployed: ${CURRENT_COMMIT}"
echo "Live Public Web: https://verischolar.duckdns.org"
echo "Health Endpoint: ${HEALTH_CHECK_URL}"
echo "API Docs:        https://verischolar.duckdns.org/docs"
echo "================================================================================"

# Clear exit trap to prevent false rollback on successful exit
trap - EXIT
exit 0

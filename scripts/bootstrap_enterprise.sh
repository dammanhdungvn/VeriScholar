#!/usr/bin/env bash
# ==============================================================================
# VeriScholar Enterprise On-Premise Single-Command Bootstrap Installer (Pillar 5)
# Target: Production Linux Server (Ubuntu/Debian/RHEL/CentOS)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/deploy/docker-compose.enterprise.yml"
ENV_FILE="${ROOT_DIR}/deploy/.env.enterprise"

echo "================================================================================"
echo "      VERISCHOLAR ENTERPRISE ON-PREMISE BOOTSTRAP INSTALLER (PILLAR 5)          "
echo "================================================================================"

# 1. Check prerequisites
echo "[1/5] Checking environment prerequisites..."
if ! command -v docker &>/dev/null; then
    echo "[-] Error: Docker engine is not installed. Please install Docker." >&2
    exit 1
fi

COMPOSE_CMD=""
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "[-] Error: Docker Compose is required." >&2
    exit 1
fi
echo "[+] Docker & ${COMPOSE_CMD} detected."

# 2. Generate secure enterprise environment variables
echo "[2/5] Initializing secure enterprise secrets..."
if [ ! -f "${ENV_FILE}" ]; then
    RANDOM_PG_PASS=$(openssl rand -hex 16 2>/dev/null || date +%s%N | sha256sum | head -c 32)
    RANDOM_JWT_SEC=$(openssl rand -hex 32 2>/dev/null || date +%s%N | sha256sum | head -c 64)
    cat <<EOF > "${ENV_FILE}"
# VeriScholar Enterprise Environment Configuration
APP_ENV=production
HTTP_PORT=80
HTTPS_PORT=443
POSTGRES_DB=verischolar
POSTGRES_USER=verischolar
POSTGRES_PASSWORD=${RANDOM_PG_PASS}
JWT_SECRET=${RANDOM_JWT_SEC}
REDIS_URL=redis://redis:6379/0
ARQ_REDIS_SETTINGS=redis://redis:6379/1
EOF
    chmod 600 "${ENV_FILE}"
    echo "[+] Generated new secure enterprise configuration at: ${ENV_FILE}"
else
    echo "[+] Reusing existing enterprise configuration at: ${ENV_FILE}"
fi

# 3. Validate Docker Compose configuration
echo "[3/5] Validating Enterprise Stack syntax..."
${COMPOSE_CMD} --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config >/dev/null
echo "[+] Docker Compose configuration validated successfully."

# 4. Display service topology
echo "[4/5] Enterprise Architecture Topology:"
echo "    - Web Gateway:        Nginx Reverse Proxy & React 19 SPA (:80, :443)"
echo "    - Application Core:   FastAPI Uvicorn AsyncIO Cluster"
echo "    - Connection Pooler:  PgBouncer (Transaction Pooling up to 5,000 clients)"
echo "    - Database:           PostgreSQL 16 + pgvector (Semantic Embeddings)"
echo "    - Cache & Broker:     Redis 7.2 (Memory Cache & ARQ Message Queue)"
echo "    - Async Workers:      ARQ Worker Cluster (PDF, OCR, DeBERTa NLI, LaTeX)"

# 5. Ready notification & optional launch
echo "[5/5] Bootstrap validation complete!"
echo "================================================================================"
echo "[SUCCESS] VeriScholar Enterprise Stack is ready for deployment."
echo "To launch in production background:"
echo "    ${COMPOSE_CMD} --env-file ${ENV_FILE} -f ${COMPOSE_FILE} up -d"
echo "================================================================================"

if [[ "${1:-}" == "--start" ]]; then
    echo "[+] Launching enterprise stack..."
    ${COMPOSE_CMD} --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d
    echo "[+] Waiting for PostgreSQL cluster via pg_isready..."
    for i in {1..30}; do
        if ${COMPOSE_CMD} --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U verischolar -d verischolar >/dev/null 2>&1; then
            echo "[+] Database is healthy and ready for queries!"
            break
        fi
        sleep 1
    done
fi


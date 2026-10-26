# VPS Deployment Automation Design

> **Document Class:** Technical Specification & Operational Runbook  
> **Status:** Approved  
> **Target Production URL:** [https://verischolar.duckdns.org](https://verischolar.duckdns.org)

---

## 1. Context & Motivation
VeriScholar requires an automated, single-command deployment mechanism to deploy new features and bugfixes directly from the development workspace to the production UAT VPS. The process must guarantee zero regressions, avoid overwriting persistent databases or environment secrets, and ensure immediate availability for manual visual and functional verification.

---

## 2. Infrastructure Architecture & State
- **VPS Host:** `48.193.46.15` (domain: `verischolar.duckdns.org`).
- **Authentication:** SSH Key (`/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem`) for user `VeriScholar`.
- **Database & Cache:** PostgreSQL 16+ with `pgvector` (`verischolar-postgres-dev`) and Redis 7 (`verischolar-redis`) managed via Docker containers.
- **Frontend Delivery:** Static assets served by Nginx from `/var/www/verischolar/web`.
- **Backend API Service:** FastAPI application managed by `verischolar-api.service` via systemd (`127.0.0.1:8000`).

---

## 3. Deployment Flow (Local Build & Sync)
1. **Safety Gate Verification:** Run local verification gates (Ruff linter/formatter, Pytest, frontend Vitest, Vite production build).
2. **Frontend Asset Delivery:** Sync pre-built static bundle (`apps/web/dist/`) to `/var/www/verischolar/web/` using `rsync` with `--delete`.
3. **Backend Monorepo Sync:** Sync core packages and API code to `/home/VeriScholar/Workspace/VeriScholar/`, strictly excluding `.git`, `node_modules`, `.venv`, and `.env`.
4. **Service Restart & Dependency Sync:** Remotely execute `uv sync --all-packages --frozen` and restart `verischolar-api.service`.
5. **Post-Deployment Health Probe:** Send an automated HTTPS probe to `https://verischolar.duckdns.org/health` and verify HTTP 200 `{"status":"ok","service":"verischolar-api"}`.

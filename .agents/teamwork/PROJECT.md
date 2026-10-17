# Project: VeriScholar Enterprise CI/CD Upgrade (100/100)

## Architecture
- **Continuous Integration (CI)**: GitHub Actions workflow `.github/workflows/ci.yml` orchestrating:
  - `backend-checks`: Pytest, linting, type checks.
  - `frontend-checks`: Vitest suite (378 tests across 63 files with optimized `vmThreads`), TypeScript checks, linting, JUnit XML generation, PR merge gating.
  - `docker-validation`: AST validation of `deploy/docker-compose.enterprise.yml` and parallel Buildx builds of `deploy/Dockerfile.api` and `deploy/Dockerfile.web` with GHA caching.
- **Continuous Deployment (CD)**: Automated deployment script `scripts/deploy_production.sh` and workflow `.github/workflows/cd.yml`:
  - Zero-downtime database migration via idempotent DDL (`apps/api/src/api/db/init_db.py`).
  - Rolling process reload via `systemctl reload verischolar-api` (SIGHUP rolling worker restart without socket unbinding).
  - Atomic static web frontend deployment to `/var/www/verischolar/web`.
  - 30-second automated health polling against `https://verischolar.duckdns.org/health`.
  - Automatic rollback to prior commit on health failure.
- **Verification & Certification**: Architecture audit, simulated failure recovery tests, execution timing benchmark (< 5 min), formal Quality Gate certification.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Frontend Vitest Quality Gate | Run full Vitest suite in CI with JUnit XML reporter, vmThreads pool optimization, and fail PRs on any failure | M1 | ORIGINAL_REQUEST § R1 |
| 2 | Docker Compose & Container CI Gate | Dual-mode AST validation of docker-compose.enterprise.yml, setuptools fix for Dockerfile.api, root .dockerignore, Buildx GHA cache | M2 | ORIGINAL_REQUEST § R2 |
| 3 | Zero-Downtime CD & Auto-Rollback | Production deploy script, SIGHUP rolling reload, idempotent DB migration, 30s duckdns healthcheck, auto-rollback | M3 | ORIGINAL_REQUEST § R3 |
| 4 | Architecture Audit & Certification | YAML syntax audit, fault injection simulations, pipeline benchmark < 5m, Quality Gate Pass certification | M4 | ORIGINAL_REQUEST § R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Frontend Vitest Quality Gate | `apps/web/vite.config.ts`, `.github/workflows/ci.yml` (frontend-checks) | none | DONE |
| 2 | M2: Docker & Container CI Gate | `pyproject.toml`, `.dockerignore`, `.github/workflows/ci.yml` (docker-validation) | none | DONE |
| 3 | M3: Zero-Downtime CD Pipeline | `scripts/deploy_production.sh`, `deploy/nginx/production-host.conf`, `.github/workflows/cd.yml` | M1, M2 | DONE |
| 4 | M4: Architecture Audit & Certification | E2E verification, fault injection, timing benchmarks, certification | M1, M2, M3 | DONE |

## Interface Contracts
### CI Workflow <-> Test Runners
- Frontend tests executed via `pnpm test:run --reporter=default --reporter=junit --outputFile=test-results.xml` in `apps/web`.
- Exit code `0` indicates 100% pass (378/378 tests). Exit code `1` fails the CI check and blocks PR merge.
- JUnit artifact uploaded via `actions/upload-artifact@v4` with `path: apps/web/test-results.xml` and `if: always()`.
- Verified in M1: 378/378 tests pass in 37.96s, valid JUnit XML.

### Docker CI <-> Build Infrastructure
- Compose syntax validated via `docker compose -f deploy/docker-compose.enterprise.yml config -q`.
- Setuptools flat layout resolved via `[tool.setuptools] packages = []` in root `pyproject.toml`.
- Buildx uses `type=gha,scope=api,mode=max` and `type=gha,scope=web,mode=max`.

### CD Pipeline <-> Production Runtime
- Migration: `uv run python -m api.db.init_db` (idempotent DDL, advisory lock 88991122).
- API reload: `sudo systemctl reload verischolar-api` (sends SIGHUP to uvicorn master process).
- Health check: Poll `https://verischolar.duckdns.org/health` up to 30s. If HTTP 200 received, deploy succeeded. If not within 30s, execute rollback.

## Code Layout
- `.github/workflows/ci.yml`: CI Quality Gates (backend, frontend, docker)
- `.github/workflows/cd.yml`: CD Pipeline
- `apps/web/vite.config.ts`: Vitest configuration (pool: vmThreads, JUnit reporter)
- `pyproject.toml`: Root package definition (setuptools package whitelist)
- `.dockerignore`: Root build context exclusion
- `scripts/deploy_production.sh`: Automated production deployment with auto-rollback
- `deploy/nginx/production-host.conf`: Host SSL Nginx configuration template

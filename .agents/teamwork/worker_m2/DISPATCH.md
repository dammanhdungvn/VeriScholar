# Task Assignment: Worker M2 (Docker Infrastructure & Container CI Gate)

## Identity
- Role: Worker (Docker CI Implementation)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2
- Exclusive Write Ownership: `pyproject.toml`, `.dockerignore`, `.github/workflows/ci.yml` (docker-validation job and related filters)

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/survey_report.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/handoff.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objective
Implement Requirement R2:
1. In root `pyproject.toml`:
   - Add:
     ```toml
     [tool.setuptools]
     packages = []
     ```
     This resolves the flat-layout discovery error where setuptools aborts because both `apps` and `packages` exist at the top level.
2. In root `.dockerignore`:
   - Create comprehensive root `.dockerignore` excluding `node_modules`, `apps/web/node_modules`, `.venv`, `.git`, `.agents`, `dist`, `__pycache__`, `*.pyc`, `data/`, `tests/` etc.
   - This eliminates the 318MB build context transfer observed during survey, reducing transfer time from 25.6s to <0.5s.
3. In `.github/workflows/ci.yml`:
   - In `detect-changes` job: ensure changes to `deploy/**`, `Dockerfile*`, and `.dockerignore` trigger `docker-validation`.
   - In `docker-validation` job:
     - Run dual-mode offline compose config validation:
       ```bash
       docker compose -f deploy/docker-compose.enterprise.yml config -q
       docker compose --env-file deploy/.env.enterprise -f deploy/docker-compose.enterprise.yml config -q
       ```
     - Set up Docker Buildx with `docker/setup-buildx-action@v3`.
     - Configure Docker Buildx caching for `verischolar-api` build using:
       `cache-from: type=gha,scope=api`
       `cache-to: type=gha,mode=max,scope=api`
     - Configure Docker Buildx caching for `verischolar-web` build using:
       `cache-from: type=gha,scope=web`
       `cache-to: type=gha,mode=max,scope=web`
     - Verify both builds run `docker/build-push-action@v6` with `push: false`.
4. Verification:
   - Run both offline docker compose config commands.
   - Run `docker build -f deploy/Dockerfile.web .` and verify context transfer is < 1MB and build succeeds (exit code 0).
   - Run `docker build -f deploy/Dockerfile.api .` and verify build succeeds through step 7/7 (`pip install .`) with exit code 0.
   - Validate YAML syntax of `.github/workflows/ci.yml`.
5. Document all changes and outputs in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md`.


## 2026-10-17T04:30:43Z
From: 037f66b3-4056-4a88-a7ee-29473f69a483
You are worker_m2.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2.
Your assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2/DISPATCH.md.

MANDATORY READING:
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/survey_report.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Task:
Implement Requirement R2 (Docker Infrastructure & Container CI Gate):
1. In `pyproject.toml`: Add `[tool.setuptools] packages = []` to fix setuptools flat-layout discovery error.
2. In `.dockerignore`: Create root `.dockerignore` to exclude node_modules, .venv, .git, etc., slashing context transfer from 318MB to <1MB.
3. In `.github/workflows/ci.yml`:
   - Ensure changes to `deploy/**`, `Dockerfile*`, `.dockerignore` trigger `docker-validation`.
   - Update `docker-validation` job:
     - Run dual-mode offline compose config validation (defaults and .env.enterprise).
     - Setup Docker Buildx.
     - Add Buildx caching `type=gha,mode=max,scope=api` and `type=gha,mode=max,scope=web`.
     - Build both images (`deploy/Dockerfile.api` and `deploy/Dockerfile.web`) with `push: false`.
4. Verification:
   - Run both offline compose config commands.
   - Run `docker build -f deploy/Dockerfile.web .` (confirm exit code 0 and context < 1MB).
   - Run `docker build -f deploy/Dockerfile.api .` (confirm exit code 0).
   - Validate YAML syntax of `.github/workflows/ci.yml`.
5. Deliver your report in `handoff.md` and send a completion message.

## 2026-10-16T13:22:04Z
You are Worker M2 for Milestone 2 (M2_ENTERPRISE_AND_BASELINE).
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2.

Read:
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/explorer_survey_pillar5_tests/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Tasks:
1. Pillar 5 Enterprise Stack:
   - In `deploy/docker-compose.enterprise.yml`:
     - Remove obsolete `version: "3.9"`.
     - In `postgres` service: mount `./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro` so pgvector and uuid extensions initialize on startup.
     - In `postgres` service: change image to `pgvector/pgvector:0.8.0-pg16` (or `pgvector/pgvector:pg16`) to strictly match the PostgreSQL 16 specification in PRD §R4.
   - In `deploy/nginx/verischolar.conf`:
     - Set web root to `root /usr/share/nginx/html;` (matching `deploy/Dockerfile.web` build output).
     - Update all proxy passes from `proxy_pass http://127.0.0.1:8000;` to `proxy_pass http://api:8000;` (connecting to `verischolar-enterprise-api` container in docker network).
   - In `pyproject.toml`:
     - Add `"arq>=0.26.0"` to main dependencies so `deploy/Dockerfile.api` installs the `arq` CLI required by `arq-worker`.
   - In `scripts/bootstrap_enterprise.sh`:
     - Verify dry-run execution: `bash scripts/bootstrap_enterprise.sh` exits cleanly with code 0.
2. Baseline Test Harmonization:
   - In `packages/core/src/core/services/exa_resolver.py:133`:
     Change `self.api_key = api_key or os.getenv("EXA_API_KEY", "")` to:
     `self.api_key = api_key if api_key is not None else os.getenv("EXA_API_KEY", "")`
     so that unit tests passing `api_key=""` never leak environment secrets or trigger live HTTP requests to `api.exa.ai`.
   - In `packages/core/src/core/services/latex_healer.py` and `packages/core/src/core/services/latex_linter.py` and `scripts/benchmark_multi_agent_stress.py`:
     Fix the 12 ruff formatting and linting errors (E501 line length, E741 ambiguous variable name `l`, unused imports/variables) so that `uv run ruff check .` and `uv run ruff format --check .` exit cleanly with zero errors.

File Ownership:
- `deploy/docker-compose.enterprise.yml`
- `deploy/nginx/verischolar.conf`
- `pyproject.toml`
- `scripts/bootstrap_enterprise.sh`
- `packages/core/src/core/services/exa_resolver.py`
- `packages/core/src/core/services/latex_healer.py`
- `packages/core/src/core/services/latex_linter.py`
- `scripts/benchmark_multi_agent_stress.py`

Required Verifications:
- `docker compose --env-file deploy/.env.enterprise -f deploy/docker-compose.enterprise.yml config` (exit code 0)
- `bash scripts/bootstrap_enterprise.sh` (exit code 0)
- `uv run pytest packages/core/tests/services/test_exa_resolver.py -v` (all pass)
- `uv run ruff check packages/core scripts/ deploy/` (0 errors)
- `uv run ruff format --check packages/core scripts/` (0 errors)

Write your complete handoff report to:
/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md
Report via send_message to your caller.

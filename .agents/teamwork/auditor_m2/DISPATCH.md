# Dispatch — Forensic Auditor (Milestone 2)

Scope: Forensic integrity audit of Milestone 2 deliverables.
Verify:
1. Docker Compose mounts genuine `init.sql` and uses `pgvector:0.8.0-pg16`.
2. Nginx routes genuinely proxy to `http://api:8000;` and serve from `/usr/share/nginx/html`.
3. `pyproject.toml` contains `arq>=0.26.0`.
4. `exa_resolver.py` strictly isolates in-memory tests when `api_key=""`.
5. No fake mock scripts or fabricated outputs.

Worker handoff: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md`
Output: `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m2/handoff.md`
Report verdict: CLEAN or INTEGRITY VIOLATION.

## 2026-10-16T13:29:45Z
You are the Forensic Auditor for Milestone 2 (M2_ENTERPRISE_AND_BASELINE).
Your working directory is: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m2.

Read:
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md (specifically section ## 2026-10-16T12:03:58Z)
- /home/VeriScholar/Workspace/VeriScholar/AGENTS.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md
- /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m2/DISPATCH.md

Execute a comprehensive forensic integrity audit on Milestone 2 deliverables:
1. Static Analysis:
   - Check `deploy/docker-compose.enterprise.yml`: confirm genuine init.sql mount and `pgvector:0.8.0-pg16` image tag.
   - Check `deploy/nginx/verischolar.conf`: confirm genuine `root /usr/share/nginx/html;` and `proxy_pass http://api:8000;`.
   - Check `pyproject.toml`: confirm `"arq>=0.26.0"`.
   - Check `packages/core/src/core/services/exa_resolver.py:133`: confirm `api_key if api_key is not None else os.getenv(...)`.
2. Runtime & Configuration Execution:
   - Verify `docker compose --env-file deploy/.env.enterprise -f deploy/docker-compose.enterprise.yml config` passes with code 0.
   - Verify `bash scripts/bootstrap_enterprise.sh` executes with code 0.
   - Verify `uv run pytest packages/core/tests/services/test_exa_resolver.py -v` passes with code 0.
   - Verify `uv run ruff check packages/core scripts/ deploy/` exits with 0 errors.

Write your audit report to:
/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/auditor_m2/handoff.md
State your verdict: CLEAN or INTEGRITY VIOLATION.
Report via send_message to your caller.

---
name: runtime-diagnostics
description: Deep runtime inspection and live diagnostic workflows for AI Agents in VeriScholar. Use to check if services (FastAPI, PostgreSQL, Redis, Nginx) are running, inspect live database state & schema, check Redis cache & ARQ queues, measure API TTFB, read journalctl logs, and inspect GitHub CI/CD failures via gh CLI.
metadata:
  origin: VeriScholar CTO Office
tools: Read, Write, Edit, Bash, Grep, Glob
---

# VeriScholar Runtime Diagnostics & Live Introspection Skill

This skill teaches AI agents how to inspect the live running state of VeriScholar rather than blindly inferring behavior from static code.

---

## 1. When to Activate

- Verifying whether the application or services are currently running.
- Investigating bug reports, latency spikes, or 502/500 errors.
- Inspecting live database tables, record counts, migrations, or pgvector indexes.
- Inspecting Redis keys, cache hits/misses, or ARQ worker job queues.
- Reading live systemd service logs (`journalctl -u verischolar-api.service`).
- Checking why a GitHub Pull Request CI run failed (`gh run view --log-failed`).
- Verifying deployments after restarting services or merging code.

---

## 2. Available Inspection Interfaces

### 2.1. Via MCP Server (`verischolar-runtime`)
If MCP is active in your agent session, you have direct access to these tools:
- `check_services_health()`: Returns systemd active state, listening ports, load average, and RAM.
- `query_database_readonly(sql="summary")`: Safe read-only SQL queries or table summary counts.
- `inspect_redis()`: Live ping, memory usage, key count, and cached synthesis keys.
- `probe_api(path="/health", host="http://127.0.0.1:8000")`: Live HTTP request with TTFB in ms.
- `read_service_logs(service="api", lines=50)`: Live journalctl logs from FastAPI or Nginx.
- `inspect_github_ci_status(pr_number=0)`: CI/CD check status and error traces from failed jobs.

### 2.2. Via Direct CLI Commands (Bash Fallback)
If MCP tools are not directly loaded in the current subagent subshell, use these commands:

#### Service Health & Ports:
```bash
systemctl is-active verischolar-api.service nginx
ss -tulpn | grep -E "8000|5432|6379|80|443"
curl -s -i http://127.0.0.1:8000/health
```

#### Live Database Inspection:
```bash
uv run python -c "
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect('postgresql://verischolar:verischolar@localhost:5432/verischolar')
    print('Users:', await conn.fetchval('SELECT count(*) FROM users'))
    print('Documents:', await conn.fetchval('SELECT count(*) FROM documents'))
    print('Drafts:', await conn.fetchval('SELECT count(*) FROM drafts'))
    await conn.close()
asyncio.run(check())
"
```

#### Live Redis Inspection:
```bash
uv run python -c "
import asyncio, redis.asyncio as aioredis
async def check():
    r = aioredis.from_url('redis://localhost:6379/0')
    print('Ping:', await r.ping())
    print('Keys:', len(await r.keys('*')))
    await r.aclose()
asyncio.run(check())
"
```

#### Live Service Logs:
```bash
journalctl -u verischolar-api.service -n 50 --no-pager
tail -n 30 /var/log/nginx/error.log
```

#### GitHub CI/CD Diagnostics (Authenticated via `gh`):
```bash
# View open PRs
gh pr list

# View checks on active PR
gh pr view 44 --json statusCheckRollup

# View recent runs
gh run list -L 5

# View the exact failed logs of a run
gh run view <RUN_ID> --log-failed
```

---

## 3. Mandatory Agent Behavior (Anti-Guessing Rule)

1. **Never guess whether code runs:** Always verify by probing the endpoint or querying the database.
2. **Never assume CI failed without looking at the log:** Run `gh run view <RUN_ID> --log-failed` to see the exact assertion or stack trace.
3. **Always check service health after restart:** If you restart `verischolar-api`, verify with `curl -s http://127.0.0.1:8000/health` that it returned HTTP 200 within 15 seconds.

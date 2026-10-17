"""VeriScholar Runtime Diagnostics MCP Server.

Provides deep runtime inspection tools for AI Agents:
- Live service health (FastAPI, Nginx, PostgreSQL, Redis, PgBouncer)
- Read-only database introspection (schemas, tables, row counts, pgvector status)
- Live Redis caching & ARQ worker queue status
- API endpoint latency & response probing (TTFB, /health, /api/v1)
- Live systemd journalctl & Nginx logs stream
- GitHub CLI CI/CD inspection (failed job logs, PR status, workflow runs)
"""

import asyncio
import json
import os
import re
import subprocess
import time
from typing import Any, Dict, List, Optional

import asyncpg
import httpx
from mcp.server.mcpserver import MCPServer
import redis.asyncio as aioredis

# Initialize MCP Server
server = MCPServer("verischolar-runtime-diagnostics")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://verischolar:verischolar@localhost:5432/verischolar",
).replace("postgresql+asyncpg://", "postgresql://")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@server.tool()
async def check_services_health() -> str:
    """Inspect the live operational status of all VeriScholar system services,

    ports, CPU, memory, and disk space.
    """
    results: Dict[str, Any] = {}

    # 1. Systemd Service status
    services = [
        "verischolar-api.service",
        "nginx.service",
        "redis-server.service",
        "postgresql.service",
    ]
    service_status = {}
    for svc in services:
        try:
            cmd = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True,
                text=True,
                timeout=3,
            )
            service_status[svc] = cmd.stdout.strip()
        except Exception as e:
            service_status[svc] = f"error: {str(e)}"
    results["services"] = service_status

    # 2. Listening Ports Check
    try:
        ss_cmd = subprocess.run(
            ["ss", "-tulpn"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        listening_ports = []
        for port in [8000, 5432, 6379, 6432, 80, 443]:
            if f":{port} " in ss_cmd.stdout or f":{port}\n" in ss_cmd.stdout:
                listening_ports.append(port)
        results["active_listening_ports"] = listening_ports
    except Exception as e:
        results["active_listening_ports"] = f"error: {str(e)}"

    # 3. System Load & Memory
    try:
        with open("/proc/loadavg", "r") as f:
            results["load_average"] = f.read().strip()
    except Exception:
        results["load_average"] = "unknown"

    try:
        free_cmd = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        results["memory_mb"] = free_cmd.stdout.strip().split("\n")[1]
    except Exception:
        results["memory_mb"] = "unknown"

    return json.dumps(results, indent=2)


@server.tool()
async def query_database_readonly(sql: str = "summary") -> str:
    """Run a safe read-only query on PostgreSQL or get table summary counts.

    Arguments:
        sql: SQL query to run (must be SELECT) or 'summary' to inspect all core tables.
    """
    clean_sql = sql.strip()

    if clean_sql.lower() in ("summary", "counts"):
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            tables = [
                "users",
                "documents",
                "document_chunks",
                "research_notes",
                "drafts",
                "research_sessions",
                "folders",
                "citation_edges",
                "reference_items",
            ]
            counts = {}
            for t in tables:
                try:
                    cnt = await conn.fetchval(f"SELECT count(*) FROM {t}")
                    counts[t] = cnt
                except Exception as ex:
                    counts[t] = f"table_not_found_or_error: {str(ex)}"

            # Also check pgvector
            vector_ext = await conn.fetchval(
                "SELECT count(*) FROM pg_extension WHERE extname = 'vector'"
            )
            counts["pgvector_installed"] = bool(vector_ext)

            await conn.close()
            return json.dumps({"database_summary": counts}, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to connect to database: {str(e)}"}, indent=2)

    # Safety Guard: strictly allow only SELECT statements
    dangerous_keywords = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant"]
    first_word = clean_sql.split()[0].lower() if clean_sql else ""
    if first_word != "select":
        return json.dumps(
            {"error": "Safety violation: Only SELECT queries are permitted in read-only diagnostics."},
            indent=2,
        )
    for kw in dangerous_keywords:
        if re.search(rf"\b{kw}\b", clean_sql, re.IGNORECASE):
            return json.dumps(
                {"error": f"Safety violation: Keyword '{kw}' forbidden in read-only diagnostics."},
                indent=2,
            )

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Cap at 50 rows
        if "limit" not in clean_sql.lower():
            clean_sql += " LIMIT 50"
        rows = await conn.fetch(clean_sql)
        await conn.close()

        records = [dict(r) for r in rows]
        # Serialize datetime / uuid / bytes
        def default_serializer(obj: Any) -> Any:
            return str(obj)

        return json.dumps({"row_count": len(records), "data": records}, default=default_serializer, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Query failed: {str(e)}"}, indent=2)


@server.tool()
async def inspect_redis() -> str:
    """Inspect live Redis server health, memory, keys, and ARQ queue tasks."""
    try:
        r = aioredis.from_url(REDIS_URL, decode_responses=True)
        pong = await r.ping()
        info = await r.info()
        keys_sample = await r.keys("*")
        await r.aclose()

        return json.dumps(
            {
                "ping": pong,
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys_count": len(keys_sample),
                "keys_sample": keys_sample[:25],
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to connect to Redis: {str(e)}"}, indent=2)


@server.tool()
async def probe_api(path: str = "/health", host: str = "http://127.0.0.1:8000") -> str:
    """Probe an API endpoint live to measure response time (TTFB), status code,

    and response body payload.

    Arguments:
        path: API path (e.g., '/health', '/api/v1/documents')
        host: Host URL ('http://127.0.0.1:8000' or 'https://verischolar.duckdns.org')
    """
    url = f"{host.rstrip('/')}/{path.lstrip('/')}"
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.get(url)
            ttfb_ms = round((time.perf_counter() - t0) * 1000, 2)
            try:
                body_json = resp.json()
            except Exception:
                body_json = resp.text[:500]

            return json.dumps(
                {
                    "url": url,
                    "status_code": resp.status_code,
                    "ttfb_ms": ttfb_ms,
                    "headers": {k: v for k, v in resp.headers.items() if k.lower() in ["content-type", "server", "x-request-id"]},
                    "body": body_json,
                },
                indent=2,
            )
    except Exception as e:
        return json.dumps({"url": url, "error": str(e), "duration_ms": round((time.perf_counter() - t0) * 1000, 2)}, indent=2)


@server.tool()
async def read_service_logs(service: str = "api", lines: int = 40, filter_keyword: str = "") -> str:
    """Fetch live log stream from FastAPI or Nginx services.

    Arguments:
        service: 'api' (verischolar-api systemd service), 'nginx-error', or 'nginx-access'
        lines: number of recent log lines to retrieve (default: 40)
        filter_keyword: optional substring to grep for (e.g. 'ERROR', 'exception')
    """
    if service == "api":
        cmd = ["journalctl", "-u", "verischolar-api.service", "-n", str(lines), "--no-pager"]
    elif service == "nginx-error":
        cmd = ["tail", "-n", str(lines), "/var/log/nginx/error.log"]
    elif service == "nginx-access":
        cmd = ["tail", "-n", str(lines), "/var/log/nginx/access.log"]
    else:
        return json.dumps({"error": f"Unsupported service '{service}'. Use 'api', 'nginx-error', or 'nginx-access'."})

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output_lines = proc.stdout.splitlines()
        if filter_keyword:
            output_lines = [l for l in output_lines if filter_keyword.lower() in l.lower()]

        return json.dumps(
            {
                "service": service,
                "lines_count": len(output_lines),
                "logs": output_lines,
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve logs: {str(e)}"}, indent=2)


@server.tool()
async def inspect_github_ci_status(pr_number: int = 0, failed_only: bool = True) -> str:
    """Inspect GitHub Pull Request CI checks and extract failed workflow logs.

    Arguments:
        pr_number: PR number (e.g. 44) or 0 to list latest repository workflow runs.
        failed_only: if True, retrieves error traces for failed CI jobs.
    """
    repo = "dammanhdungvn/VeriScholar"
    cwd = "/home/VeriScholar/Workspace/VeriScholar"
    try:
        if pr_number > 0:
            # 1. Fetch PR checks summary
            pr_cmd = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", "title,state,statusCheckRollup,url"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=cwd,
            )
            if pr_cmd.returncode != 0:
                return json.dumps({"error": pr_cmd.stderr.strip()})

            pr_data = json.loads(pr_cmd.stdout)
            return json.dumps(pr_data, indent=2)

        # 2. List recent runs
        runs_cmd = subprocess.run(
            ["gh", "run", "list", "-L", "5", "--repo", repo, "--json", "databaseId,name,status,conclusion,event,headBranch,url"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        if runs_cmd.returncode != 0:
            return json.dumps({"error": runs_cmd.stderr.strip()})

        runs = json.loads(runs_cmd.stdout)
        if failed_only and runs:
            # Find the most recent failed run
            failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)
            if failed_run:
                run_id = str(failed_run["databaseId"])
                log_cmd = subprocess.run(
                    ["gh", "run", "view", run_id, "--repo", repo, "--log-failed"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=cwd,
                )
                failed_run["failed_log_snippet"] = log_cmd.stdout[-2500:] if log_cmd.stdout else "No failed log text returned."

        return json.dumps({"recent_runs": runs}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"GitHub CLI inspection failed: {str(e)}"}, indent=2)


def main() -> None:
    """Run the MCP server over stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

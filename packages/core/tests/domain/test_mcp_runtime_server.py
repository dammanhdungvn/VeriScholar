"""Unit tests for VeriScholar Runtime Diagnostics MCP Server."""

import json

import pytest
from core.mcp.runtime_server import (
    check_services_health,
    inspect_github_ci_status,
    inspect_redis,
    probe_api,
    query_database_readonly,
    read_service_logs,
)


@pytest.mark.asyncio
async def test_check_services_health():
    res_str = await check_services_health()
    data = json.loads(res_str)
    assert "services" in data
    assert "active_listening_ports" in data
    assert isinstance(data["active_listening_ports"], list)


@pytest.mark.asyncio
async def test_query_database_readonly_summary():
    res_str = await query_database_readonly("summary")
    data = json.loads(res_str)
    assert "database_summary" in data or "error" in data


@pytest.mark.asyncio
async def test_query_database_readonly_safety_violation():
    # Attempt dangerous write queries - should be blocked by safety guard
    res_str = await query_database_readonly("DROP TABLE users")
    data = json.loads(res_str)
    assert "error" in data
    assert "Safety violation" in data["error"]

    res_str2 = await query_database_readonly("INSERT INTO users VALUES (1)")
    data2 = json.loads(res_str2)
    assert "error" in data2
    assert "Safety violation" in data2["error"]


@pytest.mark.asyncio
async def test_inspect_redis():
    res_str = await inspect_redis()
    data = json.loads(res_str)
    assert "ping" in data or "error" in data


@pytest.mark.asyncio
async def test_probe_api():
    res_str = await probe_api("/health", "http://127.0.0.1:8000")
    data = json.loads(res_str)
    assert "status_code" in data or "error" in data


@pytest.mark.asyncio
async def test_read_service_logs():
    res_str = await read_service_logs("api", lines=5)
    data = json.loads(res_str)
    assert data["service"] == "api"
    assert "logs" in data


@pytest.mark.asyncio
async def test_inspect_github_ci_status():
    res_str = await inspect_github_ci_status(pr_number=0)
    data = json.loads(res_str)
    assert "recent_runs" in data or "error" in data

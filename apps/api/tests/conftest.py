"""Pytest configuration and global fixtures for backend test suite."""

import os

# Enforce test environment flags before any application modules are imported
os.environ["ENVIRONMENT"] = "test"
os.environ["LANGFUSE_ENABLED"] = "false"

import pytest
from api.core.config import settings

# Enforce test settings on existing singleton
settings.ENVIRONMENT = "test"
settings.LANGFUSE_ENABLED = False


@pytest.fixture(autouse=True)
def disable_external_telemetry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enforce zero external telemetry calls or external network I/O in tests."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")

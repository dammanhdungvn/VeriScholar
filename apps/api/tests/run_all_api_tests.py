"""Master Autotest Runner for VeriScholar APIs.

Runs all automated test suites across all endpoints and reports overall status.
Can be executed directly via:
    uv run python apps/api/tests/run_all_api_tests.py
"""

import sys

import pytest


def run_all_api_tests() -> int:
    """Execute all API test suites with verbose output and coverage."""
    args = [
        "apps/api/tests",
        "-v",
        "--tb=short",
    ]
    print("=" * 70)
    print("🚀 VeriScholar Master API Test Suite Runner")
    print("=" * 70)
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_all_api_tests())

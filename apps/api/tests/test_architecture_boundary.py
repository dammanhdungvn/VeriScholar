"""Automated Architectural Boundary & Mechanical Enforcement Tests.

Enforces:
1. Pure Hexagonal Domain Boundary: packages/core domain & ports must not import
   infrastructure, database, web frameworks, or apps.api.
2. Zero Legacy Artifacts: Banned strings (aiosqlite, sqlite3, neo4j, ComparisonMatrix, DeBERTa)
   must not exist in Python production code.
3. Harness Integrity: Root AGENTS.md symlink, .agents constitution, and core skills.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


def test_hexagonal_boundary_pure_domain():
    """Validates that packages/core domain and ports do not import framework/infra packages."""
    core_src = ROOT_DIR / "packages" / "core" / "src" / "core"
    scan_dirs = [core_src / "domain", core_src / "ports"]

    banned_modules = {
        "fastapi",
        "starlette",
        "sqlalchemy",
        "sqlmodel",
        "alembic",
        "redis",
        "aioredis",
        "fitz",
        "pymupdf",
        "httpx",
        "aiohttp",
        "requests",
        "aiofiles",
        "e2b",
        "langfuse",
        "openai",
        "apps.api",
        "api",
    }

    violations: list[str] = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_pkg = alias.name.split(".")[0]
                        if top_pkg in banned_modules or alias.name in banned_modules:
                            violations.append(
                                f"{py_file.relative_to(ROOT_DIR)}:{node.lineno}: import {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top_pkg = node.module.split(".")[0]
                        if top_pkg in banned_modules or node.module in banned_modules:
                            violations.append(
                                f"{py_file.relative_to(ROOT_DIR)}:{node.lineno}: from {node.module} import ..."
                            )

    assert not violations, "Hexagonal architecture violation(s) detected in core:\n" + "\n".join(violations)


def test_banned_legacy_artifacts():
    """Scans Python production code to ensure obsolete 5-pillar artifacts do not exist."""
    search_dirs = [
        ROOT_DIR / "apps" / "api" / "src",
        ROOT_DIR / "packages" / "core" / "src",
    ]

    banned_keywords = [
        "aiosqlite",
        "sqlite3",
        "neo4j",
        "ComparisonMatrix",
        "DeBERTa",
    ]

    violations: list[str] = []

    for sdir in search_dirs:
        for py_file in sdir.rglob("*.py"):
            lines = py_file.read_text(encoding="utf-8").splitlines()
            for line_no, line in enumerate(lines, 1):
                # Ignore comment-only lines if any
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for kw in banned_keywords:
                    if kw in line:
                        violations.append(
                            f"{py_file.relative_to(ROOT_DIR)}:{line_no}: contains banned keyword '{kw}' -> {stripped}"
                        )

    assert not violations, "Banned legacy artifact(s) found in production Python code:\n" + "\n".join(violations)


def test_agent_harness_integrity():
    """Validates the structure and constraints of the Repo-Owned Agent Harness."""
    # 1. Root symlink check
    root_agents = ROOT_DIR / "AGENTS.md"
    assert root_agents.is_symlink(), "Root AGENTS.md must be a symlink to .agents/AGENTS.md"
    resolved_target = os.readlink(root_agents)
    assert resolved_target in [".agents/AGENTS.md", str(ROOT_DIR / ".agents" / "AGENTS.md")]

    # 2. Constitution length constraint (< 200 lines)
    target_agents = ROOT_DIR / ".agents" / "AGENTS.md"
    assert target_agents.exists(), ".agents/AGENTS.md does not exist"
    lines = target_agents.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 200, f".agents/AGENTS.md is too long ({len(lines)} lines; max 200 allowed)"

    # 3. Architecture principles check
    arch_doc = ROOT_DIR / ".agents" / "ARCHITECTURE_PRINCIPLES.md"
    assert arch_doc.exists(), ".agents/ARCHITECTURE_PRINCIPLES.md does not exist"
    arch_content = arch_doc.read_text(encoding="utf-8")
    assert "pgvector" in arch_content
    assert "Redis 7" in arch_content
    assert "Lục Giác" in arch_content or "Hexagonal" in arch_content

    # 4. Core Skills check
    core_skills = [
        "verischolar-backend",
        "verischolar-frontend",
        "verischolar-tdd",
        "agent-maintenance",
    ]
    for skill in core_skills:
        skill_doc = ROOT_DIR / ".agents" / "skills" / skill / "SKILL.md"
        assert skill_doc.exists(), f"Core skill '{skill}' is missing at {skill_doc}"

    # 5. Developer scripts check
    setup_sh = ROOT_DIR / "scripts" / "dev" / "setup.sh"
    seed_py = ROOT_DIR / "scripts" / "dev" / "seed.py"
    assert setup_sh.exists(), "scripts/dev/setup.sh is missing"
    assert os.access(setup_sh, os.X_OK), "scripts/dev/setup.sh is not executable"
    assert seed_py.exists(), "scripts/dev/seed.py is missing"
    assert os.access(seed_py, os.X_OK), "scripts/dev/seed.py is not executable"

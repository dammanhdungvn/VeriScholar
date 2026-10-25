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


BANNED_MODULES = {
    "apps",
    "apps.api",
    "api",
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
}


def is_banned_import(mod_name: str) -> bool:
    top_pkg = mod_name.split(".")[0]
    return (
        top_pkg in BANNED_MODULES
        or mod_name in BANNED_MODULES
        or any(mod_name == m or mod_name.startswith(f"{m}.") for m in BANNED_MODULES)
    )


def check_ast_violations(source: str, filename: str = "core/domain/entity.py") -> list[str]:
    tree = ast.parse(source, filename=filename)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if is_banned_import(alias.name):
                    violations.append(f"{filename}:{node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and is_banned_import(node.module):
                violations.append(f"{filename}:{node.lineno}: from {node.module} import ...")
    return violations


def test_hexagonal_checker_catches_apps_api_submodules():
    source = "from apps.api.models import DocumentModel\nimport apps.api.db"
    violations = check_ast_violations(source)
    assert len(violations) == 2


def test_hexagonal_boundary_pure_domain():
    """Validates that packages/core domain and ports do not import framework/infra packages."""
    core_src = ROOT_DIR / "packages" / "core" / "src" / "core"
    scan_dirs = [core_src / "domain", core_src / "ports"]

    violations: list[str] = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            violations.extend(
                check_ast_violations(source, filename=str(py_file.relative_to(ROOT_DIR)))
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


def test_no_absolute_file_urls_in_markdown():
    """Validates that markdown documents do not contain absolute machine URLs like file:///home/ or ](file:///."""
    scan_dirs = [
        ROOT_DIR / "docs",
        ROOT_DIR / ".agents",
    ]
    markdown_files: list[Path] = []
    for sdir in scan_dirs:
        if sdir.exists():
            markdown_files.extend(sdir.rglob("*.md"))
    for root_md in ROOT_DIR.glob("*.md"):
        markdown_files.append(root_md)

    banned_link_patterns = [
        "file:///home/",
        "file:///Users/",
        "file:///root/",
        "](file:///",
    ]

    violations: list[str] = []
    for md_file in markdown_files:
        try:
            lines = md_file.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(lines, 1):
            for pattern in banned_link_patterns:
                if pattern in line:
                    rel_path = md_file.relative_to(ROOT_DIR)
                    violations.append(
                        f"{rel_path}:{line_no}: contains banned link pattern '{pattern}' -> {line.strip()}"
                    )

    assert not violations, "Forbidden absolute file:/// URLs found in markdown documents:\n" + "\n".join(violations)


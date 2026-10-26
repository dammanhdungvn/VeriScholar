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
import re
from pathlib import Path
from urllib.parse import unquote

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

    assert not violations, "Hexagonal architecture violation(s) detected in core:\n" + "\n".join(
        violations
    )


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

    assert not violations, (
        "Banned legacy artifact(s) found in production Python code:\n" + "\n".join(violations)
    )


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

    maint_doc = (ROOT_DIR / ".agents" / "skills" / "agent-maintenance" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "Locked Anti-Recurrence Registry" in maint_doc, (
        "agent-maintenance/SKILL.md must include Locked Anti-Recurrence Registry (/learn protocol)"
    )

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

    assert not violations, (
        "Forbidden absolute file:/// URLs found in markdown documents:\n" + "\n".join(violations)
    )


def test_no_broken_relative_links_in_markdown():
    """Validates that all relative markdown links in docs/, .agents/, and root *.md resolve to existing files."""
    scan_dirs = [ROOT_DIR / "docs", ROOT_DIR / ".agents"]
    markdown_files: list[Path] = []
    for sdir in scan_dirs:
        if sdir.exists():
            markdown_files.extend(sdir.rglob("*.md"))
    markdown_files.extend(ROOT_DIR.glob("*.md"))

    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    violations: list[str] = []

    for md_file in markdown_files:
        text = md_file.read_text(encoding="utf-8")
        text_no_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for match in link_re.finditer(text_no_code):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#", "conversation://")):
                continue
            target_path = unquote(target.split("#")[0].strip())
            if not target_path:
                continue
            resolved = (md_file.resolve().parent / target_path).resolve()
            if not resolved.exists():
                violations.append(
                    f"{md_file.relative_to(ROOT_DIR)} -> broken relative link '{target}'"
                )

    assert not violations, "Broken relative markdown links detected:\n" + "\n".join(violations)


def test_prd_conciseness_and_structure_invariants():
    """Prevents PRD bloat and scope creep by enforcing line limits and required BA sections."""
    prd_dir = ROOT_DIR / "docs" / "PRD"
    prd_files = sorted(prd_dir.glob("0*.md"))
    assert len(prd_files) == 9, f"Expected 9 PRD files in docs/PRD/, found {len(prd_files)}"

    violations: list[str] = []
    for prd_file in prd_files:
        text = prd_file.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not (120 <= len(lines) <= 210):
            violations.append(
                f"{prd_file.name}: line count {len(lines)} outside allowed [120, 210] range"
            )
        for sec in ("## 1.", "## 2.", "## 3.", "## 4."):
            if sec not in text:
                violations.append(f"{prd_file.name}: missing required section prefix '{sec}'")

    assert not violations, "PRD structure or conciseness invariant violated:\n" + "\n".join(
        violations
    )

    spec_09 = ROOT_DIR / "docs" / "specs" / "09-deployment-cicd-and-evaluation-spec.md"
    assert spec_09.exists(), "docs/specs/09-deployment-cicd-and-evaluation-spec.md is missing"
    spec_09_text = spec_09.read_text(encoding="utf-8")
    for marker in (
        "Azure Ubuntu",
        "proxy_buffering off",
        "Thực Nghiệm 1",
        "Thực Nghiệm 2",
        "Thực Nghiệm 3",
    ):
        assert marker in spec_09_text, f"Spec-09 missing required section marker: {marker}"


def test_no_code_placeholders_in_superpowers_plans():
    """Ensures implementation plans in docs/superpowers/plans/ do not contain standalone '...' placeholders."""
    plans_dir = ROOT_DIR / "docs" / "superpowers" / "plans"
    plan_files = sorted(plans_dir.glob("*.md"))
    code_block_re = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.DOTALL)
    violations: list[str] = []

    for plan_file in plan_files:
        text = plan_file.read_text(encoding="utf-8")
        for block_idx, match in enumerate(code_block_re.finditer(text), 1):
            for line in match.group(1).splitlines():
                if line.strip() in ("...", "# TODO"):
                    violations.append(
                        f"{plan_file.relative_to(ROOT_DIR)} (code block #{block_idx}): contains placeholder '{line.strip()}'"
                    )

    assert not violations, "Placeholder lines found in superpowers plans:\n" + "\n".join(violations)


def test_thesis_outline_mapping_integrity():
    """Validates that docs/THESIS_OUTLINE_MAPPING.md exists and maps all 5 graduation thesis chapters."""
    thesis_doc = ROOT_DIR / "docs" / "THESIS_OUTLINE_MAPPING.md"
    assert thesis_doc.exists(), "docs/THESIS_OUTLINE_MAPPING.md is missing"
    content = thesis_doc.read_text(encoding="utf-8")
    for chapter in ("Chương 1", "Chương 2", "Chương 3", "Chương 4", "Chương 5"):
        assert chapter in content, f"THESIS_OUTLINE_MAPPING.md is missing '{chapter}'"
    assert "08-deployment-and-system-evaluation.md" in content
    assert "09-deployment-cicd-and-evaluation-spec.md" in content


def test_deployment_configs_and_nginx_sse_routes():
    """Validates Nginx SSE unbuffered routing, Dockerfile.api uv sync/CAS volume, 2-tier CI, and CD deploy scripts."""
    nginx_files = [
        ROOT_DIR / "deploy" / "nginx" / "production-host.conf",
        ROOT_DIR / "deploy" / "nginx" / "verischolar.conf",
    ]
    required_sse_fragments = [
        "context-table:stream",
        "library/graph:query",
        "drafts/.*/chat:stream",
        "summary:stream",
        "proxy_buffering off;",
    ]
    for nf in nginx_files:
        assert nf.exists(), f"Missing Nginx config: {nf}"
        content = nf.read_text(encoding="utf-8")
        for frag in required_sse_fragments:
            assert frag in content, (
                f"{nf.relative_to(ROOT_DIR)} missing required SSE fragment '{frag}'"
            )

    dockerfile_api = ROOT_DIR / "deploy" / "Dockerfile.api"
    assert dockerfile_api.exists(), "deploy/Dockerfile.api is missing"
    df_text = dockerfile_api.read_text(encoding="utf-8")
    assert "uv sync" in df_text, "deploy/Dockerfile.api must use 'uv sync' for deterministic builds"
    assert "/app/data/cas" in df_text, "deploy/Dockerfile.api must declare /app/data/cas volume"

    ci_yml = ROOT_DIR / ".github" / "workflows" / "ci.yml"
    ci_text = ci_yml.read_text(encoding="utf-8")
    assert "pgvector/pgvector:0.8.6-pg18" in ci_text, (
        "ci.yml must include pgvector service container"
    )
    assert "redis:7-alpine" in ci_text, "ci.yml must include redis:7-alpine service container"
    assert "tectonic" not in ci_text.lower(), "ci.yml must not install legacy Tectonic compiler"

    for script_name in ("deploy_production.sh", "deploy_web.sh"):
        script_path = ROOT_DIR / "scripts" / script_name
        assert script_path.exists(), f"Missing deployment script: scripts/{script_name}"
        assert os.access(script_path, os.X_OK), (
            f"scripts/{script_name} must be executable (chmod +x)"
        )


def test_mermaid_diagrams_are_human_centric_paper_grade():
    """Enforces that Mermaid diagrams in docs/specs/ and docs/PRD/ are human-centric, paper-grade conceptual/UML diagrams without code filenames, HTML tags, or fake test-list boxes."""
    spec_files = sorted((ROOT_DIR / "docs" / "specs").glob("0*.md"))
    prd_files = sorted((ROOT_DIR / "docs" / "PRD").glob("0*.md"))
    assert len(spec_files) == 10, f"Expected 10 spec files, found {len(spec_files)}"
    assert len(prd_files) == 9, f"Expected 9 PRD files, found {len(prd_files)}"

    mermaid_re = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
    banned_tokens_in_mermaid = (
        ".tsx",
        ".ts",
        ".py",
        ".sh",
        "<b>",
        "</b>",
        "<br/>",
        "<br>",
        "subgraph CoreTests",
        "Tầng Core / Domain Tests",
        "Test User Entity Creation",
        "test_hexagonal_boundary_pure_domain",
    )

    violations: list[str] = []
    sequence_diagram_count = 0

    for doc_file in [*spec_files, *prd_files]:
        text = doc_file.read_text(encoding="utf-8")
        blocks = mermaid_re.findall(text)
        rel_path = doc_file.relative_to(ROOT_DIR)
        if not blocks:
            violations.append(f"{rel_path}: must contain at least 1 ```mermaid diagram block")
            continue

        for idx, block in enumerate(blocks, 1):
            if "sequenceDiagram" in block:
                sequence_diagram_count += 1
            for token in banned_tokens_in_mermaid:
                if token in block:
                    violations.append(
                        f"{rel_path} (Mermaid block #{idx}): contains banned coder/clutter token '{token}'"
                    )

    if sequence_diagram_count < 6:
        violations.append(
            f"Expected at least 6 UML sequenceDiagram blocks across docs/specs/, found {sequence_diagram_count}"
        )

    assert not violations, (
        "Mermaid diagrams violated human-centric paper-grade standards:\n" + "\n".join(violations)
    )


def test_no_engineering_brag_or_forbidden_copy_in_frontend():
    """Enforces ERR-05 & AGENTS.md Rule 6: Absolute prohibition of engineering brag,

    internal technical jargon (AES-256, ISO 32000-1, Zero-Retention), or bulky title badges
    in user-facing frontend code (apps/web/src).
    """
    web_src = ROOT_DIR / "apps" / "web" / "src"
    if not web_src.exists():
        return

    banned_ui_terms = (
        "ISO 32000-1",
        "AES-256",
        "Zero-Retention",
        "Zero Data Retention",
        "Học giả đã xác thực",
        "Nhà Nghiên Cứu",
        "Nhà nghiên cứu Khoa học",
        "• Đang hoạt động",
        "bits)",
        "Độ an toàn:",
    )

    violations: list[str] = []
    for code_file in web_src.rglob("*"):
        if code_file.suffix not in (".tsx", ".ts"):
            continue
        # Skip node_modules or dist if any
        if any(part in code_file.parts for part in ("node_modules", "dist", ".cache")):
            continue

        text = code_file.read_text(encoding="utf-8")
        for term in banned_ui_terms:
            if term in text:
                rel_path = code_file.relative_to(ROOT_DIR)
                violations.append(
                    f"{rel_path}: contains banned engineering-brag/verbose copy '{term}'"
                )

    assert not violations, (
        "Forbidden engineering-centric or verbose UI copy detected in apps/web/src:\n"
        + "\n".join(violations)
    )

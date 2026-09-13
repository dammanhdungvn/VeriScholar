"""Architectural test: Enforces Hexagonal Architecture domain isolation.

Verifies that packages/core/src/core/domain/ contains strictly zero imports
of external frameworks or infrastructure layers (FastAPI, SQLAlchemy, Uvicorn, Docker, PyMuPDF).
"""

from pathlib import Path

BANNED_IMPORTS = ["fastapi", "sqlalchemy", "uvicorn", "docker", "fitz"]


def test_domain_layer_has_no_infrastructure_imports() -> None:
    domain_dir = Path(__file__).resolve().parent.parent.parent / "src" / "core" / "domain"
    assert domain_dir.exists(), f"Domain directory {domain_dir} does not exist."

    violations: list[str] = []

    for py_file in domain_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for banned in BANNED_IMPORTS:
            if f"import {banned}" in content or f"from {banned}" in content:
                violations.append(
                    f"Violation in {py_file.relative_to(domain_dir)}: prohibited import '{banned}'"
                )

    assert not violations, "\n".join(violations)

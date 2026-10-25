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


import importlib
import pytest


@pytest.mark.parametrize(
    "removed_module",
    [
        "core.domain.entities.safe_claim",
        "core.domain.entities.note_synthesis",
        "core.domain.value_objects.pdf_annotation",
        "core.ports.safe_verifier",
        "core.ports.pdf_annotator",
        "core.ports.eval",
        "core.services.safe_fact_checker",
        "core.services.safe_nli_adapter",
        "core.mcp.runtime_server",
        "core.eval",
        "core.prompts.template",
    ],
)
def test_out_of_scope_core_modules_removed(removed_module: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(removed_module)


def test_core_barrel_imports_clean() -> None:
    entities = importlib.import_module("core.domain.entities")
    ports = importlib.import_module("core.ports")
    services = importlib.import_module("core.services")
    assert not hasattr(entities, "AtomicClaim")
    assert not hasattr(entities, "NoteSynthesis")
    assert not hasattr(entities, "CitationEdge")
    assert not hasattr(ports, "INLIVerifierPort")
    assert not hasattr(ports, "IPdfAnnotatorPort")
    assert not hasattr(services, "SAFEFactChecker")


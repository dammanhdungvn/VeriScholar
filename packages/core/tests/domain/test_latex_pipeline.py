"""Unit tests for LaTeX Linter, Sandboxed Compiler, and Self-Healing Loop (Module 2)."""

import shutil

import pytest
from core.domain.entities.latex import SandboxCapabilityReport
from core.domain.exceptions import SandboxInfrastructureUnavailableError
from core.services.latex_compiler import SandboxedLatexCompiler
from core.services.latex_healer import AgenticLatexHealer
from core.services.latex_linter import FastLatexAstLinter
from core.services.sandbox_probe import SandboxRuntimeCapabilityProbe

_has_cli_compiler = bool(shutil.which("tectonic") or shutil.which("pdflatex"))
requires_cli_compiler = pytest.mark.skipif(
    not _has_cli_compiler,
    reason="Native LaTeX compiler (tectonic/pdflatex) not installed on host",
)


def test_fast_ast_linter_clean_code() -> None:
    """Verify that syntactically valid LaTeX code passes linter with zero errors."""
    linter = FastLatexAstLinter()
    clean_code = r"""
    \section{Introduction}
    Deep learning has revolutionized scientific discovery.
    \begin{equation}
        E = mc^2
    \end{equation}
    In this work, we present a novel approach.
    """
    errors = linter.lint(clean_code)
    assert len(errors) == 0


def test_fast_ast_linter_unclosed_environment() -> None:
    r"""Verify detection of unclosed \begin{env}."""
    linter = FastLatexAstLinter()
    broken_code = r"""
    \section{Methods}
    \begin{align}
        x = a + b
    % Missing \end{align}
    """
    errors = linter.lint(broken_code)
    assert len(errors) >= 1
    assert any(e.rule == "UNCLOSED_ENV" for e in errors)


def test_fast_ast_linter_mismatched_environment() -> None:
    r"""Verify detection of mismatched \begin{env} and \end{other}."""
    linter = FastLatexAstLinter()
    mismatched_code = r"""
    \begin{equation}
        y = f(x)
    \end{align}
    """
    errors = linter.lint(mismatched_code)
    assert len(errors) >= 1
    assert any(e.rule == "MISMATCHED_ENV" for e in errors)


def test_fast_ast_linter_unclosed_brace() -> None:
    """Verify detection of unclosed curly brace {."""
    linter = FastLatexAstLinter()
    broken_code = r"\textbf{Missing closing brace"
    errors = linter.lint(broken_code)
    assert len(errors) >= 1
    assert any(e.rule == "UNCLOSED_BRACE" for e in errors)


def test_fast_ast_linter_unescaped_underscore() -> None:
    """Verify detection of unescaped underscore in regular text."""
    linter = FastLatexAstLinter()
    code = r"Here is variable_name outside math mode."
    errors = linter.lint(code)
    assert len(errors) >= 1
    assert any(e.rule == "UNESCAPED_UNDERSCORE" for e in errors)


@requires_cli_compiler
@pytest.mark.asyncio
async def test_sandboxed_compiler_success() -> None:
    """Verify compilation returns valid PDF preview bytes and accurately reports unconfined host."""
    compiler = SandboxedLatexCompiler()
    code = r"""
    \section{Results}
    The proposed model achieves high accuracy.
    """
    result = await compiler.compile(code)
    assert result.success is True
    assert result.pdf_bytes is not None
    assert len(result.pdf_bytes) > 100
    assert result.pdf_bytes.startswith(b"%PDF")
    # On unconfined host infrastructure, is_sandboxed must be strictly False (never faked as True)
    assert result.is_sandboxed is False


@requires_cli_compiler
@pytest.mark.asyncio
async def test_agentic_latex_healer_auto_repair() -> None:
    """Verify that healer automatically repairs unclosed environment within retries."""
    healer = AgenticLatexHealer(max_retries=3)
    broken_code = r"""
    \section{Model}
    \begin{equation}
        L = -\sum y \log(\hat{y})
    """
    # Initially broken because \end{equation} is missing
    result = await healer.compile_with_healing(broken_code)
    assert result.success is True
    assert result.pdf_bytes is not None
    assert result.pdf_bytes.startswith(b"%PDF")
    assert result.retries_attempted >= 1


@pytest.mark.asyncio
async def test_agentic_latex_healer_graceful_fallback() -> None:
    """Verify graceful fallback with diagnostics when code cannot be repaired."""
    healer = AgenticLatexHealer(max_retries=2)
    # Code with an unclosed display math that cannot be simply healed
    unhealable_code = r"\end{nonexistent_env}"
    result = await healer.compile_with_healing(unhealable_code)
    assert result.success is False
    assert len(result.errors) >= 1
    assert result.retries_attempted <= 2


@pytest.mark.asyncio
async def test_sandboxed_compiler_pymupdf_fallback_returns_success() -> None:
    """Verify PyMuPDF fallback returns success=True with valid preview PDF bytes."""
    compiler = SandboxedLatexCompiler(prefer_system_compiler=False)
    code = r"""
    \section{Results}
    The proposed model achieves high accuracy.
    """
    result = await compiler.compile(code)
    assert result.success is True
    assert result.pdf_bytes is not None
    assert result.pdf_bytes.startswith(b"%PDF")
    assert result.is_sandboxed is False


@requires_cli_compiler
@pytest.mark.asyncio
async def test_sandboxed_compiler_hardened_probe_mock() -> None:
    """Verify is_sandboxed is True when hardened sandbox probe conditions are satisfied."""

    class FakeHardenedProbe(SandboxRuntimeCapabilityProbe):
        def probe(self) -> SandboxCapabilityReport:
            return SandboxCapabilityReport(
                has_cpu_limit=True,
                has_memory_limit=True,
                network_egress_blocked=True,
                read_only_rootfs=True,
                tmpfs_mounted=True,
                non_root_execution=True,
                env_allowlist_enforced=True,
                is_hardened_sandbox=True,
                status="SUPPORTED",
                block_reasons=[],
            )

    compiler = SandboxedLatexCompiler(probe=FakeHardenedProbe())
    code = r"\section{Test}"
    result = await compiler.compile(code)
    assert result.success is True
    assert result.is_sandboxed is True


@pytest.mark.asyncio
async def test_sandboxed_compiler_require_hardened_raises_on_blocked_infra() -> None:
    """Verify SandboxInfrastructureUnavailableError is raised on blocked infra."""
    compiler = SandboxedLatexCompiler(require_hardened_sandbox=True)
    code = r"\section{Test}"
    with pytest.raises(SandboxInfrastructureUnavailableError) as exc_info:
        await compiler.compile(code)
    assert "Hardened sandbox infrastructure unavailable" in str(exc_info.value)
    assert len(exc_info.value.reasons) > 0


def test_sandbox_capability_probe_host_detection() -> None:
    """Verify SandboxRuntimeCapabilityProbe detects unconfined host blockers."""
    probe = SandboxRuntimeCapabilityProbe()
    report = probe.probe()
    assert report.status in ("SUPPORTED", "BLOCKED_INFRASTRUCTURE")
    if not report.is_hardened_sandbox:
        assert len(report.block_reasons) > 0
        with pytest.raises(SandboxInfrastructureUnavailableError):
            probe.verify_sandbox_or_raise()


def test_sandbox_probe_env_sanitization() -> None:
    """Verify sensitive credentials are removed while safe system vars are preserved."""
    probe = SandboxRuntimeCapabilityProbe()
    tainted_env = {
        "PATH": "/usr/bin:/bin",
        "TMPDIR": "/tmp",
        "OPENAI_API_KEY": "dummy_secret_openai_token",
        "ANTHROPIC_API_KEY": "sk-ant-secret",
        "JWT_SECRET": "topsecretjwt",
        "AWS_SECRET_ACCESS_KEY": "awssecret",
        "CUSTOM_APP_TOKEN": "mytoken",
    }
    clean_env = probe.sanitize_env(tainted_env)
    assert "PATH" in clean_env
    assert "TMPDIR" in clean_env
    assert "OPENAI_API_KEY" not in clean_env
    assert "ANTHROPIC_API_KEY" not in clean_env
    assert "JWT_SECRET" not in clean_env
    assert "AWS_SECRET_ACCESS_KEY" not in clean_env
    assert "CUSTOM_APP_TOKEN" not in clean_env

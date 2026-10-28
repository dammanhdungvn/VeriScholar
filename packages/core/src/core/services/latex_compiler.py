"""Sandboxed LaTeX Compiler with Hardened Security & PDF Preview Fallback (Module 2).

Implements Tier 2 compilation adhering to PRD §3.2:
- Mandatory security flag: --no-shell-escape
- Timeout: 15s hard cutoff
- Pre-compile Tier 1 AST Linter gate
- In-memory rendering fallback for testing & local development
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import tempfile
import time
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from core.domain.entities.latex import LatexCompilationResult, LatexSyntaxError
from core.ports.latex import ILatexCompilerPort
from core.services.latex_linter import FastLatexAstLinter
from core.services.sandbox_probe import SandboxRuntimeCapabilityProbe

logger = structlog.get_logger("core.services.latex_compiler")

E2BSandboxFactory = Callable[..., Awaitable[Any]]
E2B_WORKDIR = "/tmp/verischolar-latex"
E2B_SOURCE_PATH = f"{E2B_WORKDIR}/document.tex"
E2B_PDF_PATH = f"{E2B_WORKDIR}/document.pdf"
MAX_DIAGNOSTIC_CHARS = 4000


class E2BLatexCompiler:
    """Compile LaTeX in an E2B sandbox without exposing application secrets."""

    def __init__(
        self,
        api_key: str | None,
        template: str | None = None,
        sandbox_factory: E2BSandboxFactory | None = None,
        request_timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = api_key.strip() if api_key else None
        self.template = template or os.getenv("E2B_LATEX_TEMPLATE", "base")
        self.sandbox_factory = sandbox_factory or self._create_sandbox
        self.request_timeout_seconds = request_timeout_seconds

    async def compile(
        self,
        code: str,
        timeout_seconds: float = 15,
    ) -> LatexCompilationResult:
        """Run pdflatex in an isolated E2B sandbox and return sanitized diagnostics."""
        if not self.api_key:
            return self._failure(
                rule="E2B_CONFIG_MISSING",
                message="E2B sandbox is not configured.",
                logs="E2B_API_KEY is not configured; no sandbox request was made.",
            )

        sandbox: Any | None = None
        try:
            sandbox = await self.sandbox_factory(
                template=self.template,
                timeout=max(1, int(timeout_seconds)),
                secure=True,
                allow_internet_access=False,
            )
            await sandbox.files.write(E2B_SOURCE_PATH, self._prepare_document(code))
            command_result = await asyncio.wait_for(
                sandbox.commands.run(
                    self._compile_command(),
                    cwd=E2B_WORKDIR,
                    timeout=timeout_seconds,
                    request_timeout=self.request_timeout_seconds or timeout_seconds,
                ),
                timeout=self.request_timeout_seconds or timeout_seconds,
            )
            stdout = self._text(getattr(command_result, "stdout", ""))
            stderr = self._text(getattr(command_result, "stderr", ""))
            diagnostics = self._sanitize_diagnostics(
                "\n".join(part for part in (stdout, stderr) if part)
            )
            exit_code = getattr(command_result, "exit_code", None)
            if exit_code is None:
                exit_code = getattr(command_result, "returncode", 1)

            if exit_code == 0:
                pdf = bytes(
                    await asyncio.wait_for(
                        sandbox.files.read(E2B_PDF_PATH, format="bytes"),
                        timeout=self.request_timeout_seconds or timeout_seconds,
                    )
                )
                if pdf.startswith(b"%PDF"):
                    return LatexCompilationResult(
                        success=True,
                        pdf_bytes=pdf,
                        logs=diagnostics,
                        is_sandboxed=True,
                    )

            return self._failure(
                rule="COMPILATION_FAILED",
                message=self._diagnostic_message(diagnostics),
                logs=diagnostics,
                line=self._diagnostic_line(diagnostics),
                is_sandboxed=True,
            )
        except (asyncio.TimeoutError, TimeoutError):
            return self._failure(
                rule="E2B_COMPILE_TIMEOUT",
                message=f"E2B compilation exceeded the {timeout_seconds:g}s timeout.",
                logs=f"E2B sandbox compilation timed out after {timeout_seconds:g}s.",
                is_sandboxed=True,
            )
        except ModuleNotFoundError:
            return self._failure(
                rule="E2B_SDK_UNAVAILABLE",
                message="The E2B Python SDK is not installed.",
                logs="Install the E2B Python SDK before enabling remote compilation.",
            )
        except Exception as exc:
            safe_error = self._sanitize_diagnostics(str(exc))
            rule = "E2B_CONFIG_INVALID" if self._looks_like_auth_error(exc) else "E2B_SANDBOX_ERROR"
            return self._failure(
                rule=rule,
                message=(
                    "E2B sandbox configuration is invalid or unavailable."
                    if rule == "E2B_CONFIG_INVALID"
                    else "E2B sandbox compilation failed."
                ),
                logs=safe_error or "E2B sandbox request failed without diagnostics.",
            )
        finally:
            if sandbox is not None:
                try:
                    await sandbox.kill()
                except Exception as exc:
                    logger.warning("e2b_sandbox_cleanup_failed", error_type=type(exc).__name__)

    async def _create_sandbox(self, **kwargs: Any) -> Any:
        """Create an SDK client with the key bound to the client, never sandbox envs."""
        from e2b import AsyncSandbox

        return await AsyncSandbox.create(api_key=self.api_key, **kwargs)

    @staticmethod
    def _prepare_document(code: str) -> str:
        if r"\documentclass" in code:
            return code
        body = code.strip()
        if r"\begin{document}" in body:
            return r"\documentclass{article}" + "\n" + r"\usepackage{amsmath,amssymb}" + "\n" + body
        return (
            r"\documentclass{article}"
            "\n"
            r"\usepackage{amsmath,amssymb}"
            "\n"
            r"\begin{document}"
            "\n" + body + "\n" + r"\end{document}" + "\n"
        )

    @staticmethod
    def _compile_command() -> str:
        return (
            "if command -v pdflatex >/dev/null 2>&1; then "
            "pdflatex -interaction=nonstopmode -halt-on-error --no-shell-escape "
            "-output-directory /tmp/verischolar-latex /tmp/verischolar-latex/document.tex; "
            "elif command -v tectonic >/dev/null 2>&1; then "
            "tectonic -X compile --untrusted --only-cached --outdir /tmp/verischolar-latex "
            "/tmp/verischolar-latex/document.tex; "
            "else echo 'No supported LaTeX compiler is installed in the E2B template.' >&2; "
            "exit 127; fi"
        )

    def _sanitize_diagnostics(self, value: str) -> str:
        sanitized = value.replace(self.api_key or "", "[REDACTED]")
        sanitized = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", sanitized)
        return sanitized[-MAX_DIAGNOSTIC_CHARS:]

    @staticmethod
    def _text(value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value or "")

    @staticmethod
    def _diagnostic_line(diagnostics: str) -> int:
        match = re.search(r"(?:document|main)\.tex:(\d+):", diagnostics)
        return int(match.group(1)) if match else 1

    @staticmethod
    def _diagnostic_message(diagnostics: str) -> str:
        for line in diagnostics.splitlines():
            if line.strip():
                return line.strip()[:500]
        return "E2B LaTeX compiler exited with a non-zero status."

    @staticmethod
    def _looks_like_auth_error(exc: Exception) -> bool:
        text = f"{type(exc).__name__} {exc}".lower()
        return any(marker in text for marker in ("auth", "api key", "401", "403", "forbidden"))

    @staticmethod
    def _failure(
        *,
        rule: str,
        message: str,
        logs: str,
        line: int = 1,
        is_sandboxed: bool = False,
    ) -> LatexCompilationResult:
        return LatexCompilationResult(
            success=False,
            pdf_bytes=None,
            errors=[
                LatexSyntaxError(
                    line=line,
                    rule=rule,
                    message=message,
                    suggested_fix="Check the E2B sandbox configuration and compiler diagnostics.",
                )
            ],
            logs=logs[-MAX_DIAGNOSTIC_CHARS:],
            is_sandboxed=is_sandboxed,
        )


class SandboxedLatexCompiler:
    """Production Sandboxed LaTeX compilation engine implementing ILatexCompilerPort."""

    def __init__(
        self,
        linter: FastLatexAstLinter | None = None,
        prefer_system_compiler: bool = True,
        probe: SandboxRuntimeCapabilityProbe | None = None,
        require_hardened_sandbox: bool = False,
        remote_compiler: ILatexCompilerPort | None = None,
    ) -> None:
        self.linter = linter or FastLatexAstLinter()
        self.prefer_system_compiler = prefer_system_compiler
        self.probe = probe or SandboxRuntimeCapabilityProbe()
        self.require_hardened_sandbox = require_hardened_sandbox
        self.remote_compiler = remote_compiler

    async def compile(
        self,
        code: str,
        timeout_seconds: float = 15,
    ) -> LatexCompilationResult:
        """Execute two-tier compilation with hardened isolation checks."""
        # Tier 1 Gate: Fast AST Linter Pre-check (< 100ms)
        syntax_errors = self.linter.lint(code)
        if syntax_errors:
            logger.info("latex_ast_precheck_failed", error_count=len(syntax_errors))
            return LatexCompilationResult(
                success=False,
                pdf_bytes=None,
                errors=syntax_errors,
                logs=f"Linter pre-check detected {len(syntax_errors)} syntax errors.",
                retries_attempted=0,
                is_sandboxed=False,
            )

        if self.remote_compiler is not None:
            remote_res = await self.remote_compiler.compile(code, timeout_seconds=timeout_seconds)
            if remote_res.success:
                return remote_res
            logger.warning(
                "remote_latex_compilation_failed_falling_back",
                error=remote_res.errors[0].message if remote_res.errors else None,
            )

        start_time = time.perf_counter()
        probe_report = self.probe.probe()

        # Enforce strict sandbox requirement when demanded:
        # Never silently fall back to host execution if hardened isolation is unavailable.
        if self.require_hardened_sandbox and not probe_report.is_hardened_sandbox:
            self.probe.verify_sandbox_or_raise()

        # Tier 2: Check for system compiler (pdflatex / tectonic)
        from pathlib import Path

        user_local_tectonic = str(Path.home() / ".local/bin/tectonic")
        ci_tectonic = "/home/VeriScholar/.local/bin/tectonic"
        has_unicode = any(ord(char) > 127 for char in code)
        compiler_bin = None
        if self.prefer_system_compiler:
            if has_unicode or "fontspec" in code or "xelatex" in code.lower():
                compiler_bin = (
                    shutil.which("xelatex")
                    or shutil.which("tectonic")
                    or (user_local_tectonic if os.path.exists(user_local_tectonic) else None)
                    or (ci_tectonic if os.path.exists(ci_tectonic) else None)
                    or shutil.which("pdflatex")
                )
            else:
                compiler_bin = (
                    shutil.which("tectonic")
                    or (user_local_tectonic if os.path.exists(user_local_tectonic) else None)
                    or (ci_tectonic if os.path.exists(ci_tectonic) else None)
                    or shutil.which("pdflatex")
                    or shutil.which("xelatex")
                )

        if compiler_bin:
            return await self._compile_with_cli(compiler_bin, code, timeout_seconds)

        # No compiler available (neither remote nor native CLI pdflatex/tectonic)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning("latex_compiler_unavailable", duration_ms=duration_ms)

        return LatexCompilationResult(
            success=False,
            pdf_bytes=None,
            errors=[
                LatexSyntaxError(
                    line=1,
                    column=0,
                    rule="COMPILER_NOT_FOUND",
                    message=(
                        "Không tìm thấy trình biên dịch LaTeX (Tectonic hoặc pdflatex) "
                        "trên máy chủ và E2B Sandbox không khả dụng."
                    ),
                    suggested_fix=(
                        "Cài đặt Tectonic, TeX Live hoặc cấu hình E2B_API_KEY để biên dịch PDF."
                    ),
                )
            ],
            logs=(
                "Native CLI LaTeX compiler unavailable and remote compilation "
                f"not configured ({duration_ms}ms)."
            ),
            retries_attempted=0,
            is_sandboxed=False,
        )

    async def _compile_with_cli(
        self,
        compiler_bin: str,
        code: str,
        timeout_seconds: int,
    ) -> LatexCompilationResult:
        """Run native compiler binary under hardened sandbox constraints."""
        probe_report = self.probe.probe()
        is_sandboxed = probe_report.is_hardened_sandbox
        sanitized_env = self.probe.sanitize_env()

        # Auto-wrap into basic article template if \documentclass is missing
        if r"\documentclass" not in code:
            if r"\begin{document}" in code:
                compilation_code = (
                    r"\documentclass{article}"
                    "\n"
                    r"\usepackage{amsmath,amssymb}"
                    "\n" + code
                )
            else:
                compilation_code = (
                    r"\documentclass{article}"
                    "\n"
                    r"\usepackage{amsmath,amssymb}"
                    "\n"
                    r"\begin{document}"
                    "\n" + code.strip() + "\n"
                    r"\end{document}"
                    "\n"
                )
        else:
            compilation_code = code

        with tempfile.TemporaryDirectory() as tmp_dir:
            tex_file = os.path.join(tmp_dir, "document.tex")
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(compilation_code)

            cmd: list[str]
            if "tectonic" in compiler_bin:
                cmd = [compiler_bin, "--untrusted", "--only-cached", "--outdir", tmp_dir, tex_file]
            else:
                cmd = [
                    compiler_bin,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "--no-shell-escape",
                    "-output-directory",
                    tmp_dir,
                    tex_file,
                ]

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmp_dir,
                    env=sanitized_env,
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_seconds,
                )
                log_output = (stdout + stderr).decode("utf-8", errors="replace")

                pdf_path = os.path.join(tmp_dir, "document.pdf")
                if proc.returncode == 0 and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                    return LatexCompilationResult(
                        success=True,
                        pdf_bytes=pdf_data,
                        errors=[],
                        logs=log_output[-1000:],
                        is_sandboxed=is_sandboxed,
                    )

                if (
                    "using only cached resource files" in log_output
                    and "failed to open input file" in log_output
                ):
                    return LatexCompilationResult(
                        success=False,
                        pdf_bytes=None,
                        errors=[
                            LatexSyntaxError(
                                line=1,
                                column=0,
                                rule="TECTONIC_BUNDLE_MISSING",
                                message=(
                                    "Tectonic requires additional packages not in the local cache."
                                ),
                                suggested_fix=(
                                    "Run tectonic with network access or use E2B Sandbox."
                                ),
                            )
                        ],
                        logs=log_output[-1000:],
                        is_sandboxed=is_sandboxed,
                    )

                return LatexCompilationResult(
                    success=False,
                    pdf_bytes=None,
                    errors=[
                        LatexSyntaxError(
                            line=1,
                            rule="COMPILATION_FAILED",
                            message="CLI LaTeX compiler exited with non-zero status.",
                            suggested_fix="Check logs for missing packages or syntax faults.",
                        )
                    ],
                    logs=log_output[-2000:],
                    is_sandboxed=is_sandboxed,
                )
            except TimeoutError:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                return LatexCompilationResult(
                    success=False,
                    pdf_bytes=None,
                    errors=[
                        LatexSyntaxError(
                            line=1,
                            rule="COMPILATION_TIMEOUT",
                            message=f"Quá thời hạn biên dịch cho phép ({timeout_seconds}s).",
                            suggested_fix="Đơn giản hóa công thức hoặc chia nhỏ tài liệu.",
                        )
                    ],
                    logs=f"Hardened Sandbox Timeout cutoff triggered at {timeout_seconds}s.",
                    is_sandboxed=is_sandboxed,
                )

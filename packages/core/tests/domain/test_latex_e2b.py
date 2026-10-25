"""Contract tests for the E2B-backed LaTeX compiler adapter."""

from __future__ import annotations

import asyncio
import inspect
from types import SimpleNamespace
from typing import Any

import pytest
from core.services.latex_compiler import E2BLatexCompiler, SandboxedLatexCompiler

VALID_LATEX = r"\documentclass{article}\begin{document}E=mc^2\end{document}"


class FakeFiles:
    def __init__(self, pdf_bytes: bytes = b"%PDF-1.7 fake") -> None:
        self.pdf_bytes = pdf_bytes
        self.writes: list[tuple[str, str]] = []

    async def write(self, path: str, data: str) -> None:
        self.writes.append((path, data))

    async def read(self, path: str, format: str = "text") -> bytes:
        assert path.endswith("/document.pdf")
        assert format == "bytes"
        return self.pdf_bytes


class FakeSandbox:
    def __init__(self, command_result: Any) -> None:
        self.files = FakeFiles()
        self.commands = self
        self.command_result = command_result
        self.commands_seen: list[dict[str, Any]] = []
        self.killed = False

    async def run(self, command: str, **kwargs: Any) -> Any:
        self.commands_seen.append({"command": command, **kwargs})
        return self.command_result

    async def kill(self) -> None:
        self.killed = True


def sandbox_factory_for(sandbox: FakeSandbox):
    async def factory(**kwargs: Any) -> FakeSandbox:
        assert kwargs["allow_internet_access"] is False
        assert kwargs["secure"] is True
        assert "envs" not in kwargs
        assert "api_key" not in kwargs
        return sandbox

    return factory


@pytest.mark.asyncio
async def test_e2b_compile_returns_pdf_and_never_sends_key_to_sandbox() -> None:
    sandbox = FakeSandbox(SimpleNamespace(exit_code=0, stdout="ok", stderr=""))
    compiler = E2BLatexCompiler(
        api_key="e2b_test_secret",
        sandbox_factory=sandbox_factory_for(sandbox),
    )

    result = await compiler.compile(VALID_LATEX)

    assert result.success is True
    assert result.pdf_bytes == b"%PDF-1.7 fake"
    assert result.is_sandboxed is True
    assert sandbox.files.writes[0][1] == VALID_LATEX
    assert "--no-shell-escape" in sandbox.commands_seen[0]["command"]
    assert sandbox.killed is True


@pytest.mark.asyncio
async def test_e2b_sdk_surface_uses_secure_network_disabled_create_without_launching() -> None:
    from e2b import AsyncSandbox

    signature = inspect.signature(AsyncSandbox.create)
    assert any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    assert "secure" in signature.parameters
    assert "allow_internet_access" in signature.parameters
    assert "timeout" in signature.parameters

    captured: dict[str, Any] = {}

    async def fake_create(**kwargs: Any) -> object:
        captured.update(kwargs)
        return object()

    original_create = AsyncSandbox.create
    AsyncSandbox.create = fake_create  # type: ignore[method-assign]
    try:
        compiler = E2BLatexCompiler(api_key="e2b_test_secret")
        await compiler._create_sandbox(
            template="base",
            timeout=15,
            secure=True,
            allow_internet_access=False,
        )
    finally:
        AsyncSandbox.create = original_create  # type: ignore[method-assign]

    assert captured == {
        "api_key": "e2b_test_secret",
        "template": "base",
        "timeout": 15,
        "secure": True,
        "allow_internet_access": False,
    }


@pytest.mark.asyncio
async def test_e2b_compile_reports_missing_configuration_without_calling_sdk() -> None:
    called = False

    async def factory(**kwargs: Any) -> Any:
        nonlocal called
        called = True
        return None

    result = await E2BLatexCompiler(api_key=None, sandbox_factory=factory).compile(VALID_LATEX)

    assert result.success is False
    assert result.errors[0].rule == "E2B_CONFIG_MISSING"
    assert called is False
    assert result.pdf_bytes is None


@pytest.mark.asyncio
async def test_e2b_compile_sanitizes_sdk_errors_and_stderr() -> None:
    secret = "e2b_test_secret"

    async def failing_factory(**kwargs: Any) -> Any:
        raise RuntimeError(f"authorization failed for {secret}")

    result = await E2BLatexCompiler(api_key=secret, sandbox_factory=failing_factory).compile(
        VALID_LATEX
    )

    assert result.success is False
    assert result.errors[0].rule == "E2B_CONFIG_INVALID"
    assert secret not in result.logs
    assert secret not in result.errors[0].message


@pytest.mark.asyncio
async def test_e2b_compile_maps_timeout_to_structured_error() -> None:
    sandbox = FakeSandbox(SimpleNamespace(exit_code=0, stdout="", stderr=""))

    async def slow_factory(**kwargs: Any) -> FakeSandbox:
        return sandbox

    async def slow_run(command: str, **kwargs: Any) -> Any:
        await asyncio.sleep(0.05)
        return SimpleNamespace(exit_code=0, stdout="", stderr="")

    sandbox.run = slow_run  # type: ignore[method-assign]
    compiler = E2BLatexCompiler(
        api_key="e2b_test_secret",
        sandbox_factory=slow_factory,
        request_timeout_seconds=0.01,
    )

    result = await compiler.compile(VALID_LATEX, timeout_seconds=1)

    assert result.success is False
    assert result.errors[0].rule == "E2B_COMPILE_TIMEOUT"
    assert sandbox.killed is True


@pytest.mark.asyncio
async def test_e2b_compile_promotes_stderr_to_line_aware_error() -> None:
    stderr = "document.tex:12: Undefined control sequence SECRET_TOKEN"
    sandbox = FakeSandbox(SimpleNamespace(exit_code=1, stdout="", stderr=stderr))
    compiler = E2BLatexCompiler(
        api_key="e2b_test_secret",
        sandbox_factory=sandbox_factory_for(sandbox),
    )

    result = await compiler.compile(VALID_LATEX)

    assert result.success is False
    assert result.errors[0].rule == "COMPILATION_FAILED"
    assert result.errors[0].line == 12
    assert "SECRET_TOKEN" in result.logs


@pytest.mark.asyncio
async def test_sandboxed_compiler_delegates_to_remote_after_lint() -> None:
    class FakeRemoteCompiler:
        def __init__(self) -> None:
            self.codes: list[str] = []

        async def compile(self, code: str, timeout_seconds: int = 15):
            self.codes.append(code)
            return SimpleNamespace(success=True, pdf_bytes=b"%PDF-remote", is_sandboxed=True)

    remote = FakeRemoteCompiler()
    compiler = SandboxedLatexCompiler(remote_compiler=remote)  # type: ignore[arg-type]

    result = await compiler.compile(VALID_LATEX)

    assert result.success is True
    assert result.pdf_bytes == b"%PDF-remote"
    assert remote.codes == [VALID_LATEX]

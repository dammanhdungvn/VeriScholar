"""LaTeX Ports (Hexagonal Architecture)."""

from typing import Protocol

from core.domain.entities.latex import LatexCompilationResult, LatexSyntaxError


class ILatexLinterPort(Protocol):
    """Port for fast AST syntax and asset dependency checking."""

    def lint(self, code: str) -> list[LatexSyntaxError]:
        """Check LaTeX code for syntax errors, unclosed environments, and missing braces.

        Returns:
            List of detected LatexSyntaxError objects. Empty if valid.
        """
        ...


class ILatexCompilerPort(Protocol):
    """Port for sandboxed LaTeX compilation."""

    async def compile(
        self,
        code: str,
        timeout_seconds: float = 15,
    ) -> LatexCompilationResult:
        """Compile LaTeX code into PDF binary in a hardened sandbox.

        Args:
            code: LaTeX source string.
            timeout_seconds: Hard execution cutoff (default: 15s).

        Returns:
            LatexCompilationResult with PDF bytes or error details.
        """
        ...

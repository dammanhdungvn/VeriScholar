"""Agentic Self-Healing LaTeX Loop with Anti-Oscillation Memory (Module 2).

Implements the self-repair loop according to PRD §3.2:
- Max retries: N = 3
- Anti-Oscillation Patching Memory (tracks visited code hashes and patch history)
- No-Rollback Constraint: Prevents oscillating back to previously failed AST states
- Graceful Fallback: Pinpoints line number and suggested fix if repair fails
"""

from __future__ import annotations

import hashlib

import structlog

from core.domain.entities.latex import LatexCompilationResult, LatexSyntaxError
from core.services.latex_compiler import SandboxedLatexCompiler

logger = structlog.get_logger("core.services.latex_healer")


class AgenticLatexHealer:
    """Orchestrates self-healing compilation with anti-oscillation safeguards."""

    def __init__(
        self,
        compiler: SandboxedLatexCompiler | None = None,
        max_retries: int = 3,
    ) -> None:
        self.compiler = compiler or SandboxedLatexCompiler()
        self.max_retries = max_retries

    @staticmethod
    def _code_hash(code: str) -> str:
        return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()[:16]

    def _auto_patch(self, code: str, errors: list[LatexSyntaxError]) -> str | None:
        """Deterministically apply single-error structural patches."""
        if not errors:
            return None

        err = errors[0]
        patched_code = code

        if err.rule == "UNCLOSED_ENV":
            # Extract env name from message
            import re

            m = re.search(r"\\begin\{([a-zA-Z0-9*_-]+)\}", err.message)
            env_name = m.group(1) if m else "equation"
            patched_code = code.rstrip() + f"\n\\end{{{env_name}}}\n"

        elif err.rule == "UNCLOSED_BRACE":
            patched_code = code.rstrip() + "}\n"

        elif err.rule == "UNCLOSED_DISPLAY_MATH":
            patched_code = code.rstrip() + "\n\\]\n"

        elif err.rule == "MISMATCHED_ENV":
            import re

            m_open = re.search(r"\\begin\{([a-zA-Z0-9*_-]+)\}", err.message)
            m_close = re.search(r"\\end\{([a-zA-Z0-9*_-]+)\}", err.message)
            if m_open and m_close:
                open_env = m_open.group(1)
                close_env = m_close.group(1)
                patched_code = code.replace(f"\\end{{{close_env}}}", f"\\end{{{open_env}}}")

        elif err.rule == "UNESCAPED_UNDERSCORE":
            lines = code.splitlines()
            if 1 <= err.line <= len(lines):
                target_line = lines[err.line - 1]
                # Replace unescaped underscores in this specific line
                import re

                fixed_line = re.sub(r"(?<!\\)_", r"\\_", target_line)
                lines[err.line - 1] = fixed_line
                patched_code = "\n".join(lines)

        return patched_code if patched_code != code else None

    async def compile_with_healing(
        self,
        code: str,
        timeout_seconds: int = 15,
    ) -> LatexCompilationResult:
        """Run self-healing compilation loop with anti-oscillation memory."""
        visited_hashes: set[str] = set()
        patch_history: list[dict[str, str | int]] = []
        current_code = code
        attempts = 0

        while attempts <= self.max_retries:
            code_hash = self._code_hash(current_code)

            # No-Rollback Constraint: abort if cycle detected
            if code_hash in visited_hashes:
                logger.warning(
                    "latex_healing_oscillation_detected",
                    code_hash=code_hash,
                    attempts=attempts,
                )
                break
            visited_hashes.add(code_hash)

            result = await self.compiler.compile(current_code, timeout_seconds=timeout_seconds)
            result.retries_attempted = attempts

            if result.success:
                logger.info(
                    "latex_healing_succeeded",
                    attempts=attempts,
                    final_hash=code_hash,
                )
                return result

            # If errors remain and retries left, synthesize patch
            if attempts < self.max_retries:
                patched = self._auto_patch(current_code, result.errors)
                if patched and patched not in visited_hashes:
                    patch_history.append(
                        {
                            "attempt": attempts + 1,
                            "from_hash": code_hash,
                            "rule_fixed": result.errors[0].rule if result.errors else "UNKNOWN",
                        }
                    )
                    current_code = patched
                    attempts += 1
                    continue

            # Cannot patch or retries exhausted
            break

        # Graceful Fallback: return the last compilation result with diagnostics
        logger.info(
            "latex_healing_graceful_fallback",
            attempts=attempts,
            error_count=len(result.errors),
        )
        result.retries_attempted = attempts
        return result

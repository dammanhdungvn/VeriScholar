"""Domain Entities for LaTeX Linter & Sandbox Compilation (Module 2)."""

from pydantic import BaseModel, ConfigDict, Field


class LatexSyntaxError(BaseModel):
    """Represents a syntax or lint issue detected in LaTeX source code."""

    model_config = ConfigDict(frozen=True)

    line: int = Field(ge=1, description="1-indexed line number where the issue occurs")
    column: int = Field(ge=0, default=0, description="0-indexed column offset")
    rule: str = Field(min_length=1, description="Rule code (e.g. ENV_MISMATCH, UNCLOSED_BRACE)")
    message: str = Field(min_length=1, description="Human and AI-readable explanation of error")
    suggested_fix: str | None = Field(
        default=None, description="Suggested replacement or correction"
    )


class LatexCompilationResult(BaseModel):
    """Result of LaTeX compilation or pre-check execution."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool = Field(description="True if compiled cleanly into PDF preview")
    pdf_bytes: bytes | None = Field(
        default=None, description="Compiled PDF binary data if successful"
    )
    errors: list[LatexSyntaxError] = Field(
        default_factory=list, description="List of syntax/compile errors"
    )
    logs: str = Field(default="", description="Compilation stdout/stderr or diagnostic log")
    retries_attempted: int = Field(
        ge=0, default=0, description="Number of self-healing retries performed"
    )
    is_sandboxed: bool = Field(
        default=True, description="True if executed under hardened sandbox flags"
    )


class SandboxCapabilityReport(BaseModel):
    """Runtime report evaluating hardened sandbox isolation capabilities."""

    model_config = ConfigDict(frozen=True)

    has_cpu_limit: bool = Field(description="1 vCPU limit enforcement active")
    has_memory_limit: bool = Field(description="512MB RAM cap enforcement active")
    network_egress_blocked: bool = Field(description="Network egress strictly denied")
    read_only_rootfs: bool = Field(description="Root filesystem mounted read-only")
    tmpfs_mounted: bool = Field(description="Isolated tmpfs mount active for scratchpad")
    non_root_execution: bool = Field(description="Executing as unprivileged non-root UID")
    env_allowlist_enforced: bool = Field(
        description="Environment variables restricted to allowlist"
    )
    is_hardened_sandbox: bool = Field(
        description="True if ALL hardened isolation conditions are satisfied"
    )
    status: str = Field(description="Overall probe status: 'SUPPORTED' or 'BLOCKED_INFRASTRUCTURE'")
    block_reasons: list[str] = Field(
        default_factory=list,
        description="Detailed causes if infrastructure blocks full sandbox isolation",
    )

"""Port specification for LLM PromptOps and Tracing (Langfuse)."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ITracerPort(Protocol):
    """Protocol for tracing LLM generations, prompt versions, and user interactions."""

    async def trace_generation(
        self,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
        usage: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an LLM prompt and completion trace."""
        ...

    async def trace_event(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an arbitrary telemetry event."""
        ...

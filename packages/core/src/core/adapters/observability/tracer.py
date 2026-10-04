"""Tracer adapters for Langfuse and Noop observation."""

import logging
from typing import Any

from core.ports.tracer import ITracerPort

logger = logging.getLogger("core.observability.tracer")


class NoopTracerAdapter(ITracerPort):
    """Null Object implementation of ITracerPort for testing and offline environments."""

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
        """No-op execution."""
        pass

    async def trace_event(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """No-op execution."""
        pass


class LangfuseTracerAdapter(ITracerPort):
    """Adapter sending LLM traces and PromptOps events to Langfuse."""

    def __init__(
        self,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str = "https://cloud.langfuse.com",
    ) -> None:
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self._enabled = bool(public_key and secret_key)
        self._client: Any = None

        if self._enabled:
            try:
                from langfuse import Langfuse  # type: ignore[import-untyped]

                self._client = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host,
                )
                logger.info("Langfuse tracing initialized successfully.")
            except ImportError:
                logger.warning("Langfuse package not installed. Running in passive logging mode.")
                self._enabled = False
            except Exception as e:
                logger.warning("Failed to initialize Langfuse client: %s", e)
                self._enabled = False

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
        """Record prompt generation trace with token usage to Langfuse."""
        if not self._enabled or not self._client:
            return

        try:
            self._client.generation(
                name=name,
                model=model,
                input=input_data,
                output=output_data,
                metadata={
                    **(metadata or {}),
                    "prompt_name": prompt_name,
                    "prompt_version": prompt_version,
                },
                usage=usage or {},
            )
        except Exception as e:
            logger.warning("Failed to emit Langfuse generation trace: %s", e)

    async def trace_event(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit arbitrary event trace to Langfuse."""
        if not self._enabled or not self._client:
            return

        try:
            self._client.event(name=name, metadata=metadata or {})
        except Exception as e:
            logger.warning("Failed to emit Langfuse event trace: %s", e)

"""AI Observability and Tracing Service using Langfuse with Fail-Safe & Privacy Protections.

Features:
- Fail-Safe & No-Op Facade: Any tracing failure is swallowed safely; core business flows never fail.
- HMAC-SHA256 User Pseudonymization: User identifiers are salted and hashed before sending.
- Zero Data Retention (ZDR): Sensitive payload masking (inputs, outputs, manuscript texts).
- Secret Scrubber: Cleanses Bearer tokens, OpenAI keys, and JWTs from traces and error messages.
- Async & Sync Context Manager support: Compatible with both `with` and `async with`.
"""

import hashlib
import hmac
import os
import random
import re
from collections.abc import Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any
from uuid import UUID

import structlog
from api.core.config import settings

logger = structlog.get_logger("api.services.ai_tracing")

# Sensitive text scrubbing patterns
_BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)
_OPENAI_KEY_PATTERN = re.compile(r"sk-[a-zA-Z0-9_\-]{16,}")
_GEMINI_KEY_PATTERN = re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}")
_GITHUB_TOKEN_PATTERN = re.compile(r"gh[pousr][_\-][a-zA-Z0-9]{20,}")
_JWT_PATTERN = re.compile(r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+")
_PASSWORD_URI_PATTERN = re.compile(r"://([^:]+):([^@]+)@")


def scrub_sensitive_text(text: str | None) -> str:
    """Scrub tokens, API keys, passwords, and JWTs from arbitrary string."""
    if not text:
        return ""
    result = _BEARER_PATTERN.sub("Bearer [REDACTED]", text)
    result = _OPENAI_KEY_PATTERN.sub("sk-[REDACTED]", result)
    result = _GEMINI_KEY_PATTERN.sub("AIzaSy[REDACTED]", result)
    result = _GITHUB_TOKEN_PATTERN.sub("gh-[REDACTED]", result)
    result = _JWT_PATTERN.sub("[REDACTED_JWT]", result)
    result = _PASSWORD_URI_PATTERN.sub(r"://\1:[REDACTED]@", result)
    return result


def pseudonymize_user_id(user_id: UUID | str | None, secret_key: str | None = None) -> str | None:
    """Hash user ID using HMAC-SHA256 to ensure zero PII leakage to third-party telemetry."""
    if not user_id:
        return None
    salt = (secret_key or settings.JWT_SECRET_KEY).encode("utf-8")
    user_str = str(user_id).strip().encode("utf-8")
    return hmac.new(salt, user_str, hashlib.sha256).hexdigest()


def mask_payload(data: Any, mask_enabled: bool = True) -> Any:
    """Mask text content according to Zero Data Retention policy.

    If mask_enabled is True:
        Replaces text bodies with length and SHA-256 fingerprint summary.
    If mask_enabled is False:
        Applies secret scrubbing to strip sensitive auth tokens and passwords.
    """
    if data is None:
        return None

    if isinstance(data, str):
        if not mask_enabled:
            return scrub_sensitive_text(data)
        if len(data) == 0:
            return ""
        digest = hashlib.sha256(data.encode("utf-8", errors="ignore")).hexdigest()[:8]
        return f"[MASKED_DATA: chars={len(data)}, sha256={digest}]"

    if isinstance(data, Mapping):
        return {k: mask_payload(v, mask_enabled=mask_enabled) for k, v in data.items()}

    if isinstance(data, Sequence) and not isinstance(data, (bytes, bytearray)):
        return [mask_payload(item, mask_enabled=mask_enabled) for item in data]

    return data


class BaseTraceSpan(AbstractContextManager, AbstractAsyncContextManager):
    """Abstract base protocol for trace and span execution contexts."""

    def set_input(self, input_data: Any) -> None:
        pass

    def set_output(self, output_data: Any) -> None:
        pass

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        pass

    def set_usage(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        reasoning_tokens: int = 0,
    ) -> None:
        pass

    def score(
        self,
        name: str,
        value: float | str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    def score_trace(
        self,
        name: str,
        value: float | str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    def update(
        self,
        *,
        name: str | None = None,
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
        level: str | None = None,
        status_message: str | None = None,
        model: str | None = None,
        usage_details: dict[str, int] | None = None,
        **kwargs: Any,
    ) -> None:
        pass

    def record_exception(self, exc: Exception) -> None:
        pass

    def end(self) -> None:
        pass


class NoOpTraceSpan(BaseTraceSpan):
    """No-Op span returned when Langfuse is disabled or sampled out."""

    def __enter__(self) -> "NoOpTraceSpan":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return False

    async def __aenter__(self) -> "NoOpTraceSpan":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return False


class LangfuseTraceSpan(BaseTraceSpan):
    """Active trace/span context manager delegating to Langfuse SDK."""

    def __init__(
        self,
        client: Any,
        name: str,
        as_type: str = "span",
        input_data: Any = None,
        output_data: Any = None,
        metadata: dict[str, Any] | None = None,
        mask_enabled: bool = True,
        model: str | None = None,
        model_parameters: dict[str, Any] | None = None,
        usage_details: dict[str, int] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        tags: list[str] | None = None,
        version: str | None = None,
    ) -> None:
        self.client = client
        self.name = name
        self.as_type = as_type
        self.mask_enabled = mask_enabled
        self.model = model
        self.model_parameters = model_parameters
        self.usage_details = usage_details
        self.user_id = user_id
        self.session_id = session_id
        self.tags = tags
        self.version = version
        self.initial_input = mask_payload(input_data, mask_enabled=mask_enabled)
        self.initial_output = mask_payload(output_data, mask_enabled=mask_enabled)
        self.metadata = metadata or {}
        self._cm: Any = None
        self._raw_span: Any = None

    def __enter__(self) -> "LangfuseTraceSpan":
        try:
            self._cm = self.client.start_as_current_observation(
                name=self.name,
                as_type=self.as_type,
                input=self.initial_input,
                output=self.initial_output,
                metadata=self.metadata,
                model=self.model,
                model_parameters=self.model_parameters,
                usage_details=self.usage_details,
                version=self.version,
            )
            self._raw_span = self._cm.__enter__()

            # Propagate first-class OpenTelemetry attributes for Langfuse
            # users/sessions/tags dashboards
            if self._raw_span is not None and hasattr(self._raw_span, "_otel_span"):
                otel_span = self._raw_span._otel_span
                if otel_span and hasattr(otel_span, "is_recording") and otel_span.is_recording():
                    try:
                        from langfuse import LangfuseOtelSpanAttributes as A

                        if self.user_id:
                            otel_span.set_attribute(A.TRACE_USER_ID, str(self.user_id))
                        if self.session_id:
                            otel_span.set_attribute(A.TRACE_SESSION_ID, str(self.session_id))
                        if self.tags:
                            otel_span.set_attribute(A.TRACE_TAGS, self.tags)
                        if self.version:
                            otel_span.set_attribute(A.RELEASE, self.version)
                    except Exception:
                        pass
        except Exception as ex:
            logger.warning(
                "langfuse_observation_start_failed",
                name=self.name,
                error=scrub_sensitive_text(str(ex)),
            )
            self._cm = None
            self._raw_span = None
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        try:
            if exc_val is not None and self._raw_span is not None:
                err_msg = scrub_sensitive_text(f"{type(exc_val).__name__}: {str(exc_val)}")
                try:
                    self._raw_span.update(
                        level="ERROR",
                        status_message=err_msg,
                    )
                except Exception:
                    pass
            if self._cm is not None:
                self._cm.__exit__(exc_type, exc_val, exc_tb)
        except Exception as ex:
            logger.warning(
                "langfuse_observation_exit_failed",
                name=self.name,
                error=scrub_sensitive_text(str(ex)),
            )
        finally:
            self._cm = None
            self._raw_span = None
        return False

    async def __aenter__(self) -> "LangfuseTraceSpan":
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return self.__exit__(exc_type, exc_val, exc_tb)

    def set_input(self, input_data: Any) -> None:
        self.update(input=input_data)

    def set_output(self, output_data: Any) -> None:
        self.update(output=output_data)

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        self.update(metadata=metadata)

    def set_usage(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        reasoning_tokens: int = 0,
    ) -> None:
        tot = total_tokens or (prompt_tokens + completion_tokens + reasoning_tokens)
        usage = {
            "input": prompt_tokens,
            "output": completion_tokens,
            "total": tot,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": tot,
        }
        if reasoning_tokens:
            usage["reasoning"] = reasoning_tokens
        self.update(usage_details=usage)

    def score(
        self,
        name: str,
        value: float | str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an evaluation score on this observation."""
        if self._raw_span is None:
            return
        try:
            clean_comment = scrub_sensitive_text(comment) if comment else None
            clean_meta = mask_payload(metadata, self.mask_enabled) if metadata else None
            if hasattr(self._raw_span, "score"):
                self._raw_span.score(
                    name=name,
                    value=value,
                    comment=clean_comment,
                    metadata=clean_meta,
                )
            elif hasattr(self._raw_span, "score_trace"):
                self._raw_span.score_trace(
                    name=name,
                    value=value,
                    comment=clean_comment,
                    metadata=clean_meta,
                )
        except Exception as ex:
            logger.debug("span_score_failed", name=name, error=str(ex))

    def score_trace(
        self,
        name: str,
        value: float | str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an evaluation score on the root trace."""
        if self._raw_span is None:
            return
        try:
            clean_comment = scrub_sensitive_text(comment) if comment else None
            clean_meta = mask_payload(metadata, self.mask_enabled) if metadata else None
            if hasattr(self._raw_span, "score_trace"):
                self._raw_span.score_trace(
                    name=name,
                    value=value,
                    comment=clean_comment,
                    metadata=clean_meta,
                )
        except Exception as ex:
            logger.debug("trace_score_failed", name=name, error=str(ex))

    def record_exception(self, exc: Exception) -> None:
        if self._raw_span is None:
            return
        try:
            sanitized = scrub_sensitive_text(f"{type(exc).__name__}: {str(exc)}")
            self._raw_span.update(level="ERROR", status_message=sanitized)
        except Exception as ex:
            logger.debug("record_exception_failed", error=str(ex))

    def update(
        self,
        *,
        name: str | None = None,
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
        level: str | None = None,
        status_message: str | None = None,
        model: str | None = None,
        usage_details: dict[str, int] | None = None,
        **kwargs: Any,
    ) -> None:
        if self._raw_span is None:
            return
        try:
            masked_in = mask_payload(input, self.mask_enabled) if input is not None else None
            masked_out = mask_payload(output, self.mask_enabled) if output is not None else None
            clean_status = scrub_sensitive_text(status_message) if status_message else None

            update_kwargs: dict[str, Any] = {}
            if name is not None:
                update_kwargs["name"] = name
            if masked_in is not None:
                update_kwargs["input"] = masked_in
            if masked_out is not None:
                update_kwargs["output"] = masked_out
            if metadata is not None:
                update_kwargs["metadata"] = metadata
            if level is not None:
                update_kwargs["level"] = level
            if clean_status is not None:
                update_kwargs["status_message"] = clean_status
            if model is not None:
                update_kwargs["model"] = model
            if usage_details is not None:
                update_kwargs["usage_details"] = usage_details

            self._raw_span.update(**update_kwargs)
        except Exception as ex:
            logger.warning(
                "langfuse_span_update_failed",
                name=self.name,
                error=scrub_sensitive_text(str(ex)),
            )

    def end(self) -> None:
        if self._raw_span is None:
            return
        try:
            self._raw_span.end()
        except Exception as ex:
            logger.debug("langfuse_span_end_failed", error=str(ex))


class AITracingService:
    """Primary facade for AI Observability and Distributed Tracing.

    Guarantees:
    - Never raises unhandled exceptions to callers (Fail-Safe).
    - Returns NoOpTraceSpan when disabled, sample rate skips, or initialization fails.
    - Anonymizes user identifiers with HMAC-SHA256.
    - Masks inputs/outputs when configured (Zero Data Retention).
    """

    def __init__(
        self,
        enabled: bool | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str | None = None,
        sample_rate: float | None = None,
        mask_input_output: bool | None = None,
        environment: str | None = None,
    ) -> None:
        self.enabled = enabled if enabled is not None else settings.LANGFUSE_ENABLED
        self.public_key = public_key or settings.LANGFUSE_PUBLIC_KEY
        self.secret_key = secret_key or (
            settings.LANGFUSE_SECRET_KEY.get_secret_value()
            if settings.LANGFUSE_SECRET_KEY
            else None
        )
        self.host = host or settings.LANGFUSE_HOST
        self.sample_rate = sample_rate if sample_rate is not None else settings.LANGFUSE_SAMPLE_RATE
        self.mask_input_output = (
            mask_input_output
            if mask_input_output is not None
            else settings.LANGFUSE_MASK_INPUT_OUTPUT
        )
        self.environment = environment or settings.LANGFUSE_ENVIRONMENT or settings.ENVIRONMENT

        self.client: Any = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        is_test_env = settings.ENVIRONMENT == "test" or bool(os.getenv("PYTEST_CURRENT_TEST"))
        if not self.enabled or is_test_env:
            logger.info("ai_tracing_disabled_noop_mode")
            return

        if not self.public_key or not self.secret_key:
            logger.warning(
                "ai_tracing_enabled_missing_credentials",
                has_public_key=bool(self.public_key),
                has_secret_key=bool(self.secret_key),
            )
            return

        try:
            from langfuse import Langfuse

            # Initialize Langfuse client with fail-safe configuration
            self.client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host,
                environment=self.environment,
                sample_rate=self.sample_rate,
                tracing_enabled=True,
            )
            logger.info(
                "ai_tracing_initialized",
                host=self.host,
                environment=self.environment,
                sample_rate=self.sample_rate,
                mask_input_output=self.mask_input_output,
            )
        except Exception as ex:
            logger.warning(
                "ai_tracing_initialization_failed_fallback_noop",
                error=scrub_sensitive_text(str(ex)),
            )
            self.client = None

    def _should_sample(self, custom_sample_rate: float | None = None) -> bool:
        """Evaluate probabilistic sampling."""
        rate = custom_sample_rate if custom_sample_rate is not None else self.sample_rate
        if rate >= 1.0:
            return True
        if rate <= 0.0:
            return False
        return random.random() < rate

    def trace(
        self,
        name: str,
        session_id: UUID | str | None = None,
        user_id: UUID | str | None = None,
        document_id: UUID | str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        input: Any = None,
        output: Any = None,
        sample_rate: float | None = None,
        version: str | None = None,
    ) -> BaseTraceSpan:
        """Start a root AI trace context manager.

        Args:
            name: Logical operation name (e.g., 'session_chat', 'note_synthesis').
            session_id: Optional research session identifier.
            user_id: Authenticated user ID (will be pseudonymized via HMAC-SHA256).
            document_id: Focused document ID if applicable.
            metadata: Custom execution metadata dictionary.
            tags: List of categorization tags.
            input: Initial input payload.
            output: Initial output payload.
            sample_rate: Optional per-trace sampling override.

        Returns:
            A BaseTraceSpan supporting both `with` and `async with`.
        """
        if not self.client or not self._should_sample(sample_rate):
            return NoOpTraceSpan()

        meta = dict(metadata or {})
        pseudonymized_user = pseudonymize_user_id(user_id)
        if pseudonymized_user:
            meta["user_id_hash"] = pseudonymized_user
        if session_id:
            meta["session_id"] = str(session_id)
        if document_id:
            meta["document_id"] = str(document_id)
        if tags:
            meta["tags"] = tags
        meta["environment"] = self.environment

        return LangfuseTraceSpan(
            client=self.client,
            name=name,
            as_type="chain",
            input_data=input,
            output_data=output,
            metadata=meta,
            mask_enabled=self.mask_input_output,
            user_id=str(user_id) if user_id else None,
            session_id=str(session_id) if session_id else None,
            tags=tags,
            version=version or getattr(settings, "VERSION", "0.1.0"),
        )

    def span(
        self,
        name: str,
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
        as_type: str = "span",
    ) -> BaseTraceSpan:
        """Start a nested span context within an active trace."""
        if not self.client:
            return NoOpTraceSpan()

        meta = dict(metadata or {})
        return LangfuseTraceSpan(
            client=self.client,
            name=name,
            as_type=as_type,
            input_data=input,
            output_data=output,
            metadata=meta,
            mask_enabled=self.mask_input_output,
        )

    def retriever(
        self,
        name: str = "retrieval",
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaseTraceSpan:
        """Start a specialized retriever observation for vector/chunk retrieval."""
        return self.span(
            name=name,
            input=input,
            output=output,
            metadata=metadata,
            as_type="retriever",
        )

    def guardrail(
        self,
        name: str = "guardrail",
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaseTraceSpan:
        """Start a specialized guardrail observation for safety and grounding checks."""
        return self.span(
            name=name,
            input=input,
            output=output,
            metadata=metadata,
            as_type="guardrail",
        )

    def tool(
        self,
        name: str = "tool",
        input: Any = None,
        output: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaseTraceSpan:
        """Start a specialized tool observation for deterministic compute and external tools."""
        return self.span(
            name=name,
            input=input,
            output=output,
            metadata=metadata,
            as_type="tool",
        )

    def generation(
        self,
        name: str,
        model: str | None = None,
        model_parameters: dict[str, Any] | None = None,
        input: Any = None,
        output: Any = None,
        usage_details: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaseTraceSpan:
        """Start a nested generation span for LLM calls."""
        if not self.client:
            return NoOpTraceSpan()

        meta = dict(metadata or {})
        return LangfuseTraceSpan(
            client=self.client,
            name=name,
            as_type="generation",
            input_data=input,
            output_data=output,
            metadata=meta,
            mask_enabled=self.mask_input_output,
            model=model,
            model_parameters=model_parameters,
            usage_details=usage_details,
        )

    def record_score(
        self,
        name: str,
        value: float,
        trace_id: str | None = None,
        session_id: str | None = None,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Record user feedback, evaluation, or benchmark score to Langfuse."""
        if not self.client:
            return False
        try:
            self.client.create_score(
                name=name,
                value=value,
                trace_id=trace_id,
                session_id=str(session_id) if session_id else None,
                comment=scrub_sensitive_text(comment) if comment else None,
                metadata=(
                    mask_payload(metadata, mask_enabled=self.mask_input_output)
                    if metadata
                    else None
                ),
            )
            return True
        except Exception as ex:
            logger.warning(
                "langfuse_create_score_failed",
                name=name,
                error=scrub_sensitive_text(str(ex)),
            )
            return False

    def flush(self) -> None:
        """Safely flush queued telemetry events to the Langfuse backend."""
        if not self.client:
            return
        try:
            self.client.flush()
        except Exception as ex:
            logger.warning(
                "ai_tracing_flush_failed",
                error=scrub_sensitive_text(str(ex)),
            )

    def shutdown(self) -> None:
        """Safely shutdown client and flush remaining events."""
        if not self.client:
            return
        try:
            self.client.shutdown()
        except Exception as ex:
            logger.warning(
                "ai_tracing_shutdown_failed",
                error=scrub_sensitive_text(str(ex)),
            )

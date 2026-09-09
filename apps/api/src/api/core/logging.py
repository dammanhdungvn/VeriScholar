import logging
import re
import sys
from typing import Any

import structlog
from api.core.config import settings
from structlog.types import EventDict, WrappedLogger

# Strict compiled regex for PII & sensitive tokens masking
SENSITIVE_KEY_RE = re.compile(
    r"(api[_-]?key|secret|token|password|auth|authorization|private[_-]?key)",
    re.IGNORECASE,
)
BEARER_RE = re.compile(r"^(Bearer\s+)[A-Za-z0-9\-_.]+=*", re.IGNORECASE)
API_KEY_VAL_RE = re.compile(
    r"\b(sk-[a-zA-Z0-9_-]{20,}|AIzaSy[a-zA-Z0-9_-]{25,40}|ghp_[a-zA-Z0-9]{36})\b"
)
REDACTED_STR = "***REDACTED***"


def mask_sensitive_value(key: str, value: Any) -> Any:
    """Masks a single value based on key name or content patterns."""
    if isinstance(value, str):
        if SENSITIVE_KEY_RE.search(key):
            if BEARER_RE.match(value):
                return BEARER_RE.sub(r"\1" + REDACTED_STR, value)
            return REDACTED_STR
        if BEARER_RE.match(value):
            return BEARER_RE.sub(r"\1" + REDACTED_STR, value)
        return API_KEY_VAL_RE.sub(REDACTED_STR, value)
    elif isinstance(value, dict):
        return {k: mask_sensitive_value(k, v) for k, v in value.items()}
    elif isinstance(value, list):
        return [mask_sensitive_value(key, item) for item in value]
    return value


def mask_pii_processor(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Structlog processor that sanitizes sensitive data from all event dict keys/values."""
    for key, val in list(event_dict.items()):
        event_dict[key] = mask_sensitive_value(key, val)
    return event_dict


def setup_logging() -> None:
    """Configures structlog and integrates with Python standard library logging.

    Enforces uniform JSON/Console output, PII masking, and contextvars propagation.
    Must be called at module load time before FastAPI app or Uvicorn startup.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        mask_pii_processor,
    ]

    if settings.LOG_FORMAT == "json" or settings.is_production:
        formatter_processor = structlog.processors.JSONRenderer()
    else:
        formatter_processor = structlog.dev.ConsoleRenderer(colors=True)

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Standard library logging handler with ProcessorFormatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                formatter_processor,
            ],
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Prevent noisy third-party loggers from flooding
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi", "httpx", "httpcore"]:
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [handler]
        std_logger.propagate = False
        std_logger.setLevel(log_level)

    # Completely mute uvicorn.access to prevent duplicate unformatted access logs
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = [logging.NullHandler()]
    uvicorn_access.propagate = False


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Returns a bound structlog logger instance."""
    return structlog.get_logger(name)

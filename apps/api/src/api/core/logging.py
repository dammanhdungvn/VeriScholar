import logging
import re
import sys
from typing import Any

import structlog
from api.core.config import settings
from structlog.types import EventDict, Processor, WrappedLogger

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
    """Structlog processor that masks sensitive tokens across keys and values."""
    for key, value in list(event_dict.items()):
        event_dict[key] = mask_sensitive_value(key, value)
    return event_dict


def setup_logging() -> None:
    """Configures structured JSON logging with request tracing context and PII masking.

    Must be called at module load time before FastAPI app or Uvicorn startup.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        mask_pii_processor,
    ]

    formatter_processor: Processor
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
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                formatter_processor,
            ],
        )
    )

    handlers: list[logging.Handler] = [console_handler]

    # Persistent Rotating Disk Logging for 30s Error Triage
    try:
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        json_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )

        audit_handler = logging.handlers.RotatingFileHandler(
            settings.LOGS_DIR / "api-audit.log",
            maxBytes=50 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )
        audit_handler.setFormatter(json_formatter)
        audit_handler.setLevel(log_level)
        handlers.append(audit_handler)

        error_handler = logging.handlers.RotatingFileHandler(
            settings.LOGS_DIR / "api-error.log",
            maxBytes=50 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )
        error_handler.setFormatter(json_formatter)
        error_handler.setLevel(logging.WARNING)
        handlers.append(error_handler)
    except Exception as exc:
        print(
            f"Warning: Failed to initialize rotating disk logging in {settings.LOGS_DIR}: {exc}",
            file=sys.stderr,
        )

    root_logger = logging.getLogger()
    root_logger.handlers = handlers
    root_logger.setLevel(log_level)

    # Prevent noisy third-party loggers from flooding
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi", "httpx", "httpcore"]:
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = handlers
        std_logger.propagate = False
        std_logger.setLevel(log_level)

    # Completely mute uvicorn.access to prevent duplicate unformatted access logs
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = [logging.NullHandler()]
    uvicorn_access.propagate = False


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Returns a bound structlog logger instance."""
    return structlog.get_logger(name)

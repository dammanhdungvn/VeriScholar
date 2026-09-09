import asyncio
from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.core.config import settings
from api.core.logging import setup_logging
from api.middleware.tracing import PureASGITracingMiddleware
from api.schemas.error import ErrorDetail, ErrorResponse

# 1. Setup logging system at module load time (strictly before FastAPI/Uvicorn startup)
setup_logging()
logger = structlog.get_logger("api.lifecycle")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for graceful startup and shutdown."""
    logger.info(
        "application_startup",
        log_type="lifecycle",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        host=settings.HOST,
        port=settings.PORT,
    )
    yield
    logger.info("application_shutdown", log_type="lifecycle")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Academic Research & Writing AI Assistant API",
    lifespan=lifespan,
)

# 2. Add Pure ASGI Tracing Middleware (must be outermost middleware)
app.add_middleware(PureASGITracingMiddleware)


# 3. Global Exception Handlers for Structured Error Envelopes
@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException | HTTPException
) -> JSONResponse:
    app_logger = structlog.get_logger("api.error")
    app_logger.warning(
        "http_exception",
        log_type="application",
        status_code=exc.status_code,
        detail=exc.detail,
    )
    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            action="Check the request parameters or route path.",
        ),
    )
    return JSONResponse(status_code=exc.status_code, content=error_payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    app_logger = structlog.get_logger("api.error")
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    loc = first_error.get("loc", ())
    field_name = " -> ".join(str(x) for x in loc) if loc else None
    msg = first_error.get("msg", "Validation error")

    app_logger.warning(
        "validation_error",
        log_type="application",
        errors_count=len(errors),
        first_error_msg=msg,
        field=field_name,
    )
    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message=msg,
            field=field_name,
            action="Ensure request payload matches the OpenAPI schema specification.",
        ),
        meta={"errors": errors},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_payload.model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app_logger = structlog.get_logger("api.error")
    app_logger.exception(
        "unhandled_server_exception",
        log_type="application",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )
    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred.",
            action="Please try again later or contact support if the issue persists.",
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload.model_dump(),
    )


# 4. Standard Core Endpoints
@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for container probes and uptime monitoring."""
    return {"status": "ok", "service": "verischolar-api"}


@app.get("/events", response_class=EventSourceResponse, tags=["streaming"])
async def demo_sse_events() -> AsyncIterable[ServerSentEvent]:
    """Demo Server-Sent Events (SSE) stream for verifying TTFB and non-buffering delivery."""
    for i in range(1, 4):
        await asyncio.sleep(0.05)
        yield ServerSentEvent(
            data={"step": i, "content": f"Streaming chunk {i}"},
            event="progress",
            id=str(i),
        )


def main() -> None:
    """Entrypoint for running the API server programmatically."""
    uvicorn.run(
        "api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=settings.RELOAD_DIRS,
        log_config=None,  # Handled by setup_logging()
    )


if __name__ == "__main__":
    main()

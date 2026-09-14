import asyncio
from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager
from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.core.config import settings
from api.core.logging import setup_logging
from api.middleware.tracing import PureASGITracingMiddleware
from api.schemas.error import ErrorDetail, ErrorResponse
from api.v1.router import api_v1_router

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

    if isinstance(exc.detail, dict):
        error_detail = ErrorDetail(
            code=str(exc.detail.get("code", f"HTTP_{exc.status_code}")),
            message=str(exc.detail.get("message", "An error occurred.")),
            field=exc.detail.get("field"),
            action=exc.detail.get("action", "Check the request parameters or route path."),
        )
    else:
        error_detail = ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            action="Check the request parameters or route path.",
        )

    error_payload = ErrorResponse(
        success=False,
        error=error_detail,
    )
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(),
        headers=headers,
    )


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
    clean_errors = []
    for err in errors:
        clean_err = dict(err)
        if "ctx" in clean_err and isinstance(clean_err["ctx"], dict):
            clean_err["ctx"] = {
                k: str(v) if isinstance(v, Exception) else v for k, v in clean_err["ctx"].items()
            }
        clean_errors.append(clean_err)

    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message=msg,
            field=field_name,
            action="Ensure request payload matches the OpenAPI schema specification.",
        ),
        meta={"errors": clean_errors},
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


# 4. Mount API Routes
app.include_router(api_v1_router)


# 5. Standard Core Endpoints
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


def custom_openapi() -> dict[str, Any]:
    """Generates custom OpenAPI schema ensuring explicit null fields in examples."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    star_path = openapi_schema.get("paths", {}).get("/api/v1/documents/{document_id}:star", {})
    post_op = star_path.get("post", {})
    req_body_json = post_op.get("requestBody", {}).get("content", {}).get("application/json", {})
    if "examples" in req_body_json and "without_folder" in req_body_json["examples"]:
        req_body_json["examples"]["without_folder"]["value"] = {"folder_id": None}

    components_schemas = openapi_schema.get("components", {}).get("schemas", {})
    if "DocumentStarRequest" in components_schemas:
        components_schemas["DocumentStarRequest"]["example"] = {"folder_id": None}
        components_schemas["DocumentStarRequest"]["examples"] = [
            {"folder_id": None},
            {"folder_id": "8a391512-4217-48f1-a1b7-d1fa18600d89"},
        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


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

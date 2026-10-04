"""FastAPI Main Application Factory with Lifespan and Structured Logging."""

import asyncio
from collections.abc import AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
import uvicorn
from core.domain.exceptions import (
    DomainError,
    DomainValidationError,
    EntityNotFoundError,
    InvariantViolationError,
)
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.middleware.tracing import PureASGITracingMiddleware
from api.schemas.error import ErrorDetail, ErrorResponse
from api.v1.router import api_v1_router

logger = structlog.get_logger("api.lifecycle")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager handling startup and shutdown events."""
    logger.info(
        "application_startup",
        log_type="lifecycle",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        host=settings.HOST,
        port=settings.PORT,
    )
    # Ensure all declared database tables exist
    import api.db.models  # noqa: F401
    from api.db.init_db import ensure_database_schema
    from api.db.models.base import Base
    from api.db.session import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_database_schema(conn)

    yield
    logger.info("application_shutdown", log_type="lifecycle")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Academic Research & Writing AI Assistant API",
    lifespan=lifespan,
)

# 2. Add Pure ASGI Tracing Middleware and CORS Middleware
app.add_middleware(PureASGITracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["ETag", "Location", "X-Request-ID", "Content-Disposition"],
)


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
        meta={
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    headers = getattr(exc, "headers", None) or {}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(mode="json"),
        headers=headers,
    )


@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Map pure core domain invariant violations to RFC 7807 structured HTTP error responses."""
    app_logger = structlog.get_logger("api.error")
    app_logger.warning(
        "domain_error",
        log_type="application",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )

    if isinstance(exc, EntityNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
        code = "ENTITY_NOT_FOUND"
        field = None
        action = "Check the entity identifier or verify that the resource exists."
    elif isinstance(exc, DomainValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        code = exc.code
        field = exc.field
        action = "Please upload a valid scholarly research paper with an extractable text layer."
    elif isinstance(exc, InvariantViolationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        code = "INVARIANT_VIOLATION"
        field = None
        action = "Ensure domain attributes and invariants satisfy business constraints."
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        code = "DOMAIN_ERROR"
        field = None
        action = "Verify that the request conforms to domain business logic."

    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code=code,
            message=str(exc),
            field=field,
            action=action,
        ),
        meta={
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    return JSONResponse(
        status_code=status_code,
        content=error_payload.model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    app_logger = structlog.get_logger("api.validation")
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    loc = first_error.get("loc", ())
    field_name = " -> ".join(str(x) for x in loc) if loc else None
    msg = first_error.get("msg", "Invalid input parameters")

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
            message=f"Validation failed for {field_name}: {msg}" if field_name else msg,
            field=field_name,
            action="Provide the correct field type and values as specified in the schema.",
        ),
        meta={
            "errors": clean_errors,
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_payload.model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Traps unhandled exceptions, logs structured details, and returns RFC 7807 500 envelope."""
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
        meta={
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload.model_dump(mode="json"),
    )


# 4. Include Versioned API Routers
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
        log_config=None,
    )


if __name__ == "__main__":
    main()

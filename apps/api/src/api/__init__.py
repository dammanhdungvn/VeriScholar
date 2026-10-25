"""FastAPI Main Application Factory with Lifespan and Structured Logging."""

import asyncio
import time
from collections.abc import AsyncIterator
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
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import setup_logging
from api.middleware.tracing import PureASGITracingMiddleware
from api.schemas.error import ErrorDetail, ErrorResponse
from api.v1.router import api_v1_router

# Configure structured JSON logging at module load
setup_logging()

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
    from sqlalchemy import text

    import api.db.models  # noqa: F401
    import api.db.session as db_session
    from api.db.init_db import ensure_database_schema
    from api.db.models.base import Base

    is_postgres = "postgres" in str(settings.DATABASE_URL).lower()

    for attempt in range(1, 4):
        try:
            async with db_session.engine.begin() as conn:
                if conn.dialect.name == "postgresql":
                    # Acquire advisory lock to prevent concurrent uvicorn workers
                    # from clashing on DDL
                    await conn.execute(text("SELECT pg_advisory_xact_lock(88991122)"))
                await conn.run_sync(Base.metadata.create_all)
                await ensure_database_schema(conn)
            break
        except Exception as exc:
            err_str = str(exc).lower()
            is_concurrency_error = any(
                k in err_str
                for k in (
                    "concurrently updated",
                    "deadlock",
                    "lock not available",
                    "serialization",
                )
            )
            if is_concurrency_error and attempt < 3:
                logger.warning(
                    "database_schema_concurrency_retry",
                    attempt=attempt,
                    error=str(exc),
                )
                await asyncio.sleep(0.4 * attempt)
                continue
            elif is_postgres:
                is_connection_error = any(
                    k in err_str
                    for k in (
                        "connection refused",
                        "cannot connect",
                        "could not translate host",
                        "connection reset",
                        "is the server running",
                    )
                )
                if is_connection_error:
                    logger.error(
                        "postgres_connection_failed",
                        error=str(exc),
                    )
                    break
                else:
                    logger.error("database_schema_initialization_error", error=str(exc))
                    break
            else:
                raise

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

    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id")
    error_payload = ErrorResponse(
        success=False,
        error=error_detail,
        meta={
            "request_id": req_id,
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    headers = dict(getattr(exc, "headers", None) or {})
    if req_id and "X-Request-ID" not in headers and "x-request-id" not in headers:
        headers["X-Request-ID"] = req_id
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
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
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

    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id")
    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code=code,
            message=str(exc),
            field=field,
            action=action,
        ),
        meta={
            "request_id": req_id,
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(
        status_code=status_code,
        content=error_payload.model_dump(mode="json"),
        headers=headers,
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

    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id")
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
            "request_id": req_id,
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_payload.model_dump(mode="json"),
        headers=headers,
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
    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id")
    error_payload = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred.",
            action="Please try again later or contact support if the issue persists.",
        ),
        meta={
            "request_id": req_id,
            "trace_id": getattr(request.state, "trace_id", None),
        },
    )
    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload.model_dump(mode="json"),
        headers=headers,
    )


# 4. Include Versioned API Routers
app.include_router(api_v1_router)


# 5. Standard Core Endpoints
@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root path to interactive OpenAPI documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for container probes and uptime monitoring."""
    return {"status": "ok", "service": "verischolar-api"}


@app.get("/health/live", tags=["system"])
async def liveness_probe() -> dict[str, Any]:
    """Liveness probe returning service metadata and active environment."""
    return {
        "status": "ok",
        "service": "verischolar-api",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }


@app.get("/health/ready", tags=["system"])
async def readiness_check() -> JSONResponse:
    """Deep readiness probe verifying PostgreSQL async connectivity and Storage writeability."""
    from sqlalchemy import text

    import api.db.session as db_session

    db_status = "ok"
    db_latency_ms = 0.0
    try:
        t0 = time.perf_counter()
        async with db_session.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    except Exception as exc:
        db_status = f"error: {type(exc).__name__}"

    storage_status = "ok"
    try:
        settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        test_file = settings.STORAGE_DIR / ".health_probe"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
    except Exception as exc:
        storage_status = f"error: {type(exc).__name__}"

    is_ready = db_status == "ok" and storage_status == "ok"
    res_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=res_status,
        content={
            "status": "ready" if is_ready else "unready",
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
            "checks": {
                "database": {"status": db_status, "latency_ms": db_latency_ms},
                "storage": {"status": storage_status},
                "langfuse": {
                    "enabled": settings.LANGFUSE_ENABLED,
                    "masked": settings.LANGFUSE_MASK_INPUT_OUTPUT,
                    "environment": settings.LANGFUSE_ENVIRONMENT,
                },
            },
        },
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

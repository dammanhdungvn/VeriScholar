import asyncio
import time
import uuid

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger("api.access")


class PureASGITracingMiddleware:
    """Pure ASGI Middleware for high-performance tracing, contextvars binding,

    accurate TTFB & Total Duration calculation, SSE stream support,
    and HTTP 499 Client Abort detection.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id: str | None = None
        headers = scope.get("headers", [])
        for name, value in headers:
            if name.lower() == b"x-request-id":
                request_id = value.decode("latin1")
                break

        if not request_id:
            request_id = str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=scope.get("method"),
            path=scope.get("path"),
        )

        start_time = time.perf_counter()
        ttfb_ms: float | None = None
        status_code = 500
        client_aborted = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, ttfb_ms
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                ttfb_ms = round((time.perf_counter() - start_time) * 1000, 2)

                res_headers = list(message.get("headers", []))
                res_headers.append((b"x-request-id", request_id.encode("latin1")))
                message = {**message, "headers": res_headers}

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except (asyncio.CancelledError, ConnectionResetError):
            client_aborted = True
            status_code = 499
            raise
        except Exception:
            status_code = 500
            raise
        finally:
            total_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_kwargs = {
                "log_type": "access",
                "status_code": status_code,
                "ttfb_ms": ttfb_ms if ttfb_ms is not None else total_duration_ms,
                "total_duration_ms": total_duration_ms,
                "client_aborted": client_aborted,
            }

            if status_code >= 500:
                logger.error("http_request_finished", **log_kwargs)
            elif status_code >= 400 or client_aborted:
                logger.warning("http_request_finished", **log_kwargs)
            else:
                logger.info("http_request_finished", **log_kwargs)

            structlog.contextvars.clear_contextvars()

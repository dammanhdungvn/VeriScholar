# ⚡ VeriScholar Backend API (`apps/api`)

The delivery and transport layer for VeriScholar, built with **FastAPI**, **Python 3.12**, and **Pure ASGI Middleware**. This service functions as the primary Driving Adapter in our Hexagonal (Clean) Architecture, exposing high-performance REST APIs, Server-Sent Events (SSE) streaming, and real-time observability.

---

## 🎯 Core Responsibilities

1. **Protocol Delivery:** Serve RESTful endpoints and real-time SSE streams to [`apps/web`](../web/).
2. **Observability & Tracing:** Outermost pure ASGI middleware capturing Time-To-First-Byte (TTFB), total latency, and distributed `X-Request-ID` propagation.
3. **Defensive Sanitization:** In-memory PII and secret redaction (`***REDACTED***`) for OpenAI keys, JWT tokens, and sensitive headers.
4. **Database Session Management:** Async SQLAlchemy 2.0 connection lifecycle with automatic driver normalization for `asyncpg`.
5. **Multi-Provider LLM Gateway:** Unified adapter switching between local Docker Model Runner (DMR) and Cloud LLMs (OpenAI, Gemini).

---

## 📁 Package Architecture

```text
apps/api/
├── src/
│   └── api/
│       ├── __init__.py           # App factory, lifespan context, exception handlers
│       ├── core/
│       │   ├── config.py         # Pydantic Settings with SecretStr & auto-normalizing DATABASE_URL
│       │   └── logging.py        # Structlog pipeline, processor formatters, PII filter
│       ├── middleware/
│       │   └── tracing.py        # Pure ASGI non-buffering tracing middleware
│       ├── routers/              # API route controllers
│       └── schemas/
│           └── error.py          # Unified ErrorResponse & ErrorDetail schemas
├── tests/
│   ├── __init__.py
│   └── test_logging.py           # Comprehensive logging & TTFB test suite (8 tests)
├── .env.example                  # Backend environment variable template
├── pyproject.toml                # UV package specification
└── README.md                     # This file
```

### Key Architectural Invariants
- **Pure ASGI Over `BaseHTTPMiddleware`:** Standard Starlette `BaseHTTPMiddleware` buffers memory and breaks response streaming. We use a raw ASGI middleware (`PureASGITracingMiddleware`) to intercept `http.response.start` for accurate TTFB without buffering chunks.
- **CPU Offloading:** Any CPU-heavy task (e.g., PDF rendering, large token chunking) is dispatched to worker threads via `asyncio.to_thread()` to keep the main event loop responsive.
- **Strict Error Envelope:** All errors return a predictable JSON payload:
  ```json
  {
    "error": {
      "code": "NOT_FOUND",
      "message": "Resource not found",
      "details": [],
      "request_id": "9c1fa8fe-1a24-41d6-b76d-68b2cf47aaaf"
    }
  }
  ```

---

## ⚙️ Configuration Reference

Configuration is managed via `api.core.config.Settings`, which reads from `apps/api/.env` or the workspace root `.env`.

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | `str` | `development` | Deployment mode: `development`, `staging`, `production`, `test`. |
| `HOST` | `str` | `0.0.0.0` | Bind IP for the Uvicorn ASGI server. |
| `PORT` | `int` | `8000` | Port for the Uvicorn ASGI server. |
| `DEBUG` | `bool` | `false` | Enable verbose tracebacks in responses. |
| `LOG_LEVEL` | `str` | `INFO` | Structlog level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `LOG_FORMAT` | `str` | `console` | `console` (colored via Rich) or `json` (single-line structured logs). |
| `DATABASE_URL` | `str` | *PostgreSQL URI* | Async connection string. Auto-converts `postgresql://` to `postgresql+asyncpg://`. |
| `LLM_PROVIDER` | `str` | `docker-model-runner` | Selected LLM backend: `docker-model-runner`, `openai`, `gemini`, `ollama`. |
| `DMR_BASE_URL` | `str` | `http://localhost:12434/engines/llama.cpp/v1` | Local Docker Model Runner endpoint. |
| `DMR_MODEL` | `str` | `ai/smollm2` | Target local model for Docker Model Runner. |
| `OPENAI_API_KEY` | `SecretStr`| `None` | OpenAI secret key (masked automatically in memory and logs). |
| `OPENAI_MODEL` | `str` | `gpt-5.6-luna` | OpenAI model identifier. |

---

## 📡 API Endpoints Catalog

| Method | Route | Description | Response Type |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service healthcheck & tracing probe | `application/json` |
| `GET` | `/events` | Real-time Server-Sent Events (SSE) stream probe | `text/event-stream` |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation | `text/html` |
| `GET` | `/redoc` | ReDoc alternative API documentation | `text/html` |

### Tracing Contract
All responses automatically include:
- `X-Request-ID`: Client-provided UUID or dynamically generated trace UUID.
- Access logs output fields: `ttfb_ms`, `total_duration_ms`, `status_code`, `client_aborted`.

---

## 🛠 Developer Workflow

### 1. Run Development Server
```bash
# From monorepo root:
uv run --package api api

# Server will start on http://localhost:8000 with hot-reload enabled across apps/api and packages/core
```

### 2. Execute Backend Test Suite
```bash
uv run pytest apps/api/tests/ -v -s
```

### 3. Verify Code Standards
```bash
uv run ruff check apps/api/
uv run ruff format --check apps/api/
```

### 4. Interactive Testing
```bash
# Verify Health Endpoint
curl -i http://localhost:8000/health

# Verify Custom Tracing Header Propagation
curl -i -H "X-Request-ID: test-custom-trace-001" http://localhost:8000/health

# Verify SSE Stream with TTFB
curl -N http://localhost:8000/events
```

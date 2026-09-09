from typing import Any

import pytest
from api import app
from api.core.logging import (
    REDACTED_STR,
    mask_pii_processor,
    mask_sensitive_value,
)
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field


@pytest.mark.asyncio
async def test_health_check_returns_200_and_request_id():
    """Verify /health returns 200 and generates or propagates X-Request-ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Without client request-id
        res1 = await client.get("/health")
        assert res1.status_code == 200
        assert res1.json() == {"status": "ok", "service": "verischolar-api"}
        assert "x-request-id" in res1.headers
        generated_id = res1.headers["x-request-id"]
        assert len(generated_id) > 0

        # 2. With client request-id
        custom_id = "test-req-id-12345"
        res2 = await client.get("/health", headers={"X-Request-ID": custom_id})
        assert res2.status_code == 200
        assert res2.headers["x-request-id"] == custom_id


def test_pii_masking_bearer_token():
    """Verify Bearer token is masked without exposing JWT / credentials."""
    token = (
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "e30.t-IDcSemACt8x4iTMCda8Yhe3iZaWbvV5XKSTbuAn0M"
    )
    masked = mask_sensitive_value("authorization", token)
    assert masked == f"Bearer {REDACTED_STR}"
    assert "eyJ" not in masked

    token_padded = "Bearer dGVzdF9zZWNyZXRfdmFsdWU="
    masked_padded = mask_sensitive_value("auth", token_padded)
    assert masked_padded == f"Bearer {REDACTED_STR}"


def test_pii_masking_api_keys():
    """Verify OpenAI, Google Gemini, and GitHub API keys are redacted."""
    openai_key = "sk-proj-1234567890abcdef1234567890"
    gemini_key = "AIzaSyD-1234567890abcdef1234567890abc"
    github_key = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

    assert mask_sensitive_value("api_key", openai_key) == REDACTED_STR
    assert mask_sensitive_value("gemini_secret", gemini_key) == REDACTED_STR
    assert (
        mask_sensitive_value("some_field", f"my key is {openai_key}") == f"my key is {REDACTED_STR}"
    )
    assert mask_sensitive_value("some_field", f"key={gemini_key}") == f"key={REDACTED_STR}"
    assert mask_sensitive_value("some_field", f"git={github_key}") == f"git={REDACTED_STR}"


def test_mask_pii_processor_nested_dict():
    """Verify structlog processor cleans nested event dictionaries."""
    event_dict: dict[str, Any] = {
        "event": "user_login",
        "password": "SuperSecretPassword123!",
        "headers": {
            "Authorization": "Bearer my_secret_token_123",
            "User-Agent": "Mozilla/5.0",
        },
        "details": [
            {"api_key": "sk-123456789012345678901234"},
            {"public_info": "visible"},
        ],
    }

    cleaned = mask_pii_processor(None, "info", event_dict)
    assert cleaned["password"] == REDACTED_STR
    assert cleaned["headers"]["Authorization"] == f"Bearer {REDACTED_STR}"
    assert cleaned["headers"]["User-Agent"] == "Mozilla/5.0"
    assert cleaned["details"][0]["api_key"] == REDACTED_STR
    assert cleaned["details"][1]["public_info"] == "visible"


@pytest.mark.asyncio
async def test_sse_streaming_endpoint():
    """Verify /events streams SSE events with valid headers and chunks."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/events")
        assert res.status_code == 200
        assert "text/event-stream" in res.headers.get("content-type", "")
        content = res.text
        assert "event: progress" in content
        assert "Streaming chunk 1" in content
        assert "Streaming chunk 3" in content


@pytest.mark.asyncio
async def test_error_handlers_return_structured_json():
    """Verify HTTP 404 error responses adhere to standard ErrorResponse schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_404 = await client.get("/non_existent_route")
        assert res_404.status_code == 404
        data_404 = res_404.json()
        assert data_404["success"] is False
        assert "error" in data_404
        assert data_404["error"]["code"] == "HTTP_404"
        assert data_404["error"]["message"] == "Not Found"


@pytest.mark.asyncio
async def test_validation_error_handler():
    """Verify 422 RequestValidationError returns structured ErrorResponse with field details."""
    test_router = APIRouter()

    class ItemPayload(BaseModel):
        title: str = Field(min_length=3)
        count: int = Field(gt=0)

    @test_router.post("/test-validation")
    async def create_item(payload: ItemPayload):
        return {"status": "created"}

    app.include_router(test_router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.post("/test-validation", json={"title": "a", "count": -5})
        assert res.status_code == 422
        data = res.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["field"] is not None
        assert "meta" in data
        assert len(data["meta"]["errors"]) > 0


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500():
    """Verify unhandled exception is trapped and returns structured 500 without crashing."""
    test_router = APIRouter()

    @test_router.get("/test-bug")
    async def trigger_bug():
        raise RuntimeError("Simulated unhandled database failure")

    app.include_router(test_router)

    # In httpx ASGITransport, set raise_app_exceptions=False to test 500 HTTP response output
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/test-bug")
        assert res.status_code == 500
        data = res.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "action" in data["error"]

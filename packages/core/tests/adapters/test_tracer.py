"""Unit tests for ITracerPort, NoopTracerAdapter, and LangfuseTracerAdapter."""

from unittest.mock import MagicMock

import pytest
from core.adapters.observability.tracer import LangfuseTracerAdapter, NoopTracerAdapter
from core.ports.tracer import ITracerPort


@pytest.mark.asyncio
async def test_noop_tracer_adapter_protocol_compliance() -> None:
    adapter = NoopTracerAdapter()
    assert isinstance(adapter, ITracerPort)

    # Calling trace methods does not raise
    await adapter.trace_generation(
        name="test-llm",
        model="smollm2",
        input_data={"prompt": "Hello"},
        output_data="World",
        prompt_name="academic_chat",
        prompt_version="1.0.0",
        usage={"total_tokens": 15},
    )
    await adapter.trace_event(name="user_opened_pdf", metadata={"doc_id": "123"})


@pytest.mark.asyncio
async def test_langfuse_tracer_disabled_without_keys() -> None:
    adapter = LangfuseTracerAdapter(public_key=None, secret_key=None)
    assert isinstance(adapter, ITracerPort)
    assert adapter._enabled is False

    # Trace calls are no-ops without error
    await adapter.trace_generation(
        name="test-llm",
        model="gpt-5.6-luna",
        input_data={"prompt": "Summarize"},
        output_data="Summary",
    )
    await adapter.trace_event(name="test_event")


@pytest.mark.asyncio
async def test_langfuse_tracer_with_mock_client() -> None:
    adapter = LangfuseTracerAdapter(
        public_key="pk-lf-test",
        secret_key="sk-lf-test",
        host="https://mock.langfuse.com",
    )
    mock_client = MagicMock()
    adapter._client = mock_client
    adapter._enabled = True

    await adapter.trace_generation(
        name="chat-generation",
        model="gemini-1.5-flash",
        input_data="What is p-value?",
        output_data="A p-value is...",
        prompt_name="academic_explain",
        prompt_version="2.0",
        usage={"input_tokens": 20, "output_tokens": 50, "total_tokens": 70},
        metadata={"user_id": "user-123"},
    )
    mock_client.generation.assert_called_once_with(
        name="chat-generation",
        model="gemini-1.5-flash",
        input="What is p-value?",
        output="A p-value is...",
        metadata={
            "user_id": "user-123",
            "prompt_name": "academic_explain",
            "prompt_version": "2.0",
        },
        usage={"input_tokens": 20, "output_tokens": 50, "total_tokens": 70},
    )

    await adapter.trace_event(
        name="citation_clicked",
        metadata={"citation_index": 2, "page": 4},
    )
    mock_client.event.assert_called_once_with(
        name="citation_clicked",
        metadata={"citation_index": 2, "page": 4},
    )

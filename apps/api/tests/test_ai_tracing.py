"""Unit and integration tests for AI Observability and Tracing Service (Langfuse)."""

import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from api.services.ai_tracing_service import (
    AITracingService,
    BaseTraceSpan,
    NoOpTraceSpan,
    mask_payload,
    pseudonymize_user_id,
    scrub_sensitive_text,
)


def test_ai_tracing_disabled_noop() -> None:
    """Verify that when disabled, AITracingService behaves as a silent, fail-safe No-Op."""
    service = AITracingService(enabled=False)
    assert service.client is None

    # Test root trace
    with service.trace("test_trace", user_id=uuid4()) as t:
        assert isinstance(t, BaseTraceSpan)
        assert isinstance(t, NoOpTraceSpan)
        t.set_input({"query": "what is attention?"})
        t.set_output({"result": "attention mechanism"})
        t.set_metadata({"key": "val"})
        t.update(level="DEFAULT", status_message="all good")
        t.record_exception(ValueError("sample error"))
        t.end()

    # Test span
    with service.span("test_span") as s:
        assert isinstance(s, NoOpTraceSpan)
        s.update(name="renamed")

    # Test generation
    with service.generation("test_gen", model="gpt-5.6-luna") as g:
        assert isinstance(g, NoOpTraceSpan)

    # Test flush and shutdown do not raise
    service.flush()
    service.shutdown()


@pytest.mark.asyncio
async def test_ai_tracing_async_context_manager() -> None:
    """Verify that NoOpTraceSpan and BaseTraceSpan support async context managers."""
    service = AITracingService(enabled=False)

    async with service.trace("async_trace") as t:
        assert isinstance(t, NoOpTraceSpan)
        t.set_output("async output")

    async with service.span("async_span") as s:
        assert isinstance(s, NoOpTraceSpan)

    async with service.generation("async_gen") as g:
        assert isinstance(g, NoOpTraceSpan)


def test_pseudonymize_user_id() -> None:
    """Verify HMAC-SHA256 user pseudonymization preserves privacy."""
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    salt = "test-salt-secret-key"

    h1 = pseudonymize_user_id(user_id, secret_key=salt)
    h2 = pseudonymize_user_id(user_id, secret_key=salt)

    # Deterministic for the same user and salt
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) == 64

    # Matches expected HMAC-SHA256 calculation
    expected = hmac.new(
        salt.encode("utf-8"),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    assert h1 == expected

    # Different user produces different hash
    h3 = pseudonymize_user_id(uuid4(), secret_key=salt)
    assert h1 != h3

    # Different salt produces different hash
    h4 = pseudonymize_user_id(user_id, secret_key="different-salt")
    assert h1 != h4

    # None and empty inputs return None
    assert pseudonymize_user_id(None) is None
    assert pseudonymize_user_id("") is None


def test_scrub_sensitive_text() -> None:
    """Verify scrubbing of Bearer tokens, API keys, passwords, and JWTs."""
    assert scrub_sensitive_text(None) == ""
    assert scrub_sensitive_text("") == ""

    # Bearer tokens
    raw_bearer = "Authorization: Bearer secret-token-value-123456789"
    scrubbed = scrub_sensitive_text(raw_bearer)
    assert "secret-token" not in scrubbed
    assert "Bearer [REDACTED]" in scrubbed

    # OpenAI API keys
    raw_openai = "Failed with key sk-proj-1234567890abcdef1234567890 in request"
    scrubbed = scrub_sensitive_text(raw_openai)
    assert "sk-proj" not in scrubbed
    assert "sk-[REDACTED]" in scrubbed

    # Gemini API keys
    raw_gemini = "Gemini key: AIzaSyD12345678901234567890123456789012"
    scrubbed = scrub_sensitive_text(raw_gemini)
    assert "AIzaSyD" not in scrubbed
    assert "AIzaSy[REDACTED]" in scrubbed

    # GitHub tokens
    raw_gh = "GitHub token ghp_1234567890abcdef1234567890"
    scrubbed = scrub_sensitive_text(raw_gh)
    assert "ghp_" not in scrubbed
    assert "gh-[REDACTED]" in scrubbed

    # Database URI with password
    raw_db = "Connecting to postgresql://verischolar:supersecretpassword@localhost:5432/verischolar"
    scrubbed = scrub_sensitive_text(raw_db)
    assert "supersecretpassword" not in scrubbed
    assert "verischolar:[REDACTED]@" in scrubbed


def test_zero_data_retention_masking() -> None:
    """Verify Zero Data Retention payload masking when enabled vs disabled."""
    sample_text = "The Transformer architecture relies entirely on self-attention mechanisms."

    # When mask_enabled=True: raw text replaced with character count and sha256 prefix
    masked = mask_payload(sample_text, mask_enabled=True)
    assert sample_text not in masked
    assert f"[MASKED_DATA: chars={len(sample_text)}, sha256=" in masked

    # Preserves empty string
    assert mask_payload("", mask_enabled=True) == ""
    assert mask_payload(None, mask_enabled=True) is None

    # Nested dictionary masking
    data = {
        "query": "explain attention",
        "nested": {
            "chunk_content": sample_text,
            "count": 42,
        },
        "tags": ["ml", "paper"],
    }
    masked_dict = mask_payload(data, mask_enabled=True)
    assert sample_text not in masked_dict["nested"]["chunk_content"]
    assert masked_dict["nested"]["count"] == 42
    assert "[MASKED_DATA" in masked_dict["query"]

    # When mask_enabled=False: text preserved, but secrets scrubbed
    unmasked = mask_payload(
        "Normal paper text with key sk-1234567890abcdef12345",
        mask_enabled=False,
    )
    assert "Normal paper text" in unmasked
    assert "sk-[REDACTED]" in unmasked


def test_ai_tracing_fail_safe_on_client_exception() -> None:
    """Verify tracing failures never bubble up or crash business workflows."""
    service = AITracingService(enabled=False)

    # Attach a faulty mock client
    mock_client = MagicMock()
    mock_client.start_as_current_observation.side_effect = RuntimeError("Langfuse timeout")
    mock_client.flush.side_effect = ConnectionResetError("Remote server closed connection")
    mock_client.shutdown.side_effect = TimeoutError("Shutdown timed out")
    service.client = mock_client

    # Starting a trace when client throws should degrade gracefully to no-op
    with service.trace("faulty_trace", user_id=uuid4()) as t:
        t.set_output({"status": "ok"})
        t.update(level="DEFAULT")

    # Flush and shutdown shouldn't crash
    service.flush()
    service.shutdown()


def test_ai_tracing_propagates_business_exceptions() -> None:
    """Verify that user-code exceptions inside a span block are NOT swallowed."""
    service = AITracingService(enabled=False)

    with pytest.raises(ZeroDivisionError):
        with service.trace("trace_with_error"):
            _ = 1 / 0


def test_ai_tracing_sampling_rate() -> None:
    """Verify sampling rate controls trace generation."""
    # sample_rate=0.0 -> never samples
    service_zero = AITracingService(enabled=True, sample_rate=0.0)
    service_zero.client = MagicMock()
    t = service_zero.trace("zero_sample_trace")
    assert isinstance(t, NoOpTraceSpan)

    # sample_rate=1.0 -> always samples if client present
    service_full = AITracingService(enabled=True, sample_rate=1.0)
    mock_client = MagicMock()
    mock_cm = MagicMock()
    mock_raw_span = MagicMock()
    mock_cm.__enter__.return_value = mock_raw_span
    mock_client.start_as_current_observation.return_value = mock_cm
    service_full.client = mock_client

    with service_full.trace("full_sample_trace", user_id=uuid4()) as trace_span:
        assert not isinstance(trace_span, NoOpTraceSpan)
        trace_span.set_output({"res": "done"})

    assert mock_client.start_as_current_observation.called
    assert mock_raw_span.update.called


def test_ai_tracing_with_mock_client_hierarchy() -> None:
    """Verify active trace captures user hash and tags in metadata."""
    user_id = uuid4()
    session_id = uuid4()
    doc_id = uuid4()

    mock_client = MagicMock()
    mock_cm = MagicMock()
    mock_span = MagicMock()
    mock_cm.__enter__.return_value = mock_span
    mock_client.start_as_current_observation.return_value = mock_cm

    service = AITracingService(enabled=True, sample_rate=1.0)
    service.client = mock_client

    with service.trace(
        name="session_chat",
        session_id=session_id,
        user_id=user_id,
        document_id=doc_id,
        metadata={"scope": "single_paper"},
        tags=["module1", "cot"],
    ) as t:
        with service.span("guardrail_check", input="is this safe?") as s:
            s.set_output({"is_safe": True})

        with service.generation(
            "llm_generation",
            model="gpt-5.6-luna",
            usage_details={"prompt_tokens": 50, "completion_tokens": 100},
        ) as g:
            g.set_output({"text": "response"})

        t.set_output({"finish_reason": "stop"})

    # Check root observation call parameters
    assert mock_client.start_as_current_observation.call_count >= 1
    root_call_kwargs = mock_client.start_as_current_observation.call_args_list[0].kwargs

    assert root_call_kwargs["name"] == "session_chat"
    meta = root_call_kwargs["metadata"]
    assert meta["session_id"] == str(session_id)
    assert meta["document_id"] == str(doc_id)
    assert meta["tags"] == ["module1", "cot"]
    assert "user_id_hash" in meta
    # Real user_id must NOT be exposed
    assert str(user_id) != meta["user_id_hash"]


@pytest.mark.asyncio
async def test_session_chat_service_tracing_integration() -> None:
    """Verify SessionChatService instruments guardrail, retrieval, context, and generation spans."""
    from api.db.models.session import ResearchSessionModel
    from api.schemas.session import SessionChatMessageRequest
    from api.services.session_chat_service import SessionChatService

    session_id = uuid4()
    user_id = uuid4()

    mock_db = MagicMock()
    mock_session_res = MagicMock()
    mock_session_model = ResearchSessionModel(
        id=session_id,
        user_id=user_id,
        title="Test Session",
        is_archived=False,
    )
    mock_session_res.scalar_one_or_none.return_value = mock_session_model
    mock_docs_res = MagicMock()
    mock_docs_res.scalars.return_value.all.return_value = []

    async def mock_execute(stmt: object, *args: object, **kwargs: object) -> object:
        s = str(stmt)
        if "research_sessions" in s:
            return mock_session_res
        return mock_docs_res

    mock_db.execute.side_effect = mock_execute
    mock_db.commit = AsyncMock()

    mock_tracing = MagicMock()
    mock_trace_span = MagicMock()
    mock_child_span = MagicMock()
    mock_tracing.trace.return_value = mock_trace_span
    mock_tracing.span.return_value = mock_child_span
    mock_tracing.generation.return_value = mock_child_span

    service = SessionChatService(db=mock_db, ai_tracing=mock_tracing)

    req = SessionChatMessageRequest(
        question="What is Multi-Head Attention?",
        scope="multi_paper",
    )

    async def is_disconnected() -> bool:
        return False

    events = [
        chunk async for chunk in service.stream_chat(session_id, user_id, req, is_disconnected)
    ]
    assert len(events) > 0

    # Verify trace and spans were invoked
    assert mock_tracing.trace.called
    assert mock_tracing.trace.call_args[1]["name"] == "session_chat"
    assert mock_tracing.trace.call_args[1]["user_id"] == user_id

    span_names = [call[1]["name"] for call in mock_tracing.span.call_args_list]
    assert "guardrail_check" in span_names
    assert "context_assembly" in span_names

    gen_names = [call[1]["name"] for call in mock_tracing.generation.call_args_list]
    assert "llm_generation" in gen_names


@pytest.mark.asyncio
async def test_note_synthesis_service_tracing_integration() -> None:
    """Verify NoteSynthesisService instruments note_synthesis, badge_assembly, and llm_synthesis."""
    from api.db.models.note import ResearchNoteModel
    from api.schemas.note import SynthesizeNotesRequest
    from api.services.note_synthesis_service import NoteSynthesisService

    user_id = uuid4()
    note_id = uuid4()

    mock_db = MagicMock()
    mock_note = ResearchNoteModel(
        id=note_id,
        user_id=user_id,
        selected_text="Self-attention allows the model to attend to information.",
        page_number=1,
        bounding_boxes=[[0.1, 0.2, 0.8, 0.4, 1]],
        user_note="Key finding",
        frozen_snapshot={
            "authors": ["Vaswani"],
            "year": 2017,
            "document_title": "Attention Paper",
        },
    )
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [mock_note]

    async def mock_execute(stmt: object, *args: object, **kwargs: object) -> object:
        return mock_res

    mock_db.execute.side_effect = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    mock_tracing = MagicMock()
    mock_trace_span = MagicMock()
    mock_child_span = MagicMock()
    mock_tracing.trace.return_value = mock_trace_span
    mock_tracing.span.return_value = mock_child_span
    mock_tracing.generation.return_value = mock_child_span

    service = NoteSynthesisService(db=mock_db, ai_tracing=mock_tracing)

    req = SynthesizeNotesRequest(
        note_ids=[note_id],
        mode="concept_lesson",
        language="vi",
    )
    resp = await service.synthesize_notes(user_id=user_id, req=req)
    assert resp is not None

    # Verify tracing
    assert mock_tracing.trace.called
    assert mock_tracing.trace.call_args[1]["name"] == "note_synthesis"

    span_names = [call[1]["name"] for call in mock_tracing.span.call_args_list]
    assert "badge_assembly" in span_names

    gen_names = [call[1]["name"] for call in mock_tracing.generation.call_args_list]
    assert "llm_synthesis" in gen_names


@pytest.mark.asyncio
async def test_document_service_summary_tracing_integration() -> None:
    """Verify DocumentService.generate_document_summary instruments document_summary & retrieval."""
    from api.db.models.document import DocumentModel
    from api.db.models.summary import DocumentSummaryModel
    from api.services.document_service import DocumentService
    from core.domain.value_objects.enums import DocumentStatus

    user_id = uuid4()
    doc_id = uuid4()

    mock_storage = MagicMock()
    mock_storage.blob_exists = MagicMock(return_value=False)

    mock_doc = DocumentModel(
        id=doc_id,
        user_id=user_id,
        title="Attention Is All You Need",
        status=DocumentStatus.COMPLETED.value,
        content_hash="dummy_hash",
        chunk_count=1,
    )
    mock_summary_model = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="RNNs are slow",
        problem_citations=[],
        contributions="Self-attention",
        contribution_citations=[],
        limitations="Quadratic memory",
        limitation_citations=[],
        total_tokens=100,
        latency_ms=200,
    )

    mock_db = MagicMock()

    async def mock_execute(stmt: object, *args: object, **kwargs: object) -> object:
        s = str(stmt)
        mock_r = MagicMock()
        if "documents" in s and "document_summaries" not in s:
            mock_r.scalar_one_or_none.return_value = mock_doc
        elif "document_summaries" in s:
            mock_r.scalar_one_or_none.return_value = mock_summary_model
        return mock_r

    mock_db.execute.side_effect = mock_execute

    mock_tracing = MagicMock()
    mock_trace_span = MagicMock()
    mock_child_span = MagicMock()
    mock_tracing.trace.return_value = mock_trace_span
    mock_tracing.span.return_value = mock_child_span

    service = DocumentService(storage=mock_storage, ai_tracing=mock_tracing)

    envelope, status_str = await service.generate_document_summary(
        document_id=doc_id,
        user_id=user_id,
        force=False,
        db=mock_db,
    )
    assert status_str == "Cache-Hit"
    assert envelope.success is True

    # Verify tracing
    assert mock_tracing.trace.called
    assert mock_tracing.trace.call_args[1]["name"] == "document_summary"
    span_names = [call[1]["name"] for call in mock_tracing.span.call_args_list]
    assert "summary_retrieval" in span_names

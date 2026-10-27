"""Unit tests for Langfuse Hierarchical Tree Tracing in Scholarly Literature Search."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from api import app
from api.adapters.scholarly_search_adapter import ScholarlySearchAdapter
from api.db.models.user import UserModel
from api.deps import get_current_user, get_scholarly_search_port
from api.services.ai_tracing_service import pseudonymize_user_id
from core.ports.scholarly_search import IScholarlySearchPort, ScholarlyPaperSearchResult
from httpx import ASGITransport, AsyncClient


class SpySpan:
    """Spy span context manager capturing hierarchical observation calls."""

    def __init__(
        self,
        name: str,
        initial_input: dict | None = None,
        initial_output: dict | None = None,
        metadata: dict | None = None,
    ):
        self.name = name
        self.input_data = initial_input
        self.output_data = initial_output
        self.metadata = metadata or {}
        self.entered = False
        self.exited = False
        self.user_id = None
        self.extra = {}

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    def set_input(self, input_data: dict):
        self.input_data = input_data

    def set_output(self, output_data: dict):
        self.output_data = output_data

    def set_metadata(self, metadata: dict):
        self.metadata.update(metadata)

    def update(self, **kwargs):
        if "input" in kwargs and kwargs["input"] is not None:
            self.input_data = kwargs["input"]
        if "output" in kwargs and kwargs["output"] is not None:
            self.output_data = kwargs["output"]
        if "metadata" in kwargs and kwargs["metadata"] is not None:
            self.metadata.update(kwargs["metadata"])


class SpyAITracingService:
    """Spy implementation of AITracingService capturing traces and spans."""

    def __init__(self):
        self.traces: list[SpySpan] = []
        self.spans: list[SpySpan] = []

    def trace(
        self,
        name: str,
        user_id: str | None = None,
        metadata: dict | None = None,
        input: dict | None = None,
        output: dict | None = None,
        **kwargs,
    ) -> SpySpan:
        span = SpySpan(
            name=name,
            initial_input=input,
            initial_output=output,
            metadata=metadata,
        )
        span.user_id = user_id
        span.extra = kwargs
        self.traces.append(span)
        return span

    def span(
        self,
        name: str,
        input: dict | None = None,
        output: dict | None = None,
        metadata: dict | None = None,
        **kwargs,
    ) -> SpySpan:
        span = SpySpan(
            name=name,
            initial_input=input,
            initial_output=output,
            metadata=metadata,
        )
        span.extra = kwargs
        self.spans.append(span)
        return span


@pytest.mark.asyncio
async def test_discovery_search_creates_langfuse_tree_with_all_spans(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test 1: Verify trace('discovery_search') and 4 child spans are created in sequence."""
    spy_tracing = SpyAITracingService()
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0, ai_tracing=spy_tracing)

    sample_exa_papers = [
        ScholarlyPaperSearchResult(
            title="Neural Architecture Search Survey",
            authors=["Alice Smith", "Bob Jones"],
            publication_year=2023,
            venue="IEEE TPAMI",
            doi="10.1109/TPAMI.2023.123456",
            arxiv_id=None,
            abstract="Comprehensive neural search survey.",
            access_status="open_access_pdf",
            pdf_url="https://example.com/paper.pdf",
            is_peer_reviewed=True,
        )
    ]
    sample_arxiv_papers = [
        ScholarlyPaperSearchResult(
            title="Denoising Diffusion Probabilistic Models",
            authors=["Jonathan Ho"],
            publication_year=2020,
            venue="arXiv",
            doi="10.48550/arXiv.2006.11239",
            arxiv_id="2006.11239",
            abstract="Diffusion models for image synthesis.",
            access_status="open_access_pdf",
            pdf_url="https://arxiv.org/pdf/2006.11239.pdf",
            is_peer_reviewed=False,
        )
    ]

    async def mock_search_exa(*args, **kwargs):
        return sample_exa_papers

    def mock_parse_arxiv_atom(*args, **kwargs):
        return sample_arxiv_papers

    monkeypatch.setattr(adapter, "_search_exa", mock_search_exa)
    monkeypatch.setattr(adapter, "_parse_arxiv_atom", mock_parse_arxiv_atom)

    class MockHttpxResponse:
        status_code = 200
        text = "<feed></feed>"

    async def mock_get(*args, **kwargs):
        return MockHttpxResponse()

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    raw_user_id = uuid4()
    results = await adapter.search(
        query="diffusion models for image generation",
        limit=5,
        is_peer_reviewed_only=False,
        user_id=raw_user_id,
    )

    # 1. Verify root trace
    assert len(spy_tracing.traces) == 1
    root_trace = spy_tracing.traces[0]
    assert root_trace.name == "discovery_search"
    assert root_trace.entered is True
    assert root_trace.exited is True
    assert root_trace.user_id == pseudonymize_user_id(raw_user_id)
    assert root_trace.metadata.get("limit") == 5
    assert root_trace.metadata.get("is_peer_reviewed_only") is False
    assert root_trace.output_data == {"total_results": len(results)}

    # 2. Verify 4 child spans created in exact sequence
    span_names = [s.name for s in spy_tracing.spans]
    assert span_names == [
        "query_decomposition",
        "exa_neural_search",
        "arxiv_api_search",
        "academic_rank_fusion",
    ]

    # Node 1 Span: query_decomposition
    s1 = spy_tracing.spans[0]
    assert s1.input_data == {"raw_query": "diffusion models for image generation"}
    assert s1.output_data["intent"] == "keyword_search"
    assert s1.output_data["identifier"] is None
    assert "diffusion" in s1.output_data["sub_topics"]

    # Node 2 Span: exa_neural_search
    s2 = spy_tracing.spans[1]
    assert s2.input_data == {
        "semantic_query": s1.output_data["semantic_query"],
        "limit": 5,
    }
    assert s2.output_data["count"] == 1
    assert s2.output_data["papers"][0]["title"] == "Neural Architecture Search Survey"
    assert s2.output_data["papers"][0]["doi"] == "10.1109/TPAMI.2023.123456"
    assert s2.output_data["papers"][0]["is_peer_reviewed"] is True

    # Node 3 Span: arxiv_api_search
    s3 = spy_tracing.spans[2]
    assert s3.input_data == {
        "query": s1.output_data["boolean_arxiv_query"],
        "limit": 5,
    }
    assert s3.output_data["count"] == 1
    assert s3.output_data["papers"][0]["title"] == "Denoising Diffusion Probabilistic Models"
    assert s3.output_data["papers"][0]["arxiv_id"] == "2006.11239"

    # Node 4 Span: academic_rank_fusion
    s4 = spy_tracing.spans[3]
    assert s4.input_data["candidate_count"] >= 2
    assert s4.input_data["is_peer_reviewed_only"] is False
    assert s4.output_data["final_count"] == len(results)
    assert s4.output_data["peer_reviewed_count"] == 1
    # Peer-reviewed paper must rank first
    assert results[0].title == "Neural Architecture Search Survey"


@pytest.mark.asyncio
async def test_direct_identifier_lookup_traces_cleanly():
    """Test 2: Search by arXiv ID creates query_decomposition and direct_identifier_lookup span."""
    spy_tracing = SpyAITracingService()
    adapter = ScholarlySearchAdapter(timeout_seconds=5.0, ai_tracing=spy_tracing)

    raw_user_id = "user-test-777"
    results = await adapter.search(
        query="2305.18290",
        limit=5,
        user_id=raw_user_id,
    )
    assert len(results) >= 1

    # 1. Verify Root Trace
    assert len(spy_tracing.traces) == 1
    root = spy_tracing.traces[0]
    assert root.name == "discovery_search"
    assert root.user_id == pseudonymize_user_id(raw_user_id)

    # 2. Verify Spans
    span_names = [s.name for s in spy_tracing.spans]
    assert "query_decomposition" in span_names
    assert "direct_identifier_lookup" in span_names
    assert "academic_rank_fusion" in span_names
    # Exa and arXiv keyword search should not be called for direct identifier lookup
    assert "exa_neural_search" not in span_names

    # Check query_decomposition output
    decomp_span = spy_tracing.spans[0]
    assert decomp_span.output_data["intent"] == "arxiv_lookup"
    assert decomp_span.output_data["identifier"] == "2305.18290"

    # Check direct_identifier_lookup span
    id_span = spy_tracing.spans[1]
    assert id_span.input_data == {"intent": "arxiv_lookup", "identifier": "2305.18290"}
    assert id_span.output_data["count"] >= 1
    assert any("Direct Preference Optimization" in title for title in id_span.output_data["papers"])

    # Check fusion output
    fusion_span = spy_tracing.spans[2]
    assert fusion_span.output_data["final_count"] >= 1


@pytest.mark.asyncio
async def test_discovery_endpoint_injects_user_into_tracing():
    """Test 3: POST /api/v1/discovery/search propagates user_id into search_port.search."""
    mock_search_port = AsyncMock(spec=IScholarlySearchPort)
    mock_search_port.search.return_value = [
        ScholarlyPaperSearchResult(
            title="Sample Tracing Paper",
            authors=["Jane Doe"],
            publication_year=2024,
            venue="NeurIPS",
            doi="10.1109/CVPR.2016.90",
            arxiv_id=None,
            abstract="Sample abstract",
            access_status="abstract_only",
            pdf_url=None,
            is_peer_reviewed=True,
        )
    ]

    test_user_id = uuid4()
    mock_user = UserModel(
        id=test_user_id,
        email="researcher@university.edu",
        full_name="Dr. Scholar",
        hashed_password="hash",
    )

    app.dependency_overrides[get_scholarly_search_port] = lambda: mock_search_port
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/discovery/search",
                json={
                    "query": "Quantum Error Correction",
                    "limit": 10,
                    "is_peer_reviewed_only": True,
                },
            )
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert len(data) == 1
            assert data[0]["title"] == "Sample Tracing Paper"

            # Verify mock_search_port.search was called with user_id=test_user_id
            mock_search_port.search.assert_awaited_once()
            call_kwargs = mock_search_port.search.await_args.kwargs
            call_args = mock_search_port.search.await_args.args

            # Check clean_query, limit, is_peer_reviewed_only, user_id
            query_passed = call_kwargs.get("query") or (call_args[0] if call_args else None)
            assert query_passed == "Quantum Error Correction"
            assert call_kwargs.get("limit") == 10
            assert call_kwargs.get("is_peer_reviewed_only") is True
            assert call_kwargs.get("user_id") == test_user_id
    finally:
        app.dependency_overrides.clear()

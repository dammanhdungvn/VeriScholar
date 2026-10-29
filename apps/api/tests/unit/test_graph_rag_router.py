"""Unit tests for GraphRAG Query Decomposer and Multi-Intent Router (Task 6)."""

from unittest.mock import AsyncMock

import pytest
from api.services.graph_rag_router import AcademicQueryDecomposer, GraphRAGRouter


@pytest.fixture
def mock_graph_service():
    service = AsyncMock()
    service.query_graph.return_value = {
        "mode_used": "hybrid",
        "answer": "Test synthesized response",
        "subgraph": {"nodes": [], "edges": [], "evidence": []},
        "evidence_chunks": [],
        "meta": {"trace_id": "test-trace"},
    }
    return service


@pytest.mark.asyncio
async def test_router_dispatches_macro_community_for_comparative_query(mock_graph_service):
    router = GraphRAGRouter(graph_service=mock_graph_service)
    res = await router.route_and_query(query="Tổng quan so sánh SOTA các mô hình Transformer")
    assert "community_macro_scan" in res["dispatched_tools"]


@pytest.mark.asyncio
async def test_router_dispatches_entity_subgraph_for_metric_query(mock_graph_service):
    router = GraphRAGRouter(graph_service=mock_graph_service)
    res = await router.route_and_query(
        query="Công thức tính và kết quả giảm bộ nhớ của Selective Attention"
    )
    assert "entity_subgraph_lookup" in res["dispatched_tools"]


@pytest.mark.asyncio
async def test_router_dispatches_bibliometric_trace_for_citation_query(mock_graph_service):
    router = GraphRAGRouter(graph_service=mock_graph_service)
    res = await router.route_and_query(query="Các bài báo trích dẫn và tài liệu nền tảng liên quan")
    assert "bibliometric_graph_trace" in res["dispatched_tools"]


def test_decomposer_identifies_intents():
    decomposer = AcademicQueryDecomposer()
    tools_macro = decomposer.decompose("Tổng quan xu hướng nghiên cứu LLM")
    assert "community_macro_scan" in tools_macro

    tools_micro = decomposer.decompose("Chỉ số BLEU score và dataset thực nghiệm")
    assert "entity_subgraph_lookup" in tools_micro

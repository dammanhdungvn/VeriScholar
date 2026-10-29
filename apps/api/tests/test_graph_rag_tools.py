from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.services.graph_rag_tools import (
    get_graph_rag_tool_schema,
    query_library_knowledge_graph,
)


@pytest.mark.asyncio
async def test_query_library_knowledge_graph_tool_delegates_to_service():
    mock_db = AsyncMock()
    user_id = uuid4()
    mock_graph_rag_service = MagicMock()
    mock_graph_rag_service.query_graph = AsyncMock(
        return_value={
            "answer": "Synthesized insight across community.",
            "citations": [],
            "subgraph": {
                "nodes": [
                    {"id": "doc-1", "label": "Paper 1", "community_id": 1},
                    {"id": "doc-2", "label": "Paper 2", "community_id": 2},
                ],
                "edges": [
                    {"source": "doc-1", "target": "doc-2", "relation": "CITES"},
                ],
            },
        }
    )

    result = await query_library_knowledge_graph(
        db=mock_db,
        user_id=user_id,
        query="Compare attention architectures",
        community_id=1,
        graph_rag_service=mock_graph_rag_service,
    )

    assert result["answer"] == "Synthesized insight across community."
    assert result["community_id"] == 1
    # Verify community filtering isolated community 1 nodes
    subgraph_nodes = result["subgraph"]["nodes"]
    assert len(subgraph_nodes) == 1
    assert subgraph_nodes[0]["id"] == "doc-1"
    mock_graph_rag_service.query_graph.assert_called_once()


@pytest.mark.asyncio
async def test_query_library_knowledge_graph_without_community_preserves_all_nodes():
    mock_db = AsyncMock()
    user_id = uuid4()
    mock_graph_rag_service = MagicMock()
    mock_graph_rag_service.query_graph = AsyncMock(
        return_value={
            "answer": "Full library search results.",
            "subgraph": {
                "nodes": [
                    {"id": "doc-1", "label": "Paper 1"},
                    {"id": "doc-2", "label": "Paper 2"},
                ],
                "edges": [],
            },
        }
    )

    result = await query_library_knowledge_graph(
        db=mock_db,
        user_id=user_id,
        query="Survey of transformers",
        community_id=None,
        graph_rag_service=mock_graph_rag_service,
    )

    assert result["answer"] == "Full library search results."
    assert len(result["subgraph"]["nodes"]) == 2


def test_get_graph_rag_tool_schema_contains_community_id():
    schema = get_graph_rag_tool_schema()
    assert schema["name"] == "query_library_knowledge_graph"
    assert "community_id" in schema["parameters"]["properties"]

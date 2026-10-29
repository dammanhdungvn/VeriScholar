"""GraphRAG Tools for Assistant and LangGraph ReAct Co-Author Agent.

Provides:
1. `query_library_knowledge_graph`: Asynchronous tool for GraphRAG retrieval.
2. `get_graph_rag_tool_schema`: Structured tool definition with community_id support.
"""

from __future__ import annotations

import inspect
from typing import Any
from uuid import UUID, uuid4

import structlog
from api.services.graph_rag_service import GraphRAGService
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.graph_rag_tools")


async def query_library_knowledge_graph(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    community_id: int | None = None,
    graph_rag_service: GraphRAGService | None = None,
    mode: str = "hybrid",
    top_k: int = 5,
) -> dict[str, Any]:
    """Execute GraphRAG retrieval on scholar's knowledge graph with optional community filtering.

    Parameters
    ----------
    db : AsyncSession
        Active database session.
    user_id : UUID
        Scholar user UUID.
    query : str
        Natural language research question or entity query.
    community_id : int | None
        Optional Louvain community ID to focus retrieval on.
    graph_rag_service : GraphRAGService | None
        GraphRAGService instance.
    mode : str
        Search mode ('local', 'global', 'hybrid').
    top_k : int
        Number of items to retrieve.
    """
    effective_service = graph_rag_service or GraphRAGService()

    sig = inspect.signature(effective_service.query_graph)
    kwargs: dict[str, Any] = {
        "query": query,
        "mode": mode,
        "top_k": top_k,
    }
    if "db" in sig.parameters:
        kwargs["db"] = db
    if "user_id" in sig.parameters:
        kwargs["user_id"] = user_id or uuid4()

    result = await effective_service.query_graph(**kwargs)

    # Attach community_id if specified
    if community_id is not None:
        result["community_id"] = community_id
        subgraph = result.get("subgraph")
        if isinstance(subgraph, dict):
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])
            # Filter nodes by community_id if the node property exists
            matching_nodes = [n for n in nodes if n.get("community_id") == community_id]
            if matching_nodes:
                matching_node_ids = {n.get("id") for n in matching_nodes}
                filtered_edges = [
                    e
                    for e in edges
                    if e.get("source") in matching_node_ids and e.get("target") in matching_node_ids
                ]
                result["subgraph"] = {
                    **subgraph,
                    "nodes": matching_nodes,
                    "edges": filtered_edges,
                }

    return result


def get_graph_rag_tool_schema() -> dict[str, Any]:
    """Return structured JSON schema for query_library_knowledge_graph."""
    return {
        "name": "query_library_knowledge_graph",
        "description": (
            "Query the scholar's personal knowledge graph and literature index. "
            "Supports local entity retrieval, global community synthesis, and optional "
            "filtering by Louvain community_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Scientific question, research topic, or methodology to search.",
                },
                "community_id": {
                    "type": "integer",
                    "description": "Optional Louvain cluster ID to restrict retrieval scope.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["local", "global", "hybrid"],
                    "description": "Search depth: local (1-hop), global (communities), or hybrid.",
                    "default": "hybrid",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of anchor results to retrieve (1..50).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    }

"""Schemas for Academic Knowledge Graph and Library queries."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class GraphQueryRequest(BaseModel):
    """Payload for querying the personal academic knowledge graph."""

    query: str = Field(
        ...,
        description="Scholarly synthesis or comparative question (3..1000 chars)",
        examples=["Các mô hình Transformer đạt kết quả BLEU và Accuracy như thế nào?"],
    )
    mode: Literal["auto", "local", "global", "hybrid"] = Field(
        default="auto",
        description=(
            "Search depth: 'auto' (smart router), 'local' (micro CTE), 'global' (macro), 'hybrid'"
        ),
        examples=["auto"],
    )
    folder_id: UUID | None = Field(
        default=None,
        description="Optional folder UUID filter",
        examples=[None],
    )
    community_id: int | None = Field(
        default=None,
        description="Optional community cluster ID filter",
        examples=[None],
    )
    top_k: int = Field(
        default=5,
        description="Number of anchor nodes or top communities (1..50)",
        examples=[5],
    )


class GraphQueryResponseData(BaseModel):
    """Data payload returned by GraphRAG query."""

    mode_used: str = Field(description="Depth strategy used: local, global, or hybrid")
    answer: str = Field(description="Synthesized scholarly answer")
    subgraph: dict[str, Any] = Field(
        description="Extracted knowledge subgraph with nodes, edges, and evidence chunks"
    )
    evidence_chunks: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Grounding evidence chunks with page numbers and bounding boxes",
    )
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Retrieval trace and match metadata",
    )


class GraphQueryResponseEnvelope(SingleResponseEnvelope[GraphQueryResponseData]):
    """Standard envelope for GraphRAG query with top-level field mirrors for Spec 05 contract."""

    mode_used: str | None = Field(default=None, description="Direct mirror of mode_used")
    answer: str | None = Field(default=None, description="Direct mirror of answer")
    subgraph: dict[str, Any] | None = Field(default=None, description="Direct mirror of subgraph")


class LibraryCommunity(BaseModel):
    """Topological community cluster detected via Louvain modularity optimization."""

    id: int = Field(description="Community cluster identifier (0..k)")
    label: str = Field(description="Representative cluster label")
    paper_count: int = Field(default=0, description="Number of papers in community")
    node_ids: list[str] = Field(default_factory=list, description="IDs of member nodes")


class LibraryGraphNode(BaseModel):
    """Knowledge graph node representing paper, concept, method, dataset, or metric."""

    id: str = Field(description="Unique node identifier")
    label: str = Field(description="Display label of the node")
    type: str = Field(
        default="Paper",
        description="Node entity type: Paper, Method, Dataset, MetricResult",
    )
    degree: int = Field(default=0, description="Connectivity degree in graph")
    group: str = Field(default="paper", description="Visual grouping category")
    community_id: int | None = Field(
        default=None,
        description="Assigned community cluster ID",
    )
    community_label: str | None = Field(
        default=None,
        description="Assigned community cluster label",
    )
    citation_count: int = Field(
        default=0,
        description="Count of inbound citations (in-degree of CITES relations)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata dictionary including abstract, publication_year, filename",
    )


class LibraryGraphEdge(BaseModel):
    """Knowledge graph edge representing relation between two nodes."""

    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    relation: str = Field(
        default="CITES",
        description="Relation type: CITES, USES_METHOD, EVALUATED_ON, RELATED",
    )
    label: str = Field(default="cites", description="Human-readable relation label")
    weight: float = Field(default=1.0, description="Edge weight / confidence")


class LibraryGraphResponseData(BaseModel):
    """Structured graph payload for personal academic knowledge graph (LLM Wiki)."""

    nodes: list[LibraryGraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: list[LibraryGraphEdge] = Field(default_factory=list, description="Graph edges")
    communities: list[LibraryCommunity] = Field(
        default_factory=list,
        description="Detected community clusters via Louvain modularity",
    )
    total_nodes: int = Field(default=0, description="Total node count")
    total_edges: int = Field(default=0, description="Total edge count")


class LibraryGraphResponseEnvelope(SingleResponseEnvelope[LibraryGraphResponseData]):
    """Standard envelope for Library Knowledge Graph."""

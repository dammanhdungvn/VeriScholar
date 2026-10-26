"""Database models for 4-Entity PostgreSQL GraphRAG."""

from typing import Any
from uuid import UUID

from api.db.models.base import IdentifiableTimestampedModel
from api.db.models.document import JSONType
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column


class GraphNodeModel(IdentifiableTimestampedModel):
    """Canonical knowledge graph node shared across papers for a user."""

    __tablename__ = "graph_nodes"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    node_type: Mapped[str] = mapped_column(String(30), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "node_type",
            "canonical_name",
            name="uq_graph_nodes_user_type_canonical",
        ),
        CheckConstraint(
            "node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult')",
            name="ck_graph_nodes_type",
        ),
        Index("idx_graph_nodes_user_canonical", "user_id", "canonical_name"),
    )

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


class GraphEdgeModel(IdentifiableTimestampedModel):
    """Typed academic relation between knowledge graph nodes."""

    __tablename__ = "graph_edges"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_node_id: Mapped[UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_node_id: Mapped[UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edge_type: Mapped[str] = mapped_column(String(30), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_chunk_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')",
            name="ck_graph_edges_type",
        ),
        Index("idx_graph_edges_source_target", "source_node_id", "target_node_id"),
        Index("idx_graph_edges_user_type", "user_id", "edge_type"),
    )

    def __init__(self, **kwargs: Any) -> None:
        if "weight" not in kwargs:
            self.weight = 1.0
        for k, v in kwargs.items():
            setattr(self, k, v)

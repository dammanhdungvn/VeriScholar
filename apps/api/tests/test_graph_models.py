"""Unit tests for 4-Entity PostgreSQL GraphRAG models (Task 5)."""

from uuid import uuid4

from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, UniqueConstraint


def test_graph_node_canonical_representation():
    """Verify GraphNodeModel attributes, table name and defaults."""
    user_id = uuid4()
    doc_id = uuid4()
    node = GraphNodeModel(
        user_id=user_id,
        document_id=doc_id,
        node_type="Method",
        canonical_name="transformer",
        display_name="Transformer",
        description="Attention-based sequence architecture",
        metadata_json={"family": "Attention", "year": 2017},
        embedding=[0.1] * 1536,
    )
    assert node.user_id == user_id
    assert node.document_id == doc_id
    assert node.node_type == "Method"
    assert node.canonical_name == "transformer"
    assert node.display_name == "Transformer"
    assert node.description == "Attention-based sequence architecture"
    assert node.metadata_json == {"family": "Attention", "year": 2017}
    assert len(node.embedding) == 1536
    assert GraphNodeModel.__tablename__ == "graph_nodes"


def test_graph_node_table_constraints():
    """Verify table constraints and Vector column on GraphNodeModel."""
    table = GraphNodeModel.__table__

    # Check unique constraint uq_graph_nodes_user_type_canonical
    unique_constraints = {c.name: c for c in table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_graph_nodes_user_type_canonical" in unique_constraints
    uq = unique_constraints["uq_graph_nodes_user_type_canonical"]
    uq_cols = {col.name for col in uq.columns}
    assert uq_cols == {"user_id", "node_type", "canonical_name"}

    # Check check constraint ck_graph_nodes_type
    check_constraints = {c.name: c for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_graph_nodes_type" in check_constraints
    assert "node_type IN ('Paper', 'Method', 'Dataset', 'MetricResult')" in str(
        check_constraints["ck_graph_nodes_type"].sqltext
    )

    # Check Vector(1536) embedding column
    assert "embedding" in table.c
    col = table.c["embedding"]
    assert isinstance(col.type, Vector)
    assert col.type.dim == 1536


def test_graph_edge_representation():
    """Verify GraphEdgeModel attributes, table name and defaults."""
    user_id = uuid4()
    doc_id = uuid4()
    source_id = uuid4()
    target_id = uuid4()
    chunk_id = uuid4()

    edge = GraphEdgeModel(
        user_id=user_id,
        document_id=doc_id,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_type="PROPOSES",
        weight=1.0,
        evidence_chunk_id=chunk_id,
    )
    assert edge.user_id == user_id
    assert edge.document_id == doc_id
    assert edge.source_node_id == source_id
    assert edge.target_node_id == target_id
    assert edge.edge_type == "PROPOSES"
    assert edge.weight == 1.0
    assert edge.evidence_chunk_id == chunk_id
    assert GraphEdgeModel.__tablename__ == "graph_edges"


def test_graph_edge_table_constraints():
    """Verify check constraints and indexes on GraphEdgeModel."""
    table = GraphEdgeModel.__table__

    # Check check constraint ck_graph_edges_type
    check_constraints = {c.name: c for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_graph_edges_type" in check_constraints
    assert "edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')" in str(
        check_constraints["ck_graph_edges_type"].sqltext
    )

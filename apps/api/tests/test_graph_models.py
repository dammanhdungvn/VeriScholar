"""Unit tests for 4-Entity PostgreSQL GraphRAG models."""

from uuid import uuid4

from api.db.models.graph import (
    FolderCommunitySummaryModel,
    GraphEdgeModel,
    GraphNodeModel,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, Integer, Text, UniqueConstraint


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
        page_number=5,
        metadata_json={"context": "empirical evaluation"},
    )
    assert edge.user_id == user_id
    assert edge.document_id == doc_id
    assert edge.source_node_id == source_id
    assert edge.target_node_id == target_id
    assert edge.edge_type == "PROPOSES"
    assert edge.weight == 1.0
    assert edge.evidence_chunk_id == chunk_id
    assert edge.page_number == 5
    assert edge.metadata_json == {"context": "empirical evaluation"}
    assert GraphEdgeModel.__tablename__ == "graph_edges"


def test_graph_edge_table_constraints():
    """Verify check constraints, columns, and indexes on GraphEdgeModel."""
    table = GraphEdgeModel.__table__

    # Check check constraint ck_graph_edges_type
    check_constraints = {c.name: c for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_graph_edges_type" in check_constraints
    assert "edge_type IN ('PROPOSES', 'EVALUATED_ON', 'ACHIEVES', 'CITES')" in str(
        check_constraints["ck_graph_edges_type"].sqltext
    )

    # Check page_number and metadata_json columns
    assert "page_number" in table.c
    col_page = table.c["page_number"]
    assert isinstance(col_page.type, Integer)
    assert col_page.nullable is True

    assert "metadata_json" in table.c
    col_meta = table.c["metadata_json"]
    assert col_meta.nullable is True


def test_folder_community_summary_model_representation():
    """Verify FolderCommunitySummaryModel attributes and table name."""
    user_id = uuid4()
    folder_id = uuid4()

    summary = FolderCommunitySummaryModel(
        user_id=user_id,
        folder_id=folder_id,
        summary_text="This community focuses on Transformer-based neural machine translation.",
        key_findings=[{"finding": "Attention improves BLEU scores"}],
        embedding=[0.05] * 1536,
    )
    assert summary.user_id == user_id
    assert summary.folder_id == folder_id
    assert (
        summary.summary_text
        == "This community focuses on Transformer-based neural machine translation."
    )
    assert summary.key_findings == [{"finding": "Attention improves BLEU scores"}]
    assert len(summary.embedding) == 1536
    assert FolderCommunitySummaryModel.__tablename__ == "folder_community_summaries"

    # Also test global root summary where folder_id is None
    global_summary = FolderCommunitySummaryModel(
        user_id=user_id,
        folder_id=None,
        summary_text="Global library summary across all topics.",
    )
    assert global_summary.folder_id is None


def test_folder_community_summary_table_constraints():
    """Verify columns, constraints, foreign keys, and indexes on FolderCommunitySummaryModel."""
    table = FolderCommunitySummaryModel.__table__

    assert table.name == "folder_community_summaries"

    # user_id
    assert "user_id" in table.c
    col_user = table.c["user_id"]
    assert col_user.nullable is False
    assert any(
        fk.target_fullname == "users.id" and fk.ondelete == "CASCADE"
        for fk in col_user.foreign_keys
    )

    # folder_id
    assert "folder_id" in table.c
    col_folder = table.c["folder_id"]
    assert col_folder.nullable is True
    assert any(
        fk.target_fullname == "folders.id" and fk.ondelete == "CASCADE"
        for fk in col_folder.foreign_keys
    )

    # summary_text
    assert "summary_text" in table.c
    col_text = table.c["summary_text"]
    assert isinstance(col_text.type, Text)
    assert col_text.nullable is False

    # key_findings
    assert "key_findings" in table.c
    col_findings = table.c["key_findings"]
    assert col_findings.nullable is True

    # embedding Vector(1536)
    assert "embedding" in table.c
    col_emb = table.c["embedding"]
    assert isinstance(col_emb.type, Vector)
    assert col_emb.type.dim == 1536
    assert col_emb.nullable is True

    # Unique constraint or index on (user_id, folder_id)
    unique_constraints = {c.name: c for c in table.constraints if isinstance(c, UniqueConstraint)}
    has_uq = any(
        {col.name for col in uq.columns} == {"user_id", "folder_id"}
        for uq in unique_constraints.values()
    )
    has_idx = any(
        {col.name for col in idx.columns} == {"user_id", "folder_id"} for idx in table.indexes
    )
    assert has_uq or has_idx

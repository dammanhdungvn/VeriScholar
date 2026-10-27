"""Tests for Dual-Level GraphRAG Query Engine (Local, Global, Hybrid & Multi-Tenant Isolation)."""

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.graph import (
    FolderCommunitySummaryModel,
    GraphEdgeModel,
    GraphNodeModel,
)
from api.db.models.user import UserModel
from api.services.graph_rag_service import GraphRAGService
from sqlalchemy.ext.asyncio import AsyncSession


def make_unit_vector(dim: int, index: int) -> list[float]:
    """Create a unit vector with 1.0 at index and 0.0 elsewhere."""
    vec = [0.0] * dim
    vec[index] = 1.0
    return vec


class MockEmbeddingService:
    """Mock embedding service returning deterministic vectors."""

    def __init__(self, mapping: dict[str, list[float]] | None = None) -> None:
        self.mapping = mapping or {}
        self.dim = 1536

    async def get_embedding(self, text: str) -> list[float]:
        for k, v in self.mapping.items():
            if k.lower() in text.lower():
                return v
        vec = [0.0] * self.dim
        idx = hash(text) % 500 + 10
        vec[idx] = 1.0
        return vec


@pytest_asyncio.fixture
async def user_a(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"scholar_a_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="TS. Học Giả A",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def user_b(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"scholar_b_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="TS. Học Giả B",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_folder(db_session: AsyncSession, user_a: UserModel) -> FolderModel:
    folder = FolderModel(
        id=uuid4(),
        user_id=user_a.id,
        name="NLP Transformers & Attention",
        color="#4F46E5",
        description="Thư mục nghiên cứu kiến trúc chú ý và các mô hình dịch máy",
    )
    db_session.add(folder)
    await db_session.flush()
    return folder


@pytest_asyncio.fixture
async def paper_vaswani(
    db_session: AsyncSession, user_a: UserModel, test_folder: FolderModel
) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=user_a.id,
        folder_id=test_folder.id,
        title="Attention Is All You Need",
        filename="vaswani2017.pdf",
        status="ready",
        content_hash=f"hash_vaswani_{uuid4().hex[:6]}",
        file_size_bytes=2048,
        page_count=15,
        chunk_count=10,
        is_starred=True,
    )
    db_session.add(doc)
    await db_session.flush()
    return doc


@pytest_asyncio.fixture
async def paper_vit(
    db_session: AsyncSession, user_a: UserModel, test_folder: FolderModel
) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=user_a.id,
        folder_id=test_folder.id,
        title="An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        filename="dosovitskiy2020.pdf",
        status="ready",
        content_hash=f"hash_vit_{uuid4().hex[:6]}",
        file_size_bytes=4096,
        page_count=22,
        chunk_count=14,
        is_starred=True,
    )
    db_session.add(doc)
    await db_session.flush()
    return doc


@pytest.mark.asyncio
async def test_local_query_mode_executes_2_step_cte_with_evidence_and_centrality(
    db_session: AsyncSession,
    user_a: UserModel,
    paper_vaswani: DocumentModel,
) -> None:
    """Test Local mode executes 2-step CTE (anchor nodes -> 1-hop edges -> chunks with bbox)."""
    v_query = make_unit_vector(1536, 1)
    v_transformer = make_unit_vector(1536, 1)  # high cosine similarity with query
    v_bleu = make_unit_vector(1536, 2)
    v_wmt = make_unit_vector(1536, 3)

    mock_embeddings = MockEmbeddingService(
        {
            "transformer": v_query,
            "Attention Is All You Need": make_unit_vector(1536, 4),
        }
    )

    # 1. Setup Document Chunks with spatial bounding boxes
    chunk_1 = DocumentChunkModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        chunk_index=0,
        page_number=3,
        content="The Transformer model relies entirely on self-attention mechanisms without recurrence.",
        bounding_boxes=[[72.0, 100.0, 520.0, 45.0]],
        token_count=18,
    )
    chunk_2 = DocumentChunkModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        chunk_index=1,
        page_number=8,
        content="On the WMT 2014 English-to-German translation task, the big transformer model achieves BLEU 28.4.",
        bounding_boxes=[[80.0, 240.0, 510.0, 55.0]],
        token_count=22,
    )
    db_session.add_all([chunk_1, chunk_2])
    await db_session.flush()

    # 2. Setup Graph Nodes (Paper, Method, Dataset, MetricResult)
    node_paper = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        node_type="Paper",
        canonical_name="attention is all you need",
        display_name="Attention Is All You Need",
        metadata_json={"year": 2017, "citation_key": "vaswani2017"},
        embedding=make_unit_vector(1536, 4),
    )
    node_method = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="Method",
        canonical_name="transformer",
        display_name="Transformer",
        metadata_json={"family": "Attention"},
        embedding=v_transformer,
    )
    node_metric = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="MetricResult",
        canonical_name="bleu: 28.4",
        display_name="BLEU: 28.4",
        metadata_json={
            "metric_name": "BLEU",
            "value": 28.4,
            "unit": "points",
            "task": "Translation",
            "split": "test",
        },
        embedding=v_bleu,
    )
    node_dataset = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="Dataset",
        canonical_name="wmt-2014 en-de",
        display_name="WMT-2014 En-De",
        metadata_json={"domain": "NLP"},
        embedding=v_wmt,
    )
    db_session.add_all([node_paper, node_method, node_metric, node_dataset])
    await db_session.flush()

    # 3. Setup Graph Edges with evidence chunks & page numbers
    edge_proposes = GraphEdgeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        source_node_id=node_paper.id,
        target_node_id=node_method.id,
        edge_type="PROPOSES",
        evidence_chunk_id=chunk_1.id,
        page_number=3,
    )
    edge_eval = GraphEdgeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        source_node_id=node_method.id,
        target_node_id=node_dataset.id,
        edge_type="EVALUATED_ON",
        evidence_chunk_id=chunk_2.id,
        page_number=8,
    )
    edge_achieves = GraphEdgeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        source_node_id=node_method.id,
        target_node_id=node_metric.id,
        edge_type="ACHIEVES",
        evidence_chunk_id=chunk_2.id,
        page_number=8,
    )
    db_session.add_all([edge_proposes, edge_eval, edge_achieves])
    await db_session.flush()

    # 4. Execute query in 'local' mode
    service = GraphRAGService(embedding_service=mock_embeddings)  # type: ignore[arg-type]
    result = await service.query_graph(
        db=db_session,
        user_id=user_a.id,
        query="Kiến trúc Transformer đạt kết quả BLEU như thế nào?",
        mode="local",
        top_k=5,
    )

    # 5. Assertions
    assert result["mode_used"] == "local"
    assert "subgraph" in result
    subgraph = result["subgraph"]
    nodes = subgraph["nodes"]
    edges = subgraph["edges"]
    assert len(nodes) >= 3
    assert len(edges) >= 2

    node_ids = [n["id"] for n in nodes]
    assert str(node_method.id) in node_ids
    assert str(node_metric.id) in node_ids

    # Check degree centrality and roles
    method_entry = next(n for n in nodes if n["id"] == str(node_method.id))
    assert method_entry["role"] == "method_hub"
    assert method_entry["degree_centrality"] >= 2

    metric_entry = next(n for n in nodes if n["id"] == str(node_metric.id))
    assert metric_entry["role"] == "metric"

    # Check evidence chunks with bounding box
    evidence_chunks = result.get("evidence_chunks") or subgraph.get("evidence")
    assert evidence_chunks is not None
    assert len(evidence_chunks) >= 1
    found_chunk_2 = next((c for c in evidence_chunks if c["chunk_id"] == str(chunk_2.id)), None)
    assert found_chunk_2 is not None
    assert found_chunk_2["bbox"] == [[80.0, 240.0, 510.0, 55.0]]
    assert found_chunk_2["page_number"] == 8

    # Check answer synthesis
    assert len(result["answer"]) > 20


@pytest.mark.asyncio
async def test_global_query_mode_scans_folder_summaries_and_hubs(
    db_session: AsyncSession,
    user_a: UserModel,
    test_folder: FolderModel,
) -> None:
    """Test Global mode uses folder community summaries and hub nodes to answer macro questions."""
    v_folder = make_unit_vector(1536, 10)
    mock_embeddings = MockEmbeddingService(
        {
            "tổng quan": v_folder,
            "transformer": v_folder,
        }
    )

    # Insert Community Summary
    summary = FolderCommunitySummaryModel(
        id=uuid4(),
        user_id=user_a.id,
        folder_id=test_folder.id,
        summary_text="Các nghiên cứu trong thư mục tập trung khai phá cơ chế Attention không cần hồi quy, đem lại bước nhảy vọt về tốc độ huấn luyện song song và hiệu năng dịch thuật.",
        key_findings=[
            "Cơ chế Multi-Head Attention thay thế hoàn toàn LSTM/GRU",
            "Mở rộng thành công sang bài toán thị giác máy tính qua Vision Transformer",
        ],
        embedding=v_folder,
    )
    # Insert a Method Hub node
    hub_node = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="Method",
        canonical_name="transformer",
        display_name="Transformer",
        metadata_json={"family": "Attention", "aliases": ["Transformer architecture"]},
        embedding=v_folder,
    )
    db_session.add_all([summary, hub_node])
    await db_session.flush()

    service = GraphRAGService(embedding_service=mock_embeddings)  # type: ignore[arg-type]
    result = await service.query_graph(
        db=db_session,
        user_id=user_a.id,
        query="Tổng quan các hướng tiếp cận và xu hướng trong thư mục này?",
        mode="global",
        folder_id=test_folder.id,
        top_k=5,
    )

    assert result["mode_used"] == "global"
    assert "Multi-Head Attention" in result["answer"] or "Attention" in result["answer"]
    assert "subgraph" in result
    hub_ids = [n["id"] for n in result["subgraph"]["nodes"]]
    assert str(hub_node.id) in hub_ids


@pytest.mark.asyncio
async def test_hybrid_query_mode_combines_macro_summary_and_micro_evidence(
    db_session: AsyncSession,
    user_a: UserModel,
    test_folder: FolderModel,
    paper_vaswani: DocumentModel,
) -> None:
    """Test Hybrid mode merges community context and empirical evidence chunks."""
    v_vec = make_unit_vector(1536, 5)
    mock_embeddings = MockEmbeddingService({"transformer": v_vec})

    summary = FolderCommunitySummaryModel(
        id=uuid4(),
        user_id=user_a.id,
        folder_id=test_folder.id,
        summary_text="Chủ đề nghiên cứu chuyển đổi mô hình tuần tự sang kiến trúc tự chú ý.",
        key_findings=["Hiệu năng SOTA trên bài toán dịch máy WMT 2014"],
        embedding=v_vec,
    )
    chunk = DocumentChunkModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        chunk_index=0,
        page_number=8,
        content="BLEU score of 28.4 on WMT En-De test split.",
        bounding_boxes=[[10.0, 20.0, 200.0, 40.0]],
        token_count=12,
    )
    node_paper = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        node_type="Paper",
        canonical_name="attention is all you need",
        display_name="Attention Is All You Need",
        metadata_json={"year": 2017},
        embedding=v_vec,
    )
    node_metric = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="MetricResult",
        canonical_name="bleu: 28.4",
        display_name="BLEU: 28.4",
        metadata_json={"metric_name": "BLEU", "value": 28.4},
        embedding=v_vec,
    )
    db_session.add_all([summary, chunk, node_paper, node_metric])
    await db_session.flush()

    edge = GraphEdgeModel(
        id=uuid4(),
        user_id=user_a.id,
        document_id=paper_vaswani.id,
        source_node_id=node_paper.id,
        target_node_id=node_metric.id,
        edge_type="ACHIEVES",
        evidence_chunk_id=chunk.id,
        page_number=8,
    )
    db_session.add(edge)
    await db_session.flush()

    service = GraphRAGService(embedding_service=mock_embeddings)  # type: ignore[arg-type]
    result = await service.query_graph(
        db=db_session,
        user_id=user_a.id,
        query="Transformer BLEU performance",
        mode="hybrid",
        folder_id=test_folder.id,
        top_k=5,
    )

    assert result["mode_used"] == "hybrid"
    assert "28.4" in result["answer"] or "BLEU" in result["answer"]
    assert len(result["subgraph"]["nodes"]) >= 2
    assert len(result["subgraph"]["edges"]) >= 1


@pytest.mark.asyncio
async def test_user_isolation_strictly_enforced_in_query_graph(
    db_session: AsyncSession,
    user_a: UserModel,
    user_b: UserModel,
) -> None:
    """Test user isolation: user_a never receives nodes/edges/chunks belonging to user_b."""
    v_shared = make_unit_vector(1536, 12)
    mock_embeddings = MockEmbeddingService({"secret": v_shared})

    # User B creates secret node and edge
    node_secret_b = GraphNodeModel(
        id=uuid4(),
        user_id=user_b.id,
        node_type="Method",
        canonical_name="secret private algorithm",
        display_name="Secret Algorithm",
        embedding=v_shared,
    )
    db_session.add(node_secret_b)
    await db_session.flush()

    service = GraphRAGService(embedding_service=mock_embeddings)  # type: ignore[arg-type]
    result_a = await service.query_graph(
        db=db_session,
        user_id=user_a.id,
        query="Tell me about secret private algorithm",
        mode="local",
        top_k=5,
    )

    # user_a must see ZERO nodes from user_b
    assert len(result_a["subgraph"]["nodes"]) == 0
    assert len(result_a["subgraph"]["edges"]) == 0
    assert "Secret" not in result_a["answer"]


@pytest.mark.asyncio
async def test_fallback_keyword_query_when_no_embeddings(
    db_session: AsyncSession,
    user_a: UserModel,
    paper_vaswani: DocumentModel,
) -> None:
    """Test keyword fallback in CTE anchor search when embedding_service is None."""
    node_method = GraphNodeModel(
        id=uuid4(),
        user_id=user_a.id,
        node_type="Method",
        canonical_name="transformer",
        display_name="Transformer Architecture",
        metadata_json={"family": "Attention"},
        embedding=None,  # No embedding
    )
    db_session.add(node_method)
    await db_session.flush()

    service = GraphRAGService(embedding_service=None)
    result = await service.query_graph(
        db=db_session,
        user_id=user_a.id,
        query="Transformer",
        mode="local",
        top_k=5,
    )

    assert result["mode_used"] == "local"
    assert len(result["subgraph"]["nodes"]) >= 1
    assert result["subgraph"]["nodes"][0]["name"] == "Transformer Architecture"

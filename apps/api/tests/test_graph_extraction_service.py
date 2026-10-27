"""Unit and integration tests for Incremental Graph Extraction & Semantic Disambiguation Service."""

import math
from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.document import DocumentModel
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.db.models.user import UserModel
from api.services.graph_extraction_service import GraphExtractionService
from core.services.graph_extractor import (
    ExtractedEntity,
    ExtractedGraphPayload,
    ExtractedRelation,
    MetricContextTuple,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def make_unit_vector(dim: int, index: int) -> list[float]:
    """Create a unit vector with 1.0 at index and 0.0 elsewhere."""
    vec = [0.0] * dim
    vec[index] = 1.0
    return vec


def make_similar_vector(
    dim: int, primary_index: int, secondary_index: int, similarity: float
) -> list[float]:
    """Create a unit vector having exact cosine similarity with unit vector at primary_index."""
    vec = [0.0] * dim
    vec[primary_index] = similarity
    vec[secondary_index] = math.sqrt(max(0.0, 1.0 - similarity * similarity))
    return vec


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"graph.scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Graph Scholar",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def paper_a(db_session: AsyncSession, test_user: UserModel) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=test_user.id,
        title="Attention Is All You Need",
        filename="attention.pdf",
        status="ready",
        content_hash=f"hash_attention_{uuid4().hex[:6]}",
        file_size_bytes=2048,
        page_count=15,
        chunk_count=10,
        is_starred=True,
    )
    db_session.add(doc)
    await db_session.flush()
    return doc


@pytest_asyncio.fixture
async def paper_b(db_session: AsyncSession, test_user: UserModel) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=test_user.id,
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        filename="bert.pdf",
        status="ready",
        content_hash=f"hash_bert_{uuid4().hex[:6]}",
        file_size_bytes=3072,
        page_count=16,
        chunk_count=12,
        is_starred=True,
    )
    db_session.add(doc)
    await db_session.flush()
    return doc


@pytest_asyncio.fixture
async def paper_c(db_session: AsyncSession, test_user: UserModel) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=test_user.id,
        title="An Isolated Algorithm Investigation",
        filename="isolated.pdf",
        status="ready",
        content_hash=f"hash_isolated_{uuid4().hex[:6]}",
        file_size_bytes=1024,
        page_count=8,
        chunk_count=5,
        is_starred=True,
    )
    db_session.add(doc)
    await db_session.flush()
    return doc


class MockEmbeddingService:
    """Deterministic mock embedding service returning predetermined vectors based on text."""

    def __init__(self, mapping: dict[str, list[float]] | None = None) -> None:
        self.mapping = mapping or {}
        self.dim = 1536

    async def get_embedding(self, text: str) -> list[float]:
        if text in self.mapping:
            return self.mapping[text]
        # Default orthogonal vector derived deterministically from text hash
        h = hash(text) % 1000 + 10
        vec = [0.0] * self.dim
        vec[h] = 1.0
        return vec


@pytest.mark.asyncio
async def test_1_star_paper_a_creates_new_hub(
    db_session: AsyncSession, test_user: UserModel, paper_a: DocumentModel
) -> None:
    """Test 1: Gắn sao bài báo A có phương pháp 'Transformer' -> tạo Hub mới trong graph_nodes."""
    v_transformer = make_unit_vector(1536, 0)
    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Transformer": v_transformer,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    payload = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )

    stats = await service.ingest_paper_graph(
        db=db_session,
        user_id=test_user.id,
        document_id=paper_a.id,
        payload=payload,
    )

    assert stats["nodes_created"] == 2
    assert stats["edges_created"] == 1

    # Verify Hub node created
    stmt = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Method",
        GraphNodeModel.canonical_name == "transformer",
    )
    res = await db_session.execute(stmt)
    hub_node = res.scalar_one_or_none()
    assert hub_node is not None
    assert hub_node.display_name == "Transformer"
    assert hub_node.embedding is not None


@pytest.mark.asyncio
async def test_2_star_paper_b_reuses_hub_with_alias_cosine_ge_90(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
    paper_b: DocumentModel,
) -> None:
    """Test 2: Gắn sao bài báo B có phương pháp 'The Transformer architecture' (Cosine >= 0.90)

    -> tái sử dụng Hub bài báo A, thêm alias, tạo cạnh mới trong graph_edges trỏ tới Hub đó,
    không tạo node thừa.
    """
    v_transformer = make_unit_vector(1536, 0)
    # Cosine similarity 0.95 >= 0.90 with v_transformer
    v_transformer_arch = make_similar_vector(1536, 0, 2, 0.95)

    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Transformer": v_transformer,
            "BERT: Pre-training of Deep Bidirectional Transformers": make_unit_vector(1536, 3),
            "The Transformer architecture": v_transformer_arch,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # 1. Ingest Paper A
    payload_a = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_a
    )

    # 2. Ingest Paper B with "The Transformer architecture"
    payload_b = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper",
                name="BERT: Pre-training of Deep Bidirectional Transformers",
                page_number=1,
            ),
            ExtractedEntity(type="Method", name="The Transformer architecture", page_number=2),
        ],
        relations=[
            ExtractedRelation(
                source_name="BERT: Pre-training of Deep Bidirectional Transformers",
                target_name="The Transformer architecture",
                type="PROPOSES",
                page_number=2,
            )
        ],
    )
    stats_b = await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id, payload=payload_b
    )

    # Only 1 new node for Paper B (itself), Method was merged into existing Hub
    assert stats_b["nodes_created"] == 1
    assert stats_b["nodes_merged"] == 1
    assert stats_b["edges_created"] == 1

    # Total Method nodes for this user MUST remain 1
    stmt_methods = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Method",
    )
    res_methods = await db_session.execute(stmt_methods)
    methods = res_methods.scalars().all()
    assert len(methods) == 1

    hub_node = methods[0]
    assert hub_node.canonical_name == "transformer"
    assert "The Transformer architecture" in hub_node.metadata_json.get("aliases", [])

    # Both edges must point to the same Hub node
    stmt_edges = select(GraphEdgeModel).where(
        GraphEdgeModel.user_id == test_user.id,
        GraphEdgeModel.target_node_id == hub_node.id,
    )
    res_edges = await db_session.execute(stmt_edges)
    edges = res_edges.scalars().all()
    assert len(edges) == 2
    doc_ids = {e.document_id for e in edges}
    assert doc_ids == {paper_a.id, paper_b.id}


@pytest.mark.asyncio
async def test_3_unstar_paper_a_prunes_edges_preserves_shared_hub(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
    paper_b: DocumentModel,
) -> None:
    """Test 3: Bỏ sao bài báo A (prune_document_graph) -> cạnh của bài báo A bị xóa,

    nhưng Hub 'Transformer' và cạnh của bài báo B VẪN NGUYÊN VẸN 100% (không bị xóa vì bài B đang dùng).
    """
    v_transformer = make_unit_vector(1536, 0)
    v_transformer_arch = make_similar_vector(1536, 0, 2, 0.95)

    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Transformer": v_transformer,
            "BERT: Pre-training of Deep Bidirectional Transformers": make_unit_vector(1536, 3),
            "The Transformer architecture": v_transformer_arch,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # Ingest Paper A & Paper B
    payload_a = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_a
    )

    payload_b = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper",
                name="BERT: Pre-training of Deep Bidirectional Transformers",
                page_number=1,
            ),
            ExtractedEntity(type="Method", name="The Transformer architecture", page_number=2),
        ],
        relations=[
            ExtractedRelation(
                source_name="BERT: Pre-training of Deep Bidirectional Transformers",
                target_name="The Transformer architecture",
                type="PROPOSES",
                page_number=2,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id, payload=payload_b
    )

    # Execute Prune on Paper A
    prune_stats = await service.prune_document_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id
    )
    assert prune_stats["edges_deleted"] >= 1

    # Verify paper A edges are gone
    stmt_a_edges = select(GraphEdgeModel).where(
        GraphEdgeModel.user_id == test_user.id,
        GraphEdgeModel.document_id == paper_a.id,
    )
    res_a_edges = await db_session.execute(stmt_a_edges)
    assert len(res_a_edges.scalars().all()) == 0

    # Verify Hub node 'Transformer' STILL EXISTS 100%
    stmt_hub = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Method",
        GraphNodeModel.canonical_name == "transformer",
    )
    res_hub = await db_session.execute(stmt_hub)
    hub_node = res_hub.scalar_one_or_none()
    assert hub_node is not None
    assert hub_node.display_name == "Transformer"

    # Verify paper B edge is STILL INTACT 100%
    stmt_b_edges = select(GraphEdgeModel).where(
        GraphEdgeModel.user_id == test_user.id,
        GraphEdgeModel.document_id == paper_b.id,
        GraphEdgeModel.target_node_id == hub_node.id,
    )
    res_b_edges = await db_session.execute(stmt_b_edges)
    b_edges = res_b_edges.scalars().all()
    assert len(b_edges) == 1


@pytest.mark.asyncio
async def test_4_unstar_deletes_orphan_node(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_c: DocumentModel,
) -> None:
    """Test 4: Khi xóa bài báo duy nhất sở hữu một đỉnh cô lập (orphan node)

    -> đỉnh đó bị dọn dẹp sạch sẽ khỏi graph_nodes.
    """
    mock_embeddings = MockEmbeddingService()
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    payload_c = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper", name="An Isolated Algorithm Investigation", page_number=1
            ),
            ExtractedEntity(type="Method", name="UniqueIsolatedAlgorithmXYZ", page_number=4),
        ],
        relations=[
            ExtractedRelation(
                source_name="An Isolated Algorithm Investigation",
                target_name="UniqueIsolatedAlgorithmXYZ",
                type="PROPOSES",
                page_number=4,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_c.id, payload=payload_c
    )

    # Check node was created
    stmt_check = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Method",
        GraphNodeModel.canonical_name == "uniqueisolatedalgorithmxyz",
    )
    res_check = await db_session.execute(stmt_check)
    assert res_check.scalar_one_or_none() is not None

    # Prune paper C
    prune_stats = await service.prune_document_graph(
        db=db_session, user_id=test_user.id, document_id=paper_c.id
    )
    assert prune_stats["nodes_pruned"] >= 1

    # Node MUST be cleanly purged from graph_nodes
    res_after = await db_session.execute(stmt_check)
    assert res_after.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_5_metric_results_preserve_independent_context_tuples(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
    paper_b: DocumentModel,
) -> None:
    """Test 5: Hai bài báo cùng trích xuất điểm số MetricResult nhưng khác context

    (ví dụ BLEU: 28.4 test set vs BLEU: 27.9 val set)
    -> lưu 2 node MetricResult độc lập với context_tuple không ghi đè.
    """
    mock_embeddings = MockEmbeddingService()
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # Paper A achieves BLEU: 28.4 on test set
    payload_a = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
            ExtractedEntity(
                type="MetricResult",
                name="BLEU: 28.4",
                page_number=8,
                context_tuple=MetricContextTuple(
                    dataset="WMT-2014 En-De",
                    task="Machine Translation",
                    split="test",
                    metric_name="BLEU",
                    value=28.4,
                    unit="points",
                ),
            ),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            ),
            ExtractedRelation(
                source_name="Transformer",
                target_name="BLEU: 28.4",
                type="ACHIEVES",
                page_number=8,
            ),
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_a
    )

    # Paper B achieves BLEU: 27.9 on val set
    payload_b = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper",
                name="BERT: Pre-training of Deep Bidirectional Transformers",
                page_number=1,
            ),
            ExtractedEntity(type="Method", name="BERT", page_number=2),
            ExtractedEntity(
                type="MetricResult",
                name="BLEU: 27.9",
                page_number=6,
                context_tuple=MetricContextTuple(
                    dataset="WMT-2014 En-De",
                    task="Machine Translation",
                    split="val",
                    metric_name="BLEU",
                    value=27.9,
                    unit="points",
                ),
            ),
        ],
        relations=[
            ExtractedRelation(
                source_name="BERT: Pre-training of Deep Bidirectional Transformers",
                target_name="BERT",
                type="PROPOSES",
                page_number=2,
            ),
            ExtractedRelation(
                source_name="BERT",
                target_name="BLEU: 27.9",
                type="ACHIEVES",
                page_number=6,
            ),
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id, payload=payload_b
    )

    # Check that 2 MetricResult nodes exist independently
    stmt = (
        select(GraphNodeModel)
        .where(
            GraphNodeModel.user_id == test_user.id,
            GraphNodeModel.node_type == "MetricResult",
        )
        .order_by(GraphNodeModel.created_at.asc())
    )
    res = await db_session.execute(stmt)
    metric_nodes = res.scalars().all()
    assert len(metric_nodes) == 2

    node_a = next(n for n in metric_nodes if n.document_id == paper_a.id)
    node_b = next(n for n in metric_nodes if n.document_id == paper_b.id)

    assert node_a.display_name == "BLEU: 28.4"
    assert node_a.metadata_json.get("split") == "test"
    assert node_a.metadata_json.get("value") == 28.4

    assert node_b.display_name == "BLEU: 27.9"
    assert node_b.metadata_json.get("split") == "val"
    assert node_b.metadata_json.get("value") == 27.9


@pytest.mark.asyncio
async def test_extract_paper_entities_fallback_parser() -> None:
    """Test extract_paper_entities fallback parser with raw text and JSON."""
    service = GraphExtractionService()

    # 1. Plain text with academic syntax
    text = (
        "Paper: Attention Is All You Need\n"
        "Method: Transformer\n"
        "Dataset: WMT-2014 En-De\n"
        "MetricResult: BLEU: 28.4\n"
        "Attention Is All You Need PROPOSES Transformer\n"
        "Transformer EVALUATED_ON WMT-2014 En-De\n"
        "Transformer ACHIEVES BLEU: 28.4\n"
    )
    payload = await service.extract_paper_entities(document_id=uuid4(), text=text)
    assert len(payload.entities) >= 3
    assert any(e.type == "Method" and e.name == "Transformer" for e in payload.entities)
    assert any(r.type == "PROPOSES" for r in payload.relations)

    # 2. JSON direct payload
    json_text = (
        '{"entities": [{"type": "Method", "name": "Mamba", "page_number": 1}], "relations": []}'
    )
    json_payload = await service.extract_paper_entities(document_id=uuid4(), text=json_text)
    assert len(json_payload.entities) == 1
    assert json_payload.entities[0].name == "Mamba"


@pytest.mark.asyncio
async def test_multi_tenant_user_isolation(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
) -> None:
    """User 1 và User 2 cùng nạp 'Transformer' -> tạo 2 Hub độc lập cho 2 user.

    Prune đồ thị của User 1 không ảnh hưởng đến đồ thị của User 2.
    """
    # Create User 2
    user_2 = UserModel(
        id=uuid4(),
        email=f"scholar2.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Scholar Two",
        role="scholar",
        is_active=True,
    )
    db_session.add(user_2)
    await db_session.flush()

    # Paper for User 2
    paper_user2 = DocumentModel(
        id=uuid4(),
        user_id=user_2.id,
        title="Attention Variations for User 2",
        filename="attention_user2.pdf",
        status="ready",
        content_hash=f"hash_u2_{uuid4().hex[:6]}",
        file_size_bytes=2048,
        page_count=12,
        chunk_count=6,
        is_starred=True,
    )
    db_session.add(paper_user2)
    await db_session.flush()

    v_transformer = make_unit_vector(1536, 0)
    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Attention Variations for User 2": make_unit_vector(1536, 2),
            "Transformer": v_transformer,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # Payload for User 1
    payload_u1 = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_u1
    )

    # Payload for User 2
    payload_u2 = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Variations for User 2", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=2),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Variations for User 2",
                target_name="Transformer",
                type="PROPOSES",
                page_number=2,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=user_2.id, document_id=paper_user2.id, payload=payload_u2
    )

    # Verify both users have distinct Hub nodes for 'Transformer'
    stmt_u1 = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.canonical_name == "transformer",
    )
    res_u1 = await db_session.execute(stmt_u1)
    hub_u1 = res_u1.scalar_one_or_none()
    assert hub_u1 is not None

    stmt_u2 = select(GraphNodeModel).where(
        GraphNodeModel.user_id == user_2.id,
        GraphNodeModel.canonical_name == "transformer",
    )
    res_u2 = await db_session.execute(stmt_u2)
    hub_u2 = res_u2.scalar_one_or_none()
    assert hub_u2 is not None

    assert hub_u1.id != hub_u2.id

    # Prune User 1's paper
    prune_res = await service.prune_document_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id
    )
    assert prune_res["nodes_pruned"] >= 1

    # Verify User 1's hub is deleted (as orphan for user 1)
    res_u1_after = await db_session.execute(stmt_u1)
    assert res_u1_after.scalar_one_or_none() is None

    # Verify User 2's hub and edge are 100% INTACT
    res_u2_after = await db_session.execute(stmt_u2)
    hub_u2_after = res_u2_after.scalar_one_or_none()
    assert hub_u2_after is not None
    assert hub_u2_after.id == hub_u2.id

    stmt_u2_edges = select(GraphEdgeModel).where(
        GraphEdgeModel.user_id == user_2.id,
        GraphEdgeModel.document_id == paper_user2.id,
    )
    res_u2_edges = await db_session.execute(stmt_u2_edges)
    u2_edges = res_u2_edges.scalars().all()
    assert len(u2_edges) == 1


@pytest.mark.asyncio
async def test_cosine_below_90_creates_new_node(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
    paper_b: DocumentModel,
) -> None:
    """Khi độ tương đồng cosine < 0.90 (ví dụ 0.80 hoặc 0.85)

    -> hệ thống tạo đỉnh mới riêng biệt, KHÔNG sáp nhập vào Hub.
    """
    v_transformer = make_unit_vector(1536, 0)
    # Cosine similarity 0.85 < 0.90 with v_transformer
    v_other_method = make_similar_vector(1536, 0, 2, 0.85)

    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Transformer": v_transformer,
            "BERT: Pre-training of Deep Bidirectional Transformers": make_unit_vector(1536, 3),
            "Recurrent Sequence Transducer": v_other_method,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # Ingest Paper A with Method "Transformer"
    payload_a = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_a
    )

    # Ingest Paper B with Method "Recurrent Sequence Transducer" (sim 0.85 < 0.90)
    payload_b = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper",
                name="BERT: Pre-training of Deep Bidirectional Transformers",
                page_number=1,
            ),
            ExtractedEntity(type="Method", name="Recurrent Sequence Transducer", page_number=2),
        ],
        relations=[
            ExtractedRelation(
                source_name="BERT: Pre-training of Deep Bidirectional Transformers",
                target_name="Recurrent Sequence Transducer",
                type="PROPOSES",
                page_number=2,
            )
        ],
    )
    stats_b = await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id, payload=payload_b
    )

    # Both entities in payload_b created as new nodes (NO merge!)
    assert stats_b["nodes_created"] == 2
    assert stats_b["nodes_merged"] == 0
    assert stats_b["edges_created"] == 1

    # Verify 2 distinct Method nodes exist for test_user
    stmt_methods = (
        select(GraphNodeModel)
        .where(
            GraphNodeModel.user_id == test_user.id,
            GraphNodeModel.node_type == "Method",
        )
        .order_by(GraphNodeModel.created_at.asc())
    )
    res_methods = await db_session.execute(stmt_methods)
    methods = res_methods.scalars().all()
    assert len(methods) == 2
    method_names = {m.display_name for m in methods}
    assert method_names == {"Transformer", "Recurrent Sequence Transducer"}


@pytest.mark.asyncio
async def test_complete_hub_lifecycle_both_papers_unstarred(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
    paper_b: DocumentModel,
) -> None:
    """Paper A unstar -> Hub được giữ lại; sau đó Paper B cũng unstar

    -> Hub trở thành đỉnh mồ côi (edge_count == 0) -> Hub bị dọn dẹp sạch sẽ khỏi graph_nodes.
    """
    v_transformer = make_unit_vector(1536, 0)
    v_transformer_arch = make_similar_vector(1536, 0, 2, 0.95)

    mock_embeddings = MockEmbeddingService(
        {
            "Attention Is All You Need": make_unit_vector(1536, 1),
            "Transformer": v_transformer,
            "BERT: Pre-training of Deep Bidirectional Transformers": make_unit_vector(1536, 3),
            "The Transformer architecture": v_transformer_arch,
        }
    )
    service = GraphExtractionService(embedding_service=mock_embeddings)  # type: ignore[arg-type]

    # Ingest Paper A & Paper B sharing Hub "Transformer"
    payload_a = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Paper", name="Attention Is All You Need", page_number=1),
            ExtractedEntity(type="Method", name="Transformer", page_number=3),
        ],
        relations=[
            ExtractedRelation(
                source_name="Attention Is All You Need",
                target_name="Transformer",
                type="PROPOSES",
                page_number=3,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload_a
    )

    payload_b = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(
                type="Paper",
                name="BERT: Pre-training of Deep Bidirectional Transformers",
                page_number=1,
            ),
            ExtractedEntity(type="Method", name="The Transformer architecture", page_number=2),
        ],
        relations=[
            ExtractedRelation(
                source_name="BERT: Pre-training of Deep Bidirectional Transformers",
                target_name="The Transformer architecture",
                type="PROPOSES",
                page_number=2,
            )
        ],
    )
    await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id, payload=payload_b
    )

    stmt_hub = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Method",
        GraphNodeModel.canonical_name == "transformer",
    )
    res_hub = await db_session.execute(stmt_hub)
    hub_node = res_hub.scalar_one_or_none()
    assert hub_node is not None

    # Step 1: Unstar Paper A
    stats_prune_a = await service.prune_document_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id
    )
    assert stats_prune_a["edges_deleted"] == 1
    # Hub must be preserved because Paper B still references it
    res_hub_after_a = await db_session.execute(stmt_hub)
    assert res_hub_after_a.scalar_one_or_none() is not None

    # Step 2: Unstar Paper B
    stats_prune_b = await service.prune_document_graph(
        db=db_session, user_id=test_user.id, document_id=paper_b.id
    )
    assert stats_prune_b["edges_deleted"] == 1
    # Hub edge_count is now 0 -> Hub MUST be pruned as an orphan node
    res_hub_after_b = await db_session.execute(stmt_hub)
    assert res_hub_after_b.scalar_one_or_none() is None

    # All nodes and edges for this user are now cleanly cleared
    stmt_all_nodes = select(GraphNodeModel).where(GraphNodeModel.user_id == test_user.id)
    res_all_nodes = await db_session.execute(stmt_all_nodes)
    assert len(res_all_nodes.scalars().all()) == 0

    stmt_all_edges = select(GraphEdgeModel).where(GraphEdgeModel.user_id == test_user.id)
    res_all_edges = await db_session.execute(stmt_all_edges)
    assert len(res_all_edges.scalars().all()) == 0


@pytest.mark.asyncio
async def test_openai_client_injection_used() -> None:
    """Test that injecting openai_client into GraphExtractionService uses the client instead of creating httpx.AsyncClient."""
    from unittest.mock import AsyncMock, MagicMock

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(
        return_value={
            "choices": [
                {
                    "message": {
                        "content": '{"entities": [{"type": "Method", "name": "InjectedModel", "page_number": 1}], "relations": []}'
                    }
                }
            ]
        }
    )
    mock_client.post = AsyncMock(return_value=mock_response)

    service = GraphExtractionService(openai_client=mock_client)
    payload = await service.extract_paper_entities(
        document_id=uuid4(), text="Some text to extract from"
    )

    assert mock_client.post.await_count == 1
    assert len(payload.entities) == 1
    assert payload.entities[0].name == "InjectedModel"


@pytest.mark.asyncio
async def test_canonical_name_length_truncation_safe(
    db_session: AsyncSession,
    test_user: UserModel,
    paper_a: DocumentModel,
) -> None:
    """Test that long entity name (> 250 characters) or long MetricResult context tokens are truncated/hashed safely <= 255 chars without DB error."""
    very_long_name = "ExtremelyLongMethodName_" + "x" * 300
    very_long_dataset = "ExtremelyLongDatasetName_" + "y" * 200

    service = GraphExtractionService()
    payload = ExtractedGraphPayload(
        entities=[
            ExtractedEntity(type="Method", name=very_long_name, page_number=1),
            ExtractedEntity(
                type="MetricResult",
                name="F1-Score",
                page_number=2,
                context_tuple=MetricContextTuple(
                    dataset=very_long_dataset,
                    task="SuperLongTaskName_" + "z" * 150,
                    split="test",
                    value=99.5,
                ),
            ),
        ],
        relations=[
            ExtractedRelation(
                source_name=very_long_name,
                target_name="F1-Score",
                type="ACHIEVES",
                page_number=2,
            )
        ],
    )

    stats = await service.ingest_paper_graph(
        db=db_session, user_id=test_user.id, document_id=paper_a.id, payload=payload
    )
    assert stats["nodes_created"] == 2
    assert stats["edges_created"] == 1

    # Verify canonical_name for both nodes is <= 255 chars in DB
    stmt = select(GraphNodeModel).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.document_id == paper_a.id,
    )
    res = await db_session.execute(stmt)
    nodes = res.scalars().all()
    assert len(nodes) == 2
    for node in nodes:
        assert len(node.canonical_name) <= 255
        assert len(node.display_name) <= 255

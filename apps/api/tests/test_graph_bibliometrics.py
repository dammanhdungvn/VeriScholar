"""Tests for Connected Papers Bibliometrics Service (Bibliographic Coupling, Prior & Derivative Works)."""

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.db.models.user import UserModel
from api.services.graph_rag_service import GraphRAGService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def scholar_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"bibliometrics_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="GS. Đỗ Thư Mục",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def other_scholar(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"other_{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="pw",
        full_name="GS. Học Giả Khác",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def folder_ml(db_session: AsyncSession, scholar_user: UserModel) -> FolderModel:
    folder = FolderModel(
        id=uuid4(),
        user_id=scholar_user.id,
        name="Thư mục Học máy & Xử lý ngôn ngữ",
        color="#10B981",
        description="Nghiên cứu về nền tảng Deep Learning",
    )
    db_session.add(folder)
    await db_session.flush()
    return folder


@pytest.mark.asyncio
async def test_bibliographic_coupling_detects_papers_with_min_shared_references(
    db_session: AsyncSession,
    scholar_user: UserModel,
    folder_ml: FolderModel,
) -> None:
    """Test Bibliographic Coupling detects pairs of papers sharing >= 2 references."""
    # Create papers in folder
    doc_a = DocumentModel(
        id=uuid4(),
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        title="Paper A: Transformer Extensions",
        filename="paper_a.pdf",
        status="ready",
        content_hash=f"hash_a_{uuid4().hex[:6]}",
        file_size_bytes=1024,
        is_starred=True,
    )
    doc_b = DocumentModel(
        id=uuid4(),
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        title="Paper B: Efficient Attention",
        filename="paper_b.pdf",
        status="ready",
        content_hash=f"hash_b_{uuid4().hex[:6]}",
        file_size_bytes=1024,
        is_starred=True,
    )
    doc_c = DocumentModel(
        id=uuid4(),
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        title="Paper C: Unrelated Vision Paper",
        filename="paper_c.pdf",
        status="ready",
        content_hash=f"hash_c_{uuid4().hex[:6]}",
        file_size_bytes=1024,
        is_starred=True,
    )
    db_session.add_all([doc_a, doc_b, doc_c])
    await db_session.flush()

    # Create Paper nodes
    node_paper_a = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_a.id,
        node_type="Paper",
        canonical_name="paper a: transformer extensions",
        display_name="Paper A: Transformer Extensions",
        metadata_json={"year": 2019, "citation_key": "author2019a"},
    )
    node_paper_b = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_b.id,
        node_type="Paper",
        canonical_name="paper b: efficient attention",
        display_name="Paper B: Efficient Attention",
        metadata_json={"year": 2020, "citation_key": "author2020b"},
    )
    node_paper_c = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_c.id,
        node_type="Paper",
        canonical_name="paper c: unrelated vision paper",
        display_name="Paper C: Unrelated Vision Paper",
        metadata_json={"year": 2021, "citation_key": "author2021c"},
    )

    # Reference nodes that are cited
    ref_1 = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="vaswani et al 2017",
        display_name="Attention Is All You Need",
        metadata_json={"year": 2017, "citation_key": "vaswani2017"},
    )
    ref_2 = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="bahdanau et al 2014",
        display_name="Neural Machine Translation by Jointly Learning to Align and Translate",
        metadata_json={"year": 2014, "citation_key": "bahdanau2014"},
    )
    ref_3 = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="srivastava et al 2014",
        display_name="Dropout: A Simple Way to Prevent Neural Networks from Overfitting",
        metadata_json={"year": 2014, "citation_key": "srivastava2014"},
    )
    db_session.add_all([node_paper_a, node_paper_b, node_paper_c, ref_1, ref_2, ref_3])
    await db_session.flush()

    # Paper A cites ref_1, ref_2, ref_3
    # Paper B cites ref_1, ref_2 (shares 2 refs with Paper A)
    # Paper C cites ref_1 only (shares 1 ref with Paper A, 1 ref with Paper B)
    edges = [
        # Paper A
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_a.id,
            source_node_id=node_paper_a.id,
            target_node_id=ref_1.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_a.id,
            source_node_id=node_paper_a.id,
            target_node_id=ref_2.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_a.id,
            source_node_id=node_paper_a.id,
            target_node_id=ref_3.id,
            edge_type="CITES",
        ),
        # Paper B
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_b.id,
            source_node_id=node_paper_b.id,
            target_node_id=ref_1.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_b.id,
            source_node_id=node_paper_b.id,
            target_node_id=ref_2.id,
            edge_type="CITES",
        ),
        # Paper C
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            document_id=doc_c.id,
            source_node_id=node_paper_c.id,
            target_node_id=ref_1.id,
            edge_type="CITES",
        ),
    ]
    db_session.add_all(edges)
    await db_session.flush()

    service = GraphRAGService()

    # Test with default min_shared_references = 2
    res_2 = await service.compute_bibliometrics(
        db=db_session,
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        min_shared_references=2,
    )
    coupling_2 = res_2["coupling_edges"]
    assert len(coupling_2) == 1
    pair = coupling_2[0]
    expected_ids = {str(node_paper_a.id), str(node_paper_b.id)}
    assert {pair["paper_a_id"], pair["paper_b_id"]} == expected_ids
    assert pair["shared_reference_count"] == 2

    # Test with min_shared_references = 1 (should include Paper C pairs as well)
    res_1 = await service.compute_bibliometrics(
        db=db_session,
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        min_shared_references=1,
    )
    coupling_1 = res_1["coupling_edges"]
    assert len(coupling_1) >= 3


@pytest.mark.asyncio
async def test_prior_and_derivative_works_classification(
    db_session: AsyncSession,
    scholar_user: UserModel,
) -> None:
    """Test identifying Prior Works (max In-Degree on CITES) & Derivative Works (max Out-Degree on CITES)."""
    # Create seminal paper (to be highly cited -> Prior Work)
    seminal_paper = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="deep residual learning",
        display_name="Deep Residual Learning for Image Recognition",
        metadata_json={"year": 2015, "citation_key": "he2015deep"},
    )
    # Create secondary classical paper
    secondary_paper = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="batch normalization",
        display_name="Batch Normalization: Accelerating Deep Network Training",
        metadata_json={"year": 2015, "citation_key": "ioffe2015batch"},
    )
    # Create survey / derivative paper (cites many papers -> Derivative Work)
    survey_paper = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="modern deep learning architectures: a comprehensive survey",
        display_name="Modern Deep Learning Architectures: A Comprehensive Survey",
        metadata_json={"year": 2023, "citation_key": "survey2023"},
    )
    # Create another citing paper
    appl_paper = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="resnet application in medical imaging",
        display_name="ResNet Application in Medical Imaging",
        metadata_json={"year": 2021, "citation_key": "appl2021"},
    )
    db_session.add_all([seminal_paper, secondary_paper, survey_paper, appl_paper])
    await db_session.flush()

    # Edges:
    # survey_paper cites: seminal_paper, secondary_paper, appl_paper (out_degree = 3)
    # appl_paper cites: seminal_paper (out_degree = 1)
    # seminal_paper is cited by: survey_paper, appl_paper (in_degree = 2)
    # secondary_paper is cited by: survey_paper (in_degree = 1)
    edges = [
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            source_node_id=survey_paper.id,
            target_node_id=seminal_paper.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            source_node_id=survey_paper.id,
            target_node_id=secondary_paper.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            source_node_id=survey_paper.id,
            target_node_id=appl_paper.id,
            edge_type="CITES",
        ),
        GraphEdgeModel(
            id=uuid4(),
            user_id=scholar_user.id,
            source_node_id=appl_paper.id,
            target_node_id=seminal_paper.id,
            edge_type="CITES",
        ),
    ]
    db_session.add_all(edges)
    await db_session.flush()

    service = GraphRAGService()
    res = await service.compute_bibliometrics(db=db_session, user_id=scholar_user.id)

    # 1. Prior Works check
    prior_works = res["prior_works"]
    assert len(prior_works) >= 2
    assert prior_works[0]["id"] == str(seminal_paper.id)
    assert prior_works[0]["in_degree"] == 2
    assert prior_works[0]["title"] == "Deep Residual Learning for Image Recognition"
    assert prior_works[0]["citation_key"] == "he2015deep"

    # 2. Derivative Works check
    derivative_works = res["derivative_works"]
    assert len(derivative_works) >= 1
    assert derivative_works[0]["id"] == str(survey_paper.id)
    assert derivative_works[0]["out_degree"] == 3
    assert derivative_works[0]["citation_key"] == "survey2023"


@pytest.mark.asyncio
async def test_bibliometrics_user_isolation(
    db_session: AsyncSession,
    scholar_user: UserModel,
    other_scholar: UserModel,
) -> None:
    """Test bibliometrics does not leak other scholars' papers or citations."""
    node_other_1 = GraphNodeModel(
        id=uuid4(),
        user_id=other_scholar.id,
        node_type="Paper",
        canonical_name="other paper 1",
        display_name="Other Paper 1",
        metadata_json={"year": 2022},
    )
    node_other_2 = GraphNodeModel(
        id=uuid4(),
        user_id=other_scholar.id,
        node_type="Paper",
        canonical_name="other paper 2",
        display_name="Other Paper 2",
        metadata_json={"year": 2023},
    )
    db_session.add_all([node_other_1, node_other_2])
    await db_session.flush()

    edge_other = GraphEdgeModel(
        id=uuid4(),
        user_id=other_scholar.id,
        source_node_id=node_other_2.id,
        target_node_id=node_other_1.id,
        edge_type="CITES",
    )
    db_session.add(edge_other)
    await db_session.flush()

    service = GraphRAGService()
    res = await service.compute_bibliometrics(db=db_session, user_id=scholar_user.id)

    # Scholar user must not see other scholar's papers
    prior_ids = [p["id"] for p in res["prior_works"]]
    deriv_ids = [d["id"] for d in res["derivative_works"]]
    assert str(node_other_1.id) not in prior_ids
    assert str(node_other_2.id) not in deriv_ids


@pytest.mark.asyncio
async def test_bibliometrics_folder_filter(
    db_session: AsyncSession,
    scholar_user: UserModel,
    folder_ml: FolderModel,
) -> None:
    """Test bibliometrics with folder_id only computes metrics for papers in that folder."""
    # Another folder
    other_folder = FolderModel(
        id=uuid4(),
        user_id=scholar_user.id,
        name="Thư mục Hệ điều hành",
        color="#EF4444",
    )
    db_session.add(other_folder)
    await db_session.flush()

    # Doc in folder_ml
    doc_ml = DocumentModel(
        id=uuid4(),
        user_id=scholar_user.id,
        folder_id=folder_ml.id,
        title="ML Paper",
        filename="ml.pdf",
        status="ready",
        content_hash=f"h_ml_{uuid4().hex[:6]}",
        file_size_bytes=100,
        is_starred=True,
    )
    # Doc in other_folder
    doc_os = DocumentModel(
        id=uuid4(),
        user_id=scholar_user.id,
        folder_id=other_folder.id,
        title="OS Paper",
        filename="os.pdf",
        status="ready",
        content_hash=f"h_os_{uuid4().hex[:6]}",
        file_size_bytes=100,
        is_starred=True,
    )
    db_session.add_all([doc_ml, doc_os])
    await db_session.flush()

    node_ml = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_ml.id,
        node_type="Paper",
        canonical_name="ml paper",
        display_name="ML Paper",
        metadata_json={"year": 2022},
    )
    node_os = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_os.id,
        node_type="Paper",
        canonical_name="os paper",
        display_name="OS Paper",
        metadata_json={"year": 2020},
    )
    ref_classic = GraphNodeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        node_type="Paper",
        canonical_name="classic reference",
        display_name="Classic Reference",
        metadata_json={"year": 2010},
    )
    db_session.add_all([node_ml, node_os, ref_classic])
    await db_session.flush()

    # Both cite ref_classic, but belong to different folders
    edge_ml = GraphEdgeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_ml.id,
        source_node_id=node_ml.id,
        target_node_id=ref_classic.id,
        edge_type="CITES",
    )
    edge_os = GraphEdgeModel(
        id=uuid4(),
        user_id=scholar_user.id,
        document_id=doc_os.id,
        source_node_id=node_os.id,
        target_node_id=ref_classic.id,
        edge_type="CITES",
    )
    db_session.add_all([edge_ml, edge_os])
    await db_session.flush()

    service = GraphRAGService()

    # Query folder_ml only:
    res_ml = await service.compute_bibliometrics(
        db=db_session, user_id=scholar_user.id, folder_id=folder_ml.id
    )
    deriv_ids_ml = [d["id"] for d in res_ml["derivative_works"]]
    assert str(node_ml.id) in deriv_ids_ml
    assert str(node_os.id) not in deriv_ids_ml

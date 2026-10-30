"""Integration test verifying 4-entity ontology and typed edges seeded for landmark papers."""

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.db.models.user import UserModel
from api.services.landmark_papers_seeder import seed_landmark_papers_for_user
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=f"graph.seeder.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Graph Seeder",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_seeder_creates_4_entity_types_and_typed_edges(
    db_session: AsyncSession, test_user: UserModel
) -> None:
    count = await seed_landmark_papers_for_user(db_session, test_user.id)
    assert count >= 10

    # Verify all 4 node types exist
    node_types_stmt = (
        select(GraphNodeModel.node_type, func.count(GraphNodeModel.id))
        .where(GraphNodeModel.user_id == test_user.id)
        .group_by(GraphNodeModel.node_type)
    )
    res_nodes = await db_session.execute(node_types_stmt)
    node_type_counts = dict(res_nodes.all())

    assert "Paper" in node_type_counts
    assert "Method" in node_type_counts
    assert "Dataset" in node_type_counts
    assert "MetricResult" in node_type_counts

    # Verify typed edges exist
    edge_types_stmt = (
        select(GraphEdgeModel.edge_type, func.count(GraphEdgeModel.id))
        .where(GraphEdgeModel.user_id == test_user.id)
        .group_by(GraphEdgeModel.edge_type)
    )
    res_edges = await db_session.execute(edge_types_stmt)
    edge_type_counts = dict(res_edges.all())

    assert "PROPOSES" in edge_type_counts
    assert "EVALUATED_ON" in edge_type_counts
    assert "ACHIEVES" in edge_type_counts
    assert "CITES" in edge_type_counts

    # Verify canonical hub deduplication: GLUE dataset is shared across papers
    glue_stmt = select(func.count(GraphNodeModel.id)).where(
        GraphNodeModel.user_id == test_user.id,
        GraphNodeModel.node_type == "Dataset",
        GraphNodeModel.canonical_name == "glue",
    )
    glue_res = await db_session.execute(glue_stmt)
    assert glue_res.scalar_one() == 1

    # Verify idempotence: seeding again does not duplicate or raise IntegrityError
    count_second = await seed_landmark_papers_for_user(db_session, test_user.id)
    assert count_second == count

    res_nodes_second = await db_session.execute(node_types_stmt)
    node_type_counts_second = dict(res_nodes_second.all())
    assert node_type_counts_second == node_type_counts

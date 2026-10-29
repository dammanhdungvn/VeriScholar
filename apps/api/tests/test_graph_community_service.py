"""Tests for GraphCommunityService (Deterministic Louvain Partitioning)."""

from api.services.graph_community_service import GraphCommunityService


def test_partition_communities_deterministic_and_clustered():
    nodes = [
        {"id": "p1", "label": "Attention Is All You Need", "type": "Paper"},
        {"id": "p2", "label": "BERT: Pre-training", "type": "Paper"},
        {"id": "p3", "label": "GPT-3 Few-Shot", "type": "Paper"},
        {"id": "r1", "label": "Retrieval-Augmented Generation", "type": "Paper"},
        {"id": "r2", "label": "GraphRAG: Knowledge Graphs", "type": "Paper"},
    ]
    edges = [
        {"source": "p2", "target": "p1", "weight": 1.0},
        {"source": "p3", "target": "p1", "weight": 1.0},
        {"source": "r2", "target": "r1", "weight": 1.0},
    ]

    service = GraphCommunityService()
    node_to_comm1, comms1 = service.partition_communities(nodes, edges, seed=42)
    node_to_comm2, comms2 = service.partition_communities(nodes, edges, seed=42)

    assert node_to_comm1 == node_to_comm2
    assert comms1 == comms2
    assert len(comms1) >= 2
    # p1, p2, p3 must share the same community
    assert node_to_comm1["p1"] == node_to_comm1["p2"] == node_to_comm1["p3"]
    # r1, r2 must share a distinct community
    assert node_to_comm1["r1"] == node_to_comm1["r2"]
    assert node_to_comm1["p1"] != node_to_comm1["r1"]

    # Verify community dict structure
    for comm in comms1:
        assert "id" in comm
        assert "label" in comm
        assert "paper_count" in comm
        assert "node_ids" in comm
        assert comm["paper_count"] == len(comm["node_ids"])


def test_partition_communities_handles_empty_and_single_node():
    service = GraphCommunityService()
    node_to_comm, comms = service.partition_communities([], [])
    assert node_to_comm == {}
    assert comms == []

    node_to_comm_single, comms_single = service.partition_communities(
        [{"id": "single", "label": "Lone Paper", "type": "Paper"}], []
    )
    assert node_to_comm_single["single"] == 0
    assert len(comms_single) == 1
    assert comms_single[0]["id"] == 0
    assert comms_single[0]["paper_count"] == 1
    assert comms_single[0]["node_ids"] == ["single"]
    assert "Lone Paper" in comms_single[0]["label"]


def test_partition_communities_disconnected_multiple_nodes():
    nodes = [{"id": f"p{i}", "label": f"Paper {i}", "type": "Paper"} for i in range(5)]
    service = GraphCommunityService()
    node_to_comm, comms = service.partition_communities(nodes, [])
    assert len(node_to_comm) == 5
    assert len(comms) == 5
    assigned_ids = {c["id"] for c in comms}
    assert assigned_ids == {0, 1, 2, 3, 4}
    for c in comms:
        assert c["paper_count"] == 1
        assert len(c["node_ids"]) == 1


def test_partition_communities_permutation_invariance_and_malformed_edges():
    nodes_order1 = [
        {"id": "c1", "label": "Community C1 Leader", "type": "Paper"},
        {"id": "c2", "label": "Community C2 Member", "type": "Paper"},
        {"id": "d1", "label": "Community D1 Leader", "type": "Paper"},
        {"id": "d2", "label": "Community D2 Member", "type": "Paper"},
    ]
    nodes_order2 = [
        nodes_order1[3],
        nodes_order1[1],
        nodes_order1[0],
        nodes_order1[2],
    ]

    edges_order1 = [
        {"source": "c1", "target": "c2", "weight": 2.0},
        {"source": "d1", "target": "d2", "weight": 1.5},
        {"source": "nonexistent_a", "target": "nonexistent_b"},
        {"source": "c1", "target": "c1"},  # Self loop
        {"source": "c1", "target": "c2", "weight": -5.0},
    ]
    edges_order2 = [
        edges_order1[1],
        edges_order1[0],
        edges_order1[4],
        edges_order1[2],
        edges_order1[3],
    ]

    service = GraphCommunityService()
    res1_map, res1_comms = service.partition_communities(nodes_order1, edges_order1, seed=42)
    res2_map, res2_comms = service.partition_communities(nodes_order2, edges_order2, seed=42)

    assert res1_map == res2_map
    assert res1_comms == res2_comms

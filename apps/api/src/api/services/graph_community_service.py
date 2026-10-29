"""Deterministic Louvain Community Partitioning Service for Knowledge Graph."""

from typing import Any

import networkx as nx


class GraphCommunityService:
    """Service to partition knowledge graph nodes into deterministic communities.

    Uses NetworkX Louvain modularity algorithm with canonical sorting
    and fixed seeding to guarantee zero community ID drift across calls.
    """

    @staticmethod
    def partition_communities(
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        seed: int = 42,
    ) -> tuple[dict[str, int], list[dict[str, Any]]]:
        """Partition nodes into deterministic communities based on topology.

        Args:
            nodes: List of node dictionaries with at least 'id' and optionally 'label', 'type'.
            edges: List of edge dictionaries with 'source', 'target', and optionally 'weight'.
            seed: Random seed for Louvain modularity optimization (default: 42).

        Returns:
            Tuple containing:
                - node_to_community: Mapping from node_id to integer community_id (0..k).
                - communities_list: List of community descriptor dicts with
                  {'id': int, 'label': str, 'paper_count': int, 'node_ids': list[str]}.
        """
        if not nodes:
            return {}, []

        # 1. Canonical node processing
        node_labels: dict[str, str] = {}
        node_types: dict[str, str] = {}
        sorted_nodes = sorted(nodes, key=lambda n: str(n.get("id", "")))

        G = nx.Graph()
        for node in sorted_nodes:
            nid = str(node.get("id", "")).strip()
            if not nid:
                continue
            label = str(node.get("label") or node.get("title") or "").strip()
            ntype = str(node.get("type", "Paper")).strip()
            node_labels[nid] = label
            node_types[nid] = ntype
            G.add_node(nid)

        if G.number_of_nodes() == 0:
            return {}, []

        # 2. Canonical edge processing
        sorted_edges = sorted(
            edges,
            key=lambda e: (str(e.get("source", "")), str(e.get("target", ""))),
        )
        for edge in sorted_edges:
            src = str(edge.get("source", "")).strip()
            tgt = str(edge.get("target", "")).strip()
            if src in G and tgt in G and src != tgt:
                raw_weight = edge.get("weight", 1.0)
                try:
                    weight = float(raw_weight) if raw_weight is not None else 1.0
                    if weight <= 0:
                        weight = 1.0
                except (ValueError, TypeError):
                    weight = 1.0
                G.add_edge(src, tgt, weight=weight)

        # 3. Community detection via Louvain modularity
        try:
            raw_communities = nx.community.louvain_communities(
                G,
                weight="weight",
                resolution=1.0,
                seed=seed,
            )
        except Exception:
            raw_communities = list(nx.connected_components(G))

        # 4. Canonical deterministic sorting of communities
        # Sort node IDs within each community alphabetically
        sorted_comm_node_ids = [sorted(comm) for comm in raw_communities if comm]

        # Sort communities by size descending, then by lowest node id ascending
        sorted_comms = sorted(
            sorted_comm_node_ids,
            key=lambda c: (-len(c), c[0] if c else ""),
        )

        node_to_community: dict[str, int] = {}
        communities_list: list[dict[str, Any]] = []

        for comm_id, comm_nodes in enumerate(sorted_comms):
            for nid in comm_nodes:
                node_to_community[nid] = comm_id

            # Determine most representative paper / node for labeling
            # Prioritize papers, then highest weighted degree, then canonical ID
            def _node_rank_key(nid: str) -> tuple[int, float, str]:
                is_paper = 1 if node_types.get(nid, "paper").lower() == "paper" else 0
                deg = float(G.degree(nid, weight="weight"))
                return (-is_paper, -deg, nid)

            best_node_id = min(comm_nodes, key=_node_rank_key)
            best_label = node_labels.get(best_node_id, "").strip()

            if best_label:
                if best_label.endswith(" Cluster"):
                    comm_label = best_label
                else:
                    comm_label = f"{best_label} Cluster"
            else:
                comm_label = f"Community {comm_id}"

            paper_count = sum(
                1 for nid in comm_nodes if node_types.get(nid, "paper").lower() == "paper"
            )

            communities_list.append(
                {
                    "id": comm_id,
                    "label": comm_label,
                    "paper_count": paper_count,
                    "node_ids": comm_nodes,
                }
            )

        return node_to_community, communities_list

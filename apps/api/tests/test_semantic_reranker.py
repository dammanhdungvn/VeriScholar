from unittest.mock import patch

from api.services.semantic_reranker_service import SemanticRerankerService


def test_semantic_reranker_ranks_relevant_chunks_higher():
    reranker = SemanticRerankerService()
    query = "What is the computational complexity of Scaled Dot-Product Attention?"
    candidates = [
        {"id": "c1", "content": "The weather in Seattle is rainy in autumn.", "score": 0.5},
        {
            "id": "c2",
            "content": "Attention has computational complexity O(n^2 * d) where n is sequence length.",
            "score": 0.5,
        },
        {
            "id": "c3",
            "content": "Recurrent neural networks process tokens sequentially in O(n * d^2).",
            "score": 0.5,
        },
    ]
    ranked, abstain = reranker.rerank(query=query, candidates=candidates, top_k=2)
    assert abstain is False
    assert len(ranked) == 2
    assert ranked[0]["id"] == "c2"
    assert ranked[0]["rerank_score"] > ranked[1]["rerank_score"]


def test_semantic_reranker_abstains_when_all_chunks_are_irrelevant():
    reranker = SemanticRerankerService()
    query = "Explain quantum gravity in AdS/CFT correspondence."
    candidates = [
        {"id": "c1", "content": "Recipe for baking sourdough bread using starter.", "score": 0.1},
        {"id": "c2", "content": "How to repair bicycle tire punctures.", "score": 0.1},
    ]
    ranked, abstain = reranker.rerank(query=query, candidates=candidates, top_k=2)
    assert abstain is True


def test_semantic_reranker_empty_inputs():
    reranker = SemanticRerankerService()
    ranked, abstain = reranker.rerank(query="", candidates=[{"id": "c1", "content": "test"}])
    assert ranked == []
    assert abstain is True

    ranked, abstain = reranker.rerank(query="hello", candidates=[])
    assert ranked == []
    assert abstain is True


def test_semantic_reranker_score_threshold_filtering():
    reranker = SemanticRerankerService()
    query = "What is the computational complexity of Scaled Dot-Product Attention?"
    candidates = [
        {"id": "c1", "content": "The weather in Seattle is rainy in autumn.", "score": 0.5},
        {
            "id": "c2",
            "content": "Attention has computational complexity O(n^2 * d) where n is sequence length.",
            "score": 0.5,
        },
        {
            "id": "c3",
            "content": "Recurrent neural networks process tokens sequentially in O(n * d^2).",
            "score": 0.5,
        },
    ]
    # Filter with score_threshold = 0.65 (only c2 >= 0.65)
    ranked, abstain = reranker.rerank(
        query=query, candidates=candidates, top_k=5, score_threshold=0.65
    )
    assert abstain is False
    assert len(ranked) == 1
    assert ranked[0]["id"] == "c2"
    assert ranked[0]["rerank_score"] >= 0.65


def test_semantic_reranker_fallback_token_overlap():
    reranker = SemanticRerankerService()
    query = "Scaled Dot-Product Attention complexity"
    candidates = [
        {"id": "c1", "content": "The weather in Seattle is rainy in autumn.", "score": 0.5},
        {
            "id": "c2",
            "content": "Attention has computational complexity O(n^2 * d) where n is sequence length.",
            "score": 0.5,
        },
    ]
    with patch.object(reranker, "_get_ranker", return_value=None):
        ranked, abstain = reranker.rerank(query=query, candidates=candidates, top_k=2)
        assert abstain is False
        assert len(ranked) == 2
        assert ranked[0]["id"] == "c2"
        assert ranked[0]["rerank_score"] > ranked[1]["rerank_score"]

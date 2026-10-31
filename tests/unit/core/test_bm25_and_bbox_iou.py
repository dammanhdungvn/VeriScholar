from core.domain.value_objects.bounding_box import BoundingBox
from core.services.bm25_scorer import OkapiBM25Scorer


def test_bounding_box_compute_iou_identical_and_partial():
    box_a = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=1)
    box_b = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=1)
    box_c = BoundingBox(x0=0.3, y0=0.3, x1=0.7, y1=0.7, page=1)
    box_diff_page = BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.5, page=2)

    assert box_a.compute_iou(box_b) == 1.0
    # Intersection is [0.3, 0.3, 0.5, 0.5] -> area 0.04; Union is 0.16 + 0.16 - 0.04 = 0.28
    assert round(box_a.compute_iou(box_c), 4) == round(0.04 / 0.28, 4)
    assert box_a.compute_iou(box_diff_page) == 0.0


def test_okapi_bm25_scorer_ranks_relevant_documents_and_handles_empty():
    scorer = OkapiBM25Scorer(k1=1.2, b=0.75)
    corpus = [
        "FlashAttention-2 reduces memory IO complexity to O(N) via GPU shared memory tiling.",
        "LoRA injects trainable low-rank decomposition matrices A and B into transformer layers.",
        "Reciprocal rank fusion combines dense vector and sparse lexical rankings with k=60.",
    ]
    ranked = scorer.rank_documents("FlashAttention-2 memory IO tiling", corpus)
    assert ranked[0][0] == 0
    assert ranked[0][1] > ranked[1][1]
    assert scorer.score_corpus("", corpus) == [0.0, 0.0, 0.0]
    assert scorer.score_corpus("query", []) == []

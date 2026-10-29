"""Local ONNX FlashRank Cross-Encoder Semantic Reranker & Confidence Gate.

Implements Spec 03 (§5.B Khối 5) Semantic Reranking with active abstention gate
and graceful fallback to token-overlap scoring if ONNX runtime is unavailable.
"""

from __future__ import annotations

import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class SemanticRerankerService:
    """Local ONNX FlashRank Cross-Encoder Semantic Reranker with Active Abstention Gate."""

    _shared_ranker: Any = None
    _shared_ranker_failed: bool = False

    def __init__(
        self,
        model_name: str = "ms-marco-TinyBERT-L-2-v2",
        cache_dir: str = "/tmp",
        confidence_threshold: float = 0.65,
        abstain_threshold: float = 0.35,
    ) -> None:
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.confidence_threshold = confidence_threshold
        self.abstain_threshold = abstain_threshold

    @classmethod
    def _get_ranker(cls, model_name: str, cache_dir: str) -> Any:
        if cls._shared_ranker is not None:
            return cls._shared_ranker
        if cls._shared_ranker_failed:
            return None
        try:
            from flashrank import Ranker

            cls._shared_ranker = Ranker(model_name=model_name, cache_dir=cache_dir)
            return cls._shared_ranker
        except Exception as ex:
            logger.warning("flashrank_ranker_init_failed", error=str(ex))
            cls._shared_ranker_failed = True
            return None

    def _token_overlap_scoring(
        self,
        query: str,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Fallback token-overlap scoring when ONNX cross-encoder is unavailable."""
        stopwords = {
            "the",
            "a",
            "an",
            "in",
            "on",
            "of",
            "for",
            "to",
            "and",
            "or",
            "is",
            "are",
            "was",
            "were",
            "what",
            "how",
            "why",
            "when",
            "where",
            "which",
            "who",
            "whom",
            "của",
            "và",
            "là",
            "trong",
            "có",
            "cho",
            "với",
            "các",
            "những",
            "này",
            "thế",
            "nào",
            "gì",
            "ở",
            "tại",
            "theo",
            "được",
            "bài",
            "báo",
            "tôi",
            "muốn",
            "bạn",
        }
        raw_tokens = re.findall(r"[a-zA-Z0-9_\-]+", query.lower())
        q_terms = [t for t in raw_tokens if len(t) >= 2 and t not in stopwords]
        q_set = set(q_terms)

        scored: list[dict[str, Any]] = []
        for cand in candidates:
            cand_copy = dict(cand)
            content = str(
                cand.get("content") or cand.get("text_content") or cand.get("text") or ""
            ).lower()
            if not content or not q_set:
                score = 0.0
            else:
                c_tokens = set(re.findall(r"[a-zA-Z0-9_\-]+", content))
                overlap = len(q_set & c_tokens)
                score = min(1.0, overlap / len(q_set))
            s_val = round(float(score), 4)
            cand_copy["rerank_score"] = s_val
            cand_copy["score"] = s_val
            scored.append(cand_copy)

        scored.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return scored

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Rerank candidate chunks against the query using FlashRank ONNX cross-encoder.

        Args:
            query: The search query string.
            candidates: List of candidate chunk dictionaries.
            top_k: Maximum number of top chunks to return.
            score_threshold: Optional minimum rerank score threshold (e.g. 0.65).

        Returns:
            tuple[list[dict[str, Any]], bool]:
                - List of ranked candidates up to top_k, each with 'rerank_score' attached.
                - abstain: True if max rerank score < abstain_threshold (0.35) or empty candidates.
        """
        if not query or not query.strip() or not candidates:
            return [], True

        ranker = self._get_ranker(self.model_name, self.cache_dir)
        scored_candidates: list[dict[str, Any]] = []

        if ranker is not None:
            try:
                from flashrank import RerankRequest

                passages = [
                    {
                        "id": str(c.get("id") or c.get("chunk_id") or idx),
                        "text": str(
                            c.get("content") or c.get("text_content") or c.get("text") or ""
                        ),
                        "_orig_idx": idx,
                    }
                    for idx, c in enumerate(candidates)
                ]
                req = RerankRequest(query=query, passages=passages)
                results = ranker.rerank(req)
                for res in results:
                    orig_idx = res.get("_orig_idx")
                    cand = candidates[orig_idx] if orig_idx is not None else None
                    if cand is not None:
                        cand_copy = dict(cand)
                        s = float(res.get("score", 0.0))
                        cand_copy["rerank_score"] = s
                        cand_copy["score"] = s
                        scored_candidates.append(cand_copy)
            except Exception as ex:
                logger.warning("flashrank_rerank_runtime_failed", error=str(ex))
                scored_candidates = []

        if not scored_candidates:
            scored_candidates = self._token_overlap_scoring(query, candidates)

        max_score = max((c.get("rerank_score", 0.0) for c in scored_candidates), default=0.0)
        abstain = bool(max_score < self.abstain_threshold)

        if score_threshold is not None:
            filtered = [
                c for c in scored_candidates if c.get("rerank_score", 0.0) >= score_threshold
            ]
            return filtered[:top_k], abstain

        return scored_candidates[:top_k], abstain

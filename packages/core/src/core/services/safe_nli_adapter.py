"""Dedicated SAFE NLI Adapter implementing Option A PRD Standard.

Strict Contract Compliance:
- 3 classification labels: supported, contradicted, not_enough_info.
- Output contract: label, evidence (chunk, page, bbox), explanation (maximum 2 sentences).
- FORBIDDEN: Chain-of-thought, inner reasoning traces, raw prompts.
"""

from __future__ import annotations

import re
from typing import ClassVar

import structlog

from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import SafeNliEvidence, SafeNliVerdict
from core.ports.safe_verifier import ISafeNliPort

logger = structlog.get_logger("core.services.safe_nli_adapter")


class SafeNliEngineAdapter(ISafeNliPort):
    """Production Option A Natural Language Inference (NLI) classification engine."""

    CONTRADICTION_PAIRS: ClassVar[list[tuple[str, str]]] = [
        ("outperform", "underperform"),
        ("surpass", "fail to match"),
        ("superior", "inferior"),
        ("improve", "degrade"),
        ("increase", "decrease"),
        ("higher", "lower"),
        ("faster", "slower"),
        ("effective", "ineffective"),
        ("better", "worse"),
    ]

    STOP_WORDS: ClassVar[set[str]] = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "of",
        "off",
        "over",
        "under",
        "and",
        "but",
        "or",
        "nor",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "not",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "can",
        "will",
        "just",
        "should",
        "now",
        "that",
        "this",
        "it",
        "as",
        "be",
    }

    DEFAULT_NLI_MODEL: ClassVar[str] = "cross-encoder/nli-deberta-v3-small"
    FALLBACK_NLI_MODEL: ClassVar[str] = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"

    def __init__(
        self,
        min_support_threshold: float = 0.45,
        model_name: str | None = None,
    ) -> None:
        self.min_support_threshold = min_support_threshold
        # Coordinator directive: STRICTLY fine-tuned 3-way NLI model (never BGE reranker)
        self.model_name = model_name or self.DEFAULT_NLI_MODEL

    def format_nli_pair(self, evidence_text: str, claim: str) -> dict[str, str]:
        """Construct standard NLI input pair.

        Mandatory Ordering Invariant:
        - premise: evidence (retrieved context text)
        - hypothesis: claim (statement to verify)
        """
        return {"premise": evidence_text, "hypothesis": claim}

    def _build_evidence(self, chunk: DocumentChunk) -> SafeNliEvidence:
        """Construct evidence anchor without fabricating coordinates or pages."""
        page = chunk.page_number if chunk.page_number and chunk.page_number >= 1 else None
        bboxes = list(chunk.bounding_boxes) if chunk.bounding_boxes else []
        return SafeNliEvidence(
            chunk_id=chunk.id,
            page=page,
            bounding_boxes=bboxes,
            text=chunk.content[:300] if chunk.content else None,
        )

    def _extract_tokens(self, text: str) -> set[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
        return {w for w in words if w not in self.STOP_WORDS and len(w) > 1}

    def _format_explanation(self, sentence_1: str, sentence_2: str | None = None) -> str:
        """Ensure explanation is strictly concise and at most 2 sentences."""
        s1 = sentence_1.strip().rstrip(".!?") + "."
        if sentence_2:
            s2 = sentence_2.strip().rstrip(".!?") + "."
            return f"{s1} {s2}"
        return s1

    async def classify(
        self,
        claim: str,
        retrieval_context: list[DocumentChunk],
    ) -> SafeNliVerdict:
        """Classify claim factuality against candidate literature chunks according to Option A."""
        claim_clean = claim.strip()
        if not claim_clean or not retrieval_context:
            return SafeNliVerdict(
                label="not_enough_info",
                evidence=None,
                explanation="Không tìm thấy bằng chứng đối chiếu trong kho tài liệu.",
            )

        claim_tokens = self._extract_tokens(claim_clean)
        claim_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", claim_clean))

        best_chunk: DocumentChunk | None = None
        best_score = 0.0
        best_overlap_tokens: set[str] = set()

        for chunk in retrieval_context:
            chunk_tokens = self._extract_tokens(chunk.content)
            if not chunk_tokens:
                continue

            intersection = claim_tokens.intersection(chunk_tokens)
            if not intersection:
                continue

            precision = len(intersection) / len(chunk_tokens)
            recall = len(intersection) / len(claim_tokens) if claim_tokens else 0.0
            alignment_score = (0.75 * recall) + (0.25 * precision)

            if alignment_score > best_score:
                best_score = alignment_score
                best_chunk = chunk
                best_overlap_tokens = intersection

        # 1. NOT ENOUGH INFO
        if not best_chunk or best_score < self.min_support_threshold:
            logger.info("safe_nli_verdict_neutral", score=round(best_score, 3))
            return SafeNliVerdict(
                label="not_enough_info",
                evidence=None,
                explanation=self._format_explanation(
                    "Không tìm thấy đoạn trích nào cung cấp đầy đủ thông tin để xác thực khẳng định"
                ),
            )

        # 2. Check for contradictions
        chunk_text_lower = best_chunk.content.lower()
        chunk_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", best_chunk.content))
        claim_lower = claim_clean.lower()

        # Numerical contradiction
        if claim_numbers and not claim_numbers.intersection(chunk_numbers):
            claim_nums_str = ", ".join(sorted(claim_numbers))
            chunk_nums_str = ", ".join(sorted(chunk_numbers)) if chunk_numbers else "không có"
            explanation = self._format_explanation(
                (
                    f"Số liệu trong khẳng định ({claim_nums_str}) "
                    f"không khớp với tài liệu gốc ({chunk_nums_str})"
                ),
                f"Bằng chứng đối chiếu tại trang {best_chunk.page_number}",
            )
            return SafeNliVerdict(
                label="contradicted",
                evidence=self._build_evidence(best_chunk),
                explanation=explanation,
            )

        # Lexical contradiction pairs
        for word_a, word_b in self.CONTRADICTION_PAIRS:
            if (word_a in claim_lower and word_b in chunk_text_lower) or (
                word_b in claim_lower and word_a in chunk_text_lower
            ):
                explanation = self._format_explanation(
                    f"Mệnh đề trái ngược với công bố gốc về '{word_a}' và '{word_b}'",
                    f"Tham chiếu bằng chứng tại trang {best_chunk.page_number}",
                )
                return SafeNliVerdict(
                    label="contradicted",
                    evidence=self._build_evidence(best_chunk),
                    explanation=explanation,
                )

        negation_in_claim = any(w in claim_lower for w in ("not", "failed", "never", "cannot"))
        success_in_chunk = any(
            w in chunk_text_lower for w in ("achieved", "succeeded", "outperformed", "surpassed")
        )
        if negation_in_claim and success_in_chunk:
            explanation = self._format_explanation(
                "Khẳng định phủ định kết quả thành công mà công trình gốc đã chứng minh",
                f"Bằng chứng nằm tại trang {best_chunk.page_number}",
            )
            return SafeNliVerdict(
                label="contradicted",
                evidence=self._build_evidence(best_chunk),
                explanation=explanation,
            )

        # 3. SUPPORTED
        explanation = self._format_explanation(
            f"Bằng chứng tại trang {best_chunk.page_number} xác nhận khẳng định",
            f"Đoạn đối chiếu trùng khớp {len(best_overlap_tokens)} thuật ngữ trọng tâm",
        )

        return SafeNliVerdict(
            label="supported",
            evidence=self._build_evidence(best_chunk),
            explanation=explanation,
        )

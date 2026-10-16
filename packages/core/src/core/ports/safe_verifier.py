"""SAFE Fact Checker Port Definition (Hexagonal Architecture)."""

from typing import Protocol
from uuid import UUID

from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import FactVerificationReport, SafeNliVerdict


class ISafeNliPort(Protocol):
    """Port for dedicated 3-label SAFE Natural Language Inference (NLI) classification."""

    async def classify(
        self,
        claim: str,
        retrieval_context: list[DocumentChunk],
    ) -> SafeNliVerdict:
        """Classify factual claim against candidate literature chunks according to Option A PRD.

        Returns:
            SafeNliVerdict with label, evidence, and concise explanation (max 2 sentences).
            Strictly no chain-of-thought.
        """
        ...


class ISafeFactCheckerPort(Protocol):
    """Port for SAFE (Search-Augmented Factuality Evaluator) verification engine."""

    async def verify_text(
        self,
        text: str,
        retrieval_context: list[DocumentChunk],
        doc_metadata: dict[UUID, str] | None = None,
        draft_id: UUID | None = None,
    ) -> FactVerificationReport:
        """Decompose text into atomic claims, match evidence, and run NLI scoring.

        Args:
            text: Raw input text from draft or passage.
            retrieval_context: Candidate literature chunks to evaluate claims against.
            doc_metadata: Optional mapping from document UUID to title/citation.
            draft_id: Optional UUID of the associated draft.

        Returns:
            FactVerificationReport containing atomic claims, verdicts, and bounding boxes.
        """
        ...

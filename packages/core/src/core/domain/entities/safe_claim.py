import re
from datetime import UTC, datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.value_objects.bounding_box import BoundingBox


class FactVerificationStatus(str, Enum):
    """3-label strict classification status for atomic factual claims (PRD §3.2)."""

    SUPPORTED = "supported"  # 🟢 Claim matches verified literature data + Bounding Box
    CONTRADICTED = "contradicted"  # 🔴 Claim contradicts author's published findings
    NOT_ENOUGH_INFO = "not_enough_info"  # 🟡 No conclusive evidence found in repository


class SafeNliEvidence(BaseModel):
    """Evidence anchor for factual verification verdict."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: UUID | None = None
    page: int | None = Field(default=None, ge=1, description="1-indexed page number")
    bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Normalized bounding box coordinates [x0, y0, x1, y1, page]",
    )
    text: str | None = Field(default=None, description="Exact passage snippet from evidence chunk")


class SafeNliVerdict(BaseModel):
    """Option A PRD-compliant SAFE NLI Output Contract.

    Strict Invariants:
    - Exactly 3 classification labels: 'supported', 'contradicted', 'not_enough_info'.
    - Output contract contains ONLY: label, evidence, explanation.
    - Explanation is concise (maximum 2 sentences).
    - Chain-of-thought or reasoning traces are strictly FORBIDDEN (extra='forbid').
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: Literal["supported", "contradicted", "not_enough_info"]
    evidence: SafeNliEvidence | None = None
    explanation: str = Field(
        description="Concise factual explanation of verdict, maximum 2 sentences."
    )

    @field_validator("explanation")
    @classmethod
    def validate_explanation_length(cls, v: str) -> str:
        clean = v.strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if s.strip()]
        if len(sentences) > 2:
            return " ".join(sentences[:2])
        return clean


class AtomicClaim(BaseModel):
    """Single atomic factual proposition extracted from draft text."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Unique claim identifier")
    claim_text: str = Field(min_length=1, description="Atomic factual proposition")
    normalized_entities: list[str] = Field(
        default_factory=list,
        description="Resolved explicit entities (de-anaphorized)",
    )
    status: FactVerificationStatus = Field(
        default=FactVerificationStatus.NOT_ENOUGH_INFO,
        description="Verification verdict",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the NLI verdict",
    )
    evidence_text: str | None = Field(
        default=None,
        description="Supporting or contradicting text passage from literature",
    )
    evidence_document_id: UUID | None = Field(
        default=None,
        description="Parent document UUID containing evidence",
    )
    evidence_document_title: str | None = Field(
        default=None,
        description="Title of the source document",
    )
    evidence_page: int | None = Field(
        default=None,
        ge=1,
        description="1-indexed page number of the evidence chunk",
    )
    evidence_bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Normalized bounding boxes [x0, y0, x1, y1, page] for visual canvas overlay",
    )
    reasoning: str = Field(
        default="",
        description="Explanation of the NLI classification verdict",
    )


class FactVerificationReport(BaseModel):
    """Aggregate verification report for a draft or passage."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Report identifier")
    draft_id: UUID | None = Field(default=None, description="Associated draft UUID if applicable")
    verified_text: str = Field(min_length=1, description="Original source text subjected to SAFE")
    claims: list[AtomicClaim] = Field(default_factory=list, description="List of verified claims")
    total_claims: int = Field(ge=0, default=0)
    supported_claims: int = Field(ge=0, default=0)
    contradicted_claims: int = Field(ge=0, default=0)
    unverified_claims: int = Field(ge=0, default=0)
    supported_ratio: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="Ratio of supported claims over total claims",
    )
    latency_ms: float = Field(ge=0.0, default=0.0, description="Verification execution time in ms")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def compute_summary(self) -> None:
        """Recalculate summary metrics from claim list."""
        self.total_claims = len(self.claims)
        self.supported_claims = sum(
            1 for c in self.claims if c.status == FactVerificationStatus.SUPPORTED
        )
        self.contradicted_claims = sum(
            1 for c in self.claims if c.status == FactVerificationStatus.CONTRADICTED
        )
        self.unverified_claims = sum(
            1 for c in self.claims if c.status == FactVerificationStatus.NOT_ENOUGH_INFO
        )
        self.supported_ratio = (
            round(self.supported_claims / self.total_claims, 4) if self.total_claims > 0 else 0.0
        )

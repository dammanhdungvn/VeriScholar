"""DocumentChunk Domain Entity.

Represents a semantically coherent text chunk of an academic paper,
carrying exact bounding boxes for spatial grounding and a 1024-dimensional
dense vector embedding from BGE-M3.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.exceptions import InvariantViolationError
from core.domain.value_objects.bounding_box import BoundingBox

BGE_M3_EMBEDDING_DIM = 1024
OPENAI_EMBEDDING_DIM = 1536
VALID_EMBEDDING_DIMS = (BGE_M3_EMBEDDING_DIM, OPENAI_EMBEDDING_DIM)


class DocumentChunk(BaseModel):
    """Domain Entity representing a text chunk extracted from a document."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Unique chunk identifier")
    document_id: UUID = Field(description="Parent document identifier")
    chunk_index: int = Field(ge=0, description="0-indexed sequence order in the document")
    page_number: int = Field(ge=1, description="Primary document page number where chunk begins")
    content: str = Field(min_length=1, description="Raw textual content of the chunk")
    bounding_boxes: list[BoundingBox] = Field(
        default_factory=list,
        description="Non-null invariant: list of normalized bounding boxes across pages",
    )
    token_count: int = Field(gt=0, description="Calculated token count of chunk content")
    embedding: list[float] | None = Field(
        default=None,
        description="Dense vector embedding (1024-dim BGE-M3 or 1536-dim OpenAI)",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v: list[float] | None) -> list[float] | None:
        """Enforce strict embedding dimension invariant (1024 for BGE-M3 or 1536 for OpenAI)."""
        if v is not None and len(v) not in VALID_EMBEDDING_DIMS:
            raise InvariantViolationError(
                f"Embedding dimension mismatch: expected 1024 or 1536, got {len(v)}."
            )
        return v

    def attach_embedding(self, embedding_vector: list[float]) -> None:
        """Attach calculated dense vector embedding to the chunk."""
        if len(embedding_vector) not in VALID_EMBEDDING_DIMS:
            raise InvariantViolationError(
                f"Embedding size {len(embedding_vector)} invalid. Must be 1024 or 1536."
            )
        self.embedding = embedding_vector

    def add_bounding_box(self, box: BoundingBox) -> None:
        """Add a spatial bounding box to this chunk."""
        self.bounding_boxes.append(box)

    @property
    def bounding_boxes_raw(self) -> list[list[float | int]]:
        """Serialize bounding boxes to list of raw 5-element arrays for JSONB storage."""
        return [box.to_list() for box in self.bounding_boxes]

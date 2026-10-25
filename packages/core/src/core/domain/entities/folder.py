"""Domain entities for Hierarchical Research Folders and Library Management (Module 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class FolderEntity:
    """Domain entity representing a research topic folder."""

    id: UUID
    user_id: UUID
    name: str
    parent_id: UUID | None = None
    color: str = "#6366f1"
    description: str | None = None
    document_count: int = 0
    subfolder_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        parent_id: UUID | None = None,
        color: str = "#6366f1",
        description: str | None = None,
    ) -> FolderEntity:
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            name=name.strip(),
            parent_id=parent_id,
            color=color,
            description=description.strip() if description else None,
            created_at=now,
            updated_at=now,
        )


@dataclass
class SufficiencyEvaluation:
    """Evaluation result from the Sufficiency Gate measuring evidence completeness."""

    is_sufficient: bool
    sufficiency_score: float  # 0.0 to 1.0 (Threshold: >= 0.85)
    analyzed_aspects: list[str]
    missing_aspects: list[str]
    recommended_search_queries: list[str]
    reasoning: str

"""Schemas for Compiled Academic LLM Wiki pages and Research Gaps synthesis.

Aligns with Spec 05 (§1.D, §3, §4) and VeriScholar MVP architecture.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class WikiPageSummary(BaseModel):
    """Summary representation of a compiled academic wiki page for listing."""

    id: UUID = Field(description="Unique page identifier")
    slug: str = Field(description="URL-friendly kebab-case concept slug")
    title: str = Field(description="Scholarly concept or method title")
    page_type: str = Field(
        default="topic",
        description="Type: method, dataset, topic, research_gap, comparison",
    )
    summary: str | None = Field(
        default=None,
        description="Abstractive summary or lead paragraph of the concept",
    )
    markdown_content: str | None = Field(
        default=None,
        description="Full compiled Markdown content or lead preview",
    )
    wikilinks: list[str] = Field(
        default_factory=list,
        description="Outbound [[wikilinks]] referencing other concepts",
    )
    backlinks_count: int = Field(
        default=0,
        description="Count of inbound wikilinks targeting this concept",
    )
    folder_id: UUID | None = Field(
        default=None,
        description="Parent folder UUID if scoped to a project folder",
    )
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class WikiListResponse(BaseModel):
    """Payload for listing academic wiki pages."""

    total: int = Field(default=0, description="Total count of matching wiki pages")
    pages: list[WikiPageSummary] = Field(
        default_factory=list,
        description="List of compiled academic wiki pages",
    )


class WikiPageResponse(BaseModel):
    """Full detail of a compiled academic wiki page."""

    id: UUID = Field(description="Unique page identifier")
    user_id: UUID = Field(description="Owner user identifier")
    folder_id: UUID | None = Field(
        default=None,
        description="Associated project folder UUID",
    )
    slug: str = Field(description="Concept slug")
    title: str = Field(description="Scholarly title")
    page_type: str = Field(
        default="topic",
        description="Type: method, dataset, topic, research_gap, comparison",
    )
    markdown_content: str = Field(
        description="Full compiled Markdown content with [[wikilinks]]",
    )
    content_markdown: str | None = Field(
        default=None,
        description="Alias synonym for markdown_content",
    )
    yaml_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted YAML frontmatter metadata",
    )
    metadata_json: dict[str, Any] | None = Field(
        default=None,
        description="Alias synonym for yaml_metadata",
    )
    wikilinks: list[str] = Field(
        default_factory=list,
        description="List of extracted [[wikilinks]]",
    )
    summary: str | None = Field(
        default=None,
        description="Abstractive summary of the page",
    )
    backlinks_count: int = Field(
        default=0,
        description="Number of inbound links",
    )
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class ResearchGapsRequest(BaseModel):
    """Request payload for cross-paper research gap synthesis."""

    folder_id: UUID | None = Field(
        default=None,
        description="Optional folder UUID filter",
    )
    query: str | None = Field(
        default=None,
        description="Optional focus query or topic area for gap exploration",
    )


class UnsolvedFrontierItem(BaseModel):
    """Unsolved challenge or bottleneck synthesized across scholarly literature."""

    domain: str = Field(description="Thematic research domain of the limitation")
    acknowledged_by: list[str] = Field(
        default_factory=list,
        description="Papers, authors, or citations acknowledging this bottleneck",
    )
    bottleneck_description: str = Field(
        description="Detailed description of the theoretical or empirical bottleneck",
    )
    potential_solution: str | None = Field(
        default=None,
        description="Promising methodology or research direction to resolve the bottleneck",
    )


class SuggestedTopicItem(BaseModel):
    """Novel research topic proposal addressing identified literature gaps."""

    title: str = Field(description="Proposed scholarly research or thesis title")
    rationale: str = Field(
        description="Academic justification addressing identified limitations",
    )


class ResearchGapsResponse(BaseModel):
    """Response payload containing cross-paper research gaps and topic proposals."""

    folder_id: UUID | None = Field(
        default=None,
        description="Target folder ID if filtered by folder",
    )
    unsolved_frontiers: list[UnsolvedFrontierItem] = Field(
        default_factory=list,
        description="Synthesized limitations and unsolved frontiers",
    )
    suggested_topics: list[SuggestedTopicItem] = Field(
        default_factory=list,
        description="Actionable suggested research directions / thesis topics",
    )
    recommended_directions: list[str] = Field(
        default_factory=list,
        description="Recommended actionable research directions",
    )
    synthesized_matrix_markdown: str = Field(
        default="",
        description="Synthesized Markdown table/matrix of cross-paper research gaps",
    )
    total_papers_analyzed: int = Field(
        default=0,
        description="Total number of papers analyzed during synthesis",
    )


class WikiListResponseEnvelope(SingleResponseEnvelope[WikiListResponse]):
    """Standard envelope for academic wiki listing."""


class WikiPageResponseEnvelope(SingleResponseEnvelope[WikiPageResponse]):
    """Standard envelope for academic wiki page detail."""


class ResearchGapsResponseEnvelope(SingleResponseEnvelope[ResearchGapsResponse]):
    """Standard envelope for research gaps synthesis."""

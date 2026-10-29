"""Wiki models for Compiled Academic LLM Wiki (Pure Domain)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WikiPageDraft(BaseModel):
    """Input draft for compiling a structured academic wiki page."""

    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, description="Academic concept or entity page title")
    summary: str = Field(default="", description="High-level synthesis or concept summary")
    key_insights: list[str] = Field(
        default_factory=list,
        description="Key algorithmic, architectural, or empirical insights",
    )
    related_entities: list[str] = Field(
        default_factory=list,
        description="Canonical names of related entities for [[wikilink]] generation",
    )
    source_papers: list[str] = Field(
        default_factory=list,
        description="Source academic paper citations or titles",
    )
    slug: str | None = Field(
        default=None,
        description="Optional custom URL-safe slug; if None, derived from title",
    )
    content: str | None = Field(
        default=None,
        description="Optional pre-existing or custom markdown body content",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Taxonomy tags or categories",
    )
    custom_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional YAML metadata fields",
    )


class WikiCompileResult(BaseModel):
    """Result of compiling or parsing an academic wiki markdown page."""

    model_config = ConfigDict(extra="ignore")

    slug: str = Field(description="URL-friendly unique slug identifier")
    title: str = Field(description="Human-readable concept or page title")
    markdown: str = Field(description="Full compiled markdown document including frontmatter")
    yaml_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured YAML frontmatter metadata dictionary",
    )
    wikilinks: list[str] = Field(
        default_factory=list,
        description="Extracted cross-referencing [[wikilink]] entity targets",
    )
    body: str = Field(
        default="",
        description="Markdown body content excluding frontmatter",
    )

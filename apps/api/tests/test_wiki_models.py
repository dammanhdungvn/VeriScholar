"""Unit tests for Compiled Academic Wiki database model (wiki_pages)."""

from uuid import uuid4

from api.db.models.wiki import WikiPageModel
from pgvector.sqlalchemy import Vector
from sqlalchemy import UniqueConstraint


def test_wiki_page_model_attributes_and_tablename():
    """Verify WikiPageModel attributes, table name, and defaults."""
    uid = uuid4()
    page = WikiPageModel(
        user_id=uid,
        slug="scaled-dot-product-attention",
        title="Scaled Dot-Product Attention",
        markdown_content="# Scaled Dot-Product Attention\nCore mechanism.",
        yaml_metadata={"tags": ["attention"]},
        wikilinks=["Transformer"],
    )
    assert page.__tablename__ == "wiki_pages"
    assert page.slug == "scaled-dot-product-attention"
    assert page.user_id == uid
    assert page.title == "Scaled Dot-Product Attention"
    assert page.markdown_content == "# Scaled Dot-Product Attention\nCore mechanism."
    assert page.yaml_metadata == {"tags": ["attention"]}
    assert page.wikilinks == ["Transformer"]
    assert page.embedding is None
    assert page.page_type == "topic"
    assert page.folder_id is None


def test_wiki_page_table_constraints():
    """Verify table constraints and Vector column on WikiPageModel."""
    table = WikiPageModel.__table__

    # Check unique constraint uq_wiki_pages_user_slug
    unique_constraints = {c.name: c for c in table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_wiki_pages_user_slug" in unique_constraints
    uq = unique_constraints["uq_wiki_pages_user_slug"]
    uq_cols = {col.name for col in uq.columns}
    assert uq_cols == {"user_id", "slug"}

    # Check Vector(1536) embedding column
    assert "embedding" in table.c
    col = table.c["embedding"]
    assert isinstance(col.type, Vector)
    assert col.type.dim == 1536

    # Check foreign keys
    fk_cols = {fk.column.table.name: fk.parent.name for fk in table.foreign_keys}
    assert fk_cols.get("users") == "user_id"
    assert fk_cols.get("folders") == "folder_id"


def test_wiki_page_synonyms_and_aliases():
    """Verify content_markdown and metadata_json synonyms work seamlessly."""
    uid = uuid4()
    page = WikiPageModel(
        user_id=uid,
        slug="flash-attention",
        title="FlashAttention",
        content_markdown="# FlashAttention\nIO-aware exact attention.",
        metadata_json={"complexity": "O(N)"},
        wikilinks=["GPU", "SRAM"],
    )
    assert page.markdown_content == "# FlashAttention\nIO-aware exact attention."
    assert page.content_markdown == "# FlashAttention\nIO-aware exact attention."
    assert page.yaml_metadata == {"complexity": "O(N)"}
    assert page.metadata_json == {"complexity": "O(N)"}

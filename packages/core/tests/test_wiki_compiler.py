"""Tests for Pure Domain Wiki Compiler (wiki_compiler.py) and Wiki models."""

from core.models.wiki import WikiCompileResult, WikiPageDraft
from core.services.wiki_compiler import WikiCompiler


def test_wiki_compiler_extracts_wikilinks_and_compiles_markdown():
    compiler = WikiCompiler()
    draft = WikiPageDraft(
        title="Scaled Dot-Product Attention",
        summary="A core attention mechanism proposed in Attention Is All You Need.",
        key_insights=[
            "Computes attention weights via softmax(QK^T / sqrt(d_k)).",
            "Quadratic complexity with respect to sequence length.",
        ],
        related_entities=["Transformer", "Multi-Head Attention", "WMT 2014 En-De"],
        source_papers=["Vaswani et al., 2017"],
    )
    result = compiler.compile_page(draft)
    assert isinstance(result, WikiCompileResult)
    assert result.slug == "scaled-dot-product-attention"
    assert result.title == "Scaled Dot-Product Attention"
    assert "[[Transformer]]" in result.markdown
    assert "[[Multi-Head Attention]]" in result.markdown
    assert "scaled-dot-product-attention" in result.yaml_metadata["slug"]
    assert set(result.wikilinks) == {"Transformer", "Multi-Head Attention", "WMT 2014 En-De"}


def test_wiki_compiler_parses_existing_markdown_with_frontmatter():
    compiler = WikiCompiler()
    raw = """---
title: RoPE Positional Encoding
slug: rope-positional-encoding
tags: [embedding, rotary]
---
# RoPE Positional Encoding
RoPE encodes relative position via complex rotation. See [[Transformer]] and [[LLaMA]].
"""
    parsed = compiler.parse_markdown(raw)
    assert isinstance(parsed, WikiCompileResult)
    assert parsed.title == "RoPE Positional Encoding"
    assert parsed.slug == "rope-positional-encoding"
    assert "Transformer" in parsed.wikilinks
    assert "LLaMA" in parsed.wikilinks
    assert parsed.yaml_metadata.get("tags") == ["embedding", "rotary"]


def test_wiki_compiler_extracts_piped_wikilinks():
    compiler = WikiCompiler()
    raw = """---
title: Multi-Head Attention
slug: multi-head-attention
---
# Multi-Head Attention
See [[Transformer|Transformer Architecture]] and [[Scaled Dot-Product Attention]].
"""
    parsed = compiler.parse_markdown(raw)
    assert "Transformer" in parsed.wikilinks
    assert "Scaled Dot-Product Attention" in parsed.wikilinks
    assert len(parsed.wikilinks) == 2


def test_wiki_compiler_parses_markdown_without_frontmatter():
    compiler = WikiCompiler()
    raw = """# FlashAttention

FlashAttention optimizes GPU memory IO. Connected to [[Transformer]] and [[Triton]].
"""
    parsed = compiler.parse_markdown(raw)
    assert parsed.title == "FlashAttention"
    assert parsed.slug == "flashattention"
    assert "Transformer" in parsed.wikilinks
    assert "Triton" in parsed.wikilinks


def test_slugify_normalization():
    compiler = WikiCompiler()
    assert (
        compiler.slugify("Attention Is All You Need (Vaswani et al., 2017)")
        == "attention-is-all-you-need-vaswani-et-al-2017"
    )
    assert compiler.slugify("   Scaled Dot-Product Attention   ") == "scaled-dot-product-attention"
    assert compiler.slugify("GPT-4 / Claude 3.5 Sonnet") == "gpt-4-claude-3-5-sonnet"

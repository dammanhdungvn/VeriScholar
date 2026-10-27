"""Core Query Decomposition Engine for Scholarly Literature Search.

Transforms unstructured user queries into structured academic representations:
identifies DOI/arXiv lookup intents, creates normalized neural queries, builds
arXiv boolean expressions, and extracts key topic tokens.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

# Academic identifier patterns
MODERN_ARXIV_PATTERN = re.compile(r"^(\d{4}\.\d{4,5})(?:v\d+)?$")
LEGACY_ARXIV_PATTERN = re.compile(r"^([a-zA-Z\-]+(?:\.[a-zA-Z]+)?\/\d{7})(?:v\d+)?$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")

# Common English stopwords and academic filler terms
STOPWORDS: set[str] = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "need",
    "needs",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shan't",
    "she",
    "she'd",
    "she'll",
    "she's",
    "should",
    "shouldn't",
    "so",
    "some",
    "such",
    "than",
    "that",
    "that's",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "there's",
    "these",
    "they",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "were",
    "weren't",
    "what",
    "what's",
    "when",
    "when's",
    "where",
    "where's",
    "which",
    "while",
    "who",
    "who's",
    "whom",
    "why",
    "why's",
    "with",
    "won't",
    "would",
    "wouldn't",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


class DecomposedQuery(BaseModel):
    """Structured academic query representation."""

    intent: Literal["doi_lookup", "arxiv_lookup", "keyword_search"] = Field(
        ..., description="Detected query intent classification"
    )
    identifier: str | None = Field(
        default=None,
        description="Cleaned academic identifier (DOI or arXiv ID) if intent is lookup, else None",
    )
    semantic_query: str = Field(
        ...,
        description="Cleaned string suitable for neural and semantic search (e.g. Exa)",
    )
    boolean_arxiv_query: str = Field(
        ...,
        description="Boolean query formatted specifically for arXiv API",
    )
    sub_topics: list[str] = Field(
        default_factory=list,
        description="Key extracted topic keywords in lowercase without stopwords",
    )


class QueryDecomposer:
    """Core Query Decomposition Engine."""

    @classmethod
    def decompose(cls, raw_query: str) -> DecomposedQuery:
        """Decompose a raw user search query into structured academic search directives."""
        clean_query = raw_query.strip()
        if not clean_query:
            return DecomposedQuery(
                intent="keyword_search",
                identifier=None,
                semantic_query="",
                boolean_arxiv_query="",
                sub_topics=[],
            )

        # 1. Check for DOI pattern or DOI prefix/URL
        doi_candidate = clean_query
        doi_prefix = re.match(
            r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", doi_candidate, re.IGNORECASE
        )
        if doi_prefix:
            doi_candidate = doi_candidate[doi_prefix.end() :].strip()

        if DOI_PATTERN.match(doi_candidate):
            return DecomposedQuery(
                intent="doi_lookup",
                identifier=doi_candidate,
                semantic_query=doi_candidate,
                boolean_arxiv_query=f'doi:"{doi_candidate}"',
                sub_topics=[],
            )

        # 2. Check for arXiv ID pattern or arXiv prefix/URL
        arxiv_candidate = clean_query
        arxiv_prefix = re.match(
            r"^(?:https?://arxiv\.org/(?:abs|pdf)/|arxiv:\s*)",
            arxiv_candidate,
            re.IGNORECASE,
        )
        if arxiv_prefix:
            arxiv_candidate = arxiv_candidate[arxiv_prefix.end() :].strip()
            if arxiv_candidate.lower().endswith(".pdf"):
                arxiv_candidate = arxiv_candidate[:-4].strip()

        arxiv_match = MODERN_ARXIV_PATTERN.match(arxiv_candidate) or LEGACY_ARXIV_PATTERN.match(
            arxiv_candidate
        )
        if arxiv_match:
            base_arxiv_id = arxiv_match.group(1)
            return DecomposedQuery(
                intent="arxiv_lookup",
                identifier=base_arxiv_id,
                semantic_query=base_arxiv_id,
                boolean_arxiv_query=f"id:{base_arxiv_id}",
                sub_topics=[],
            )

        # 3. Fallback: Keyword & Semantic Search
        semantic_query = re.sub(r"\s+", " ", clean_query)
        sub_topics = cls._extract_sub_topics(semantic_query)
        boolean_arxiv_query = cls._build_boolean_arxiv_query(semantic_query, sub_topics)

        return DecomposedQuery(
            intent="keyword_search",
            identifier=None,
            semantic_query=semantic_query,
            boolean_arxiv_query=boolean_arxiv_query,
            sub_topics=sub_topics,
        )

    @classmethod
    def _extract_sub_topics(cls, text: str) -> list[str]:
        """Extract key keywords excluding stopwords and normalized by basic singularization."""
        raw_tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        sub_topics: list[str] = []
        seen: set[str] = set()

        for t in raw_tokens:
            if t in STOPWORDS or len(t) < 2:
                continue
            # Basic singularization if ends with 's' and not 'ss' (length > 3)
            if t.endswith("s") and not t.endswith("ss") and len(t) > 3:
                t = t[:-1]
            if t not in seen and t not in STOPWORDS:
                seen.add(t)
                sub_topics.append(t)

        return sub_topics

    @classmethod
    def _build_boolean_arxiv_query(cls, clean_query: str, sub_topics: list[str]) -> str:
        """Build precision arXiv query with title phrase and token conjunctions."""
        clean_phrase = re.sub(r'["\(\)\n\r\t]+', " ", clean_query).strip()
        clean_phrase = re.sub(r"\s+", " ", clean_phrase)

        if sub_topics:
            subset = sub_topics[:4]
            ti_tokens = " AND ".join(f"ti:{t}" for t in subset)
            abs_tokens = " AND ".join(f"abs:{t}" for t in subset)
            return f'ti:"{clean_phrase}" OR ({ti_tokens} AND {abs_tokens})'

        return f'ti:"{clean_phrase}"'

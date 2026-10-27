"""Socratic roadmap service for parsing bridge hint tags and extracting scholarly identifiers.

Adheres strictly to Hexagonal Isolation: pure Python Standard Library only.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

# Regex matching <bridge_hint .../> or <bridge_hint ...>...</bridge_hint>
_BRIDGE_HINT_TAG_PATTERN = re.compile(
    r"[ \t]*<bridge_hint\b((?:[^\"\'<>]|\"[^\"]*\"|'[^']*')*?)(?:/>|>.*?</bridge_hint>|>)[ \t]*",
    re.DOTALL | re.IGNORECASE,
)

# Robust DOI pattern matching 10.xxxx/...
_DOI_PATTERN = re.compile(r"(?i)\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9<>]+)")

# arXiv patterns:
# 1. Explicit mention: arXiv:1706.03762, arxiv.org/abs/..., etc.
_ARXIV_EXPLICIT_PATTERN = re.compile(
    r"(?i)\b(?:arxiv(?:\.org/(?:abs|pdf))?\s*[:/]?\s*|arxiv\s+preprint\s+(?:arxiv\s*:\s*)?)"
    r"([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?|[a-z\-]+(?:\.[a-z\-]+)?/[0-9]{7}(?:v[0-9]+)?)"
)

# 2. arXiv ID inside arXiv DOI: 10.48550/arXiv.1706.03762
_ARXIV_DOI_PATTERN = re.compile(
    r"(?i)10\.\d{4,9}/arxiv\.([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?|[a-z\-]+(?:\.[a-z\-]+)?/[0-9]{7}(?:v[0-9]+)?)"
)

# 3. Standalone arXiv ID: e.g. 1706.03762
_ARXIV_STANDALONE_PATTERN = re.compile(r"(?<![0-9/A-Za-z])([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)\b")


@dataclass
class BridgeHintPayload:
    """Structured payload representing a Socratic pedagogical bridge hint."""

    ref_index: int
    concept_name: str
    reason: str


def _clean_doi(raw_doi: str) -> str:
    """Clean trailing punctuation and unclosed closing brackets/parentheses from DOI."""
    doi = re.sub(r"[.,;:?!]+$", "", raw_doi.strip())
    # Strip unmatched trailing closing delimiters
    if doi.endswith(")") and doi.count(")") > doi.count("("):
        doi = doi[:-1]
    if doi.endswith("]") and doi.count("]") > doi.count("["):
        doi = doi[:-1]
    if doi.endswith(">") and doi.count(">") > doi.count("<"):
        doi = doi[:-1]
    return re.sub(r"[.,;:?!]+$", "", doi)


def _clean_attr_value(val: str) -> str:
    """Unescape XML/HTML entities and unescape backslash-escaped quotes."""
    cleaned = val.replace(r"\"", '"').replace(r"\'", "'")
    return html.unescape(cleaned).strip()


def extract_and_strip_bridge_hint(text: str) -> tuple[str, BridgeHintPayload | None]:
    """Parse the first valid <bridge_hint> tag and strip all hint tags from text.

    Args:
        text: Raw text containing potential <bridge_hint .../> tags.

    Returns:
        A tuple of (cleaned_text, payload or None).
    """
    if not text or not isinstance(text, str):
        return "", None

    matches = list(_BRIDGE_HINT_TAG_PATTERN.finditer(text))
    if not matches:
        return text, None

    first_payload: BridgeHintPayload | None = None
    for m in matches:
        attrs = m.group(1)
        ref_match = re.search(r'\bref_index\s*=\s*["\']?(\d+)["\']?', attrs)
        concept_match = re.search(
            r'\b(?:concept|concept_name)\s*=\s*(["\'])((?:\\.|(?!\1).)*?)\1', attrs
        )
        reason_match = re.search(r'\breason\s*=\s*(["\'])((?:\\.|(?!\1).)*?)\1', attrs)

        if ref_match and concept_match and reason_match:
            try:
                ref_idx = int(ref_match.group(1))
                concept_val = _clean_attr_value(concept_match.group(2))
                reason_val = _clean_attr_value(reason_match.group(2))
                if concept_val and first_payload is None:
                    first_payload = BridgeHintPayload(
                        ref_index=ref_idx,
                        concept_name=concept_val,
                        reason=reason_val,
                    )
            except (ValueError, TypeError):
                continue

    cleaned_text = _BRIDGE_HINT_TAG_PATTERN.sub("", text).strip()
    return cleaned_text, first_payload


def extract_scholarly_identifiers(raw_citation: str) -> dict[str, str | None]:
    """Extract DOI and arXiv identifiers from raw citation string using robust regex.

    Returns:
        dict with keys "doi" and "arxiv_id", values are str or None.
    """
    result: dict[str, str | None] = {"doi": None, "arxiv_id": None}
    if not raw_citation or not isinstance(raw_citation, str):
        return result

    # 1. Extract DOI
    doi_match = _DOI_PATTERN.search(raw_citation)
    if doi_match:
        result["doi"] = _clean_doi(doi_match.group(1))

    # 2. Extract arXiv ID
    # Priority 1: Explicit arXiv mention
    arxiv_match = _ARXIV_EXPLICIT_PATTERN.search(raw_citation)
    if arxiv_match:
        result["arxiv_id"] = arxiv_match.group(1).removesuffix(".pdf")
    else:
        # Priority 2: Extract from arXiv DOI if present
        arxiv_doi_match = _ARXIV_DOI_PATTERN.search(raw_citation)
        if arxiv_doi_match:
            result["arxiv_id"] = arxiv_doi_match.group(1).removesuffix(".pdf")
        else:
            # Priority 3: Standalone arXiv identifier pattern
            standalone_match = _ARXIV_STANDALONE_PATTERN.search(raw_citation)
            if standalone_match:
                result["arxiv_id"] = standalone_match.group(1)

    return result

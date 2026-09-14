"""Domain entity and extractor for scholarly references."""

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedReferenceInfo:
    """Structured academic fields extracted from raw citation text."""

    title: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    arxiv_id: str | None = None
    doi: str | None = None


@dataclass(frozen=True)
class ExtractedReference:
    """Single reference item with index, original raw text, and parsed metadata."""

    ref_index: int
    raw_text: str
    parsed: ParsedReferenceInfo


_ARXIV_PATTERN = re.compile(
    r"(?i)\barxiv(?:[:\s]+|(?:\.org/abs/)|(?:\s+preprint\s+(?:arxiv:)?))\s*"
    r"([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?|[a-z\-]+(?:\.[a-z\-]+)?/[0-9]{7})"
)
_DOI_PATTERN = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")
_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")


def parse_reference_item(raw_item: str, ref_index: int) -> ExtractedReference:
    """Parse a single raw reference string into structured academic fields."""
    # Clean marker like [1], 1., etc.
    cleaned = re.sub(r"^\[\d+\]\s*", "", raw_item.strip())
    cleaned = re.sub(r"^\d+\.\s*", "", cleaned).strip()
    # Normalize whitespace/newlines inside the reference
    cleaned = re.sub(r"\s+", " ", cleaned)

    # 1. Extract DOI
    doi_match = _DOI_PATTERN.search(cleaned)
    doi = doi_match.group(1) if doi_match else None

    # 2. Extract arXiv ID
    arxiv_match = _ARXIV_PATTERN.search(cleaned)
    arxiv_id = arxiv_match.group(1) if arxiv_match else None

    # 3. Extract Year (prefer last 4-digit year found)
    years = _YEAR_PATTERN.findall(cleaned)
    year = int(years[-1]) if years else None

    # 4. Extract Authors and Title using standard academic punctuation
    authors: list[str] = []
    title: str | None = None

    # Try finding quoted title first: "Title" or ``Title''
    quoted_title_match = re.search(r'["“`](.+?)["”\']', cleaned)
    if quoted_title_match:
        title = quoted_title_match.group(1).strip()
        author_segment = cleaned[: quoted_title_match.start()].rstrip("., ")
        if author_segment:
            authors = [
                a.strip()
                for a in re.split(r",\s*(?:and\s+)?|\s+and\s+", author_segment)
                if a.strip()
            ]
    else:
        # Standard format: Author1, Author2, and Author3. Title. Journal/Venue...
        parts = cleaned.split(". ")
        if len(parts) >= 2:
            author_segment = parts[0].strip()
            title = parts[1].strip()
            authors = [
                a.strip()
                for a in re.split(r",\s*(?:and\s+)?|\s+and\s+", author_segment)
                if a.strip()
            ]
        else:
            title = cleaned

    parsed_info = ParsedReferenceInfo(
        title=title,
        authors=authors,
        year=year,
        arxiv_id=arxiv_id,
        doi=doi,
    )
    return ExtractedReference(
        ref_index=ref_index,
        raw_text=cleaned,
        parsed=parsed_info,
    )


def extract_references_from_text(references_text: str) -> list[ExtractedReference]:
    """Extract and parse all reference entries from a raw references text block."""
    if not references_text or not references_text.strip():
        return []

    # Try bracketed numbering: [1] ... [2] ...
    bracket_blocks = re.findall(r"(\[\d+\]\s*.+?)(?=\[\d+\]|\Z)", references_text, re.DOTALL)
    if bracket_blocks:
        extracted: list[ExtractedReference] = []
        for i, block in enumerate(bracket_blocks, start=1):
            extracted.append(parse_reference_item(block, ref_index=i))
        return extracted

    # Try numbered lines: 1. ... 2. ...
    numbered_blocks = re.findall(
        r"(?:^|\n)(\d+\.\s*.+?)(?=(?:\n\d+\.|\Z))", references_text, re.DOTALL
    )
    if numbered_blocks:
        extracted = []
        for i, block in enumerate(numbered_blocks, start=1):
            extracted.append(parse_reference_item(block, ref_index=i))
        return extracted

    # Fallback: line-by-line separation if entries separated by double newlines
    paragraphs = [p.strip() for p in references_text.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        return [parse_reference_item(p, ref_index=i) for i, p in enumerate(paragraphs, start=1)]

    # Single block fallback
    return [parse_reference_item(references_text, ref_index=1)]

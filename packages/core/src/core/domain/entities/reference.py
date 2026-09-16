"""Reference domain entity and parsing logic for scientific documents."""

import re

from pydantic import BaseModel, Field


class ParsedReferenceInfo(BaseModel):
    """Structured fields parsed from a raw reference citation string."""

    title: str | None = Field(
        default=None, description="Extracted academic work title or paper title"
    )
    authors: list[str] = Field(
        default_factory=list,
        description="Extracted list of author names formatted as Surname, Initials",
    )
    year: int | None = Field(default=None, description="Publication year (4-digit integer)")
    arxiv_id: str | None = Field(default=None, description="arXiv identifier e.g. 2404.14219")
    doi: str | None = Field(
        default=None, description="Digital Object Identifier without URL prefix"
    )


class ExtractedReference(BaseModel):
    """Single reference item with index, original raw text, and parsed metadata."""

    ref_index: int
    raw_text: str
    parsed: ParsedReferenceInfo


_ARXIV_PATTERN = re.compile(
    r"(?i)(?:\barxiv(?:\.org/abs/|/abs/|[:\s]+|\s+preprint\s+(?:arxiv:)?|\.)|doi\.org/10\.\d+/arxiv\.)\s*"
    r"([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?|[a-z\-]+(?:\.[a-z\-]+)?/[0-9]{7})"
)
_DOI_PATTERN = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")
_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")


def _pair_authors(tokens: list[str]) -> list[str]:
    """Pair up comma-separated Surname, Initials into unified author entries."""
    paired: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if i + 1 < len(tokens) and re.match(r"^[A-Z](\.[A-Z])*\.?$", tokens[i + 1]):
            initials = tokens[i + 1] if tokens[i + 1].endswith(".") else f"{tokens[i + 1]}."
            paired.append(f"{token}, {initials}")
            i += 2
        else:
            paired.append(token)
            i += 1
    return paired


def _parse_authors(author_segment: str) -> list[str]:
    """Extract list of authors from a citation author segment."""
    if not author_segment:
        return []
    raw_tokens = [
        a.strip()
        for a in re.split(r",\s*(?:and\s+|&\s*)?|;\s*|\s+and\s+|\s+&\s+", author_segment)
        if a.strip()
    ]
    return _pair_authors(raw_tokens)


def parse_reference_item(raw_item: str, ref_index: int) -> ExtractedReference:
    """Parse a single raw reference string into structured academic fields."""
    # Clean marker like [1], 1., etc.
    cleaned = re.sub(r"^\s*\[\d+\]\s*", "", raw_item.strip())
    cleaned = re.sub(r"^\s*\d+\.\s*", "", cleaned).strip()
    # Normalize whitespace/newlines inside the reference
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Strip PDF running headers / footers at page boundaries (e.g. "Reconstructing Context 15")
    cleaned = re.sub(r"\s+Reconstructing Context\s+\d+\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\d{1,3}\s*$", "", cleaned)

    # Normalize broken URLs/identifiers caused by PDF line-wrapping
    cleaned = re.sub(r"https?:\s*//\s*", "https://", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"arxiv\.\s*org", "arxiv.org", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"doi\.\s*org", "doi.org", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"https?://doi\.org/https?://doi\.org/", "https://doi.org/", cleaned)

    # 1. Extract DOI
    doi_match = _DOI_PATTERN.search(cleaned)
    doi = doi_match.group(1).rstrip(".") if doi_match else None

    # 2. Extract arXiv ID
    arxiv_match = _ARXIV_PATTERN.search(cleaned)
    arxiv_id = arxiv_match.group(1) if arxiv_match else None

    # 3. Extract Year with priority to academic citation dates
    # First: check date in parentheses: (2020), (03 2016), (Oct 2024), (10 2024)
    paren_year_match = re.search(
        r"\((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})\s+)?((?:19|20)\d{2})\)",
        cleaned,
        re.IGNORECASE,
    )
    if paren_year_match:
        year = int(paren_year_match.group(1))
    else:
        # Standalone year not followed by decimal/digits (avoiding arXiv IDs like 2004.04906)
        year_candidates = re.findall(r"(?<!\d|\/)(?:19|20)\d{2}(?!\.\d|\d)", cleaned)
        year = int(year_candidates[0]) if year_candidates else None

    # 4. Extract Authors and Title using academic citation patterns
    authors: list[str] = []
    title: str | None = None

    # Format 1: Quoted title e.g. "Title." or “Title.”
    quoted_match = re.search(r"\"([^\"]+)\"|“([^”]+)”|`([^`]+)`", cleaned)
    if quoted_match:
        title = (
            (quoted_match.group(1) or quoted_match.group(2) or quoted_match.group(3))
            .strip()
            .rstrip(".")
        )
        author_segment = cleaned[: quoted_match.start()].rstrip(", ")
        authors = _parse_authors(author_segment)

    # Format 2: Colon-separated authors (Springer LNCS, NeurIPS, ICML, arXiv)
    # e.g., "Abdin, M., ..., Zhou, X.: Phi-3 technical report..."
    colon_idx = cleaned.find(": ")
    if not title and colon_idx != -1 and colon_idx < 3000:
        candidate = cleaned[:colon_idx].strip()
        lower_cand = candidate.lower()
        ignored_prefixes = ("arxiv", "doi", "http", "in:", "vol.", "pp.")
        has_author_sep = (
            "," in candidate or " and " in candidate or "&" in candidate or ".ai" in lower_cand
        )
        if not any(p in lower_cand for p in ignored_prefixes) and has_author_sep:
            authors = _parse_authors(candidate)
            rest = cleaned[colon_idx + 2 :].strip()
            m_title = re.match(
                r"^(.+?)(?:\s*\((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})\s+)?(?:19|20)\d{2}\)|\.\s+(?:vol\.|pp\.|In:|https?://|[A-Z][a-z]+)|\s*,\s*https?://)",
                rest,
                re.IGNORECASE,
            )
            if m_title:
                title = m_title.group(1).strip().rstrip(".")
            else:
                title = rest.split(". ")[0].strip().rstrip(".")

    # Format 3: APA style e.g. "Vaswani, A., ... (2017). Attention is all you need. Advances..."
    if not title:
        apa_match = re.search(r"\((19\d{2}|20\d{2})\)\.\s+([^.]+)\.", cleaned)
        if apa_match:
            authors = _parse_authors(cleaned[: apa_match.start()].rstrip(", "))
            title = apa_match.group(2).strip().rstrip(".")

    # Format 4: Period-separated fallback
    if not title:
        m_authors_title = re.search(
            r"^(.+?(?:&|and|et al\.?)[^.]+?\.)\s+([A-Z0-9][^.]+\.)",
            cleaned,
        )
        if m_authors_title:
            authors = _parse_authors(m_authors_title.group(1).rstrip("."))
            title = m_authors_title.group(2).strip().rstrip(".")
        else:
            parts = cleaned.split(". ")
            if len(parts) >= 2:
                authors = _parse_authors(parts[0].strip())
                title = parts[1].strip().rstrip(".")
            else:
                title = cleaned

    # Post-process title: strip any remaining trailing date in parentheses
    if title:
        title = (
            re.sub(
                r"\s*\((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})\s+)?(?:19|20)\d{2}\)$",
                "",
                title,
                flags=re.IGNORECASE,
            )
            .strip()
            .rstrip(".")
        )

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
    bracket_blocks = re.findall(
        r"(\[\d{1,4}\]\s*.+?)(?=(?:\[\d{1,4}\]|\Z))", references_text, re.DOTALL
    )
    if bracket_blocks:
        extracted: list[ExtractedReference] = []
        for i, block in enumerate(bracket_blocks, start=1):
            ref = parse_reference_item(block, i)
            extracted.append(ref)
        return extracted

    # Try numbered lines: 1. ... 2. ... (require 1-3 digits + dot + space)
    # Using lookahead to ensure clean split across entries even if text wraps
    numbered_blocks = re.findall(
        r"(?:^|\n)\s*(\d{1,3})\.\s+(.+?)(?=(?:\n\s*\d{1,3}\.\s+|\Z))",
        references_text,
        re.DOTALL,
    )
    if numbered_blocks:
        extracted = []
        for num_str, block in numbered_blocks:
            idx = int(num_str) if num_str.isdigit() else len(extracted) + 1
            ref = parse_reference_item(block, idx)
            extracted.append(ref)
        return extracted

    # Fallback to paragraph splitting by double newlines
    paragraphs = [p.strip() for p in references_text.split("\n\n") if p.strip()]
    if paragraphs:
        return [parse_reference_item(p, idx) for idx, p in enumerate(paragraphs, start=1)]

    return []

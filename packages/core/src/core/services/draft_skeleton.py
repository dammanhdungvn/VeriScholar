"""Academic Draft Skeleton Generator and Asset Security Guard.

Generates validated LaTeX/BibTeX starter scaffolds for the Reading-to-Writing bridge
and enforces path traversal / Zip Slip security validation on uploaded assets.
"""

from __future__ import annotations

import re
from typing import Any

# Allowed characters for asset filenames: alphanumeric, underscore, hyphen, dot
VALID_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
DEFAULT_MAX_ASSET_BYTES = 10 * 1024 * 1024  # 10MB per asset


class ZipSlipSecurityError(ValueError):
    """Raised when an asset filename violates path traversal or containment invariants."""

    pass


def escape_bibtex_value(val: Any) -> str:
    """Deterministically escape BibTeX special characters (&, %, _, #, $).

    Uses negative lookbehind to avoid double-escaping already escaped characters.
    """
    if val is None:
        return ""
    text = str(val)
    # Spec 3.A: escaped_title = re.sub(r'(?<!\\)([&%_$#])', r'\\\1', raw_title)
    return re.sub(r"(?<!\\)([&%_$#])", r"\\\1", text)


def sanitize_and_validate_asset_filename(
    filename: str,
    byte_size: int,
    max_bytes: int = DEFAULT_MAX_ASSET_BYTES,
) -> str:
    """Validate asset filename against Path Traversal (Zip Slip) and enforce size boundaries.

    Args:
        filename: Base name of the file to be stored in figures/.
        byte_size: Size of the payload in bytes.
        max_bytes: Maximum allowed size per file (default: 10MB).

    Returns:
        The validated clean filename.

    Raises:
        ValueError / ZipSlipSecurityError: If filename or size violates constraints.
    """
    if not filename or not isinstance(filename, str):
        raise ZipSlipSecurityError("Asset filename cannot be empty.")

    clean_name = filename.strip()
    if not clean_name:
        raise ZipSlipSecurityError("Asset filename cannot be empty.")

    # Guard against Path Traversal / Zip Slip
    if ".." in clean_name or "/" in clean_name or "\\" in clean_name:
        raise ZipSlipSecurityError(
            f"Path traversal characters detected in asset filename: '{clean_name}'"
        )

    # Disallow hidden files
    if clean_name.startswith("."):
        raise ZipSlipSecurityError(f"Hidden asset files are disallowed: '{clean_name}'")

    # Ensure file has a valid extension
    if "." not in clean_name or clean_name.endswith("."):
        raise ZipSlipSecurityError(
            f"Asset filename must include a valid file extension: '{clean_name}'"
        )

    # Strict regex check
    if not VALID_FILENAME_REGEX.match(clean_name):
        raise ZipSlipSecurityError(f"Asset filename contains prohibited characters: '{clean_name}'")

    # File size validation
    if byte_size <= 0:
        raise ValueError(f"Asset file size must be greater than 0 bytes (got {byte_size}).")

    if byte_size > max_bytes:
        raise ValueError(f"Asset file size ({byte_size} bytes) exceeds limit ({max_bytes} bytes).")

    return clean_name


def generate_academic_skeleton(
    title: str,
    papers: list[dict[str, Any]],
    notes: list[dict[str, Any]] | None = None,
) -> tuple[str, str]:
    """Generate a syntactically valid LaTeX academic manuscript and BibTeX bibliography.

    Args:
        title: Title of the draft / reading session.
        papers: List of paper metadata dictionaries from the research library.
        notes: Optional user notes taken during reading sessions.

    Returns:
        tuple[str, str]: (main_tex, references_bib)
    """
    notes = notes or []
    clean_title = escape_bibtex_value(title.strip() if title else "Academic Research Draft")

    # 1. Build references.bib
    bib_entries: list[str] = []
    cite_keys: list[str] = []

    for idx, paper in enumerate(papers, 1):
        raw_key = (
            paper.get("citation_key") or paper.get("citekey") or paper.get("id") or f"paper_{idx}"
        )
        cite_key = re.sub(r"[^a-zA-Z0-9_\-]", "", str(raw_key)) or f"paper_{idx}"
        cite_keys.append(cite_key)

        p_title = escape_bibtex_value(paper.get("title", "Untitled Research"))

        # Format authors
        raw_authors = paper.get("authors", [])
        if isinstance(raw_authors, list):
            escaped_authors = [escape_bibtex_value(a) for a in raw_authors if a]
            author_str = " and ".join(escaped_authors) if escaped_authors else "VeriScholar Scholar"
        else:
            author_str = escape_bibtex_value(raw_authors) if raw_authors else "VeriScholar Scholar"

        raw_year = paper.get("year", 2024)
        year_str = escape_bibtex_value(str(raw_year)) if raw_year else "2024"

        entry_lines = [
            f"@article{{{cite_key},",
            f"  title = {{{p_title}}},",
            f"  author = {{{author_str}}},",
            f"  year = {{{year_str}}}",
            "}",
        ]
        bib_entries.append("\n".join(entry_lines))

    references_bib = "\n\n".join(bib_entries) + ("\n" if bib_entries else "")

    # 2. Build Related Work citations
    related_work_paragraphs: list[str] = []
    if papers:
        citation_sentences: list[str] = []
        for paper, key in zip(papers, cite_keys, strict=False):
            p_title = escape_bibtex_value(paper.get("title", "this study"))
            citation_sentences.append(
                f"Prior literature explores foundational aspects in ``{p_title}'' \\cite{{{key}}}."
            )
        related_work_paragraphs.append(" ".join(citation_sentences))
    else:
        related_work_paragraphs.append(
            "Relevant literature and contextual frameworks are reviewed in this section."
        )

    # 3. Format Reading Session Notes
    notes_paragraphs: list[str] = []
    if notes:
        notes_paragraphs.append("\\subsection*{Session Notes}")
        for note in notes:
            note_content = note.get("content") or note.get("text") or note.get("note") or str(note)
            clean_note = escape_bibtex_value(note_content)
            notes_paragraphs.append(f"\\paragraph{{Note:}} {clean_note}")

    notes_section_body = "\n\n".join(notes_paragraphs)
    related_work_body = "\n\n".join(related_work_paragraphs)

    abstract_text = (
        "This academic manuscript is initiated from an exploratory research reading session. "
        "It establishes a coherent research problem, synthesizes literature, "
        "and formalizes methodology."
    )
    intro_text = (
        "Scientific investigation begins with continuous synthesis of established empirical "
        "findings and theoretical formulations. This document serves as a structured draft "
        "for subsequent development."
    )
    method_text = (
        "In this section, we formulate the proposed framework, detailing architectural hypotheses "
        "and formal analytical derivations."
    )
    exp_text = (
        "Empirical evaluation protocols, baseline comparisons, and diagnostic benchmarks "
        "are outlined here."
    )
    concl_text = (
        "We synthesize the preliminary insights of this research and highlight directions "
        "for subsequent investigations."
    )

    # 4. Assemble main.tex
    main_tex = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{cite}}

\\title{{{clean_title}}}
\\author{{VeriScholar Scholar}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{abstract_text}
\\end{{abstract}}

\\section{{Introduction}}
{intro_text}

\\section{{Related Work}}
{related_work_body}

{notes_section_body}

\\section{{Methodology}}
{method_text}

\\section{{Experiments}}
{exp_text}

\\section{{Conclusion}}
{concl_text}

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""

    return main_tex, references_bib

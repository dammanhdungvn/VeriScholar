"""Unit tests for reference extraction domain logic (100% in-memory)."""

from core.domain.entities.reference import (
    extract_references_from_text,
    parse_reference_item,
)


def test_parse_reference_item_with_arxiv_and_authors() -> None:
    """Validate extraction of author, title, year, and arxiv_id from IEEE/ACM style citation."""
    raw = (
        "[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. "
        "Layer normalization. arXiv preprint arXiv:1607.06450, 2016."
    )
    ref = parse_reference_item(raw, ref_index=1)

    assert ref.ref_index == 1
    assert ref.parsed.title == "Layer normalization"
    assert ref.parsed.authors == ["Jimmy Lei Ba", "Jamie Ryan Kiros", "Geoffrey E Hinton"]
    assert ref.parsed.year == 2016
    assert ref.parsed.arxiv_id == "1607.06450"
    assert ref.parsed.doi is None


def test_parse_reference_item_with_doi() -> None:
    """Validate extraction of DOI from citation."""
    raw = (
        "[2] John Doe and Jane Smith. Attention mechanisms in NLP. "
        "Journal of AI Research, 2021. doi:10.1145/1234567.890123"
    )
    ref = parse_reference_item(raw, ref_index=2)

    assert ref.ref_index == 2
    assert ref.parsed.doi == "10.1145/1234567.890123"
    assert ref.parsed.year == 2021
    assert ref.parsed.authors == ["John Doe", "Jane Smith"]


def test_extract_references_from_multi_item_block() -> None:
    """Validate segmentation of multiple references in bracketed format."""
    block = """
    [1] Author One. Title One. arXiv:2001.00001, 2020.
    [2] Author Two and Author Three. Title Two. 2021.
    [3] Author Four. Title Three. 10.1000/182, 2019.
    """
    refs = extract_references_from_text(block)

    assert len(refs) == 3
    assert refs[0].ref_index == 1
    assert refs[0].parsed.arxiv_id == "2001.00001"
    assert refs[1].ref_index == 2
    assert refs[1].parsed.year == 2021
    assert refs[2].ref_index == 3
    assert refs[2].parsed.doi == "10.1000/182"


def test_extract_references_from_empty_text() -> None:
    """Empty or whitespace text should return empty list."""
    assert extract_references_from_text("") == []
    assert extract_references_from_text("   \n\t  ") == []

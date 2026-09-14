"""Unit tests for reference extraction and parsing domain logic."""

from core.domain.entities.reference import (
    extract_references_from_text,
    parse_reference_item,
)


def test_parse_reference_item_with_arxiv_and_authors() -> None:
    """Ensure standard academic format parses authors, title, year, and arxiv_id."""
    raw = (
        "1. Smith, J., Doe, A. & Brown, C. Efficient Transformer Architecture. "
        "arXiv:2301.12345, 2023."
    )
    ref = parse_reference_item(raw, ref_index=1)

    assert ref.ref_index == 1
    assert ref.parsed.arxiv_id == "2301.12345"
    assert ref.parsed.year == 2023
    assert len(ref.parsed.authors) == 3
    assert "Smith, J." in ref.parsed.authors
    assert "Doe, A." in ref.parsed.authors
    assert "Brown, C." in ref.parsed.authors


def test_parse_reference_item_with_doi() -> None:
    """Ensure DOI is properly captured and cleaned."""
    raw = (
        "[5] Johnson, M. Deep Learning in Genomics. Nature, "
        "https://doi.org/10.1038/s41586-020-2649-2, 2020."
    )
    ref = parse_reference_item(raw, ref_index=5)

    assert ref.ref_index == 5
    assert ref.parsed.doi == "10.1038/s41586-020-2649-2"
    assert ref.parsed.year == 2020


def test_parse_reference_item_springer_lncs_colon_format() -> None:
    """Ensure Springer LNCS / NeurIPS colon author format parses properly."""
    raw = (
        "Abdin, M., Aneja, J., Awadalla, H., Zhou, X.: "
        "Phi-3 technical report: A highly capable language model locally on your phone (2024), "
        "https://arxiv.org/abs/2404.14219"
    )
    ref = parse_reference_item(raw, ref_index=1)

    assert (
        ref.parsed.title
        == "Phi-3 technical report: A highly capable language model locally on your phone"
    )
    assert ref.parsed.year == 2024
    assert ref.parsed.arxiv_id == "2404.14219"
    assert len(ref.parsed.authors) == 4
    assert ref.parsed.authors[0] == "Abdin, M."
    assert ref.parsed.authors[-1] == "Zhou, X."


def test_parse_reference_item_apa_style() -> None:
    """Ensure APA format with (Year). Title. is correctly parsed."""
    raw = (
        "Vaswani, A., Shazeer, N., & Parmar, N. (2017). "
        "Attention is all you need. Advances in Neural Information Processing Systems. "
        "https://arxiv.org/abs/1706.03762"
    )
    ref = parse_reference_item(raw, ref_index=1)

    assert ref.parsed.title == "Attention is all you need"
    assert ref.parsed.authors == ["Vaswani, A.", "Shazeer, N.", "Parmar, N."]
    assert ref.parsed.year == 2017
    assert ref.parsed.arxiv_id == "1706.03762"


def test_parse_reference_item_prefers_publication_year_over_arxiv_prefix() -> None:
    """Ensure year 2020 in (2020) is chosen instead of 2004 from arXiv 2004.04906."""
    raw = (
        "Karpukhin, V., Lewis, P., Edunov, S.: "
        "Dense passage retrieval for open-domain question answering (2020), "
        "https: //arxiv.org/abs/2004.04906"
    )
    ref = parse_reference_item(raw, ref_index=13)

    assert ref.parsed.title == "Dense passage retrieval for open-domain question answering"
    assert ref.parsed.year == 2020
    assert ref.parsed.arxiv_id == "2004.04906"


def test_parse_reference_item_normalizes_split_arxiv_and_cleans_title_dates() -> None:
    """Ensure space-split arxiv. org is normalized and month-year parens stripped from title."""
    raw_item_split_arxiv = (
        "Hsieh, C.Y., Chuang, Y.S., Pfister, T.: Found in the middle: "
        "Calibrating positional attention bias improves long context utilization (2024), "
        "https://arxiv. org/abs/2406.16008"
    )
    ref1 = parse_reference_item(raw_item_split_arxiv, ref_index=11)
    assert ref1.parsed.arxiv_id == "2406.16008"
    assert ref1.parsed.year == 2024
    expected_title1 = (
        "Found in the middle: "
        "Calibrating positional attention bias improves long context utilization"
    )
    assert ref1.parsed.title == expected_title1

    raw_item_month_year = (
        "Gupta, S., Ranjan, R., Singh, S.: A comprehensive survey of retrieval-augmented "
        "generation (rag): Evolution, current landscape and future directions (10 2024). "
        "https://doi.org/10.48550/arXiv.2410.12837"
    )
    ref2 = parse_reference_item(raw_item_month_year, ref_index=8)
    assert ref2.parsed.year == 2024
    expected_title2 = (
        "A comprehensive survey of retrieval-augmented generation (rag): "
        "Evolution, current landscape and future directions"
    )
    assert ref2.parsed.title == expected_title2
    assert ref2.parsed.doi == "10.48550/arXiv.2410.12837"
    assert ref2.parsed.arxiv_id == "2410.12837"


def test_extract_references_does_not_split_on_wrapped_arxiv_links() -> None:
    """Ensure newline-wrapped arxiv links like 2406.14673 do not create false items."""
    raw_block = """
1. Author One, A.: First Paper Title (2024), https://arxiv.org/abs/
2406.14673
2. Author Two, B.: Second Paper Title (2023). https://doi.org/10.1016/j.neucom.2023.126356
"""
    refs = extract_references_from_text(raw_block)
    assert len(refs) == 2
    assert refs[0].ref_index == 1
    assert refs[0].parsed.arxiv_id == "2406.14673"
    assert refs[0].parsed.title == "First Paper Title"
    assert refs[1].ref_index == 2
    assert refs[1].parsed.doi == "10.1016/j.neucom.2023.126356"


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

from core.services.socratic_roadmap import (
    BridgeHintPayload,
    extract_and_strip_bridge_hint,
    extract_scholarly_identifiers,
)


def test_extract_and_strip_bridge_hint_tag():
    raw_output = (
        "Cơ chế này dựa trên tích vô hướng có tỷ lệ.\n"
        '<bridge_hint ref_index="3" concept="Scaled Dot-Product Attention" '
        'reason="Bài [3] trình bày chứng minh gốc về hệ số 1/sqrt(d_k)." />'
    )
    cleaned_text, hint = extract_and_strip_bridge_hint(raw_output)
    assert "<bridge_hint" not in cleaned_text
    assert hint is not None
    assert isinstance(hint, BridgeHintPayload)
    assert hint.ref_index == 3
    assert hint.concept_name == "Scaled Dot-Product Attention"
    assert "1/sqrt(d_k)" in hint.reason
    assert cleaned_text == "Cơ chế này dựa trên tích vô hướng có tỷ lệ."


def test_extract_and_strip_multiple_tags_extracts_first_and_strips_all():
    raw_output = (
        "Phần mở đầu thảo luận về Transformer.\n"
        '<bridge_hint ref_index="3" concept="Attention Mechanism" reason="Nền tảng kiến trúc." />\n'
        "Tiếp theo là phần cơ chế căn chỉnh.\n"
        '<bridge_hint ref_index="14" concept="Alignment" reason="Kế thừa căn chỉnh chuỗi." />\n'
        "Lời kết tóm lược."
    )
    cleaned_text, hint = extract_and_strip_bridge_hint(raw_output)
    assert "<bridge_hint" not in cleaned_text
    assert hint is not None
    assert hint.ref_index == 3
    assert hint.concept_name == "Attention Mechanism"
    assert "Phần mở đầu thảo luận về Transformer." in cleaned_text
    assert "Tiếp theo là phần cơ chế căn chỉnh." in cleaned_text
    assert "Lời kết tóm lược." in cleaned_text


def test_extract_and_strip_attribute_permutations_and_closing_tags():
    # Tag with closing tag syntax and different attribute order
    raw_output = (
        'Giải thích chi tiết.\n<bridge_hint reason="Giải thích DDPM" '
        'concept_name="Diffusion Models" ref_index="7"></bridge_hint>'
    )
    cleaned_text, hint = extract_and_strip_bridge_hint(raw_output)
    assert "<bridge_hint" not in cleaned_text
    assert "</bridge_hint>" not in cleaned_text
    assert hint is not None
    assert hint.ref_index == 7
    assert hint.concept_name == "Diffusion Models"
    assert hint.reason == "Giải thích DDPM"


def test_extract_and_strip_no_tags():
    raw = "Văn bản thông thường không có thẻ gợi ý nào."
    cleaned_text, hint = extract_and_strip_bridge_hint(raw)
    assert cleaned_text == raw
    assert hint is None


def test_extract_and_strip_malformed_tag_returns_none():
    raw = 'Văn bản có thẻ lỗi: <bridge_hint ref_index="abc" concept="" />'
    cleaned_text, hint = extract_and_strip_bridge_hint(raw)
    assert "<bridge_hint" not in cleaned_text
    assert hint is None


def test_extract_scholarly_identifiers_handles_doi_and_arxiv():
    cite = "Vaswani et al. (2017). Attention is all you need. arXiv:1706.03762, doi:10.48550/arXiv.1706.03762."
    ids = extract_scholarly_identifiers(cite)
    assert ids["arxiv_id"] == "1706.03762"
    assert ids["doi"] == "10.48550/arXiv.1706.03762"


def test_extract_scholarly_identifiers_doi_variations():
    # Standard DOI with URL prefix and trailing punctuation
    cite1 = "He et al. (2016). Deep Residual Learning. https://doi.org/10.1109/CVPR.2016.90."
    ids1 = extract_scholarly_identifiers(cite1)
    assert ids1["doi"] == "10.1109/CVPR.2016.90"

    # DOI inside parenthesis
    cite2 = "Smith et al. (doi: 10.1016/j.artint.2020.103342)."
    ids2 = extract_scholarly_identifiers(cite2)
    assert ids2["doi"] == "10.1016/j.artint.2020.103342"

    # Legacy DOI with internal parentheses
    cite3 = "Legacy paper 10.1002/(SICI)1097-0142(19960715)78:2<285::AID-CNCR14>3.0.CO;2-N."
    ids3 = extract_scholarly_identifiers(cite3)
    assert ids3["doi"] == "10.1002/(SICI)1097-0142(19960715)78:2<285::AID-CNCR14>3.0.CO;2-N"


def test_extract_scholarly_identifiers_arxiv_variations():
    # arXiv with version and URL
    cite1 = "Ho et al. (2020). Denoising Diffusion. https://arxiv.org/abs/2006.11239v2"
    ids1 = extract_scholarly_identifiers(cite1)
    assert ids1["arxiv_id"] == "2006.11239v2"

    # arXiv preprint format with space
    cite2 = "Preprint arXiv: 2301.12345 [cs.AI]."
    ids2 = extract_scholarly_identifiers(cite2)
    assert ids2["arxiv_id"] == "2301.12345"

    # ArXiv extracted from arXiv DOI when no explicit arXiv prefix is in text
    cite3 = "Paper with doi only: 10.48550/arXiv.1512.03385"
    ids3 = extract_scholarly_identifiers(cite3)
    assert ids3["arxiv_id"] == "1512.03385"
    assert ids3["doi"] == "10.48550/arXiv.1512.03385"


def test_extract_scholarly_identifiers_books_and_malformed():
    # Book citation with no DOI or arXiv
    cite_book = (
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "
        "Introduction to Algorithms (3rd ed.). MIT Press."
    )
    ids_book = extract_scholarly_identifiers(cite_book)
    assert ids_book["doi"] is None
    assert ids_book["arxiv_id"] is None

    # Empty and invalid inputs
    assert extract_scholarly_identifiers("") == {"doi": None, "arxiv_id": None}
    assert extract_scholarly_identifiers(None) == {"doi": None, "arxiv_id": None}  # type: ignore[arg-type]

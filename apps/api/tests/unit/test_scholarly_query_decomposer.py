"""Unit tests for scholarly query decomposition engine."""

from api.services.query_decomposer import DecomposedQuery, QueryDecomposer


def test_doi_lookup_direct():
    query = "10.1109/CVPR.2016.90"
    res = QueryDecomposer.decompose(query)

    assert isinstance(res, DecomposedQuery)
    assert res.intent == "doi_lookup"
    assert res.identifier == "10.1109/CVPR.2016.90"
    assert "10.1109/CVPR.2016.90" in res.semantic_query
    assert 'doi:"10.1109/CVPR.2016.90"' in res.boolean_arxiv_query


def test_doi_lookup_with_prefix_and_spaces():
    query = "doi: 10.1109/CVPR.2016.90"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "doi_lookup"
    assert res.identifier == "10.1109/CVPR.2016.90"
    assert 'doi:"10.1109/CVPR.2016.90"' in res.boolean_arxiv_query


def test_doi_lookup_with_url():
    query = "https://doi.org/10.1038/s42256-024-00800-x"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "doi_lookup"
    assert res.identifier == "10.1038/s42256-024-00800-x"
    assert 'doi:"10.1038/s42256-024-00800-x"' in res.boolean_arxiv_query


def test_arxiv_lookup_standard_id():
    query = "2305.18290"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "arxiv_lookup"
    assert res.identifier == "2305.18290"
    assert "2305.18290" in res.semantic_query
    assert "2305.18290" in res.boolean_arxiv_query


def test_arxiv_lookup_with_prefix_and_version():
    query = "arxiv:1706.03762v2"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "arxiv_lookup"
    assert res.identifier == "1706.03762"
    assert "1706.03762" in res.boolean_arxiv_query


def test_arxiv_lookup_with_url():
    query = "https://arxiv.org/abs/1706.03762v3"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "arxiv_lookup"
    assert res.identifier == "1706.03762"
    assert "1706.03762" in res.boolean_arxiv_query


def test_long_semantic_query_decomposition():
    query = "Attention Is All You Need Transformer architectures for NLP"
    res = QueryDecomposer.decompose(query)

    assert res.intent == "keyword_search"
    assert res.identifier is None
    assert res.semantic_query == "Attention Is All You Need Transformer architectures for NLP"
    for expected_keyword in ["attention", "transformer", "architecture", "nlp"]:
        assert expected_keyword in res.sub_topics

    # Check arXiv boolean format: ti:"..." OR (ti:... AND abs:...)
    assert 'ti:"' in res.boolean_arxiv_query
    assert " OR " in res.boolean_arxiv_query
    assert "ti:" in res.boolean_arxiv_query
    assert "abs:" in res.boolean_arxiv_query


def test_empty_or_whitespace_query():
    res = QueryDecomposer.decompose("   ")

    assert res.intent == "keyword_search"
    assert res.identifier is None
    assert res.semantic_query == ""
    assert res.boolean_arxiv_query == ""
    assert res.sub_topics == []


def test_instantiated_decomposer():
    decomposer = QueryDecomposer()
    res = decomposer.decompose("2305.18290")
    assert res.intent == "arxiv_lookup"
    assert res.identifier == "2305.18290"

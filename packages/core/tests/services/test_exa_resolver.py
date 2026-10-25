"""Unit test suite for ExaAcademicResolverAdapter and GlobalAcademicCache.

Aligns with VeriScholar PRD §3.3:
- Exa Neural Search integration & query synthesis.
- Deterministic In-Memory Resolver double.
- Global Academic Cache with normalized DOI / arXiv keys (< 10ms SLA).
- Strict Public-Only Cache Isolation Invariant (private drafts rejected).
- Resilient fallback on zero results or API failures.
"""

import time
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    ResolvedAcademicReference,
)
from core.services.academic_cache import (
    GlobalAcademicCache,
    normalize_arxiv,
    normalize_doi,
)
from core.services.exa_resolver import (
    ExaAcademicResolverAdapter,
    InMemoryAcademicResolverAdapter,
)

# ==============================================================================
# 1. GlobalAcademicCache Unit Tests
# ==============================================================================


def test_normalize_doi_cases() -> None:
    """Validate DOI normalization handles URLs, prefixes, and trailing symbols."""
    assert normalize_doi("https://doi.org/10.1145/3372278.3390678") == "10.1145/3372278.3390678"
    doi_dx = "http://dx.doi.org/10.1038/s41586-020-2649-2."
    assert normalize_doi(doi_dx) == "10.1038/s41586-020-2649-2"
    assert normalize_doi("doi: 10.48550/arXiv.2404.14219/") == "10.48550/arxiv.2404.14219"
    assert normalize_doi("10.1007/978-3-030-58951-6_1") == "10.1007/978-3-030-58951-6_1"
    assert normalize_doi(None) is None
    assert normalize_doi("   ") is None


def test_normalize_arxiv_cases() -> None:
    """Validate arXiv identifier normalization handles URLs and extensions."""
    assert normalize_arxiv("https://arxiv.org/abs/2404.14219") == "2404.14219"
    assert normalize_arxiv("https://arxiv.org/pdf/2404.14219.pdf") == "2404.14219"
    assert normalize_arxiv("arXiv: 1706.03762v5") == "1706.03762v5"
    assert normalize_arxiv("2404.14219.pdf") == "2404.14219"
    assert normalize_arxiv(None) is None
    assert normalize_arxiv("") is None


def test_cache_public_only_isolation_invariant() -> None:
    """Strict Invariant: Private preprints or user drafts MUST NOT be cached globally."""
    cache = GlobalAcademicCache()

    private_ref = ResolvedAcademicReference(
        ref_index=1,
        raw_text="My private unpublished draft",
        title="Secret Algorithmic Discovery",
        authors=["Alice Doe"],
        year=2026,
        doi="10.1234/draft-doi",
        arxiv_id="2601.99999",
    )

    # Attempt to cache with is_public=False
    saved = cache.set(private_ref, is_public=False)
    assert saved is False
    assert cache.size() == 0
    assert cache.get("doi:10.1234/draft-doi") is None
    assert cache.get("arxiv:2601.99999") is None

    # Entry without DOI or arXiv is also rejected from global public cache
    no_id_ref = ResolvedAcademicReference(
        ref_index=2,
        raw_text="Random citation without standard ID",
        title="Unknown Paper",
        authors=["Bob Smith"],
    )
    saved_no_id = cache.set(no_id_ref, is_public=True)
    assert saved_no_id is False
    assert cache.size() == 0


def test_cache_hit_latency_and_retrieval() -> None:
    """Validate cache hit latency is well within < 10ms SLA."""
    cache = GlobalAcademicCache(ttl_seconds=3600)

    public_ref = ResolvedAcademicReference(
        ref_index=1,
        raw_text="Attention is All You Need",
        title="Attention Is All You Need",
        authors=["Vaswani, A.", "Shazeer, N."],
        year=2017,
        doi="10.5555/3295222.3295349",
        arxiv_id="1706.03762",
        open_access_pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
    )

    assert cache.set(public_ref, is_public=True) is True
    assert cache.size() == 3  # Stored under doi, arxiv, and title keys

    t0 = time.perf_counter()
    res_doi = cache.get("doi:10.5555/3295222.3295349")
    t1 = time.perf_counter()

    latency_ms = (t1 - t0) * 1000.0
    assert latency_ms < 10.0, f"Cache latency {latency_ms:.3f}ms exceeded 10ms SLA!"
    assert res_doi is not None
    assert res_doi.title == "Attention Is All You Need"
    assert res_doi.arxiv_id == "1706.03762"

    # Also test get_by_reference lookup
    extracted = ExtractedReference(
        ref_index=1,
        raw_text="Attention is All You Need",
        parsed=ParsedReferenceInfo(
            title="Attention Is All You Need",
            arxiv_id="1706.03762",
        ),
    )
    res_extracted = cache.get_by_reference(extracted)
    assert res_extracted is not None
    assert res_extracted.doi == "10.5555/3295222.3295349"


def test_cache_ttl_expiration() -> None:
    """Validate that entries expire and are purged when TTL expires."""
    cache = GlobalAcademicCache(ttl_seconds=0.05)  # 50ms TTL

    ref = ResolvedAcademicReference(
        ref_index=1,
        raw_text="Ephemeral Citation",
        title="Ephemeral Paper",
        arxiv_id="2401.00001",
    )
    cache.set(ref, is_public=True)
    assert cache.get("arxiv:2401.00001") is not None

    time.sleep(0.06)
    assert cache.get("arxiv:2401.00001") is None
    assert cache.size() == 0


# ==============================================================================
# 2. InMemoryAcademicResolverAdapter Unit Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_in_memory_resolver_deterministic_synthesis() -> None:
    """Validate InMemoryAcademicResolverAdapter generates structured academic metadata."""
    adapter = InMemoryAcademicResolverAdapter()

    ref = ExtractedReference(
        ref_index=3,
        raw_text="Radford et al., Language Models are Unsupervised Multitask Learners. 2019.",
        parsed=ParsedReferenceInfo(
            title="Language Models are Unsupervised Multitask Learners",
            authors=["Radford, A.", "Wu, J."],
            year=2019,
            arxiv_id="1901.00001",
        ),
    )

    resolved = await adapter.resolve_reference(ref)

    assert resolved.ref_index == 3
    assert resolved.title == "Language Models are Unsupervised Multitask Learners"
    assert resolved.authors == ["Radford, A.", "Wu, J."]
    assert resolved.year == 2019
    assert resolved.arxiv_id == "1901.00001"
    assert resolved.open_access_pdf_url == "https://arxiv.org/pdf/1901.00001.pdf"
    assert "arXiv" in resolved.sources
    assert resolved.landing_url == "https://arxiv.org/abs/1901.00001"
    assert resolved.is_ingested is False


@pytest.mark.asyncio
async def test_in_memory_resolver_mock_injection() -> None:
    """Validate that pre-registered mocks take priority."""
    adapter = InMemoryAcademicResolverAdapter()

    custom_resolved = ResolvedAcademicReference(
        ref_index=1,
        raw_text="Custom Reference",
        title="Injected Mock Discovery",
        authors=["Custom Author"],
        year=2025,
        doi="10.9999/injected",
        open_access_pdf_url="https://example.com/custom.pdf",
    )
    adapter.register_mock("10.9999/injected", custom_resolved)

    ref = ExtractedReference(
        ref_index=5,
        raw_text="Custom Reference",
        parsed=ParsedReferenceInfo(
            title="Some other title",
            doi="10.9999/injected",
        ),
    )

    resolved = await adapter.resolve_reference(ref)
    assert resolved.ref_index == 5
    assert resolved.title == "Injected Mock Discovery"
    assert resolved.doi == "10.9999/injected"
    assert resolved.open_access_pdf_url == "https://example.com/custom.pdf"


# ==============================================================================
# 3. ExaAcademicResolverAdapter Unit Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_exa_resolver_fallback_when_no_api_key() -> None:
    """When EXA_API_KEY is empty, adapter seamlessly falls back to InMemory adapter."""
    cache = GlobalAcademicCache()
    fallback = InMemoryAcademicResolverAdapter()
    adapter = ExaAcademicResolverAdapter(
        api_key="",
        cache=cache,
        fallback_adapter=fallback,
    )

    ref = ExtractedReference(
        ref_index=1,
        raw_text="Devlin et al., BERT: Pre-training of Deep Bidirectional Transformers (2018)",
        parsed=ParsedReferenceInfo(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            arxiv_id="1810.04805",
        ),
    )

    resolved = await adapter.resolve_reference(ref)
    assert resolved.title == "BERT: Pre-training of Deep Bidirectional Transformers"
    assert resolved.open_access_pdf_url == "https://arxiv.org/pdf/1810.04805.pdf"
    # Should also be cached in global cache
    assert cache.get("arxiv:1810.04805") is not None


@pytest.mark.asyncio
async def test_exa_resolver_successful_http_response() -> None:
    """Mock Exa API 200 OK response with research paper results."""
    mock_exa_response: dict[str, Any] = {
        "results": [
            {
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "author": ["Ashish Vaswani", "Noam Shazeer"],
                "summary": "Dominant sequence transduction models use recurrent networks.",
                "highlights": ["We propose the Transformer architecture."],
                "citationCount": 95000,
            }
        ]
    }

    # Mock transport
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=mock_exa_response))
    client = httpx.AsyncClient(transport=transport)

    cache = GlobalAcademicCache()
    adapter = ExaAcademicResolverAdapter(
        api_key="mock-exa-key-12345",
        cache=cache,
        http_client=client,
    )

    ref = ExtractedReference(
        ref_index=1,
        raw_text="Vaswani et al. 2017. Attention is all you need.",
        parsed=ParsedReferenceInfo(
            title="Attention is all you need",
            authors=["Vaswani, A."],
        ),
    )

    resolved = await adapter.resolve_reference(ref)

    assert resolved.title == "Attention Is All You Need"
    assert resolved.authors == ["Ashish Vaswani", "Noam Shazeer"]
    assert resolved.arxiv_id == "1706.03762"
    assert resolved.open_access_pdf_url == "https://arxiv.org/pdf/1706.03762.pdf"
    assert resolved.citation_count == 95000
    assert "Exa" in resolved.sources
    assert "arXiv" in resolved.sources
    assert resolved.abstract is not None
    assert "Dominant sequence transduction models" in resolved.abstract

    # Subsequent resolution must hit cache without invoking HTTP
    client.post = AsyncMock(side_effect=RuntimeError("Should hit cache, not call HTTP!"))
    cached_res = await adapter.resolve_reference(ref)
    assert cached_res.title == "Attention Is All You Need"

    await client.aclose()


@pytest.mark.asyncio
async def test_exa_resolver_zero_results_fallback() -> None:
    """When Exa returns 0 results, fall back gracefully to deterministic adapter."""
    mock_zero_response: dict[str, Any] = {"results": []}

    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=mock_zero_response))
    client = httpx.AsyncClient(transport=transport)

    adapter = ExaAcademicResolverAdapter(
        api_key="mock-exa-key",
        http_client=client,
    )

    ref = ExtractedReference(
        ref_index=2,
        raw_text="Obscure Unpublished Work (2024)",
        parsed=ParsedReferenceInfo(
            title="Obscure Unpublished Work",
            authors=["John Doe"],
            year=2024,
        ),
    )

    resolved = await adapter.resolve_reference(ref)
    assert resolved.title == "Obscure Unpublished Work"
    assert "Deterministic" in resolved.sources
    assert adapter.cache.size() == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_exa_resolver_error_resilience() -> None:
    """When Exa returns 500 Internal Server Error or network timeout, fall back cleanly."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(500, text="Internal Server Error")
    )
    client = httpx.AsyncClient(transport=transport)

    adapter = ExaAcademicResolverAdapter(
        api_key="mock-exa-key",
        http_client=client,
    )

    ref = ExtractedReference(
        ref_index=1,
        raw_text="Resilience Test Paper (2023)",
        parsed=ParsedReferenceInfo(
            title="Resilience Test Paper",
            arxiv_id="2301.00001",
        ),
    )

    resolved = await adapter.resolve_reference(ref)
    assert resolved.title == "Resilience Test Paper"
    assert resolved.arxiv_id == "2301.00001"
    assert resolved.open_access_pdf_url == "https://arxiv.org/pdf/2301.00001.pdf"

    await client.aclose()


@pytest.mark.asyncio
async def test_exa_resolver_batch_resolution() -> None:
    """Validate resolve_batch processes multiple references concurrently."""
    adapter = InMemoryAcademicResolverAdapter()

    refs = [
        ExtractedReference(
            ref_index=i,
            raw_text=f"Batch Reference #{i}",
            parsed=ParsedReferenceInfo(
                title=f"Paper Title #{i}",
                year=2020 + i,
                arxiv_id=f"200{i}.0000{i}",
            ),
        )
        for i in range(1, 5)
    ]

    resolved_list = await adapter.resolve_batch(refs)

    assert len(resolved_list) == 4
    for idx, r in enumerate(resolved_list, start=1):
        assert r.ref_index == idx
        assert r.title == f"Paper Title #{idx}"
        assert r.open_access_pdf_url == f"https://arxiv.org/pdf/200{idx}.0000{idx}.pdf"

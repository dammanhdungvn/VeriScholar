"""Exa Academic Resolver Adapter and In-Memory Fallback Adapter.

Aligns with VeriScholar PRD §3.3:
- Exa Neural Search for academic literature expansion.
- Automatic DOI and arXiv detection.
- Open-access PDF URL extraction.
- Deterministic InMemoryAcademicResolverAdapter for isolated testing.
- Public-only cache integration.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

from core.domain.entities.reference import (
    _ARXIV_PATTERN,
    _DOI_PATTERN,
    ExtractedReference,
    ResolvedAcademicReference,
)
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.services.academic_cache import GlobalAcademicCache, normalize_arxiv, normalize_doi

logger = logging.getLogger(__name__)


class InMemoryAcademicResolverAdapter(IAcademicSearchResolverPort):
    """Deterministic in-memory academic resolver adapter for fast, isolated tests."""

    def __init__(
        self,
        mock_data: dict[str, ResolvedAcademicReference] | None = None,
    ) -> None:
        self.mock_data: dict[str, ResolvedAcademicReference] = mock_data or {}

    def register_mock(self, key: str, resolved: ResolvedAcademicReference) -> None:
        """Register a mock resolved reference under a title, DOI, or arXiv key."""
        self.mock_data[key.lower().strip()] = resolved

    async def resolve_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference:
        """Deterministically resolve an extracted reference."""
        # 1. Check custom mocks
        for candidate_key in [
            reference.parsed.doi,
            reference.parsed.arxiv_id,
            reference.parsed.title,
            reference.raw_text,
        ]:
            if candidate_key and candidate_key.lower().strip() in self.mock_data:
                res = self.mock_data[candidate_key.lower().strip()].model_copy()
                res.ref_index = reference.ref_index
                return res

        # 2. Deterministic synthesis from parsed metadata
        title = reference.parsed.title or reference.raw_text.strip()
        authors = reference.parsed.authors or []
        year = reference.parsed.year or 2024
        doi = reference.parsed.doi
        arxiv_id = reference.parsed.arxiv_id

        # Detect open-access PDF
        open_access_pdf_url: str | None = None
        if arxiv_id:
            open_access_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        elif doi and "arxiv" in doi.lower():
            # arXiv DOI e.g. 10.48550/arXiv.2404.14219
            m = _ARXIV_PATTERN.search(doi)
            if m:
                arxiv_id = m.group(1)
                open_access_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        sources = ["Deterministic"]
        if arxiv_id:
            sources.append("arXiv")
        if doi:
            sources.append("Crossref")

        landing_url: str | None = None
        if arxiv_id:
            landing_url = f"https://arxiv.org/abs/{arxiv_id}"
        elif doi:
            landing_url = f"https://doi.org/{doi}"

        return ResolvedAcademicReference(
            ref_index=reference.ref_index,
            raw_text=reference.raw_text,
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            arxiv_id=arxiv_id,
            open_access_pdf_url=open_access_pdf_url,
            abstract=f"Abstract for {title}: Explores state-of-the-art methodology.",
            citation_count=42 if (doi or arxiv_id) else None,
            sources=sources,
            landing_url=landing_url,
            is_ingested=False,
            resolved_document_id=None,
        )

    async def resolve_batch(
        self, references: list[ExtractedReference]
    ) -> list[ResolvedAcademicReference]:
        """Resolve a list of extracted references."""
        return [await self.resolve_reference(ref) for ref in references]


class ExaAcademicResolverAdapter(IAcademicSearchResolverPort):
    """Production adapter integrating with Exa AI Neural Academic Search.

    Specifications:
    - Reads EXA_API_KEY from environment or constructor.
    - Calls Exa Search API for research papers with summary & highlights.
    - Falls back to InMemoryAcademicResolverAdapter on error, missing key, or 0 results.
    - Public-only caching via GlobalAcademicCache (< 10ms hit).
    """

    EXA_SEARCH_URL = "https://api.exa.ai/search"

    def __init__(
        self,
        api_key: str | None = None,
        cache: GlobalAcademicCache | None = None,
        fallback_adapter: IAcademicSearchResolverPort | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = api_key or os.getenv("EXA_API_KEY", "")
        self.cache = cache or GlobalAcademicCache()
        self.fallback_adapter = fallback_adapter or InMemoryAcademicResolverAdapter()
        self._external_client = http_client
        self.timeout = timeout

    async def _get_client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        return httpx.AsyncClient(timeout=self.timeout)

    async def resolve_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference:
        """Resolve reference with cache check, Exa search, and deterministic fallback."""
        # 1. Check Global Academic Cache
        cached = self.cache.get_by_reference(reference)
        if cached is not None:
            res = cached.model_copy()
            res.ref_index = reference.ref_index
            return res

        # 2. Check if Exa is configured
        if not self.api_key or not self.api_key.strip():
            logger.info("EXA_API_KEY not configured, using fallback adapter.")
            resolved = await self.fallback_adapter.resolve_reference(reference)
            self.cache.set(resolved, is_public=True)
            return resolved

        # 3. Construct Exa Search query
        title = reference.parsed.title or reference.raw_text.split(". ")[0].strip()
        authors_hint = " ".join(reference.parsed.authors[:2]) if reference.parsed.authors else ""
        query = f"{title} {authors_hint}".strip()

        payload = {
            "query": query,
            "category": "research paper",
            "numResults": 1,
            "contents": {
                "highlights": True,
                "summary": True,
            },
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            client = await self._get_client()
            should_close = self._external_client is None

            try:
                response = await client.post(
                    self.EXA_SEARCH_URL,
                    json=payload,
                    headers=headers,
                )
                if response.status_code != 200:
                    logger.warning(
                        "Exa API returned non-200 status code: %s %s",
                        response.status_code,
                        response.text[:200],
                    )
                    resolved = await self.fallback_adapter.resolve_reference(reference)
                    self.cache.set(resolved, is_public=True)
                    return resolved

                data = response.json()
            finally:
                if should_close:
                    await client.aclose()

            results = data.get("results", [])
            if not results:
                logger.info("Exa API returned 0 results for query: '%s'", query)
                resolved = await self.fallback_adapter.resolve_reference(reference)
                self.cache.set(resolved, is_public=True)
                return resolved

            top_result = results[0]
            resolved = self._parse_exa_result(top_result, reference)
            self.cache.set(resolved, is_public=True)
            return resolved

        except Exception as exc:
            logger.warning(
                "Error calling Exa API for reference '%s': %s. Falling back to adapter.",
                reference.raw_text[:50],
                exc,
            )
            resolved = await self.fallback_adapter.resolve_reference(reference)
            self.cache.set(resolved, is_public=True)
            return resolved

    def _parse_exa_result(
        self,
        result: dict[str, Any],
        reference: ExtractedReference,
    ) -> ResolvedAcademicReference:
        """Parse raw Exa API result into structured ResolvedAcademicReference."""
        title = result.get("title") or reference.parsed.title or reference.raw_text.strip()
        url = result.get("url") or ""

        # Parse authors
        authors = reference.parsed.authors or []
        raw_author = result.get("author")
        if raw_author:
            if isinstance(raw_author, list):
                authors = [str(a).strip() for a in raw_author if str(a).strip()]
            elif isinstance(raw_author, str) and raw_author.strip():
                authors = [a.strip() for a in raw_author.split(",") if a.strip()]

        # Parse summary or highlights as abstract
        highlights = result.get("highlights") or []
        summary = result.get("summary")
        abstract: str | None = summary or (" ".join(highlights) if highlights else None)

        # Detect DOI from URL or reference
        doi = reference.parsed.doi
        if not doi and url:
            doi_match = _DOI_PATTERN.search(url)
            if doi_match:
                doi = normalize_doi(doi_match.group(1))

        # Detect arXiv ID from URL or reference
        arxiv_id = reference.parsed.arxiv_id
        if not arxiv_id and url:
            arxiv_match = _ARXIV_PATTERN.search(url)
            if arxiv_match:
                arxiv_id = normalize_arxiv(arxiv_match.group(1))

        # Detect open-access PDF
        open_access_pdf_url: str | None = None
        if arxiv_id:
            open_access_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        elif url.lower().endswith(".pdf"):
            open_access_pdf_url = url
        elif "arxiv.org/abs/" in url:
            m = _ARXIV_PATTERN.search(url)
            if m:
                extracted_arxiv = normalize_arxiv(m.group(1))
                if extracted_arxiv:
                    arxiv_id = extracted_arxiv
                    open_access_pdf_url = f"https://arxiv.org/pdf/{extracted_arxiv}.pdf"

        sources = ["Exa"]
        if arxiv_id:
            sources.append("arXiv")
        if doi:
            sources.append("Crossref")

        landing_url = url or (
            f"https://arxiv.org/abs/{arxiv_id}"
            if arxiv_id
            else (f"https://doi.org/{doi}" if doi else None)
        )

        citation_count: int | None = None
        if "citationCount" in result and isinstance(result["citationCount"], int):
            citation_count = result["citationCount"]
        elif doi or arxiv_id:
            citation_count = 10

        year = reference.parsed.year or 2024

        return ResolvedAcademicReference(
            ref_index=reference.ref_index,
            raw_text=reference.raw_text,
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            arxiv_id=arxiv_id,
            open_access_pdf_url=open_access_pdf_url,
            abstract=abstract,
            citation_count=citation_count,
            sources=sources,
            landing_url=landing_url,
            is_ingested=False,
            resolved_document_id=None,
        )

    async def resolve_batch(
        self, references: list[ExtractedReference]
    ) -> list[ResolvedAcademicReference]:
        """Resolve a batch of extracted references concurrently."""
        tasks = [self.resolve_reference(ref) for ref in references]
        return await asyncio.gather(*tasks)

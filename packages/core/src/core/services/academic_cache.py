"""Global Academic Cache with strict Public-Only Cache Isolation and normalized keys.

Aligns with VeriScholar PRD §3.3 & System Architecture:
- Cache resolved public papers by normalized key (doi:10.xxx or arxiv:xxxx.xxxxx).
- Cache TTL: 24 hours (86,400 seconds).
- Strict Public-Only Cache Isolation Invariant: User unstarred / private preprints
  or unpublished drafts MUST NOT be stored in global cache.
- Ultra-low latency (< 10ms hit time).
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass

from core.domain.entities.reference import ExtractedReference, ResolvedAcademicReference


def normalize_doi(raw_doi: str | None) -> str | None:
    """Normalize DOI string by lowercasing and stripping prefixes and trailing punctuation."""
    if not raw_doi or not raw_doi.strip():
        return None
    cleaned = raw_doi.strip().lower()
    cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    cleaned = cleaned.rstrip("./")
    # Validate basic DOI structure 10.xxxx/...
    if not re.match(r"^10\.\d{4,9}/[-._;()/:a-z0-9]+$", cleaned):
        return None
    return cleaned


def normalize_arxiv(raw_arxiv: str | None) -> str | None:
    """Normalize arXiv identifier by lowercasing and stripping URLs and extensions."""
    if not raw_arxiv or not raw_arxiv.strip():
        return None
    cleaned = raw_arxiv.strip().lower()
    cleaned = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", cleaned)
    cleaned = re.sub(r"^arxiv:\s*", "", cleaned)
    cleaned = re.sub(r"\.pdf$", "", cleaned)
    cleaned = cleaned.rstrip("./")
    return cleaned if cleaned else None


def normalize_title(raw_title: str | None) -> str | None:
    """Normalize paper title for case-insensitive punctuation-agnostic cache indexing."""
    if not raw_title or not raw_title.strip():
        return None
    cleaned = re.sub(r"[^\w\s]", "", raw_title.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) >= 5 else None


@dataclass
class _CacheEntry:
    reference: ResolvedAcademicReference
    cached_at: float


class GlobalAcademicCache:
    """Thread-safe in-memory cache for resolved public academic references."""

    DEFAULT_TTL_SECONDS = 86400  # 24 hours

    def __init__(self, ttl_seconds: float = DEFAULT_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> ResolvedAcademicReference | None:
        """Retrieve a cached reference by normalized key if not expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if time.time() - entry.cached_at > self.ttl_seconds:
                del self._cache[key]
                return None
            return entry.reference.model_copy()

    def get_by_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference | None:
        """Lookup cached resolution using DOI, arXiv ID, or title from extracted reference."""
        doi_key = None
        if reference.parsed.doi:
            norm_doi = normalize_doi(reference.parsed.doi)
            if norm_doi:
                doi_key = f"doi:{norm_doi}"

        arxiv_key = None
        if reference.parsed.arxiv_id:
            norm_arxiv = normalize_arxiv(reference.parsed.arxiv_id)
            if norm_arxiv:
                arxiv_key = f"arxiv:{norm_arxiv}"

        if doi_key:
            res = self.get(doi_key)
            if res is not None:
                return res

        if arxiv_key:
            res = self.get(arxiv_key)
            if res is not None:
                return res

        # Title-based lookup if present
        candidate_title = reference.parsed.title or reference.raw_text
        norm_t = normalize_title(candidate_title)
        if norm_t:
            res = self.get(f"title:{norm_t}")
            if res is not None:
                return res

        return None

    def set(self, reference: ResolvedAcademicReference, is_public: bool = True) -> bool:
        """Store a resolved reference in the global cache.

        Strict Public-Only Cache Isolation Invariant:
        - If is_public is False, do NOT cache (enforces tenant privacy).
        - If neither DOI nor arXiv ID is present, do NOT cache in public cache.
        """
        if not is_public:
            return False

        norm_doi = normalize_doi(reference.doi)
        norm_arxiv = normalize_arxiv(reference.arxiv_id)

        # Only public literature with standard identifier can be cached globally
        if not norm_doi and not norm_arxiv:
            return False

        norm_t = normalize_title(reference.title)
        now = time.time()
        stored = False

        with self._lock:
            if norm_doi:
                self._cache[f"doi:{norm_doi}"] = _CacheEntry(
                    reference=reference.model_copy(),
                    cached_at=now,
                )
                stored = True

            if norm_arxiv:
                self._cache[f"arxiv:{norm_arxiv}"] = _CacheEntry(
                    reference=reference.model_copy(),
                    cached_at=now,
                )
                stored = True

            if norm_t:
                self._cache[f"title:{norm_t}"] = _CacheEntry(
                    reference=reference.model_copy(),
                    cached_at=now,
                )
                stored = True

        return stored

    def delete(self, key: str) -> bool:
        """Remove an item from cache by key."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all entries in the cache."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Return the number of unexpired entries currently in cache."""
        now = time.time()
        with self._lock:
            # Purge expired entries
            expired_keys = [
                k for k, v in self._cache.items() if now - v.cached_at > self.ttl_seconds
            ]
            for k in expired_keys:
                del self._cache[k]
            return len(self._cache)

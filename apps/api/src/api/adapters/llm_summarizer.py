"""LLM Grounded Document Summarizer Adapter.

Generates 3-point grounded summaries (problem_statement, contributions, limitations)
using OpenAI-compatible LLM endpoints with structured JSON responses and
spatial visual bounding box alignment via PyMuPDF.
Includes automatic fallback to HeuristicGroundedSummarizer when offline or unconfigured.
"""

import json
import logging
import re
import time
from typing import Any
from uuid import UUID

import httpx
from api.adapters.heuristic_summarizer import HeuristicGroundedSummarizer
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.summary import DocumentSummary, SummaryPoint
from core.domain.value_objects.bounding_box import BoundingBox
from core.ports.summary import IDocumentSummarizerPort
from core.prompts import default_registry

logger = logging.getLogger(__name__)


class LLMGroundedSummarizer(IDocumentSummarizerPort):
    """LLM-backed summarizer with resilient zero-downtime heuristic fallback."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-5.6-luna",
        fallback: IDocumentSummarizerPort | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback = fallback or HeuristicGroundedSummarizer()
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _select_representative_chunks(
        chunks: list[DocumentChunk], max_chunks: int = 16
    ) -> list[DocumentChunk]:
        """Select representative chunks combining head and tail/structural sections."""
        if len(chunks) <= max_chunks:
            return chunks

        selected_indices: set[int] = set()

        # 1. Take first 8 chunks (Abstract, Intro, Method overview, Contributions)
        head_count = min(8, len(chunks))
        for i in range(head_count):
            selected_indices.add(i)

        # 2. Search intermediate and tail chunks for limitations or discussion
        keyword_targets = (
            "limitation",
            "threats to validity",
            "future work",
            "discussion",
            "conclusion",
        )
        keyword_matches: list[int] = []
        for i in range(head_count, len(chunks)):
            c_text = chunks[i].content.lower()
            if any(kw in c_text for kw in keyword_targets) and "references" not in c_text[:60]:
                keyword_matches.append(i)

        for idx in keyword_matches[:5]:
            selected_indices.add(idx)

        # 3. Always include tail chunks (before references if possible, or last 4 chunks)
        tail_count = 4
        start_tail = max(head_count, len(chunks) - tail_count)
        for i in range(start_tail, len(chunks)):
            selected_indices.add(i)

        # Sort selected by original chunk index to preserve narrative flow
        sorted_indices = sorted(selected_indices)[:max_chunks]
        return [chunks[i] for i in sorted_indices]

    async def summarize(
        self,
        document_id: UUID,
        title: str | None,
        abstract: str | None,
        chunks: list[DocumentChunk],
        pdf_bytes: bytes | None = None,
    ) -> DocumentSummary:
        """Generate 3-point grounded summary via LLM, falling back to heuristic on failure."""
        if not self.api_key or not self.api_key.strip():
            logger.info(
                "LLM API key not configured. Using HeuristicGroundedSummarizer for document %s",
                document_id,
            )
            return await self.fallback.summarize(document_id, title, abstract, chunks, pdf_bytes)

        start_time = time.perf_counter()
        try:
            # Build context combining head and tail/structural sections
            repr_chunks = self._select_representative_chunks(chunks, max_chunks=16)

            # Load prompt template from Prompts-as-Code registry
            prompt_tmpl = default_registry.get("document-grounded-summary")
            messages = prompt_tmpl.render_messages(
                title=title or "Unknown",
                abstract=abstract or "Not available",
                chunks=repr_chunks,
            )

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if not response.is_success:
                    logger.warning(
                        "LLM API returned %s: %s",
                        response.status_code,
                        response.text,
                    )
                response.raise_for_status()
                data = response.json()

            content_raw = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            parsed_json = json.loads(content_raw)

            # Ground coordinates using quotes and PyMuPDF
            problem_boxes = self._resolve_grounding_boxes(
                parsed_json.get("problem_quote", ""), chunks, pdf_bytes
            )
            contrib_boxes = self._resolve_grounding_boxes(
                parsed_json.get("contribution_quote", ""), chunks, pdf_bytes
            )
            limitation_boxes = self._resolve_grounding_boxes(
                parsed_json.get("limitation_quote", ""), chunks, pdf_bytes
            )

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            return DocumentSummary(
                document_id=document_id,
                problem_statement=SummaryPoint(
                    text=parsed_json.get("problem_statement", "").strip()
                    or "Core research problem identified.",
                    bounding_boxes=problem_boxes,
                ),
                contributions=SummaryPoint(
                    text=parsed_json.get("contributions", "").strip()
                    or "Key methodological contribution proposed.",
                    bounding_boxes=contrib_boxes,
                ),
                limitations=SummaryPoint(
                    text=parsed_json.get("limitations", "").strip()
                    or "Empirical limitations and constraints highlighted.",
                    bounding_boxes=limitation_boxes,
                ),
                total_tokens=total_tokens,
                latency_ms=latency_ms,
            )

        except Exception as exc:
            logger.warning(
                "LLM generation failed for document %s: %s. Falling back to heuristic summarizer.",
                document_id,
                exc,
            )
            return await self.fallback.summarize(document_id, title, abstract, chunks, pdf_bytes)

    def _resolve_grounding_boxes(
        self,
        quote: str,
        chunks: list[DocumentChunk],
        pdf_bytes: bytes | None,
    ) -> list[BoundingBox]:
        """Resolve visual bounding boxes for an extracted quote with multi-tier search."""
        if not chunks:
            return []

        fallback_boxes = chunks[0].bounding_boxes if chunks[0].bounding_boxes else []
        if not quote or not quote.strip():
            return fallback_boxes

        # Clean quote: normalize spaces, strip quotes and trailing punctuation
        quote_clean = re.sub(r"\s+", " ", quote.strip().strip("\"'“”"))
        words = quote_clean.split()

        # 1. Search in PDF via PyMuPDF if bytes are available
        if pdf_bytes and words:
            import pymupdf

            try:
                doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
                # Multi-tier sub-query: try 10 words, then 6 words if first fails
                candidate_queries: list[str] = []
                if len(words) >= 10:
                    candidate_queries.append(" ".join(words[:10]))
                if len(words) >= 6:
                    candidate_queries.append(" ".join(words[:6]))
                candidate_queries.append(quote_clean)

                for query in candidate_queries:
                    found_boxes: list[BoundingBox] = []
                    for page_idx in range(len(doc)):
                        page = doc[page_idx]
                        rects = page.search_for(query)
                        if rects:
                            w, h = page.rect.width, page.rect.height
                            for r in rects:
                                found_boxes.append(
                                    BoundingBox(
                                        x0=round(max(0.0, min(1.0, r.x0 / w)), 4),
                                        y0=round(max(0.0, min(1.0, r.y0 / h)), 4),
                                        x1=round(max(0.0, min(1.0, r.x1 / w)), 4),
                                        y1=round(max(0.0, min(1.0, r.y1 / h)), 4),
                                        page=page_idx + 1,
                                    )
                                )
                            return found_boxes
            except Exception as e:
                logger.debug("PDF micro-search failed for quote '%s': %s", quote_clean[:30], e)

        # 2. Search in chunks by text containment (with whitespace normalization)
        normalized_quote = quote_clean.lower()
        sub_needle = " ".join(words[:6]).lower() if len(words) >= 6 else normalized_quote

        for chunk in chunks:
            chunk_text_norm = re.sub(r"\s+", " ", chunk.content.lower())
            if (
                normalized_quote in chunk_text_norm or sub_needle in chunk_text_norm
            ) and chunk.bounding_boxes:
                return chunk.bounding_boxes

        return fallback_boxes

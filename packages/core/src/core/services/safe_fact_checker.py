"""SAFE (Search-Augmented Factuality Evaluator) Core Domain Engine (Module 2).

Implements the 4-stage factual verification pipeline according to PRD §3.2:
1. Fact Decomposition: Breaks complex sentences into atomic factual propositions.
2. Entity & Context Normalization: Resolves anaphora and ambiguous pronouns.
3. Targeted Retrieval Matching: Locates candidate evidence passages from literature chunks.
4. NLI Scoring with Premise Context Augmentation:
   - 🟢 SUPPORTED: Supported by evidence with page & bounding box coordinates.
   - 🔴 CONTRADICTED: Direct contradiction or numerical mismatch detected.
   - 🟡 NOT_ENOUGH_INFO: Insufficient evidence in literature repository.
"""

from __future__ import annotations

import asyncio
import re
import time
from uuid import UUID

import structlog

from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.safe_claim import (
    AtomicClaim,
    FactVerificationReport,
    FactVerificationStatus,
)
from core.ports.safe_verifier import ISafeNliPort

logger = structlog.get_logger("core.services.safe_fact_checker")

# Pronouns and demonstratives requiring entity resolution
DEMONSTRATIVE_PATTERNS = [
    (
        re.compile(
            r"\b(this model|this approach|this method|the proposed method)\b",
            re.IGNORECASE,
        ),
        "proposed system",
    ),
    (re.compile(r"\b(the authors|they|the researchers)\b", re.IGNORECASE), "authors"),
    (re.compile(r"\b(it achieves|it achieves an?)\b", re.IGNORECASE), "the model achieves"),
]

# Negation and contradiction indicator pairs (hypothesis vs premise)
CONTRADICTION_PAIRS = [
    ("outperform", "underperform"),
    ("surpass", "fail to match"),
    ("superior", "inferior"),
    ("improve", "degrade"),
    ("increase", "decrease"),
    ("higher", "lower"),
    ("faster", "slower"),
    ("effective", "ineffective"),
    ("better", "worse"),
]


def clean_latex_for_fact_checking(text: str) -> str:
    """Extract and sanitize verifiable academic prose from raw LaTeX source code.

    Strips LaTeX preambles, comments, environments, math formulas, citations,
    and command markup so that only genuine factual prose claims are evaluated.
    """
    if not text:
        return ""

    cleaned = text

    # 1. Preamble & postamble: if \begin{document} is present, discard everything before it.
    if r"\begin{document}" in cleaned:
        cleaned = cleaned.split(r"\begin{document}", 1)[1]
    if r"\end{document}" in cleaned:
        cleaned = cleaned.split(r"\end{document}", 1)[0]

    # 2. Strip comments (% to end of line)
    cleaned = re.sub(r"(?<!\\)%.*$", "", cleaned, flags=re.MULTILINE)

    # 3. Strip environments that are non-prose or code/math/figures
    cleaned = re.sub(
        r"\\begin\{(?:equation|align|gather|multline|tabular|table|figure|lstlisting|verbatim|tikzpicture|array)\*?\}.*?\\end\{(?:equation|align|gather|multline|tabular|table|figure|lstlisting|verbatim|tikzpicture|array)\*?\}",
        " ",
        cleaned,
        flags=re.DOTALL,
    )

    # 4. Strip display & inline math ($...$, $$...$$, \[...\], \(...\))
    cleaned = re.sub(r"\$\$.*?\$\$", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"\\\[.*?\\\]", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"\$.*?\$", " ", cleaned)
    cleaned = re.sub(r"\\\(.*?\\\)", " ", cleaned)

    # 5. Remove citations and refs
    cleaned = re.sub(
        r"\\(?:cite|citep|citet|nocite|ref|eqref|pageref|label)\{[^}]*\}",
        " ",
        cleaned,
    )

    # 6. Unwrap formatting commands (\textbf{text} -> text, etc.)
    for _ in range(3):
        cleaned = re.sub(
            r"\\(?:textbf|textit|textsl|textsc|textsf|texttt|underline|emph)\{([^{}]+)\}",
            r"\1",
            cleaned,
        )

    # 7. Convert headings (\section{...}) into sentence delimiters
    cleaned = re.sub(
        r"\\(?:section|subsection|subsubsection|paragraph|subparagraph)\*?\{([^{}]+)\}",
        r". \1. ",
        cleaned,
    )

    # 8. Strip preamble commands in case \begin{document} was missing
    cleaned = re.sub(
        r"\\(?:documentclass|usepackage|geometry|hypersetup|title|author|date|affiliation|affil|bibliographystyle|bibliography)(?:\[[^\]]*\])?\{[^{}]*\}",
        " ",
        cleaned,
    )

    # 9. Strip standalone formatting commands
    cleaned = re.sub(
        r"\\(?:item|centering|raggedright|raggedleft|noindent|newpage|clearpage|maketitle|tableofcontents|appendix)",
        " ",
        cleaned,
    )

    # 10. Strip any remaining generic LaTeX macros
    cleaned = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*", " ", cleaned)

    # 11. Clean up residual LaTeX syntax characters and normalize whitespace
    cleaned = cleaned.replace("{", " ").replace("}", " ").replace("\\", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class SafeFactChecker:
    """Production in-memory implementation of SAFE Fact-Checking Port."""

    def __init__(
        self,
        min_support_threshold: float = 0.45,
        nli_adapter: ISafeNliPort | None = None,
    ) -> None:
        self.min_support_threshold = min_support_threshold
        self.nli_adapter = nli_adapter

    # --------------------------------------------------------------------------
    # 1. Fact Decomposition (Atomic Claims)
    # --------------------------------------------------------------------------
    def decompose_claims(self, text: str) -> list[str]:
        """Decompose text into atomic factual propositions.

        Splits on sentence boundaries, semicolon, and coordinating conjunctions
        with independent clauses. Filters out trivial or non-factual fragments.
        Strips LaTeX commands, preamble, and math to keep only verifiable prose.
        """
        # If text contains LaTeX markup, sanitize it first
        if "\\" in text or "{" in text or "%" in text:
            cleaned_text = clean_latex_for_fact_checking(text)
        else:
            cleaned_text = text.strip()

        raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", cleaned_text)
        claims: list[str] = []

        for sentence in raw_sentences:
            s_clean = sentence.strip().rstrip(".!?,")
            # Discard short fragments
            if not s_clean or len(s_clean) < 15:
                continue

            # Must contain at least 3 natural language words
            words = re.findall(r"\b[a-zA-Z\u00C0-\u1EF9]{2,}\b", s_clean)
            if len(words) < 3:
                continue

            # Discard any fragments that look like stray code/markup
            if s_clean.startswith("\\") or s_clean.endswith("{") or s_clean.endswith("}"):
                continue

            # Check for multi-clause split (e.g. "..., and ...", "..., whereas ...")
            sub_clauses = re.split(
                r",\s+(?:and|while|whereas|but|yielding|achieving)\s+",
                s_clean,
            )
            if len(sub_clauses) > 1:
                for sub in sub_clauses:
                    sub_strip = sub.strip().rstrip(".!?,")
                    sub_words = re.findall(r"\b[a-zA-Z\u00C0-\u1EF9]{2,}\b", sub_strip)
                    if len(sub_strip) >= 15 and len(sub_words) >= 3:
                        claims.append(sub_strip)
            else:
                claims.append(s_clean)

        return (
            claims
            if claims
            else (
                [cleaned_text.strip()]
                if cleaned_text.strip()
                and len(re.findall(r"\b[a-zA-Z\u00C0-\u1EF9]{2,}\b", cleaned_text)) >= 3
                else []
            )
        )

    # --------------------------------------------------------------------------
    # 2. Entity & Context Normalization
    # --------------------------------------------------------------------------
    def normalize_entities(
        self,
        claim: str,
        context_subject: str | None = None,
    ) -> tuple[str, list[str]]:
        """Normalize vague demonstratives and track extracted named entities."""
        normalized = claim
        resolved_entities: list[str] = []

        # Extract numerical tokens (percentages, metrics, scores)
        num_matches = re.findall(r"\b\d+(?:\.\d+)?%?\b", claim)
        resolved_entities.extend(num_matches)

        # Extract capitalized entities
        cap_matches = re.findall(r"\b[A-Z][a-zA-Z0-9_\-]+\b", claim)
        for cap in cap_matches:
            if cap not in ("The", "This", "It", "We", "They", "Our", "In", "On", "A", "An"):
                resolved_entities.append(cap)

        # Resolve demonstratives if subject context is provided
        if context_subject:
            normalized = re.sub(
                r"\b(this model|this approach|the method|it)\b",
                context_subject,
                normalized,
                flags=re.IGNORECASE,
            )

        return normalized, list(dict.fromkeys(resolved_entities))

    # --------------------------------------------------------------------------
    # 3. Targeted Retrieval & 4. NLI Scoring
    # --------------------------------------------------------------------------
    def _extract_tokens(self, text: str) -> set[str]:
        """Tokenize text into lowercase alphanumeric words, ignoring common stop words."""
        stop_words = {
            "the",
            "a",
            "an",
            "in",
            "on",
            "of",
            "to",
            "for",
            "with",
            "at",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "and",
            "or",
            "that",
            "this",
            "it",
            "as",
            "be",
        }
        words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
        return {w for w in words if w not in stop_words and len(w) > 1}

    def _verify_single_claim(
        self,
        claim_text: str,
        retrieval_context: list[DocumentChunk],
        doc_metadata: dict[UUID, str] | None = None,
    ) -> AtomicClaim:
        """Verify a single atomic proposition against the literature context."""
        normalized_claim, entities = self.normalize_entities(claim_text)
        claim_tokens = self._extract_tokens(normalized_claim)
        claim_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", normalized_claim))

        best_chunk: DocumentChunk | None = None
        best_score = 0.0
        best_overlap_tokens: set[str] = set()

        for chunk in retrieval_context:
            chunk_tokens = self._extract_tokens(chunk.content)
            if not chunk_tokens:
                continue

            intersection = claim_tokens.intersection(chunk_tokens)
            if not intersection:
                continue

            # Coverage of claim terms in chunk (claim recall) and density (precision)
            precision = len(intersection) / len(chunk_tokens)
            recall = len(intersection) / len(claim_tokens) if claim_tokens else 0.0
            entity_matches = sum(1 for e in entities if e.lower() in chunk.content.lower())

            # Asymmetric scoring: a chunk naturally contains many other words,
            # so claim coverage (recall) is the primary determinant of relevance.
            alignment_score = (0.75 * recall + 0.25 * precision) + (0.15 * min(entity_matches, 3))

            if alignment_score > best_score:
                best_score = alignment_score
                best_chunk = chunk
                best_overlap_tokens = intersection

        # NLI Classification
        meta_title = (
            doc_metadata.get(best_chunk.document_id)
            if (best_chunk and doc_metadata and best_chunk.document_id in doc_metadata)
            else None
        )

        if not best_chunk or best_score < self.min_support_threshold:
            return AtomicClaim(
                claim_text=claim_text,
                normalized_entities=entities,
                status=FactVerificationStatus.NOT_ENOUGH_INFO,
                confidence_score=round(best_score, 3),
                evidence_text=None,
                reasoning=(
                    "Không tìm thấy bằng chứng đối chiếu trực tiếp trong kho tài liệu "
                    f"(độ tương đồng: {best_score:.2f} < ngưỡng {self.min_support_threshold:.2f})."
                ),
            )

        chunk_text_lower = best_chunk.content.lower()
        chunk_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", best_chunk.content))

        # Check for numerical contradiction: claim asserts a number not present in matching chunk
        if claim_numbers and not claim_numbers.intersection(chunk_numbers):
            contradictory_context = True
        else:
            contradictory_context = False

        # Check for lexical contradiction pairs
        claim_lower = normalized_claim.lower()
        lexical_contradiction = False
        contradiction_reason = ""
        for word_a, word_b in CONTRADICTION_PAIRS:
            if word_a in claim_lower and word_b in chunk_text_lower:
                lexical_contradiction = True
                contradiction_reason = (
                    f"Mệnh đề khẳng định '{word_a}' nhưng tài liệu nêu '{word_b}'."
                )
                break
            if word_b in claim_lower and word_a in chunk_text_lower:
                lexical_contradiction = True
                contradiction_reason = (
                    f"Mệnh đề khẳng định '{word_b}' nhưng tài liệu nêu '{word_a}'."
                )
                break

        negation_in_claim = (
            "not" in claim_lower or "failed" in claim_lower or "never" in claim_lower
        )
        success_in_chunk = (
            "achieved" in chunk_text_lower
            or "succeeded" in chunk_text_lower
            or "outperformed" in chunk_text_lower
        )
        if negation_in_claim and success_in_chunk:
            lexical_contradiction = True
            contradiction_reason = "Mệnh đề phủ định thành tựu mà tài liệu gốc ghi nhận."

        if contradictory_context or lexical_contradiction:
            reason = contradiction_reason or (
                f"Số liệu trong khẳng định ({list(claim_numbers)}) "
                f"không khớp với tài liệu gốc ({list(chunk_numbers)})."
            )
            return AtomicClaim(
                claim_text=claim_text,
                normalized_entities=entities,
                status=FactVerificationStatus.CONTRADICTED,
                confidence_score=round(min(1.0, best_score + 0.2), 3),
                evidence_text=best_chunk.content[:400],
                evidence_document_id=best_chunk.document_id,
                evidence_document_title=meta_title,
                evidence_page=best_chunk.page_number,
                evidence_bounding_boxes=best_chunk.bounding_boxes,
                reasoning=reason,
            )

        # Confirmed Supported
        confidence = min(1.0, round(best_score + 0.1, 3))
        return AtomicClaim(
            claim_text=claim_text,
            normalized_entities=entities,
            status=FactVerificationStatus.SUPPORTED,
            confidence_score=confidence,
            evidence_text=best_chunk.content[:400],
            evidence_document_id=best_chunk.document_id,
            evidence_document_title=meta_title,
            evidence_page=best_chunk.page_number,
            evidence_bounding_boxes=best_chunk.bounding_boxes,
            reasoning=(
                f"Được chứng minh bởi tài liệu trang {best_chunk.page_number} "
                f"với {len(best_overlap_tokens)} từ khóa then chốt trùng khớp."
            ),
        )

    # --------------------------------------------------------------------------
    # Main Async Verification Pipeline
    # --------------------------------------------------------------------------
    async def verify_text(
        self,
        text: str,
        retrieval_context: list[DocumentChunk],
        doc_metadata: dict[UUID, str] | None = None,
        draft_id: UUID | None = None,
    ) -> FactVerificationReport:
        """Execute parallel 4-stage SAFE fact-checking pipeline."""
        start_time = time.perf_counter()

        raw_claims = self.decompose_claims(text)
        if not raw_claims:
            report = FactVerificationReport(
                draft_id=draft_id,
                verified_text=text,
                claims=[],
                latency_ms=0.0,
            )
            report.compute_summary()
            return report

        if self.nli_adapter is not None:
            # Neural NLI verification route using ISafeNliPort
            chunk_by_id = {c.id: c for c in retrieval_context}

            async def _verify_claim_with_adapter(raw_claim: str) -> AtomicClaim:
                normalized_claim, entities = self.normalize_entities(raw_claim)
                try:
                    assert self.nli_adapter is not None
                    verdict = await self.nli_adapter.classify(normalized_claim, retrieval_context)
                except Exception as err:
                    logger.warning("safe_nli_adapter_failed_fallback_to_heuristic", error=str(err))
                    loop = asyncio.get_running_loop()
                    return await loop.run_in_executor(
                        None,
                        self._verify_single_claim,
                        raw_claim,
                        retrieval_context,
                        doc_metadata,
                    )

                status_map = {
                    "supported": FactVerificationStatus.SUPPORTED,
                    "contradicted": FactVerificationStatus.CONTRADICTED,
                    "not_enough_info": FactVerificationStatus.NOT_ENOUGH_INFO,
                }
                status = status_map.get(verdict.label, FactVerificationStatus.NOT_ENOUGH_INFO)

                ev = verdict.evidence
                chunk_match = chunk_by_id.get(ev.chunk_id) if (ev and ev.chunk_id) else None
                doc_id = chunk_match.document_id if chunk_match else None
                doc_title = (
                    doc_metadata.get(doc_id)
                    if (doc_id and doc_metadata and doc_id in doc_metadata)
                    else None
                )

                if status == FactVerificationStatus.SUPPORTED:
                    confidence = 0.90 if ev else self.min_support_threshold
                elif status == FactVerificationStatus.CONTRADICTED:
                    confidence = 0.90
                else:
                    confidence = 0.0

                return AtomicClaim(
                    claim_text=raw_claim,
                    normalized_entities=entities,
                    status=status,
                    confidence_score=confidence,
                    evidence_text=ev.text if ev else None,
                    evidence_document_id=doc_id,
                    evidence_document_title=doc_title,
                    evidence_page=ev.page if ev else None,
                    evidence_bounding_boxes=list(ev.bounding_boxes) if ev else [],
                    reasoning=verdict.explanation,
                )

            tasks = [_verify_claim_with_adapter(c) for c in raw_claims]
            verified_claims = await asyncio.gather(*tasks)
        else:
            # Async parallel claim verification with heuristic fallback
            loop = asyncio.get_running_loop()
            tasks = [
                loop.run_in_executor(
                    None,
                    self._verify_single_claim,
                    claim,
                    retrieval_context,
                    doc_metadata,
                )
                for claim in raw_claims
            ]
            verified_claims = await asyncio.gather(*tasks)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        report = FactVerificationReport(
            draft_id=draft_id,
            verified_text=text,
            claims=list(verified_claims),
            latency_ms=duration_ms,
        )
        report.compute_summary()
        return report

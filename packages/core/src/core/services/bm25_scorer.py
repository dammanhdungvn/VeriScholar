"""Pure-Python Okapi BM25 lexical relevance scorer.

Adheres strictly to Hexagonal Isolation: uses only Python Standard Library.
"""

from __future__ import annotations

import math
import re
from collections import Counter


class OkapiBM25Scorer:
    """Deterministic Okapi BM25 lexical scorer for scholarly passages."""

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Tokenize input text into lowercase alphanumeric lexical tokens."""
        return re.findall(r"[a-z0-9]+", text.lower())

    def score_corpus(self, query: str, documents: list[str]) -> list[float]:
        """Compute Okapi BM25 scores for each document in the corpus against the query."""
        if not documents:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return [0.0 for _ in documents]

        tokenized_docs = [self.tokenize(doc) for doc in documents]
        n_docs = len(documents)
        doc_lengths = [len(tokens) for tokens in tokenized_docs]
        avgdl = sum(doc_lengths) / n_docs if n_docs > 0 else 0.0
        if avgdl <= 0.0:
            return [0.0 for _ in documents]

        doc_counters = [Counter(tokens) for tokens in tokenized_docs]
        scores = [0.0 for _ in documents]

        for term in query_tokens:
            df = sum(1 for counter in doc_counters if term in counter)
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for idx, counter in enumerate(doc_counters):
                tf = counter.get(term, 0)
                if tf == 0:
                    continue
                dl = doc_lengths[idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (dl / avgdl))
                scores[idx] += idf * (numerator / denominator)

        return scores

    def rank_documents(self, query: str, documents: list[str]) -> list[tuple[int, float]]:
        """Rank documents by descending Okapi BM25 score as (doc_index, score) tuples."""
        scores = self.score_corpus(query, documents)
        return sorted(enumerate(scores), key=lambda item: (-item[1], item[0]))

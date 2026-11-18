
import math
import re
from collections import Counter

from .models import Chunk


def tokenize(text: str) -> list[str]:
    """Convert text into searchable lowercase tokens."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", text)

    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return tokens


class BM25:
    def __init__(
        self,
        chunks: list[Chunk] | list[str],
        k1: float = 1.5,
        b: float = 0.75
    ) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b

        self.N = len(chunks)
        self.doc_lengths: list[int] = []
        self.term_frequencies: list[dict[str, int]] = []
        self.inverted_index: dict[str, dict[int, int]] = {}

        # Build document statistics
        for doc_id, chunk in enumerate(chunks):
            if isinstance(chunk, Chunk):
                text = chunk.text
            else:
                text = chunk

            tokens = tokenize(text)

            # Document length
            self.doc_lengths.append(len(tokens))

            # Term frequencies
            frequencies = Counter(tokens)
            self.term_frequencies.append(dict(frequencies))

            # Inverted index
            for term, frequency in frequencies.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}

                self.inverted_index[term][doc_id] = frequency

        # Average document length
        if self.N > 0:
            self.avgdl = sum(self.doc_lengths) / self.N
        else:
            self.avgdl = 0.0

    def _idf(self, term: str) -> float:
        """Calculate inverse document frequency."""
        containing_docs = len(self.inverted_index.get(term, {}))

        return math.log(
            1 + (self.N - containing_docs + 0.5)
            / (containing_docs + 0.5)
        )

    def _score(self, term: str, doc_id: int) -> float:
        """Calculate BM25 score for one term in one document."""
        frequency = self.inverted_index[term][doc_id]
        doc_length = self.doc_lengths[doc_id]

        numerator = frequency * (self.k1 + 1)

        denominator = frequency + self.k1 * (
            1 - self.b + self.b * doc_length / self.avgdl
        )

        return self._idf(term) * numerator / denominator

    def search(
        self,
        query: str,
        k: int
    ) -> list[tuple[int, float]]:
        """Return the top-k documents ranked by BM25 score."""
        if k <= 0 or self.N == 0 or self.avgdl == 0:
            return []

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        scores: dict[int, float] = {}

        for term in query_tokens:
            matching_docs = self.inverted_index.get(term, {})

            for doc_id in matching_docs:
                score = self._score(term, doc_id)

                scores[doc_id] = scores.get(doc_id, 0.0) + score

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return ranked[:k]

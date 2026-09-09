import re

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    Lexical retriever using the BM25 ranking algorithm.

    BM25 is useful for exact technical terms such as:
    - HTTP status codes
    - service names
    - error codes
    - policy terms
    - configuration names
    """

    def __init__(self, chunks: list[dict], top_k: int = 5):
        if not chunks:
            raise ValueError("Chunks cannot be empty")

        self.chunks = chunks
        self.top_k = top_k

        tokenized_corpus = [
            self._tokenize(chunk.get("content", ""))
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str) -> list[dict]:
        """
        Search the indexed chunks using BM25.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        ranked_results = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        for index, score in ranked_results[: self.top_k]:
            if score <= 0:
                continue

            result = {
                **self.chunks[index],
                "score": float(score),
            }

            results.append(result)

        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """
        Convert text into lowercase word/token terms.

        Example:
            "HTTP 503 Payment API"
            ->
            ["http", "503", "payment", "api"]
        """

        return re.findall(r"\b\w+\b", text.lower())
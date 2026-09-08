class RelevanceFilter:
    """
    Filters retrieved knowledge-base chunks based on
    their semantic similarity score.

    Only sufficiently relevant chunks are allowed
    to reach the LLM.
    """

    def __init__(self, threshold: float = 0.35):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0.0 and 1.0"
            )

        self.threshold = threshold

    def filter(
        self,
        results: list[dict],
    ) -> list[dict]:
        """
        Return only results whose relevance score
        meets or exceeds the configured threshold.
        """

        return [
            result
            for result in results
            if result["score"] >= self.threshold
        ]

    def has_relevant_results(
        self,
        results: list[dict],
    ) -> bool:
        """
        Determine whether at least one sufficiently
        relevant result exists.
        """

        return any(
            result["score"] >= self.threshold
            for result in results
        )
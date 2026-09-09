class RRFFusion:
    """
    Reciprocal Rank Fusion (RRF) for combining ranked retrieval results.

    RRF combines rankings from different retrieval systems without
    requiring their scores to be on the same scale.
    """

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        result_lists: list[list[dict]],
        top_k: int = 20,
    ) -> list[dict]:
        """
        Combine multiple ranked result lists using RRF.

        Each result must contain a unique 'chunk_id'.
        """

        fused_scores: dict[str, float] = {}
        result_by_chunk_id: dict[str, dict] = {}

        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                chunk_id = result["chunk_id"]

                rrf_score = 1 / (self.k + rank)

                fused_scores[chunk_id] = (
                    fused_scores.get(chunk_id, 0.0)
                    + rrf_score
                )

                if chunk_id not in result_by_chunk_id:
                    result_by_chunk_id[chunk_id] = result.copy()
                else:
                    existing = result_by_chunk_id[chunk_id]

                    # Preserve the dense semantic score when
                    # the same chunk is also returned by BM25.
                    if "score" not in existing and "score" in result:
                        existing["score"] = result["score"]

        ranked_chunk_ids = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )

        fused_results = []

        for chunk_id in ranked_chunk_ids[:top_k]:
            result = {
                **result_by_chunk_id[chunk_id],
                "rrf_score": fused_scores[chunk_id],
            }

            fused_results.append(result)

        return fused_results
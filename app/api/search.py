from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.ingestion import KnowledgeBaseIngestion
from app.rag.retriever import Retriever


router = APIRouter(
    prefix="/api/v1",
    tags=["RAG Search"],
)


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language question",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve",
    )


class SearchResult(BaseModel):
    score: float
    chunk_id: str
    source: str
    content: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    """
    Retrieve semantically relevant knowledge-base chunks.
    """

    try:
        retriever = Retriever(
            collection_name="enterprise_operations"
        )

        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
        )

        return SearchResponse(
            query=request.query,
            results=results,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {exc}",
        ) from exc
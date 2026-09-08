from fastapi import FastAPI

from app.api.search import router as search_router


app = FastAPI(
    title="Enterprise AI Operations Copilot",
    description="Production-oriented GenAI reference application",
    version="0.1.0",
)


app.include_router(search_router)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "enterprise-ai-operations-copilot",
    }


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Operations Copilot",
        "version": "0.1.0",
    }
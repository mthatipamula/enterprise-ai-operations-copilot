from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from pydantic import BaseModel, Field

from app.agents.operations_agent import OperationsAgent


router = APIRouter(
    prefix="/api/v1/agent",
    tags=["Agent"],
)


# Keep one agent instance so in-memory conversation
# sessions survive across requests.
agent = OperationsAgent()


class AgentRequest(BaseModel):
    session_id: str = Field(
        default="default",
        min_length=1,
        description="Conversation/session identifier",
    )
    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language user question",
    )


@router.post("/chat")
def chat(
    request: AgentRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a request through the Operations Agent.

    The agent can:
    - route knowledge questions to RAG
    - route operational questions to tools
    - maintain conversation state by session_id
    """
    try:
        return agent.run(
            query=request.query,
            session_id=request.session_id,
            user_context=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}",
        ) from exc
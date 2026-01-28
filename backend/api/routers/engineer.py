from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from backend.agents.engineer_agent import engineer_agent, AgentResponse

router = APIRouter()

class EngineerRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=AgentResponse)
async def chat_with_engineer(request: EngineerRequest):
    """
    Chat with the Autonomous Engineer Agent.
    """
    try:
        response = await engineer_agent.process(
            message=request.message,
            context=request.context or {}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

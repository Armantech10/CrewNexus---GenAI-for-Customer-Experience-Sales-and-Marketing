from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.api.dependencies import get_current_user
from backend.agents.orchestrator import UnifiedOrchestrator
from backend.agents.models import UserContext, FinalResponse

router = APIRouter()
orchestrator = UnifiedOrchestrator()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None
    stream: bool = False

@router.post("/chat", response_model=FinalResponse)
async def chat_endpoint(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    user: Optional[dict] = Depends(get_current_user)
):
    try:
        # Build context
        context = UserContext(
            user_id=request.user_id or "anonymous",
            session_id=request.session_id,
            name=user.get("name") if user else None,
            email=user.get("email") if user else None
        )
        
        # Process message
        response = await orchestrator.process_message(request.message, context)
        
        # TODO: Add background tasks (analytics, memory update)
        # background_tasks.add_task(save_analytics, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

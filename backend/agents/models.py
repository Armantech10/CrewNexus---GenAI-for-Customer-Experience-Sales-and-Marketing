from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
from backend.services.intent_detector import Intent, IntentAnalysis
from backend.services.sentiment_analyzer import Sentiment, SentimentAnalysis

class Action(str, Enum):
    SELL = "sell"
    UPSELL = "upsell"
    SUPPORT = "support"
    NURTURE = "nurture"
    RETAIN = "retain"
    QUALIFY = "qualify"
    ESCALATE = "escalate"
    MARKET = "market"
    WAIT = "wait"

class AgentType(str, Enum):
    SALES = "sales_agent"
    SUPPORT = "support_agent"
    MARKETING = "marketing_crew"
    RETENTION = "retention_agent"
    NONE = "none"

class UserContext(BaseModel):
    user_id: str
    session_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    customer_tier: str = "standard"  # standard, premium, enterprise
    ltv: float = 0.0
    churn_risk: float = 0.0
    purchase_history: List[Dict] = []
    active_campaigns: List[str] = []

class DecisionResult(BaseModel):
    action: Action
    agent_type: AgentType
    priority: int
    reasoning: str
    suggested_response: Optional[str] = None

class FinalResponse(BaseModel):
    response: str
    intent: Intent
    sentiment: Sentiment
    action_taken: Action
    agent_used: AgentType
    confidence: float
    analytics_id: Optional[str] = None

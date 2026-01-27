from typing import Optional
from backend.agents.models import FinalResponse, UserContext
from backend.services.intent_detector import IntentDetector
from backend.services.sentiment_analyzer import SentimentAnalyzer
from backend.agents.decision_engine import DecisionEngine
from backend.agents.base_agent import BaseAgent
from backend.agents.sales_agent import SalesAgent
from backend.agents.marketing_crew import MarketingCrewWrapper
from backend.agents.support_agent import SupportAgent

class UnifiedOrchestrator:
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.decision_engine = DecisionEngine()
        
        # Initialize agents
        self.sales_agent = SalesAgent()
        self.marketing_crew = MarketingCrewWrapper()
        self.support_agent = SupportAgent()
        
        self.active_agents = {
            "sales_agent": self.sales_agent,
            "marketing_crew": self.marketing_crew,
            "support_agent": self.support_agent
        } 

    async def process_message(self, message: str, user_context: UserContext) -> FinalResponse:
        # 1. Analyze input (Parallelize these in production)
        intent_analysis = await self.intent_detector.detect(message)
        sentiment_analysis = await self.sentiment_analyzer.analyze(message)
        
        # 2. Make decision
        decision = await self.decision_engine.decide(
            intent_analysis,
            sentiment_analysis,
            user_context
        )
        
        # Route based on keywords
        if "market" in message.lower() or "campaign" in message.lower() or "post" in message.lower():
            decision.agent_type = "marketing_crew"
            decision.action = "market"
            agent = self.marketing_crew
        elif "help" in message.lower() or "support" in message.lower() or "issue" in message.lower():
            decision.agent_type = "support_agent"
            decision.action = "support"
            agent = self.support_agent
        else:
            # Default to sales
            agent = self.sales_agent
            decision.agent_type = "sales_agent"

        agent_result = await agent.process(message, user_context.dict())
        
        # 4. Construct final response
        return FinalResponse(
            response=agent_result.response,
            intent=intent_analysis.intent,
            sentiment=sentiment_analysis.sentiment,
            action_taken=decision.action,
            agent_used=decision.agent_type,
            confidence=decision.priority / 10.0
        )

from backend.agents.models import DecisionResult, UserContext
from backend.services.intent_detector import IntentAnalysis
from backend.services.sentiment_analyzer import SentimentAnalysis
from backend.agents.business_rules import BusinessRulesEngine

class DecisionEngine:
    def __init__(self):
        self.rules_engine = BusinessRulesEngine()
        
    async def decide(self, 
               intent_analysis: IntentAnalysis, 
               sentiment_analysis: SentimentAnalysis, 
               context: UserContext) -> DecisionResult:
        
        # 1. Evaluate explicit business rules
        rule_result = self.rules_engine.evaluate(
            intent_analysis.intent, 
            sentiment_analysis.sentiment, 
            context
        )
        
        if rule_result:
            return rule_result
            
        # 2. (Optional) LLM-based fallback decision if no rules match
        # For now, return what the business rules engine returned (which has a default)
        return self.rules_engine.evaluate(intent_analysis.intent, sentiment_analysis.sentiment, context)

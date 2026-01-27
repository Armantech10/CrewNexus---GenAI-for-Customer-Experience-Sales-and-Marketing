from abc import ABC, abstractmethod
from typing import List, Optional
from backend.agents.models import DecisionResult, Action, AgentType, UserContext
from backend.services.intent_detector import Intent
from backend.services.sentiment_analyzer import Sentiment

class Rule(ABC):
    @abstractmethod
    def evaluate(self, intent: Intent, sentiment: Sentiment, context: UserContext) -> Optional[DecisionResult]:
        pass

class CriticalSupportRule(Rule):
    def evaluate(self, intent: Intent, sentiment: Sentiment, context: UserContext) -> Optional[DecisionResult]:
        if sentiment == Sentiment.NEGATIVE or intent == Intent.COMPLAINT:
            return DecisionResult(
                action=Action.ESCALATE,
                agent_type=AgentType.SUPPORT,
                priority=10,
                reasoning="Negative sentiment or complaint detected, immediate support needed."
            )
        return None

class PurchaseIntentRule(Rule):
    def evaluate(self, intent: Intent, sentiment: Sentiment, context: UserContext) -> Optional[DecisionResult]:
        if intent == Intent.PURCHASE:
            return DecisionResult(
                action=Action.SELL,
                agent_type=AgentType.SALES,
                priority=8,
                reasoning="User expressed purchase intent."
            )
        return None

# TODO: Add more rules (ChurnPrevention, HighValueCustomer, UpsellOpportunity)

class BusinessRulesEngine:
    def __init__(self):
        self.rules: List[Rule] = [
            CriticalSupportRule(),
            PurchaseIntentRule(),
            # Add other rules here in priority order
        ]

    def evaluate(self, intent: Intent, sentiment: Sentiment, context: UserContext) -> Optional[DecisionResult]:
        for rule in self.rules:
            result = rule.evaluate(intent, sentiment, context)
            if result:
                return result
        # Default fallback
        return DecisionResult(
            action=Action.WAIT,
            agent_type=AgentType.SALES, # Default to Sales/General agent
            priority=0,
            reasoning="No specific rule matched, defaulting to general handling."
        )

from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.services.intent_detector import Intent
from backend.services.llm_service import llm_service
import random

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SalesAgent")
        # Stages: Introduction -> Qualification -> Value Prop -> Closing
        self.products = [
            {"name": "GenAI Enterprise Suite", "price": "$999/mo", "features": ["All agents", "Unlimited queries"]},
            {"name": "Starter Pack", "price": "$299/mo", "features": ["Sales agent only"]}
        ]

    async def initialize_tools(self):
        pass

    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        # Simple rule-based logic for specific triggers
        msg_lower = message.lower()
        response_text = ""
        
        if "price" in msg_lower or "cost" in msg_lower:
            response_text = "Our Enterprise Suite starts at $999/mo, which includes all agents. We also have a Starter Pack for $299/mo. which would you be interested in?"
        elif "features" in msg_lower or "do" in msg_lower:
            response_text = "We offer a unified platform with Sales, Support, and Marketing agents. Our AI can handle customer inquiries, manage campaigns, and close deals automatically."
        elif "buy" in msg_lower or "sign up" in msg_lower:
            response_text = "Great! I can send you a secure payment link via Stripe. Shall I proceed?"
        else:
            # Connect to LLM (Gemini/OpenAI) for intelligent conversation
            system_prompt = """You are an expert AI Sales Representative for 'CrewNexus'. 
            Your goal is to sell our GenAI Platform (Enterprise: $999/mo, Starter: $299/mo).
            Be helpful, professional, and concise. Do not make up features.
            Context: We help businesses automate Sales, Marketing, and Support."""
            
            try:
                llm_response = await llm_service.generate(
                    prompt=message,
                    system_prompt=system_prompt,
                    temperature=0.7
                )
                response_text = llm_response.content
            except Exception as e:
                response_text = "I'm having trouble connecting to my brain right now. Please ask about 'price' or 'features'."
                print(f"LLM Error: {e}")

        return AgentResponse(
            response=response_text,
            metadata={
                "stage": "qualification",
                "product_interest": "general"
            }
        )

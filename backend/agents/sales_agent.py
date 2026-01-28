from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.services.intent_detector import Intent
from backend.services.llm_service import llm_service
import random

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SalesAgent")
        self.products = [
            {"name": "GenAI Enterprise Suite", "price": "$999/mo", "features": ["All agents", "Unlimited queries", "Priority support", "Custom integrations"]},
            {"name": "Starter Pack", "price": "$299/mo", "features": ["Sales agent only", "5000 queries/mo"]}
        ]
        
        # Smart responses for common questions (saves API quota)
        self.smart_responses = {
            # Pricing
            ("price", "cost", "pricing", "how much", "expensive", "cheap", "afford"): 
                "Great question! Our Enterprise Suite is $999/mo (all agents, unlimited queries, priority support). "
                "For smaller teams, the Starter Pack is just $299/mo with Sales agent and 5000 queries. "
                "Which sounds like a better fit for your needs?",
            
            # Features & Capabilities
            ("feature", "what can", "capability", "able to", "function"): 
                "CrewNexus offers powerful AI agents:\n"
                "• **Sales Agent** - Lead qualification, follow-ups, deal closing\n"
                "• **Support Agent** - 24/7 customer support with knowledge base\n"
                "• **Marketing Agent** - Campaign creation, social media, content\n"
                "All powered by cutting-edge AI. What area interests you most?",
            
            # About CrewNexus
            ("about", "what is crewnexus", "tell me about", "who are you", "your company", "introduce"):
                "I'm CrewNexus, your AI-powered business automation platform! 🚀\n\n"
                "We help companies automate Sales, Marketing, and Customer Support using intelligent AI agents. "
                "Our platform reduces manual work by 70% and increases conversion rates. "
                "Would you like to see how we can help your specific business?",
            
            # Comparison & Competition
            ("competitor", "vs", "compare", "better than", "difference", "why choose", "why should"):
                "What sets CrewNexus apart:\n"
                "✅ **Unified Platform** - Sales, Support & Marketing in one place\n"
                "✅ **No Code Required** - Set up in minutes, not weeks\n"
                "✅ **AI-Powered** - Uses GPT-4 & Gemini for intelligent responses\n"
                "✅ **Affordable** - Starting at just $299/mo (competitors charge $1000+)\n"
                "Would you like a personalized demo to see the difference?",
            
            # Demo & Trial
            ("demo", "trial", "try", "test", "sample", "free"):
                "Absolutely! We offer a **14-day free trial** with full access to all features. "
                "No credit card required. I can set that up for you right now. "
                "What's the best email to send the trial invite to?",
            
            # Getting Started & Buying
            ("buy", "purchase", "sign up", "start", "get started", "subscribe", "order"):
                "Excellent choice! 🎉 Here's how to get started:\n"
                "1. Choose your plan (Starter $299/mo or Enterprise $999/mo)\n"
                "2. I'll send you a secure Stripe payment link\n"
                "3. Get instant access to your AI agents\n\n"
                "Which plan would you like to proceed with?",
            
            # Support & Help
            ("support", "help", "issue", "problem", "contact", "assistance"):
                "I'm here to help! For technical support, we offer:\n"
                "• 24/7 AI support (that's me!)\n"
                "• Email: support@crewnexus.ai\n"
                "• Enterprise: Dedicated account manager\n"
                "What specific question can I help you with today?",
            
            # Integration
            ("integrat", "connect", "api", "zapier", "webhook", "crm", "salesforce", "hubspot"):
                "CrewNexus integrates seamlessly with your existing tools:\n"
                "• **CRMs**: Salesforce, HubSpot, Pipedrive\n"
                "• **Communication**: Slack, Teams, Email\n"
                "• **Payments**: Stripe, PayPal\n"
                "• **Custom**: REST API & Webhooks\n"
                "Which integration is most important for your workflow?",
            
            # Greeting
            ("hello", "hi ", "hey", "good morning", "good afternoon", "good evening"):
                "Hello! 👋 Welcome to CrewNexus! I'm your AI Sales Assistant. "
                "I can help you learn about our platform, pricing, or schedule a demo. "
                "What brings you here today?",
        }

    async def initialize_tools(self):
        pass

    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        msg_lower = message.lower()
        response_text = ""
        
        # Check smart responses first (saves API quota)
        for keywords, response in self.smart_responses.items():
            if any(keyword in msg_lower for keyword in keywords):
                response_text = response
                break
        
        # If no keyword match, try LLM with graceful fallback
        if not response_text:
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
                # Graceful fallback with helpful message
                print(f"LLM Error: {e}")
                response_text = (
                    "I'd love to tell you more! Here's what I can help with:\n\n"
                    "💰 **Pricing** - Ask about our plans ($299-$999/mo)\n"
                    "✨ **Features** - Learn what our AI agents can do\n"
                    "🎯 **Demo** - Try our 14-day free trial\n"
                    "🔗 **Integrations** - Connect with your existing tools\n\n"
                    "Just type your question or pick a topic above!"
                )

        return AgentResponse(
            response=response_text,
            metadata={
                "stage": "qualification",
                "product_interest": "general"
            }
        )

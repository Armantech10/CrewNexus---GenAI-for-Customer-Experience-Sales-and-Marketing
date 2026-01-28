from typing import Any, Dict
from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.services.rag_service import RAGService
from backend.services.llm_service import llm_service

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SupportGenie")
        self.rag_service = RAGService()
        
        # Smart responses for common triggers (saves API quota)
        self.smart_responses = {
            ("hello", "hi ", "hey", "good morning"): 
                "Hello! 👋 I'm SupportGenie. I can help you with technical issues, account management, or billing questions. How can I assist you?",
                
            ("reset password", "forgot password", "change password"):
                "To reset your password:\n1. Go to Settings > Security\n2. Click 'Change Password'\n3. Follow the email instructions.\n\nNeed a direct link?",
                
            ("billing", "invoice", "receipt", "payment method"):
                "You can manage all billing details in the 'Billing' tab of your dashboard. You can view invoices, update payment methods, or upgrade your plan there.",
                
            ("contact", "human", "person", "agent", "support email"):
                "You can reach our human support team at support@crewnexus.ai. For urgent issues, please call our 24/7 hotline at +1-800-CREW-HELP."
        }

    async def initialize_tools(self):
        # Allow pre-loading some knowledge base items
        pass

    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        msg_lower = message.lower()
        
        # 1. Check smart responses first
        for keywords, response in self.smart_responses.items():
            if any(keyword in msg_lower for keyword in keywords):
                return AgentResponse(
                    response=response, 
                    metadata={"source": "smart_response"}
                )

        # 2. Retrieve relevant info from Knowledge Base (RAG)
        docs = await self.rag_service.retrieve(message)
        context_text = "\n".join([f"- {d['content']}" for d in docs]) if docs else "No specific documentation found."
        
        # 3. Generate Intelligent Response using Gemini
        system_prompt = f"""You are 'SupportGenie', an expert customer support AI for CrewNexus.
        Use the following Knowledge Base context to answer the user's question.
        
        KNOWLEDGE BASE:
        {context_text}
        
        Guidelines:
        - Be polite, concise, and helpful.
        - If the answer is in the Knowledge Base, explain it clearly.
        - If the answer is NOT in the Knowledge Base, strictly say: "I don't have that information right now, but you can contact support@crewnexus.ai"."
        - Do not make up information."""

        try:
            llm_response = await llm_service.generate(
                prompt=message,
                system_prompt=system_prompt,
                temperature=0.3 # Lower temperature for factual support
            )
            response_text = llm_response.content
        except Exception as e:
            print(f"Support LLM Error: {e}")
            response_text = "I'm having trouble accessing my knowledge base directly. Please try asking again or contact human support."

        return AgentResponse(
            response=response_text,
            metadata={
                "source": "RAG + Gemini",
                "docs_found": len(docs)
            }
        )

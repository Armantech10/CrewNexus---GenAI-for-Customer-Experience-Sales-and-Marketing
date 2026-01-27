from typing import Any, Dict
from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.services.rag_service import RAGService

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SupportGenie")
        self.rag_service = RAGService()

    async def initialize_tools(self):
        # Allow pre-loading some knowledge base items
        pass

    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        # 1. Retrieve relevant info
        docs = await self.rag_service.retrieve(message)
        
        # 2. Formulate response (Simulated LLM Generation)
        if docs:
            context_text = "\n".join([f"- {d['content']}" for d in docs])
            response = f"Based on our knowledge base:\n{context_text}\n\nIs there anything else I can help with?"
        else:
            response = "I couldn't find specific information in my knowledge base. Let me escalate this to a human specialist."
            
        return AgentResponse(
            response=response,
            metadata={
                "source": "RAG",
                "docs_found": len(docs)
            }
        )

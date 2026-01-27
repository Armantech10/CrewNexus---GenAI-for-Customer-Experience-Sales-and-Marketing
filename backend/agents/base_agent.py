from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AgentResponse(BaseModel):
    response: str
    metadata: Dict[str, Any] = {}
    sources: List[str] = []

class BaseAgent(ABC):
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Process a user message and return a response.
        """
        pass
        
    @abstractmethod
    async def initialize_tools(self):
        """
        Initialize any tools or external services required by the agent.
        """
        pass
    
    async def remember(self, key: str, value: Any):
        """
        Store information in the agent's memory.
        """
        # Placeholder for memory integration
        pass
        
    async def recall(self, key: str) -> Any:
        """
        Retrieve information from the agent's memory.
        """
        # Placeholder for memory integration
        return None

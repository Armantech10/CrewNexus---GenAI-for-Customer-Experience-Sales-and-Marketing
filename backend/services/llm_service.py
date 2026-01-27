"""
LLM Service - Multi-provider LLM integration with fallback support.

Supports:
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude Sonnet, Claude Opus)
- Mock responses for testing without API keys
"""
import os
from typing import Optional, AsyncIterator
from enum import Enum
from pydantic import BaseModel
from backend.config.settings import settings

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class LLMResponse(BaseModel):
    content: str
    tokens_used: int
    provider: str
    model: str


class LLMService:
    """Multi-provider LLM service with automatic fallback."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients based on API keys."""
        if settings.OPENAI_API_KEY and AsyncOpenAI:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY and anthropic:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
    
    @property
    def available_provider(self) -> LLMProvider:
        """Get the best available provider."""
        if self.openai_client:
            return LLMProvider.OPENAI
        elif self.anthropic_client:
            return LLMProvider.ANTHROPIC
        return LLMProvider.MOCK
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        provider: Optional[LLMProvider] = None
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User message/prompt
            system_prompt: Optional system instructions
            model: Specific model to use (defaults based on provider)
            max_tokens: Maximum response tokens
            temperature: Creativity (0-1)
            provider: Force a specific provider
        
        Returns:
            LLMResponse with content and metadata
        """
        provider = provider or self.available_provider
        
        if provider == LLMProvider.OPENAI:
            return await self._generate_openai(
                prompt, system_prompt, model or "gpt-4o-mini", max_tokens, temperature
            )
        elif provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(
                prompt, system_prompt, model or "claude-sonnet-4-20250514", max_tokens, temperature
            )
        else:
            return await self._generate_mock(prompt, system_prompt)
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """Generate using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens,
            provider="openai",
            model=model
        )
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """Generate using Anthropic Claude."""
        message = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return LLMResponse(
            content=message.content[0].text,
            tokens_used=message.usage.input_tokens + message.usage.output_tokens,
            provider="anthropic",
            model=model
        )
    
    async def _generate_mock(
        self,
        prompt: str,
        system_prompt: Optional[str]
    ) -> LLMResponse:
        """Generate mock response for testing without API keys."""
        prompt_lower = prompt.lower()
        
        # Generate contextual mock responses
        if any(word in prompt_lower for word in ["buy", "purchase", "price", "product"]):
            content = "I'd be happy to help you with your purchase! We have several great products available. Could you tell me more about what you're looking for? I can provide pricing details and help you find the perfect solution."
        elif any(word in prompt_lower for word in ["campaign", "marketing", "post", "social"]):
            content = "I can help you create an engaging marketing campaign! Let me suggest a strategy: First, we'll identify your target audience, then craft compelling content, and schedule posts for optimal engagement. What platform would you like to focus on?"
        elif any(word in prompt_lower for word in ["help", "support", "issue", "problem"]):
            content = "I understand you need assistance. I'm here to help! Could you describe the issue you're experiencing in more detail? I'll do my best to resolve it quickly."
        else:
            content = "Thank you for your message. I'm your AI assistant ready to help with sales, marketing, or customer support. How can I assist you today?"
        
        return LLMResponse(
            content=content,
            tokens_used=len(prompt.split()) + len(content.split()),  # Rough estimate
            provider="mock",
            model="mock-v1"
        )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream a response from OpenAI (streaming only supported for OpenAI).
        
        Yields chunks of the response as they're generated.
        """
        if self.available_provider != LLMProvider.OPENAI:
            # Fallback to regular generation for non-OpenAI
            response = await self.generate(prompt, system_prompt, model, max_tokens, temperature)
            yield response.content
            return
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.openai_client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
llm_service = LLMService()

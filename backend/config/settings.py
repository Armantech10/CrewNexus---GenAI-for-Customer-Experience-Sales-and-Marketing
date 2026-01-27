from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Unified GenAI Platform"
    DEBUG: bool = True
    
    # API
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # LLM
    OPENAI_API_KEY: Optional[str] = None  # Made optional to allow startup without key
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Database
    REDIS_URL: str = "redis://localhost:6379"
    QDRANT_URL: str = "http://localhost:6333"
    POSTGRES_URL: Optional[str] = None
    
    # Integrations
    STRIPE_SECRET_KEY: Optional[str] = None
    EXA_API_KEY: Optional[str] = None

    # Performance & Security
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour default
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()

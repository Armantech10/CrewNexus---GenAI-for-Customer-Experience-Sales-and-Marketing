import json
from typing import Optional, Dict, List
import redis.asyncio as redis
from backend.config.settings import settings

class MemoryService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = 60 * 60 * 24 * 7  # 7 days

    async def add_message(self, session_id: str, message: Dict):
        """Add a message to the conversation history."""
        key = f"chat:{session_id}"
        await self.redis.rpush(key, json.dumps(message))
        await self.redis.expire(key, self.default_ttl)

    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve conversation history."""
        key = f"chat:{session_id}"
        messages = await self.redis.lrange(key, -limit, -1)
        return [json.loads(m) for m in messages]

    async def clear_history(self, session_id: str):
        """Clear conversation history."""
        key = f"chat:{session_id}"
        await self.redis.delete(key)

    async def set_context(self, user_id: str, context: Dict):
        """Set user context/profile data."""
        key = f"user:{user_id}"
        await self.redis.set(key, json.dumps(context))

    async def get_context(self, user_id: str) -> Optional[Dict]:
        """Get user context/profile data."""
        key = f"user:{user_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

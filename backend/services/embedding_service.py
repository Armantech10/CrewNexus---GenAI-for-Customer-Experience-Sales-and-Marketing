from typing import List
# import openai
from sentence_transformers import SentenceTransformer
from backend.config.settings import settings

class EmbeddingService:
    def __init__(self, mode="local"):
        self.mode = mode
        if self.mode == "local":
            # Lightweight local model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None # Setup OpenAI client

    async def embed_query(self, text: str) -> List[float]:
        if self.mode == "local":
            return self.model.encode(text).tolist()
        # else: call openai
        return []

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.mode == "local":
            return self.model.encode(texts).tolist()
        return []

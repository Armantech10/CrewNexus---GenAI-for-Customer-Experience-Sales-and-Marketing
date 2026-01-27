from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.services.embedding_service import EmbeddingService
from backend.config.settings import settings
import uuid

class RAGService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "knowledge_base"
        self.embedding_service = EmbeddingService()
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    async def ingest_document(self, content: str, metadata: Dict[str, Any]):
        vector = await self.embedding_service.embed_query(content)
        doc_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"content": content, **metadata}
                )
            ]
        )
        return doc_id

    async def retrieve(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        vector = await self.embedding_service.embed_query(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )
        
        return [
            {
                "content": hit.payload.get("content"),
                "score": hit.score,
                "metadata": {k:v for k,v in hit.payload.items() if k != "content"}
            }
            for hit in results
        ]

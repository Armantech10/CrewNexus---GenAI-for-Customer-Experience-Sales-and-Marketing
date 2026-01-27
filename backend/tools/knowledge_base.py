"""
Knowledge Base Tool - Product and service information retrieval.

Uses RAG service to retrieve relevant information for agent responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    features: List[str]
    in_stock: bool = True


# Mock product catalog (in production, this would be in a vector DB)
_products: Dict[str, Product] = {
    "prod_001": Product(
        id="prod_001",
        name="GenAI Starter Pack",
        description="Perfect for small businesses starting their AI journey. Includes basic chat agent and analytics.",
        price=99.0,
        category="starter",
        features=["1 AI Agent", "5000 messages/month", "Basic analytics", "Email support"]
    ),
    "prod_002": Product(
        id="prod_002",
        name="GenAI Professional",
        description="For growing teams that need more power. Multi-agent system with CRM integration.",
        price=299.0,
        category="professional",
        features=["3 AI Agents", "50000 messages/month", "Advanced analytics", "CRM integration", "Priority support"]
    ),
    "prod_003": Product(
        id="prod_003",
        name="GenAI Enterprise",
        description="Full-featured enterprise solution with unlimited agents and custom integrations.",
        price=999.0,
        category="enterprise",
        features=["Unlimited Agents", "Unlimited messages", "Custom integrations", "Dedicated support", "SLA guarantee", "On-premise option"]
    )
}


class KnowledgeBaseTool:
    """Product and service knowledge retrieval tool."""
    
    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Product]:
        """
        Search products based on query.
        
        In production, this would use the RAG service with vector search.
        """
        results = []
        query_lower = query.lower()
        
        for product in _products.values():
            # Simple keyword matching (replace with vector search in production)
            score = 0
            if query_lower in product.name.lower():
                score += 3
            if query_lower in product.description.lower():
                score += 2
            for feature in product.features:
                if query_lower in feature.lower():
                    score += 1
            
            if score > 0 or not query:
                results.append((score, product))
        
        # Filter by category if specified
        if category:
            results = [(s, p) for s, p in results if p.category == category]
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results[:max_results]]
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return _products.get(product_id)
    
    async def get_product_recommendations(
        self,
        user_context: Dict[str, Any]
    ) -> List[Product]:
        """Get product recommendations based on user context."""
        customer_value = user_context.get("customer_value", "unknown")
        
        if customer_value == "high" or "enterprise" in user_context.get("tags", []):
            # Recommend enterprise
            return [p for p in _products.values() if p.category == "enterprise"]
        elif customer_value == "medium":
            # Recommend professional
            return [p for p in _products.values() if p.category == "professional"]
        else:
            # Recommend based on price, starter first
            return sorted(_products.values(), key=lambda p: p.price)
    
    async def get_pricing_info(self) -> Dict[str, Any]:
        """Get pricing information summary."""
        return {
            "plans": [
                {
                    "name": product.name,
                    "price": f"${product.price}/month",
                    "features": product.features[:3],
                    "category": product.category
                }
                for product in sorted(_products.values(), key=lambda p: p.price)
            ],
            "currency": "USD",
            "billing": "monthly",
            "enterprise_contact": "sales@example.com"
        }


# Singleton instance
knowledge_base = KnowledgeBaseTool()

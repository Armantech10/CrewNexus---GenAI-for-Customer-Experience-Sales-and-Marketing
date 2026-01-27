"""
Exa Web Search Tool
Provides semantic web search capabilities using Exa AI.
Falls back to mock mode when EXA_API_KEY is not set.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

# Try to import Exa
try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False

from backend.config.settings import settings


class SearchResult(BaseModel):
    """Search result model"""
    id: str
    url: str
    title: str
    score: float
    published_date: Optional[str] = None
    author: Optional[str] = None
    text: Optional[str] = None  # Only if contents requested
    highlights: List[str] = []


class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    query: str
    total: int
    mock: bool = False


class WebSearch:
    """
    Exa AI web search integration.
    Provides semantic search with auto-prompt capability.
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'EXA_API_KEY', None)
        self.mock_mode = not self.api_key or not EXA_AVAILABLE
        
        if not self.mock_mode:
            self.client = Exa(api_key=self.api_key)
        else:
            self.client = None
        
        # Mock data for realistic responses
        self._mock_results = [
            {
                "title": "AI Trends 2026: The Future of Machine Learning",
                "url": "https://techcrunch.com/ai-trends-2026",
                "text": "Artificial intelligence continues to evolve rapidly. Key trends include multimodal AI, autonomous agents, and enhanced reasoning capabilities...",
                "published_date": "2026-01-15"
            },
            {
                "title": "How GenAI is Transforming Business Operations",
                "url": "https://hbr.org/genai-business-transformation",
                "text": "Generative AI is revolutionizing how businesses operate, from customer service to marketing automation...",
                "published_date": "2026-01-10"
            },
            {
                "title": "The Rise of AI Agents in Enterprise Software",
                "url": "https://forbes.com/ai-agents-enterprise",
                "text": "AI agents are becoming central to enterprise software, automating complex workflows and decision-making processes...",
                "published_date": "2026-01-08"
            },
            {
                "title": "Marketing Automation with AI: Best Practices",
                "url": "https://marketingweek.com/ai-marketing-automation",
                "text": "Learn how leading brands are using AI to automate marketing campaigns, personalize content, and improve ROI...",
                "published_date": "2026-01-05"
            },
            {
                "title": "Customer Experience in the Age of AI",
                "url": "https://gartner.com/cx-ai-insights",
                "text": "AI-powered customer experience solutions are delivering unprecedented personalization and efficiency...",
                "published_date": "2025-12-28"
            }
        ]
    
    @property
    def is_mock(self) -> bool:
        return self.mock_mode
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        use_autoprompt: bool = True,
        type: str = "neural"
    ) -> SearchResponse:
        """
        Perform a semantic web search.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 100)
            include_domains: Only include results from these domains
            exclude_domains: Exclude results from these domains
            start_published_date: Only return results published after this date (YYYY-MM-DD)
            use_autoprompt: Let Exa optimize the query
            type: Search type - "neural" (semantic) or "keyword"
        
        Returns:
            SearchResponse with list of results
        """
        if self.mock_mode:
            # Filter mock results based on query keywords
            query_lower = query.lower()
            filtered = []
            
            for i, result in enumerate(self._mock_results[:num_results]):
                score = 0.9 - (i * 0.05)
                
                # Boost score if query terms appear in title/text
                if any(word in result["title"].lower() for word in query_lower.split()):
                    score += 0.05
                
                filtered.append(SearchResult(
                    id=f"mock_{uuid.uuid4().hex[:12]}",
                    url=result["url"],
                    title=result["title"],
                    score=min(score, 1.0),
                    published_date=result.get("published_date"),
                    text=result.get("text"),
                    highlights=[query] if query else []
                ))
            
            return SearchResponse(
                results=filtered,
                query=query,
                total=len(filtered),
                mock=True
            )
        
        # Real Exa API
        search_params = {
            "query": query,
            "num_results": num_results,
            "use_autoprompt": use_autoprompt,
            "type": type
        }
        
        if include_domains:
            search_params["include_domains"] = include_domains
        if exclude_domains:
            search_params["exclude_domains"] = exclude_domains
        if start_published_date:
            search_params["start_published_date"] = start_published_date
        
        response = self.client.search(**search_params)
        
        results = [
            SearchResult(
                id=r.id,
                url=r.url,
                title=r.title,
                score=r.score,
                published_date=r.published_date,
                author=r.author
            )
            for r in response.results
        ]
        
        return SearchResponse(
            results=results,
            query=query,
            total=len(results),
            mock=False
        )
    
    async def search_and_contents(
        self,
        query: str,
        num_results: int = 5,
        text_length: int = 1000,
        highlights: bool = True
    ) -> SearchResponse:
        """
        Search and retrieve page contents in one call.
        
        Args:
            query: Search query
            num_results: Number of results
            text_length: Max characters of text to return per result
            highlights: Include highlighted relevant passages
        
        Returns:
            SearchResponse with text content included
        """
        if self.mock_mode:
            response = await self.search(query, num_results)
            # Mock results already include text
            return response
        
        response = self.client.search_and_contents(
            query=query,
            num_results=num_results,
            text={"max_characters": text_length},
            highlights=highlights
        )
        
        results = [
            SearchResult(
                id=r.id,
                url=r.url,
                title=r.title,
                score=r.score,
                published_date=r.published_date,
                author=r.author,
                text=r.text[:text_length] if r.text else None,
                highlights=r.highlights or []
            )
            for r in response.results
        ]
        
        return SearchResponse(
            results=results,
            query=query,
            total=len(results),
            mock=False
        )
    
    async def get_contents(
        self,
        urls: List[str],
        text_length: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Get contents of specific URLs.
        
        Args:
            urls: List of URLs to fetch
            text_length: Max characters per URL
        
        Returns:
            List of content dictionaries
        """
        if self.mock_mode:
            return [
                {
                    "url": url,
                    "title": f"Content from {url.split('/')[2]}",
                    "text": f"Mock content for {url}. This would contain the actual page text in production.",
                    "author": None,
                    "published_date": None
                }
                for url in urls
            ]
        
        response = self.client.get_contents(
            urls=urls,
            text={"max_characters": text_length}
        )
        
        return [
            {
                "url": r.url,
                "title": r.title,
                "text": r.text,
                "author": r.author,
                "published_date": r.published_date
            }
            for r in response.results
        ]
    
    async def find_similar(
        self,
        url: str,
        num_results: int = 10,
        exclude_source_domain: bool = True
    ) -> SearchResponse:
        """
        Find pages similar to a given URL.
        
        Args:
            url: Source URL to find similar pages
            num_results: Number of results
            exclude_source_domain: Exclude results from the same domain
        
        Returns:
            SearchResponse with similar pages
        """
        if self.mock_mode:
            # Return mock similar results
            return SearchResponse(
                results=[
                    SearchResult(
                        id=f"sim_{uuid.uuid4().hex[:12]}",
                        url=f"https://similar-site-{i}.com/article",
                        title=f"Similar Article {i+1}",
                        score=0.85 - (i * 0.05),
                        text="This is a similar article that covers related topics..."
                    )
                    for i in range(min(num_results, 5))
                ],
                query=f"similar:{url}",
                total=min(num_results, 5),
                mock=True
            )
        
        response = self.client.find_similar(
            url=url,
            num_results=num_results,
            exclude_source_domain=exclude_source_domain
        )
        
        results = [
            SearchResult(
                id=r.id,
                url=r.url,
                title=r.title,
                score=r.score,
                published_date=r.published_date
            )
            for r in response.results
        ]
        
        return SearchResponse(
            results=results,
            query=f"similar:{url}",
            total=len(results),
            mock=False
        )
    
    async def research_topic(
        self,
        topic: str,
        num_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Comprehensive research on a topic.
        Performs multiple searches and aggregates information.
        
        Args:
            topic: Topic to research
            num_sources: Number of sources to gather
        
        Returns:
            Aggregated research results
        """
        # Search for the topic
        main_results = await self.search_and_contents(topic, num_sources)
        
        # Compile research
        sources = []
        key_points = []
        
        for result in main_results.results:
            sources.append({
                "title": result.title,
                "url": result.url,
                "date": result.published_date
            })
            if result.text:
                # Extract first 200 chars as a key point
                key_points.append(result.text[:200] + "...")
        
        return {
            "topic": topic,
            "sources": sources,
            "key_points": key_points,
            "total_sources": len(sources),
            "mock": main_results.mock
        }


# Singleton instance
web_search = WebSearch()

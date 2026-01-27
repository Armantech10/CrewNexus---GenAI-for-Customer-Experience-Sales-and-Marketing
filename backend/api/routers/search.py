"""
Search Router
API endpoints for web search using Exa.
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

from backend.tools.web_search import web_search

router = APIRouter()


class ResearchRequest(BaseModel):
    topic: str
    num_sources: int = 5


class ContentsRequest(BaseModel):
    urls: List[str]
    text_length: int = 2000


@router.get("/mode")
async def get_search_mode():
    """Check if search is in mock or live mode"""
    return {
        "mock_mode": web_search.is_mock,
        "message": "Mock mode - simulated results" if web_search.is_mock else "Live Exa search"
    }


@router.get("/")
async def search(
    q: str = Query(..., description="Search query"),
    num_results: int = Query(10, ge=1, le=100),
    include_domains: Optional[str] = Query(None, description="Comma-separated domains to include"),
    exclude_domains: Optional[str] = Query(None, description="Comma-separated domains to exclude"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    use_autoprompt: bool = Query(True)
):
    """
    Perform a semantic web search.
    Returns relevant results based on meaning, not just keywords.
    """
    include_list = include_domains.split(",") if include_domains else None
    exclude_list = exclude_domains.split(",") if exclude_domains else None
    
    response = await web_search.search(
        query=q,
        num_results=num_results,
        include_domains=include_list,
        exclude_domains=exclude_list,
        start_published_date=start_date,
        use_autoprompt=use_autoprompt
    )
    
    return {
        "results": [r.dict() for r in response.results],
        "query": response.query,
        "total": response.total,
        "mock": response.mock
    }


@router.get("/with-contents")
async def search_with_contents(
    q: str = Query(..., description="Search query"),
    num_results: int = Query(5, ge=1, le=20),
    text_length: int = Query(1000, ge=100, le=5000)
):
    """
    Search and retrieve page contents in one call.
    More expensive but provides full context.
    """
    response = await web_search.search_and_contents(
        query=q,
        num_results=num_results,
        text_length=text_length
    )
    
    return {
        "results": [r.dict() for r in response.results],
        "query": response.query,
        "total": response.total,
        "mock": response.mock
    }


@router.post("/contents")
async def get_contents(request: ContentsRequest):
    """Get contents of specific URLs"""
    contents = await web_search.get_contents(
        urls=request.urls,
        text_length=request.text_length
    )
    
    return {
        "contents": contents,
        "total": len(contents),
        "mock": web_search.is_mock
    }


@router.get("/similar")
async def find_similar(
    url: str = Query(..., description="URL to find similar pages"),
    num_results: int = Query(10, ge=1, le=50),
    exclude_source: bool = Query(True)
):
    """Find pages similar to a given URL"""
    response = await web_search.find_similar(
        url=url,
        num_results=num_results,
        exclude_source_domain=exclude_source
    )
    
    return {
        "results": [r.dict() for r in response.results],
        "source_url": url,
        "total": response.total,
        "mock": response.mock
    }


@router.post("/research")
async def research_topic(request: ResearchRequest):
    """
    Comprehensive research on a topic.
    Gathers multiple sources and key points.
    """
    result = await web_search.research_topic(
        topic=request.topic,
        num_sources=request.num_sources
    )
    
    return result

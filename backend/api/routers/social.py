"""
Social Media Router
API endpoints for social media management.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.tools.social_media import social_media, Platform, PostStatus

router = APIRouter()


class CreatePostRequest(BaseModel):
    platform: Platform
    content: str
    media_urls: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None


class SchedulePostRequest(BaseModel):
    scheduled_time: datetime


class CrossPostRequest(BaseModel):
    content: str
    platforms: List[Platform]
    media_urls: Optional[List[str]] = None
    adapt_content: bool = True


@router.get("/mode")
async def get_social_mode():
    """Check if social media is in mock or live mode"""
    return {
        "mock_mode": social_media.is_mock,
        "message": "Mock mode - simulated posts" if social_media.is_mock else "Live mode"
    }


@router.get("/accounts")
async def get_connected_accounts():
    """Get all connected social media accounts"""
    accounts = await social_media.get_connected_accounts()
    return {
        "accounts": [a.dict() for a in accounts],
        "total": len(accounts),
        "mock": social_media.is_mock
    }


@router.get("/accounts/{platform}")
async def get_account_info(platform: Platform):
    """Get info for a specific platform"""
    account = await social_media.get_account_info(platform)
    if not account:
        raise HTTPException(status_code=404, detail=f"Account not found for {platform.value}")
    return {**account.dict(), "mock": social_media.is_mock}


@router.post("/posts")
async def create_post(request: CreatePostRequest):
    """Create a new social media post"""
    post = await social_media.create_post(
        platform=request.platform,
        content=request.content,
        media_urls=request.media_urls,
        scheduled_time=request.scheduled_time
    )
    return {**post.dict(), "mock": social_media.is_mock}


@router.get("/posts")
async def list_posts(
    platform: Optional[Platform] = None,
    status: Optional[PostStatus] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """List posts with optional filtering"""
    posts = await social_media.list_posts(
        platform=platform,
        status=status,
        limit=limit
    )
    return {
        "posts": [p.dict() for p in posts],
        "total": len(posts),
        "mock": social_media.is_mock
    }


@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    """Get a specific post"""
    post = await social_media.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {**post.dict(), "mock": social_media.is_mock}


@router.post("/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Publish a post immediately"""
    try:
        post = await social_media.publish_post(post_id)
        return {**post.dict(), "mock": social_media.is_mock}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/posts/{post_id}/schedule")
async def schedule_post(post_id: str, request: SchedulePostRequest):
    """Schedule a post for later"""
    try:
        post = await social_media.schedule_post(post_id, request.scheduled_time)
        return {**post.dict(), "mock": social_media.is_mock}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a post"""
    deleted = await social_media.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"deleted": True, "post_id": post_id}


@router.get("/posts/{post_id}/analytics")
async def get_post_analytics(post_id: str):
    """Get analytics for a specific post"""
    analytics = await social_media.get_post_analytics(post_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Post not found")
    return {**analytics.dict(), "mock": social_media.is_mock}


@router.get("/analytics/{platform}")
async def get_platform_analytics(
    platform: Platform,
    days: int = Query(30, ge=1, le=90)
):
    """Get aggregate analytics for a platform"""
    analytics = await social_media.get_platform_analytics(platform, days)
    return analytics


@router.post("/cross-post")
async def cross_post(request: CrossPostRequest):
    """Post content to multiple platforms at once"""
    posts = await social_media.cross_post(
        content=request.content,
        platforms=request.platforms,
        media_urls=request.media_urls,
        adapt_content=request.adapt_content
    )
    return {
        "posts": [p.dict() for p in posts],
        "total": len(posts),
        "mock": social_media.is_mock
    }

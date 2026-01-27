"""
Social Media Tool
Integration with Instagram, LinkedIn, and Facebook APIs.
Falls back to mock mode when credentials are not configured.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid

from backend.config.settings import settings


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class SocialPost(BaseModel):
    """Social media post model"""
    id: str
    platform: Platform
    content: str
    media_urls: List[str] = []
    status: PostStatus = PostStatus.DRAFT
    scheduled_time: Optional[datetime] = None
    published_time: Optional[datetime] = None
    url: Optional[str] = None
    metrics: Dict[str, int] = {}
    created_at: datetime = datetime.now()


class PostAnalytics(BaseModel):
    """Post analytics model"""
    post_id: str
    platform: Platform
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    fetched_at: datetime = datetime.now()


class AccountInfo(BaseModel):
    """Social account info"""
    platform: Platform
    account_id: str
    username: str
    followers: int = 0
    following: int = 0
    posts: int = 0
    connected: bool = False


class SocialMedia:
    """
    Social media API integration.
    Supports Instagram, LinkedIn, and Facebook.
    All in mock mode until OAuth credentials are configured.
    """
    
    def __init__(self):
        # Check for API credentials in settings
        self.instagram_token = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', None)
        self.linkedin_token = getattr(settings, 'LINKEDIN_ACCESS_TOKEN', None)
        self.facebook_token = getattr(settings, 'FACEBOOK_ACCESS_TOKEN', None)
        
        # All mock for now
        self.mock_mode = True
        
        # Mock storage
        self._mock_posts: Dict[str, SocialPost] = {}
        self._mock_accounts: Dict[Platform, AccountInfo] = {
            Platform.INSTAGRAM: AccountInfo(
                platform=Platform.INSTAGRAM,
                account_id="ig_123456",
                username="@yourcompany",
                followers=15420,
                following=892,
                posts=342,
                connected=True
            ),
            Platform.LINKEDIN: AccountInfo(
                platform=Platform.LINKEDIN,
                account_id="li_789012",
                username="Your Company",
                followers=8750,
                following=423,
                posts=156,
                connected=True
            ),
            Platform.FACEBOOK: AccountInfo(
                platform=Platform.FACEBOOK,
                account_id="fb_345678",
                username="Your Company Page",
                followers=23100,
                following=0,
                posts=489,
                connected=True
            )
        }
        
        # Seed some mock posts
        self._seed_mock_posts()
    
    def _seed_mock_posts(self):
        """Seed mock posts for demo"""
        mock_data = [
            {
                "platform": Platform.INSTAGRAM,
                "content": "✨ Excited to announce our new AI-powered features! #AI #Innovation",
                "status": PostStatus.PUBLISHED,
                "metrics": {"likes": 342, "comments": 28, "shares": 15}
            },
            {
                "platform": Platform.LINKEDIN,
                "content": "We're thrilled to share our latest whitepaper on AI in enterprise.",
                "status": PostStatus.PUBLISHED,
                "metrics": {"likes": 156, "comments": 23, "shares": 45}
            },
            {
                "platform": Platform.FACEBOOK,
                "content": "Join us for our upcoming webinar on customer experience automation!",
                "status": PostStatus.SCHEDULED,
                "metrics": {}
            }
        ]
        
        for data in mock_data:
            post_id = f"post_{uuid.uuid4().hex[:12]}"
            self._mock_posts[post_id] = SocialPost(
                id=post_id,
                **data
            )
    
    @property
    def is_mock(self) -> bool:
        return self.mock_mode
    
    async def get_connected_accounts(self) -> List[AccountInfo]:
        """Get all connected social media accounts"""
        if self.mock_mode:
            return list(self._mock_accounts.values())
        
        # Real API implementation would go here
        return []
    
    async def get_account_info(self, platform: Platform) -> Optional[AccountInfo]:
        """Get info for a specific platform account"""
        if self.mock_mode:
            return self._mock_accounts.get(platform)
        
        return None
    
    async def create_post(
        self,
        platform: Platform,
        content: str,
        media_urls: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None
    ) -> SocialPost:
        """
        Create a social media post.
        
        Args:
            platform: Target platform
            content: Post content/caption
            media_urls: Optional media URLs to attach
            scheduled_time: Optional time to schedule post
        
        Returns:
            Created post object
        """
        post_id = f"post_{uuid.uuid4().hex[:12]}"
        
        status = PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT
        
        post = SocialPost(
            id=post_id,
            platform=platform,
            content=content,
            media_urls=media_urls or [],
            status=status,
            scheduled_time=scheduled_time
        )
        
        self._mock_posts[post_id] = post
        return post
    
    async def publish_post(self, post_id: str) -> SocialPost:
        """
        Publish a draft or scheduled post immediately.
        
        Args:
            post_id: ID of the post to publish
        
        Returns:
            Updated post with published status
        """
        if post_id not in self._mock_posts:
            raise ValueError(f"Post {post_id} not found")
        
        post = self._mock_posts[post_id]
        
        if self.mock_mode:
            post.status = PostStatus.PUBLISHED
            post.published_time = datetime.now()
            post.url = f"https://{post.platform.value}.com/p/{post_id}"
            post.metrics = {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0
            }
            return post
        
        # Real API implementation
        return post
    
    async def schedule_post(
        self,
        post_id: str,
        scheduled_time: datetime
    ) -> SocialPost:
        """
        Schedule a post for future publishing.
        
        Args:
            post_id: ID of the post
            scheduled_time: When to publish
        
        Returns:
            Updated post
        """
        if post_id not in self._mock_posts:
            raise ValueError(f"Post {post_id} not found")
        
        post = self._mock_posts[post_id]
        post.status = PostStatus.SCHEDULED
        post.scheduled_time = scheduled_time
        
        return post
    
    async def get_post(self, post_id: str) -> Optional[SocialPost]:
        """Get a post by ID"""
        return self._mock_posts.get(post_id)
    
    async def list_posts(
        self,
        platform: Optional[Platform] = None,
        status: Optional[PostStatus] = None,
        limit: int = 20
    ) -> List[SocialPost]:
        """
        List posts with optional filtering.
        
        Args:
            platform: Filter by platform
            status: Filter by status
            limit: Max results
        
        Returns:
            List of posts
        """
        posts = list(self._mock_posts.values())
        
        if platform:
            posts = [p for p in posts if p.platform == platform]
        if status:
            posts = [p for p in posts if p.status == status]
        
        return posts[:limit]
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        if post_id in self._mock_posts:
            del self._mock_posts[post_id]
            return True
        return False
    
    async def get_post_analytics(self, post_id: str) -> Optional[PostAnalytics]:
        """
        Get analytics for a specific post.
        
        Args:
            post_id: ID of the post
        
        Returns:
            Post analytics
        """
        post = self._mock_posts.get(post_id)
        if not post:
            return None
        
        metrics = post.metrics
        impressions = metrics.get("impressions", 1000)
        engagement = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)
        
        return PostAnalytics(
            post_id=post_id,
            platform=post.platform,
            impressions=impressions,
            reach=int(impressions * 0.7),
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0),
            clicks=metrics.get("clicks", 0),
            engagement_rate=round(engagement / max(impressions, 1) * 100, 2)
        )
    
    async def get_platform_analytics(
        self,
        platform: Platform,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregate analytics for a platform.
        
        Args:
            platform: Target platform
            days: Number of days to analyze
        
        Returns:
            Aggregate analytics
        """
        if self.mock_mode:
            account = self._mock_accounts.get(platform)
            return {
                "platform": platform.value,
                "period_days": days,
                "account": account.dict() if account else None,
                "metrics": {
                    "total_posts": 15,
                    "total_impressions": 45000,
                    "total_reach": 32000,
                    "total_engagement": 2456,
                    "followers_gained": 234,
                    "avg_engagement_rate": 5.4
                },
                "top_performing_post": {
                    "id": "post_abc123",
                    "engagement": 892,
                    "impressions": 12500
                },
                "mock": True
            }
        
        return {}
    
    async def cross_post(
        self,
        content: str,
        platforms: List[Platform],
        media_urls: Optional[List[str]] = None,
        adapt_content: bool = True
    ) -> List[SocialPost]:
        """
        Post content to multiple platforms.
        
        Args:
            content: Base content
            platforms: List of target platforms
            media_urls: Optional media
            adapt_content: Adapt content per platform (hashtags, length, etc.)
        
        Returns:
            List of created posts
        """
        posts = []
        
        for platform in platforms:
            # Adapt content per platform
            adapted_content = content
            
            if adapt_content:
                if platform == Platform.INSTAGRAM:
                    # Instagram: Add hashtags, limit mentions
                    adapted_content = f"{content}\n\n#AI #Marketing #Tech"
                elif platform == Platform.LINKEDIN:
                    # LinkedIn: More professional tone
                    adapted_content = content.replace("!", ".")
                elif platform == Platform.FACEBOOK:
                    # Facebook: Can be longer
                    adapted_content = content
            
            post = await self.create_post(
                platform=platform,
                content=adapted_content,
                media_urls=media_urls
            )
            posts.append(post)
        
        return posts


# Singleton instance
social_media = SocialMedia()

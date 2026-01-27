"""
Marketing Campaigns Router - CRUD API for campaign management.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import uuid4

router = APIRouter()


# Models
class CampaignMetrics(BaseModel):
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    clicks: int = 0
    conversions: int = 0


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    platform: Literal["instagram", "twitter", "linkedin", "email"] = "instagram"
    target_audience: Optional[str] = None
    content: Optional[str] = None


class CampaignCreate(CampaignBase):
    scheduled_date: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[Literal["instagram", "twitter", "linkedin", "email"]] = None
    status: Optional[Literal["draft", "scheduled", "active", "paused", "completed"]] = None
    scheduled_date: Optional[str] = None
    target_audience: Optional[str] = None
    content: Optional[str] = None


class Campaign(CampaignBase):
    id: str
    status: Literal["draft", "scheduled", "active", "paused", "completed"] = "draft"
    scheduled_date: Optional[str] = None
    created_at: datetime
    metrics: CampaignMetrics = Field(default_factory=CampaignMetrics)


# In-memory store (replace with database in production)
_campaigns: dict[str, Campaign] = {
    "1": Campaign(
        id="1",
        name="Summer AI Launch",
        description="Launch campaign for our new AI features",
        status="active",
        platform="instagram",
        scheduled_date="Jan 28, 2026",
        created_at=datetime.now(),
        metrics=CampaignMetrics(impressions=45200, likes=3420, comments=189)
    ),
    "2": Campaign(
        id="2",
        name="Product Demo Series",
        description="Weekly product demonstrations",
        status="scheduled",
        platform="linkedin",
        scheduled_date="Feb 1, 2026",
        created_at=datetime.now()
    ),
    "3": Campaign(
        id="3",
        name="Customer Spotlight",
        description="Featuring our best customers",
        status="draft",
        platform="twitter",
        created_at=datetime.now()
    ),
    "4": Campaign(
        id="4",
        name="Q4 Wrap-up",
        description="Year-end summary campaign",
        status="completed",
        platform="instagram",
        created_at=datetime.now(),
        metrics=CampaignMetrics(impressions=89500, likes=7210, comments=423)
    )
}


@router.get("/campaigns", response_model=List[Campaign])
async def list_campaigns(
    status: Optional[str] = None,
    platform: Optional[str] = None
):
    """List all campaigns with optional filtering."""
    campaigns = list(_campaigns.values())
    
    if status:
        campaigns = [c for c in campaigns if c.status == status]
    if platform:
        campaigns = [c for c in campaigns if c.platform == platform]
    
    return campaigns


@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get a single campaign by ID."""
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _campaigns[campaign_id]


@router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    """Create a new campaign."""
    new_id = str(uuid4())[:8]
    new_campaign = Campaign(
        id=new_id,
        name=campaign.name,
        description=campaign.description,
        platform=campaign.platform,
        target_audience=campaign.target_audience,
        content=campaign.content,
        scheduled_date=campaign.scheduled_date,
        created_at=datetime.now()
    )
    _campaigns[new_id] = new_campaign
    return new_campaign


@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, updates: CampaignUpdate):
    """Update an existing campaign."""
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = _campaigns[campaign_id]
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    _campaigns[campaign_id] = campaign
    return campaign


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign."""
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    del _campaigns[campaign_id]
    return {"message": "Campaign deleted successfully"}


@router.post("/campaigns/{campaign_id}/generate-content")
async def generate_campaign_content(campaign_id: str):
    """Use AI to generate content for a campaign."""
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = _campaigns[campaign_id]
    
    # Import LLM service
    from backend.services.llm_service import llm_service
    
    system_prompt = """You are a creative marketing expert. Generate engaging social media content 
    based on the campaign details provided. Keep it concise, engaging, and platform-appropriate."""
    
    prompt = f"""Generate social media content for the following campaign:
    
Campaign Name: {campaign.name}
Platform: {campaign.platform}
Description: {campaign.description or 'No description provided'}
Target Audience: {campaign.target_audience or 'General audience'}

Please provide:
1. A catchy headline
2. Main post content (appropriate for {campaign.platform})
3. 3-5 relevant hashtags
4. A call-to-action"""
    
    response = await llm_service.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=500,
        temperature=0.8
    )
    
    # Update campaign content
    campaign.content = response.content
    _campaigns[campaign_id] = campaign
    
    return {
        "content": response.content,
        "provider": response.provider,
        "campaign": campaign
    }

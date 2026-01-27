from fastapi import APIRouter
from typing import Dict, List, Any
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary():
    """
    Get high-level statistics for the dashboard.
    In a real app, this would query the database.
    """
    # Simulating dynamic data
    return {
        "revenue": {
            "value": "$52,140.00",
            "trend": "+12.5% from last month",
            "trendUp": True
        },
        "sales_conversations": {
            "value": str(random.randint(2000, 3000)),
            "trend": "+5% from last week",
            "trendUp": True
        },
        "marketing_reach": {
            "value": "1.2M",
            "trend": "+8.2% from last campaign",
            "trendUp": True
        },
        "active_users": {
            "value": str(random.randint(500, 800)),
            "trend": "+24 in last hour",
            "trendUp": True
        }
    }

@router.get("/activity")
async def get_activity_chart():
    """
    Get activity data for chars.
    """
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    data = []
    
    for day in days:
        data.append({
            "name": day,
            "sales": random.randint(20, 50),
            "marketing": random.randint(15, 60),
            "support": random.randint(10, 30)
        })
        
    return data

@router.get("/recent-actions")
async def get_recent_actions():
    actions = [
        "Sales Agent qualified lead #1234",
        "Marketing Crew generated new campaign 'Summer Sale'",
        "Support Genie resolved ticket #998",
        "Sales Agent closed deal with Acme Corp",
        "System backup completed"
    ]
    
    return [
        {
            "id": i,
            "description": action,
            "time": f"{random.randint(1, 10)} mins ago",
            "agent": "system" if "System" in action else "agent"
        }
        for i, action in enumerate(random.sample(actions, 4))
    ]

"""
Pytest configuration and fixtures for unified-genai-platform tests.
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def sample_campaign():
    """Sample campaign data for testing"""
    return {
        "name": "Test Campaign",
        "platform": "instagram",
        "description": "A test marketing campaign"
    }


@pytest.fixture
def sample_payment():
    """Sample payment data for testing"""
    return {
        "amount": 2999,
        "currency": "usd",
        "metadata": {"order_id": "test-123"}
    }


@pytest.fixture
def sample_event():
    """Sample calendar event data"""
    from datetime import datetime, timedelta
    return {
        "title": "Test Meeting",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=1),
        "description": "A test meeting"
    }


@pytest.fixture
def sample_social_post():
    """Sample social media post data"""
    return {
        "platform": "instagram",
        "content": "Test post content #test",
        "media_urls": []
    }

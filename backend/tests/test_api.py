"""
API Integration Tests
Tests for FastAPI routers using TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestPaymentsAPI:
    """Tests for payments API endpoints"""
    
    def test_get_payment_mode(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/payments/mode")
        assert response.status_code == 200
        assert "mock_mode" in response.json()
    
    def test_create_payment_intent(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.post("/api/v1/payments/create-intent", json={
            "amount": 2999,
            "currency": "usd"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 2999
        assert "client_secret" in data


class TestSearchAPI:
    """Tests for search API endpoints"""
    
    def test_search(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/search/", params={"q": "AI marketing"})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["query"] == "AI marketing"
    
    def test_search_mode(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/search/mode")
        assert response.status_code == 200


class TestSocialAPI:
    """Tests for social media API endpoints"""
    
    def test_get_accounts(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/social/accounts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["accounts"]) == 3
    
    def test_list_posts(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/social/posts")
        
        assert response.status_code == 200
        assert "posts" in response.json()
    
    def test_create_post(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.post("/api/v1/social/posts", json={
            "platform": "instagram",
            "content": "Test post from API"
        })
        
        assert response.status_code == 200
        assert response.json()["platform"] == "instagram"


class TestCalendarAPI:
    """Tests for calendar API endpoints"""
    
    def test_list_events(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/calendar/events")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
    
    def test_create_event(self):
        from backend.api.main import app
        client = TestClient(app)
        
        start = (datetime.now() + timedelta(days=1)).isoformat()
        end = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        response = client.post("/api/v1/calendar/events", json={
            "title": "API Test Event",
            "start_time": start,
            "end_time": end
        })
        
        assert response.status_code == 200
        assert response.json()["title"] == "API Test Event"


class TestMarketingAPI:
    """Tests for marketing campaigns API"""
    
    def test_list_campaigns(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/marketing/campaigns")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_campaign(self):
        from backend.api.main import app
        client = TestClient(app)
        
        response = client.post("/api/v1/marketing/campaigns", json={
            "name": "Test Campaign",
            "platform": "instagram",
            "description": "Testing from API"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Campaign"
        assert data["status"] == "draft"

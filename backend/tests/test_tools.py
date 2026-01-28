"""
Tests for backend tools.
"""
import pytest
from datetime import datetime, timedelta


class TestStripePayments:
    """Tests for Stripe payments tool"""
    
    @pytest.mark.asyncio
    async def test_create_payment_intent(self):
        from backend.tools.stripe_payments import stripe_payments
        
        intent = await stripe_payments.create_payment_intent(
            amount=2999,
            currency="usd"
        )
        
        assert intent.id.startswith("pi_mock_")
        assert intent.amount == 2999
        assert intent.currency == "usd"
        assert intent.status == "requires_payment_method"
        assert intent.client_secret is not None
    
    @pytest.mark.asyncio
    async def test_create_checkout_session(self):
        from backend.tools.stripe_payments import stripe_payments
        
        session = await stripe_payments.create_checkout_session(
            line_items=[{
                "price_data": {"unit_amount": 1000, "currency": "usd", "product_data": {"name": "Test"}},
                "quantity": 2
            }],
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert session.id.startswith("cs_mock_")
        assert session.url.startswith("https://checkout.stripe.com/mock/")
        assert session.amount_total == 2000
    
    @pytest.mark.asyncio
    async def test_process_refund(self):
        from backend.tools.stripe_payments import stripe_payments
        
        # First create a payment
        intent = await stripe_payments.create_payment_intent(amount=5000)
        
        # Then refund it
        refund = await stripe_payments.process_refund(intent.id)
        
        assert refund.id.startswith("re_mock_")
        assert refund.payment_intent_id == intent.id
        assert refund.status == "succeeded"


class TestWebSearch:
    """Tests for Exa web search tool"""
    
    @pytest.mark.asyncio
    async def test_search(self):
        from backend.tools.web_search import web_search
        
        response = await web_search.search("AI trends 2026", num_results=5)
        
        assert response.query == "AI trends 2026"
        assert len(response.results) > 0
        assert response.mock is True
        
        # Check result structure
        result = response.results[0]
        assert result.url is not None
        assert result.title is not None
        assert result.score > 0
    
    @pytest.mark.asyncio
    async def test_research_topic(self):
        from backend.tools.web_search import web_search
        
        result = await web_search.research_topic("marketing automation")
        
        assert result["topic"] == "marketing automation"
        assert len(result["sources"]) > 0
        assert "key_points" in result


class TestSocialMedia:
    """Tests for social media tool"""
    
    @pytest.mark.asyncio
    async def test_get_connected_accounts(self):
        from backend.tools.social_media import social_media
        
        accounts = await social_media.get_connected_accounts()
        
        assert len(accounts) == 3  # Instagram, LinkedIn, Facebook
        platforms = [a.platform.value for a in accounts]
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "facebook" in platforms
    
    @pytest.mark.asyncio
    async def test_create_post(self):
        from backend.tools.social_media import social_media, Platform
        
        post = await social_media.create_post(
            platform=Platform.INSTAGRAM,
            content="Test post #testing"
        )
        
        assert post.id.startswith("post_")
        assert post.platform == Platform.INSTAGRAM
        assert post.content == "Test post #testing"
        assert post.status.value == "draft"
    
    @pytest.mark.asyncio
    async def test_cross_post(self):
        from backend.tools.social_media import social_media, Platform
        
        posts = await social_media.cross_post(
            content="Cross-platform test!",
            platforms=[Platform.INSTAGRAM, Platform.LINKEDIN]
        )
        
        assert len(posts) == 2
        assert posts[0].platform == Platform.INSTAGRAM
        assert posts[1].platform == Platform.LINKEDIN


class TestCalendar:
    """Tests for calendar scheduling tool"""
    
    @pytest.mark.asyncio
    async def test_create_event(self):
        from backend.tools.calendar import calendar, EventType
        
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        event = await calendar.create_event(
            title="Test Meeting",
            start_time=start,
            end_time=end,
            event_type=EventType.MEETING
        )
        
        assert event.id.startswith("evt_")
        assert event.title == "Test Meeting"
        assert event.meeting_link is not None
    
    @pytest.mark.asyncio
    async def test_find_available_slots(self):
        from backend.tools.calendar import calendar
        
        start = datetime.now().replace(hour=9, minute=0)
        end = start + timedelta(days=3)
        
        slots = await calendar.find_available_slots(
            duration_minutes=30,
            start_date=start,
            end_date=end
        )
        
        assert len(slots) > 0
        for slot in slots:
            assert slot.duration_minutes == 30
            assert slot.end > slot.start
    
    @pytest.mark.asyncio
    async def test_schedule_meeting(self):
        from backend.tools.calendar import calendar
        
        result = await calendar.schedule_meeting(
            title="Scheduled Test",
            duration_minutes=60,
            attendees=[{"email": "test@example.com", "name": "Test User"}]
        )
        
        assert result["success"] is True
        assert "event" in result
        assert result["event"]["title"] == "Scheduled Test"


class TestKnowledgeBase:
    """Tests for knowledge base tool"""
    
    @pytest.mark.asyncio
    async def test_search_products(self):
        from backend.tools.knowledge_base import knowledge_base
        
        results = await knowledge_base.search_products("enterprise")
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_get_pricing_info(self):
        from backend.tools.knowledge_base import knowledge_base
        
        pricing = await knowledge_base.get_pricing_info()
        
        assert "plans" in pricing
        assert len(pricing["plans"]) > 0


class TestCRM:
    """Tests for CRM tool"""
    
    @pytest.mark.asyncio
    async def test_lookup_customer(self):
        from backend.tools.crm import crm_tool
        
        # Look up by email (using existing mock data)
        customer = await crm_tool.lookup_customer(email="alice@example.com")
        
        assert customer is not None
        assert customer.email == "alice@example.com"
    
    @pytest.mark.asyncio
    async def test_create_lead(self):
        from backend.tools.crm import crm_tool
        
        lead = await crm_tool.create_lead(
            email="newlead@test.com",
            name="New Lead",
            source="website"
        )
        
        assert lead.id.startswith("lead_")
        assert lead.email == "newlead@test.com"
        assert lead.status == "new"
